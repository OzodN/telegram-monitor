from __future__ import annotations

import json
import logging
from collections import Counter
from typing import Any, TypedDict

from src.classification_support import ALLOWED_CATEGORIES, TREND_CATEGORIES
from src.gemini_client import GeminiClient
from src.models import AggregatedReport, ClassifiedPost, GeminiConfig, PathsConfig, ReportNarrative
from src.utils import read_utf8_text


logger = logging.getLogger(__name__)
PROHIBITED_PHRASES = [
    "эҳтимол",
    "афтидан",
    "кўринишича",
    "бу шундан далолат беради",
    "сабаби шуки",
    "балки",
    "деб тахмин қилинади",
    "бунинг сабаби",
    "аномалия",
]
TREND_DISCLAIMER = "Олдинги давр бўйича таққослаш учун база мавжуд эмас."
METHODOLOGY_DISCLAIMER = (
    "Ушбу давр таснифи олдинги давр билан солиштириш имконини бермайди, чунки таснифлаш услубияти ўзгарган."
)

CategorySectionsSchema = TypedDict("CategorySectionsSchema", {
    "2": str,
    "3": str,
    "4": str,
    "5": str,
    "6": str,
    "7": str,
    "8": str,
    "9": str,
    "10": str,
    "11": str,
    "12": str,
})

class NarrativeResponseSchema(TypedDict):
    summary: str
    category_sections: CategorySectionsSchema
    final_heading: str
    final_observation: str


def generate_narrative(
    classified_posts: list[ClassifiedPost],
    aggregated: AggregatedReport,
    config: GeminiConfig,
    paths: PathsConfig,
    gemini_client: GeminiClient,
) -> ReportNarrative:
    del classified_posts

    narrative_facts = build_narrative_facts(aggregated)
    system_instruction, user_prompt = _build_narrative_prompts(narrative_facts, paths)
    payload = gemini_client.generate_json(
        contents=user_prompt,
        request_config={
            "temperature": 0,
            "response_mime_type": "application/json",
            "system_instruction": system_instruction,
        },
        operation_name="narrative generation",
        validator=_is_narrative_payload_shape,
        response_schema=NarrativeResponseSchema,
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


def _build_narrative_prompts(narrative_facts: dict[str, Any], paths: PathsConfig) -> tuple[str, str]:
    specification_text = read_utf8_text(paths.narrative_specification_md)

    system_instruction = f"""
Сиз ишлаб турган production Telegram мониторинг тизими учун расмий ҳафталик изоҳ ёзасиз.

Манба қоидалари:
- Қуйидаги narrative specification ягона authoritative ҳужжатдир.
- Фақат FACTS JSON ичидаги маълумотлардан фойдаланинг.
- Ҳеч қандай сабаб, мотив, сиёсий талқин, яширин тренд ёки етишмаётган фактни ихтиро қилманг.
- Ҳисоб-китоб қилманг. Барча сонлар ва фоизлар FACTS JSON ичида тайёр берилган.
- Қўллаб-қувватланмаган майдонлар бўйича даъво қилманг.
- Қуйидаги сўз ва ибораларни ишлатманг: {", ".join(PROHIBITED_PHRASES)}.
- Банд 10 ва 11 да тренд фақат trend_status=available бўлса ёзилади. Акс ҳолда facts ичидаги disclaimer матнидан фойдаланинг.
- Ҳар бир банд алоҳида параграф бўлсин.
- category_sections ичидаги ҳар бир қиймат (масалан, "2" категорияга тегишли матн) мутлақо мос равишда "2. " (ёки "3. ", "4. " ва ҳоказо) префикси билан бошланиши шарт. "2-категория:", "2) ", "[2] " каби бошқа форматлар қатъиян тақиқланади!
- Final observation фақат олдинги бандларда аллақачон айтилган ноль ҳолатлар ёки кескин устунлик ҳолатларини қисқа жамласин.
- Барча матнлар ҚАТЪИЯН Ўзбек Кирилл алифбосида ёзилиши шарт. JSON калитлари ва махсус атамаларни (масалан, инглиз тилидаги статуслар) ўзгаришсиз қолдиринг.
- Жавоб фақат JSON бўлсин.

AUTHORITATIVE NARRATIVE SPECIFICATION:
{specification_text}

Қатъий JSON формати:
{{
  "summary": "1-банд мазмунидаги кириш параграфи",
  "category_sections": {{
    "2": "2. [Матн фақат '2. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]",
    "3": "3. [Матн фақат '3. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]",
    "4": "4. [Матн фақат '4. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]",
    "5": "5. [Матн фақат '5. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]",
    "6": "6. [Матн фақат '6. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]",
    "7": "7. [Матн фақат '7. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]",
    "8": "8. [Матн фақат '8. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]",
    "9": "9. [Матн фақат '9. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]",
    "10": "10. [Матн фақат '10. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]",
    "11": "11. [Матн фақат '11. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]",
    "12": "12. [Матн фақат '12. ' префикси билан бошланиши шарт. Бошқа форматлар тақиқланади]"
  }},
  "final_heading": "13. Турли масалалар",
  "final_observation": "..."
}}
""".strip()

    user_prompt = f"FACTS JSON:\n{json.dumps(narrative_facts, ensure_ascii=False, indent=2)}"

    return system_instruction, user_prompt


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
            "3-категория таркибида ушбу уч мансабдорнинг фаолияти билан бирга уларнинг шахсан олиб борган 24 та масала ўрганишлари ҳам киради."
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

    total = aggregated.totals_by_category[12]
    system_subtypes = {}
    for subtype, count in subtype_counter.items():
        percent = round(count * 100 / total) if total else 0
        system_subtypes[subtype] = {
            "count": count,
            "percent": percent,
        }

    dominant_subtype = None
    if total:
        for subtype, count in subtype_counter.items():
            if count * 2 > total:
                dominant_subtype = {"subtype": subtype, "count": count, "percent": round(count * 100 / total)}
                break

    return {
        "subtype_supported": subtype_supported,
        "system_subtypes": system_subtypes,
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
        points.append(f"Умумий тизим бўйича 0 та ҳолат қайд этилган категориялар: {', '.join(zero_categories)}")

    for category_id in range(2, 13):
        if aggregated.totals_by_category.get(category_id, 0) > 0:
            zero_channels = [
                stats.council_name
                for stats in aggregated.channel_stats
                if stats.category_counts.get(category_id, 0) == 0
            ]
            if zero_channels:
                points.append(f"{category_id}-устун бўйича пост эълон қилмаган (0 та) каналлар: {', '.join(zero_channels)}")

    for anomaly in anomalies:
        points.append(
            f"{anomaly['category_id']}-категорияда {anomaly['council_name']} канали {anomaly['count']} та пост билан {anomaly['percent']} фоиз улушни эгаллаган"
        )
        
    if getattr(aggregated, 'madad_channels', None):
        points.append(f"«Мадад» ННТ билан ҳамкорликда учрашув ёки маслаҳат ташкил этилгани тўғрисида пост эълон қилган каналлар: {', '.join(aggregated.madad_channels)}")
        
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
