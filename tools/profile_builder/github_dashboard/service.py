"""Service layer for collecting, normalizing, and rendering the GitHub dashboard."""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.profile_builder.github_dashboard.client import (
    GitHubDashboardClient,
    ProviderFailure,
    RateLimitedError,
)
from tools.profile_builder.github_dashboard.metrics import (
    aggregate_language_shares,
    aggregate_stars,
    calculate_streaks,
    count_public_releases_past_year,
    eligible_public_repositories,
    normalize_contribution_days,
    trailing_window_endpoints,
    utc_today,
)
from tools.profile_builder.github_dashboard.models import (
    ContributionBreakdown,
    DashboardMethodology,
    DashboardStatus,
    GitHubDashboardSnapshot,
    RepositoryInventory,
    StreakMetrics,
)
from tools.profile_builder.github_dashboard.renderer import render_dashboard_svg
from tools.profile_builder.regions import atomic_write

MODULE_NAME = "github-dashboard"
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME
DEFAULT_FIXTURE = REPO_ROOT / "profile" / "fixtures" / "github-dashboard.json"
DEFAULT_USERNAME = "szmyty"
_FRESHNESS_POLICY = {
    "cadence": "daily",
    "ttl_seconds": 86400,
    "warn_after_seconds": 172800,
}
_RENDERER_VERSION = "1.0"
_SCHEMA_VERSION = "1.0"


def _write_json(path: Path, data: dict[str, Any]) -> str:
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    atomic_write(path, text)
    return text


def load_snapshot(path: Path) -> GitHubDashboardSnapshot:
    """Load a dashboard snapshot from JSON."""
    return GitHubDashboardSnapshot.model_validate_json(path.read_text(encoding="utf-8"))


def load_fixture(path: Path = DEFAULT_FIXTURE) -> GitHubDashboardSnapshot:
    """Load the synthetic offline dashboard fixture."""
    return load_snapshot(path)


