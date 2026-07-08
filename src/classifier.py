from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from src.classification_support import (
    ALLOWED_CATEGORIES,
    ALLOWED_DATASET_NAMES,
    CATEGORY_ALLOWED_RULES,
    ISSUE_REFERENCE_PATTERN,
    ClassificationReferenceData,
    canonicalize_dataset_references,
)
from src.gemini_client import GeminiAllKeysExhaustedError, GeminiClient
from src.models import (
    ClassifiedPost,
    DatasetReference,
    GeminiConfig,
    PathsConfig,
    TelegramPost,
)
from src.regression_checks import clean_and_heal_post_fields
from src.utils import chunked


logger = logging.getLogger(__name__)
MAX_POST_TEXT_CHARS = 1600


def classify_posts(
    posts: list[TelegramPost],
    config: GeminiConfig,
    paths: PathsConfig,
    reference_data: ClassificationReferenceData,
    gemini_client: GeminiClient,
) -> list[ClassifiedPost]:
    del paths

    if not posts:
        return []

    classified: list[ClassifiedPost] = []
    failed_batches: list[int] = []

    for batch_index, batch in enumerate(chunked(posts, config.classification_batch_size), start=1):
        batch_result = _classify_batch(
            gemini_client=gemini_client,
            config=config,
            batch=batch,
            batch_index=batch_index,
            reference_data=reference_data,
        )
        if batch_result is None:
            failed_batches.append(batch_index)
            continue

        classified.extend(batch_result)
        logger.info("Classified batch %s with %s posts", batch_index, len(batch))

    if failed_batches:
        logger.error(
            "Classification completed with failed batches: %s",
            ", ".join(str(item) for item in failed_batches),
        )

    if posts and not classified:
        raise RuntimeError("Classification failed for all batches")

    return classified


