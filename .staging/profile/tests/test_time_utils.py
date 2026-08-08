#!/usr/bin/env python3
"""
Unit tests for time-related utility functions.
"""

import pytest
from datetime import datetime, timezone, timedelta
from scripts.lib.utils import format_time_since, is_data_stale


class TestFormatTimeSince:
    """Test suite for format_time_since function."""

    def test_just_now(self):
        """Test that very recent timestamps show 'just now'."""
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "just now"

    def test_30_seconds_ago(self):
        """Test that 30 seconds ago shows 'just now'."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(seconds=30)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "just now"

    def test_2_minutes_ago(self):
        """Test that 2 minutes ago shows '2m ago'."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(minutes=2)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "2m ago"

    def test_30_minutes_ago(self):
        """Test that 30 minutes ago shows '30m ago'."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(minutes=30)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "30m ago"

    def test_59_minutes_ago(self):
        """Test that 59 minutes ago shows '59m ago'."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(minutes=59)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "59m ago"

    def test_1_hour_ago(self):
        """Test that 1 hour ago shows '1h ago'."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "1h ago"

    def test_5_hours_ago(self):
        """Test that 5 hours ago shows '5h ago'."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=5)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "5h ago"

    def test_23_hours_ago(self):
        """Test that 23 hours ago shows '23h ago'."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=23)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "23h ago"

    def test_1_day_ago(self):
        """Test that 1 day ago shows '1d ago'."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=1)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "1d ago"

    def test_7_days_ago(self):
        """Test that 7 days ago shows '7d ago'."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=7)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "7d ago"

    def test_30_days_ago(self):
        """Test that 30 days ago shows '30d ago'."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=30)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = format_time_since(timestamp)
        assert result == "30d ago"

    def test_invalid_timestamp(self):
        """Test that invalid timestamps return 'unknown'."""
        result = format_time_since("invalid-timestamp")
        assert result == "unknown"

    def test_empty_timestamp(self):
        """Test that empty timestamps return 'unknown'."""
        result = format_time_since("")
        assert result == "unknown"

    def test_iso_format_with_plus_zero(self):
        """Test timestamp with +00:00 timezone format."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=2)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        result = format_time_since(timestamp)
        assert result == "2h ago"

    def test_iso_format_without_timezone(self):
        """Test timestamp without timezone (assumes UTC)."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=3)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%S")
        result = format_time_since(timestamp)
        assert result == "3h ago"


class TestIsDataStale:
    """Test suite for is_data_stale function."""

    def test_fresh_data_just_now(self):
        """Test that very recent data is not stale."""
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = is_data_stale(timestamp, stale_threshold_hours=24)
        assert result is False

    def test_fresh_data_1_hour_ago(self):
        """Test that 1 hour old data is not stale."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = is_data_stale(timestamp, stale_threshold_hours=24)
        assert result is False

    def test_fresh_data_12_hours_ago(self):
        """Test that 12 hour old data is not stale."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=12)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = is_data_stale(timestamp, stale_threshold_hours=24)
        assert result is False

    def test_fresh_data_23_hours_ago(self):
        """Test that 23 hour old data is not stale."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=23)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = is_data_stale(timestamp, stale_threshold_hours=24)
        assert result is False

    def test_stale_data_25_hours_ago(self):
        """Test that 25 hour old data is stale."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=25)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = is_data_stale(timestamp, stale_threshold_hours=24)
        assert result is True

    def test_stale_data_48_hours_ago(self):
        """Test that 48 hour old data is stale."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=48)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = is_data_stale(timestamp, stale_threshold_hours=24)
        assert result is True

    def test_stale_data_7_days_ago(self):
        """Test that 7 day old data is stale."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=7)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = is_data_stale(timestamp, stale_threshold_hours=24)
        assert result is True

    def test_custom_threshold_2_hours(self):
        """Test with custom threshold of 2 hours."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=3)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = is_data_stale(timestamp, stale_threshold_hours=2)
        assert result is True

    def test_custom_threshold_fresh(self):
        """Test with custom threshold - data is fresh."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = is_data_stale(timestamp, stale_threshold_hours=2)
        assert result is False

    def test_invalid_timestamp_returns_true(self):
        """Test that invalid timestamps are considered stale (safe default)."""
        result = is_data_stale("invalid-timestamp")
        assert result is True

    def test_empty_timestamp_returns_true(self):
        """Test that empty timestamps are considered stale (safe default)."""
        result = is_data_stale("")
        assert result is True

    def test_iso_format_with_plus_zero(self):
        """Test timestamp with +00:00 timezone format."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=30)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        result = is_data_stale(timestamp, stale_threshold_hours=24)
        assert result is True

    def test_iso_format_without_timezone(self):
        """Test timestamp without timezone (assumes UTC)."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=20)
        timestamp = past.strftime("%Y-%m-%dT%H:%M:%S")
        result = is_data_stale(timestamp, stale_threshold_hours=24)
        assert result is False
