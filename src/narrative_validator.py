from __future__ import annotations

import re

from typing import Any
from src.classification_support import ALLOWED_CATEGORIES, TREND_CATEGORIES
from src.models import AggregatedReport, PathsConfig, ReportNarrative
from src.narrative_generator import build_narrative_facts


PROHIBITED_PHRASES = (
    "эҳтимол",
    "афтидан",
    "кўринишича",
    "бу шундан далолат беради",
    "сабаби шуки",
    "аномалия",
)
TREND_PATTERNS = (
    "нисбатан",
    "таққослаганда",
    "солиштирганда",
    "ошди",
    "камайди",
    "кўпайди",
    "пасайди",
    "яхшиланди",
    "ёмонлашди",
)


def normalize_section_prefix(text: str, category_id: int) -> str:
    cleaned = text.strip()
    # Matches Category X-, X. , X) , [X] , X: , X-toifa, X-kategoriya
    pattern = r"^(?:Category\s+)?(?:" + str(category_id) + r")\s*[-).\]:]\s*|^(?:" + str(category_id) + r")-(?:toifa|тоифа|kategoriya|категория)\s*"
    if re.match(pattern, cleaned, re.IGNORECASE):
        cleaned = re.sub(pattern, "", cleaned, count=1).strip()
    return f"{category_id}. {cleaned}"


def _extract_all_numbers_from_facts(data: Any) -> set[str]:
    tokens = set()
    if isinstance(data, dict):
        for val in data.values():
            tokens.update(_extract_all_numbers_from_facts(val))
    elif isinstance(data, list):
        for item in data:
            tokens.update(_extract_all_numbers_from_facts(item))
    elif isinstance(data, (int, float)):
        val_str = str(int(data))
        tokens.add(val_str)
        if len(val_str) == 1:
            tokens.add(f"0{val_str}")
    elif isinstance(data, str):
        # Scan strings for embedded numeric sequences (like ISO dates)
        for token in re.findall(r"\d+", data):
            tokens.add(token)
            if len(token) == 1:
                tokens.add(f"0{token}")
    return tokens


