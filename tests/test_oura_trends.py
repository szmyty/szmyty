"""Tests for privacy-bounded Oura aggregate SVG publication."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from tools.modules import oura_trends as oura
from tools.profile_builder.models import (
    OURA_PUBLIC_AGGREGATE_ALLOWLIST,
    OuraTrendsAggregate,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "profile"
    / "fixtures"
    / "oura-trends.json"
)
REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "profile"
    / "content"
    / "modules-registry.yml"
)


def _aggregate(**overrides) -> OuraTrendsAggregate:
    values = {
        "window_days": 90,
        "contributing_days": 70,
        "period_label": "Aug 2026",
        "avg_sleep_hours": None,
        "sleep_regularity_band": None,
        "avg_readiness_band": "average",
        "activity_consistency_band": "moderate",
        "hrv_direction": None,
        "is_synthetic": False,
        "data_source": "live",
        "generated_month": "2026-08",
    }
    values.update(overrides)
    return OuraTrendsAggregate.model_validate(values)


def test_model_rejects_unknown_raw_provider_fields() -> None:
    with pytest.raises(ValidationError):
        OuraTrendsAggregate.model_validate(
            {
                **_aggregate().model_dump(mode="json"),
                "daily_sleep_records": [{"day": "2026-08-01", "score": 80}],
            }
        )


def test_apply_allowlist_drops_auth_location_and_daily_arrays() -> None:
    raw = {
        **_aggregate().model_dump(mode="json"),
        "access_token": "secret",
        "timezone": "America/New_York",
        "daily": [{"day": "2026-08-01"}],
    }
    filtered = oura._apply_allowlist(raw)
    assert set(filtered).issubset(OURA_PUBLIC_AGGREGATE_ALLOWLIST)
    assert "access_token" not in filtered
    assert "timezone" not in filtered
    assert "daily" not in filtered


def test_window_dates_enforces_safety_buffer(monkeypatch) -> None:
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 8, 21, 12, 0, tzinfo=UTC)

    monkeypatch.setattr(oura, "datetime", FixedDatetime)
    start, end = oura._window_dates(90)

    assert end == date(2026, 8, 21) - timedelta(days=oura.SAFETY_BUFFER_DAYS)
    assert (end - start).days == 89


def test_parse_daily_scores_ignores_malformed_records() -> None:
    series = oura._parse_daily_scores(
        {
            "data": [
                {"day": "2026-08-01", "score": 80},
                {"day": "bad", "score": 90},
                {"day": "2026-08-02", "score": None},
                {"day": "2026-08-03", "score": 70.5},
            ]
        }
    )
    assert series == [
        (date(2026, 8, 1), 80.0),
        (date(2026, 8, 3), 70.5),
    ]


def test_weekly_scores_are_rounded_and_unlabeled() -> None:
    series = [
        (date(2026, 8, 3), 81.0),
        (date(2026, 8, 4), 84.0),
        (date(2026, 8, 10), 72.0),
        (date(2026, 8, 11), 73.0),
    ]
    assert oura._weekly_scores(series) == [80, 70]


def test_fetch_live_uses_daily_scope_summary_endpoints(monkeypatch) -> None:
    days = [
        (date(2026, 5, 1) + timedelta(days=index)).isoformat()
        for index in range(30)
    ]

    def fake_get(endpoint: str, token: str, params: dict[str, str]):
        assert params["fields"] == "day,score"
        assert endpoint in {
            "usercollection/daily_sleep",
            "usercollection/daily_readiness",
            "usercollection/daily_activity",
        }
        return {
            "data": [
                {"day": day, "score": 75 + (index % 10)}
                for index, day in enumerate(days)
            ],
            "next_token": None,
        }

    monkeypatch.setattr(oura, "_oura_get", fake_get)
    aggregate, trends = oura.fetch_live_with_trends("oauth-token")

    assert aggregate.data_source == "live"
    assert aggregate.is_synthetic is False
    assert aggregate.contributing_days == 30
    assert set(trends) == {"sleep", "readiness", "activity"}
    assert all(len(values) <= 8 for values in trends.values())


def test_public_artifact_contains_only_allowlisted_aggregate_fields(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.delenv("OURA_ACCESS_TOKEN", raising=False)
    output = tmp_path / "oura-trends" / "cache.json"

    oura.build_aggregate(
        output_path=output,
        fixture_path=FIXTURE_PATH,
        publication_allowed=True,
    )
    written = json.loads(output.read_text(encoding="utf-8"))
    assert set(written).issubset(OURA_PUBLIC_AGGREGATE_ALLOWLIST)


def test_publication_blocked_writes_no_primary_artifact(tmp_path) -> None:
    output = tmp_path / "oura-trends" / "cache.json"
    aggregate = oura.build_aggregate(
        output_path=output,
        fixture_path=FIXTURE_PATH,
        publication_allowed=False,
    )
    assert aggregate.data_source == "disabled"
    assert not output.exists()


def test_missing_token_uses_synthetic_fixture_and_hides_context(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.delenv("OURA_ACCESS_TOKEN", raising=False)
    output = tmp_path / "oura-trends" / "cache.json"

    aggregate = oura.build_aggregate(
        output_path=output,
        fixture_path=FIXTURE_PATH,
        publication_allowed=True,
    )
    context = oura.load_template_context(output)

    assert aggregate.is_synthetic is True
    assert context["is_public"] is False
    assert (output.parent / "card-light.svg").exists()
    assert (output.parent / "card-mobile-dark.svg").exists()


def test_real_cache_is_preferred_when_oauth_token_missing(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.delenv("OURA_ACCESS_TOKEN", raising=False)
    output = tmp_path / "oura-trends" / "cache.json"
    output.parent.mkdir(parents=True)
    output.write_text(
        json.dumps(_aggregate().model_dump(mode="json")),
        encoding="utf-8",
    )

    aggregate = oura.build_aggregate(
        output_path=output,
        fixture_path=FIXTURE_PATH,
        publication_allowed=True,
    )

    assert aggregate.data_source == "cache"
    assert aggregate.is_synthetic is False


def test_svg_contains_only_coarse_weekly_chart_context(tmp_path) -> None:
    aggregate = _aggregate()
    trends = {
        "sleep": [70, 75, 80, 80],
        "readiness": [65, 70, 75, 80],
        "activity": [80, 80, 85, 85],
    }
    oura.render_cards(aggregate, trends, tmp_path)
    svg = (tmp_path / "card-light.svg").read_text(encoding="utf-8")

    assert "OURA · AGGREGATE TRENDS" in svg
    assert "Weekly averages rounded to 5-point buckets" in svg
    assert "2026-08-01" not in svg
    assert "access_token" not in svg
    assert "timezone" not in svg


def test_registry_records_owner_approved_oura_publication() -> None:
    raw = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    modules = {module["name"]: module for module in raw["modules"]}
    entry = modules["oura-trends"]

    assert entry["enabled"] is True
    assert entry["publication"] == "allowed"
    assert entry["sensitivity"] == "sensitive"
    assert entry["secret_names"] == ["OURA_ACCESS_TOKEN"]
