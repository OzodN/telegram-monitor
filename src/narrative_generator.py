from __future__ import annotations

import json
import logging
from collections import Counter
from typing import Any

from src.classification_support import ALLOWED_CATEGORIES, TREND_CATEGORIES
from src.gemini_client import GeminiClient
from src.models import AggregatedReport, ClassifiedPost, GeminiConfig, PathsConfig, ReportNarrative
from src.utils import read_utf8_text


logger = logging.getLogger(__name__)
PROHIBITED_PHRASES = [
    "ehtimol",
    "aftidan",
    "ko'rinishicha",
    "ko‘rinishicha",
    "bu shundan dalolat beradi",
    "sababi shuki",
    "balki",
    "deb taxmin qilinadi",
    "buning sababi",
]
TREND_DISCLAIMER = "Oldingi davr bo'yicha taqqoslash uchun baza mavjud emas."
METHODOLOGY_DISCLAIMER = (
    "Ushbu davr tasnifi oldingi davr bilan solishtirish imkonini bermaydi, chunki tasniflash uslubiyati o'zgargan."
)


def generate_narrative(
    classified_posts: list[ClassifiedPost],
    aggregated: AggregatedReport,
    config: GeminiConfig,
    paths: PathsConfig,
    gemini_client: GeminiClient,
) -> ReportNarrative:
    del classified_posts

    narrative_facts = build_narrative_facts(aggregated)
    prompt = _build_narrative_prompt(narrative_facts, paths)
    payload = gemini_client.generate_json(
        contents=prompt,
        request_config={
            "temperature": 0,
            "response_mime_type": "application/json",
        },
        operation_name="narrative generation",
        validator=_is_narrative_payload_shape,
    )
    category_sections = {category_id: "" for category_id in ALLOWED_CATEGORIES}
    for key, value in payload["category_sections"].items():
        category_sections[int(key)] = str(value).strip()

    return ReportNarrative(
        summary=str(payload["summary"]).strip(),
        category_sections=category_sections,
        final_heading=str(payload["final_heading"]).strip(),
        final_observation=str(payload["final_observation"]).strip(),
    )


def _build_narrative_prompt(narrative_facts: dict[str, Any], paths: PathsConfig) -> str:
    specification_text = read_utf8_text(paths.narrative_specification_md)

    return f"""
Siz ishlab turgan production Telegram monitoring tizimi uchun rasmiy haftalik izoh yozasiz.

Manba qoidalari:
- Quyidagi narrative specification yagona authoritative hujjatdir.
- Faqat FACTS JSON ichidagi ma'lumotlardan foydalaning.
- Hech qanday sabab, motiv, siyosiy talqin, yashirin trend yoki yetishmayotgan faktni ixtiro qilmang.
- Hisob-kitob qilmang. Barcha sonlar va foizlar FACTS JSON ichida tayyor berilgan.
- Qo'llab-quvvatlanmagan maydonlar bo'yicha da'vo qilmang.
- Quyidagi so'z va iboralarni ishlatmang: {", ".join(PROHIBITED_PHRASES)}.
- Band 10 va 11 da trend faqat trend_status=available bo'lsa yoziladi. Aks holda facts ichidagi disclaimer matnidan foydalaning.
- Har bir band alohida paragraf bo'lsin.
- category_sections ichidagi har bir qiymat (masalan, "2" toifaga tegishli matn) mutlaqo mos ravishda "2. " (yoki "3. ", "4. " va hokazo) prefiksi bilan boshlanishi shart. "2-toifa:", "2) ", "[2] " kabi boshqa formatlar qat'iyan taqiqlanadi!
- Final observation faqat oldingi bandlarda allaqachon aytilgan nol holatlar yoki anomaly holatlarini qisqa jamlasin.
- Javob faqat JSON bo'lsin.

AUTHORITATIVE NARRATIVE SPECIFICATION:
{specification_text}

FACTS JSON:
{json.dumps(narrative_facts, ensure_ascii=False, indent=2)}

Qat'iy JSON formati:
{{
  "summary": "1-band mazmunidagi kirish paragrafi",
  "category_sections": {{
    "2": "2. [Matn faqat '2. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]",
    "3": "3. [Matn faqat '3. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]",
    "4": "4. [Matn faqat '4. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]",
    "5": "5. [Matn faqat '5. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]",
    "6": "6. [Matn faqat '6. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]",
    "7": "7. [Matn faqat '7. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]",
    "8": "8. [Matn faqat '8. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]",
    "9": "9. [Matn faqat '9. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]",
    "10": "10. [Matn faqat '10. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]",
    "11": "11. [Matn faqat '11. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]",
    "12": "12. [Matn faqat '12. ' prefiksi bilan boshlanishi shart. Boshqa formatlar taqiqlanadi]"
  }},
  "final_heading": "13. Turli masalalar",
  "final_observation": "..."
}}
""".strip()


