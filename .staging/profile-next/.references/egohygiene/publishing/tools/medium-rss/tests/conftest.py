"""Shared fixtures and helpers for the medium_rss test suite."""

from __future__ import annotations

from pathlib import Path

import feedparser
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def sample_rss_path() -> Path:
    return FIXTURES_DIR / "sample.rss"


@pytest.fixture()
def sample_raw_entries(sample_rss_path: Path) -> list[dict]:
    parsed = feedparser.parse(sample_rss_path.read_bytes())
    entries = []
    for entry in parsed.entries:
        raw = dict(entry)
        content_list = raw.get("content", [])
        if content_list and isinstance(content_list, list):
            raw["content_html"] = content_list[0].get("value", "")
        else:
            raw["content_html"] = ""
        entries.append(raw)
    return entries


@pytest.fixture()
def two_valid_entries(sample_raw_entries: list[dict]) -> list[dict]:
    """Return the two well-formed entries from the fixture."""
    return [e for e in sample_raw_entries if e.get("link")]
