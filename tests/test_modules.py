"""Tests for dynamic profile module scripts and templates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from tools.modules import (
    github_metrics,
    music_highlight,
    recent_activity,
    update_readme,
)
from tools.modules import (
    soundcloud as soundcloud_mod,
)
from tools.modules import (
    steam as steam_mod,
)
from tools.profile_builder import cache as cache_utils
from tools.profile_builder.models import (
    GithubMetrics,
    MusicHighlight,
    RecentActivity,
    SoundCloudSnapshot,
    SteamSnapshot,
)
from tools.profile_builder.rendering import render_template


def test_github_metrics_fixture_renders_template(tmp_path) -> None:
    output = tmp_path / "metrics.json"
    metrics = github_metrics.build_metrics(
        output_path=output,
        fixture_path=github_metrics.DEFAULT_FIXTURE,
        token=None,
    )
    rendered = render_template("github-metrics.md.j2", {"metrics": metrics})
    written = GithubMetrics.model_validate_json(output.read_text(encoding="utf-8"))

    assert written.data_source == "fixture"
    assert "### GitHub Metrics" in rendered
    assert "**Public repositories:** 12" in rendered
    # Fixture must not include synthetic star counts or follower counts to avoid
    # fabricating adoption metrics (CONTENT.md: "Do not fabricate: stars, users").
    assert written.stars_received is None
    assert "followers" not in output.read_text(encoding="utf-8")
    # Stars are omitted from the rendered template when the value is None.
    assert "Stars received" not in rendered


def test_recent_activity_filters_and_bounds_live_events(monkeypatch, tmp_path) -> None:
    def fake_get_json(url: str, token: str | None = None):
        assert "events/public" in url
        return [
            {
                "type": "WatchEvent",
                "repo": {"name": "szmyty/ignore"},
                "created_at": "2024-01-20T00:00:00Z",
                "payload": {},
            },
            {
                "type": "PushEvent",
                "repo": {"name": "szmyty/szmyty"},
                "created_at": "2024-01-19T00:00:00Z",
                "payload": {"commits": [{"message": "Updated README"}]},
            },
            {
                "type": "PushEvent",
                "repo": {"name": "szmyty/bot"},
                "created_at": "2024-01-18T00:00:00Z",
                "actor": {"login": "octocat[bot]"},
                "payload": {"commits": [{"message": "Ignore bot"}]},
            },
            {
                "type": "CreateEvent",
                "repo": {"name": "szmyty/one"},
                "created_at": "2024-01-17T00:00:00Z",
                "payload": {"ref_type": "branch", "ref": "main"},
            },
            {
                "type": "PullRequestEvent",
                "repo": {"name": "szmyty/two"},
                "created_at": "2024-01-16T00:00:00Z",
                "payload": {
                    "pull_request": {
                        "title": "Ship module",
                        "html_url": "https://github.com/szmyty/two/pull/1",
                    },
                },
            },
            {
                "type": "IssueCommentEvent",
                "repo": {"name": "szmyty/three"},
                "created_at": "2024-01-15T00:00:00Z",
                "payload": {
                    "issue": {
                        "title": "Bugfix",
                        "html_url": "https://github.com/szmyty/three/issues/2",
                    },
                },
            },
            {
                "type": "ReleaseEvent",
                "repo": {"name": "szmyty/four"},
                "created_at": "2024-01-14T00:00:00Z",
                "payload": {
                    "release": {
                        "name": "v1.0.0",
                        "html_url": (
                            "https://github.com/szmyty/four/releases/tag/v1.0.0"
                        ),
                    },
                },
            },
            {
                "type": "PushEvent",
                "repo": {"name": "szmyty/five"},
                "created_at": "2024-01-13T00:00:00Z",
                "payload": {"commits": [{"message": "Overflow item"}]},
            },
        ], {}

    monkeypatch.setattr(recent_activity, "_github_get_json", fake_get_json)
    output = tmp_path / "activity.json"

    activity = recent_activity.build_activity(
        output_path=output,
        fixture_path=recent_activity.DEFAULT_FIXTURE,
        token="x",
    )

    assert activity.data_source == "live"
    assert len(activity.events) == 5
    assert [event.event_type.value for event in activity.events] == [
        "PushEvent",
        "CreateEvent",
        "PullRequestEvent",
        "IssueCommentEvent",
        "ReleaseEvent",
    ]
    assert all("[bot]" not in event.summary for event in activity.events)


def test_recent_activity_uses_cache_on_rate_limit(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(cache_utils, "CACHE_ROOT", tmp_path / "cache-root")
    cache_utils.write_cache(
        "recent-activity",
        RecentActivity.model_validate_json(
            recent_activity.DEFAULT_FIXTURE.read_text(encoding="utf-8")
        ).model_dump(mode="json"),
    )

    def fake_get_json(url: str, token: str | None = None):
        raise recent_activity.RateLimitedError("HTTP 403")

    monkeypatch.setattr(recent_activity, "_github_get_json", fake_get_json)
    output = tmp_path / "activity.json"

    activity = recent_activity.build_activity(
        output_path=output,
        fixture_path=recent_activity.DEFAULT_FIXTURE,
        token="x",
    )

    assert activity.data_source == "cache"
    assert json.loads(output.read_text(encoding="utf-8"))["data_source"] == "cache"


def test_github_metrics_uses_cache_on_provider_failure(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(cache_utils, "CACHE_ROOT", tmp_path / "cache-root")
    cache_utils.write_cache(
        "github-metrics",
        GithubMetrics.model_validate_json(
            github_metrics.DEFAULT_FIXTURE.read_text(encoding="utf-8")
        ).model_dump(mode="json"),
    )
    monkeypatch.setattr(
        github_metrics,
        "fetch_live_metrics",
        lambda username=github_metrics.USERNAME, token=None: (_ for _ in ()).throw(
            github_metrics.ProviderFailure("boom")
        ),
    )

    output = tmp_path / "metrics.json"
    metrics = github_metrics.build_metrics(
        output_path=output,
        fixture_path=github_metrics.DEFAULT_FIXTURE,
        token="x",
    )

    assert metrics.data_source == "cache"
    assert json.loads(output.read_text(encoding="utf-8"))["data_source"] == "cache"


def test_first_run_without_cache_falls_back_to_fixture(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(cache_utils, "CACHE_ROOT", tmp_path / "cache-root")
    monkeypatch.setattr(
        github_metrics,
        "fetch_live_metrics",
        lambda username=github_metrics.USERNAME, token=None: (_ for _ in ()).throw(
            github_metrics.ProviderFailure("offline")
        ),
    )

    output = tmp_path / "metrics.json"
    metrics = github_metrics.build_metrics(
        output_path=output,
        fixture_path=github_metrics.DEFAULT_FIXTURE,
        token="x",
    )

    assert metrics.data_source == "fixture"
    assert output.exists()


def test_music_highlight_uses_cache_on_malformed_input(tmp_path) -> None:
    input_path = tmp_path / "music.yml"
    input_path.write_text("title: [broken\n", encoding="utf-8")
    output_path = tmp_path / "artifact.yml"
    output_path.write_text(
        yaml.safe_dump(
            {
                "title": "Cached",
                "public_url": "https://soundcloud.com/szmyty",
                "data_source": "manual",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    music = music_highlight.build_music_highlight(
        input_path=input_path,
        output_path=output_path,
        fixture_path=music_highlight.DEFAULT_FIXTURE,
    )

    assert music.data_source == "cache"
    assert "Cached" in output_path.read_text(encoding="utf-8")


def test_music_highlight_first_run_without_cache_uses_fixture(tmp_path) -> None:
    input_path = tmp_path / "missing.yml"
    output_path = tmp_path / "artifact.yml"

    music = music_highlight.build_music_highlight(
        input_path=input_path,
        output_path=output_path,
        fixture_path=music_highlight.DEFAULT_FIXTURE,
    )

    assert music.data_source == "fixture"
    assert (
        MusicHighlight.model_validate(
            yaml.safe_load(output_path.read_text(encoding="utf-8"))
        ).title
        == "Ego Hygiene"
    )


def test_invalid_fixture_json_raises_when_no_fallback(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(cache_utils, "CACHE_ROOT", tmp_path / "cache-root")
    monkeypatch.setattr(
        github_metrics,
        "fetch_live_metrics",
        lambda username=github_metrics.USERNAME, token=None: (_ for _ in ()).throw(
            github_metrics.ProviderFailure("offline")
        ),
    )
    bad_fixture = tmp_path / "broken.json"
    bad_fixture.write_text("{broken", encoding="utf-8")

    with pytest.raises(github_metrics.ProviderFailure):
        github_metrics.build_metrics(
            output_path=tmp_path / "metrics.json",
            fixture_path=bad_fixture,
            token="x",
        )


def test_aggregate_stars_sums_non_archived_repos() -> None:
    repos = [
        {"stargazers_count": 10, "archived": False},
        {"stargazers_count": 5, "archived": False},
        {"stargazers_count": 999, "archived": True},  # archived — excluded
        {"stargazers_count": None, "archived": False},  # missing value — treated as 0
    ]
    assert github_metrics.aggregate_stars(repos) == 15


def test_aggregate_stars_empty_repos_returns_zero() -> None:
    assert github_metrics.aggregate_stars([]) == 0


def test_aggregate_stars_all_archived_returns_zero() -> None:
    repos = [
        {"stargazers_count": 50, "archived": True},
        {"stargazers_count": 30, "archived": True},
    ]
    assert github_metrics.aggregate_stars(repos) == 0


def test_count_recent_releases_counts_within_window(monkeypatch) -> None:
    from datetime import UTC, datetime, timedelta

    now = datetime.now(UTC)
    recent = (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    old = (now - timedelta(days=400)).strftime("%Y-%m-%dT%H:%M:%SZ")

    repos = [
        {"full_name": "szmyty/repo-a"},
        {"full_name": "szmyty/repo-b"},
    ]

    call_count = {"n": 0}

    def fake_get_json(url: str, token: str | None = None):
        call_count["n"] += 1
        if "repo-a" in url:
            return [
                {"draft": False, "published_at": recent},
                {"draft": False, "published_at": old},  # older than window
            ], {}
        # repo-b has a draft release (excluded) and one recent
        return [
            {"draft": True, "published_at": recent},  # draft — excluded
            {"draft": False, "published_at": recent},
        ], {}

    monkeypatch.setattr(github_metrics, "_github_get_json", fake_get_json)

    count = github_metrics.count_recent_releases(repos, token="x")
    # repo-a: 1 recent non-draft; repo-b: 1 recent non-draft (draft excluded)
    assert count == 2


def test_count_recent_releases_skips_404_repos(monkeypatch) -> None:
    repos = [{"full_name": "szmyty/gone"}]

    def fake_get_json(url: str, token: str | None = None):
        raise github_metrics.ProviderFailure("HTTP 404")

    monkeypatch.setattr(github_metrics, "_github_get_json", fake_get_json)
    assert github_metrics.count_recent_releases(repos, token="x") == 0


def test_count_recent_releases_empty_repos() -> None:
    assert github_metrics.count_recent_releases([], token=None) == 0


def test_live_metrics_includes_stars_and_releases(monkeypatch) -> None:
    """fetch_live_metrics populates stars_received and public_releases_count."""
    from datetime import UTC, datetime, timedelta

    recent = (datetime.now(UTC) - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")

    fake_repos = [
        {
            "name": "my-repo",
            "full_name": "szmyty/my-repo",
            "html_url": "https://github.com/szmyty/my-repo",
            "description": "A repo",
            "stargazers_count": 7,
            "archived": False,
            "fork": False,
            "private": False,
            "pushed_at": recent,
            "languages_url": "https://api.github.com/repos/szmyty/my-repo/languages",
        },
    ]

    monkeypatch.setattr(
        github_metrics,
        "fetch_public_repositories",
        lambda username=github_metrics.USERNAME, token=None: fake_repos,
    )
    monkeypatch.setattr(
        github_metrics,
        "fetch_public_repo_count",
        lambda username=github_metrics.USERNAME, token=None: 1,
    )

    def fake_get_json(url: str, token: str | None = None):
        if "languages" in url:
            return {"Python": 1000}, {}
        if "releases" in url:
            return [{"draft": False, "published_at": recent}], {}
        return {}, {}

    monkeypatch.setattr(github_metrics, "_github_get_json", fake_get_json)

    metrics = github_metrics.fetch_live_metrics(token="x")
    assert metrics.stars_received == 7
    assert metrics.public_releases_count == 1
    assert metrics.data_source == "live"


def test_github_metrics_template_shows_stars_when_present() -> None:
    metrics = GithubMetrics(
        top_languages=[],
        public_repo_count=5,
        stars_received=42,
        public_releases_count=3,
        data_source="live",
    )
    rendered = render_template("github-metrics.md.j2", {"metrics": metrics})
    assert "**Stars received:** 42" in rendered
    assert "**Releases (past year):** 3" in rendered


def test_github_metrics_template_omits_stars_when_none() -> None:
    metrics = GithubMetrics(
        top_languages=[],
        public_repo_count=5,
        stars_received=None,
        public_releases_count=None,
        data_source="fixture",
    )
    rendered = render_template("github-metrics.md.j2", {"metrics": metrics})
    assert "Stars received" not in rendered
    assert "Releases (past year)" not in rendered


def test_fetch_public_repos_excludes_forks_and_private(monkeypatch) -> None:
    """fetch_public_repositories filters out forks and private repos."""

    def fake_get_json(url: str, token: str | None = None):
        return [
            {"name": "public-own", "private": False, "fork": False},
            {"name": "forked", "private": False, "fork": True},  # excluded
            {"name": "secret", "private": True, "fork": False},  # excluded
        ], {}

    monkeypatch.setattr(github_metrics, "_github_get_json", fake_get_json)
    repos = github_metrics.fetch_public_repositories(token="x")
    assert len(repos) == 1
    assert repos[0]["name"] == "public-own"


def test_select_maintained_repos_excludes_archived(monkeypatch) -> None:
    from datetime import UTC, datetime, timedelta

    recent = (datetime.now(UTC) - timedelta(days=30)).isoformat()
    repos = [
        {
            "name": "active",
            "html_url": "https://github.com/szmyty/active",
            "description": None,
            "pushed_at": recent,
            "archived": False,
        },
        {
            "name": "archived-repo",
            "html_url": "https://github.com/szmyty/archived-repo",
            "description": None,
            "pushed_at": recent,
            "archived": True,  # excluded
        },
    ]
    maintained = github_metrics.select_maintained_repositories(repos)
    assert len(maintained) == 1
    assert maintained[0].name == "active"


def test_update_readme_reports_unchanged_on_second_render(
    tmp_path, monkeypatch
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "header\n\n"
        "<!-- START:github-metrics -->\n<!-- END:github-metrics -->\n\n"
        "<!-- START:recent-activity -->\n<!-- END:recent-activity -->\n\n"
        "<!-- START:music-highlight -->\n<!-- END:music-highlight -->\n",
        encoding="utf-8",
    )
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    repo_root = Path(__file__).resolve().parents[1]
    for name in [
        "github-metrics.md.j2",
        "recent-activity.md.j2",
        "music-highlight.md.j2",
    ]:
        source = (repo_root / "profile" / "templates" / name).read_text(
            encoding="utf-8"
        )
        (templates_dir / name).write_text(source, encoding="utf-8")

    artifact_root = tmp_path / "profile" / "artifacts"
    (artifact_root / "github-metrics").mkdir(parents=True)
    (artifact_root / "recent-activity").mkdir(parents=True)
    (artifact_root / "music-highlight").mkdir(parents=True)
    (artifact_root / "github-metrics" / "cache.json").write_text(
        github_metrics.DEFAULT_FIXTURE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (artifact_root / "recent-activity" / "cache.json").write_text(
        recent_activity.DEFAULT_FIXTURE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (artifact_root / "music-highlight" / "music.yml").write_text(
        music_highlight.DEFAULT_FIXTURE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    config_path = tmp_path / "modules.yml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "modules": [
                    {
                        "name": "github-metrics",
                        "enabled": True,
                        "region_start_marker": "<!-- START:github-metrics -->",
                        "region_end_marker": "<!-- END:github-metrics -->",
                        "template": "github-metrics.md.j2",
                        "artifact_path": "profile/artifacts/github-metrics/cache.json",
                    },
                    {
                        "name": "recent-activity",
                        "enabled": True,
                        "region_start_marker": "<!-- START:recent-activity -->",
                        "region_end_marker": "<!-- END:recent-activity -->",
                        "template": "recent-activity.md.j2",
                        "artifact_path": "profile/artifacts/recent-activity/cache.json",
                    },
                    {
                        "name": "music-highlight",
                        "enabled": True,
                        "region_start_marker": "<!-- START:music-highlight -->",
                        "region_end_marker": "<!-- END:music-highlight -->",
                        "template": "music-highlight.md.j2",
                        "artifact_path": "profile/artifacts/music-highlight/music.yml",
                    },
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(update_readme, "REPO_ROOT", tmp_path)
    first = update_readme.render_modules(
        config_path=config_path,
        readme_path=readme,
        templates_dir=templates_dir,
    )
    second = update_readme.render_modules(
        config_path=config_path,
        readme_path=readme,
        templates_dir=templates_dir,
    )

    assert all(status == "updated" for _, status in first)
    assert all(status == "unchanged" for _, status in second)
    rendered = readme.read_text(encoding="utf-8")
    assert "### GitHub Metrics" in rendered
    assert "### Recent Public Activity" in rendered
    assert "### Music" in rendered


# ---------------------------------------------------------------------------
# SoundCloud module
# ---------------------------------------------------------------------------


def test_soundcloud_fixture_loads() -> None:
    snap = soundcloud_mod.load_fixture()
    assert isinstance(snap, SoundCloudSnapshot)
    assert snap.data_source == "fixture"
    assert snap.artist_name is not None
    assert snap.profile_url is not None


def test_soundcloud_build_without_credentials_uses_fixture(tmp_path) -> None:
    output = tmp_path / "soundcloud" / "cache.json"
    snap = soundcloud_mod.build_snapshot(
        output_path=output,
        fixture_path=soundcloud_mod.DEFAULT_FIXTURE,
    )
    assert snap.data_source in {"fixture", "static"}
    assert output.exists()


def test_soundcloud_fallback_to_cache(tmp_path) -> None:
    """Cached artifact is preferred over fixture when live provider is absent."""
    cached_snap = SoundCloudSnapshot(
        artist_name="Cached Artist",
        profile_url="https://soundcloud.com/cached",
        data_source="live",
    )
    output = tmp_path / "soundcloud" / "cache.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(cached_snap.model_dump(mode="json"), ensure_ascii=False),
        encoding="utf-8",
    )
    snap = soundcloud_mod.build_snapshot(
        output_path=output,
        fixture_path=soundcloud_mod.DEFAULT_FIXTURE,
    )
    assert snap.artist_name == "Cached Artist"
    assert snap.data_source == "cache"


# ---------------------------------------------------------------------------
# Steam module
# ---------------------------------------------------------------------------


def test_steam_fixture_loads() -> None:
    snap = steam_mod.load_fixture()
    assert isinstance(snap, SteamSnapshot)
    assert snap.data_source == "fixture"
    assert snap.display_name is not None
    assert len(snap.recent_games) >= 1


def test_steam_build_without_credentials_uses_fixture(tmp_path) -> None:
    output = tmp_path / "steam" / "cache.json"
    snap = steam_mod.build_snapshot(
        output_path=output,
        fixture_path=steam_mod.DEFAULT_FIXTURE,
    )
    assert snap.data_source in {"fixture", "static"}
    assert output.exists()


def test_steam_fallback_to_cache(tmp_path) -> None:
    """Cached artifact is preferred over fixture when live provider is absent."""
    cached_snap = SteamSnapshot(
        display_name="Cached Player",
        profile_url="https://steamcommunity.com/id/cached/",
        data_source="live",
    )
    output = tmp_path / "steam" / "cache.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(cached_snap.model_dump(mode="json"), ensure_ascii=False),
        encoding="utf-8",
    )
    snap = steam_mod.build_snapshot(
        output_path=output,
        fixture_path=steam_mod.DEFAULT_FIXTURE,
    )
    assert snap.display_name == "Cached Player"
    assert snap.data_source == "cache"


def test_steam_recent_games_capped(tmp_path) -> None:
    """recent_games list is bounded to at most 5 entries."""
    snap = steam_mod.load_fixture()
    assert len(snap.recent_games) <= 5
