"""Pydantic models for normalized profile builder inputs.

All public inputs are validated here before being passed to renderers.
Models are intentionally minimal; extend only when a second concrete module
needs the same abstraction.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Evidence catalog
# ---------------------------------------------------------------------------


class EvidenceEntry(BaseModel):
    """One entry in the evidence catalog (profile/content/evidence.yml)."""

    id: str = Field(description="Stable kebab-case identifier.")
    claim: str = Field(description="Candidate claim text as it might appear in a profile.")
    evidence_type: Literal["url", "repo-path", "self-reported", "inferred", "none"] = Field(
        description="Kind of evidence backing the claim."
    )
    url: str | None = Field(default=None, description="Public URL to the evidence artifact.")
    repo_path: str | None = Field(
        default=None, description="Repository-relative path to the artifact."
    )
    status: Literal["verified", "needs-user-verification", "excluded"] = Field(
        description="Current verification status."
    )
    sensitivity: Literal["public", "sensitive", "internal"] = Field(
        description="Privacy sensitivity of the claim."
    )
    last_reviewed: str = Field(description="ISO-8601 review date (YYYY-MM-DD).")
    notes: str | None = Field(default=None, description="Optional free-text notes.")

    @field_validator("url", mode="before")
    @classmethod
    def _coerce_url(cls, v: object) -> str | None:
        """Accept plain strings; skip empty values."""
        if not v:
            return None
        return str(v)

    @field_validator("repo_path", mode="before")
    @classmethod
    def _coerce_repo_path(cls, v: object) -> str | None:
        if not v:
            return None
        return str(v)


class EvidenceCatalog(BaseModel):
    """Validated evidence catalog loaded from profile/content/evidence.yml."""

    entries: list[EvidenceEntry] = Field(default_factory=list)

    @property
    def verified(self) -> list[EvidenceEntry]:
        """Return only verified entries."""
        return [e for e in self.entries if e.status == "verified"]

    @property
    def pending(self) -> list[EvidenceEntry]:
        """Return entries that require explicit user verification before publish."""
        return [e for e in self.entries if e.status == "needs-user-verification"]

    @property
    def excluded(self) -> list[EvidenceEntry]:
        """Return entries excluded from publication."""
        return [e for e in self.entries if e.status == "excluded"]


# ---------------------------------------------------------------------------
# Module configuration
# ---------------------------------------------------------------------------


class ModuleConfig(BaseModel):
    """Configuration for one named profile module (region + optional artifact)."""

    name: str = Field(description="Stable machine-readable module name.")
    enabled: bool = Field(default=True, description="Whether this module is active.")
    region_start_marker: str = Field(
        description="HTML comment that opens the owned README region, e.g. <!-- START:module -->"
    )
    region_end_marker: str = Field(
        description="HTML comment that closes the owned README region, e.g. <!-- END:module -->"
    )
    template: str = Field(description="Template name relative to profile/templates/.")
    artifact_path: Path | None = Field(
        default=None,
        description="Optional path to a tracked artifact produced by this module.",
    )

    @field_validator("region_start_marker", "region_end_marker", mode="before")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()


class ProfileConfig(BaseModel):
    """Top-level configuration collected from all active modules."""

    modules: list[ModuleConfig] = Field(default_factory=list)

    @property
    def enabled_modules(self) -> list[ModuleConfig]:
        """Return only enabled modules in declaration order."""
        return [m for m in self.modules if m.enabled]

    @model_validator(mode="after")
    def _validate_unique_region_ownership(self) -> "ProfileConfig":
        names_seen: set[str] = set()
        start_seen: set[str] = set()
        end_seen: set[str] = set()
        for module in self.modules:
            if module.name in names_seen:
                raise ValueError(f"Duplicate module name: {module.name}")
            names_seen.add(module.name)
            if module.region_start_marker in start_seen:
                raise ValueError(
                    f"Duplicate region_start_marker: {module.region_start_marker}"
                )
            start_seen.add(module.region_start_marker)
            if module.region_end_marker in end_seen:
                raise ValueError(
                    f"Duplicate region_end_marker: {module.region_end_marker}"
                )
            end_seen.add(module.region_end_marker)
        return self


# ---------------------------------------------------------------------------
# Dynamic profile modules
# ---------------------------------------------------------------------------


class LanguageEntry(BaseModel):
    """Aggregated language usage entry for the GitHub metrics module."""

    name: str
    percentage: Annotated[float, Field(ge=0.0, le=100.0)]


class RepositorySummary(BaseModel):
    """Minimal repository details rendered into the metrics module."""

    name: str
    url: str
    description: str | None = None
    is_maintained: bool = True


class GithubMetrics(BaseModel):
    """Normalized GitHub profile metrics."""

    top_languages: list[LanguageEntry] = Field(default_factory=list, max_length=5)
    public_repo_count: int = Field(ge=0)
    maintained_repos: list[RepositorySummary] = Field(default_factory=list)
    latest_release: str | None = None
    data_source: Literal["live", "cache", "fixture"] = "fixture"


class ActivityEventType(str, Enum):
    """Supported public GitHub event types."""

    PUSH = "PushEvent"
    CREATE = "CreateEvent"
    PULL_REQUEST = "PullRequestEvent"
    ISSUE_COMMENT = "IssueCommentEvent"
    RELEASE = "ReleaseEvent"


class ActivityEvent(BaseModel):
    """One normalized recent-activity entry."""

    event_type: ActivityEventType
    repo: str
    repo_url: str
    summary: str
    occurred_at: str


class RecentActivity(BaseModel):
    """Bounded public GitHub activity feed."""

    events: list[ActivityEvent] = Field(default_factory=list, max_length=5)
    data_source: Literal["live", "cache", "fixture"] = "fixture"


class MusicHighlight(BaseModel):
    """Manually reviewed public music metadata."""

    title: str
    public_url: str
    description: str | None = None
    release_year: int | None = None
    artwork_path: str | None = None
    data_source: Literal["manual", "cache", "fixture"] = "manual"
