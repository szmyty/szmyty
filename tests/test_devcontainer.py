"""Tests for the development container configuration."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]


def _strip_jsonc_comments(content: str) -> str:
    result: list[str] = []
    in_string = False
    escaped = False
    index = 0

    while index < len(content):
        char = content[index]
        next_char = content[index + 1] if index + 1 < len(content) else ""

        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"' and not in_string:
            in_string = True
            result.append(char)
            index += 1
            continue

        if char == "/" and next_char == "/":
            index += 2
            while index < len(content) and content[index] != "\n":
                index += 1
            continue

        if char == "/" and next_char == "*":
            index += 2
            while index + 1 < len(content) and content[index : index + 2] != "*/":
                index += 1
            index += 2
            continue

        result.append(char)
        index += 1

    return "".join(result)


def _load_jsonc(path: Path) -> dict[str, object]:
    content = path.read_text(encoding="utf-8")
    uncommented = _strip_jsonc_comments(content)
    normalized = re.sub(r",(\s*[}\]])", r"\1", uncommented)
    return json.loads(normalized)


def test_devcontainer_installs_required_tooling_and_extensions() -> None:
    devcontainer = _load_jsonc(REPO_ROOT / ".devcontainer" / "devcontainer.json")
    extensions = _load_jsonc(REPO_ROOT / ".vscode" / "extensions.json")

    recommendations = extensions["recommendations"]
    assert isinstance(recommendations, list)
    assert "esbenp.prettier-vscode" in recommendations
    assert "davidanson.vscode-markdownlint" in recommendations

    features = devcontainer["features"]
    assert isinstance(features, dict)
    assert features["ghcr.io/devcontainers/features/node:1"] == {"version": "lts"}

    post_create = devcontainer["postCreateCommand"]
    assert isinstance(post_create, dict)
    python_tooling = post_create["install-python-tooling"]
    node_tooling = post_create["install-node-tooling"]
    assert isinstance(python_tooling, str)
    assert isinstance(node_tooling, str)
    assert "python -m venv" in python_tooling
    assert "$HOME/.local/share/poetry/bin/pip" in python_tooling
    assert "$HOME/.local/share/poetry/bin/poetry" in python_tooling
    assert "install --with lint,test" in python_tooling
    assert "npm install --global" in node_tooling
    assert "prettier" in node_tooling
    assert "markdownlint-cli" in node_tooling


def test_workspace_extension_recommendations_are_available_in_devcontainer() -> None:
    workspace = _load_jsonc(REPO_ROOT / "szmyty.code-workspace")
    workspace_recommendations = workspace["extensions"]["recommendations"]
    extensions = _load_jsonc(REPO_ROOT / ".vscode" / "extensions.json")

    assert isinstance(workspace_recommendations, list)
    assert isinstance(extensions["recommendations"], list)
    assert set(workspace_recommendations).issubset(set(extensions["recommendations"]))
