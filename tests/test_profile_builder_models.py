"""Tests for tools/profile_builder/models.py."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from tools.profile_builder.models import (
    ActivityEvent,
    EvidenceCatalog,
    EvidenceEntry,
    GithubMetrics,
    LanguageEntry,
    ModuleConfig,
    MusicHighlight,
    ProfileConfig,
    RecentActivity,
    RepositorySummary,
)


# ---------------------------------------------------------------------------
# EvidenceEntry
# ---------------------------------------------------------------------------


def test_evidence_entry_minimal() -> None:
    entry = EvidenceEntry(
        id="open-source-contributions",
        claim="Active open-source contributor.",
        evidence_type="url",
        status="verified",
    )
    assert entry.id == "open-source-contributions"
    assert entry.url is None


def test_evidence_entry_full() -> None:
    entry = EvidenceEntry(
        id="python-experience",
        claim="10+ years of Python.",
        evidence_type="self-reported",
        status="pending",
        notes="Inferred from commit history.",
    )
    assert entry.notes is not None


def test_evidence_entry_invalid_type() -> None:
    with pytest.raises(ValidationError):
        EvidenceEntry(
            id="x",
            claim="y",
            evidence_type="unsupported-type",  # type: ignore[arg-type]
            status="verified",
        )


def test_evidence_entry_invalid_status() -> None:
    with pytest.raises(ValidationError):
        EvidenceEntry(
            id="x",
            claim="y",
            evidence_type="none",
            status="unknown-status",  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# EvidenceCatalog
# ---------------------------------------------------------------------------


def test_evidence_catalog_verified_filter() -> None:
    catalog = EvidenceCatalog(
        entries=[
            EvidenceEntry(id="a", claim="A", evidence_type="none", status="verified"),
            EvidenceEntry(id="b", claim="B", evidence_type="none", status="pending"),
            EvidenceEntry(id="c", claim="C", evidence_type="none", status="disputed"),
        ]
    )
    assert len(catalog.verified) == 1
    assert catalog.verified[0].id == "a"
    assert len(catalog.pending) == 1
    assert catalog.pending[0].id == "b"


def test_evidence_catalog_empty() -> None:
    catalog = EvidenceCatalog(entries=[])
    assert catalog.verified == []
    assert catalog.pending == []


# ---------------------------------------------------------------------------
# ModuleConfig
# ---------------------------------------------------------------------------


def test_module_config_defaults() -> None:
    mod = ModuleConfig(
        name="example",
        region_start_marker="<!-- START:example -->",
        region_end_marker="<!-- END:example -->",
        template="example.md.j2",
    )
    assert mod.enabled is True
    assert mod.artifact_path is None


def test_module_config_marker_stripping() -> None:
    mod = ModuleConfig(
        name="example",
        region_start_marker="  <!-- START:example -->  ",
        region_end_marker="  <!-- END:example -->  ",
        template="example.md.j2",
    )
    assert mod.region_start_marker == "<!-- START:example -->"
    assert mod.region_end_marker == "<!-- END:example -->"


# ---------------------------------------------------------------------------
# ProfileConfig
# ---------------------------------------------------------------------------


def test_profile_config_enabled_modules() -> None:
    cfg = ProfileConfig(
        modules=[
            ModuleConfig(
                name="active",
                enabled=True,
                region_start_marker="<!-- START:active -->",
                region_end_marker="<!-- END:active -->",
                template="active.md.j2",
            ),
            ModuleConfig(
                name="inactive",
                enabled=False,
                region_start_marker="<!-- START:inactive -->",
                region_end_marker="<!-- END:inactive -->",
                template="inactive.md.j2",
            ),
        ]
    )
    assert len(cfg.enabled_modules) == 1
    assert cfg.enabled_modules[0].name == "active"


def test_profile_config_empty() -> None:
    cfg = ProfileConfig(modules=[])
    assert cfg.enabled_modules == []


# ---------------------------------------------------------------------------
# Dynamic module models
# ---------------------------------------------------------------------------


def test_github_metrics_model() -> None:
    metrics = GithubMetrics(
        top_languages=[LanguageEntry(name='Python', percentage=60.0)],
        public_repo_count=3,
        maintained_repos=[
            RepositorySummary(name='szmyty', url='https://github.com/szmyty/szmyty')
        ],
        latest_release='szmyty@v1.0.0',
        data_source='live',
    )
    assert metrics.top_languages[0].name == 'Python'
    assert metrics.public_repo_count == 3


def test_recent_activity_model_max_length() -> None:
    event = ActivityEvent(
        event_type='PushEvent',
        repo='szmyty/szmyty',
        repo_url='https://github.com/szmyty/szmyty',
        summary='Updated profile README',
        occurred_at='2024-01-15',
    )
    activity = RecentActivity(events=[event], data_source='fixture')
    assert activity.events[0].repo == 'szmyty/szmyty'


def test_music_highlight_model_optional_fields() -> None:
    music = MusicHighlight(
        title='Ego Hygiene',
        public_url='https://soundcloud.com/szmyty',
        data_source='manual',
    )
    assert music.description is None
    assert music.artwork_path is None
