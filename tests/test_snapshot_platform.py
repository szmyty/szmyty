"""Tests for the snapshot-module platform additions to tools/profile_builder/."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from tools.profile_builder import cache as cache_utils
from tools.profile_builder.models import (
    FreshnessPolicy,
    ModuleRegistry,
    ModuleRegistryEntry,
    ModuleResult,
    ResultState,
)

# ---------------------------------------------------------------------------
# ResultState
# ---------------------------------------------------------------------------


def test_result_state_values() -> None:
    assert ResultState.FRESH == "fresh"
    assert ResultState.CACHED == "cached"
    assert ResultState.STATIC == "static"
    assert ResultState.DISABLED == "disabled"
    assert ResultState.FAILED_WITH_FALLBACK == "failed-with-fallback"


# ---------------------------------------------------------------------------
# FreshnessPolicy
# ---------------------------------------------------------------------------


def test_freshness_policy_daily() -> None:
    policy = FreshnessPolicy(
        cadence="daily", ttl_seconds=86400, warn_after_seconds=172800
    )
    assert policy.cadence == "daily"
    assert policy.ttl_seconds == 86400


def test_freshness_policy_never() -> None:
    policy = FreshnessPolicy(cadence="never", ttl_seconds=None, warn_after_seconds=None)
    assert policy.ttl_seconds is None


def test_freshness_policy_invalid_cadence() -> None:
    with pytest.raises(ValidationError):
        FreshnessPolicy(cadence="fortnightly")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# ModuleRegistryEntry
# ---------------------------------------------------------------------------

_ENTRY_DEFAULTS = dict(
    name="test-module",
    provider_type="api",
    provider_module="tools.modules.test_module",
    sensitivity="public",
    freshness_policy={"cadence": "daily", "ttl_seconds": 86400},
    artifact_dir="profile/artifacts/test-module",
    artifact_file="cache.json",
    region_start_marker="<!-- START:test-module -->",
    region_end_marker="<!-- END:test-module -->",
    template="test-module.md.j2",
)


def test_registry_entry_valid() -> None:
    entry = ModuleRegistryEntry.model_validate(_ENTRY_DEFAULTS)
    assert entry.name == "test-module"
    assert entry.sensitivity == "public"
    assert entry.freshness_policy.cadence == "daily"
    assert entry.secret_names == []
    assert entry.enabled is True


def test_registry_entry_strips_markers() -> None:
    d = {**_ENTRY_DEFAULTS, "region_start_marker": "  <!-- START:test-module -->  "}
    entry = ModuleRegistryEntry.model_validate(d)
    assert entry.region_start_marker == "<!-- START:test-module -->"


def test_registry_entry_invalid_sensitivity() -> None:
    d = {**_ENTRY_DEFAULTS, "sensitivity": "classified"}
    with pytest.raises(ValidationError):
        ModuleRegistryEntry.model_validate(d)


def test_registry_entry_invalid_provider_type() -> None:
    d = {**_ENTRY_DEFAULTS, "provider_type": "webhook"}
    with pytest.raises(ValidationError):
        ModuleRegistryEntry.model_validate(d)


# ---------------------------------------------------------------------------
# ModuleRegistry
# ---------------------------------------------------------------------------


def test_module_registry_enabled_filter() -> None:
    reg = ModuleRegistry.model_validate(
        {
            "modules": [
                {**_ENTRY_DEFAULTS, "name": "mod-a", "enabled": True},
                {
                    **_ENTRY_DEFAULTS,
                    "name": "mod-b",
                    "enabled": False,
                    "region_start_marker": "<!-- START:mod-b -->",
                    "region_end_marker": "<!-- END:mod-b -->",
                },
            ]
        }
    )
    assert len(reg.modules) == 2
    assert len(reg.enabled_modules) == 1
    assert reg.enabled_modules[0].name == "mod-a"


def test_module_registry_duplicate_name_rejected() -> None:
    with pytest.raises(ValidationError):
        ModuleRegistry.model_validate(
            {
                "modules": [
                    _ENTRY_DEFAULTS,
                    _ENTRY_DEFAULTS,
                ]
            }
        )


# ---------------------------------------------------------------------------
# ModuleResult
# ---------------------------------------------------------------------------


def test_module_result_fresh() -> None:
    result = ModuleResult(
        module_name="github-metrics",
        state=ResultState.FRESH,
        human_summary="Fresh from GitHub API (0 min ago)",
        data_source="live",
        result_at="2026-08-09T18:06:21+00:00",
        data_at="2026-08-09T18:06:21+00:00",
        data_hash="abc123",
        ttl_seconds=86400,
        is_stale=False,
        seconds_until_stale=86400,
    )
    assert result.state == ResultState.FRESH
    assert result.error is None


def test_module_result_failed_with_fallback() -> None:
    result = ModuleResult(
        module_name="recent-activity",
        state=ResultState.FAILED_WITH_FALLBACK,
        human_summary="Provider failed; using cached data.",
        data_source="cache",
        result_at="2026-08-09T18:06:21+00:00",
        error="HTTP 503",
    )
    assert result.state == ResultState.FAILED_WITH_FALLBACK
    assert result.error == "HTTP 503"


# ---------------------------------------------------------------------------
# modules-registry.yml loading
# ---------------------------------------------------------------------------

_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1] / "profile" / "content" / "modules-registry.yml"
)


def test_modules_registry_yml_loads() -> None:
    assert _REGISTRY_PATH.exists(), f"Missing {_REGISTRY_PATH}"
    raw = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))
    reg = ModuleRegistry.model_validate(raw)
    names = {m.name for m in reg.modules}
    # Original modules must be present; new modules are additive.
    assert {"github-dashboard", "ai-agent-showcase", "music-highlight"}.issubset(names)
    assert len(reg.modules) >= 3


def test_modules_registry_yml_music_highlight_is_manual() -> None:
    raw = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))
    reg = ModuleRegistry.model_validate(raw)
    music = next(m for m in reg.modules if m.name == "music-highlight")
    assert music.provider_type == "manual"
    assert music.freshness_policy.cadence == "never"
    assert music.freshness_policy.ttl_seconds is None


def test_modules_registry_yml_api_modules_have_token() -> None:
    raw = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))
    reg = ModuleRegistry.model_validate(raw)
    # GitHub API modules require GITHUB_TOKEN; public unauthenticated APIs do not.
    # Any new `api`-type module that does NOT use the GitHub API must be listed
    # in one of the exemption sets below.
    _UNAUTHENTICATED_API_MODULES = {"orcid", "medium"}
    # Third-party API modules authenticate with provider-specific secrets (not
    # GITHUB_TOKEN).  They must declare at least one secret_name of their own.
    _THIRD_PARTY_API_MODULES = {"soundcloud", "steam", "oura-trends"}
    for mod in reg.modules:
        if mod.provider_type != "api":
            continue
        if mod.name in _UNAUTHENTICATED_API_MODULES:
            # Public APIs — assert no GitHub secret is required.
            assert "GITHUB_TOKEN" not in mod.secret_names, (
                f"Module {mod.name!r} is listed as unauthenticated "
                f"but declares GITHUB_TOKEN"
            )
        elif mod.name in _THIRD_PARTY_API_MODULES:
            # Third-party provider APIs — must not use GITHUB_TOKEN and must
            # declare at least one provider-specific secret.
            assert "GITHUB_TOKEN" not in mod.secret_names, (
                f"Module {mod.name!r} is a third-party API module "
                f"but declares GITHUB_TOKEN"
            )
            assert len(mod.secret_names) > 0, (
                f"Module {mod.name!r} is a third-party API module "
                f"but declares no secret_names"
            )
        else:
            # All other API modules must declare GITHUB_TOKEN.
            assert "GITHUB_TOKEN" in mod.secret_names, (
                f"Module {mod.name!r} is type 'api' but declares no GITHUB_TOKEN secret"
            )


# ---------------------------------------------------------------------------
# cache.write_metadata
# ---------------------------------------------------------------------------


def test_write_metadata_creates_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(cache_utils, "CACHE_ROOT", tmp_path)
    cache_utils.write_metadata(
        module_name="test-module",
        state="fresh",
        data_source="live",
        human_summary="Fresh from API",
        ttl_seconds=86400,
        data_at="2026-08-09T18:00:00+00:00",
        data_hash="abc123",
        is_stale=False,
        seconds_until_stale=82000,
    )
    metadata_path = tmp_path / "test-module" / "metadata.json"
    assert metadata_path.exists()
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert meta["module_name"] == "test-module"
    assert meta["state"] == "fresh"
    assert meta["data_source"] == "live"
    assert meta["ttl_seconds"] == 86400
    assert meta["is_stale"] is False
    assert meta["error"] is None
    assert "generated_at" in meta


def test_write_metadata_error_field(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(cache_utils, "CACHE_ROOT", tmp_path)
    cache_utils.write_metadata(
        module_name="bad-module",
        state="failed-with-fallback",
        data_source="cache",
        human_summary="Provider failed; using cached data.",
        error="HTTP 503 Service Unavailable",
    )
    meta = json.loads(
        (tmp_path / "bad-module" / "metadata.json").read_text(encoding="utf-8")
    )
    assert meta["state"] == "failed-with-fallback"
    assert meta["error"] == "HTTP 503 Service Unavailable"
