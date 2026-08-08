#!/usr/bin/env python3
"""
Tests for quote card generation functionality.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_quote_card import generate_svg, wrap_text


class TestQuoteCard:
    """Tests for quote card generation."""

    def test_wrap_text_short(self):
        """Test that short text doesn't get wrapped unnecessarily."""
        text = "Short quote"
        lines = wrap_text(text, max_chars_per_line=55)
        assert len(lines) == 1
        assert lines[0] == "Short quote"

    def test_wrap_text_long(self):
        """Test that long text gets wrapped at word boundaries."""
        text = "This is a very long quote that should be wrapped into multiple lines for better readability"
        lines = wrap_text(text, max_chars_per_line=40)
        assert len(lines) > 1
        for line in lines:
            assert len(line) <= 50  # Allow some margin for word boundaries

    def test_wrap_text_exact_boundary(self):
        """Test text wrapping at exact character boundary."""
        text = "A" * 30 + " " + "B" * 30
        lines = wrap_text(text, max_chars_per_line=35)
        assert len(lines) == 2

    def test_generate_svg_basic(self):
        """Test SVG generation with basic quote data."""
        svg = generate_svg(
            text="Test quote",
            author="Test Author",
            source="local",
            fetched_at="2025-12-05T00:00:00Z",
        )
        
        assert svg.startswith("<svg")
        assert "Test quote" in svg
        assert "Test Author" in svg
        assert "Quote of the Day" in svg

    def test_generate_svg_with_category(self):
        """Test SVG generation with category."""
        svg = generate_svg(
            text="Test quote",
            author="Test Author",
            source="local",
            fetched_at="2025-12-05T00:00:00Z",
            category="wisdom",
        )
        
        assert "wisdom" in svg

    def test_generate_svg_long_quote(self):
        """Test SVG generation with long quote that needs wrapping."""
        long_text = "This is a very long quote that should be wrapped into multiple lines for better readability and proper display in the SVG card"
        svg = generate_svg(
            text=long_text,
            author="Test Author",
            source="local",
            fetched_at="2025-12-05T00:00:00Z",
        )
        
        # Should contain multiple text elements for wrapped lines
        assert svg.count("<text") > 5  # Header, multiple quote lines, author, footer

    def test_generate_svg_special_characters(self):
        """Test SVG generation with special XML characters."""
        svg = generate_svg(
            text='Test "quote" with <special> & characters',
            author="Test & Author",
            source="local",
            fetched_at="2025-12-05T00:00:00Z",
        )
        
        # Check that special characters are escaped
        # Double quotes should be escaped
        assert "&quot;" in svg or "&#34;" in svg
        # Less than should be escaped
        assert "&lt;" in svg
        # Ampersand should be escaped
        assert "&amp;" in svg

    def test_quote_json_structure(self):
        """Test that a valid quote JSON has required fields."""
        quote_file = Path(__file__).parent.parent / "quotes" / "quote.json"
        if quote_file.exists():
            with open(quote_file) as f:
                quote = json.load(f)
            
            # Check required fields
            assert "text" in quote
            assert "author" in quote
            assert "source" in quote
            assert "fetched_at" in quote
            
            # Check field types
            assert isinstance(quote["text"], str)
            assert isinstance(quote["author"], str)
            assert len(quote["text"]) > 0
            assert len(quote["author"]) > 0

    def test_local_quotes_database(self):
        """Test that local quotes database is valid."""
        quotes_file = Path(__file__).parent.parent / "data" / "quotes" / "quotes.json"
        assert quotes_file.exists(), "Local quotes database should exist"
        
        with open(quotes_file) as f:
            quotes = json.load(f)
        
        assert isinstance(quotes, list)
        assert len(quotes) > 0, "Quotes database should not be empty"
        
        # Check structure of each quote
        for quote in quotes:
            assert "text" in quote
            assert "author" in quote
            assert isinstance(quote["text"], str)
            assert isinstance(quote["author"], str)
            assert len(quote["text"]) > 0
            assert len(quote["author"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
