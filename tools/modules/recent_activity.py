"""Fetch and normalize recent public GitHub activity for the profile README."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import click

from tools.modules.github_metrics import (
    ProviderFailure,
    RateLimitedError,
    _github_get_json,
)
from tools.profile_builder import cache as cache_utils
from tools.profile_builder.models import (
    ActivityEvent,
    ActivityEventType,
    RecentActivity,
)

MODULE_NAME = 'recent-activity'
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = REPO_ROOT / 'profile' / 'fixtures' / 'recent-activity.json'
DEFAULT_OUTPUT = REPO_ROOT / 'profile' / 'artifacts' / MODULE_NAME / 'cache.json'
USERNAME = 'szmyty'
API_ROOT = 'https://api.github.com'
ALLOWED_EVENT_TYPES = {
    ActivityEventType.PUSH.value,
    ActivityEventType.CREATE.value,
    ActivityEventType.PULL_REQUEST.value,
    ActivityEventType.ISSUE_COMMENT.value,
    ActivityEventType.RELEASE.value,
}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def load_fixture(path: Path = DEFAULT_FIXTURE) -> RecentActivity:
    """Load sanitized offline recent activity fixture data."""
    return RecentActivity.model_validate_json(path.read_text(encoding='utf-8'))


def load_cached_activity() -> RecentActivity | None:
    """Load cached recent activity if present and valid."""
    raw = cache_utils.read_cache(MODULE_NAME)
    if raw is None:
        return None
    activity = RecentActivity.model_validate(raw)
    return activity.model_copy(update={'data_source': 'cache'})


def _is_bot_event(event: dict[str, Any]) -> bool:
    actor = event.get('actor') or {}
    login = str(actor.get('display_login') or actor.get('login') or '')
    return login.endswith('[bot]') or actor.get('type') == 'Bot'


def _summarize_event(event: dict[str, Any]) -> tuple[str, str] | None:
    repo = event.get('repo') or {}
    repo_name = str(repo.get('name') or '')
    repo_url = f'https://github.com/{repo_name}' if repo_name else 'https://github.com/szmyty'
    payload = event.get('payload') or {}
    event_type = event.get('type')

    if event_type == ActivityEventType.PUSH.value:
        commits = payload.get('commits') or []
        if commits:
            first = commits[0].get('message') or 'Pushed commits'
            return repo_url, str(first).splitlines()[0]
        return repo_url, 'Pushed commits'
    if event_type == ActivityEventType.CREATE.value:
        ref_type = payload.get('ref_type') or 'repository'
        ref_name = payload.get('ref') or repo_name
        return repo_url, f'Created {ref_type} {ref_name}'
    if event_type == ActivityEventType.PULL_REQUEST.value:
        pr = payload.get('pull_request') or {}
        title = pr.get('title') or 'Updated pull request'
        return str(pr.get('html_url') or repo_url), str(title)
    if event_type == ActivityEventType.ISSUE_COMMENT.value:
        issue = payload.get('issue') or {}
        title = issue.get('title') or 'Commented on issue'
        return str(issue.get('html_url') or repo_url), f'Commented on {title}'
    if event_type == ActivityEventType.RELEASE.value:
        release = payload.get('release') or {}
        name = release.get('name') or release.get('tag_name') or 'Published release'
        return str(release.get('html_url') or repo_url), f'Published {name}'
    return None


def normalize_events(events: list[dict[str, Any]]) -> RecentActivity:
    """Normalize raw public GitHub events into a bounded display model."""
    normalized: list[ActivityEvent] = []
    for event in events:
        event_type = event.get('type')
        if event_type not in ALLOWED_EVENT_TYPES:
            continue
        if _is_bot_event(event):
            continue
        repo = event.get('repo') or {}
        repo_name = str(repo.get('name') or '')
        if not repo_name:
            continue
        summary = _summarize_event(event)
        if summary is None:
            continue
        repo_url, summary_text = summary
        occurred_at = str(event.get('created_at') or '')[:10]
        normalized.append(
            ActivityEvent(
                event_type=ActivityEventType(event_type),
                repo=repo_name,
                repo_url=repo_url,
                summary=summary_text,
                occurred_at=occurred_at,
            )
        )
        if len(normalized) == 5:
            break
    return RecentActivity(events=normalized, data_source='live')


def fetch_live_activity(username: str = USERNAME, token: str | None = None) -> RecentActivity:
    """Fetch normalized public activity from GitHub."""
    payload, _ = _github_get_json(f'{API_ROOT}/users/{username}/events/public?per_page=20', token)
    if not isinstance(payload, list):
        raise ProviderFailure('Unexpected recent-activity payload from GitHub API.')
    events = [item for item in payload if isinstance(item, dict) and item.get('public') is not False]
    return normalize_events(events)


def build_activity(output_path: Path, fixture_path: Path = DEFAULT_FIXTURE, token: str | None = None) -> RecentActivity:
    """Build recent activity using live data, cache fallback, or fixture fallback."""
    if not token:
        activity = load_fixture(fixture_path)
        _write_json(output_path, activity.model_dump(mode='json'))
        return activity

    try:
        activity = fetch_live_activity(token=token)
        cache_utils.write_cache(MODULE_NAME, activity.model_dump(mode='json'))
    except (ProviderFailure, RateLimitedError, ValueError) as exc:
        cached = load_cached_activity()
        if cached is not None:
            activity = cached
        else:
            try:
                activity = load_fixture(fixture_path)
            except Exception as fixture_exc:  # noqa: BLE001
                raise ProviderFailure(f'No usable recent activity data: {exc}; fixture failed: {fixture_exc}') from fixture_exc
    _write_json(output_path, activity.model_dump(mode='json'))
    return activity


@click.command()
@click.option('--output', 'output_path', type=click.Path(path_type=Path), default=str(DEFAULT_OUTPUT), show_default=True)
@click.option('--fixture', 'fixture_path', type=click.Path(exists=True, path_type=Path), default=str(DEFAULT_FIXTURE), show_default=True)
def main(output_path: Path, fixture_path: Path) -> None:
    """Write normalized recent activity to *output_path*."""
    token = os.getenv('GITHUB_TOKEN')
    activity = build_activity(output_path=output_path, fixture_path=fixture_path, token=token)
    click.echo(f'recent-activity: wrote {output_path} ({activity.data_source})')


if __name__ == '__main__':
    main()
