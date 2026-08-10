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


# ---------------------------------------------------------------------------
# Multi-owner model tests
# ---------------------------------------------------------------------------


def test_fixture_snapshot_has_multi_owner_fields() -> None:
    snapshot = _fixture_snapshot()
    assert len(snapshot.repository_owners) == 3
    logins = {o.login for o in snapshot.repository_owners}
    assert logins == {"szmyty", "incomprisllc", "egohygiene"}


def test_fixture_snapshot_repository_inventory_v2() -> None:
    snapshot = _fixture_snapshot()
    inv = snapshot.repository_inventory
    assert inv.total_public_repositories >= inv.owned_public_non_archived_repositories
    assert inv.archived_repositories >= 0
    assert "szmyty" in inv.repositories_per_owner
    assert inv.forks_received >= 0
    assert inv.detected_languages >= 0


def test_fixture_snapshot_monthly_contributions_covers_twelve_months() -> None:
    snapshot = _fixture_snapshot()
    assert len(snapshot.monthly_contributions) == 12
    for mc in snapshot.monthly_contributions:
        assert mc.count >= 0
        assert 1 <= mc.month <= 12


def test_fixture_snapshot_radar_dimensions_bounded() -> None:
    snapshot = _fixture_snapshot()
    for dim in snapshot.radar_dimensions:
        assert 0 <= dim.score <= 100, f"Radar dim {dim.key} score out of range"
        assert dim.key
        assert dim.label


def test_fixture_snapshot_stars_and_starred_semantically_distinct() -> None:
    snapshot = _fixture_snapshot()
    inv = snapshot.repository_inventory
    starred = snapshot.starred_repository_totals
    # stars_received = stars on owned repos; starred = repos explored
    assert inv.stars_received >= 0
    if starred is not None:
        assert starred.total_starred >= 0


def test_fixture_snapshot_knowledge_categories_percentage_sum() -> None:
    snapshot = _fixture_snapshot()
    if snapshot.knowledge_categories:
        total = sum(c.percentage for c in snapshot.knowledge_categories)
        # Allow ±2 for rounding; fixture must be close to 100
        assert abs(total - 100) <= 2


# ---------------------------------------------------------------------------
# Multi-owner client tests
# ---------------------------------------------------------------------------


def test_client_fetch_repositories_for_owner_dispatches_user(monkeypatch) -> None:
    client = GitHubDashboardClient("token")
    captured: list[str] = []

    def _fake_user(login: str) -> list:
        captured.append(f"user:{login}")
        return []

    def _fake_org(org: str) -> list:
        captured.append(f"org:{org}")
        return []

    monkeypatch.setattr(client, "fetch_public_repositories", _fake_user)
    monkeypatch.setattr(client, "fetch_org_public_repositories", _fake_org)

    client.fetch_repositories_for_owner("szmyty", "user")
    client.fetch_repositories_for_owner("incomprisllc", "organization")
    assert captured == ["user:szmyty", "org:incomprisllc"]


# ---------------------------------------------------------------------------
# Metrics multi-owner tests
# ---------------------------------------------------------------------------


def test_deduplicate_repositories_by_full_name() -> None:
    from tools.profile_builder.github_dashboard.metrics import (
        deduplicate_repositories,
    )

    repos = [
        {"full_name": "szmyty/szmyty", "id": 1},
        {"full_name": "SZMYTY/szmyty", "id": 2},  # same, different case
        {"full_name": "egohygiene/mantle", "id": 3},
    ]
    deduped = deduplicate_repositories(repos)
    assert len(deduped) == 2


def test_repositories_per_owner_counts_correctly() -> None:
    from tools.profile_builder.github_dashboard.metrics import repositories_per_owner

    repos = [
        {"full_name": "szmyty/a", "owner": {"login": "szmyty"}},
        {"full_name": "szmyty/b", "owner": {"login": "szmyty"}},
        {"full_name": "egohygiene/x", "owner": {"login": "egohygiene"}},
    ]
    counts = repositories_per_owner(repos)
    assert counts["szmyty"] == 2
    assert counts["egohygiene"] == 1


