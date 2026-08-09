"""Pydantic models for normalized profile builder inputs.

All public inputs are validated here before being passed to renderers.
Models are intentionally minimal; extend only when a second concrete module
needs the same abstraction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


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
    status: Literal["verified", "pending", "disputed", "stale"] = Field(
        description="Current verification status."
    )
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
        """Return entries that have not yet been verified."""
        return [e for e in self.entries if e.status == "pending"]


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