def validate_narrative(narrative: ReportNarrative, aggregated: AggregatedReport, paths: PathsConfig) -> dict:
    # Heal prefix anchors in-place
    for category_id in ALLOWED_CATEGORIES:
        key_to_use = category_id
        section_text = narrative.category_sections.get(category_id)
        if section_text is None:
            section_text = narrative.category_sections.get(str(category_id), "")
            key_to_use = str(category_id)
            
        healed_text = normalize_section_prefix(section_text, category_id)
        narrative.category_sections[key_to_use] = healed_text

    # Heal final heading in-place
    cleaned_heading = narrative.final_heading.strip()
    if len(cleaned_heading) < 50 and re.search(r"13|турли|масалалар|turli|masalalar", cleaned_heading, re.IGNORECASE):
        narrative.final_heading = "13. Турли масалалар"

    errors: list[str] = []
    warnings: list[str] = []
    text_by_section = {
        "summary": narrative.summary,
        **{
            str(category_id): narrative.category_sections.get(
                int(category_id), narrative.category_sections.get(str(category_id), "")
            ).strip()
            for category_id in ALLOWED_CATEGORIES
        },
        "final_heading": narrative.final_heading,
        "final_observation": narrative.final_observation,
    }

    all_text = "\n".join(text_by_section.values())
    normalized_text = _normalize_text(all_text)

    for phrase in PROHIBITED_PHRASES:
        if _normalize_text(phrase) in normalized_text:
            errors.append(f"Prohibited phrase detected: {phrase}")

    expected_prefixes = {category_id: f"{category_id}." for category_id in ALLOWED_CATEGORIES}
    for category_id, prefix in expected_prefixes.items():
        section_text = narrative.category_sections.get(
            int(category_id), narrative.category_sections.get(str(category_id), "")
        ).strip()
        if not section_text.startswith(prefix):
            errors.append(f"Category {category_id} section must start with '{prefix}'")

    if narrative.final_heading.strip() != "13. Турли масалалар":
        errors.append(f"Final heading must be exactly '13. Турли масалалар', but got: '{narrative.final_heading}'")

    allowed_numbers = _build_allowed_numbers(aggregated, paths)
    observed_numbers = re.findall(r"\d+", all_text)
    for token in observed_numbers:
        if token not in allowed_numbers:
            errors.append(f"Unexpected numeric token in narrative: {token}")

    if aggregated.prior_period_reference is None or aggregated.prior_period_reference.get("spec_version") != aggregated.current_spec_version:
        trend_text = _normalize_text(
            "\n".join(
                narrative.category_sections.get(
                    int(cat_id), narrative.category_sections.get(str(cat_id), "")
                ).strip()
                for cat_id in TREND_CATEGORIES
            )
            + "\n"
            + narrative.final_observation
        )
        for pattern in TREND_PATTERNS:
            if _normalize_text(pattern) in trend_text:
                errors.append(f"Trend language is not allowed without comparable prior-period data: {pattern}")

    report = {
        "stage": "narrative_validation",
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    if errors:
        raise ValueError("\n".join(errors))
    return report


def _build_allowed_numbers(aggregated: AggregatedReport, paths: PathsConfig) -> set[str]:
    tokens = {str(value) for value in range(0, 32)}
    tokens.update({"2024", "2025", "2026", "2027"})

    # Extract facts sent to LLM and add all embedded numbers
    facts = build_narrative_facts(aggregated)
    tokens.update(_extract_all_numbers_from_facts(facts))

    # Extract reference constants from the narrative specification
    from src.utils import read_utf8_text
    spec_text = read_utf8_text(paths.narrative_specification_md)
    tokens.update(re.findall(r"\d+", spec_text))

    # Ensure period day count and raw date parts are included
    tokens.add(str((aggregated.period.end.date() - aggregated.period.start.date()).days + 1))
    for part in (
        aggregated.period.start.year,
        aggregated.period.start.month,
        aggregated.period.start.day,
        aggregated.period.end.year,
        aggregated.period.end.month,
        aggregated.period.end.day,
    ):
        tokens.add(str(part))
        if part < 10:
            tokens.add(f"0{part}")

    for stats in aggregated.channel_stats:
        tokens.add(str(stats.total_posts))
        tokens.add(str(stats.average_views))
        tokens.add(str(stats.total_views))
        tokens.add(str(stats.viewed_posts_count))
        tokens.add(str(stats.subscriber_count or 0))
        for value in stats.category_counts.values():
            tokens.add(str(value))
        for item in stats.daily_post_counts:
            tokens.add(str(item["count"]))
            year, month, day = item["date"].split("-")
            tokens.update({year, str(int(month)), str(int(day))})
            if int(month) < 10:
                tokens.add(f"0{int(month)}")
            if int(day) < 10:
                tokens.add(f"0{int(day)}")
        for percent in _category_percentages_for_channel(stats):
            tokens.add(str(percent))

    for percent in _system_percentages(aggregated):
        tokens.add(str(percent))

    return tokens


def _category_percentages_for_channel(stats) -> set[int]:
    if stats.total_posts == 0:
        return {0}
    return {round(count * 100 / stats.total_posts) for count in stats.category_counts.values()}


def _system_percentages(aggregated: AggregatedReport) -> set[int]:
    totals = aggregated.totals_by_category
    total_posts = totals.get(1, totals.get("1", 0))
    if total_posts == 0:
        return {0}
    return {
        round(totals.get(category_id, totals.get(str(category_id), 0)) * 100 / total_posts)
        for category_id in ALLOWED_CATEGORIES
    }


def _normalize_text(value: str) -> str:
    text = value.casefold().replace("’", "'").replace("‘", "'").replace("`", "'")
    return re.sub(r"\s+", " ", text).strip()
