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
    publication: Literal["allowed", "blocked-pending-owner-approval"] = Field(
        default="allowed",
        description=(
            "Publication gate. 'blocked-pending-owner-approval' prevents any "
            "public output until the owner explicitly approves the allowlist."
        ),
    )
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
    """Normalized GitHub profile metrics.

    All fields come exclusively from official GitHub REST API responses for
    the public user profile and public non-fork repositories.  Fields that
    are derived or aggregated are documented below.

    ``stars_received`` — sum of ``stargazers_count`` across all owned,
    non-fork, non-archived public repositories.  None when the value cannot
    be reliably computed (e.g. fixture mode).

    ``public_releases_count`` — count of public releases published within
    the last ``MAINTAINED_WINDOW_DAYS`` days across all owned non-fork
    public repositories.  None when unavailable.
    """

    top_languages: list[LanguageEntry] = Field(default_factory=list, max_length=5)
    public_repo_count: int = Field(ge=0)
    stars_received: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Total stargazers across owned, non-fork, non-archived public repositories. "
            "Omitted from fixture data to avoid fabricating adoption metrics."
        ),
    )
    public_releases_count: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Number of public releases published within MAINTAINED_WINDOW_DAYS "
            "across owned non-fork public repositories. Omitted from fixture data."
        ),
    )
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


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------


class EducationDegree(BaseModel):
    """A single verified education credential."""

    institution: str = Field(description="Full institution name.")
    degree: str = Field(description="Full degree title.")
    field_of_study: str = Field(description="Field or program of study.")
    institution_url: str | None = Field(
        default=None, description="Link to the official program or institution page."
    )
    graduation_year: int | None = Field(
        default=None, description="Optional graduation year (user-controlled)."
    )
    evidence_id: str = Field(
        description="ID of the evidence record backing this credential."
    )
    enabled: bool = Field(
        default=False,
        description="Whether this degree is approved for public rendering.",
    )


class EducationConfig(BaseModel):
    """Collection of education credentials for the profile."""

    degrees: list[EducationDegree] = Field(default_factory=list)

    @property
    def public_degrees(self) -> list[EducationDegree]:
        """Return only degrees approved for public rendering."""
        return [d for d in self.degrees if d.enabled]


# ---------------------------------------------------------------------------
# Resume
# ---------------------------------------------------------------------------


class ResumeConfig(BaseModel):
    """Configuration for the public resume surface."""

    enabled: bool = Field(
        default=False,
        description=(
            "Whether the public resume CTA is active.  Must remain False "
            "until a sanitized artifact passes the privacy/metadata checklist."
        ),
    )
    public_url: str | None = Field(
        default=None,
        description="Stable external URL or repo-relative path to the public PDF.",
    )
    evidence_id: str = Field(
        default="resume-public-document",
        description="Evidence catalog ID for the resume publication claim.",
    )
    checklist_path: str = Field(
        default="docs/RESUME-CHECKLIST.md",
        description="Repo-relative path to the privacy/metadata checklist.",
    )


# ---------------------------------------------------------------------------
# ORCID / publications
# ---------------------------------------------------------------------------


class OrcidWork(BaseModel):
    """One normalized public work from an ORCID record."""

    title: str
    work_type: str | None = None
    year: int | None = None
    doi: str | None = None
    public_url: str | None = None
    contributor_role: str | None = None

    @field_validator("doi", mode="before")
    @classmethod
    def _normalise_doi(cls, v: object) -> str | None:
        if not v:
            return None
        return str(v).strip()


class OrcidConfig(BaseModel):
    """User-supplied ORCID configuration slot."""

    enabled: bool = Field(
        default=False,
        description=(
            "Whether the ORCID module is active.  Must remain False "
            "until Alan supplies and confirms the ORCID iD."
        ),
    )
    orcid_id: str | None = Field(
        default=None,
        description="ORCID iD in 0000-0000-0000-0000 format.",
        pattern=r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$",
    )
    profile_url: str | None = Field(
        default=None,
        description="Canonical ORCID public profile URL.",
    )
    evidence_id: str = Field(default="orcid-id")


