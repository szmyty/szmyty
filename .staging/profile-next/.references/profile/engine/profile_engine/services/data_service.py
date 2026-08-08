"""
Data service layer for fetching and processing profile data.

This service layer sits between the CLI/API and the clients,
providing business logic, error handling, and data transformation.
"""

import logging
from pathlib import Path
from typing import Optional

from profile_engine.clients.github import GitHubClient
from profile_engine.clients.weather import WeatherClient
from profile_engine.clients.oura import OuraClient
from profile_engine.clients.soundcloud import SoundCloudClient
from profile_engine.clients.quote import QuoteClient
from profile_engine.models.developer import DeveloperStats
from profile_engine.models.weather import WeatherData
from profile_engine.models.oura import OuraHealthMetrics, OuraMood
from profile_engine.models.soundcloud import SoundCloudTrack
from profile_engine.models.quote import Quote

logger = logging.getLogger(__name__)


class DataService:
    """Service for fetching and managing profile data."""
    
    def __init__(self):
        """Initialize data service with clients."""
        self.github_client = GitHubClient()
        self.weather_client = WeatherClient()
        self.oura_client = OuraClient()
        self.soundcloud_client = SoundCloudClient()
        self.quote_client = QuoteClient()
    
    def fetch_developer_stats(
        self, 
        username: str,
        output_path: Optional[Path] = None
    ) -> DeveloperStats:
        """
        Fetch developer statistics with error handling.
        
        Args:
            username: GitHub username
            output_path: Optional custom output path
            
        Returns:
            DeveloperStats model
        """
        try:
            logger.info(f"Fetching developer statistics for {username}")
            stats = self.github_client.fetch_developer_stats(username, output_path)
            logger.info("Developer statistics fetched successfully")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch developer stats: {e}")
            raise
    
    def fetch_weather(self, output_path: Optional[Path] = None) -> WeatherData:
        """
        Fetch weather data with error handling.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            WeatherData model
        """
        try:
            logger.info("Fetching weather data")
            weather = self.weather_client.fetch_weather(output_path)
            logger.info("Weather data fetched successfully")
            return weather
        except Exception as e:
            logger.error(f"Failed to fetch weather data: {e}")
            raise
    
    def fetch_oura_metrics(
        self,
        output_path: Optional[Path] = None
    ) -> OuraHealthMetrics:
        """
        Fetch Oura health metrics with error handling.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            OuraHealthMetrics model
        """
        try:
            logger.info("Fetching Oura health metrics")
            metrics = self.oura_client.fetch_health_metrics(output_path)
            logger.info("Oura health metrics fetched successfully")
            return metrics
        except Exception as e:
            logger.error(f"Failed to fetch Oura metrics: {e}")
            raise
    
    def fetch_soundcloud_track(
        self,
        username: str,
        output_path: Optional[Path] = None
    ) -> SoundCloudTrack:
        """
        Fetch SoundCloud track with error handling.
        
        Args:
            username: SoundCloud username
            output_path: Optional custom output path
            
        Returns:
            SoundCloudTrack model
        """
        try:
            logger.info(f"Fetching SoundCloud track for {username}")
            track = self.soundcloud_client.fetch_track(username, output_path)
            logger.info("SoundCloud track fetched successfully")
            return track
        except Exception as e:
            logger.error(f"Failed to fetch SoundCloud track: {e}")
            raise
    
    def fetch_quote(self, output_path: Optional[Path] = None) -> Quote:
        """
        Fetch quote of the day with error handling.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Quote model
        """
        try:
            logger.info("Fetching quote of the day")
            quote = self.quote_client.fetch_quote(output_path)
            logger.info("Quote fetched successfully")
            return quote
        except Exception as e:
            logger.error(f"Failed to fetch quote: {e}")
            raise
