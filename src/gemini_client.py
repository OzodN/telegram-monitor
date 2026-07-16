from __future__ import annotations

import logging
import math
import random
import re
import time
import threading
from collections import deque
from collections.abc import Callable
from typing import Any

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from src.models import GeminiConfig
from src.structured_output import StructuredOutputError, extract_validated_json


logger = logging.getLogger(__name__)
RETRY_DELAY_PATTERN = re.compile(r"^\s*(?P<seconds>-?\d+(?:\.\d+)?)s\s*$")
TRY_AGAIN_SECONDS_PATTERN = re.compile(r"try again in (?P<seconds>\d+) seconds", re.IGNORECASE)
RETRYABLE_SERVER_CODES = {500, 502, 503, 504}
DAILY_QUOTA_HINTS = (
    "per day",
    "/day",
    "daily",
    "rpd",
    "perday",
    "generaterequestsperdayperprojectpermodel-freetier",
    "generate_content_free_tier_requests",
)
QUOTA_EXHAUSTION_HINTS = (
    "resource_exhausted",
    "quota",
    "limit",
    "exceeded",
    "exhausted",
)


class GeminiAllKeysExhaustedError(RuntimeError):
    """Raised when every configured Gemini key is exhausted for the day."""


class GeminiRetryableResponseFormatError(RuntimeError):
    """Raised when a Gemini response is not valid structured output for the requested operation."""


import queue
import threading

class GeminiKeyPool:
    def __init__(self, api_keys: list[str]) -> None:
        if not api_keys:
            raise ValueError("At least one Gemini API key must be configured")
        self._api_keys = list(api_keys)
        
        self._idle_keys = queue.Queue()
        for key in self._api_keys:
            self._idle_keys.put(key)
            
        self._active_keys_count = len(api_keys)
        self._lock = threading.Lock()

    def acquire_key(self) -> str:
        with self._lock:
            if self._active_keys_count == 0:
                raise GeminiAllKeysExhaustedError("All configured Gemini API keys are exhausted.")
                
        # Block until an idle key is returned to the pool
        # If all active keys are busy, this thread will wait.
        return self._idle_keys.get()

    def release_key(self, key: str) -> None:
        self._idle_keys.put(key)

    def drop_key(self, key: str) -> None:
        # Key is not returned to the idle queue, permanently reducing the pool size.
        with self._lock:
            self._active_keys_count -= 1
            if self._active_keys_count == 0:
                # Release a dummy item just to unblock any waiting threads 
                # so they can wake up and raise GeminiAllKeysExhaustedError
                self._idle_keys.put("EXHAUSTED")

    def format_key_label(self, key: str) -> str:
        try:
            index = self._api_keys.index(key)
        except ValueError:
            index = -1
        suffix = key[-4:] if len(key) >= 4 else key
        return f"{index + 1}/{len(self._api_keys)} (...{suffix})"


