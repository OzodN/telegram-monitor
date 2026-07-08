from __future__ import annotations

import os
from pathlib import Path

import yaml

from src.models import (
    AppConfig,
    ChannelConfig,
    GeminiConfig,
    PathsConfig,
    ReportPeriodConfig,
    TelegramConfig,
)


TELEGRAM_API_ID_MIN = 1
TELEGRAM_API_ID_MAX = 2_147_483_647


def load_app_config(config_path: Path) -> AppConfig:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    telegram = data["telegram"]
    gemini = data["gemini"]
    classification = data.get("classification", {})
    paths = data["paths"]

    api_id = _parse_telegram_api_id(_resolve_config_value(telegram, "api_id", "api_id_env"))

    return AppConfig(
        timezone=data["timezone"],
        telegram=TelegramConfig(
            api_id=api_id,
            api_hash=_resolve_config_value(telegram, "api_hash", "api_hash_env"),
            session_name=telegram["session_name"],
            channels=[
                ChannelConfig(
                    council_name=item["council_name"],
                    telegram_url=item["telegram_url"],
                )
                for item in telegram["channels"]
            ],
        ),
        gemini=GeminiConfig(
            api_keys=_resolve_config_list(
                gemini,
                list_key="api_keys",
                env_list_key="api_keys_env",
                legacy_direct_key="api_key",
                legacy_env_key="api_key_env",
            ),
            model=gemini["model"],
            request_timeout_seconds=_parse_positive_float(
                gemini.get("request_timeout_seconds", 300),
                "gemini.request_timeout_seconds",
            ),
            classification_batch_size=_parse_positive_int(
                classification.get("batch_size", gemini.get("classification_batch_size", 100)),
                "classification.batch_size",
            ),
            retry_attempts=_parse_positive_int(
                classification.get("retry_attempts", 10),
                "classification.retry_attempts",
            ),
            retry_backoff_seconds=_parse_positive_float(
                classification.get("retry_backoff_seconds", 60),
                "classification.retry_backoff_seconds",
            ),
            request_delay_seconds=_parse_non_negative_float(
                classification.get("request_delay_seconds", 65),
                "classification.request_delay_seconds",
            ),
            max_backoff_seconds=_parse_positive_float(
                classification.get("max_backoff_seconds", 600),
                "classification.max_backoff_seconds",
            ),
            max_requests_per_minute=_parse_positive_int(
                classification.get("max_requests_per_minute", 1),
                "classification.max_requests_per_minute",
            ),
            temperature=float(gemini["temperature"]),
        ),
        paths=PathsConfig(
            classification_specification_md=Path(paths["classification_specification_md"]),
            narrative_specification_md=Path(paths["narrative_specification_md"]),
            issues_24_md=Path(paths["issues_24_md"]),
            laws_162_md=Path(paths["laws_162_md"]),
            reference_report_docx=Path(paths["reference_report_docx"]),
            output_root=Path(paths["output_root"]),
        ),
        report_period=ReportPeriodConfig(
            mode=data["report_period"]["mode"],
            explicit_start=data["report_period"]["explicit_start"],
            explicit_end=data["report_period"]["explicit_end"],
        ),
    )


def _resolve_config_value(section: dict, direct_key: str, env_key: str) -> str:
    if direct_key in section and section[direct_key] is not None:
        return str(section[direct_key])

    if env_key not in section or section[env_key] is None:
        raise ValueError(f"Either '{direct_key}' or '{env_key}' must be provided in config")

    raw_value = section[env_key]
    if not isinstance(raw_value, str):
        return str(raw_value)

    env_value = os.getenv(raw_value)
    if env_value:
        candidate = env_value.strip()
        if candidate:
            return candidate

    if raw_value.startswith(("GEMINI_", "TELEGRAM_")):
        raise ValueError(
            f"Environment variable '{raw_value}' is not defined or is empty in the environment."
        )

    return raw_value


def _resolve_config_list(
    section: dict,
    *,
    list_key: str,
    env_list_key: str,
    legacy_direct_key: str,
    legacy_env_key: str,
) -> list[str]:
    if list_key in section and section[list_key] is not None:
        raw_values = section[list_key]
    elif env_list_key in section and section[env_list_key] is not None:
        raw_values = section[env_list_key]
    elif legacy_direct_key in section and section[legacy_direct_key] is not None:
        raw_values = [section[legacy_direct_key]]
    elif legacy_env_key in section and section[legacy_env_key] is not None:
        raw_values = [section[legacy_env_key]]
    else:
        raise ValueError(
            f"Either '{list_key}', '{env_list_key}', '{legacy_direct_key}', or '{legacy_env_key}' must be provided in config"
        )

    if not isinstance(raw_values, list):
        raise ValueError(f"{list_key} must be a list, got: {type(raw_values).__name__}")

    resolved = [_resolve_scalar_or_env(item) for item in raw_values]
    non_empty = [item for item in resolved if item]
    if not non_empty:
        raise ValueError(f"{list_key} must contain at least one non-empty API key")

    return non_empty


def _resolve_scalar_or_env(value: object) -> str:
    if not isinstance(value, str):
        return str(value)

    is_env_var_name = value.startswith(("GEMINI_", "TELEGRAM_"))

    env_value = os.getenv(value)
    if env_value:
        candidate = env_value.strip()
        if candidate:
            return candidate

    if is_env_var_name:
        raise ValueError(
            f"Environment variable '{value}' is not defined or is empty in the environment."
        )

    candidate = value.strip()
    if not candidate:
        return ""
    return candidate


def _parse_telegram_api_id(value: str) -> int:
    try:
        api_id = int(value)
    except ValueError as exc:
        raise ValueError(f"Telegram api_id must be an integer, got: {value!r}") from exc

    if not (TELEGRAM_API_ID_MIN <= api_id <= TELEGRAM_API_ID_MAX):
        raise ValueError(
            "Telegram api_id is invalid. Expected a my.telegram.org app id within 32-bit signed integer range, "
            f"got: {api_id}"
        )

    return api_id


def _parse_positive_int(value: object, field_name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer, got: {value!r}") from exc

    if parsed < 1:
        raise ValueError(f"{field_name} must be greater than zero, got: {parsed}")

    return parsed


def _parse_positive_float(value: object, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number, got: {value!r}") from exc

    if parsed <= 0:
        raise ValueError(f"{field_name} must be greater than zero, got: {parsed}")

    return parsed


def _parse_non_negative_float(value: object, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number, got: {value!r}") from exc

    if parsed < 0:
        raise ValueError(f"{field_name} must be zero or greater, got: {parsed}")

    return parsed
