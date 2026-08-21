import json
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
MANIFEST_PATH = REPO_ROOT / "docs" / "launch-gates" / "2026-08-21.json"
REPORT_PATH = (
    REPO_ROOT / "docs" / "audits" / "2026-08-21-CROSS-SURFACE-LAUNCH-REVIEW.md"
)


def load_gate() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_launch_gate_snapshot_is_current_and_fail_closed() -> None:
    gate = load_gate()

    assert gate["schema_version"] == 1
    assert date.fromisoformat(gate["review_date"]) == date(2026, 8, 21)
    assert gate["tracking_issue"].endswith("/szmyty/szmyty/issues/146")
    assert gate["overall_status"] == "blocked"
    assert gate["launch_decision"] == "not_ready_for_applications"
    assert gate["alan_signoff"] is False
    assert gate["blockers"]
    assert all(
        blocker["status"]
        in {
            "open",
            "pending",
            "pending_reference",
            "checks_pending",
            "checks_failed_repair_pending",
            "resolved",
        }
        for blocker in gate["blockers"]
    )
    assert any(blocker["status"] != "resolved" for blocker in gate["blockers"])


def test_profile_evidence_is_bounded_to_the_observed_live_state() -> None:
    profile = load_gate()["surfaces"]["profile"]

    assert profile["status"] == "partial_pass"
    assert profile["change_pull_request"]["number"] == 145
    assert profile["change_pull_request"]["state"] == "merged"

    observations = profile["live_observations"]
    assert observations == [
        {
            "id": "github-readme-signed-out-desktop-light",
            "date": "2026-08-21",
            "viewer": "signed_out",
            "viewport": "desktop",
            "theme": "light",
            "status": "pass",
            "scope_limit": (
                "This observation does not cover mobile, dark theme, or reduced motion."
            ),
        }
    ]


def test_portfolio_drafts_are_not_mistaken_for_visual_approval() -> None:
    portfolio = load_gate()["surfaces"]["portfolio"]
    pull_requests = {item["number"]: item for item in portfolio["pull_requests"]}

    assert portfolio["status"] == "blocked"
    assert set(pull_requests) == {290, 291, 292, 293}
    assert portfolio["preview_access"] == {
        "deployment_status": "ready",
        "signed_out_access": "blocked_by_vercel_sso",
        "visual_qa": "pending",
    }
    assert portfolio["integration_sequence"] == [
        {"phase": 1, "pull_requests": [291, 293]},
        {"phase": 2, "pull_requests": [292]},
        {"phase": 3, "pull_requests": [290]},
        {"phase": 4, "pull_requests": [294]},
    ]
    assert all(item["state"] == "draft" for item in pull_requests.values())
    assert all(item["checks"] == "pass" for item in pull_requests.values())
    assert all(
        item["preview_deployment"] == "ready"
        and item["signed_out_review"] == "blocked_by_vercel_sso"
        for item in pull_requests.values()
    )

    integration_contract = portfolio["integration_contract"]
    assert any(
        item["producer_pr"] == 293
        and item["consumer_pr"] == 292
        and "camera-fit" in item["requirement"]
        for item in integration_contract
    )


def test_pending_cross_surface_pr_references_keep_gate_blocked() -> None:
    surfaces = load_gate()["surfaces"]

    for surface_name in ("trust_suite", "resume"):
        surface = surfaces[surface_name]
        if surface["status"] == "pending_reference":
            assert surface["pull_request"] is None
        else:
            pull_request = surface["pull_request"]
            assert pull_request["number"] > 0
            assert pull_request["url"].startswith("https://github.com/")
            assert pull_request["state"] in {"draft", "open", "merged"}

    resume = surfaces["resume"]
    trust_suite = surfaces["trust_suite"]
    assert trust_suite["status"] == "draft_checks_pass"
    assert trust_suite["pull_request"]["number"] == 294
    assert trust_suite["pull_request"]["state"] == "draft"
    assert trust_suite["pull_request"]["integration_prerequisites"] == [
        290,
        291,
        292,
        293,
    ]
    assert trust_suite["pull_request"]["release_gate"]["status"] == "not_run"
    assert (
        trust_suite["pull_request"]["signed_out_preview_access"]
        == "blocked_by_vercel_sso"
    )
    assert (
        trust_suite["pull_request"]["release_gate"]["deployed_release_job"] == "skipped"
    )
    trust_checks = {
        check["name"]: check for check in trust_suite["pull_request"]["github_checks"]
    }
    assert trust_checks["CI"]["conclusion"] == "success"
    assert (
        trust_checks["Application Readiness static contracts"]["conclusion"]
        == "success"
    )
    assert trust_checks["Optimize Images"] == {
        "name": "Optimize Images",
        "run_id": 32511398215,
        "status": "completed",
        "conclusion": "success",
    }

    resume = surfaces["resume"]
    assert resume["status"] == "draft_checks_pass"
    assert resume["pull_request"]["number"] == 22
    assert resume["pull_request"]["state"] == "draft"
    assert resume["pull_request"]["head_sha"] == (
        "b514d11cb87f1de1b6a963a37701553db6cf1d44"
    )
    assert resume["pull_request"]["local_validation"] == "pass"
    assert (
        "9 artifacts and 18 rendered pages"
        in resume["pull_request"]["local_validation_summary"]
    )
    assert resume["pull_request"]["github_ci"] == {
        "run_id": 32511953627,
        "status": "completed",
        "conclusion": "success",
    }


