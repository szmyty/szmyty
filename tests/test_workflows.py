"""Tests for production GitHub workflow configuration."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from tools.profile_builder.models import ModuleRegistry, ProfileConfig

REPO_ROOT = Path(__file__).parents[1]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
EXPECTED_WORKFLOWS = {
    "ci.yml",
    "pages.yml",
    "update-profile.yml",
}
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


def test_update_profile_uses_safe_refresh_events() -> None:
    workflow = _load_yaml(WORKFLOWS_DIR / "update-profile.yml")
    events = _workflow_events(workflow)
    assert "pull_request_target" not in events
    assert "workflow_dispatch" in events
    assert "issues" in events
    assert events["issues"]["types"] == ["closed", "edited", "labeled", "reopened"]
    assert events["push"]["branches"] == ["master"]
    assert "profile/fixtures/github-dashboard.json" in events["push"]["paths"]
    assert "tools/profile_builder/github_dashboard/**" in events["push"]["paths"]


def test_update_profile_summary_uses_poetry_environment() -> None:
    workflow = _load_yaml(WORKFLOWS_DIR / "update-profile.yml")
    summarize = next(
        step
        for step in workflow["jobs"]["refresh"]["steps"]
        if step.get("name") == "Summarize module refresh"
    )
    assert "poetry run python - <<'PY'" in summarize["run"]


def test_update_profile_commit_retries_non_fast_forward_pushes() -> None:
    workflow = _load_yaml(WORKFLOWS_DIR / "update-profile.yml")
    commit_step = next(
        step
        for step in workflow["jobs"]["commit"]["steps"]
        if step.get("name") == "Commit semantic changes"
    )
    assert "for attempt in 1 2 3" in commit_step["run"]
    assert "git fetch origin master" in commit_step["run"]
    assert "git rebase origin/master" in commit_step["run"]


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


# ---------------------------------------------------------------------------
# README region marker convention
# ---------------------------------------------------------------------------

_START_PATTERN = re.compile(r"<!-- START:(\S+?) -->")
_END_PATTERN = re.compile(r"<!-- END:(\S+?) -->")
_LEGACY_PATTERN = re.compile(r"<!-- GENERATED:[A-Z]+:(START|END) -->")


def test_readme_uses_only_documented_start_end_markers() -> None:
    """README must not contain any GENERATED:* legacy markers."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    legacy = _LEGACY_PATTERN.findall(readme)
    assert legacy == [], f"Found legacy GENERATED:* markers: {legacy}"


def test_readme_start_end_markers_are_unique() -> None:
    """Each START and END marker must appear exactly once."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    start_names = _START_PATTERN.findall(readme)
    end_names = _END_PATTERN.findall(readme)
    assert len(start_names) == len(set(start_names)), (
        f"Duplicate START markers: {start_names}"
    )
    assert len(end_names) == len(set(end_names)), f"Duplicate END markers: {end_names}"


def test_readme_start_and_end_markers_match() -> None:
    """Every START marker must have a corresponding END marker with the same name."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    start_names = set(_START_PATTERN.findall(readme))
    end_names = set(_END_PATTERN.findall(readme))
    assert start_names == end_names, (
        f"Mismatched markers — START only: {start_names - end_names}, "
        f"END only: {end_names - start_names}"
    )


def test_readme_markers_match_modules_registry() -> None:
    """README markers must correspond exactly to registry-declared modules."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    registry_data = yaml.safe_load(
        (REPO_ROOT / "profile" / "content" / "modules-registry.yml").read_text(
            encoding="utf-8"
        )
    )
    registry = ModuleRegistry.model_validate(registry_data)
    declared_names = {m.name for m in registry.modules}
    readme_start_names = set(_START_PATTERN.findall(readme))
    assert readme_start_names == declared_names, (
        f"README markers do not match modules-registry.yml — "
        f"README only: {readme_start_names - declared_names}, "
        f"modules-registry.yml only: {declared_names - readme_start_names}"
    )


def test_modules_yml_stays_in_sync_with_registry_render_subset() -> None:
    """The legacy mirror must not drift from the canonical registry."""
    modules_data = yaml.safe_load(
        (REPO_ROOT / "profile" / "content" / "modules.yml").read_text(encoding="utf-8")
    )
    registry_data = yaml.safe_load(
        (REPO_ROOT / "profile" / "content" / "modules-registry.yml").read_text(
            encoding="utf-8"
        )
    )
    modules_cfg = ProfileConfig.model_validate(modules_data)
    registry = ModuleRegistry.model_validate(registry_data)
    registry_subset = {
        mod.name: (
            mod.enabled,
            mod.region_start_marker,
            mod.region_end_marker,
            mod.template,
            f"{mod.artifact_dir}/{mod.artifact_file}",
        )
        for mod in registry.modules
    }
    modules_subset = {
        mod.name: (
            mod.enabled,
            mod.region_start_marker,
            mod.region_end_marker,
            mod.template,
            None if mod.artifact_path is None else str(mod.artifact_path),
        )
        for mod in modules_cfg.modules
    }
    assert modules_subset == registry_subset


# ---------------------------------------------------------------------------
# Issue template contact links
# ---------------------------------------------------------------------------

# Slug names for existing Discussions categories (all lowercase, as used in URLs).
# If a category is added or renamed in the GitHub UI, update this set AND the
# owner checklist in docs/RUNBOOK.md § 10 (GitHub Surface Owner Checklist).
_KNOWN_VALID_DISCUSSIONS_CATEGORIES = {"ideas", "q-a"}
_KNOWN_VALID_URLS = {
    "https://github.com/szmyty/szmyty/discussions",
    "https://github.com/szmyty/szmyty/security/advisories/new",
}


def test_issue_config_contact_links_are_well_formed() -> None:
    """All contact_links must have non-empty name, url, and about fields."""
    config = _load_yaml(REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml")
    for link in config.get("contact_links", []):
        assert link.get("name"), f"Missing name in contact link: {link}"
        assert link.get("url", "").startswith("https://"), (
            f"Invalid or missing url in contact link: {link}"
        )
        assert link.get("about"), f"Missing about in contact link: {link}"


def test_issue_config_discussions_links_use_known_categories() -> None:
    """Discussion category links must point to known-existing categories."""
    config = _load_yaml(REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml")
    for link in config.get("contact_links", []):
        url: str = link.get("url", "")
        if "discussions/categories/" not in url:
            continue
        category = url.rsplit("/", 1)[-1]
        assert category in _KNOWN_VALID_DISCUSSIONS_CATEGORIES, (
            f"Contact link points to unknown Discussions category '{category}': {url}"
        )