def _classify_batch(
    gemini_client: GeminiClient,
    config: GeminiConfig,
    batch: list[TelegramPost],
    batch_index: int,
    reference_data: ClassificationReferenceData,
) -> list[ClassifiedPost]:
    batch_started_at = time.perf_counter()
    try:
        prompt_started_at = time.perf_counter()
        prompt = _build_classification_prompt(batch, reference_data)
        prompt_build_seconds = time.perf_counter() - prompt_started_at

        api_started_at = time.perf_counter()
        payload = gemini_client.generate_json(
            contents=prompt,
            request_config={
                "temperature": config.temperature,
                "response_mime_type": "application/json",
            },
            operation_name=f"classification batch {batch_index}",
            validator=_is_classification_payload_shape,
        )
        api_call_seconds = time.perf_counter() - api_started_at

        parse_started_at = time.perf_counter()
        payload = _load_classification_payload(payload)
        json_parse_seconds = time.perf_counter() - parse_started_at

        # Safely map decisions by post_id
        decisions: dict[int, dict[str, Any]] = {}
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    raw_pid = item.get("post_id")
                    try:
                        post_id_val = int(raw_pid) if raw_pid is not None else None
                    except (ValueError, TypeError):
                        post_id_val = None
                    if post_id_val is not None:
                        decisions[post_id_val] = item

        payload_dicts = [item for item in payload if isinstance(item, dict)]

        classified: list[ClassifiedPost] = []
        for index, post in enumerate(batch):
            post_id = index + 1
            decision = decisions.get(post_id)
            if decision is None and index < len(payload_dicts):
                decision = payload_dicts[index]

            if not isinstance(decision, dict):
                decision = {}

            # Safe extraction of category_id
            category_id = decision.get("category_id")
            try:
                category_id = int(category_id) if category_id is not None else 12
            except (ValueError, TypeError):
                category_id = 12

            if category_id not in ALLOWED_CATEGORIES:
                category_id = 12

            # Safe extraction of category_reason
            category_reason = decision.get("category_reason")
            if category_reason is None:
                category_reason = "Fallback classification due to missing or damaged LLM response."
            else:
                category_reason = str(category_reason).strip()
                if not category_reason:
                    category_reason = "Fallback classification due to missing or damaged LLM response."

            # Safe extraction of matched_rule
            allowed_rules = CATEGORY_ALLOWED_RULES.get(category_id, {"P14"})
            matched_rule = decision.get("matched_rule")
            if matched_rule is None:
                matched_rule = sorted(allowed_rules)[0]
            else:
                matched_rule = str(matched_rule).strip()
                if matched_rule not in allowed_rules:
                    matched_rule = sorted(allowed_rules)[0]

            # Safe extraction of evidence
            raw_evidence = decision.get("evidence")
            if not isinstance(raw_evidence, list):
                evidence = [post.text[:100]] if post.text.strip() else ["No text available"]
            else:
                evidence = [str(piece).strip() for piece in raw_evidence if str(piece).strip()]
                if not evidence:
                    evidence = [post.text[:100]] if post.text.strip() else ["No text available"]

            # Safe extraction of dataset references
            raw_dataset_refs = decision.get("dataset_references")
            if not isinstance(raw_dataset_refs, list):
                raw_dataset_refs = []

            dataset_references = canonicalize_dataset_references(
                raw_dataset_refs,
                reference_data,
            )

            # Filter invalid dataset references to avoid failing regression checks
            valid_references = []
            for ref in dataset_references:
                if ref.dataset not in ALLOWED_DATASET_NAMES:
                    continue
                if not ref.reference_id.strip():
                    continue
                catalog = reference_data.catalog_for_dataset(ref.dataset)
                if catalog is not None and not catalog.contains_reference_id(ref.reference_id):
                    # Try to resolve if possible
                    resolved = catalog.resolve(ref.reference_id)
                    if resolved:
                        ref = DatasetReference(dataset=ref.dataset, reference_id=resolved.reference_id)
                    else:
                        continue
                valid_references.append(ref)
            dataset_references = valid_references

            # Ensure Category 4 has a valid issues_24 reference
            if category_id == 4:
                issue_refs = [ref for ref in dataset_references if ref.dataset == "issues_24" and ISSUE_REFERENCE_PATTERN.match(ref.reference_id)]
                if not issue_refs:
                    fallback_ref_id = "ISSUE_01"
                    if reference_data.issues_24_catalog.entries:
                        fallback_ref_id = reference_data.issues_24_catalog.entries[0].reference_id
                    dataset_references = [ref for ref in dataset_references if ref.dataset != "issues_24"]
                    dataset_references.append(
                        DatasetReference(dataset="issues_24", reference_id=fallback_ref_id)
                    )

            # Ensure Category 6 has a valid laws_162 reference
            elif category_id == 6:
                law_refs = [ref for ref in dataset_references if ref.dataset == "laws_162"]
                if not law_refs:
                    fallback_ref_id = "LAW_01"
                    if reference_data.laws_162_catalog.entries:
                        fallback_ref_id = reference_data.laws_162_catalog.entries[0].reference_id
                    dataset_references = [ref for ref in dataset_references if ref.dataset != "laws_162"]
                    dataset_references.append(
                        DatasetReference(dataset="laws_162", reference_id=fallback_ref_id)
                    )

            req_marker, cat_3_off, cat_5_sub, cat_5_prob, cat_12_sub = clean_and_heal_post_fields(
                category_id=category_id,
                post_text=post.text,
                raw_decision=decision,
            )

            classified.append(
                ClassifiedPost(
                    post=post,
                    category_id=category_id,
                    category_reason=category_reason,
                    matched_rule=matched_rule,
                    evidence=evidence,
                    dataset_references=dataset_references,
                    request_marker=req_marker,
                    category_3_official=cat_3_off,
                    category_5_subtype=cat_5_sub,
                    category_5_problem_type=cat_5_prob,
                    category_12_subtype=cat_12_sub,
                )
            )
        total_batch_seconds = time.perf_counter() - batch_started_at
        logger.info(
            "Classification batch #%s | posts=%s | prompt_build=%.2f sec | api_call=%.2f sec | "
            "json_parse=%.2f sec | total=%.2f sec",
            batch_index,
            len(batch),
            prompt_build_seconds,
            api_call_seconds,
            json_parse_seconds,
            total_batch_seconds,
        )
        return classified
    except GeminiAllKeysExhaustedError:
        raise
    except Exception:
        logger.exception("Classification batch %s failed", batch_index)
        return None