class OrcidData(BaseModel):
    """Normalized ORCID module output."""

    orcid_id: str | None = None
    profile_url: str | None = None
    works: list[OrcidWork] = Field(default_factory=list, max_length=10)
    data_source: Literal["live", "cache", "fixture", "disabled"] = "disabled"


# ---------------------------------------------------------------------------
# Medium writing
# ---------------------------------------------------------------------------


class MediumArticle(BaseModel):
    """One normalized article from a Medium RSS feed."""

    title: str
    canonical_url: str
    published_date: str = Field(description="ISO-8601 date string (YYYY-MM-DD).")
    summary: str | None = Field(
        default=None,
        description="Safe plain-text summary with HTML and tracking markup stripped.",
    )


class MediumConfig(BaseModel):
    """User-supplied Medium configuration slot."""

    enabled: bool = Field(
        default=False,
        description=(
            "Whether the Medium module is active.  Must remain False "
            "until Alan supplies and confirms the Medium username."
        ),
    )
    username: str | None = Field(
        default=None,
        description="Medium username (without @).",
    )
    evidence_id: str = Field(default="medium-username")

    @property
    def feed_url(self) -> str | None:
        """Return the public RSS feed URL, or None when username is unset."""
        if not self.username:
            return None
        return f"https://medium.com/feed/@{self.username}"


class MediumFeed(BaseModel):
    """Normalized Medium module output."""

    username: str | None = None
    profile_url: str | None = None
    articles: list[MediumArticle] = Field(default_factory=list, max_length=5)
    data_source: Literal["live", "cache", "fixture", "disabled"] = "disabled"


# ---------------------------------------------------------------------------
# Working style
# ---------------------------------------------------------------------------


class WorkingStyleConfig(BaseModel):
    """User-supplied 16Personalities working-style configuration.

    Every field requires explicit user approval before content can render.
    """

    enabled: bool = Field(
        default=False,
        description=(
            "Whether working-style content is approved for public rendering.  "
            "Must remain False until Alan supplies and approves all fields."
        ),
    )
    personality_type: str | None = Field(
        default=None,
        description="16Personalities type label (e.g. INFJ-A), supplied by Alan.",
    )
    personality_url: str | None = Field(
        default=None,
        description="Public 16Personalities profile or type link.",
    )
    image_path: str | None = Field(
        default=None,
        description="Repo-relative path to the user-owned personality image.",
    )
    summary: str | None = Field(
        default=None,
        description=(
            "Alan-approved first-person working-style summary.  "
            "Must not be generated or inferred."
        ),
    )
    evidence_id: str = Field(default="working-style-16personalities")


# ---------------------------------------------------------------------------
# STARS career development
# ---------------------------------------------------------------------------


class StarsConfig(BaseModel):
    """STARS career-development configuration slot (non-public by default).

    Raw coaching or career-development notes must never be published.
    Individual items must be explicitly approved by Alan before any content
    can render.
    """

    enabled: bool = Field(
        default=False,
        description=(
            "Whether any STARS content is approved for public rendering.  "
            "Must remain False until Alan explicitly selects and approves items."
        ),
    )
    public_items: list[str] = Field(
        default_factory=list,
        description=(
            "Alan-approved public-facing STARS items (plain text only).  "
            "Empty until Alan makes explicit selections."
        ),
    )
    evidence_id: str = Field(default="stars-career-development")


# ---------------------------------------------------------------------------
# SoundCloud snapshot
# ---------------------------------------------------------------------------