def test_public_safety_and_history_work_are_separate_blockers() -> None:
    gate = load_gate()
    guild = gate["surfaces"]["guild"]
    scout = gate["surfaces"]["scout"]
    blockers = {blocker["id"]: blocker for blocker in gate["blockers"]}

    assert guild == {
        "status": "blocked",
        "repository": "https://github.com/167guild/167guild.io",
        "tracking_issue": "https://github.com/167guild/167guild.io/issues/69",
        "live_url": "https://167guild.io/",
        "signed_out_state": "public_wikijs_welcome_page",
        "required_state": (
            "restricted_or_intentionally_unpublished_and_verified_signed_out"
        ),
    }
    assert blockers["167guild-safety-state"]["separate_operation"] is True
    assert blockers["profile-history-remediation"]["separate_operation"] is True
    assert blockers["scout-application-strategy-privacy"]["separate_operation"] is True
    assert blockers["167guild-safety-state"]["tracking_issue"].endswith(
        "/167guild/167guild.io/issues/69"
    )
    assert blockers["profile-history-remediation"]["tracking_issue"].endswith(
        "/szmyty/szmyty/issues/147"
    )
    assert scout == {
        "status": "blocked",
        "repository": "https://github.com/szmyty/scout",
        "tracking_issue": "https://github.com/szmyty/scout/issues/3",
        "current_risk": "public_employer_level_application_strategy",
        "required_state": "aggregate_only_public_career_strategy_verified",
    }
    assert blockers["scout-application-strategy-privacy"]["tracking_issue"].endswith(
        "/szmyty/scout/issues/3"
    )


def test_owner_only_controls_are_specific_and_executable() -> None:
    controls = {
        control["id"]: control for control in load_gate()["owner_only_controls"]
    }

    assert set(controls) == {
        "github-account-bio",
        "github-pinned-repositories",
        "github-account-location",
        "github-branch-protection",
    }
    assert controls["github-account-bio"]["required_value"] == (
        "Software engineer building reliable developer platforms, "
        "local-first systems, and AI-assisted workflows."
    )
    assert controls["github-account-location"]["required_value"] == (
        "Greater Boston, MA"
    )
    assert controls["github-pinned-repositories"]["required_repositories"] == [
        "egohygiene/reflector",
        "egohygiene/renderflow",
        "egohygiene/relay",
        "egohygiene/aether",
        "egohygiene/optiflow",
        "egohygiene/mantle",
    ]
    assert controls["github-branch-protection"]["requirements"] == [
        "pull_requests_required",
        "required_checks_enabled",
        "default_branch_deletion_disabled",
        "default_branch_force_push_disabled",
    ]
    assert controls["github-branch-protection"]["history_cutover_exception"].endswith(
        "/szmyty/szmyty/issues/147"
    )


def test_ready_state_requires_every_manual_and_machine_gate() -> None:
    gate = load_gate()
    is_ready = gate["overall_status"] == "ready"
    blockers_resolved = all(
        blocker["status"] == "resolved" for blocker in gate["blockers"]
    )
    owner_controls_complete = all(
        control["status"] == "complete" for control in gate["owner_only_controls"]
    )
    surfaces_complete = all(
        gate["surfaces"][surface_name]["status"] == "pass"
        for surface_name in (
            "profile",
            "portfolio",
            "trust_suite",
            "resume",
            "guild",
            "scout",
        )
    )

    if is_ready:
        assert gate["launch_decision"] == "ready_for_applications"
        assert gate["alan_signoff"] is True
        assert blockers_resolved
        assert owner_controls_complete
        assert surfaces_complete
    else:
        assert not (
            gate["alan_signoff"]
            and blockers_resolved
            and owner_controls_complete
            and surfaces_complete
        )


def test_report_and_runbook_point_to_the_machine_gate() -> None:
    gate = load_gate()
    report = REPORT_PATH.read_text(encoding="utf-8")
    runbook = (REPO_ROOT / "docs" / "RUNBOOK.md").read_text(encoding="utf-8")
    handoff = (REPO_ROOT / "docs" / "FINAL-OWNER-HANDOFF-CHECKLIST.md").read_text(
        encoding="utf-8"
    )

    assert gate["report"] == REPORT_PATH.relative_to(REPO_ROOT).as_posix()
    assert "**NOT READY**" in report
    assert "- [ ] Alan reviewed" in report
    assert MANIFEST_PATH.name in report
    assert REPORT_PATH.name in runbook
    assert REPORT_PATH.name in handoff
