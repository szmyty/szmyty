"""Pydantic models for developer statistics."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CommitActivity(BaseModel):
    """Commit activity statistics."""
    total_30_days: int = Field(default=0, ge=0)
    total_7_days: int = Field(default=0, ge=0)
    by_day: Optional[List[int]] = None


class LanguageStats(BaseModel):
    """Language statistics."""
    name: str
    bytes: int = Field(ge=0)
    percentage: float = Field(ge=0.0, le=100.0)


class Repository(BaseModel):
    """Repository information."""
    name: str
    description: Optional[str] = None
    stars: int = Field(default=0, ge=0)
    forks: int = Field(default=0, ge=0)
    language: Optional[str] = None
    commits: Optional[int] = Field(default=None, ge=0)


class DeveloperStats(BaseModel):
    """Developer statistics model."""
    username: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    
    # Repository stats
    public_repos: int = Field(default=0, ge=0)
    private_repos: int = Field(default=0, ge=0)
    total_repos: int = Field(default=0, ge=0)
    
    # Social stats
    followers: int = Field(default=0, ge=0)
    following: int = Field(default=0, ge=0)
    
    # Contribution stats
    total_stars: int = Field(default=0, ge=0)
    total_forks: int = Field(default=0, ge=0)
    commit_activity: Optional[CommitActivity] = None
    
    # Language breakdown
    languages: List[LanguageStats] = Field(default_factory=list)
    
    # Top repositories
    top_repos: List[Repository] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "octocat",
                "name": "The Octocat",
                "avatar_url": "https://github.com/octocat.png",
                "bio": "GitHub mascot",
                "public_repos": 8,
                "private_repos": 0,
                "total_repos": 8,
                "followers": 1000,
                "following": 10,
                "total_stars": 500,
                "total_forks": 100,
                "commit_activity": {
                    "total_30_days": 50,
                    "total_7_days": 10,
                    "by_day": [2, 5, 3, 8, 1, 6, 4]
                },
                "languages": [
                    {"name": "Python", "bytes": 50000, "percentage": 45.0},
                    {"name": "JavaScript", "bytes": 30000, "percentage": 27.0}
                ],
                "top_repos": [
                    {
                        "name": "Hello-World",
                        "description": "My first repository",
                        "stars": 100,
                        "forks": 20,
                        "language": "Python",
                        "commits": 50
                    }
                ]
            }
        }