class SoundCloudSnapshot(BaseModel):
    """Sanitized public SoundCloud profile snapshot.

    All fields are optional so the model degrades cleanly when credentials
    or provider access are unavailable.  Artwork URLs are never embedded
    directly in rendered output to prevent active-content injection.
    """

    artist_name: str | None = Field(
        default=None,
        description="Public SoundCloud display name.",
    )
    profile_url: str | None = Field(
        default=None,
        description="Canonical public SoundCloud profile URL.",
    )
    latest_track_title: str | None = Field(
        default=None,
        description="Title of the most recent public track.",
    )
    latest_track_url: str | None = Field(
        default=None,
        description="Permalink of the most recent public track.",
    )
    track_count: int | None = Field(
        default=None,
        ge=0,
        description="Total number of public tracks in the catalog.",
    )
    data_source: Literal["live", "cache", "fixture", "static"] = Field(
        default="fixture",
        description="Origin of this snapshot.",
    )
    data_at: str | None = Field(
        default=None,
        description="ISO-8601 UTC timestamp of the source data.",
    )


# ---------------------------------------------------------------------------
# Steam snapshot
# ---------------------------------------------------------------------------


class SteamRecentGame(BaseModel):
    """Selected metadata for a recently played Steam game."""

    name: str = Field(description="Game title.")
    appid: int = Field(description="Steam application ID.")
    playtime_2weeks: int | None = Field(
        default=None,
        ge=0,
        description="Minutes played in the last two weeks.",
    )
    store_url: str | None = Field(
        default=None,
        description="Steam store page URL.",
    )


class SteamSnapshot(BaseModel):
    """Sanitized public Steam profile snapshot.

    Only data publicly visible through Steam's Web API with the user's current
    privacy settings is included.  Private game details or unavailable
    endpoints yield None fields rather than empty successful records.
    """

    display_name: str | None = Field(
        default=None,
        description="Public Steam display name.",
    )
    profile_url: str | None = Field(
        default=None,
        description="Public Steam community profile URL.",
    )
    steam_level: int | None = Field(
        default=None,
        ge=0,
        description="Public Steam level.",
    )
    recent_games: list[SteamRecentGame] = Field(
        default_factory=list,
        description="Selected recently played games (capped at 5).",
        max_length=5,
    )
    data_source: Literal["live", "cache", "fixture", "static"] = Field(
        default="fixture",
        description="Origin of this snapshot.",
    )
    data_at: str | None = Field(
        default=None,
        description="ISO-8601 UTC timestamp of the source data.",
    )


# ---------------------------------------------------------------------------
# Oura trends aggregate (gated; publication blocked by default)
# ---------------------------------------------------------------------------

# Approved band labels — the *only* values that may enter public output.
_SLEEP_BAND_LABELS: frozenset[str] = frozenset(
    {"below-average", "average", "above-average"}
)
_READINESS_BAND_LABELS: frozenset[str] = frozenset(
    {"below-average", "average", "above-average"}
)
_ACTIVITY_BAND_LABELS: frozenset[str] = frozenset(
    {"low", "moderate", "consistent"}
)
_HRV_DIRECTION_LABELS: frozenset[str] = frozenset(
    {"trending-down", "stable", "trending-up"}
)

# Explicit allowlist: only these keys may appear in the public aggregate.
OURA_PUBLIC_AGGREGATE_ALLOWLIST: frozenset[str] = frozenset(
    {
        "window_days",
        "contributing_days",
        "period_label",
        "avg_sleep_hours",
        "sleep_regularity_band",
        "avg_readiness_band",
        "activity_consistency_band",
        "hrv_direction",
        "is_synthetic",
        "data_source",
        "generated_month",
    }
)


