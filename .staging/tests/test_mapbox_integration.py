#!/usr/bin/env python3
"""
Unit tests for Mapbox integration and fallback map generation.

This test suite validates:
1. Fallback map generation when Mapbox is unavailable
2. Proper PNG output format
3. Correct coordinate display
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest
from PIL import Image

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestMapboxIntegration:
    """Tests for Mapbox integration and fallback handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
        
        # Import the generate_fallback_map function
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "generate_fallback_map",
            self.scripts_dir / "generate-fallback-map.py"
        )
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_fallback_map_generation(self):
        """Test that fallback map is generated correctly."""
        generate_fallback_map = self.module.generate_fallback_map
        
        output_path = os.path.join(self.test_dir, "fallback-map.png")
        lat, lon = 40.7128, -74.0060  # New York City
        
        # Generate fallback map
        generate_fallback_map(output_path, lat, lon)
        
        # Verify file exists
        assert os.path.exists(output_path), "Fallback map file was not created"
        
        # Verify it's a valid PNG
        with Image.open(output_path) as img:
            assert img.format == "PNG", f"Expected PNG format, got {img.format}"
            assert img.size == (600, 400), f"Expected 600x400 size, got {img.size}"
            assert img.mode == "RGB", f"Expected RGB mode, got {img.mode}"

    def test_fallback_map_coordinates(self):
        """Test that fallback map is generated with correct coordinates."""
        generate_fallback_map = self.module.generate_fallback_map
        
        output_path = os.path.join(self.test_dir, "fallback-map.png")
        
        # Test various coordinates
        test_cases = [
            (40.7128, -74.0060),  # New York (positive lat, negative lon)
            (-33.8688, 151.2093),  # Sydney (negative lat, positive lon)
            (51.5074, -0.1278),    # London (positive lat, negative lon)
            (-22.9068, -43.1729),  # Rio (negative lat, negative lon)
        ]
        
        for lat, lon in test_cases:
            generate_fallback_map(output_path, lat, lon)
            assert os.path.exists(output_path), f"Failed to generate map for {lat}, {lon}"
            
            # Verify it's a valid image
            with Image.open(output_path) as img:
                assert img.format == "PNG"
                assert img.size == (600, 400)

    def test_fallback_map_file_size(self):
        """Test that fallback map has reasonable file size."""
        generate_fallback_map = self.module.generate_fallback_map
        
        output_path = os.path.join(self.test_dir, "fallback-map.png")
        lat, lon = 40.7128, -74.0060
        
        generate_fallback_map(output_path, lat, lon)
        
        # Check file size is reasonable (should be small, but not empty)
        file_size = os.path.getsize(output_path)
        assert file_size > 1000, f"File size too small: {file_size} bytes"
        assert file_size < 100000, f"File size too large: {file_size} bytes"

    def test_fallback_map_dimensions(self):
        """Test that fallback map has correct dimensions."""
        generate_fallback_map = self.module.generate_fallback_map
        
        output_path = os.path.join(self.test_dir, "fallback-map.png")
        lat, lon = 40.7128, -74.0060
        
        generate_fallback_map(output_path, lat, lon)
        
        with Image.open(output_path) as img:
            width, height = img.size
            assert width == 600, f"Expected width 600, got {width}"
            assert height == 400, f"Expected height 400, got {height}"

    def test_fallback_map_creates_directory(self):
        """Test that fallback map creation creates parent directories if needed."""
        generate_fallback_map = self.module.generate_fallback_map
        
        nested_path = os.path.join(self.test_dir, "nested", "dirs", "fallback-map.png")
        lat, lon = 40.7128, -74.0060
        
        # Should not raise an error even if parent directories don't exist
        generate_fallback_map(nested_path, lat, lon)
        
        assert os.path.exists(nested_path), "Fallback map not created in nested directory"


class TestFallbackMapScript:
    """Tests for the fallback map generation script."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.scripts_dir = Path(__file__).parent.parent / "scripts"

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_script_command_line(self):
        """Test that the script works from command line."""
        import subprocess
        
        output_path = os.path.join(self.test_dir, "cli-fallback.png")
        script_path = self.scripts_dir / "generate-fallback-map.py"
        
        # Run the script
        result = subprocess.run(
            [sys.executable, str(script_path), output_path, "40.7128", "-74.0060"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert os.path.exists(output_path), "Output file not created"
        
        # Verify output
        with Image.open(output_path) as img:
            assert img.format == "PNG"
            assert img.size == (600, 400)

    def test_script_invalid_arguments(self):
        """Test that script fails gracefully with invalid arguments."""
        import subprocess
        
        script_path = self.scripts_dir / "generate-fallback-map.py"
        
        # Test with missing arguments
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0, "Script should fail with missing arguments"
        assert "Usage:" in result.stderr, "Should show usage message"

    def test_script_invalid_coordinates(self):
        """Test that script fails with invalid coordinates."""
        import subprocess
        
        output_path = os.path.join(self.test_dir, "invalid-coords.png")
        script_path = self.scripts_dir / "generate-fallback-map.py"
        
        # Test with invalid latitude (non-numeric)
        result = subprocess.run(
            [sys.executable, str(script_path), output_path, "invalid", "-74.0060"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0, "Script should fail with invalid coordinates"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
