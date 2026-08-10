"""Deterministic aggregation helpers for the GitHub engineering dashboard."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from tools.profile_builder.github_dashboard.models import (
    ContributionDay,
    LanguageShare,
    MonthlyContribution,
    RadarDimension,
)

_LEVEL_MAP = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}

# ---------------------------------------------------------------------------
# Radar normalization thresholds — change these via config, not renderer edits
# ---------------------------------------------------------------------------
_RADAR_THRESHOLDS = {
    "build": 2000,  # commits
    "collaborate": 500,  # PRs + reviews
    "ship": 100,  # releases + PRs merged
    "maintain": 50,  # active non-archived repos
    "explore": 5000,  # starred repos
    "breadth": 20,  # languages * 2 + orgs * 3 (composite)
}


def _log_score(value: float, threshold: float) -> int:
    """Return a 0–100 log-scaled score bounded deterministically."""
    if value <= 0 or threshold <= 0:
        return 0
    raw = math.log10(value + 1) / math.log10(threshold + 1) * 100
    return max(0, min(100, round(raw)))


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
    """Filter repositories to active public inventory (non-fork, non-archived)."""
    return [
        repo
        for repo in repositories
        if not repo.get("private", False)
        and not repo.get("fork", False)
        and not repo.get("archived", False)
    ]


def all_public_non_fork_repositories(
    repositories: list[dict[str, object]],
) -> list[dict[str, object]]:
    """All public, non-fork repositories including archived (for total inventory)."""
    return [
        repo
        for repo in repositories
        if not repo.get("private", False) and not repo.get("fork", False)
    ]


def deduplicate_repositories(
    repositories: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Deduplicate repositories by canonical full_name (owner/name)."""
    seen: set[str] = set()
    result: list[dict[str, object]] = []
    for repo in repositories:
        full_name = str(repo.get("full_name") or "").lower()
        if full_name and full_name not in seen:
            seen.add(full_name)
            result.append(repo)
    return result


def repositories_per_owner(
    repositories: list[dict[str, object]],
) -> dict[str, int]:
    """Count active public repositories per owner login."""
    counts: dict[str, int] = defaultdict(int)
    for repo in repositories:
        owner_data = repo.get("owner") or {}
        login = str(
            (owner_data.get("login") if isinstance(owner_data, dict) else None) or ""
        )
        if login:
            counts[login] += 1
    return dict(counts)


def aggregate_stars(repositories: list[dict[str, object]]) -> int:
    """Sum stars across eligible repositories."""
    return sum(int(repo.get("stargazers_count") or 0) for repo in repositories)


def aggregate_forks(repositories: list[dict[str, object]]) -> int:
    """Sum fork counts across eligible repositories."""
    return sum(int(repo.get("forks_count") or 0) for repo in repositories)


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


def calculate_monthly_contributions(
    contribution_days: list[ContributionDay],
    *,
    window_start: date,
    window_end: date,
) -> list[MonthlyContribution]:
    """Sum contributions by calendar month within the trailing window."""
    totals: dict[tuple[int, int], int] = defaultdict(int)
    cursor = window_start.replace(day=1)
    while cursor <= window_end:
        totals[(cursor.year, cursor.month)] = 0
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)
    for day in contribution_days:
        value = date.fromisoformat(day.date)
        if window_start <= value <= window_end:
            totals[(value.year, value.month)] += day.contribution_count
    return [
        MonthlyContribution(year=year, month=month, count=count)
        for (year, month), count in sorted(totals.items())
    ]


def calculate_active_days(contribution_days: list[ContributionDay]) -> int:
    """Count days with at least one contribution."""
    return sum(1 for day in contribution_days if day.contribution_count > 0)


def calculate_most_active_month(
    monthly_contributions: list[MonthlyContribution],
) -> str:
    """Return YYYY-MM label for the month with the most contributions."""
    if not monthly_contributions:
        return ""
    peak = max(monthly_contributions, key=lambda m: m.count)
    return f"{peak.year}-{peak.month:02d}"


def calculate_average_contributions_per_active_day(
    contribution_days: list[ContributionDay],
    active_days: int,
) -> float:
    """Mean contributions per day that had at least one contribution."""
    if active_days <= 0:
        return 0.0
    total = sum(day.contribution_count for day in contribution_days)
    return round(total / active_days, 2)


def calculate_radar_dimensions(
    *,
    commits: int,
    pull_requests: int,
    reviews: int,
    releases: int,
    active_repositories: int,
    total_starred: int,
    detected_languages: int,
    orgs_count: int,
) -> list[RadarDimension]:
    """Derive six Engineering Signature radar dimensions from documented metrics."""
    return [
        RadarDimension(
            key="build",
            label="Build",
            score=_log_score(commits, _RADAR_THRESHOLDS["build"]),
            source_fields=["public_commit_contributions"],
            formula=(
                "log10(commits + 1) / log10(threshold + 1) * 100, bounded 0–100; "
                f"threshold={_RADAR_THRESHOLDS['build']}"
            ),
            unavailable=commits == 0,
        ),
        RadarDimension(
            key="collaborate",
            label="Collaborate",
            score=_log_score(pull_requests + reviews, _RADAR_THRESHOLDS["collaborate"]),
            source_fields=[
                "public_pull_request_contributions",
                "public_pull_request_review_contributions",
            ],
            formula=(
                "log10(PRs + reviews + 1) / log10(threshold + 1) * 100, bounded 0–100; "
                f"threshold={_RADAR_THRESHOLDS['collaborate']}"
            ),
            unavailable=(pull_requests + reviews) == 0,
        ),
        RadarDimension(
            key="ship",
            label="Ship",
            score=_log_score(releases + pull_requests, _RADAR_THRESHOLDS["ship"]),
            source_fields=[
                "public_releases_past_year",
                "public_pull_request_contributions",
            ],
            formula=(
                "log10(releases + PRs + 1) / log10(threshold + 1) * 100, "
                f"bounded 0–100; threshold={_RADAR_THRESHOLDS['ship']}"
            ),
            unavailable=(releases + pull_requests) == 0,
        ),
        RadarDimension(
            key="maintain",
            label="Maintain",
            score=_log_score(active_repositories, _RADAR_THRESHOLDS["maintain"]),
            source_fields=[
                "owned_public_non_archived_repositories",
            ],
            formula=(
                "log10(active_repos + 1) / log10(threshold + 1) * 100, bounded 0–100; "
                f"threshold={_RADAR_THRESHOLDS['maintain']}"
            ),
            unavailable=active_repositories == 0,
        ),
        RadarDimension(
            key="explore",
            label="Explore",
            score=_log_score(total_starred, _RADAR_THRESHOLDS["explore"]),
            source_fields=["total_starred"],
            formula=(
                "log10(starred + 1) / log10(threshold + 1) * 100, bounded 0–100; "
                f"threshold={_RADAR_THRESHOLDS['explore']}"
            ),
            unavailable=total_starred == 0,
        ),
        RadarDimension(
            key="breadth",
            label="Breadth",
            score=_log_score(
                detected_languages * 2 + orgs_count * 3,
                _RADAR_THRESHOLDS["breadth"],
            ),
            source_fields=[
                "detected_languages",
                "orgs_count",
            ],
            formula=(
                "log10(languages*2 + orgs*3 + 1) / log10(threshold + 1) * 100, "
                f"bounded 0–100; threshold={_RADAR_THRESHOLDS['breadth']}"
            ),
            unavailable=(detected_languages + orgs_count) == 0,
        ),
    ]
