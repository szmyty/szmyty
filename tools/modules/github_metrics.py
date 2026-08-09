"""Fetch and normalize public GitHub metrics for the profile README."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from email.message import Message
from pathlib import Path
from typing import Any
from urllib import error, parse, request

import click

from tools.profile_builder import cache as cache_utils
from tools.profile_builder.models import GithubMetrics, LanguageEntry, RepositorySummary

MODULE_NAME = "github-metrics"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = REPO_ROOT / "profile" / "fixtures" / "github-metrics.json"
DEFAULT_OUTPUT = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME / "cache.json"
USERNAME = "szmyty"
API_ROOT = "https://api.github.com"
MAINTAINED_WINDOW_DAYS = 365


class ProviderFailure(RuntimeError):
    """Raised when live data cannot be collected."""


class RateLimitedError(ProviderFailure):
    """Raised when GitHub responds with rate limiting or temporary denial."""


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_fixture(path: Path = DEFAULT_FIXTURE) -> GithubMetrics:
    """Load sanitized offline fixture data."""
    return GithubMetrics.model_validate_json(path.read_text(encoding="utf-8"))


def load_cached_metrics() -> GithubMetrics | None:
    """Load cached GitHub metrics if present and valid."""
    raw = cache_utils.read_cache(MODULE_NAME)
    if raw is None:
        return None
    metrics = GithubMetrics.model_validate(raw)
    return metrics.model_copy(update={"data_source": "cache"})


def _github_get_json(url: str, token: str | None = None) -> tuple[Any, Message]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "szmyty-profile-builder/1.0",
    }
    if token:
        headers["Authorization"] = " ".join(["Bearer", token])
    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req) as response:  # noqa: S310
            payload = response.read().decode("utf-8")
            return json.loads(payload), response.headers
    except error.HTTPError as exc:
        if exc.code in {403, 429}:
            raise RateLimitedError(f"GitHub API rate limited: HTTP {exc.code}") from exc
        raise ProviderFailure(f"GitHub API request failed: HTTP {exc.code}") from exc
    except error.URLError as exc:
        raise ProviderFailure(f"GitHub API unavailable: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise ProviderFailure(f"GitHub API returned invalid JSON: {exc}") from exc


def _parse_next_link(headers: Message) -> str | None:
    link_header = headers.get("Link")
    if not link_header:
        return None
    for part in link_header.split(","):
        chunks = [item.strip() for item in part.split(";")]
        if len(chunks) < 2:
            continue
        url_part, rel_part = chunks[0], chunks[1]
        if (
            rel_part == 'rel="next"'
            and url_part.startswith("<")
            and url_part.endswith(">")
        ):
            return url_part[1:-1]
    return None


def fetch_public_repositories(
    username: str = USERNAME,
    token: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch all public, non-fork repositories owned by *username*."""
    params = parse.urlencode({"per_page": 100, "type": "owner", "sort": "updated"})
    next_url = f"{API_ROOT}/users/{username}/repos?{params}"
    repositories: list[dict[str, Any]] = []
    while next_url:
        payload, headers = _github_get_json(next_url, token)
        if not isinstance(payload, list):
            raise ProviderFailure("Unexpected repository payload from GitHub API.")
        repositories.extend(
            repo
            for repo in payload
            if isinstance(repo, dict)
            and not repo.get("private", False)
            and not repo.get("fork", False)
        )
        next_url = _parse_next_link(headers)
    return repositories


def fetch_public_repo_count(username: str = USERNAME, token: str | None = None) -> int:
    """Fetch the public repository count from the public user profile."""
    payload, _ = _github_get_json(f"{API_ROOT}/users/{username}", token)
    if not isinstance(payload, dict) or "public_repos" not in payload:
        raise ProviderFailure("Unexpected user payload from GitHub API.")
    return int(payload["public_repos"])


_LANGUAGE_SAMPLE_LIMIT = 10  # Limit API calls; sample most-recently-pushed repos.