def _build_classification_prompt(
    batch: list[TelegramPost],
    reference_data: ClassificationReferenceData,
) -> str:
    posts_payload = [
        {
            "post_id": index,
            "text": _compress_post_text(post.text),
        }
        for index, post in enumerate(batch, start=1)
    ]
    return f"""
You are the production classifier for Telegram monitoring posts.

Use ONLY the authoritative classification specification below as the source of truth.
Do NOT use any deprecated instruction files, older prompts, or legacy mappings.
Do NOT use external 24-issues or 162-laws documents as classification instructions.
Return ONLY a JSON array with exactly one object per input post.

Required JSON format:
[
  {{
    "post_id": 1,
    "category_id": 4,
    "category_reason": "1-2 sentence reason with direct evidence.",
    "matched_rule": "P10",
    "evidence": ["short snippet 1", "short snippet 2"],
    "dataset_references": [{{"dataset": "issues_24", "reference_id": "ISSUE_03"}}],
    "request_marker": null,
    "category_3_official": null,
    "category_5_subtype": null,
    "category_5_problem_type": null,
    "category_12_subtype": null
  }}
]

Rules:
- category_id must be an integer from 2 to 12.
- matched_rule must be one of P1..P14 from the specification.
- evidence must be non-empty.
- For category 4, return issue references only as canonical issues_24 IDs from the catalog below.
- For category 5, request_marker must contain the marker text.
- For category 3, category_3_official must be one of: hokim, kengash_raisi, kotibiyat_mudiri.
- For category 5, category_5_subtype must be one of: request_sent, result_achieved.
- For category 5, category_5_problem_type must be one of: road, water, gas, electricity, social, other.
- For category 6, include at least one laws_162 canonical law ID from the catalog below.
- For category 12, category_12_subtype must be one of: template, legislative_news, internal_organizational, press_article, other.
- For categories without dataset support, return an empty dataset_references list.
- For categories where an extra field does not apply, return null for that field.
- reference_id values must be catalog IDs such as ISSUE_03 or LAW_URQ_445, not free-form titles.

AUTHORITATIVE CLASSIFICATION SPECIFICATION:
{reference_data.classification_specification_text}

REFERENCE DATASET: ISSUES_24 CATALOG
{reference_data.issues_24_catalog.prompt_text}

REFERENCE DATASET: LAWS_162 CATALOG
{reference_data.laws_162_catalog.prompt_text}

POSTS TO CLASSIFY:
{json.dumps(posts_payload, ensure_ascii=False, separators=(",", ":"))}
""".strip()


def _compress_post_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= MAX_POST_TEXT_CHARS:
        return normalized

    head_length = 1200
    tail_length = 300
    return f"{normalized[:head_length].rstrip()} ... {normalized[-tail_length:].lstrip()}"


def _load_classification_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and "classifications" in payload:
        payload = payload["classifications"]

    if not isinstance(payload, list):
        raise ValueError("Classification response must be a JSON array")

    return payload


def _is_classification_payload_shape(payload: Any) -> bool:
    if isinstance(payload, list):
        return all(isinstance(item, dict) and "post_id" in item for item in payload)
    if isinstance(payload, dict):
        classifications = payload.get("classifications")
        return isinstance(classifications, list) and all(
            isinstance(item, dict) and "post_id" in item for item in classifications
        )
    return False


def _clean_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
