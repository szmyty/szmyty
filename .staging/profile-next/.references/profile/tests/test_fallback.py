#!/usr/bin/env python3
"""
Unit tests for fallback functionality in scripts/lib/utils.py.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from lib.utils import (
    try_load_json,
    try_validate_json,
    try_load_and_validate_json,
    fallback_exists,
    log_fallback_used,
    generate_card_with_fallback,
    handle_error_with_fallback,
)


class TestTryLoadJson:
    """Tests for try_load_json function."""

    def test_load_valid_json(self, tmp_path):
        """Test loading a valid JSON file."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"name": "test", "value": 42}')

        data, error = try_load_json(str(json_file), "Test file")

        assert error is None
        assert data == {"name": "test", "value": 42}

    def test_load_missing_file(self, tmp_path):
        """Test loading a non-existent file."""
        json_file = tmp_path / "missing.json"

        data, error = try_load_json(str(json_file), "Test file")

        assert data is None
        assert "not found" in error
        assert "missing.json" in error

    def test_load_invalid_json(self, tmp_path):
        """Test loading a file with invalid JSON."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid json }")

        data, error = try_load_json(str(json_file), "Test file")

        assert data is None
        assert "Invalid JSON" in error

    def test_load_empty_file(self, tmp_path):
        """Test loading an empty file."""
        json_file = tmp_path / "empty.json"
        json_file.write_text("")

        data, error = try_load_json(str(json_file), "Test file")

        assert data is None
        assert "Invalid JSON" in error


class TestTryValidateJson:
    """Tests for try_validate_json function."""

    def test_validation_with_valid_data(self):
        """Test validation passes with valid data."""
        # Use weather schema which exists in the repo
        data = {
            "location": "Test City",
            "current": {
                "temperature": 20,
                "weathercode": 0,
                "condition": "Clear",
                "emoji": "☀️",
            },
            "daily": {"temperature_max": 25, "temperature_min": 15},
            "updated_at": "2025-01-01T00:00:00Z",
        }

        error = try_validate_json(data, "weather", "Weather data")

        # Should pass validation (no error)
        assert error is None

    def test_validation_with_invalid_data(self):
        """Test validation fails with invalid data."""
        # Missing required fields
        data = {"invalid": "data"}

        error = try_validate_json(data, "weather", "Weather data")

        # Should fail validation
        assert error is not None
        assert "validation failed" in error


class TestTryLoadAndValidateJson:
    """Tests for try_load_and_validate_json function."""

    def test_load_and_validate_success(self, tmp_path):
        """Test successful load and validation."""
        json_file = tmp_path / "weather.json"
        data = {
            "location": "Test City",
            "current": {
                "temperature": 20,
                "condition": "Clear",
                "emoji": "☀️",
                "weathercode": 0,
                "is_day": 1,
                "wind_speed": 10,
            },
            "daily": {
                "temperature_max": 25,
                "temperature_min": 15,
                "sunrise": "2025-01-01T07:00:00",
                "sunset": "2025-01-01T17:00:00",
            },
            "updated_at": "2025-01-01T00:00:00Z",
        }
        json_file.write_text(json.dumps(data))

        result, error = try_load_and_validate_json(
            str(json_file), "weather", "Weather data"
        )

        assert error is None
        assert result == data

    def test_load_fails(self, tmp_path):
        """Test when file doesn't exist."""
        json_file = tmp_path / "missing.json"

        result, error = try_load_and_validate_json(
            str(json_file), "weather", "Weather data"
        )

        assert result is None
        assert "not found" in error

    def test_validation_fails(self, tmp_path):
        """Test when validation fails."""
        json_file = tmp_path / "invalid_weather.json"
        json_file.write_text('{"invalid": "data"}')

        result, error = try_load_and_validate_json(
            str(json_file), "weather", "Weather data"
        )

        assert result is None
        assert "validation failed" in error


class TestFallbackExists:
    """Tests for fallback_exists function."""

    def test_valid_svg_exists(self, tmp_path):
        """Test detection of a valid SVG file."""
        svg_file = tmp_path / "card.svg"
        svg_file.write_text('<svg xmlns="http://www.w3.org/2000/svg">content</svg>')

        assert fallback_exists(str(svg_file)) is True

    def test_file_not_exists(self, tmp_path):
        """Test when file doesn't exist."""
        svg_file = tmp_path / "missing.svg"

        assert fallback_exists(str(svg_file)) is False

    def test_empty_file(self, tmp_path):
        """Test when file is empty."""
        svg_file = tmp_path / "empty.svg"
        svg_file.write_text("")

        assert fallback_exists(str(svg_file)) is False

    def test_non_svg_content(self, tmp_path):
        """Test when file doesn't contain valid SVG."""
        svg_file = tmp_path / "not_svg.svg"
        svg_file.write_text("<html><body>Not SVG</body></html>")

        assert fallback_exists(str(svg_file)) is False

    def test_incomplete_svg(self, tmp_path):
        """Test when SVG is incomplete (missing closing tag)."""
        svg_file = tmp_path / "incomplete.svg"
        svg_file.write_text('<svg xmlns="http://www.w3.org/2000/svg">content')

        assert fallback_exists(str(svg_file)) is False

    def test_svg_with_whitespace(self, tmp_path):
        """Test SVG with leading/trailing whitespace."""
        svg_file = tmp_path / "whitespace.svg"
        svg_file.write_text('  \n<svg xmlns="http://www.w3.org/2000/svg">content</svg>\n  ')

        assert fallback_exists(str(svg_file)) is True


