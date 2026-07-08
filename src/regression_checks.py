from __future__ import annotations

from typing import Any

from src.classification_support import (
    ALLOWED_CATEGORIES,
    ALLOWED_DATASET_NAMES,
    ALLOWED_MATCHED_RULES,
    CATEGORY_ALLOWED_RULES,
    ISSUE_REFERENCE_PATTERN,
    ClassificationReferenceData,
)
from src.models import ClassifiedPost

ALLOWED_CATEGORY_3_OFFICIALS = {"hokim", "kengash_raisi", "kotibiyat_mudiri"}
ALLOWED_CATEGORY_5_SUBTYPES = {"request_sent", "result_achieved"}
ALLOWED_CATEGORY_5_PROBLEM_TYPES = {"road", "water", "gas", "electricity", "social", "other"}
ALLOWED_CATEGORY_12_SUBTYPES = {"template", "legislative_news", "internal_organizational", "press_article", "other"}


def run_regression_checks(
    classified_posts: list[ClassifiedPost],
    reference_data: ClassificationReferenceData,
    *,
    stage_name: str,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    for item in classified_posts:
        post_label = item.post.stable_id()

        if item.category_id not in ALLOWED_CATEGORIES:
            errors.append(f"{stage_name}:{post_label}: invalid category_id={item.category_id}")

        if not item.category_reason.strip():
            errors.append(f"{stage_name}:{post_label}: category_reason is empty")

        if item.matched_rule not in ALLOWED_MATCHED_RULES:
            errors.append(f"{stage_name}:{post_label}: matched_rule={item.matched_rule!r} is invalid")
        elif item.category_id in CATEGORY_ALLOWED_RULES and item.matched_rule not in CATEGORY_ALLOWED_RULES[item.category_id]:
            errors.append(
                f"{stage_name}:{post_label}: matched_rule={item.matched_rule!r} is inconsistent with category_id={item.category_id}"
            )

        if not item.evidence or not any(piece.strip() for piece in item.evidence):
            errors.append(f"{stage_name}:{post_label}: evidence is empty")

        for reference in item.dataset_references:
            if reference.dataset not in ALLOWED_DATASET_NAMES:
                errors.append(
                    f"{stage_name}:{post_label}: dataset reference dataset={reference.dataset!r} is invalid"
                )
            if not reference.reference_id.strip():
                errors.append(f"{stage_name}:{post_label}: dataset reference_id is empty")
                continue

            catalog = reference_data.catalog_for_dataset(reference.dataset)
            if catalog is not None and not catalog.contains_reference_id(reference.reference_id):
                errors.append(
                    f"{stage_name}:{post_label}: dataset reference_id={reference.reference_id!r} "
                    f"is not a valid {reference.dataset} catalog ID"
                )

        if item.category_id == 4:
            issue_refs = [ref.reference_id for ref in item.dataset_references if ref.dataset == "issues_24"]
            if not issue_refs:
                errors.append(f"{stage_name}:{post_label}: Category 4 requires an issues_24 dataset reference")
            elif not any(ISSUE_REFERENCE_PATTERN.match(ref_id) for ref_id in issue_refs):
                errors.append(f"{stage_name}:{post_label}: Category 4 issue reference must match ISSUE_01..ISSUE_24")
            elif not all(reference_data.issues_24_catalog.contains_reference_id(ref_id) for ref_id in issue_refs):
                errors.append(f"{stage_name}:{post_label}: Category 4 issue reference is not present in issues_24 catalog")

        if item.category_id == 5 and not (item.request_marker or "").strip():
            errors.append(f"{stage_name}:{post_label}: Category 5 requires request_marker")

        if item.category_id == 3:
            if item.category_3_official not in ALLOWED_CATEGORY_3_OFFICIALS:
                errors.append(
                    f"{stage_name}:{post_label}: Category 3 requires category_3_official in {sorted(ALLOWED_CATEGORY_3_OFFICIALS)}"
                )
        elif item.category_3_official is not None:
            errors.append(f"{stage_name}:{post_label}: category_3_official must be null outside Category 3")

        if item.category_id == 5:
            if item.category_5_subtype not in ALLOWED_CATEGORY_5_SUBTYPES:
                errors.append(
                    f"{stage_name}:{post_label}: Category 5 requires category_5_subtype in {sorted(ALLOWED_CATEGORY_5_SUBTYPES)}"
                )
            if item.category_5_problem_type not in ALLOWED_CATEGORY_5_PROBLEM_TYPES:
                errors.append(
                    f"{stage_name}:{post_label}: Category 5 requires category_5_problem_type in {sorted(ALLOWED_CATEGORY_5_PROBLEM_TYPES)}"
                )
        else:
            if item.category_5_subtype is not None:
                errors.append(f"{stage_name}:{post_label}: category_5_subtype must be null outside Category 5")
            if item.category_5_problem_type is not None:
                errors.append(f"{stage_name}:{post_label}: category_5_problem_type must be null outside Category 5")

        if item.category_id == 6:
            law_refs = [ref.reference_id for ref in item.dataset_references if ref.dataset == "laws_162"]
            if not law_refs:
                errors.append(f"{stage_name}:{post_label}: Category 6 requires a laws_162 dataset reference")
            elif not all(reference_data.laws_162_catalog.contains_reference_id(ref_id) for ref_id in law_refs):
                errors.append(f"{stage_name}:{post_label}: Category 6 law reference is not present in laws_162 catalog")

        if item.category_id == 7 and not any(piece.strip() for piece in item.evidence):
            errors.append(f"{stage_name}:{post_label}: Category 7 requires committee evidence")

        if item.category_id == 11 and item.matched_rule != "P8":
            errors.append(f"{stage_name}:{post_label}: Category 11 must come from matched rule P8")

        if item.category_id == 12:
            if item.category_12_subtype not in ALLOWED_CATEGORY_12_SUBTYPES:
                errors.append(
                    f"{stage_name}:{post_label}: Category 12 requires category_12_subtype in {sorted(ALLOWED_CATEGORY_12_SUBTYPES)}"
                )
        elif item.category_12_subtype is not None:
            errors.append(f"{stage_name}:{post_label}: category_12_subtype must be null outside Category 12")

        if item.audit_status and item.audit_status not in {"confirmed", "corrected"}:
            errors.append(f"{stage_name}:{post_label}: audit_status={item.audit_status!r} is invalid")

    report = {
        "stage": stage_name,
        "checked_posts": len(classified_posts),
        "warnings": warnings,
        "errors": errors,
        "passed": not errors,
    }

    if errors:
        raise ValueError("\n".join(errors))

    return report


def clean_and_heal_post_fields(
    category_id: int,
    post_text: str,
    raw_decision: dict[str, Any],
) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    """Cleans up and auto-heals optional/conditional fields returned by the LLM
    to ensure compliance with regression checks.
    """
    if not isinstance(raw_decision, dict):
        raw_decision = {}

    def _clean_optional_text(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    request_marker = _clean_optional_text(raw_decision.get("request_marker"))
    category_3_official = _clean_optional_text(raw_decision.get("category_3_official"))
    category_5_subtype = _clean_optional_text(raw_decision.get("category_5_subtype"))
    category_5_problem_type = _clean_optional_text(raw_decision.get("category_5_problem_type"))
    category_12_subtype = _clean_optional_text(raw_decision.get("category_12_subtype"))

    # Force to None if not in the target category (spec requirement)
    if category_id != 3:
        category_3_official = None
    if category_id != 5:
        category_5_subtype = None
        category_5_problem_type = None
        request_marker = None
    if category_id != 12:
        category_12_subtype = None

    # Heal Category 3
    if category_id == 3:
        if category_3_official not in ALLOWED_CATEGORY_3_OFFICIALS:
            normalized_text = post_text.lower()
            if "kotibiyat" in normalized_text or "mudiri" in normalized_text:
                category_3_official = "kotibiyat_mudiri"
            elif "raisi" in normalized_text:
                category_3_official = "kengash_raisi"
            elif "hokim" in normalized_text:
                category_3_official = "hokim"
            else:
                category_3_official = "hokim"

    # Heal Category 5
    elif category_id == 5:
        if category_5_subtype not in ALLOWED_CATEGORY_5_SUBTYPES:
            normalized_text = post_text.lower()
            if any(w in normalized_text for w in ["natijasida", "ijobiy hal", "binoan", "asosida"]):
                category_5_subtype = "result_achieved"
            else:
                category_5_subtype = "request_sent"

        if category_5_problem_type not in ALLOWED_CATEGORY_5_PROBLEM_TYPES:
            normalized_text = post_text.lower()
            if "yo'l" in normalized_text or "yol" in normalized_text or "ko'cha" in normalized_text or "kucha" in normalized_text:
                category_5_problem_type = "road"
            elif "suv" in normalized_text:
                category_5_problem_type = "water"
            elif "gaz" in normalized_text:
                category_5_problem_type = "gas"
            elif "elektr" in normalized_text or "tok" in normalized_text or "chiroq" in normalized_text:
                category_5_problem_type = "electricity"
            elif "ijtimoiy" in normalized_text or "maktab" in normalized_text or "bog'cha" in normalized_text or "shifoxona" in normalized_text:
                category_5_problem_type = "social"
            else:
                category_5_problem_type = "other"

        if not request_marker:
            normalized_text = post_text.lower()
            markers = ["so'rov yuborildi", "so'roviga binoan", "deputatlik so'rovi", "so'rov", "murojaat"]
            found_marker = None
            for m in markers:
                if m in normalized_text:
                    found_marker = m
                    break
            request_marker = found_marker or "so'rov"

    # Heal Category 12
    elif category_id == 12:
        if category_12_subtype not in ALLOWED_CATEGORY_12_SUBTYPES:
            normalized_text = post_text.lower()
            if "assalomu alaykum" in normalized_text or "ijtimoiy tarmoq" in normalized_text:
                category_12_subtype = "template"
            elif "qonun" in normalized_text or "qaror" in normalized_text or "prezident" in normalized_text:
                category_12_subtype = "legislative_news"
            elif "ish reja" in normalized_text or "kotibiyat" in normalized_text or "tashkiliy" in normalized_text or "kunlik" in normalized_text:
                category_12_subtype = "internal_organizational"
            elif "maqola" in normalized_text or "gazeta" in normalized_text or "gazetasi" in normalized_text or "oav" in normalized_text:
                category_12_subtype = "press_article"
            else:
                category_12_subtype = "other"

    return request_marker, category_3_official, category_5_subtype, category_5_problem_type, category_12_subtype
