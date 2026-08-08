"""Weather API client for fetching weather data."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from profile_engine.models.weather import WeatherData


class WeatherClient:
    """Client for fetching weather data."""
    
    def __init__(self):
        """Initialize Weather client."""
        pass
    
    def fetch_weather(self, output_path: Optional[Path] = None) -> WeatherData:
        """
        Fetch current weather data.
        
        Args:
            output_path: Optional path to save JSON output
            
        Returns:
            WeatherData model with current weather
        """
        # For now, use the existing script as a wrapper
        # TODO: Refactor to use httpx directly
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "fetch-weather.sh"
        
        if output_path is None:
            output_path = Path("weather") / "weather.json"
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Run the existing script
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to fetch weather data: {result.stderr}")
        
        # Load and validate the output
        if output_path.exists():
            with open(output_path, "r") as f:
                data = json.load(f)
            return WeatherData(**data)
        
        raise RuntimeError("Weather data file not created")