def load_cached(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> GitHubDashboardSnapshot | None:
    """Load the last-known-good dashboard snapshot when present."""
    path = output_dir / "snapshot.json"
    if not path.exists():
        return None
    return load_snapshot(path)


def _classify_failure(exc: Exception) -> str:
    if isinstance(exc, RateLimitedError):
        return "rate-limited"
    if "GITHUB_TOKEN" in str(exc):
        return "configuration"
    return "provider-unavailable"


def _is_stale(data_timestamp: str, *, now: datetime) -> bool:
    data_at = datetime.fromisoformat(data_timestamp.replace("Z", "+00:00"))
    if data_at.tzinfo is None:
        data_at = data_at.replace(tzinfo=UTC)
    return (now - data_at).total_seconds() > _FRESHNESS_POLICY["ttl_seconds"]


def _fetch_languages(
    github: GitHubDashboardClient,
    repositories: list[dict[str, object]],
) -> dict[str, dict[str, int]]:
    urls = [
        str(repo.get("languages_url"))
        for repo in repositories
        if repo.get("languages_url")
    ]
    def load(url: str) -> tuple[str, dict[str, int]]:
        try:
            return url, github.fetch_languages(url)
        except ProviderFailure:
            return url, {}

    with ThreadPoolExecutor(max_workers=min(8, max(1, len(urls)))) as executor:
        results = executor.map(load, urls)
        return {key: value for key, value in results}


def _fetch_releases(
    github: GitHubDashboardClient,
    repositories: list[dict[str, object]],
) -> dict[str, list[dict[str, Any]]]:
    names = [
        str(repo.get("full_name"))
        for repo in repositories
        if repo.get("full_name")
    ]
    def load(full_name: str) -> tuple[str, list[dict[str, Any]]]:
        try:
            return full_name, github.fetch_releases(full_name)
        except ProviderFailure:
            return full_name, []

    with ThreadPoolExecutor(max_workers=min(8, max(1, len(names)))) as executor:
        results = executor.map(load, names)
        return {key: value for key, value in results}


def _render_variants(snapshot: GitHubDashboardSnapshot, output_dir: Path) -> None:
    variants = {
        "card-light.svg": {"theme": "light", "mobile": False},
        "card-dark.svg": {"theme": "dark", "mobile": False},
        "card-mobile-light.svg": {"theme": "light", "mobile": True},
        "card-mobile-dark.svg": {"theme": "dark", "mobile": True},
    }
    for filename, params in variants.items():
        atomic_write(
            output_dir / filename,
            render_dashboard_svg(snapshot, **params),
        )


def _write_metadata(
    output_dir: Path,
    *,
    state: str,
    failure_category: str | None,
    snapshot: GitHubDashboardSnapshot,
    data_hash: str,
) -> None:
    atomic_write(
        output_dir / "metadata.json",
        json.dumps(
            {
                "module_name": MODULE_NAME,
                "result_state": state,
                "data_source": snapshot.status.data_source,
                "data_timestamp": snapshot.status.data_timestamp,
                "generation_timestamp": snapshot.status.generation_timestamp,
                "data_hash": data_hash,
                "freshness_policy": _FRESHNESS_POLICY,
                "stale_state": {"is_stale": snapshot.status.is_stale},
                "failure_category": failure_category,
                "renderer_version": _RENDERER_VERSION,
                "schema_version": _SCHEMA_VERSION,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
    )


def collect_live_snapshot(
    *,
    username: str,
    token: str,
    now: datetime,
    client: GitHubDashboardClient | None = None,
) -> GitHubDashboardSnapshot:
    """Collect and normalize a live dashboard snapshot."""
    today = utc_today(now)
    window_start, window_end = trailing_window_endpoints(today=today, days=365)
    github = client or GitHubDashboardClient(token)
    collection = github.fetch_contributions(
        username,
        window_start=window_start,
        window_end=window_end,
    )
    calendar = collection.get("contributionCalendar") or {}
    raw_weeks = calendar.get("weeks") or []
    if not isinstance(raw_weeks, list):
        raise ProviderFailure("Unexpected contribution-calendar weeks payload.")
    contribution_days = normalize_contribution_days(
        raw_weeks,
        window_start=window_start,
        window_end=window_end,
    )
    repositories = eligible_public_repositories(
        github.fetch_public_repositories(username)
    )
    languages_by_repo = _fetch_languages(github, repositories)
    releases_by_repo = _fetch_releases(github, repositories)
    current_streak, longest_streak = calculate_streaks(contribution_days, today=today)
    data_timestamp = now.astimezone(UTC).isoformat()
    return GitHubDashboardSnapshot(
        schema_version=_SCHEMA_VERSION,
        username=username,
        trailing_window_days=365,
        window_start=window_start.isoformat(),
        window_end=window_end.isoformat(),
        contribution_days=contribution_days,
        contribution_breakdown=ContributionBreakdown(
            total_public_contributions=int(calendar.get("totalContributions") or 0),
            public_commit_contributions=int(
                collection.get("totalCommitContributions") or 0
            ),
            public_pull_request_contributions=int(
                collection.get("totalPullRequestContributions") or 0
            ),
            public_issue_contributions=int(
                collection.get("totalIssueContributions") or 0
            ),
            public_pull_request_review_contributions=int(
                collection.get("totalPullRequestReviewContributions") or 0
            ),
        ),
        streaks=StreakMetrics(
            current_days=current_streak,
            longest_days=longest_streak,
        ),
        repository_inventory=RepositoryInventory(
            owned_public_non_archived_repositories=len(repositories),
            stars_received=aggregate_stars(repositories),
            public_releases_past_year=count_public_releases_past_year(
                repositories,
                releases_by_repo,
                window_start=window_start,
            ),
        ),
        languages=aggregate_language_shares(repositories, languages_by_repo),
        status=DashboardStatus(
            data_source="live",
            source_state="fresh",
            data_timestamp=data_timestamp,
            generation_timestamp=data_timestamp,
            is_stale=False,
        ),
        methodology=DashboardMethodology(
            trailing_window_days=365,
            window_start=window_start.isoformat(),
            window_end=window_end.isoformat(),
            contribution_calendar_source=(
                "GitHub GraphQL contributionsCollection.contributionCalendar "
                f"for @{username}, trailing 365-day window."
            ),
            contribution_type_source=(
                "GitHub GraphQL totalCommitContributions, "
                "totalPullRequestContributions, totalIssueContributions, and "
                "totalPullRequestReviewContributions for the same window."
            ),
            repository_inventory_source=(
                "GitHub REST /users/{username}/repos type=owner, excluding "
                "private, forked, and archived repositories."
            ),
            language_distribution_source=(
                "GitHub REST languages_url aggregated across all eligible "
                "owned public repositories."
            ),
            release_count_source=(
                "GitHub REST /repos/{owner}/{repo}/releases, excluding drafts, "
                "published on or after the trailing-window start date."
            ),
            current_streak_definition=(
                "Contiguous contribution days ending today, or ending yesterday "
                "when today has no contribution yet."
            ),
            longest_streak_definition=(
                "Longest contiguous contribution streak fully contained within "
                "the displayed trailing 365-day window."
            ),
            language_rounding_policy=(
                "Largest-remainder integer percentages across all eligible "
                "repository language bytes so displayed percentages sum to 100."
            ),
        ),
    )


def build_dashboard(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    fixture_path: Path = DEFAULT_FIXTURE,
    username: str = DEFAULT_USERNAME,
    token: str | None = None,
    now: datetime | None = None,
    client: GitHubDashboardClient | None = None,
) -> GitHubDashboardSnapshot:
    """Build the GitHub dashboard with live, cache, or fixture fallback."""
    output_dir.mkdir(parents=True, exist_ok=True)
    instant = now or datetime.now(UTC)
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=UTC)

    state = "fresh"
    failure_category: str | None = None
    if token:
        try:
            snapshot = collect_live_snapshot(
                username=username,
                token=token,
                now=instant,
                client=client,
            )
        except Exception as exc:  # noqa: BLE001
            failure_category = _classify_failure(exc)
            cached = load_cached(output_dir)
            if cached is not None:
                snapshot = cached.model_copy(
                    update={
                        "status": cached.status.model_copy(
                            update={
                                "data_source": "cache",
                                "source_state": "failed-with-fallback",
                                "generation_timestamp": instant.isoformat(),
                                "is_stale": _is_stale(
                                    cached.status.data_timestamp,
                                    now=instant,
                                ),
                            }
                        )
                    }
                )
                state = "failed-with-fallback"
            else:
                fixture = load_fixture(fixture_path)
                snapshot = fixture.model_copy(
                    update={
                        "status": fixture.status.model_copy(
                            update={
                                "data_source": "fixture",
                                "source_state": "static",
                                "generation_timestamp": instant.isoformat(),
                            }
                        )
                    }
                )
                state = "static"
    else:
        fixture = load_fixture(fixture_path)
        snapshot = fixture.model_copy(
            update={
                "status": fixture.status.model_copy(
                    update={
                        "data_source": "fixture",
                        "source_state": "static",
                        "generation_timestamp": instant.isoformat(),
                    }
                )
            }
        )
        state = "static"

    snapshot_text = _write_json(
        output_dir / "snapshot.json", snapshot.model_dump(mode="json")
    )
    data_hash = hashlib.sha256(snapshot_text.encode("utf-8")).hexdigest()
    _render_variants(snapshot, output_dir)
    _write_metadata(
        output_dir,
        state=state,
        failure_category=failure_category,
        snapshot=snapshot,
        data_hash=data_hash,
    )
    return snapshot