def build_narrative_facts(aggregated: AggregatedReport) -> dict[str, Any]:
    total_posts = aggregated.totals_by_category[1]
    channel_count = len(aggregated.channel_stats)
    anomalies = _build_anomalies(aggregated)

    facts = {
        "period": {
            "start": aggregated.period.start.date().isoformat(),
            "end": aggregated.period.end.date().isoformat(),
            "days": (aggregated.period.end.date() - aggregated.period.start.date()).days + 1,
            "channel_count": channel_count,
            "is_full_week": (aggregated.period.end.date() - aggregated.period.start.date()).days + 1 == 7,
        },
        "summary": {
            "total_posts": total_posts,
            "leaders": _leaders_from_total_posts(aggregated),
            "low_performers": _low_performers_from_total_posts(aggregated),
            "zero_day_channels": _zero_day_channels(aggregated),
        },
        "bands": {},
        "anomalies": anomalies,
        "final_observation_points": _build_final_observation_points(aggregated, anomalies),
    }

    for category_id in ALLOWED_CATEGORIES:
        facts["bands"][str(category_id)] = _build_category_band_facts(aggregated, category_id)

    return facts


def _build_category_band_facts(aggregated: AggregatedReport, category_id: int) -> dict[str, Any]:
    total = aggregated.totals_by_category[category_id]
    system_total_posts = max(aggregated.totals_by_category[1], 1)
    counts_by_channel = {item.council_name: item.category_counts[category_id] for item in aggregated.channel_stats}
    leaders = _leaders(counts_by_channel)
    low_performers = _low_performers(counts_by_channel)
    zero_channels = _zero_channels(counts_by_channel)

    band = {
        "total": total,
        "overall_percent": round(total * 100 / system_total_posts) if aggregated.totals_by_category[1] else 0,
        "leaders": leaders,
        "low_performers": low_performers,
        "zero_channels": zero_channels,
        "nonzero_channels": [
            {
                "council_name": item.council_name,
                "count": item.category_counts[category_id],
                "percent_of_channel_posts": round(item.category_counts[category_id] * 100 / item.total_posts)
                if item.total_posts
                else 0,
            }
            for item in aggregated.channel_stats
            if item.category_counts[category_id] > 0
        ],
        "dominant_channel_anomaly": _category_dominant_channel_anomaly(aggregated, category_id),
    }

    if category_id == 3:
        band.update(_build_category_3_facts(aggregated))
    elif category_id == 4:
        band.update(_build_category_4_facts(aggregated))
    elif category_id == 5:
        band.update(_build_category_5_facts(aggregated))
    elif category_id == 6:
        band.update(_build_category_6_facts(aggregated))
    elif category_id in TREND_CATEGORIES:
        band.update(_build_trend_facts(aggregated))
    elif category_id == 12:
        band.update(_build_category_12_facts(aggregated))

    return band


