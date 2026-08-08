#!/usr/bin/env python3
"""
Unit tests for scripts/lib/utils.py utility functions.
"""

import pytest
import sys
import os
import tempfile
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from lib.utils import (
    escape_xml,
    safe_get,
    safe_value,
    generate_sparkline_path,
    fallback_exists,
)


class TestEscapeXml:
    """Tests for escape_xml function."""

    def test_escape_ampersand(self):
        """Test ampersand escaping."""
        assert escape_xml("Tom & Jerry") == "Tom &amp; Jerry"

    def test_escape_less_than(self):
        """Test less-than sign escaping."""
        assert escape_xml("a < b") == "a &lt; b"

    def test_escape_greater_than(self):
        """Test greater-than sign escaping."""
        assert escape_xml("a > b") == "a &gt; b"

    def test_escape_double_quote(self):
        """Test double quote escaping."""
        assert escape_xml('Say "hello"') == "Say &quot;hello&quot;"

    def test_escape_single_quote(self):
        """Test single quote escaping."""
        assert escape_xml("It's fine") == "It&#39;s fine"

    def test_escape_all_special_chars(self):
        """Test escaping all special characters at once."""
        result = escape_xml('<tag attr="val" foo=\'bar\'>&data</tag>')
        expected = "&lt;tag attr=&quot;val&quot; foo=&#39;bar&#39;&gt;&amp;data&lt;/tag&gt;"
        assert result == expected

    def test_escape_empty_string(self):
        """Test empty string returns empty string."""
        assert escape_xml("") == ""

    def test_escape_none_returns_empty(self):
        """Test None input returns empty string."""
        assert escape_xml(None) == ""

    def test_escape_no_special_chars(self):
        """Test string without special chars is unchanged."""
        assert escape_xml("Hello World") == "Hello World"

    def test_escape_numeric_input(self):
        """Test numeric input is converted to string."""
        assert escape_xml(42) == "42"


class TestSafeGet:
    """Tests for safe_get function."""

    def test_single_key_exists(self):
        """Test getting a value with a single key that exists."""
        data = {"name": "Alice"}
        assert safe_get(data, "name") == "Alice"

    def test_single_key_missing(self):
        """Test getting a value with a single key that doesn't exist."""
        data = {"name": "Alice"}
        assert safe_get(data, "age") is None

    def test_single_key_missing_with_default(self):
        """Test getting a value with default when key doesn't exist."""
        data = {"name": "Alice"}
        assert safe_get(data, "age", default=25) == 25

    def test_nested_key_exists(self):
        """Test getting a nested value that exists."""
        data = {"user": {"profile": {"name": "Bob"}}}
        assert safe_get(data, "user", "profile", "name") == "Bob"

    def test_nested_key_missing(self):
        """Test getting a nested value when intermediate key is missing."""
        data = {"user": {"profile": {"name": "Bob"}}}
        assert safe_get(data, "user", "settings", "theme") is None

    def test_nested_key_missing_with_default(self):
        """Test getting a nested value with default when key is missing."""
        data = {"user": {"profile": {"name": "Bob"}}}
        assert safe_get(data, "user", "settings", "theme", default="dark") == "dark"

    def test_deeply_nested_key(self):
        """Test getting a deeply nested value."""
        data = {"a": {"b": {"c": {"d": {"e": 42}}}}}
        assert safe_get(data, "a", "b", "c", "d", "e") == 42

    def test_non_dict_intermediate_value(self):
        """Test when intermediate value is not a dict."""
        data = {"user": "not_a_dict"}
        assert safe_get(data, "user", "name") is None

    def test_none_value_returns_default(self):
        """Test that None value returns the default."""
        data = {"value": None}
        assert safe_get(data, "value", default="default") == "default"

    def test_empty_dict(self):
        """Test safe_get on empty dictionary."""
        data = {}
        assert safe_get(data, "key") is None

    def test_zero_value_is_returned(self):
        """Test that zero value is returned (not treated as falsy)."""
        data = {"count": 0}
        assert safe_get(data, "count", default=10) == 0


class TestSafeValue:
    """Tests for safe_value function."""

    def test_value_present(self):
        """Test that a present value is returned."""
        assert safe_value(42) == "42"

    def test_value_none_returns_default(self):
        """Test that None returns default placeholder."""
        assert safe_value(None) == "—"

    def test_value_none_with_custom_default(self):
        """Test that None returns custom default."""
        assert safe_value(None, default="N/A") == "N/A"

    def test_value_with_suffix(self):
        """Test value with suffix appended."""
        assert safe_value(100, suffix="%") == "100%"

    def test_value_none_with_suffix(self):
        """Test None value ignores suffix."""
        assert safe_value(None, suffix="%") == "—"

    def test_string_value(self):
        """Test string value is returned."""
        assert safe_value("hello") == "hello"

    def test_float_value(self):
        """Test float value is returned."""
        assert safe_value(3.14) == "3.14"


