"""Normalized public-safe models for the GitHub engineering dashboard."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Owner configuration
# ---------------------------------------------------------------------------


class RepositoryOwnerConfig(BaseModel):
    """One declared repository owner for multi-owner collection."""

    model_config = ConfigDict(extra="forbid")

    login: str
    type: Literal["user", "organization"]


# ---------------------------------------------------------------------------
# Contribution models
# ---------------------------------------------------------------------------


class ContributionDay(BaseModel):
    """One public contribution-calendar day."""

    model_config = ConfigDict(extra="forbid")

    date: str
    contribution_count: int = Field(ge=0)
    level: int = Field(ge=0, le=4)
    weekday: int = Field(ge=0, le=6)
    is_future: bool = False

    @field_validator("date")
    @classmethod
    def _validate_date(cls, value: str) -> str:
        if len(value) != 10:
            raise ValueError("date must use YYYY-MM-DD format")
        return value


class ContributionBreakdown(BaseModel):
    """Trailing-window public GitHub contribution totals."""

    model_config = ConfigDict(extra="forbid")

    total_public_contributions: int = Field(ge=0)
    public_commit_contributions: int = Field(ge=0)
    public_pull_request_contributions: int = Field(ge=0)
    public_issue_contributions: int = Field(ge=0)
    public_pull_request_review_contributions: int = Field(ge=0)


class StreakMetrics(BaseModel):
    """Contribution streaks limited to the displayed trailing window."""

    model_config = ConfigDict(extra="forbid")

    current_days: int = Field(ge=0)
    longest_days: int = Field(ge=0)


class RepositoryInventory(BaseModel):
    """Current public repository inventory metrics across all configured owners."""

    model_config = ConfigDict(extra="forbid")

    owned_public_non_archived_repositories: int = Field(ge=0)
    total_public_repositories: int = Field(ge=0)
    archived_repositories: int = Field(ge=0)
    repositories_per_owner: dict[str, int] = Field(default_factory=dict)
    stars_received: int = Field(ge=0)
    forks_received: int = Field(ge=0)
    public_releases_past_year: int = Field(ge=0)
    detected_languages: int = Field(ge=0, default=0)


class MonthlyContribution(BaseModel):
    """Monthly contribution total for the trailing 12-month window."""

    model_config = ConfigDict(extra="forbid")

    year: int
    month: int
    count: int = Field(ge=0)


class RadarDimension(BaseModel):
    """One axis of the Engineering Signature radar chart (0–100 score)."""

    model_config = ConfigDict(extra="forbid")

    key: str
    label: str
    score: int = Field(ge=0, le=100)
    source_fields: list[str] = Field(default_factory=list)
    formula: str = ""
    unavailable: bool = False


class FeaturedRepository(BaseModel):
    """A deliberately configured featured repository."""

    model_config = ConfigDict(extra="forbid")

    owner: str
    name: str
    full_name: str
    description: str = ""
    primary_language: str = ""
    stars: int = Field(ge=0, default=0)
    forks: int = Field(ge=0, default=0)
    html_url: str = ""
    latest_release_tag: str = ""
    latest_release_date: str = ""
    missing: bool = False


class KnowledgeCategory(BaseModel):
    """One top-level Knowledge Atlas category for the starred-repo treemap."""

    model_config = ConfigDict(extra="forbid")

    key: str
    label: str
    count: int = Field(ge=0)
    percentage: int = Field(ge=0, le=100)


class VerifiedAchievement(BaseModel):
    """One explicitly verified GitHub achievement for public display."""

    model_config = ConfigDict(extra="forbid")

    key: str
    name: str
    tier: str | None = None
    description: str = ""
    profile_url: str = ""
    verified: bool


class StarredRepositoryTotals(BaseModel):
    """Authoritative starred-repository totals from GitHub."""

    model_config = ConfigDict(extra="forbid")

    total_starred: int = Field(ge=0)
    crawl_complete: bool = False
    crawl_pages: int = Field(ge=0, default=0)


class LanguageShare(BaseModel):
    """Compact display distribution for repository languages."""

    model_config = ConfigDict(extra="forbid")

    name: str
    percentage: int = Field(ge=0, le=100)
    bytes: int = Field(ge=0)


class DashboardStatus(BaseModel):
    """Display-safe provenance and freshness fields."""

    model_config = ConfigDict(extra="forbid")

    data_source: Literal["live", "cache", "fixture"]
    source_state: Literal["fresh", "cached", "failed-with-fallback", "static"]
    data_timestamp: str
    generation_timestamp: str
    is_stale: bool = False


class DashboardMethodology(BaseModel):
    """Human-readable metric definitions recorded in the snapshot."""

    model_config = ConfigDict(extra="forbid")

    trailing_window_days: int = Field(ge=1)
    window_start: str
    window_end: str
    contribution_calendar_source: str
    contribution_type_source: str
    repository_inventory_source: str
    starred_repository_total_source: str = ""
    language_distribution_source: str
    release_count_source: str
    current_streak_definition: str
    longest_streak_definition: str
    language_rounding_policy: str
    multi_owner_scope: str = ""
    personal_activity_scope: str = ""


class GitHubDashboardSnapshot(BaseModel):
    """Normalized, public-safe AFQC dashboard snapshot for SVG rendering."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "2.0"
    title: str = "GitHub Engineering"
    username: str
    repository_owners: list[RepositoryOwnerConfig] = Field(default_factory=list)
    trailing_window_days: int = Field(ge=1)
    window_start: str
    window_end: str
    contribution_days: list[ContributionDay] = Field(default_factory=list)
    monthly_contributions: list[MonthlyContribution] = Field(default_factory=list)
    contribution_breakdown: ContributionBreakdown
    streaks: StreakMetrics
    most_active_month: str = ""
    average_contributions_per_active_day: float = Field(ge=0.0, default=0.0)
    active_contribution_days: int = Field(ge=0, default=0)
    repositories_contributed_to: int = Field(ge=0, default=0)
    repository_inventory: RepositoryInventory
    languages: list[LanguageShare] = Field(default_factory=list)
    radar_dimensions: list[RadarDimension] = Field(default_factory=list)
    featured_repositories: list[FeaturedRepository] = Field(default_factory=list)
    knowledge_categories: list[KnowledgeCategory] = Field(default_factory=list)
    starred_repository_totals: StarredRepositoryTotals | None = None
    verified_achievements: list[VerifiedAchievement] = Field(default_factory=list)
    nonfatal_diagnostics: list[str] = Field(default_factory=list)
    status: DashboardStatus
    methodology: DashboardMethodology