class GeminiClient:
    def __init__(self, config: GeminiConfig) -> None:
        self._config = config
        self._pool = GeminiKeyPool(config.api_keys)
        self._clients: dict[str, genai.Client] = {}

    def generate_content(
        self,
        *,
        contents: str,
        request_config: dict[str, Any],
        operation_name: str,
    ) -> Any:
        return self._generate_with_retry(
            contents=contents,
            request_config=request_config,
            operation_name=operation_name,
        )

    def generate_json(
        self,
        *,
        contents: str,
        request_config: dict[str, Any],
        operation_name: str,
        validator: Callable[[Any], bool],
        response_schema: Any | None = None,
    ) -> Any:
        config = dict(request_config)
        if response_schema is not None:
            config["response_schema"] = response_schema

        return self._generate_with_retry(
            contents=contents,
            request_config=config,
            operation_name=operation_name,
            response_parser=lambda raw_text: _parse_json_response(raw_text, validator=validator),
        )

    def _generate_with_retry(
        self,
        *,
        contents: str,
        request_config: dict[str, Any],
        operation_name: str,
        response_parser: Callable[[str], Any] | None = None,
    ) -> Any:
        while True:
            key = self._pool.acquire_key()
            if key == "EXHAUSTED":
                raise GeminiAllKeysExhaustedError("All configured Gemini API keys are exhausted.")
                
            client = self._get_client_for_key(key)
            key_died = False
            
            for attempt in range(1, self._config.retry_attempts + 1):
                try:
                    response = client.models.generate_content(
                        model=self._config.model,
                        contents=contents,
                        config=request_config,
                    )
                    self._pool.release_key(key)
                    if response_parser is None:
                        return response
                    return response_parser(getattr(response, "text", "") or "")
                except Exception as exc:
                    is_conn_error = _is_retryable_transport_error(exc)
                    is_timeout_err = _is_timeout_error(exc)
                    is_daily_quota = _is_daily_quota_exhaustion_error(exc)
                    is_auth_err = _is_auth_error(exc)

                    key_label = self._pool.format_key_label(key)

                    # 1. Immediate key drop for dead keys (Daily Quota or Auth errors)
                    if is_daily_quota or is_auth_err:
                        reason = "Daily quota exhausted" if is_daily_quota else "Authentication/Authorization failure (invalid/dead key)"
                        logger.warning(
                            "%s for %s during %s. Dropping key from pool.",
                            reason,
                            key_label,
                            operation_name,
                        )
                        self._pool.drop_key(key)
                        self._drop_client(key)
                        key_died = True
                        break # Break inner loop, fetch new key from pool

                    # 2. Check if this is a retryable error
                    is_retryable = (
                        _is_retryable_same_key_error(exc)
                        or is_conn_error
                        or is_timeout_err
                    )

                    if is_retryable:
                        if attempt < self._config.retry_attempts:
                            retry_delay_seconds = _calculate_retry_delay_seconds(exc, self._config, attempt)
                            logger.warning(
                                "Retryable Gemini failure during %s | reason=%s | status=%s | "
                                "retry_attempt=%s/%s | sleep_penalty=%s | current_key=%s. "
                                "Sleeping while holding key.",
                                operation_name,
                                _extract_retry_reason(exc),
                                _extract_error_code(exc),
                                attempt,
                                self._config.retry_attempts,
                                _format_wait_seconds(retry_delay_seconds),
                                key_label,
                            )
                            # Sleep while holding the key. This naturally rate-limits this specific key!
                            time.sleep(retry_delay_seconds)
                            continue
                        else:
                            logger.warning(
                                "Max retries exhausted for key %s during %s | reason=%s.",
                                key_label,
                                operation_name,
                                _extract_retry_reason(exc),
                            )
                            self._pool.release_key(key)
                            raise

                    # 3. Non-retryable
                    logger.error(
                        "Non-retryable Gemini error during %s | reason=%s | status=%s | current_key=%s. Failing immediately.",
                        operation_name,
                        _extract_retry_reason(exc),
                        _extract_error_code(exc),
                        key_label,
                    )
                    self._pool.release_key(key)
                    raise
                    
            if not key_died:
                raise RuntimeError("Unexpected exit from retry loop")

    def _get_client_for_key(self, api_key: str) -> genai.Client:
        client = self._clients.get(api_key)
        if client is None:
            client = genai.Client(
                api_key=api_key,
                http_options=genai_types.HttpOptions(
                    timeout=int(self._config.request_timeout_seconds * 1000),
                ),
            )
            self._clients[api_key] = client
        return client

    def _drop_client(self, api_key: str) -> None:
        client = self._clients.pop(api_key, None)
        if client is not None:
            try:
                client.close()
            except Exception as e:
                logger.warning("Error closing Gemini client for key %s: %s", api_key, e)


