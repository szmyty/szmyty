"""Focused tests for the GitHub engineering dashboard module."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from urllib import error

import pytest

from tools.profile_builder.github_dashboard import models
from tools.profile_builder.github_dashboard import service as dashboard_service
from tools.profile_builder.github_dashboard.client import (
    GitHubDashboardClient,
    ProviderFailure,
    RateLimitedError,
)
from tools.profile_builder.github_dashboard.metrics import (
    aggregate_language_shares,
    calculate_streaks,
)
from tools.profile_builder.github_dashboard.renderer import render_dashboard_svg
from tools.profile_builder.github_dashboard.service import build_dashboard


def _fixture_snapshot() -> models.GitHubDashboardSnapshot:
    path = (
        Path(__file__).resolve().parents[1]
        / "profile"
        / "fixtures"
        / "github-dashboard.json"
    )
    return models.GitHubDashboardSnapshot.model_validate_json(
        path.read_text(encoding="utf-8")
    )


def test_calculate_streaks_ends_yesterday_when_today_is_empty() -> None:
    days = [
        models.ContributionDay(
            date=value,
            contribution_count=count,
            level=1 if count else 0,
            weekday=index,
        )
        for index, (value, count) in enumerate(
            [
                ("2026-08-04", 1),
                ("2026-08-05", 1),
                ("2026-08-06", 1),
                ("2026-08-07", 1),
                ("2026-08-08", 2),
                ("2026-08-09", 0),
            ]
        )
    ]
    current, longest = calculate_streaks(
        days,
        today=datetime(2026, 8, 9, tzinfo=UTC).date(),
    )
    assert current == 5
    assert longest == 5


def test_aggregate_language_shares_rounds_to_coherent_total() -> None:
    repositories = [
        {"languages_url": "repo-a"},
        {"languages_url": "repo-b"},
    ]
    shares = aggregate_language_shares(
        repositories,
        {
            "repo-a": {"Python": 51, "TypeScript": 24, "Shell": 10},
            "repo-b": {"Python": 49, "Go": 9, "HTML": 7, "CSS": 5},
        },
    )
    assert sum(item.percentage for item in shares) == 100
    assert shares[0].name == "Python"


def test_client_only_treats_rate_limited_403_as_rate_limit(monkeypatch) -> None:
    client = GitHubDashboardClient("token")

    def _raise_scope_error(*args, **kwargs):
        raise error.HTTPError(
            url="https://api.github.com/graphql",
            code=403,
            msg="Forbidden",
            hdrs={"X-RateLimit-Remaining": "42"},
            fp=BytesIO(b"{}"),
        )

    monkeypatch.setattr("urllib.request.urlopen", _raise_scope_error)

    try:
        client._request_json("https://api.github.com/graphql")
    except ProviderFailure as exc:
        assert "HTTP 403" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ProviderFailure for non-rate-limited 403")

    def _raise_rate_limit(*args, **kwargs):
        raise error.HTTPError(
            url="https://api.github.com/graphql",
            code=403,
            msg="Forbidden",
            hdrs={"X-RateLimit-Remaining": "0"},
            fp=BytesIO(b"{}"),
        )

    monkeypatch.setattr("urllib.request.urlopen", _raise_rate_limit)

    try:
        client._request_json("https://api.github.com/graphql")
    except RateLimitedError:
        pass
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected RateLimitedError when rate limit is exhausted")


def test_render_dashboard_svg_includes_accessible_metadata() -> None:
    snapshot = _fixture_snapshot()
    svg = render_dashboard_svg(snapshot, theme="dark", mobile=False)
    assert '<title id="title">' in svg
    assert '<desc id="desc">' in svg
    assert "GitHub Engineering" in svg
    assert "<foreignObject" not in svg


def test_render_dashboard_svg_rejects_unknown_theme() -> None:
    snapshot = _fixture_snapshot()
    with pytest.raises(ValueError):
        render_dashboard_svg(snapshot, theme="solarized")  # type: ignore[arg-type]


def test_build_dashboard_uses_cache_on_provider_failure(tmp_path, monkeypatch) -> None:
    output_dir = tmp_path / "github-dashboard"
    output_dir.mkdir(parents=True)
    fixture = _fixture_snapshot()
    cached = fixture.model_copy(
        update={
            "status": fixture.status.model_copy(
                update={
                    "data_source": "live",
                    "source_state": "fresh",
                    "data_timestamp": "2026-08-09T12:00:00+00:00",
                    "generation_timestamp": "2026-08-09T12:00:00+00:00",
                }
            )
        }
    )
    (output_dir / "snapshot.json").write_text(
        json.dumps(cached.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )

    def _fail(**kwargs):
        raise RuntimeError("upstream failed")

    monkeypatch.setattr(dashboard_service, "collect_live_snapshot", _fail)

    snapshot = build_dashboard(
        output_dir=output_dir,
        fixture_path=Path(__file__).resolve().parents[1]
        / "profile"
        / "fixtures"
        / "github-dashboard.json",
        token="token",
        now=datetime(2026, 8, 9, 18, 0, tzinfo=UTC),
    )
    assert snapshot.status.data_source == "cache"
    assert snapshot.status.source_state == "failed-with-fallback"
    assert (output_dir / "metadata.json").exists()
    assert (output_dir / "card-dark.svg").exists()