def aggregate_languages(
    repositories: list[dict[str, Any]],
    token: str | None = None,
) -> list[LanguageEntry]:
    """Aggregate repository language byte counts into percentage shares.

    To keep API call count bounded, only the *_LANGUAGE_SAMPLE_LIMIT*
    most-recently-pushed repositories are queried for language data.
    """
    totals: dict[str, int] = {}
    sampled = repositories[:_LANGUAGE_SAMPLE_LIMIT]
    for repo in sampled:
        languages_url = repo.get("languages_url")
        if not languages_url:
            continue
        payload, _ = _github_get_json(str(languages_url), token)
        if not isinstance(payload, dict):
            raise ProviderFailure("Unexpected language payload from GitHub API.")
        for name, value in payload.items():
            if not isinstance(name, str):
                continue
            totals[name] = totals.get(name, 0) + int(value)
    total_bytes = sum(totals.values())
    if total_bytes <= 0:
        return []
    return [
        LanguageEntry(name=name, percentage=round((value / total_bytes) * 100, 1))
        for name, value in sorted(
            totals.items(), key=lambda item: item[1], reverse=True
        )[:5]
    ]


def select_maintained_repositories(
    repositories: list[dict[str, Any]],
) -> list[RepositorySummary]:
    """Select recently pushed public repositories as actively maintained."""
    cutoff = datetime.now(UTC) - timedelta(days=MAINTAINED_WINDOW_DAYS)
    maintained: list[RepositorySummary] = []
    for repo in repositories:
        pushed_at = repo.get("pushed_at")
        if not pushed_at:
            continue
        pushed = datetime.fromisoformat(str(pushed_at).replace("Z", "+00:00"))
        if pushed < cutoff or repo.get("archived", False):
            continue
        maintained.append(
            RepositorySummary(
                name=str(repo.get("name", "unknown")),
                url=str(repo.get("html_url", f"https://github.com/{USERNAME}")),
                description=repo.get("description"),
                is_maintained=True,
            )
        )
    return maintained[:5]


def fetch_latest_release(
    repositories: list[dict[str, Any]],
    token: str | None = None,
) -> str | None:
    """Return the newest public release in ``repo@tag`` format, if any."""
    latest: tuple[datetime, str] | None = None
    for repo in repositories:
        full_name = repo.get("full_name")
        if not full_name:
            continue
        try:
            payload, _ = _github_get_json(
                f"{API_ROOT}/repos/{full_name}/releases/latest",
                token,
            )
        except ProviderFailure as exc:
            if "HTTP 404" in str(exc):
                continue
            raise
        if not isinstance(payload, dict):
            continue
        tag_name = payload.get("tag_name")
        published_at = payload.get("published_at")
        if not tag_name or not published_at:
            continue
        published = datetime.fromisoformat(str(published_at).replace("Z", "+00:00"))
        candidate = (published, f"{repo.get('name', full_name)}@{tag_name}")
        if latest is None or candidate[0] > latest[0]:
            latest = candidate
    return None if latest is None else latest[1]


def aggregate_stars(repositories: list[dict[str, Any]]) -> int:
    """Sum stargazers_count across owned, non-fork, non-archived public repositories.

    Repositories are already pre-filtered to exclude forks by
    ``fetch_public_repositories``.  Archived repositories are additionally
    excluded here because their star counts reflect historical rather than
    active community interest.

    Methodology: sum of ``stargazers_count`` from the GitHub REST
    ``/users/{username}/repos`` response, type=owner, excluding archived.
    """
    return sum(
        int(repo.get("stargazers_count") or 0)
        for repo in repositories
        if not repo.get("archived", False)
    )