def _is_retryable_same_key_error(exc: Exception) -> bool:
    return (
        isinstance(exc, GeminiRetryableResponseFormatError)
        or _is_retryable_rate_limit_error(exc)
        or _is_retryable_server_error(exc)
    )


def _is_auth_error(exc: Exception) -> bool:
    if isinstance(exc, genai_errors.APIError):
        return exc.code in {401, 403}
    return False



def _is_timeout_error(exc: Exception) -> bool:
    if isinstance(exc, TimeoutError):
        return True

    class_name = exc.__class__.__name__.lower()
    if "timeout" in class_name:
        return True

    module_name = exc.__class__.__module__.lower()
    return "httpx" in module_name and "timeout" in class_name


def _is_retryable_transport_error(exc: Exception) -> bool:
    class_name = exc.__class__.__name__.lower()
    module_name = exc.__class__.__module__.lower()
    error_text = str(exc).lower()

    if "httpx" in module_name or "httpcore" in module_name:
        transport_markers = (
            "readerror",
            "writeerror",
            "connecterror",
            "closeerror",
            "networkerror",
            "protocolerror",
            "transporterror",
        )
        if any(marker in class_name for marker in transport_markers):
            return True

    transient_markers = (
        "connection reset",
        "connection aborted",
        "connection dropped",
        "remote host forcibly closed",
        "forcibly closed",
        "winerror 10054",
        "broken pipe",
    )
    return any(marker in error_text for marker in transient_markers)


def _is_daily_quota_exhaustion_error(exc: Exception) -> bool:
    if not isinstance(exc, genai_errors.APIError):
        return False

    status = (exc.status or "").upper()
    message = (exc.message or "").lower()
    flattened_details = " ".join(_flatten_strings(exc.details)).lower()
    haystack = " ".join(part for part in (status, message, flattened_details) if part)

    if not haystack:
        return False

    if _contains_daily_quota_violation(exc.details):
        return True

    if "resource_exhausted" not in haystack and "quota" not in haystack and exc.code != 429:
        return False

    return any(hint in haystack for hint in DAILY_QUOTA_HINTS) and any(
        hint in haystack for hint in QUOTA_EXHAUSTION_HINTS
    )


def _contains_daily_quota_violation(details: Any) -> bool:
    if isinstance(details, dict):
        quota_id = str(details.get("quotaId", "")).lower()
        quota_metric = str(details.get("quotaMetric", "")).lower()
        if quota_id == "generaterequestsperdayperprojectpermodel-freetier":
            return True
        if quota_metric == "generativelanguage.googleapis.com/generate_content_free_tier_requests":
            return True

        for value in details.values():
            if _contains_daily_quota_violation(value):
                return True
        return False

    if isinstance(details, list):
        return any(_contains_daily_quota_violation(item) for item in details)

    return False


def _is_retryable_rate_limit_error(exc: Exception) -> bool:
    if not isinstance(exc, genai_errors.APIError):
        return False

    if _is_daily_quota_exhaustion_error(exc):
        return False

    if exc.code == 429:
        return True

    status = (exc.status or "").upper()
    if status == "RESOURCE_EXHAUSTED":
        return True

    message = (exc.message or "").upper()
    return "RESOURCE_EXHAUSTED" in message


def _is_retryable_server_error(exc: Exception) -> bool:
    return isinstance(exc, genai_errors.APIError) and exc.code in RETRYABLE_SERVER_CODES


def _calculate_retry_delay_seconds(exc: Exception, config: GeminiConfig, attempt: int) -> float:
    retry_delay = _extract_retry_delay_seconds(exc)
    exponential_backoff = config.retry_backoff_seconds * (2 ** (attempt - 1))
    jitter_ceiling = min(config.retry_backoff_seconds, config.max_backoff_seconds)
    computed_delay = min(config.max_backoff_seconds, exponential_backoff + random.uniform(0.0, jitter_ceiling))

    if retry_delay is not None:
        return min(config.max_backoff_seconds, max(retry_delay, computed_delay))
    return computed_delay