def _build_category_3_facts(aggregated: AggregatedReport) -> dict[str, Any]:
    supported = all(
        stats.category_counts[3] == sum(stats.category_3_by_official.values()) for stats in aggregated.channel_stats
    )
    by_official: dict[str, list[str]] = {}
    for official in ("hokim", "kengash_raisi", "kotibiyat_mudiri"):
        by_official[official] = sorted(
            [stats.council_name for stats in aggregated.channel_stats if stats.category_3_by_official.get(official, 0) > 0]
        )

    anomalies = []
    if supported:
        for stats in aggregated.channel_stats:
            total = stats.category_counts[3]
            if total == 0:
                continue
            for official, count in stats.category_3_by_official.items():
                if count * 2 > total:
                    anomalies.append(
                        {
                            "council_name": stats.council_name,
                            "official": official,
                            "count": count,
                            "percent": round(count * 100 / total),
                        }
                    )

    return {
        "official_breakdown_supported": supported,
        "channels_by_official": by_official,
        "uncovered_channels": sorted(
            [
                stats.council_name
                for stats in aggregated.channel_stats
                if sum(stats.category_3_by_official.values()) == 0 and stats.data_completeness == "complete"
            ]
        ),
        "official_anomalies": anomalies,
        "methodology_note": (
            "3-toifa tarkibida ushbu uch mansabdorning faoliyati bilan birga ularning shaxsan olib borgan 24 ta masala o'rganishlari ham kiradi."
        ),
    }


def _build_category_4_facts(aggregated: AggregatedReport) -> dict[str, Any]:
    counter: Counter[str] = Counter()
    for stats in aggregated.channel_stats:
        counter.update(stats.category_4_by_issue)

    return {
        "issues_supported": bool(counter),
        "top_issues": [
            {"issue": issue, "count": count}
            for issue, count in counter.most_common(5)
        ],
    }


def _build_category_5_facts(aggregated: AggregatedReport) -> dict[str, Any]:
    subtype_counter: Counter[str] = Counter()
    problem_type_counter: Counter[str] = Counter()
    subtype_supported = True
    problem_type_supported = True

    for stats in aggregated.channel_stats:
        subtype_counter.update(stats.category_5_by_subtype)
        problem_type_counter.update(stats.category_5_by_problem_type)
        if stats.category_counts[5] != sum(stats.category_5_by_subtype.values()):
            subtype_supported = False
        if stats.category_counts[5] != sum(stats.category_5_by_problem_type.values()):
            problem_type_supported = False

    return {
        "subtype_supported": subtype_supported,
        "problem_type_supported": problem_type_supported,
        "system_subtypes": dict(subtype_counter),
        "system_problem_types": dict(problem_type_counter),
    }


def _build_category_6_facts(aggregated: AggregatedReport) -> dict[str, Any]:
    counter: Counter[str] = Counter()
    for stats in aggregated.channel_stats:
        counter.update(stats.category_6_by_law)

    return {
        "laws_supported": bool(counter),
        "top_laws": [{"law": law, "count": count} for law, count in counter.most_common(5)],
    }


def _build_trend_facts(aggregated: AggregatedReport) -> dict[str, Any]:
    prior = aggregated.prior_period_reference
    if prior is None:
        return {"trend_status": "missing_baseline", "trend_disclaimer": TREND_DISCLAIMER}

    prior_version = str(prior.get("spec_version", "")).strip()
    if prior_version != aggregated.current_spec_version:
        return {"trend_status": "methodology_mismatch", "trend_disclaimer": METHODOLOGY_DISCLAIMER}

    return {"trend_status": "available", "trend_disclaimer": ""}


def _build_category_12_facts(aggregated: AggregatedReport) -> dict[str, Any]:
    subtype_counter: Counter[str] = Counter()
    subtype_supported = True
    for stats in aggregated.channel_stats:
        subtype_counter.update(stats.category_12_by_subtype)
        if stats.category_counts[12] != sum(stats.category_12_by_subtype.values()):
            subtype_supported = False

    dominant_subtype = None
    total = aggregated.totals_by_category[12]
    if total:
        for subtype, count in subtype_counter.items():
            if count * 2 > total:
                dominant_subtype = {"subtype": subtype, "count": count, "percent": round(count * 100 / total)}
                break

    return {
        "subtype_supported": subtype_supported,
        "system_subtypes": dict(subtype_counter),
        "dominant_subtype_anomaly": dominant_subtype,
    }