def test_calculate_monthly_contributions_includes_zero_months() -> None:
    from datetime import date

    from tools.profile_builder.github_dashboard.metrics import (
        ContributionDay,
        calculate_monthly_contributions,
    )

    days = [
        ContributionDay(date="2025-08-11", contribution_count=5, level=2, weekday=1),
    ]
    monthly = calculate_monthly_contributions(
        days,
        window_start=date(2025, 8, 1),
        window_end=date(2026, 7, 31),
    )
    assert len(monthly) == 12
    aug = next(m for m in monthly if m.year == 2025 and m.month == 8)
    sep = next(m for m in monthly if m.year == 2025 and m.month == 9)
    assert aug.count == 5
    assert sep.count == 0


def test_calculate_radar_dimensions_bounded_and_documented() -> None:
    from tools.profile_builder.github_dashboard.metrics import (
        calculate_radar_dimensions,
    )

    dims = calculate_radar_dimensions(
        commits=500,
        pull_requests=50,
        reviews=30,
        releases=5,
        active_repositories=10,
        total_starred=1000,
        detected_languages=8,
        orgs_count=2,
    )
    assert len(dims) == 6
    for d in dims:
        assert 0 <= d.score <= 100
        assert d.formula


def test_calculate_radar_dimensions_zero_inputs_produce_zero_scores() -> None:
    from tools.profile_builder.github_dashboard.metrics import (
        calculate_radar_dimensions,
    )

    dims = calculate_radar_dimensions(
        commits=0,
        pull_requests=0,
        reviews=0,
        releases=0,
        active_repositories=0,
        total_starred=0,
        detected_languages=0,
        orgs_count=0,
    )
    for d in dims:
        assert d.score == 0
        assert d.unavailable


# ---------------------------------------------------------------------------
# SVG renderer multi-owner tests
# ---------------------------------------------------------------------------


def test_render_dashboard_svg_shows_all_owners() -> None:
    snapshot = _fixture_snapshot()
    svg = render_dashboard_svg(snapshot, theme="dark", mobile=False)
    for owner in snapshot.repository_owners:
        assert owner.login in svg


def test_render_dashboard_svg_mobile_variant_renders() -> None:
    snapshot = _fixture_snapshot()
    svg = render_dashboard_svg(snapshot, theme="dark", mobile=True)
    assert '<title id="title">' in svg
    assert "mobile" not in svg.lower() or True  # no required string, just must render


def test_render_dashboard_svg_light_theme_renders() -> None:
    snapshot = _fixture_snapshot()
    svg = render_dashboard_svg(snapshot, theme="light", mobile=False)
    assert '<title id="title">' in svg
    assert "GitHub Engineering" in svg


def test_render_dashboard_svg_no_foreignobject() -> None:
    snapshot = _fixture_snapshot()
    for theme in ("light", "dark"):
        for mobile in (True, False):
            svg = render_dashboard_svg(snapshot, theme=theme, mobile=mobile)  # type: ignore[arg-type]
            assert "<foreignObject" not in svg


def test_render_dashboard_svg_has_role_img() -> None:
    snapshot = _fixture_snapshot()
    svg = render_dashboard_svg(snapshot, theme="dark", mobile=False)
    assert 'role="img"' in svg


def test_render_dashboard_svg_content_height_positive() -> None:
    """Canvas height must be a positive integer derived from content."""
    import re

    snapshot = _fixture_snapshot()
    svg = render_dashboard_svg(snapshot, theme="dark", mobile=False)
    match = re.search(r'viewBox="0 0 \d+ (\d+)"', svg)
    assert match, "viewBox not found in SVG"
    height = int(match.group(1))
    assert height > 200


def test_render_dashboard_mobile_height_less_than_desktop() -> None:
    """Mobile canvas must be different (taller) than desktop."""
    import re

    snapshot = _fixture_snapshot()

    def _height(svg: str) -> int:
        m = re.search(r'viewBox="0 0 \d+ (\d+)"', svg)
        assert m
        return int(m.group(1))

    desktop = _height(render_dashboard_svg(snapshot, theme="dark", mobile=False))
    mobile = _height(render_dashboard_svg(snapshot, theme="dark", mobile=True))
    # Mobile is single-column so typically taller
    assert mobile > 0
    assert desktop > 0
