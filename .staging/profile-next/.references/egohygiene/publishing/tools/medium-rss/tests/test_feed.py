"""Tests for feed.py – RSS parsing from fixture bytes."""

from __future__ import annotations

from pathlib import Path

import pytest

from medium_rss.feed import _parse_feed

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_feed_returns_entries(sample_rss_path: Path) -> None:
    content = sample_rss_path.read_bytes()
    entries = _parse_feed(content, "file://sample.rss")
    # fixture has 3 items (including the malformed one)
    assert len(entries) == 3


def test_parse_feed_entry_has_link(sample_rss_path: Path) -> None:
    content = sample_rss_path.read_bytes()
    entries = _parse_feed(content, "file://sample.rss")
    links = [e.get("link") for e in entries if e.get("link")]
    assert "https://szmyty.medium.com/mood-colors-your-reality-f284b362c931" in links


def test_parse_feed_exposes_content_html(sample_rss_path: Path) -> None:
    """content:encoded should be accessible as content_html."""
    content = sample_rss_path.read_bytes()
    entries = _parse_feed(content, "file://sample.rss")
    content_entries = [e for e in entries if e.get("content_html")]
    assert len(content_entries) >= 2
    assert "<h2>" in content_entries[0]["content_html"]


def test_parse_feed_invalid_xml_raises() -> None:
    with pytest.raises(ValueError, match="Feed could not be parsed"):
        _parse_feed(b"this is not xml at all!!!", "file://bad.rss")


def test_parse_feed_dc_creator_available(sample_rss_path: Path) -> None:
    """dc:creator should be present as author field."""
    content = sample_rss_path.read_bytes()
    entries = _parse_feed(content, "file://sample.rss")
    authors = [e.get("author") for e in entries if e.get("author")]
    assert any("szmyty" in (a or "") for a in authors)


def test_parse_feed_categories_present(sample_rss_path: Path) -> None:
    """Category tags should be parsed."""
    content = sample_rss_path.read_bytes()
    entries = _parse_feed(content, "file://sample.rss")
    tagged = [e for e in entries if e.get("tags")]
    assert len(tagged) >= 1
