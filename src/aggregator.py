from __future__ import annotations

from datetime import timedelta

from src.classification_support import ClassificationReferenceData
from src.models import AggregatedReport, ChannelConfig, ChannelStats, ClassifiedPost, ReportPeriod


CATEGORY_3_OFFICIALS = ("hokim", "kengash_raisi", "kotibiyat_mudiri")
CATEGORY_5_SUBTYPES = ("request_sent", "result_achieved")
CATEGORY_5_PROBLEM_TYPES = ("road", "water", "gas", "electricity", "social", "other")
CATEGORY_12_SUBTYPES = ("template", "legislative_news", "internal_organizational", "press_article", "other")


def aggregate_report_data(
    classified_posts: list[ClassifiedPost],
    channels: list[ChannelConfig],
    period: ReportPeriod,
    reference_data: ClassificationReferenceData,
) -> AggregatedReport:
    channel_posts: dict[str, list[ClassifiedPost]] = {channel.council_name: [] for channel in channels}
    for item in classified_posts:
        channel_posts.setdefault(item.post.source_channel, []).append(item)

    channel_stats: list[ChannelStats] = []
    totals_by_category = {category_id: 0 for category_id in range(1, 13)}
    overall_total_views = 0
    overall_viewed_posts_count = 0

    for channel in channels:
        posts = channel_posts.get(channel.council_name, [])
        category_counts = {category_id: 0 for category_id in range(2, 13)}
        for post in posts:
            category_counts[post.category_id] += 1

        total_posts = len(posts)
        totals_by_category[1] += total_posts
        for category_id in range(2, 13):
            totals_by_category[category_id] += category_counts[category_id]

        subscriber_count = _pick_subscriber_count(posts)
        total_views, viewed_posts_count, average_views = _summarize_views(posts)
        overall_total_views += total_views
        overall_viewed_posts_count += viewed_posts_count

        channel_stats.append(
            ChannelStats(
                council_name=channel.council_name,
                total_posts=total_posts,
                category_counts=category_counts,
                subscriber_count=subscriber_count,
                average_views=average_views,
                total_views=total_views,
                viewed_posts_count=viewed_posts_count,
                data_completeness="complete",
                daily_post_counts=_build_daily_post_counts(posts, period),
                category_3_by_official=_count_category_3_officials(posts),
                category_4_by_issue=_count_category_4_issues(posts, reference_data),
                category_5_by_subtype=_count_category_5_subtypes(posts),
                category_5_by_problem_type=_count_category_5_problem_types(posts),
                category_6_by_law=_count_category_6_laws(posts, reference_data),
                category_12_by_subtype=_count_category_12_subtypes(posts),
            )
        )

    overall_average_views = sum(stats.average_views for stats in channel_stats)

    aggregated_report = AggregatedReport(
        period=period,
        channel_stats=channel_stats,
        totals_by_category=totals_by_category,
        overall_average_views=overall_average_views,
        overall_total_views=overall_total_views,
        overall_viewed_posts_count=overall_viewed_posts_count,
        current_spec_version=_derive_spec_version(reference_data),
        prior_period_reference=None,
        flagged_anomalies=[],
    )
    _assert_aggregation_identity(aggregated_report)
    return aggregated_report


def _pick_subscriber_count(posts: list[ClassifiedPost]) -> int | None:
    for post in posts:
        if post.post.subscriber_count is not None:
            return post.post.subscriber_count
    return None


def _summarize_views(posts: list[ClassifiedPost]) -> tuple[int, int, int]:
    values = [post.post.views for post in posts if post.post.views is not None]
    if not values:
        return 0, 0, 0

    total_views = sum(values)
    viewed_posts_count = len(values)
    average_views = round(total_views / viewed_posts_count)
    return total_views, viewed_posts_count, average_views