def count_recent_releases(
    repositories: list[dict[str, Any]],
    token: str | None = None,
    window_days: int = MAINTAINED_WINDOW_DAYS,
) -> int:
    """Count public releases published within *window_days* across all repositories.

    Methodology: for each owned non-fork public repository, fetch the list of
    releases (paginated) and count those whose ``published_at`` falls within
    the rolling window.  Draft releases are excluded because they are not
    publicly visible.

    The result is a public-snapshot estimate — it reflects the window at the
    time the data was fetched.

    Ordering assumption: the GitHub Releases API returns releases newest-first
    (``/repos/{owner}/{repo}/releases`` with default ``per_page``).  This is
    documented behaviour but not contractually guaranteed.  As an optimisation,
    pagination stops as soon as the current page contains any release older than
    the cutoff, because all subsequent pages will contain only older releases
    given strict newest-first ordering.  All within-window releases on the same
    page as the first out-of-window release are still counted before stopping.
    If the API ever returns pages out of order, releases on later pages would be
    silently missed; the count is therefore labelled a public-snapshot estimate.
    """
    cutoff = datetime.now(UTC) - timedelta(days=window_days)
    total = 0
    for repo in repositories:
        full_name = repo.get("full_name")
        if not full_name:
            continue
        params = parse.urlencode({"per_page": 100})
        next_url: str | None = f"{API_ROOT}/repos/{full_name}/releases?{params}"
        while next_url:
            try:
                payload, headers = _github_get_json(next_url, token)
            except ProviderFailure as exc:
                if "HTTP 404" in str(exc):
                    break
                raise
            if not isinstance(payload, list):
                break
            found_older = False
            for release in payload:
                if not isinstance(release, dict):
                    continue
                if release.get("draft", False):
                    continue
                published_at = release.get("published_at")
                if not published_at:
                    continue
                published = datetime.fromisoformat(
                    str(published_at).replace("Z", "+00:00")
                )
                if published < cutoff:
                    # Newest-first ordering: remaining pages are all older.
                    found_older = True
                    continue
                total += 1
            if found_older:
                break
            next_url = _parse_next_link(headers)
    return total


def fetch_live_metrics(
    username: str = USERNAME, token: str | None = None
) -> GithubMetrics:
    """Fetch normalized live GitHub metrics."""
    repositories = fetch_public_repositories(username=username, token=token)
    return GithubMetrics(
        top_languages=aggregate_languages(repositories, token=token),
        public_repo_count=fetch_public_repo_count(username=username, token=token),
        stars_received=aggregate_stars(repositories),
        public_releases_count=count_recent_releases(repositories, token=token),
        maintained_repos=select_maintained_repositories(repositories),
        latest_release=fetch_latest_release(repositories, token=token),
        data_source="live",
    )


def build_metrics(
    output_path: Path,
    fixture_path: Path = DEFAULT_FIXTURE,
    token: str | None = None,
) -> GithubMetrics:
    """Build metrics using live data, cached fallback, or fixture fallback."""
    if not token:
        metrics = load_fixture(fixture_path)
        _write_json(output_path, metrics.model_dump(mode="json"))
        return metrics

    try:
        metrics = fetch_live_metrics(token=token)
        cache_utils.write_cache(MODULE_NAME, metrics.model_dump(mode="json"))
    except (ProviderFailure, ValueError) as exc:
        cached = load_cached_metrics()
        if cached is not None:
            metrics = cached
        else:
            try:
                metrics = load_fixture(fixture_path)
            except Exception as fixture_exc:  # noqa: BLE001
                raise ProviderFailure(
                    f"No usable metrics data: {exc}; fixture failed: {fixture_exc}"
                ) from fixture_exc
    _write_json(output_path, metrics.model_dump(mode="json"))
    return metrics


@click.command()
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_OUTPUT),
    show_default=True,
)
@click.option(
    "--fixture",
    "fixture_path",
    type=click.Path(exists=True, path_type=Path),
    default=str(DEFAULT_FIXTURE),
    show_default=True,
)
def main(output_path: Path, fixture_path: Path) -> None:
    """Write normalized GitHub metrics to *output_path*."""
    token = os.getenv("GITHUB_TOKEN")
    metrics = build_metrics(
        output_path=output_path, fixture_path=fixture_path, token=token
    )
    click.echo(f"github-metrics: wrote {output_path} ({metrics.data_source})")


if __name__ == "__main__":
    main()
