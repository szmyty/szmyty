"""Pydantic models for weather data."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WeatherCondition(BaseModel):
    """Current weather condition."""
    description: str
    icon: str
    code: int


class WeatherData(BaseModel):
    """Weather data model."""
    location: str
    temperature: float = Field(description="Temperature in Celsius")
    feels_like: Optional[float] = Field(default=None, description="Feels like temperature")
    humidity: int = Field(ge=0, le=100, description="Humidity percentage")
    wind_speed: float = Field(ge=0, description="Wind speed in km/h")
    wind_direction: Optional[int] = Field(default=None, ge=0, le=360)
    condition: WeatherCondition
    timestamp: datetime
    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    timezone: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": "San Francisco, CA",
                "temperature": 18.5,
                "feels_like": 17.2,
                "humidity": 65,
                "wind_speed": 15.5,
                "wind_direction": 270,
                "condition": {
                    "description": "Partly cloudy",
                    "icon": "partly-cloudy-day",
                    "code": 1003
                },
                "timestamp": "2024-01-01T12:00:00Z",
                "sunrise": "07:00:00",
                "sunset": "18:00:00",
                "timezone": "America/Los_Angeles"
            }
        }
