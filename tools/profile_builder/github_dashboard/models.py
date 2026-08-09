"""Normalized public-safe models for the GitHub engineering dashboard."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    """Current public repository inventory metrics."""

    model_config = ConfigDict(extra="forbid")

    owned_public_non_archived_repositories: int = Field(ge=0)
    stars_received: int = Field(ge=0)
    public_releases_past_year: int = Field(ge=0)


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
    language_distribution_source: str
    release_count_source: str
    current_streak_definition: str
    longest_streak_definition: str
    language_rounding_policy: str


class GitHubDashboardSnapshot(BaseModel):
    """Normalized, public-safe dashboard snapshot for SVG rendering."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    title: str = "GitHub Engineering"
    username: str
    trailing_window_days: int = Field(ge=1)
    window_start: str
    window_end: str
    contribution_days: list[ContributionDay] = Field(default_factory=list)
    contribution_breakdown: ContributionBreakdown
    streaks: StreakMetrics
    repository_inventory: RepositoryInventory
    languages: list[LanguageShare] = Field(default_factory=list)
    status: DashboardStatus
    methodology: DashboardMethodology
