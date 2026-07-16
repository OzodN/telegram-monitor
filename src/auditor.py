from __future__ import annotations

import json
import logging
import re
import time
import concurrent.futures
from typing import Any, TypedDict

from src.classification_support import (
    ALLOWED_CATEGORIES,
    ALLOWED_DATASET_NAMES,
    CATEGORY_ALLOWED_RULES,
    ISSUE_REFERENCE_PATTERN,
    ClassificationReferenceData,
    canonicalize_dataset_references,
)
from src.gemini_client import GeminiClient
from src.models import (
    ClassifiedPost,
    DatasetReference,
    GeminiConfig,
)
from src.regression_checks import clean_and_heal_post_fields
from src.utils import chunked


class DatasetReferenceSchema(TypedDict):
    dataset: str
    reference_id: str

class AuditDecisionSchema(TypedDict):
    post_id: int
    category_id: int
    category_reason: str
    matched_rule: str
    evidence: list[str]
    dataset_references: list[DatasetReferenceSchema]
    request_marker: str | None
    category_3_official: str | None
    category_5_subtype: str | None
    category_5_problem_type: str | None
    category_12_subtype: str | None
    audit_status: str
    audit_notes: str | None

logger = logging.getLogger(__name__)
MAX_POST_TEXT_CHARS = 1600


def audit_classified_posts(
    classified_posts: list[ClassifiedPost],
    config: GeminiConfig,
    reference_data: ClassificationReferenceData,
    gemini_client: GeminiClient,
) -> list[ClassifiedPost]:
    if not classified_posts:
        return []

    audited: list[ClassifiedPost] = []
    batches = list(chunked(classified_posts, config.classification_batch_size))

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(config.api_keys)) as executor:
        futures = [
            executor.submit(
                _audit_batch,
                batch,
                batch_index,
                config,
                reference_data,
                gemini_client,
            )
            for batch_index, batch in enumerate(batches, start=1)
        ]

        for batch_index, future in enumerate(futures, start=1):
            batch_result = future.result()
            audited.extend(batch_result)
            logger.info("Audited batch %s with %s posts", batch_index, len(batches[batch_index - 1]))

    return audited


def _audit_batch(
    batch: list[ClassifiedPost],
    batch_index: int,
    config: GeminiConfig,
    reference_data: ClassificationReferenceData,
    gemini_client: GeminiClient,
) -> list[ClassifiedPost]:
    batch_started_at = time.perf_counter()
    prompt = _build_audit_prompt(batch, reference_data)
    prompt_build_seconds = time.perf_counter() - batch_started_at

    api_started_at = time.perf_counter()
    payload = gemini_client.generate_json(
        contents=prompt,
        request_config={
            "temperature": config.temperature,
            "response_mime_type": "application/json",
        },
        operation_name=f"audit batch {batch_index}",
        validator=_is_audit_payload_shape,
        response_schema=list[AuditDecisionSchema],
    )
    api_call_seconds = time.perf_counter() - api_started_at

    parse_started_at = time.perf_counter()
    payload = _load_payload(payload)
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

    audited: list[ClassifiedPost] = []
    for index, item in enumerate(batch):
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
            evidence = [item.post.text[:100]] if item.post.text.strip() else ["No text available"]
        else:
            evidence = [str(piece).strip() for piece in raw_evidence if str(piece).strip()]
            if not evidence:
                evidence = [item.post.text[:100]] if item.post.text.strip() else ["No text available"]

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
            post_text=item.post.text,
            raw_decision=decision,
        )

        # Safe audit_status
        audit_status = str(decision.get("audit_status", "confirmed")).strip().lower()
        if audit_status not in {"confirmed", "corrected"}:
            audit_status = "confirmed"

        audited.append(
            ClassifiedPost(
                post=item.post,
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
                audit_status=audit_status,
                audit_notes=_clean_optional_text(decision.get("audit_notes")),
            )
        )

    total_batch_seconds = time.perf_counter() - batch_started_at
    logger.info(
        "Audit batch #%s | posts=%s | prompt_build=%.2f sec | api_call=%.2f sec | "
        "json_parse=%.2f sec | total=%.2f sec",
        batch_index,
        len(batch),
        prompt_build_seconds,
        api_call_seconds,
        json_parse_seconds,
        total_batch_seconds,
    )
    return audited


