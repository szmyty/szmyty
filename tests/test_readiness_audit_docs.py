from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]


def test_final_readiness_artifacts_exist_and_cross_link() -> None:
    report = REPO_ROOT / "docs" / "audits" / "FINAL-PROFILE-READINESS-REPORT.md"
    handoff = REPO_ROOT / "docs" / "FINAL-OWNER-HANDOFF-CHECKLIST.md"
    runbook = (REPO_ROOT / "docs" / "RUNBOOK.md").read_text(encoding="utf-8")

    assert report.exists()
    assert handoff.exists()
    assert handoff.name in runbook

    report_text = report.read_text(encoding="utf-8")
    handoff_text = handoff.read_text(encoding="utf-8")

    assert "## Recommendation" in report_text
    assert any(
        token in report_text
        for token in ("**READY**", "**READY WITH MANUAL SETUP**", "**NOT READY**")
    )
    assert "egolint" in report_text
    assert report.name in handoff_text
