from __future__ import annotations

from datetime import UTC, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.models import ReportPeriod, ReportPeriodConfig


FALLBACK_TIMEZONES = {
    "Asia/Tashkent": timezone(timedelta(hours=5)),
}


def calculate_report_period(config: ReportPeriodConfig, timezone_name: str) -> ReportPeriod:
    timezone_info = _resolve_timezone(timezone_name)
    now = datetime.now(timezone_info)

    if config.mode == "explicit":
        if not config.explicit_start or not config.explicit_end:
            raise ValueError("explicit_start and explicit_end are required for explicit mode")
        return ReportPeriod(
            start=_parse_explicit_datetime(config.explicit_start, timezone_info),
            end=_parse_explicit_datetime(config.explicit_end, timezone_info),
        )

    if config.mode == "previous_week":
        return _previous_week_period(now)

    if config.mode == "current_week":
        return _current_week_period(now)

    if config.mode == "auto":
        if now.weekday() == 0:
            return _previous_week_period(now)
        return _current_week_period(now)

    raise ValueError(f"Unsupported report period mode: {config.mode}")


def _resolve_timezone(timezone_name: str):
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        fallback = FALLBACK_TIMEZONES.get(timezone_name)
        if fallback is None:
            raise
        return fallback


def _parse_explicit_datetime(value: str, timezone_info) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone_info)
    return parsed.astimezone(timezone_info)


def _current_week_period(now: datetime) -> ReportPeriod:
    start_date = now.date() - timedelta(days=now.weekday())
    start = datetime.combine(start_date, time.min, tzinfo=now.tzinfo)
    return ReportPeriod(start=start, end=now)


def _previous_week_period(now: datetime) -> ReportPeriod:
    current_week_start = now.date() - timedelta(days=now.weekday())
    previous_week_start = current_week_start - timedelta(days=7)
    start = datetime.combine(previous_week_start, time.min, tzinfo=now.tzinfo)
    previous_week_end_date = current_week_start - timedelta(days=1)
    end = datetime.combine(previous_week_end_date, time.max, tzinfo=now.tzinfo)
    return ReportPeriod(start=start, end=end)
