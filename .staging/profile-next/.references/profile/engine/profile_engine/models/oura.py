"""Pydantic models for Oura health data."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class OuraHealthMetrics(BaseModel):
    """Oura health metrics model."""
    date: date
    readiness_score: Optional[int] = Field(default=None, ge=0, le=100)
    sleep_score: Optional[int] = Field(default=None, ge=0, le=100)
    activity_score: Optional[int] = Field(default=None, ge=0, le=100)
    
    # Sleep metrics
    total_sleep: Optional[int] = Field(default=None, ge=0, description="Total sleep in minutes")
    deep_sleep: Optional[int] = Field(default=None, ge=0, description="Deep sleep in minutes")
    rem_sleep: Optional[int] = Field(default=None, ge=0, description="REM sleep in minutes")
    light_sleep: Optional[int] = Field(default=None, ge=0, description="Light sleep in minutes")
    
    # Activity metrics
    steps: Optional[int] = Field(default=None, ge=0)
    calories: Optional[int] = Field(default=None, ge=0)
    active_calories: Optional[int] = Field(default=None, ge=0)
    
    # Heart rate
    resting_heart_rate: Optional[int] = Field(default=None, ge=0)
    average_hrv: Optional[int] = Field(default=None, ge=0, description="Heart rate variability")
    
    # Body temperature
    temperature_delta: Optional[float] = Field(default=None, description="Temperature deviation")
    
    timestamp: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-01",
                "readiness_score": 85,
                "sleep_score": 82,
                "activity_score": 78,
                "total_sleep": 450,
                "deep_sleep": 90,
                "rem_sleep": 120,
                "light_sleep": 240,
                "steps": 8500,
                "calories": 2200,
                "active_calories": 450,
                "resting_heart_rate": 58,
                "average_hrv": 65,
                "temperature_delta": 0.2,
                "timestamp": "2024-01-01T08:00:00Z"
            }
        }


class OuraMood(BaseModel):
    """Oura mood tracking model."""
    date: date
    mood_name: str
    mood_score: int = Field(ge=0, le=100)
    mood_color: Optional[str] = None
    emoji: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-01",
                "mood_name": "Energized",
                "mood_score": 85,
                "mood_color": "#4CAF50",
                "emoji": "⚡",
                "timestamp": "2024-01-01T08:00:00Z"
            }
        }
