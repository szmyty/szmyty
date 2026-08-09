"""Tests for tools/profile_builder/cli.py."""

from __future__ import annotations

from pathlib import Path

import yaml
from click.testing import CliRunner

from tools.profile_builder.cli import main


def test_validate_uses_records_key(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.yml"
    evidence.write_text(
        yaml.safe_dump(
            {
                "schema_version": "1",
                "records": [
                    {
                        "id": "verified-claim",
                        "claim": "Claim",
                        "evidence_type": "none",
                        "status": "verified",
                        "sensitivity": "public",
                        "last_reviewed": "2026-08-09",
                    },
                    {
                        "id": "needs-review-claim",
                        "claim": "Claim",
                        "evidence_type": "none",
                        "status": "needs-user-verification",
                        "sensitivity": "public",
                        "last_reviewed": "2026-08-09",
                    },
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    modules = tmp_path / "modules.yml"
    modules.write_text("modules: []\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["validate", "--evidence", str(evidence), "--config", str(modules)],
    )

    assert result.exit_code == 0
    assert "evidence: 2 entries — 1 verified, 1 needs-user-verification, 0 excluded" in result.output
