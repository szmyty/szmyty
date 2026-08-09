"""Pydantic models for quote data."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Quote(BaseModel):
    """Quote of the day model."""
    text: str = Field(min_length=1, max_length=500)
    author: str
    category: Optional[str] = None
    source: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The only way to do great work is to love what you do.",
                "author": "Steve Jobs",
                "category": "motivation",
                "source": "inspirational-quotes",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
