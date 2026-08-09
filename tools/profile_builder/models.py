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
# Snapshot module platform
# ---------------------------------------------------------------------------


class ResultState(str, Enum):
    """Possible states returned by a module refresh."""

    FRESH = "fresh"
    CACHED = "cached"
    STATIC = "static"
    DISABLED = "disabled"
    FAILED_WITH_FALLBACK = "failed-with-fallback"


class FreshnessPolicy(BaseModel):
    """Declares how often a module should refresh and when it is considered stale."""

    cadence: Literal["never", "hourly", "daily", "weekly", "monthly"] = Field(
        description="How often the module data should be refreshed."
    )
    ttl_seconds: int | None = Field(
        default=None,
        ge=0,
        description="Time-to-live in seconds; None means no expiry.",
    )
    warn_after_seconds: int | None = Field(
        default=None,
        ge=0,
        description="Seconds after which a staleness warning is emitted; None disables.",
    )


class ModuleRegistryEntry(BaseModel):
    """Full registry declaration for one profile module."""

    name: str = Field(description="Stable kebab-case module name.")
    enabled: bool = Field(default=True, description="Whether this module is active.")
    description: str | None = Field(default=None, description="Human-readable description.")

    # Provider
    provider_type: Literal["api", "manual", "computed"] = Field(
        description="How the module obtains its data."
    )
    provider_module: str = Field(
        description="Importable Python path for the module script."
    )
    secret_names: list[str] = Field(
        default_factory=list,
        description="Names of required secrets (never values).",
    )

    # Privacy
    sensitivity: Literal["public", "internal", "sensitive"] = Field(
        description="Privacy sensitivity classification."
    )

    # Freshness
    freshness_policy: FreshnessPolicy = Field(
        description="Refresh cadence and TTL policy."
    )

    # Artifact layout
    artifact_dir: str = Field(
        description="Directory for all outputs, relative to repo root."
    )
    artifact_file: str = Field(
        description="Primary artifact filename within artifact_dir."
    )
    asset_files: list[str] = Field(
        default_factory=list,
        description="Additional generated files within artifact_dir.",
    )
    fixture_file: str | None = Field(
        default=None,
        description="Fallback fixture path, relative to repo root.",
    )

    # README integration
    readme_path: str = Field(
        default="README.md",
        description="Path to the README file managed by this module.",
    )
    region_start_marker: str = Field(
        description="HTML comment that opens the owned README region."
    )
    region_end_marker: str = Field(
        description="HTML comment that closes the owned README region."
    )
    template: str = Field(
        description="Jinja2 template filename relative to profile/templates/."
    )

    @field_validator("region_start_marker", "region_end_marker", mode="before")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()


class ModuleRegistry(BaseModel):
    """Top-level registry loaded from modules-registry.yml."""

    modules: list[ModuleRegistryEntry] = Field(default_factory=list)

    @property
    def enabled_modules(self) -> list[ModuleRegistryEntry]:
        """Return only enabled modules in declaration order."""
        return [m for m in self.modules if m.enabled]

    @model_validator(mode="after")
    def _validate_unique_names(self) -> "ModuleRegistry":
        names_seen: set[str] = set()
        for m in self.modules:
            if m.name in names_seen:
                raise ValueError(f"Duplicate module name: {m.name}")
            names_seen.add(m.name)
        return self


class ModuleResult(BaseModel):
    """Result produced by one module refresh cycle."""

    module_name: str
    state: ResultState
    human_summary: str
    data_source: Literal["live", "cache", "fixture", "manual", "disabled", "error"]
    result_at: str = Field(description="ISO-8601 datetime of this result.")
    data_at: str | None = Field(
        default=None,
        description="ISO-8601 datetime of the underlying data.",
    )
    data_hash: str | None = Field(
        default=None,
        description="SHA-256 hex digest of the primary artifact.",
    )
    ttl_seconds: int | None = None
    is_stale: bool = False
    seconds_until_stale: int | None = None
    error: str | None = None

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
        markers_seen: set[str] = set()
        for module in self.modules:
            if module.name in names_seen:
                raise ValueError(f"Duplicate module name: {module.name}")
            names_seen.add(module.name)
            if module.region_start_marker == module.region_end_marker:
                raise ValueError(
                    "Module "
                    f"{module.name} uses the same start and end region marker: "
                    f"{module.region_start_marker}"
                )
            if module.region_start_marker in markers_seen:
                raise ValueError(f"Region marker already in use: {module.region_start_marker}")
            markers_seen.add(module.region_start_marker)
            if module.region_end_marker in markers_seen:
                raise ValueError(f"Region marker already in use: {module.region_end_marker}")
            markers_seen.add(module.region_end_marker)
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
