"""Tests for the privacy-bounded Monkeytype profile module."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools.modules import monkeytype

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_URL = "https://monkeytype.com/profile/szmyty"


def test_fixture_is_synthetic_and_hidden() -> None:
    fixture = monkeytype.load_fixture()
    assert fixture["is_synthetic"] is True
    assert fixture["data_source"] == "fixture"

    context = monkeytype.load_template_context(monkeytype.DEFAULT_FIXTURE)
    assert context["is_public"] is False


def test_fetch_live_normalizes_only_bounded_fields(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, str] | None]] = []

    def fake_get(
        path: str,
        ape_key: str,
        *,
        params: dict[str, str] | None = None,
    ) -> dict:
        assert ape_key == "secret-value"
        calls.append((path, params))
        if path == "/users/stats":
            return {
                "data": {
                    "completedTests": 123,
                    "startedTests": 140,
                    "timeTyping": 9876,
                    "email": "must-not-leak@example.com",
                    "uid": "must-not-leak",
                }
            }
        assert params is not None
        duration = int(params["mode2"])
        return {
            "data": [
                {
                    "wpm": 80 + duration / 10,
                    "acc": 98.5,
                    "consistency": 82.0,
                    "timestamp": 123456789,
                    "raw": 999,
                }
            ]
        }

    monkeypatch.setattr(monkeytype, "_api_get", fake_get)
    snapshot = monkeytype.fetch_live("secret-value")

    assert snapshot["profile_url"] == PROFILE_URL
    assert snapshot["completed_tests"] == 123
    assert snapshot["started_tests"] == 140
    assert snapshot["time_typing_seconds"] == 9876
    assert [item["duration_seconds"] for item in snapshot["personal_bests"]] == [
        15,
        30,
        60,
        120,
    ]
    serialized = json.dumps(snapshot)
    for forbidden in ("email", "uid", "timestamp", "raw", "secret-value"):
        assert forbidden not in serialized
    assert calls[0] == ("/users/stats", None)
    assert len(calls) == 5


def test_build_snapshot_prefers_real_cache_when_key_is_missing(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("MONKEYTYPE_APE_KEY", raising=False)
    output = tmp_path / "monkeytype" / "cache.json"
    output.parent.mkdir(parents=True)
    cached = monkeytype.load_fixture().copy()
    cached.update({"data_source": "live", "is_synthetic": False})
    output.write_text(json.dumps(cached), encoding="utf-8")

    snapshot = monkeytype.build_snapshot(
        output_path=output,
        fixture_path=monkeytype.DEFAULT_FIXTURE,
        ape_key=None,
    )

    assert snapshot["data_source"] == "cache"
    assert snapshot["is_synthetic"] is False


def test_render_cards_are_accessible_and_privacy_bounded(tmp_path) -> None:
    snapshot = monkeytype.load_fixture()
    monkeytype.render_cards(snapshot, tmp_path)

    for filename in (
        "card-light.svg",
        "card-dark.svg",
        "card-mobile-light.svg",
        "card-mobile-dark.svg",
    ):
        svg = (tmp_path / filename).read_text(encoding="utf-8")
        assert "<title>Monkeytype typing statistics for szmyty</title>" in svg
        assert "Official Monkeytype API" in svg
        assert "15s" in svg
        assert "120s" in svg
        for forbidden in ("ApeKey", "email", "uid", "timestamp"):
            assert forbidden not in svg


def test_registry_readme_and_workflow_contract() -> None:
    registry = yaml.safe_load(
        (REPO_ROOT / "profile/content/modules-registry.yml").read_text(encoding="utf-8")
    )
    module = next(item for item in registry["modules"] if item["name"] == "monkeytype")
    assert module["enabled"] is True
    assert module["provider_type"] == "api"
    assert module["secret_names"] == ["MONKEYTYPE_APE_KEY"]

    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "https://monkeytype.com/profile/szmyty" in readme
    assert "<!-- START:monkeytype -->" in readme
    assert "<!-- END:monkeytype -->" in readme

    workflow = (REPO_ROOT / ".github/workflows/update-profile.yml").read_text(
        encoding="utf-8"
    )
    assert "MONKEYTYPE_APE_KEY: ${{ secrets.MONKEYTYPE_APE_KEY }}" in workflow
    assert "tools.modules.monkeytype" in workflow