def _parse_json_response(raw_text: str, validator: Callable[[Any], bool]) -> Any:
    try:
        return extract_validated_json(raw_text, validator=validator)
    except StructuredOutputError as exc:
        raise GeminiRetryableResponseFormatError(str(exc)) from exc


def _extract_retry_delay_seconds(exc: Exception) -> float | None:
    if not isinstance(exc, genai_errors.APIError):
        return None

    retry_after_seconds = _extract_retry_after_header_seconds(exc)
    if retry_after_seconds is not None:
        return retry_after_seconds

    payload_delay = _extract_retry_delay_from_payload(exc.details)
    if payload_delay is not None:
        return payload_delay

    message = exc.message or ""
    match = TRY_AGAIN_SECONDS_PATTERN.search(message)
    if match:
        return max(float(match.group("seconds")), 0.0)

    return None


def _extract_retry_after_header_seconds(exc: genai_errors.APIError) -> float | None:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if not headers:
        return None

    retry_after = headers.get("retry-after") or headers.get("Retry-After")
    if retry_after is None:
        return None

    try:
        return max(float(retry_after), 0.0)
    except (TypeError, ValueError):
        return None


def _extract_retry_delay_from_payload(payload: Any) -> float | None:
    if isinstance(payload, dict):
        for key in ("retryDelay", "retry_delay"):
            if key in payload:
                parsed = _parse_duration_seconds(payload[key])
                if parsed is not None:
                    return parsed
        for value in payload.values():
            parsed = _extract_retry_delay_from_payload(value)
            if parsed is not None:
                return parsed
        return None

    if isinstance(payload, list):
        for item in payload:
            parsed = _extract_retry_delay_from_payload(item)
            if parsed is not None:
                return parsed

    return None


def _parse_duration_seconds(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return max(float(value), 0.0)

    if isinstance(value, dict):
        seconds = value.get("seconds")
        nanos = value.get("nanos", 0)
        if seconds is None and nanos is None:
            return None

        try:
            total = 0.0
            if seconds is not None:
                total += float(seconds)
            if nanos is not None:
                total += float(nanos) / 1_000_000_000
            return max(total, 0.0)
        except (TypeError, ValueError):
            return None

    if isinstance(value, str):
        stripped = value.strip()
        match = RETRY_DELAY_PATTERN.match(stripped)
        if match:
            return max(float(match.group("seconds")), 0.0)
        try:
            return max(float(stripped), 0.0)
        except ValueError:
            return None

    return None


def _flatten_strings(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        return [value]

    if isinstance(value, dict):
        flattened: list[str] = []
        for item in value.values():
            flattened.extend(_flatten_strings(item))
        return flattened

    if isinstance(value, list):
        flattened: list[str] = []
        for item in value:
            flattened.extend(_flatten_strings(item))
        return flattened

    return [str(value)]


def _extract_error_code(exc: Exception) -> str:
    if _is_timeout_error(exc):
        return "TIMEOUT"
    if isinstance(exc, genai_errors.APIError):
        return str(exc.code)
    return exc.__class__.__name__


def _extract_retry_reason(exc: Exception) -> str:
    if _is_timeout_error(exc):
        return "REQUEST_TIMEOUT"
    if isinstance(exc, genai_errors.APIError):
        status = (exc.status or "").strip()
        message = (exc.message or "").strip()
        if status and message:
            return f"{status} | {message}"
        if status:
            return status
        if message:
            return message
    return exc.__class__.__name__


def _format_wait_seconds(seconds: float) -> str:
    return str(max(1, math.ceil(seconds)))


def _format_timeout_seconds(seconds: float) -> str:
    rounded = round(seconds)
    if abs(seconds - rounded) < 1e-9:
        return str(int(rounded))
    return f"{seconds:.1f}"