def _build_daily_post_counts(posts: list[ClassifiedPost], period: ReportPeriod) -> list[dict[str, int]]:
    counts_by_date: dict[str, int] = {}
    cursor = period.start.date()
    end_date = period.end.date()
    while cursor <= end_date:
        counts_by_date[cursor.isoformat()] = 0
        cursor += timedelta(days=1)

    for item in posts:
        key = item.post.published_at.date().isoformat()
        if key in counts_by_date:
            counts_by_date[key] += 1

    return [{"date": date_label, "count": count} for date_label, count in counts_by_date.items()]


def _count_category_3_officials(posts: list[ClassifiedPost]) -> dict[str, int]:
    counts = {key: 0 for key in CATEGORY_3_OFFICIALS}
    for item in posts:
        if item.category_id != 3 or item.category_3_official not in counts:
            continue
        counts[item.category_3_official] += 1
    return counts


def _count_category_5_subtypes(posts: list[ClassifiedPost]) -> dict[str, int]:
    counts = {key: 0 for key in CATEGORY_5_SUBTYPES}
    for item in posts:
        if item.category_id != 5 or item.category_5_subtype not in counts:
            continue
        counts[item.category_5_subtype] += 1
    return counts


def _count_category_4_issues(
    posts: list[ClassifiedPost],
    reference_data: ClassificationReferenceData,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in posts:
        if item.category_id != 4:
            continue
        for reference in item.dataset_references:
            if reference.dataset != "issues_24":
                continue
            issue_entry = reference_data.issues_24_catalog.resolve(reference.reference_id)
            issue_name = issue_entry.title if issue_entry is not None else reference.reference_id
            counts[issue_name] = counts.get(issue_name, 0) + 1
    return dict(sorted(counts.items()))


def _count_category_5_problem_types(posts: list[ClassifiedPost]) -> dict[str, int]:
    counts = {key: 0 for key in CATEGORY_5_PROBLEM_TYPES}
    for item in posts:
        if item.category_id != 5 or item.category_5_problem_type not in counts:
            continue
        counts[item.category_5_problem_type] += 1
    return counts


def _count_category_6_laws(
    posts: list[ClassifiedPost],
    reference_data: ClassificationReferenceData,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in posts:
        if item.category_id != 6:
            continue
        for reference in item.dataset_references:
            if reference.dataset != "laws_162":
                continue
            law_entry = reference_data.laws_162_catalog.resolve(reference.reference_id)
            law_name = law_entry.title if law_entry is not None else reference.reference_id
            counts[law_name] = counts.get(law_name, 0) + 1
    return dict(sorted(counts.items()))


def _count_category_12_subtypes(posts: list[ClassifiedPost]) -> dict[str, int]:
    counts = {key: 0 for key in CATEGORY_12_SUBTYPES}
    for item in posts:
        if item.category_id != 12 or item.category_12_subtype not in counts:
            continue
        counts[item.category_12_subtype] += 1
    return counts


def _derive_spec_version(reference_data: ClassificationReferenceData) -> str:
    for line in reference_data.classification_specification_text.splitlines():
        if "classification_specification_v" in line:
            token = line.strip().strip("`")
            if token:
                return token
    return "classification_specification_v2"


def _assert_aggregation_identity(aggregated_report: AggregatedReport) -> None:
    overall_sum = sum(aggregated_report.totals_by_category[category_id] for category_id in range(2, 13))
    if aggregated_report.totals_by_category[1] != overall_sum:
        raise ValueError(
            "Aggregation identity check failed for overall totals: "
            f"category_1={aggregated_report.totals_by_category[1]} "
            f"sum_categories_2_12={overall_sum}"
        )

    for channel_stats in aggregated_report.channel_stats:
        category_sum = sum(channel_stats.category_counts[category_id] for category_id in range(2, 13))
        if channel_stats.total_posts != category_sum:
            raise ValueError(
                "Aggregation identity check failed for channel "
                f"{channel_stats.council_name!r}: total_posts={channel_stats.total_posts} "
                f"sum_categories_2_12={category_sum}"
            )
