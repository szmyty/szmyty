from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tools.modules import ai_agent_showcase
from tools.profile_builder.models import (
    AgentShowcaseConfig,
    AgentShowcaseStage,
    AgentShowcaseStageBlueprint,
)


def test_showcase_content_file_loads() -> None:
    config = ai_agent_showcase.load_config()
    assert isinstance(config, AgentShowcaseConfig)
    assert len(config.candidates) >= 3


def test_observed_stage_requires_public_github_or_pages_url() -> None:
    with pytest.raises(ValidationError):
        AgentShowcaseStageBlueprint(
            evidence_mode="observed",
            public_url="https://example.com/private",
            evidence_summary="Bad host",
        )

    with pytest.raises(ValidationError):
        AgentShowcaseStage(
            type="validation",
            status="completed",
            evidence_mode="observed",
            evidence_summary="Missing direct link",
        )


def test_select_live_snapshot_prefers_latest_completed_non_sensitive_issue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    full_config = ai_agent_showcase.load_config()
    config = full_config.model_copy(update={"candidates": full_config.candidates[1:]})

    def fake_get_json(path: str, token: str | None = None) -> object:
        if path.endswith("/issues/111"):
            return {
                "number": 111,
                "state": "closed",
                "title": "Issue 111",
                "html_url": "https://github.com/szmyty/szmyty/issues/111",
                "body": (
                    "## Objective\n\n"
                    "Issue 111 summary.\n\n"
                    "Stable queue key: `queue-111`"
                ),
                "labels": [{"name": "profile-finalization"}],
                "closed_at": "2026-08-09T20:29:59Z",
            }
        if path.endswith("/issues/112"):
            return {
                "number": 112,
                "state": "closed",
                "title": "Issue 112",
                "html_url": "https://github.com/szmyty/szmyty/issues/112",
                "body": (
                    "## Objective\n\n"
                    "Issue 112 summary.\n\n"
                    "Stable queue key: `queue-112`"
                ),
                "labels": [{"name": "profile-finalization"}],
                "closed_at": "2026-08-09T20:47:50Z",
            }
        if path.endswith("/issues/113"):
            return {
                "number": 113,
                "state": "closed",
                "title": "Sensitive issue 113",
                "html_url": "https://github.com/szmyty/szmyty/issues/113",
                "body": (
                    "## Objective\n\n"
                    "Oura health summary.\n\n"
                    "Stable queue key: `queue-113`"
                ),
                "labels": [{"name": "area:security"}],
                "closed_at": "2026-08-09T21:01:18Z",
            }
        if path.endswith("/pulls/125"):
            return {
                "html_url": "https://github.com/szmyty/szmyty/pull/125",
                "merged": True,
                "changed_files": 2,
                "base": {"ref": "master"},
                "merge_commit_sha": "b" * 40,
            }
        if path.endswith("/pulls/126"):
            return {
                "html_url": "https://github.com/szmyty/szmyty/pull/126",
                "merged": True,
                "changed_files": 3,
                "base": {"ref": "master"},
                "merge_commit_sha": "c" * 40,
            }
        if path.endswith("/pulls/125/files"):
            return [{"filename": "tests/test_modules.py"}]
        if path.endswith("/pulls/126/files"):
            return [
                {"filename": "tools/modules/soundcloud.py"},
                {"filename": "tests/test_modules.py"},
                {"filename": "profile/templates/soundcloud.md.j2"},
            ]
        if path.endswith("/actions/runs/31334404125"):
            return {
                "name": "CI",
                "conclusion": "success",
                "html_url": "https://github.com/szmyty/szmyty/actions/runs/31334404125",
                "head_sha": "b" * 40,
            }
        if path.endswith("/actions/runs/31335166521"):
            return {
                "name": "CI",
                "conclusion": "success",
                "html_url": "https://github.com/szmyty/szmyty/actions/runs/31335166521",
                "head_sha": "c" * 40,
            }
        if path.endswith("/actions/runs/31334404125/jobs"):
            return {
                "jobs": [
                    {
                        "steps": [
                            {
                                "name": "Validate profile inputs",
                                "conclusion": "success",
                            },
                            {"name": "Run tests", "conclusion": "success"},
                        ]
                    }
                ]
            }
        if path.endswith("/actions/runs/31335166521/jobs"):
            return {
                "jobs": [
                    {
                        "steps": [
                            {
                                "name": "Validate profile inputs",
                                "conclusion": "success",
                            },
                            {
                                "name": "Validate profile assets",
                                "conclusion": "success",
                            },
                            {"name": "Lint Python", "conclusion": "success"},
                            {"name": "Lint workflow YAML", "conclusion": "success"},
                            {"name": "Run tests", "conclusion": "success"},
                        ]
                    }
                ]
            }
        raise AssertionError(f"Unexpected path: {path}")

    monkeypatch.setattr(ai_agent_showcase, "_github_get_json", fake_get_json)

    snapshot = ai_agent_showcase._select_live_snapshot(config, token=None)

    assert snapshot.selected_trace.repository.issue_number == 112
    assert snapshot.selected_trace.validation.status == "passed"
    assert snapshot.provenance.selected_from_candidates == 2


def test_build_showcase_falls_back_to_cache_when_live_data_is_incomplete(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cached = ai_agent_showcase.load_fixture().model_copy(
        update={
            "provenance": ai_agent_showcase.load_fixture().provenance.model_copy(
                update={"data_source": "live", "source_state": "fresh"}
            )
        }
    )
    output = tmp_path / "profile" / "artifacts" / "ai-agent-showcase" / "cache.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(cached.model_dump(mode="json")), encoding="utf-8")

    monkeypatch.setattr(
        ai_agent_showcase,
        "_select_live_snapshot",
        lambda config, token: (_ for _ in ()).throw(
            ai_agent_showcase.ProviderFailure("missing relationship")
        ),
    )

    snapshot = ai_agent_showcase.build_showcase(
        input_path=ai_agent_showcase.DEFAULT_INPUT,
        output_path=output,
        fixture_path=ai_agent_showcase.DEFAULT_FIXTURE,
        card_output_path=tmp_path / "card.svg",
        page_output_path=tmp_path / "detail.html",
    )

    assert snapshot.provenance.data_source == "cache"
    assert snapshot.provenance.source_state == "failed-with-fallback"


def test_rendered_outputs_are_static_and_accessible(tmp_path: Path) -> None:
    snapshot = ai_agent_showcase.load_fixture()
    card = tmp_path / "card.svg"
    page = tmp_path / "detail.html"

    ai_agent_showcase._render_outputs(
        snapshot,
        card_output_path=card,
        page_output_path=page,
        templates_dir=Path(__file__).resolve().parents[1] / "profile" / "templates",
    )

    card_text = card.read_text(encoding="utf-8")
    page_text = page.read_text(encoding="utf-8")

    assert "<title" in card_text
    assert "<desc" in card_text
    assert "Inspect public evidence" in page_text
    assert "This stage is explanatory context" in page_text
    assert (
        '<script type="module" src="js/execution-observatory.js"></script>' in page_text
    )
    assert "JavaScript is disabled. Use the timeline links below" in page_text
