"""Deterministic aggregation helpers for the GitHub engineering dashboard."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from tools.profile_builder.github_dashboard.models import ContributionDay, LanguageShare

_LEVEL_MAP = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}


def utc_today(now: datetime | None = None) -> date:
    """Return today's UTC date from an injectable clock."""
    instant = now or datetime.now(UTC)
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=UTC)
    return instant.astimezone(UTC).date()


def trailing_window_endpoints(*, today: date, days: int) -> tuple[date, date]:
    """Return the inclusive trailing window endpoints."""
    return today - timedelta(days=days - 1), today


def normalize_contribution_days(
    raw_weeks: list[dict[str, object]],
    *,
    window_start: date,
    window_end: date,
) -> list[ContributionDay]:
    """Normalize GraphQL contribution weeks into a flat trailing-window series."""
    normalized: list[ContributionDay] = []
    for week in raw_weeks:
        days = week.get("contributionDays")
        if not isinstance(days, list):
            continue
        for day in days:
            if not isinstance(day, dict):
                continue
            value = date.fromisoformat(str(day["date"]))
            if value < window_start or value > window_end:
                continue
            normalized.append(
                ContributionDay(
                    date=value.isoformat(),
                    contribution_count=int(day.get("contributionCount") or 0),
                    level=_LEVEL_MAP.get(str(day.get("contributionLevel")), 0),
                    weekday=int(day.get("weekday") or 0),
                    is_future=False,
                )
            )
    normalized.sort(key=lambda item: item.date)
    return normalized


def calculate_streaks(
    contribution_days: list[ContributionDay], *, today: date
) -> tuple[int, int]:
    """Return ``(current_streak, longest_streak)`` for the displayed window."""
    counts = {
        date.fromisoformat(day.date): day.contribution_count
        for day in contribution_days
        if not day.is_future
    }
    if not counts:
        return 0, 0

    anchor = today if counts.get(today, 0) > 0 else today - timedelta(days=1)
    current = 0
    if counts.get(anchor, 0) > 0:
        cursor = anchor
        while counts.get(cursor, 0) > 0:
            current += 1
            cursor -= timedelta(days=1)

    longest = 0
    running = 0
    previous: date | None = None
    for value in sorted(counts):
        if counts[value] <= 0:
            running = 0
            previous = value
            continue
        if previous is not None and value == previous + timedelta(days=1):
            running += 1
        else:
            running = 1
        longest = max(longest, running)
        previous = value
    return current, longest


def aggregate_language_shares(
    repositories: list[dict[str, object]],
    languages_by_repo: dict[str, dict[str, int]],
    *,
    display_limit: int = 5,
) -> list[LanguageShare]:
    """Aggregate eligible repository language bytes into coherent percentages."""
    totals: dict[str, int] = defaultdict(int)
    for repo in repositories:
        languages_url = str(repo.get("languages_url") or "")
        for name, value in languages_by_repo.get(languages_url, {}).items():
            totals[name] += value
    total_bytes = sum(totals.values())
    if total_bytes <= 0:
        return []

    sorted_totals = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    top = sorted_totals[:display_limit]
    remainder = sum(value for _, value in sorted_totals[display_limit:])
    if remainder > 0:
        top.append(("Other", remainder))

    exact = [(name, value, (value / total_bytes) * 100) for name, value in top]
    floors = [
        (name, value, math.floor(pct), pct - math.floor(pct))
        for name, value, pct in exact
    ]
    points_left = 100 - sum(item[2] for item in floors)
    order = sorted(
        range(len(floors)),
        key=lambda idx: (-floors[idx][3], -floors[idx][1], floors[idx][0]),
    )
    percentages = [item[2] for item in floors]
    for idx in order[:points_left]:
        percentages[idx] += 1

    return [
        LanguageShare(
            name=floors[idx][0], bytes=floors[idx][1], percentage=percentages[idx]
        )
        for idx in range(len(floors))
        if percentages[idx] > 0
    ]


def eligible_public_repositories(
    repositories: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Filter repositories to the dashboard's public inventory definition."""
    return [
        repo
        for repo in repositories
        if not repo.get("private", False)
        and not repo.get("fork", False)
        and not repo.get("archived", False)
    ]


def aggregate_stars(repositories: list[dict[str, object]]) -> int:
    """Sum stars across eligible repositories."""
    return sum(int(repo.get("stargazers_count") or 0) for repo in repositories)


def count_public_releases_past_year(
    repositories: list[dict[str, object]],
    releases_by_repo: dict[str, list[dict[str, object]]],
    *,
    window_start: date,
) -> int:
    """Count non-draft public releases published within the trailing window."""
    count = 0
    cutoff = datetime.combine(window_start, datetime.min.time(), tzinfo=UTC)
    for repo in repositories:
        full_name = str(repo.get("full_name") or "")
        for release in releases_by_repo.get(full_name, []):
            if release.get("draft", False):
                continue
            published_at = release.get("published_at")
            if not published_at:
                continue
            published = datetime.fromisoformat(str(published_at).replace("Z", "+00:00"))
            if published >= cutoff:
                count += 1
    return count