class TestLogFallbackUsed:
    """Tests for log_fallback_used function."""

    def test_log_output(self, capsys):
        """Test that fallback logs are written to stderr."""
        log_fallback_used("weather", "Test error", "/path/to/fallback.svg")

        captured = capsys.readouterr()
        assert "FALLBACK" in captured.err
        assert "weather" in captured.err
        assert "Test error" in captured.err
        assert "/path/to/fallback.svg" in captured.err


class TestHandleErrorWithFallback:
    """Tests for handle_error_with_fallback function."""

    def test_returns_true_when_fallback_exists(self, capsys):
        """Test that function returns True when fallback is available."""
        result = handle_error_with_fallback(
            "test", "Test error", "/path/to/fallback.svg", has_fallback=True
        )
        assert result is True
        captured = capsys.readouterr()
        assert "FALLBACK" in captured.err

    def test_exits_when_no_fallback(self):
        """Test that function exits with code 1 when no fallback exists."""
        with pytest.raises(SystemExit) as exc_info:
            handle_error_with_fallback(
                "test", "Test error", "/path/to/missing.svg", has_fallback=False
            )
        assert exc_info.value.code == 1


class TestGenerateCardWithFallback:
    """Tests for generate_card_with_fallback function."""

    def test_successful_generation(self, tmp_path):
        """Test successful card generation."""
        json_file = tmp_path / "data.json"
        output_file = tmp_path / "output.svg"

        json_file.write_text('{"title": "Test"}')

        def generator(data):
            return f'<svg><text>{data["title"]}</text></svg>'

        result = generate_card_with_fallback(
            card_type="test",
            output_path=str(output_file),
            json_path=str(json_file),
            schema_name=None,  # Skip validation
            generator_func=generator,
        )

        assert result is True
        assert output_file.exists()
        assert "Test" in output_file.read_text()

    def test_fallback_on_missing_json(self, tmp_path):
        """Test fallback when JSON file is missing."""
        output_file = tmp_path / "output.svg"
        output_file.write_text('<svg><text>Old content</text></svg>')

        def generator(data):
            return "<svg>new</svg>"

        result = generate_card_with_fallback(
            card_type="test",
            output_path=str(output_file),
            json_path=str(tmp_path / "missing.json"),
            schema_name=None,
            generator_func=generator,
        )

        assert result is False
        # Original content should be preserved
        assert "Old content" in output_file.read_text()

    def test_fallback_on_invalid_json(self, tmp_path):
        """Test fallback when JSON is invalid."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid }")

        output_file = tmp_path / "output.svg"
        output_file.write_text('<svg><text>Old content</text></svg>')

        def generator(data):
            return "<svg>new</svg>"

        result = generate_card_with_fallback(
            card_type="test",
            output_path=str(output_file),
            json_path=str(json_file),
            schema_name=None,
            generator_func=generator,
        )

        assert result is False
        assert "Old content" in output_file.read_text()

    def test_fallback_on_generator_exception(self, tmp_path):
        """Test fallback when generator raises an exception."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"title": "Test"}')

        output_file = tmp_path / "output.svg"
        output_file.write_text('<svg><text>Old content</text></svg>')

        def failing_generator(data):
            raise ValueError("Something went wrong")

        result = generate_card_with_fallback(
            card_type="test",
            output_path=str(output_file),
            json_path=str(json_file),
            schema_name=None,
            generator_func=failing_generator,
        )

        assert result is False
        assert "Old content" in output_file.read_text()

    def test_fallback_on_invalid_svg(self, tmp_path):
        """Test fallback when generator returns invalid SVG."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"title": "Test"}')

        output_file = tmp_path / "output.svg"
        output_file.write_text('<svg><text>Old content</text></svg>')

        def bad_generator(data):
            return "not svg content"

        result = generate_card_with_fallback(
            card_type="test",
            output_path=str(output_file),
            json_path=str(json_file),
            schema_name=None,
            generator_func=bad_generator,
        )

        assert result is False
        assert "Old content" in output_file.read_text()

    def test_exit_when_no_fallback(self, tmp_path):
        """Test that system exits when no fallback is available."""
        json_file = tmp_path / "missing.json"
        output_file = tmp_path / "output.svg"

        def generator(data):
            return "<svg>content</svg>"

        with pytest.raises(SystemExit) as exc_info:
            generate_card_with_fallback(
                card_type="test",
                output_path=str(output_file),
                json_path=str(json_file),
                schema_name=None,
                generator_func=generator,
            )

        assert exc_info.value.code == 1

    def test_creates_parent_directory(self, tmp_path):
        """Test that parent directories are created if needed."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"title": "Test"}')

        output_file = tmp_path / "subdir" / "nested" / "output.svg"

        def generator(data):
            return "<svg>content</svg>"

        result = generate_card_with_fallback(
            card_type="test",
            output_path=str(output_file),
            json_path=str(json_file),
            schema_name=None,
            generator_func=generator,
        )

        assert result is True
        assert output_file.exists()
