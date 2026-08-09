"""Tests for production GitHub workflow configuration."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).parents[1]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
EXPECTED_WORKFLOWS = {"ci.yml", "pages.yml", "update-profile.yml"}
SITE_REQUIRED_FILES = {
    "index.html",
    "manifest.webmanifest",
    "robots.txt",
    "sitemap.xml",
    "README.md",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _workflow_events(workflow: dict[str, Any]) -> dict[str, Any]:
    events = workflow.get("on")
    if events is None:
        events = workflow.get(True)
    assert isinstance(events, dict)
    return events


def _iter_steps(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for job in workflow.get("jobs", {}).values():
        steps.extend(job.get("steps", []))
    return steps


def test_only_expected_production_workflows_exist() -> None:
    workflow_files = {path.name for path in WORKFLOWS_DIR.glob("*.yml")}
    assert workflow_files == EXPECTED_WORKFLOWS


def test_dependabot_updates_pinned_actions() -> None:
    config = _load_yaml(REPO_ROOT / ".github" / "dependabot.yml")
    assert config["version"] == 2
    assert config["updates"] == [
        {
            "package-ecosystem": "github-actions",
            "directory": "/",
            "schedule": {"interval": "weekly"},
            "target-branch": "master",
        }
    ]


def test_ci_is_read_only_and_avoids_pull_request_target() -> None:
    workflow = _load_yaml(WORKFLOWS_DIR / "ci.yml")
    assert "pull_request_target" not in _workflow_events(workflow)
    assert workflow["permissions"] == {"contents": "read"}
    for job in workflow["jobs"].values():
        permissions = job.get("permissions", workflow["permissions"])
        assert all(level != "write" for level in permissions.values())


def test_checkout_is_read_only_outside_writer_job() -> None:
    for workflow_name in EXPECTED_WORKFLOWS:
        workflow = _load_yaml(WORKFLOWS_DIR / workflow_name)
        for job in workflow["jobs"].values():
            permissions = job.get("permissions", workflow.get("permissions", {}))
            is_writer = permissions.get("contents") == "write"
            for step in job.get("steps", []):
                uses = step.get("uses", "")
                if uses.startswith("actions/checkout@") and not is_writer:
                    assert step.get("with", {}).get("persist-credentials") is False


def test_external_actions_are_sha_pinned() -> None:
    pattern = re.compile(r"^[^@]+@[0-9a-f]{40}$")
    for workflow_name in EXPECTED_WORKFLOWS:
        workflow = _load_yaml(WORKFLOWS_DIR / workflow_name)
        for step in _iter_steps(workflow):
            uses = step.get("uses")
            if not uses or uses.startswith("./"):
                continue
            assert pattern.match(uses), f"{workflow_name}: unpinned action {uses}"


def test_update_profile_scopes_write_permission_and_concurrency() -> None:
    workflow = _load_yaml(WORKFLOWS_DIR / "update-profile.yml")
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] is False
    assert workflow["jobs"]["commit"]["permissions"] == {"contents": "write"}
    assert workflow["jobs"]["validate"]["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["refresh"]["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["report-partial-failure"]["permissions"] == {}


def test_pages_scopes_pages_permissions_to_deploy_job() -> None:
    workflow = _load_yaml(WORKFLOWS_DIR / "pages.yml")
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["validate"]["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["deploy"]["permissions"] == {
        "contents": "read",
        "pages": "write",
        "id-token": "write",
    }


def test_site_directory_contains_committed_pages_inputs() -> None:
    site_dir = REPO_ROOT / "site"
    committed_files = {path.name for path in site_dir.iterdir() if path.is_file()}
    assert committed_files >= SITE_REQUIRED_FILES
