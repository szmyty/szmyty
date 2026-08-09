"""Tests for the oura-trends privacy-preserving aggregate module.

Required coverage (per issue #113):
- allowlist rejects unknown/new provider fields;
- exact timestamps, raw samples, daily arrays, tags, locations, workouts,
  and authentication values cannot enter public output;
- recent safety buffer and minimum sample window are enforced;
- small sample sets are suppressed;
- synthetic fixtures cannot be mistaken for actual data;
- expired/missing token produces a safe disabled/cached state;
- identical aggregates render deterministically.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from tools.modules import oura_trends as oura_mod
from tools.modules.oura_trends import (
    MIN_SAMPLE_DAYS,
    SAFETY_BUFFER_DAYS,
    _apply_allowlist,
    _hrv_direction,
    _period_label,
    _window_dates,
    aggregate_window,
    build_aggregate,
    load_fixture,
)
from tools.profile_builder.models import (
    OURA_PUBLIC_AGGREGATE_ALLOWLIST,
    OuraTrendsAggregate,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1] / "profile" / "fixtures" / "oura-trends.json"
)
REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "profile"
    / "content"
    / "modules-registry.yml"
)


def _make_agg(**overrides) -> OuraTrendsAggregate:
    base = dict(
        window_days=30,
        contributing_days=25,
        period_label="Jul 2026",
        avg_sleep_hours=7.0,
        sleep_regularity_band="average",
        avg_readiness_band="average",
        activity_consistency_band="moderate",
        hrv_direction="stable",
        is_synthetic=True,
        data_source="fixture",
        generated_month="2026-08",
    )
    base.update(overrides)
    return OuraTrendsAggregate.model_validate(base)


# ---------------------------------------------------------------------------
# Allowlist: OuraTrendsAggregate model rejects unknown fields
# ---------------------------------------------------------------------------


def test_allowlist_rejects_unknown_field() -> None:
    """Extra provider fields must be rejected at validation time."""
    with pytest.raises(ValidationError):
        OuraTrendsAggregate.model_validate(
            dict(
                window_days=30,
                contributing_days=25,
                period_label="Jul 2026",
                is_synthetic=True,
                data_source="fixture",
                generated_month="2026-08",
                _unknown_provider_field="should_fail",  # not in allowlist
            )
        )


def test_allowlist_rejects_daily_array_field() -> None:
    """A raw daily-samples field must not pass validation."""
    with pytest.raises(ValidationError):
        OuraTrendsAggregate.model_validate(
            dict(
                window_days=30,
                contributing_days=25,
                period_label="Jul 2026",
                is_synthetic=True,
                data_source="fixture",
                generated_month="2026-08",
                daily_sleep_records=[{"date": "2026-07-01", "duration_seconds": 25200}],
            )
        )


def test_allowlist_rejects_tag_field() -> None:
    with pytest.raises(ValidationError):
        OuraTrendsAggregate.model_validate(
            dict(
                window_days=30,
                contributing_days=25,
                period_label="Jul 2026",
                is_synthetic=True,
                data_source="fixture",
                generated_month="2026-08",
                tags=["menstrual_cycle", "alcohol"],
            )
        )


def test_allowlist_rejects_location_field() -> None:
    with pytest.raises(ValidationError):
        OuraTrendsAggregate.model_validate(
            dict(
                window_days=30,
                contributing_days=25,
                period_label="Jul 2026",
                is_synthetic=True,
                data_source="fixture",
                generated_month="2026-08",
                timezone="America/New_York",
            )
        )


def test_allowlist_rejects_workout_field() -> None:
    with pytest.raises(ValidationError):
        OuraTrendsAggregate.model_validate(
            dict(
                window_days=30,
                contributing_days=25,
                period_label="Jul 2026",
                is_synthetic=True,
                data_source="fixture",
                generated_month="2026-08",
                workout_records=[{"start_time": "2026-07-01T06:30:00"}],
            )
        )


def test_allowlist_rejects_auth_field() -> None:
    with pytest.raises(ValidationError):
        OuraTrendsAggregate.model_validate(
            dict(
                window_days=30,
                contributing_days=25,
                period_label="Jul 2026",
                is_synthetic=True,
                data_source="fixture",
                generated_month="2026-08",
                access_token="oura_deadbeef",
            )
        )


# ---------------------------------------------------------------------------
# Explicit allowlist function: _apply_allowlist
# ---------------------------------------------------------------------------


def test_apply_allowlist_strips_unknown_keys() -> None:
    raw = {
        "window_days": 90,
        "contributing_days": 80,
        "period_label": "Jul 2026",
        "avg_sleep_hours": 7.0,
        "daily_array": [1, 2, 3],          # must be stripped
        "access_token": "oura_secret",     # must be stripped
        "tags": ["alcohol"],               # must be stripped
        "is_synthetic": True,
        "data_source": "fixture",
        "generated_month": "2026-08",
    }
    filtered = _apply_allowlist(raw)
    assert "daily_array" not in filtered
    assert "access_token" not in filtered
    assert "tags" not in filtered
    assert "window_days" in filtered
    assert "avg_sleep_hours" in filtered


def test_apply_allowlist_passes_only_allowlist_keys() -> None:
    raw = {"every": "possible", "new_provider_field": "surprise", "window_days": 30}
    filtered = _apply_allowlist(raw)
    for key in filtered:
        assert key in OURA_PUBLIC_AGGREGATE_ALLOWLIST


# ---------------------------------------------------------------------------
# Band validators — invalid band labels are rejected
# ---------------------------------------------------------------------------


def test_invalid_sleep_band_rejected() -> None:
    with pytest.raises(ValidationError):
        _make_agg(sleep_regularity_band="great")


def test_invalid_readiness_band_rejected() -> None:
    with pytest.raises(ValidationError):
        _make_agg(avg_readiness_band="poor")


def test_invalid_activity_band_rejected() -> None:
    with pytest.raises(ValidationError):
        _make_agg(activity_consistency_band="very-high")


def test_invalid_hrv_direction_rejected() -> None:
    with pytest.raises(ValidationError):
        _make_agg(hrv_direction="increasing")


# ---------------------------------------------------------------------------
# Sleep rounding — prevents precise inference
# ---------------------------------------------------------------------------


def test_sleep_rounded_to_half_hour() -> None:
    agg = _make_agg(avg_sleep_hours=7.3)
    assert agg.avg_sleep_hours == 7.5


def test_sleep_rounded_to_half_hour_down() -> None:
    agg = _make_agg(avg_sleep_hours=6.7)
    assert agg.avg_sleep_hours == 6.5


def test_sleep_exact_half_unchanged() -> None:
    agg = _make_agg(avg_sleep_hours=7.5)
    assert agg.avg_sleep_hours == 7.5


# ---------------------------------------------------------------------------
# Safety buffer: _window_dates excludes recent days
# ---------------------------------------------------------------------------


def test_window_dates_excludes_today(monkeypatch) -> None:
    """End date must be at least SAFETY_BUFFER_DAYS before today."""
    fixed_today = date(2026, 8, 9)

    class _FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 8, 9, 12, 0, 0, tzinfo=UTC)

    monkeypatch.setattr(oura_mod, "datetime", _FixedDatetime)
    start, end = _window_dates(30)
    expected_end = fixed_today - timedelta(days=SAFETY_BUFFER_DAYS)
    assert end == expected_end
    assert (end - start).days == 29  # 30-day window: start..end inclusive


def test_window_dates_start_before_end(monkeypatch) -> None:
    class _FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 8, 9, 12, 0, 0, tzinfo=UTC)

    monkeypatch.setattr(oura_mod, "datetime", _FixedDatetime)
    start, end = _window_dates(90)
    assert start < end


# ---------------------------------------------------------------------------
# Minimum sample window enforcement
# ---------------------------------------------------------------------------


def test_aggregate_suppresses_metrics_when_below_min_sample() -> None:
    """All metrics should be None when contributing_days < MIN_SAMPLE_DAYS."""
    few_days = MIN_SAMPLE_DAYS - 1
    agg = aggregate_window(
        daily_sleep_seconds=[25200.0] * few_days,
        readiness_scores=[75.0] * few_days,
        activity_scores=[80.0] * few_days,
        hrv_rmssd_values=[50.0] * few_days,
        window_days=30,
        end_date=date(2026, 8, 7),
    )
    assert agg.avg_sleep_hours is None
    assert agg.sleep_regularity_band is None
    assert agg.avg_readiness_band is None
    assert agg.activity_consistency_band is None
    assert agg.hrv_direction is None


def test_aggregate_emits_metrics_when_above_min_sample() -> None:
    """Metrics should be present when contributing_days >= MIN_SAMPLE_DAYS."""
    enough = MIN_SAMPLE_DAYS
    agg = aggregate_window(
        daily_sleep_seconds=[25200.0] * enough,
        readiness_scores=[75.0] * enough,
        activity_scores=[80.0] * enough,
        hrv_rmssd_values=[50.0] * enough,
        window_days=30,
        end_date=date(2026, 8, 7),
    )
    assert agg.avg_sleep_hours is not None
    assert agg.avg_readiness_band is not None


# ---------------------------------------------------------------------------
# Period label coarseness — no exact dates
# ---------------------------------------------------------------------------


def test_long_window_period_label_is_month_year() -> None:
    label = _period_label(90, date(2026, 8, 7))
    # Must contain a month abbreviation and year but not an exact day
    assert "2026" in label
    assert "-07-" not in label and "-08-07" not in label


def test_short_window_period_label_is_week_ending() -> None:
    label = _period_label(30, date(2026, 8, 7))
    assert "week ending" in label
    # The exact day of the end_date should not appear verbatim
    assert "2026-08-07" not in label


# ---------------------------------------------------------------------------
# Synthetic fixture
# ---------------------------------------------------------------------------


def test_fixture_file_exists() -> None:
    assert FIXTURE_PATH.exists(), f"Fixture missing: {FIXTURE_PATH}"


def test_fixture_is_valid_aggregate() -> None:
    agg = load_fixture(FIXTURE_PATH)
    assert isinstance(agg, OuraTrendsAggregate)


def test_fixture_is_marked_synthetic() -> None:
    """Synthetic fixtures must be flagged so they cannot be mistaken for real data."""
    agg = load_fixture(FIXTURE_PATH)
    assert agg.is_synthetic is True, "Fixture must have is_synthetic=True"


def test_fixture_data_source_is_fixture() -> None:
    agg = load_fixture(FIXTURE_PATH)
    assert agg.data_source == "fixture"


def test_fixture_contributing_days_within_window() -> None:
    agg = load_fixture(FIXTURE_PATH)
    assert agg.contributing_days <= agg.window_days


# ---------------------------------------------------------------------------
# Missing/expired token → safe disabled/cached state
# ---------------------------------------------------------------------------


def test_build_aggregate_disabled_when_publication_blocked(tmp_path) -> None:
    """With publication_allowed=False the module must return a disabled state."""
    agg = build_aggregate(
        output_path=tmp_path / "cache.json",
        fixture_path=FIXTURE_PATH,
        publication_allowed=False,
    )
    assert agg.data_source == "disabled"
    # Must not write a public artifact when publication is blocked
    assert not (tmp_path / "cache.json").exists()


def test_build_aggregate_falls_back_to_fixture_when_no_token(
    tmp_path, monkeypatch
) -> None:
    """Missing OURA_ACCESS_TOKEN must fall back gracefully — no crash."""
    monkeypatch.delenv("OURA_ACCESS_TOKEN", raising=False)
    agg = build_aggregate(
        output_path=tmp_path / "cache.json",
        fixture_path=FIXTURE_PATH,
        publication_allowed=True,
    )
    # Should use fixture as last resort
    assert agg.data_source in ("fixture", "cache", "live")
    # Artifact must be written (publication is allowed)
    assert (tmp_path / "cache.json").exists()


def test_build_aggregate_falls_back_to_cache_when_no_token(
    tmp_path, monkeypatch
) -> None:
    """When cached artifact exists, it should be preferred over the fixture."""
    monkeypatch.delenv("OURA_ACCESS_TOKEN", raising=False)
    # Pre-seed a cached artifact
    cache_path = tmp_path / "cache.json"
    cached_agg = _make_agg(
        window_days=90,
        contributing_days=70,
        data_source="live",
        is_synthetic=True,
        generated_month="2026-07",
    )
    cache_path.write_text(
        json.dumps(cached_agg.model_dump(mode="json"), indent=2), encoding="utf-8"
    )
    agg = build_aggregate(
        output_path=cache_path,
        fixture_path=FIXTURE_PATH,
        publication_allowed=True,
    )
    assert agg.data_source == "cache"


# ---------------------------------------------------------------------------
# Deterministic rendering
# ---------------------------------------------------------------------------


def test_identical_aggregates_render_deterministically() -> None:
    agg1 = _make_agg()
    agg2 = _make_agg()
    assert agg1.model_dump(mode="json") == agg2.model_dump(mode="json")


def test_aggregate_json_contains_no_token_or_timestamp() -> None:
    agg = _make_agg()
    dumped = json.dumps(agg.model_dump(mode="json"))
    assert "access_token" not in dumped
    assert "Bearer" not in dumped
    # generated_month is coarse (YYYY-MM), not an exact ISO timestamp
    assert "T" not in agg.generated_month


# ---------------------------------------------------------------------------
# Public artifact contains only allowlisted keys
# ---------------------------------------------------------------------------


def test_public_artifact_contains_only_allowlisted_keys(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.delenv("OURA_ACCESS_TOKEN", raising=False)
    output = tmp_path / "cache.json"
    build_aggregate(
        output_path=output,
        fixture_path=FIXTURE_PATH,
        publication_allowed=True,
    )
    written = json.loads(output.read_text(encoding="utf-8"))
    for key in written:
        assert key in OURA_PUBLIC_AGGREGATE_ALLOWLIST, (
            f"Public artifact contains non-allowlisted key: {key!r}"
        )


# ---------------------------------------------------------------------------
# Registry entry: oura-trends is disabled by default
# ---------------------------------------------------------------------------


def test_registry_oura_trends_disabled_by_default() -> None:
    raw = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = {m["name"]: m for m in raw["modules"]}
    assert "oura-trends" in entries, "oura-trends must be in modules-registry.yml"
    entry = entries["oura-trends"]
    assert entry.get("enabled", True) is False, (
        "oura-trends must be disabled by default"
    )
    assert entry.get("publication") == "blocked-pending-owner-approval"


def test_registry_oura_trends_sensitivity_is_sensitive() -> None:
    raw = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = {m["name"]: m for m in raw["modules"]}
    assert entries["oura-trends"]["sensitivity"] == "sensitive"


def test_registry_oura_trends_declares_secret() -> None:
    raw = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = {m["name"]: m for m in raw["modules"]}
    assert "OURA_ACCESS_TOKEN" in entries["oura-trends"]["secret_names"]


# ---------------------------------------------------------------------------
# HRV direction logic
# ---------------------------------------------------------------------------


def test_hrv_direction_stable_with_small_values() -> None:
    values = [50.0] * 20
    assert _hrv_direction(values) == "stable"


def test_hrv_direction_trending_up() -> None:
    values = [45.0] * 10 + [55.0] * 10
    assert _hrv_direction(values) == "trending-up"


def test_hrv_direction_trending_down() -> None:
    values = [55.0] * 10 + [45.0] * 10
    assert _hrv_direction(values) == "trending-down"


def test_hrv_direction_stable_with_few_samples() -> None:
    # Fewer than 4 values must return 'stable' without crashing
    assert _hrv_direction([50.0, 48.0]) == "stable"
