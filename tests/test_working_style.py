"""Tests for the owner-approved 16Personalities working-style surface."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools.modules import working_style

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = REPO_ROOT / "profile" / "artifacts" / "working-style" / "working-style.json"
README = REPO_ROOT / "README.md"
REGISTRY = REPO_ROOT / "profile" / "content" / "modules-registry.yml"
PROFILE_URL = "https://www.16personalities.com/profiles/366f5f0cddbe1"


def test_working_style_snapshot_is_bounded_and_public() -> None:
    snapshot = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert snapshot["personality_name"] == "Architect"
    assert snapshot["personality_type"] == "INTJ-T"
    assert snapshot["profile_url"] == PROFILE_URL
    assert snapshot["is_public"] is True
    assert len(snapshot["traits"]) == 5

    for trait in snapshot["traits"]:
        assert 0 <= trait["left_percent"] <= 100
        assert 0 <= trait["right_percent"] <= 100
        assert trait["left_percent"] + trait["right_percent"] == 100


def test_working_style_provider_publishes_complete_snapshot() -> None:
    context = working_style.load_template_context(ARTIFACT)
    assert context["is_public"] is True
    assert context["snapshot"]["personality_type"] == "INTJ-T"


def test_working_style_cards_are_accessible_and_bounded() -> None:
    artifact_dir = ARTIFACT.parent
    for filename in (
        "card-light.svg",
        "card-dark.svg",
        "card-mobile-light.svg",
        "card-mobile-dark.svg",
    ):
        svg = (artifact_dir / filename).read_text(encoding="utf-8")
        assert "<title>16Personalities assessment: Architect (INTJ-T)</title>" in svg
        assert "not an ability score" in svg
        assert "<foreignObject" not in svg
        assert "Introverted 76%" in svg
        assert "Intuitive 88%" in svg


def test_readme_links_badge_and_section_to_public_profile() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "16Personalities-Architect_(INTJ--T)-88619A" in readme
    assert readme.count(PROFILE_URL) >= 3
    assert readme.index("<!-- START:working-style -->") < readme.index("## How I work")
    assert readme.count("<!-- START:working-style -->") == 1
    assert readme.count("<!-- END:working-style -->") == 1


def test_working_style_registry_is_enabled_with_responsive_assets() -> None:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    module = next(item for item in registry["modules"] if item["name"] == "working-style")

    assert module["enabled"] is True
    assert module["provider_type"] == "manual"
    assert module["secret_names"] == []
    assert module["asset_files"] == [
        "card-light.svg",
        "card-dark.svg",
        "card-mobile-light.svg",
        "card-mobile-dark.svg",
    ]