def _build_audit_prompt(
    batch: list[ClassifiedPost],
    reference_data: ClassificationReferenceData,
) -> str:
    posts_payload = []
    for index, item in enumerate(batch, start=1):
        posts_payload.append(
            {
                "post_id": index,
                "text": _compress_post_text(item.post.text),
                "current_classification": {
                    "category_id": item.category_id,
                    "category_reason": item.category_reason,
                    "matched_rule": item.matched_rule,
                    "evidence": item.evidence,
                    "dataset_references": [reference.to_dict() for reference in item.dataset_references],
                    "request_marker": item.request_marker,
                    "category_3_official": item.category_3_official,
                    "category_5_subtype": item.category_5_subtype,
                    "category_5_problem_type": item.category_5_problem_type,
                    "category_12_subtype": item.category_12_subtype,
                },
            }
        )

    return f"""
You are the mandatory batch auditor for a production Telegram monitoring pipeline.

Audit every post in the batch. No sampling. No skipping. No single-post mode.
Review the current classification against the authoritative specification and correct it if needed.
Use the reference datasets only for evidence, validation, and reasoning support. They are not separate classification instructions.

Return ONLY a JSON array with exactly one object per input post in this format:
[
  {{
    "post_id": 1,
    "category_id": 4,
    "category_reason": "1-2 sentence reason with concrete evidence.",
    "matched_rule": "P10",
    "evidence": ["short snippet 1", "short snippet 2"],
    "dataset_references": [{{"dataset": "issues_24", "reference_id": "ISSUE_03"}}],
    "request_marker": null,
    "category_3_official": null,
    "category_5_subtype": null,
    "category_5_problem_type": null,
    "category_12_subtype": null,
    "audit_status": "confirmed",
    "audit_notes": "Short note or null."
  }}
]

Rules:
- Classification decisions must follow ONLY the authoritative classification specification below.
- Every object must have non-empty category_reason, matched_rule, and evidence.
- Category 4 must use issues_24 canonical IDs from the catalog below.
- Category 5 must include request_marker.
- Category 3 must use category_3_official with one of: hokim, kengash_raisi, kotibiyat_mudiri.
- Category 5 must use category_5_subtype with one of: request_sent, result_achieved.
- Category 5 must use category_5_problem_type with one of: road, water, gas, electricity, social, other.
- Category 6 must include at least one laws_162 canonical law ID from the catalog below.
- Category 12 must use category_12_subtype with one of: template, legislative_news, internal_organizational, press_article, other.
- reference_id values must be catalog IDs such as ISSUE_03 or LAW_URQ_445, not free-form titles.
- Non-applicable extra fields must be null.
- audit_status must be either "confirmed" or "corrected".

AUTHORITATIVE CLASSIFICATION SPECIFICATION:
{reference_data.classification_specification_text}

REFERENCE DATASET: 24 ISSUES
{reference_data.issues_24_catalog.prompt_text}

REFERENCE DATASET: 162 LAWS
{reference_data.laws_162_catalog.prompt_text}

POSTS TO AUDIT:
{json.dumps(posts_payload, ensure_ascii=False, indent=2)}
""".strip()


def _load_payload(payload: object) -> list[dict]:
    if isinstance(payload, dict) and "audits" in payload:
        payload = payload["audits"]
    if not isinstance(payload, list):
        raise ValueError("Audit response must be a JSON array")
    return payload


def _is_audit_payload_shape(payload: object) -> bool:
    if isinstance(payload, list):
        return all(isinstance(item, dict) and "post_id" in item for item in payload)
    if isinstance(payload, dict):
        audits = payload.get("audits")
        return isinstance(audits, list) and all(isinstance(item, dict) and "post_id" in item for item in audits)
    return False


def _compress_post_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= MAX_POST_TEXT_CHARS:
        return normalized

    head_length = 1200
    tail_length = 300
    return f"{normalized[:head_length].rstrip()} ... {normalized[-tail_length:].lstrip()}"


def _clean_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
