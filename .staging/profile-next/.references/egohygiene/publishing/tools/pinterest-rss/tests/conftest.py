"""Shared fixtures and helpers for the pinterest_rss test suite."""

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
    return [dict(e) for e in parsed.entries]


@pytest.fixture()
def two_valid_entries(sample_raw_entries: list[dict]) -> list[dict]:
    """Return just the two well-formed entries from the fixture."""
    return [e for e in sample_raw_entries if e.get("link")]
