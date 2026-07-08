from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class ChannelConfig:
    council_name: str
    telegram_url: str


@dataclass(slots=True)
class TelegramConfig:
    api_id: int
    api_hash: str
    session_name: str
    channels: list[ChannelConfig]


@dataclass(slots=True)
class GeminiConfig:
    api_keys: list[str]
    model: str
    request_timeout_seconds: float
    classification_batch_size: int
    retry_attempts: int
    retry_backoff_seconds: float
    request_delay_seconds: float
    max_backoff_seconds: float
    max_requests_per_minute: int
    temperature: float


@dataclass(slots=True)
class PathsConfig:
    classification_specification_md: Path
    narrative_specification_md: Path
    issues_24_md: Path
    laws_162_md: Path
    reference_report_docx: Path
    output_root: Path


@dataclass(slots=True)
class DatasetReference:
    dataset: str
    reference_id: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class ReportPeriodConfig:
    mode: str
    explicit_start: str | None
    explicit_end: str | None


@dataclass(slots=True)
class AppConfig:
    timezone: str
    telegram: TelegramConfig
    gemini: GeminiConfig
    paths: PathsConfig
    report_period: ReportPeriodConfig


@dataclass(slots=True)
class ReportPeriod:
    start: datetime
    end: datetime


@dataclass(slots=True)
class TelegramPost:
    source_channel: str
    source_url: str
    message_id: int
    published_at: datetime
    text: str
    views: int | None
    subscriber_count: int | None
    has_media: bool

    def stable_id(self) -> str:
        return f"{self.source_channel}:{self.message_id}"

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["published_at"] = self.published_at.isoformat()
        payload["stable_id"] = self.stable_id()
        return payload


@dataclass(slots=True)
class ClassifiedPost:
    post: TelegramPost
    category_id: int
    category_reason: str
    matched_rule: str
    evidence: list[str]
    dataset_references: list[DatasetReference]
    request_marker: str | None = None
    category_3_official: str | None = None
    category_5_subtype: str | None = None
    category_5_problem_type: str | None = None
    category_12_subtype: str | None = None
    audit_status: str | None = None
    audit_notes: str | None = None

    def to_dict(self) -> dict:
        return {
            "post": self.post.to_dict(),
            "category_id": self.category_id,
            "category_reason": self.category_reason,
            "matched_rule": self.matched_rule,
            "evidence": self.evidence,
            "dataset_references": [item.to_dict() for item in self.dataset_references],
            "request_marker": self.request_marker,
            "category_3_official": self.category_3_official,
            "category_5_subtype": self.category_5_subtype,
            "category_5_problem_type": self.category_5_problem_type,
            "category_12_subtype": self.category_12_subtype,
            "audit_status": self.audit_status,
            "audit_notes": self.audit_notes,
        }


@dataclass(slots=True)
class ChannelStats:
    council_name: str
    total_posts: int
    category_counts: dict[int, int]
    subscriber_count: int | None
    average_views: int
    total_views: int = 0
    viewed_posts_count: int = 0
    data_completeness: str = "complete"
    daily_post_counts: list[dict[str, int]] = field(default_factory=list)
    category_3_by_official: dict[str, int] = field(default_factory=dict)
    category_4_by_issue: dict[str, int] = field(default_factory=dict)
    category_5_by_subtype: dict[str, int] = field(default_factory=dict)
    category_5_by_problem_type: dict[str, int] = field(default_factory=dict)
    category_6_by_law: dict[str, int] = field(default_factory=dict)
    category_12_by_subtype: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.category_counts is not None:
            self.category_counts = {int(k): int(v) for k, v in self.category_counts.items()}


@dataclass(slots=True)
class AggregatedReport:
    period: ReportPeriod
    channel_stats: list[ChannelStats]
    totals_by_category: dict[int, int]
    overall_average_views: int = 0
    overall_total_views: int = 0
    overall_viewed_posts_count: int = 0
    current_spec_version: str = ""
    prior_period_reference: dict | None = None
    flagged_anomalies: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.totals_by_category is not None:
            self.totals_by_category = {int(k): int(v) for k, v in self.totals_by_category.items()}

    def to_dict(self) -> dict:
        return {
            "period": {
                "start": self.period.start.isoformat(),
                "end": self.period.end.isoformat(),
            },
            "channel_stats": [asdict(item) for item in self.channel_stats],
            "totals_by_category": self.totals_by_category,
            "overall_average_views": self.overall_average_views,
            "overall_total_views": self.overall_total_views,
            "overall_viewed_posts_count": self.overall_viewed_posts_count,
            "current_spec_version": self.current_spec_version,
            "prior_period_reference": self.prior_period_reference,
            "flagged_anomalies": self.flagged_anomalies,
        }


@dataclass(slots=True)
class ReportNarrative:
    summary: str
    category_sections: dict[int, str]
    final_heading: str
    final_observation: str

    def __post_init__(self) -> None:
        if self.category_sections is not None:
            self.category_sections = {int(k): str(v) for k, v in self.category_sections.items()}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class RunDirectories:
    root_dir: Path
    raw_posts_path: Path
    classified_posts_path: Path
    classification_regression_checks_path: Path
    audited_posts_path: Path
    audit_regression_checks_path: Path
    aggregated_stats_path: Path
    narrative_path: Path
    narrative_validation_path: Path
    reports_dir: Path
