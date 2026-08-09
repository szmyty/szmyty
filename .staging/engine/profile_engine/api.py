"""
FastAPI application for the Profile Engine.

This API provides REST endpoints for the React dashboard to fetch profile data.
"""

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(
    title="Profile Engine API",
    description="REST API for GitHub Profile Dashboard",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS for React dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data from file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary containing JSON data
        
    Raises:
        HTTPException: If file not found or invalid JSON
    """
    path = Path(file_path)
    
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: {file_path}"
        )
    
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON in file {file_path}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading file {file_path}: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Profile Engine API",
        "version": "1.0.0",
        "endpoints": {
            "weather": "/api/weather",
            "developer": "/api/developer",
            "oura": "/api/oura",
            "mood": "/api/mood",
            "soundcloud": "/api/soundcloud",
            "quote": "/api/quote",
            "theme": "/api/theme",
            "docs": "/api/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "profile-engine-api"}


@app.get("/api/weather")
async def get_weather():
    """Get current weather data."""
    data = load_json_file("weather/weather.json")
    return JSONResponse(content=data)


@app.get("/api/developer")
async def get_developer():
    """Get GitHub developer statistics."""
    data = load_json_file("developer/stats.json")
    return JSONResponse(content=data)


@app.get("/api/oura")
async def get_oura():
    """Get Oura health metrics."""
    data = load_json_file("oura/metrics.json")
    return JSONResponse(content=data)


@app.get("/api/mood")
async def get_mood():
    """Get Oura mood data."""
    try:
        data = load_json_file("oura/mood.json")
        return JSONResponse(content=data)
    except HTTPException as e:
        if e.status_code == 404:
            # Return default mood if file doesn't exist
            return JSONResponse(content={
                "mood_name": "Unknown",
                "mood_score": 50,
                "date": None
            })
        raise


@app.get("/api/soundcloud")
async def get_soundcloud():
    """Get SoundCloud track data."""
    data = load_json_file("assets/metadata.json")
    return JSONResponse(content=data)


@app.get("/api/quote")
async def get_quote():
    """Get quote of the day."""
    data = load_json_file("quotes/quote.json")
    return JSONResponse(content=data)


@app.get("/api/theme")
async def get_theme():
    """Get theme configuration."""
    data = load_json_file("config/theme.json")
    return JSONResponse(content=data)


@app.get("/api/location")
async def get_location():
    """Get location data."""
    data = load_json_file("location/location.json")
    return JSONResponse(content=data)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
