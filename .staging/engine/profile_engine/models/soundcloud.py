"""Pydantic models for SoundCloud data."""

from typing import Optional
from pydantic import BaseModel, Field


class SoundCloudTrack(BaseModel):
    """SoundCloud track model."""
    title: str
    artist: str
    duration: int = Field(ge=0, description="Duration in milliseconds")
    play_count: int = Field(default=0, ge=0)
    like_count: int = Field(default=0, ge=0)
    comment_count: int = Field(default=0, ge=0)
    genre: Optional[str] = None
    permalink_url: str
    artwork_url: Optional[str] = None
    waveform_url: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Amazing Track",
                "artist": "Cool Artist",
                "duration": 180000,
                "play_count": 1500,
                "like_count": 250,
                "comment_count": 45,
                "genre": "Electronic",
                "permalink_url": "https://soundcloud.com/artist/track",
                "artwork_url": "https://i1.sndcdn.com/artworks-000123456789-abcdef-large.jpg",
                "waveform_url": "https://wave.sndcdn.com/abc123.png",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