def _build_anomalies(aggregated: AggregatedReport) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []
    for category_id in range(2, 13):
        dominant = _category_dominant_channel_anomaly(aggregated, category_id)
        if dominant is not None:
            anomalies.append({"kind": "category_channel_share", "category_id": category_id, **dominant})
    return anomalies


def _build_final_observation_points(aggregated: AggregatedReport, anomalies: list[dict[str, Any]]) -> list[str]:
    points: list[str] = []
    zero_categories = [str(category_id) for category_id in range(2, 13) if aggregated.totals_by_category[category_id] == 0]
    if zero_categories:
        points.append(f"0 ta holat qayd etilgan toifalar: {', '.join(zero_categories)}")
    for anomaly in anomalies:
        points.append(
            f"{anomaly['category_id']}-toifada {anomaly['council_name']} kanali {anomaly['count']} ta post bilan {anomaly['percent']} foiz ulushni egallagan"
        )
    return points


def _leaders_from_total_posts(aggregated: AggregatedReport) -> list[dict[str, Any]]:
    counts = {item.council_name: item.total_posts for item in aggregated.channel_stats}
    return _leaders(counts)


def _low_performers_from_total_posts(aggregated: AggregatedReport) -> list[dict[str, Any]]:
    counts = {item.council_name: item.total_posts for item in aggregated.channel_stats}
    return _low_performers(counts)


def _zero_day_channels(aggregated: AggregatedReport) -> list[dict[str, Any]]:
    results = []
    for stats in aggregated.channel_stats:
        zero_dates = [item["date"] for item in stats.daily_post_counts if item["count"] == 0]
        if zero_dates:
            results.append({"council_name": stats.council_name, "dates": zero_dates})
    return results


def _leaders(counts_by_channel: dict[str, int]) -> list[dict[str, Any]]:
    if not counts_by_channel:
        return []
    maximum = max(counts_by_channel.values())
    return [
        {"council_name": council_name, "count": count}
        for council_name, count in sorted(counts_by_channel.items())
        if count == maximum
    ]


def _low_performers(counts_by_channel: dict[str, int]) -> list[dict[str, Any]]:
    if not counts_by_channel:
        return []

    zero_channels = [(name, count) for name, count in counts_by_channel.items() if count == 0]
    if zero_channels:
        source = zero_channels
    else:
        minimum = min(counts_by_channel.values())
        source = [(name, count) for name, count in counts_by_channel.items() if count == minimum]

    return [{"council_name": council_name, "count": count} for council_name, count in sorted(source)]


def _zero_channels(counts_by_channel: dict[str, int]) -> list[str]:
    return sorted([council_name for council_name, count in counts_by_channel.items() if count == 0])


def _category_dominant_channel_anomaly(aggregated: AggregatedReport, category_id: int) -> dict[str, Any] | None:
    total = aggregated.totals_by_category[category_id]
    if total == 0:
        return None

    for stats in aggregated.channel_stats:
        count = stats.category_counts[category_id]
        if count * 2 > total:
            return {
                "council_name": stats.council_name,
                "count": count,
                "percent": round(count * 100 / total),
            }
    return None


def _is_narrative_payload_shape(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False

    category_sections = payload.get("category_sections")
    if not isinstance(category_sections, dict):
        return False

    required_keys = {str(category_id) for category_id in ALLOWED_CATEGORIES}
    return (
        isinstance(payload.get("summary"), str)
        and isinstance(payload.get("final_heading"), str)
        and isinstance(payload.get("final_observation"), str)
        and required_keys.issubset(category_sections.keys())
    )