class TestGenerateSparklinePath:
    """Tests for generate_sparkline_path SVG helper function."""

    def test_basic_sparkline(self):
        """Test basic sparkline generation."""
        values = [0, 50, 100, 50, 0]
        path = generate_sparkline_path(values, width=100, height=25)
        # Path should start with M and contain L for line segments
        assert path.startswith("M")
        assert "L" in path

    def test_empty_values(self):
        """Test sparkline with empty values returns flat line."""
        path = generate_sparkline_path([], width=100, height=25)
        # Should return a flat horizontal line in the middle
        assert "M0,12" in path or "M0,12.5" in path

    def test_single_value(self):
        """Test sparkline with single value returns flat line."""
        path = generate_sparkline_path([50], width=100, height=25)
        assert "M0,12" in path or "M0,12.5" in path

    def test_two_values(self):
        """Test sparkline with two values."""
        values = [0, 100]
        path = generate_sparkline_path(values, width=100, height=25)
        assert path.startswith("M")
        # First point at x=0, second at x=100
        assert "0.0," in path
        assert "100.0," in path

    def test_constant_values(self):
        """Test sparkline with all same values."""
        values = [50, 50, 50, 50]
        path = generate_sparkline_path(values, width=100, height=25)
        # All points should be at the same height (middle since val_range is 1)
        assert path.startswith("M")

    def test_values_with_none(self):
        """Test sparkline filters out None values."""
        values = [0, None, 50, None, 100]
        path = generate_sparkline_path(values, width=100, height=25)
        # Should work with the three non-None values
        assert path.startswith("M")
        assert "L" in path

    def test_all_none_values(self):
        """Test sparkline with all None values returns flat line."""
        values = [None, None, None]
        path = generate_sparkline_path([None, None, None], width=100, height=25)
        assert "M0,12" in path or "M0,12.5" in path

    def test_custom_dimensions(self):
        """Test sparkline with custom width and height."""
        values = [0, 100]
        path = generate_sparkline_path(values, width=200, height=50)
        # Second point should be at x=200
        assert "200.0," in path

    def test_sparkline_path_format(self):
        """Test sparkline path has correct SVG format."""
        values = [10, 20, 30]
        path = generate_sparkline_path(values, width=100, height=25)
        # Should be in format "M0.0,y L50.0,y L100.0,y"
        parts = path.split(" L")
        assert len(parts) == 3  # M + 2 L segments
        assert parts[0].startswith("M")


class TestFallbackExists:
    """Tests for fallback_exists function."""

    def test_nonexistent_file(self):
        """Test that nonexistent file returns False."""
        assert fallback_exists("/tmp/nonexistent_file.svg") is False

    def test_valid_svg_file(self):
        """Test that valid SVG file returns True."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>')
            temp_path = f.name
        
        try:
            assert fallback_exists(temp_path) is True
        finally:
            Path(temp_path).unlink()

    def test_invalid_svg_missing_closing_tag(self):
        """Test that SVG without closing tag returns False."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg"><rect/>')
            temp_path = f.name
        
        try:
            assert fallback_exists(temp_path) is False
        finally:
            Path(temp_path).unlink()

    def test_invalid_svg_missing_opening_tag(self):
        """Test that file without <svg> opening tag returns False."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write('<html><body>Not SVG</body></html>')
            temp_path = f.name
        
        try:
            assert fallback_exists(temp_path) is False
        finally:
            Path(temp_path).unlink()

    def test_empty_svg_file(self):
        """Test that empty SVG file returns False."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write('')
            temp_path = f.name
        
        try:
            assert fallback_exists(temp_path) is False
        finally:
            Path(temp_path).unlink()

    def test_png_file_returns_false(self):
        """Test that PNG file returns False (not an SVG)."""
        # Create a minimal PNG file (PNG magic bytes + minimal structure)
        png_data = (
            b'\x89PNG\r\n\x1a\n'  # PNG signature
            b'\x00\x00\x00\rIHDR'  # IHDR chunk
            b'\x00\x00\x00\x01\x00\x00\x00\x01'  # 1x1 image
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
            f.write(png_data)
            temp_path = f.name
        
        try:
            # Should return False because it's not an SVG file
            assert fallback_exists(temp_path) is False
        finally:
            Path(temp_path).unlink()

    def test_png_with_svg_extension(self):
        """Test that PNG with .svg extension returns False (binary content)."""
        # Create a PNG file but with .svg extension
        png_data = (
            b'\x89PNG\r\n\x1a\n'  # PNG signature
            b'\x00\x00\x00\rIHDR'
            b'\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        )
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.svg', delete=False) as f:
            f.write(png_data)
            temp_path = f.name
        
        try:
            # Should return False because read_text will fail or content won't start with <svg
            assert fallback_exists(temp_path) is False
        finally:
            Path(temp_path).unlink()

    def test_svg_with_whitespace(self):
        """Test that SVG with leading/trailing whitespace is handled correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write('\n  <svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>  \n')
            temp_path = f.name
        
        try:
            assert fallback_exists(temp_path) is True
        finally:
            Path(temp_path).unlink()

    def test_txt_file_with_svg_content(self):
        """Test that .txt file with SVG content returns False (wrong extension)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>')
            temp_path = f.name
        
        try:
            # Should return False because extension is not .svg
            assert fallback_exists(temp_path) is False
        finally:
            Path(temp_path).unlink()

    def test_svg_uppercase_extension(self):
        """Test that .SVG uppercase extension works."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.SVG', delete=False) as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>')
            temp_path = f.name
        
        try:
            assert fallback_exists(temp_path) is True
        finally:
            Path(temp_path).unlink()
