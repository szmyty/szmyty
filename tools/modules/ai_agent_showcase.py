"""Build an evidence-backed public AI-agent execution showcase."""

from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib import error, request

import click
import yaml

from tools.profile_builder import cache as cache_utils
from tools.profile_builder.models import (
    AgentShowcaseArtifactLink,
    AgentShowcaseCandidate,
    AgentShowcaseConfig,
    AgentShowcaseProvenance,
    AgentShowcaseRepositoryRef,
    AgentShowcaseSnapshot,
    AgentShowcaseStage,
    AgentShowcaseTrace,
    AgentShowcaseValidationOutcome,
)
from tools.profile_builder.rendering import render_template

MODULE_NAME = "ai-agent-showcase"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / "profile" / "content" / "ai-agent-showcase.yml"
DEFAULT_FIXTURE = REPO_ROOT / "profile" / "fixtures" / "ai-agent-showcase.json"
DEFAULT_OUTPUT = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME / "cache.json"
DEFAULT_CARD_OUTPUT = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME / "card.svg"
DEFAULT_PAGE_OUTPUT = REPO_ROOT / "site" / "ai-agent-showcase.html"
DEFAULT_TEMPLATES = REPO_ROOT / "profile" / "templates"
_MAX_ARTIFACT_LINKS = 6
_API_ROOT = "https://api.github.com"
_TIMEOUT = 20
_QUEUE_KEY_PATTERN = re.compile(r"Stable queue key:\s*`([^`]+)`", re.IGNORECASE)


class ProviderFailure(RuntimeError):
    """Raised when live public evidence cannot produce a complete trace."""


