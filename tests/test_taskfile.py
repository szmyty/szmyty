"""Taskfile task definitions for local workflow parity."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parents[1]
TASKFILE_PATH = REPO_ROOT / "Taskfile.yml"


def _taskfile_tasks() -> dict[str, dict[str, object]]:
    content = yaml.safe_load(TASKFILE_PATH.read_text(encoding="utf-8"))
    return content["tasks"]


def test_required_local_dx_tasks_exist() -> None:
    tasks = _taskfile_tasks()

    assert "lint" in tasks
    assert "fmt" in tasks
    assert "health" in tasks
    assert "repo:audit" in tasks


def test_required_local_dx_task_commands_match_issue_contract() -> None:
    tasks = _taskfile_tasks()

    assert tasks["lint"]["cmds"] == [
        "npx prettier --check .",
        "npx markdownlint .",
    ]
    assert tasks["fmt"]["cmds"] == ["npx prettier --write ."]
    assert tasks["repo:audit"]["cmds"] == ['echo "Audit task placeholder"']

    health_cmds = tasks["health"]["cmds"]
    assert any("test -f README.md" in cmd for cmd in health_cmds)
    assert any("test -d .github/workflows" in cmd for cmd in health_cmds)
    assert any("test -f .editorconfig" in cmd for cmd in health_cmds)
    assert any("test -d docs" in cmd for cmd in health_cmds)
    assert health_cmds[-1] == 'echo "Repository health check passed"'
