"""Tests for feed.py – RSS parsing from fixture bytes."""

from __future__ import annotations

from pathlib import Path

import pytest

from pinterest_rss.feed import _parse_feed

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
    assert "https://www.pinterest.com/pin/123456789/" in links


def test_parse_feed_entry_has_media_content(sample_rss_path: Path) -> None:
    content = sample_rss_path.read_bytes()
    entries = _parse_feed(content, "file://sample.rss")
    media_entries = [e for e in entries if e.get("media_content")]
    assert len(media_entries) >= 1


def test_parse_feed_invalid_xml_raises() -> None:
    with pytest.raises(ValueError, match="Feed could not be parsed"):
        _parse_feed(b"this is not xml at all!!!", "file://bad.rss")