class OuraTrendsAggregate(BaseModel):
    """Coarse, privacy-preserving Oura Ring aggregate for public profile display.

    Publication contract
    --------------------
    * This model is only written to a tracked artifact when the owning module
      has ``publication: allowed`` AND ``enabled: true`` in the registry.
    * Fields are restricted to the explicit allowlist above; unknown fields are
      rejected at validation time.
    * All values are coarse: sleep is rounded to the nearest 0.5 h; numeric
      readiness and HRV are replaced with band labels; timestamps are coarsened
      to month/year or week-ending date only.
    * ``is_synthetic`` must be ``True`` for fixture data.  A ``False`` value
      requires explicit owner approval and real credentials.

    Disclaimer
    ----------
    This is experimental personal wellness data shared voluntarily by the
    profile owner.  It does not constitute medical advice.
    """

    window_days: Literal[30, 90] = Field(
        description="Aggregation window: 30 or 90 days."
    )
    contributing_days: int = Field(
        ge=0,
        description="Number of days with valid data included in this window.",
    )
    period_label: str = Field(
        description=(
            "Coarse display label for the aggregation period, e.g. 'Jul 2026' "
            "or 'week ending 2026-07-27'.  Must not expose an exact date."
        )
    )

    # Approved aggregate metrics — all optional so they can be suppressed.
    avg_sleep_hours: float | None = Field(
        default=None,
        ge=0.0,
        le=24.0,
        description="Average sleep duration rounded to nearest 0.5 h.",
    )
    sleep_regularity_band: str | None = Field(
        default=None,
        description="Coarse regularity band: 'below-average', 'average', or 'above-average'.",
    )
    avg_readiness_band: str | None = Field(
        default=None,
        description="Coarse readiness band: 'below-average', 'average', or 'above-average'.",
    )
    activity_consistency_band: str | None = Field(
        default=None,
        description="Activity consistency band: 'low', 'moderate', or 'consistent'.",
    )
    hrv_direction: str | None = Field(
        default=None,
        description="HRV trend direction: 'trending-down', 'stable', or 'trending-up'.",
    )

    # Provenance
    is_synthetic: bool = Field(
        default=True,
        description=(
            "True for fixture / test data; must remain True until the owner "
            "approves real-data publication."
        ),
    )
    data_source: Literal["live", "cache", "fixture", "disabled"] = Field(
        default="fixture",
        description="Origin of this aggregate.",
    )
    generated_month: str = Field(
        description="Coarse generation label (YYYY-MM) — never an exact timestamp.",
    )

    @field_validator("sleep_regularity_band", mode="before")
    @classmethod
    def _validate_sleep_band(cls, v: object) -> str | None:
        if v is None:
            return None
        if str(v) not in _SLEEP_BAND_LABELS:
            raise ValueError(
                f"sleep_regularity_band {v!r} is not in the approved allowlist "
                f"{sorted(_SLEEP_BAND_LABELS)}"
            )
        return str(v)

    @field_validator("avg_readiness_band", mode="before")
    @classmethod
    def _validate_readiness_band(cls, v: object) -> str | None:
        if v is None:
            return None
        if str(v) not in _READINESS_BAND_LABELS:
            raise ValueError(
                f"avg_readiness_band {v!r} is not in the approved allowlist "
                f"{sorted(_READINESS_BAND_LABELS)}"
            )
        return str(v)

    @field_validator("activity_consistency_band", mode="before")
    @classmethod
    def _validate_activity_band(cls, v: object) -> str | None:
        if v is None:
            return None
        if str(v) not in _ACTIVITY_BAND_LABELS:
            raise ValueError(
                f"activity_consistency_band {v!r} is not in the approved allowlist "
                f"{sorted(_ACTIVITY_BAND_LABELS)}"
            )
        return str(v)

    @field_validator("hrv_direction", mode="before")
    @classmethod
    def _validate_hrv_direction(cls, v: object) -> str | None:
        if v is None:
            return None
        if str(v) not in _HRV_DIRECTION_LABELS:
            raise ValueError(
                f"hrv_direction {v!r} is not in the approved allowlist "
                f"{sorted(_HRV_DIRECTION_LABELS)}"
            )
        return str(v)

    @field_validator("avg_sleep_hours", mode="before")
    @classmethod
    def _round_sleep_hours(cls, v: object) -> float | None:
        """Round sleep hours to nearest 0.5 h to prevent precise inference."""
        if v is None:
            return None
        raw = float(v)  # type: ignore[arg-type]
        return round(raw * 2) / 2

    model_config = {"extra": "forbid"}
