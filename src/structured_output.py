from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


class StructuredOutputError(ValueError):
    """Raised when a structured model response cannot be extracted or validated."""


Validator = Callable[[Any], bool]


@dataclass(slots=True, frozen=True)
class JsonCandidate:
    raw_text: str
    parsed_value: Any


def extract_validated_json(
    raw_text: str,
    *,
    validator: Validator | None = None,
) -> Any:
    candidates = _extract_json_candidates(raw_text)
    if not candidates:
        raise StructuredOutputError("No valid JSON object or array found in model response")

    if validator is None:
        if len(candidates) != 1:
            raise StructuredOutputError(f"Expected exactly one JSON block, found {len(candidates)}")
        return candidates[0].parsed_value

    matching = [candidate for candidate in candidates if validator(candidate.parsed_value)]
    if not matching:
        raise StructuredOutputError("No extracted JSON block matched the expected response schema")
    if len(matching) != 1:
        raise StructuredOutputError(f"Expected exactly one schema-matching JSON block, found {len(matching)}")
    return matching[0].parsed_value


def _extract_json_candidates(raw_text: str) -> list[JsonCandidate]:
    candidates: list[JsonCandidate] = []
    stack: list[str] = []
    start_index: int | None = None
    in_string = False
    escape_next = False

    for index, char in enumerate(raw_text):
        if in_string:
            if escape_next:
                escape_next = False
            elif char == "\\":
                escape_next = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            continue

        if char not in "[{]}":
            continue

        if char in "[{":
            if not stack:
                start_index = index
            stack.append(char)
            continue

        if not stack:
            continue

        opening = stack[-1]
        if (opening == "{" and char != "}") or (opening == "[" and char != "]"):
            stack.clear()
            start_index = None
            continue

        stack.pop()
        if stack or start_index is None:
            continue

        candidate_text = raw_text[start_index : index + 1]
        parsed_value = _parse_json_candidate(candidate_text)
        if parsed_value is not None:
            candidates.append(JsonCandidate(raw_text=candidate_text, parsed_value=parsed_value))
        start_index = None

    return candidates


def _parse_json_candidate(candidate_text: str) -> Any | None:
    try:
        parsed_value = json.loads(candidate_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(parsed_value, dict | list):
        return None

    return parsed_value
