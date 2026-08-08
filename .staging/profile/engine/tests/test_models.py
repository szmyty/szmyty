"""Tests for Pydantic models."""

from datetime import date, datetime
from profile_engine.models.developer import DeveloperStats, CommitActivity
from profile_engine.models.weather import WeatherData, WeatherCondition
from profile_engine.models.oura import OuraHealthMetrics, OuraMood
from profile_engine.models.quote import Quote
from profile_engine.models.soundcloud import SoundCloudTrack


def test_developer_stats_model():
    """Test DeveloperStats model validation."""
    stats = DeveloperStats(
        username="testuser",
        name="Test User",
        public_repos=10,
        private_repos=5,
        total_repos=15,
        followers=100,
        following=50,
        total_stars=200,
        total_forks=50
    )
    assert stats.username == "testuser"
    assert stats.total_repos == 15
    assert stats.followers == 100


def test_weather_data_model():
    """Test WeatherData model validation."""
    weather = WeatherData(
        location="San Francisco",
        temperature=18.5,
        humidity=65,
        wind_speed=15.5,
        condition=WeatherCondition(
            description="Partly cloudy",
            icon="partly-cloudy-day",
            code=1003
        ),
        timestamp=datetime.now()
    )
    assert weather.location == "San Francisco"
    assert weather.temperature == 18.5
    assert weather.condition.description == "Partly cloudy"


def test_oura_health_metrics_model():
    """Test OuraHealthMetrics model validation."""
    metrics = OuraHealthMetrics(
        date=date.today(),
        readiness_score=85,
        sleep_score=82,
        activity_score=78,
        total_sleep=450,
        steps=8500
    )
    assert metrics.readiness_score == 85
    assert metrics.sleep_score == 82
    assert metrics.steps == 8500


def test_oura_mood_model():
    """Test OuraMood model validation."""
    mood = OuraMood(
        date=date.today(),
        mood_name="Energized",
        mood_score=85,
        emoji="⚡"
    )
    assert mood.mood_name == "Energized"
    assert mood.mood_score == 85


def test_quote_model():
    """Test Quote model validation."""
    quote = Quote(
        text="Test quote",
        author="Test Author",
        category="motivation"
    )
    assert quote.text == "Test quote"
    assert quote.author == "Test Author"


def test_soundcloud_track_model():
    """Test SoundCloudTrack model validation."""
    track = SoundCloudTrack(
        title="Test Track",
        artist="Test Artist",
        duration=180000,
        play_count=1500,
        permalink_url="https://soundcloud.com/test/track"
    )
    assert track.title == "Test Track"
    assert track.artist == "Test Artist"
    assert track.duration == 180000
