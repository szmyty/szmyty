"""Tests for the development container configuration."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_workspace_recommendations(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    match = re.search(r'"recommendations"\s*:\s*\[(?P<items>.*?)\]', content, re.DOTALL)
    assert match is not None
    return re.findall(r'"([^"]+)"', match.group("items"))


def test_devcontainer_installs_required_tooling_and_extensions() -> None:
    devcontainer = _load_json(REPO_ROOT / ".devcontainer" / "devcontainer.json")
    extensions = _load_json(REPO_ROOT / ".vscode" / "extensions.json")

    recommendations = extensions["recommendations"]
    assert isinstance(recommendations, list)
    assert "esbenp.prettier-vscode" in recommendations
    assert "davidanson.vscode-markdownlint" in recommendations

    features = devcontainer["features"]
    assert isinstance(features, dict)
    assert features["ghcr.io/devcontainers/features/node:1"] == {"version": "lts"}

    post_create = devcontainer["postCreateCommand"]
    assert isinstance(post_create, str)
    assert "python -m pip install --user poetry==2.1.4" in post_create
    assert "~/.local/bin/poetry install --with lint,test" in post_create
    assert "npm install --global prettier markdownlint-cli" in post_create


def test_workspace_extension_recommendations_are_available_in_devcontainer() -> None:
    workspace_recommendations = _load_workspace_recommendations(
        REPO_ROOT / "szmyty.code-workspace"
    )
    extensions = _load_json(REPO_ROOT / ".vscode" / "extensions.json")

    assert isinstance(workspace_recommendations, list)
    assert isinstance(extensions["recommendations"], list)
    assert set(workspace_recommendations).issubset(set(extensions["recommendations"]))