def _github_get_json(path: str, token: str | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "szmyty-profile-builder/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    req = request.Request(f"{_API_ROOT}{path}", headers=headers)
    try:
        with request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:  # pragma: no cover - exercised via fallback paths
        raise ProviderFailure(f"GitHub API request failed: HTTP {exc.code}") from exc
    except error.URLError as exc:  # pragma: no cover - exercised via fallback paths
        raise ProviderFailure(f"GitHub API unreachable: {exc.reason}") from exc


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _page_url(config: AgentShowcaseConfig) -> str:
    return f"https://szmyty.github.io/{config.repo}/{config.page_path}"


def load_config(path: Path = DEFAULT_INPUT) -> AgentShowcaseConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("AI agent showcase config must contain a mapping.")
    return AgentShowcaseConfig.model_validate(raw)


def load_fixture(path: Path = DEFAULT_FIXTURE) -> AgentShowcaseSnapshot:
    return AgentShowcaseSnapshot.model_validate_json(path.read_text(encoding="utf-8"))


def load_cached(path: Path = DEFAULT_OUTPUT) -> AgentShowcaseSnapshot | None:
    if not path.exists():
        return None
    cached = AgentShowcaseSnapshot.model_validate_json(path.read_text(encoding="utf-8"))
    return cached.model_copy(
        update={
            "generated_at": datetime.now(UTC).isoformat(),
            "provenance": cached.provenance.model_copy(
                update={"data_source": "cache", "source_state": "cached"}
            ),
        }
    )


def _extract_problem_summary(body: str) -> str:
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
        if paragraph.startswith("#") or paragraph.startswith("```"):
            continue
        if paragraph.startswith("- ") or paragraph.startswith("* "):
            continue
        return " ".join(line.strip() for line in paragraph.splitlines())
    return "Public issue selected for the execution showcase."


def _extract_queue_key(body: str) -> str | None:
    match = _QUEUE_KEY_PATTERN.search(body)
    return match.group(1) if match else None


def _issue_is_blocked(issue: dict[str, Any], config: AgentShowcaseConfig) -> bool:
    label_names = [
        str(label.get("name", "")).lower() for label in issue.get("labels", [])
    ]
    blocked_labels = tuple(term.lower() for term in config.blocked_label_terms)
    if any(term in label for term in blocked_labels for label in label_names):
        return True
    text = " ".join(
        [
            str(issue.get("title", "")).lower(),
            str(issue.get("body", "")).lower(),
        ]
    )
    return any(term.lower() in text for term in config.blocked_text_terms)


def _file_kind(path: str) -> str:
    if path.startswith("docs/"):
        return "documentation"
    if path.startswith("tests/"):
        return "test"
    if path.startswith(".github/workflows/"):
        return "workflow"
    if path.startswith("site/") or path.startswith("assets/") or path.endswith(".svg"):
        return "visual"
    return "code"


def _artifact_links(
    files: list[dict[str, Any]],
    owner: str,
    repo: str,
    commit_sha: str,
) -> list[AgentShowcaseArtifactLink]:
    links: list[AgentShowcaseArtifactLink] = []
    for item in files[:_MAX_ARTIFACT_LINKS]:
        filename = str(item.get("filename", "")).strip()
        if not filename:
            continue
        links.append(
            AgentShowcaseArtifactLink(
                label=filename,
                kind=_file_kind(filename),
                public_url=f"https://github.com/{owner}/{repo}/blob/{commit_sha}/{filename}",
            )
        )
    return links


def _summarize_files(files: list[dict[str, Any]]) -> str:
    if not files:
        return "no tracked file changes listed"
    names = [
        str(item.get("filename", "")).strip() for item in files if item.get("filename")
    ]
    if len(names) <= 3:
        return ", ".join(names)
    return f"{', '.join(names[:3])}, and {len(names) - 3} more"


def _validation_summary(run: dict[str, Any], jobs: dict[str, Any]) -> str:
    job_list = jobs.get("jobs", [])
    if not job_list:
        return f"{run['name']} run concluded {run['conclusion']}."
    validate_job = job_list[0]
    passing_steps = [
        step["name"]
        for step in validate_job.get("steps", [])
        if step.get("conclusion") == "success"
        and step.get("name")
        in {
            "Validate profile inputs",
            "Validate profile assets",
            "Lint Python",
            "Lint workflow YAML",
            "Run tests",
        }
    ]
    return (
        f"{run['name']} validate job passed "
        f"{len(passing_steps)} public checks: {', '.join(passing_steps)}."
    )


def _build_trace(
    config: AgentShowcaseConfig,
    candidate: AgentShowcaseCandidate,
    token: str | None,
) -> tuple[str, AgentShowcaseTrace]:
    issue = _github_get_json(
        f"/repos/{config.owner}/{config.repo}/issues/{candidate.issue_number}",
        token,
    )
    if issue.get("state") != "closed":
        raise ProviderFailure(f"Issue #{candidate.issue_number} is not completed")
    if _issue_is_blocked(issue, config):
        raise ProviderFailure(
            f"Issue #{candidate.issue_number} is not eligible for showcase"
        )

    pr = _github_get_json(
        f"/repos/{config.owner}/{config.repo}/pulls/{candidate.implementation_pr_number}",
        token,
    )
    if not pr.get("merged"):
        raise ProviderFailure(f"PR #{candidate.implementation_pr_number} is not merged")
    files = _github_get_json(
        f"/repos/{config.owner}/{config.repo}/pulls/{candidate.implementation_pr_number}/files",
        token,
    )
    run = _github_get_json(
        f"/repos/{config.owner}/{config.repo}/actions/runs/{candidate.validation_run_id}",
        token,
    )
    if run.get("conclusion") != "success":
        raise ProviderFailure(f"Run {candidate.validation_run_id} did not pass")
    jobs = _github_get_json(
        f"/repos/{config.owner}/{config.repo}/actions/runs/{candidate.validation_run_id}/jobs",
        token,
    )

    body = str(issue.get("body", "") or "")
    queue_key = _extract_queue_key(body)
    problem_summary = _extract_problem_summary(body)
    labels = [
        str(label.get("name", ""))
        for label in issue.get("labels", [])
        if label.get("name")
    ]
    merge_commit_sha = (
        str(pr.get("merge_commit_sha") or "")
        or str(run.get("head_sha") or "")
        or str(pr.get("head", {}).get("sha") or "")
    )
    file_summary = _summarize_files(files if isinstance(files, list) else [])
    issue_url = str(issue["html_url"])
    pr_url = str(pr["html_url"])
    run_url = str(run["html_url"])
    closed_at = str(issue.get("closed_at") or "")[:10]

    trace = AgentShowcaseTrace(
        trace_id=f"issue-{candidate.issue_number}",
        public_title=str(issue.get("title", "")),
        problem_summary=problem_summary,
        stable_queue_key=queue_key,
        issue_labels=labels,
        stages=[
            AgentShowcaseStage(
                type="intent",
                status="completed",
                evidence_mode="observed",
                public_url=issue_url,
                evidence_summary=problem_summary,
            ),
            AgentShowcaseStage(
                type="architecture",
                status="completed",
                evidence_mode=candidate.architecture.evidence_mode,
                public_url=candidate.architecture.public_url,
                evidence_summary=candidate.architecture.evidence_summary,
            ),
            AgentShowcaseStage(
                type="specification",
                status="completed",
                evidence_mode=candidate.specification.evidence_mode,
                public_url=candidate.specification.public_url,
                evidence_summary=candidate.specification.evidence_summary,
            ),
            AgentShowcaseStage(
                type="issue",
                status="completed",
                evidence_mode="observed",
                public_url=issue_url,
                evidence_summary=(
                    f"Issue #{candidate.issue_number} closed with labels "
                    f"{', '.join(labels)}."
                ),
            ),
            AgentShowcaseStage(
                type="implementation",
                status="completed",
                evidence_mode="observed",
                public_url=pr_url,
                evidence_summary=(
                    f"PR #{candidate.implementation_pr_number} merged with "
                    f"{pr.get('changed_files', 0)} changed file(s): {file_summary}."
                ),
            ),
            AgentShowcaseStage(
                type="validation",
                status="completed",
                evidence_mode="observed",
                public_url=run_url,
                evidence_summary=_validation_summary(run, jobs),
            ),
            AgentShowcaseStage(
                type="reflection",
                status="completed",
                evidence_mode=candidate.reflection.evidence_mode,
                public_url=candidate.reflection.public_url,
                evidence_summary=candidate.reflection.evidence_summary,
            ),
        ],
        repository=AgentShowcaseRepositoryRef(
            owner=config.owner,
            repo=config.repo,
            issue_number=candidate.issue_number,
            issue_url=issue_url,
            pull_request_number=candidate.implementation_pr_number,
            pull_request_url=pr_url,
            base_ref=str(pr.get("base", {}).get("ref") or "master"),
            merge_commit_sha=merge_commit_sha,
            merge_commit_url=(
                f"https://github.com/{config.owner}/{config.repo}/commit/{merge_commit_sha}"
            ),
        ),
        validation=AgentShowcaseValidationOutcome(
            status="passed",
            public_url=run_url,
            summary=_validation_summary(run, jobs),
        ),
        artifacts=_artifact_links(
            files if isinstance(files, list) else [],
            config.owner,
            config.repo,
            merge_commit_sha,
        ),
        outcome_summary=(
            f"Merged to {pr.get('base', {}).get('ref', 'master')} after "
            f"{run['name']} passed on the public repository."
        ),
        follow_up_state=(
            "Last-known-good output remains renderable from committed artifacts."
        ),
        completed_date=closed_at,
        freshness_date=closed_at,
    )
    return str(issue.get("closed_at") or ""), trace


def _select_live_snapshot(
    config: AgentShowcaseConfig,
    token: str | None,
) -> AgentShowcaseSnapshot:
    eligible: list[tuple[str, AgentShowcaseTrace]] = []
    for candidate in config.candidates:
        if not candidate.showcase:
            continue
        try:
            eligible.append(_build_trace(config, candidate, token))
        except ProviderFailure:
            continue
    if not eligible:
        raise ProviderFailure("No complete public showcase traces were eligible")
    _, trace = sorted(eligible, key=lambda item: item[0], reverse=True)[0]
    return AgentShowcaseSnapshot(
        selected_trace=trace,
        page_url=_page_url(config),
        generated_at=datetime.now(UTC).isoformat(),
        provenance=AgentShowcaseProvenance(
            data_source="live",
            source_state="fresh",
            selected_from_candidates=len(eligible),
            notes="Selected the most recent completed opted-in public issue.",
        ),
    )


def _render_outputs(
    snapshot: AgentShowcaseSnapshot,
    *,
    card_output_path: Path,
    page_output_path: Path,
    templates_dir: Path,
) -> None:
    svg = (
        render_template(
            "ai-agent-showcase-card.svg.j2",
            {"snapshot": snapshot, "trace": snapshot.selected_trace},
            templates_dir=templates_dir,
        ).rstrip()
        + "\n"
    )
    page = (
        render_template(
            "ai-agent-showcase-page.html.j2",
            {"snapshot": snapshot, "trace": snapshot.selected_trace},
            templates_dir=templates_dir,
        ).rstrip()
        + "\n"
    )
    _write_text(card_output_path, svg)
    _write_text(page_output_path, page)


def build_showcase(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
    card_output_path: Path = DEFAULT_CARD_OUTPUT,
    page_output_path: Path = DEFAULT_PAGE_OUTPUT,
    templates_dir: Path = DEFAULT_TEMPLATES,
) -> AgentShowcaseSnapshot:
    """Build the public execution showcase with cache/fixture fallback."""
    error_msg: str | None = None
    try:
        config = load_config(input_path)
        snapshot = _select_live_snapshot(config, os.environ.get("GITHUB_TOKEN"))
        metadata_state = "fresh"
    except Exception as exc:  # noqa: BLE001
        error_msg = str(exc)
        snapshot = load_cached(output_path)
        if snapshot is not None:
            snapshot = snapshot.model_copy(
                update={
                    "generated_at": datetime.now(UTC).isoformat(),
                    "provenance": snapshot.provenance.model_copy(
                        update={
                            "data_source": "cache",
                            "source_state": "failed-with-fallback",
                        }
                    ),
                }
            )
            metadata_state = "failed-with-fallback"
        else:
            fixture = load_fixture(fixture_path)
            snapshot = fixture.model_copy(
                update={
                    "generated_at": datetime.now(UTC).isoformat(),
                    "provenance": fixture.provenance.model_copy(
                        update={"data_source": "fixture", "source_state": "static"}
                    ),
                }
            )
            metadata_state = "static"

    _write_json(output_path, snapshot.model_dump(mode="json"))
    _render_outputs(
        snapshot,
        card_output_path=card_output_path,
        page_output_path=page_output_path,
        templates_dir=templates_dir,
    )
    cache_utils.write_metadata(
        module_name=MODULE_NAME,
        state=metadata_state,
        data_source=snapshot.provenance.data_source,
        human_summary=f"AI agent showcase ({metadata_state})",
        data_at=snapshot.selected_trace.completed_date,
        error=error_msg,
    )
    return snapshot


@click.command()
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, path_type=Path),
    default=str(DEFAULT_INPUT),
    show_default=True,
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_OUTPUT),
    show_default=True,
)
@click.option(
    "--fixture",
    "fixture_path",
    type=click.Path(exists=True, path_type=Path),
    default=str(DEFAULT_FIXTURE),
    show_default=True,
)
@click.option(
    "--card-output",
    "card_output_path",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_CARD_OUTPUT),
    show_default=True,
)
@click.option(
    "--page-output",
    "page_output_path",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_PAGE_OUTPUT),
    show_default=True,
)
@click.option(
    "--templates",
    "templates_dir",
    type=click.Path(exists=True, path_type=Path),
    default=str(DEFAULT_TEMPLATES),
    show_default=True,
)
def main(
    input_path: Path,
    output_path: Path,
    fixture_path: Path,
    card_output_path: Path,
    page_output_path: Path,
    templates_dir: Path,
) -> None:
    """Write the selected public AI-agent showcase artifact and renderers."""
    snapshot = build_showcase(
        input_path=input_path,
        output_path=output_path,
        fixture_path=fixture_path,
        card_output_path=card_output_path,
        page_output_path=page_output_path,
        templates_dir=templates_dir,
    )
    click.echo(
        f"ai-agent-showcase: wrote {output_path} ({snapshot.provenance.data_source})"
    )


if __name__ == "__main__":
    main()
