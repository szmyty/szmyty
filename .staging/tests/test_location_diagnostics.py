#!/usr/bin/env python3
"""
Unit tests for location card generation diagnostic features.

This test suite validates that the location card generation scripts
properly detect and report failures with actionable error messages.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from lib.utils import try_load_json


class TestLocationCardDiagnostics:
    """Tests for location card generation diagnostic features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_metadata(self, path: str, **kwargs) -> str:
        """Create a test metadata JSON file."""
        metadata = {
            "location": kwargs.get("location", "San Francisco, CA"),
            "display_name": kwargs.get("display_name", "San Francisco, California, United States"),
            "coordinates": kwargs.get("coordinates", {"lat": 37.7749, "lon": -122.4194}),
            "map_path": kwargs.get("map_path", "location/location-map.png"),
            "updated_at": kwargs.get("updated_at", "2024-12-03T04:00:00Z")
        }
        
        with open(path, 'w') as f:
            json.dump(metadata, f)
        
        return path

    def create_test_map_image(self, path: str, size=(600, 400)) -> str:
        """Create a test map image."""
        img = Image.new('RGB', size, color='lightblue')
        img.save(path)
        return path

    def test_metadata_file_not_found(self):
        """Test that missing metadata file produces actionable error."""
        nonexistent = os.path.join(self.test_dir, "nonexistent.json")
        map_path = os.path.join(self.test_dir, "map.png")
        output_path = os.path.join(self.test_dir, "card.svg")
        
        self.create_test_map_image(map_path)
        
        result = subprocess.run(
            ["python", str(self.scripts_dir / "generate-location-card.py"),
             nonexistent, map_path, output_path],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "❌ FAILURE: Cannot read location metadata" in result.stderr
        assert "not found" in result.stderr.lower()
        assert nonexistent in result.stderr

    def test_invalid_json_metadata(self):
        """Test that invalid JSON in metadata file produces actionable error."""
        bad_json = os.path.join(self.test_dir, "bad.json")
        map_path = os.path.join(self.test_dir, "map.png")
        output_path = os.path.join(self.test_dir, "card.svg")
        
        with open(bad_json, 'w') as f:
            f.write("not valid json{")
        
        self.create_test_map_image(map_path)
        
        result = subprocess.run(
            ["python", str(self.scripts_dir / "generate-location-card.py"),
             bad_json, map_path, output_path],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "❌ FAILURE: Cannot read location metadata" in result.stderr
        assert "Invalid JSON" in result.stderr

    def test_missing_location_field(self):
        """Test that missing location field produces actionable error."""
        metadata_path = os.path.join(self.test_dir, "metadata.json")
        map_path = os.path.join(self.test_dir, "map.png")
        output_path = os.path.join(self.test_dir, "card.svg")
        
        # Create metadata without location field
        with open(metadata_path, 'w') as f:
            json.dump({"coordinates": {"lat": 37.7749, "lon": -122.4194}}, f)
        
        self.create_test_map_image(map_path)
        
        result = subprocess.run(
            ["python", str(self.scripts_dir / "generate-location-card.py"),
             metadata_path, map_path, output_path],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "❌ FAILURE: Missing 'location' field" in result.stderr

    def test_missing_coordinates(self):
        """Test that missing coordinates produce actionable error."""
        metadata_path = os.path.join(self.test_dir, "metadata.json")
        map_path = os.path.join(self.test_dir, "map.png")
        output_path = os.path.join(self.test_dir, "card.svg")
        
        # Create metadata without coordinates
        with open(metadata_path, 'w') as f:
            json.dump({"location": "San Francisco"}, f)
        
        self.create_test_map_image(map_path)
        
        result = subprocess.run(
            ["python", str(self.scripts_dir / "generate-location-card.py"),
             metadata_path, map_path, output_path],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "❌ FAILURE: Missing coordinates" in result.stderr

    def test_map_file_not_found(self):
        """Test that missing map file produces actionable error."""
        metadata_path = os.path.join(self.test_dir, "metadata.json")
        nonexistent_map = os.path.join(self.test_dir, "nonexistent.png")
        output_path = os.path.join(self.test_dir, "card.svg")
        
        self.create_test_metadata(metadata_path)
        
        result = subprocess.run(
            ["python", str(self.scripts_dir / "generate-location-card.py"),
             metadata_path, nonexistent_map, output_path],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "❌ FAILURE: Map image not found" in result.stderr
        assert "map download may have failed" in result.stderr.lower()
        assert "debug_map_response.txt" in result.stderr

    def test_successful_card_generation_with_diagnostics(self):
        """Test that successful generation includes diagnostic info."""
        metadata_path = os.path.join(self.test_dir, "metadata.json")
        map_path = os.path.join(self.test_dir, "map.png")
        output_path = os.path.join(self.test_dir, "card.svg")
        
        self.create_test_metadata(metadata_path)
        self.create_test_map_image(map_path)
        
        result = subprocess.run(
            ["python", str(self.scripts_dir / "generate-location-card.py"),
             metadata_path, map_path, output_path],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "✅ Generated location SVG card" in result.stderr
        assert "Card size:" in result.stderr
        assert "Base64 image size:" in result.stderr
        assert os.path.exists(output_path)
        
        # Validate SVG content
        with open(output_path, 'r') as f:
            svg_content = f.read()
            assert svg_content.startswith('<svg')
            assert 'data:image/png;base64,' in svg_content

    def test_empty_map_file_detection(self):
        """Test that empty map file produces actionable error."""
        metadata_path = os.path.join(self.test_dir, "metadata.json")
        empty_map = os.path.join(self.test_dir, "empty.png")
        output_path = os.path.join(self.test_dir, "card.svg")
        
        self.create_test_metadata(metadata_path)
        
        # Create empty file
        Path(empty_map).touch()
        
        result = subprocess.run(
            ["python", str(self.scripts_dir / "generate-location-card.py"),
             metadata_path, empty_map, output_path],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "❌ FAILURE" in result.stderr


class TestUtilsFunctions:
    """Tests for utility functions used in location card generation."""

    def test_try_load_json_with_valid_file(self):
        """Test try_load_json with valid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name
        
        try:
            data, error = try_load_json(temp_path, "Test file")
            assert error is None
            assert data == {"test": "data"}
        finally:
            os.unlink(temp_path)

    def test_try_load_json_with_missing_file(self):
        """Test try_load_json with missing file."""
        data, error = try_load_json("/nonexistent/file.json", "Test file")
        assert data is None
        assert error is not None
        assert "not found" in error.lower()

    def test_try_load_json_with_invalid_json(self):
        """Test try_load_json with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json{")
            temp_path = f.name
        
        try:
            data, error = try_load_json(temp_path, "Test file")
            assert data is None
            assert error is not None
            assert "Invalid JSON" in error
        finally:
            os.unlink(temp_path)
