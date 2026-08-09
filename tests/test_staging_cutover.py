"""Tests for the final staging cutover."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
EXPECTED_LEDGER_ROW_COUNT = 95
ACTIVE_FILES = (
    "README.md",
    "AGENTS.md",
    "Taskfile.yml",
    "szmyty.code-workspace",
    ".tasks/check-identity.sh",
    ".github/workflows/ci.yml",
    ".github/workflows/pages.yml",
    ".github/workflows/update-profile.yml",
    "profile/content/evidence.yml",
    "templates/README.md",
    "templates/manifest.yml",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
    "docs/PRIVACY.md",
)


def test_staging_directory_removed() -> None:
    assert not (REPO_ROOT / ".staging").exists()


def test_active_files_do_not_reference_staging_paths() -> None:
    for rel_path in ACTIVE_FILES:
        content = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert ".staging" not in content, rel_path


def test_migration_ledger_has_no_unresolved_rows() -> None:
    rows: list[list[str]] = []
    content = (REPO_ROOT / "docs/MIGRATION.md").read_text(encoding="utf-8")
    for line in content.splitlines():
        if not line.startswith("|"):
            continue
        columns = [value.strip() for value in line.strip("|").split("|")]
        if len(columns) >= 7 and columns[0].isdigit():
            rows.append(columns)

    assert len(rows) == EXPECTED_LEDGER_ROW_COUNT
    unresolved = [row[0] for row in rows if not row[6]]
    assert unresolved == []
