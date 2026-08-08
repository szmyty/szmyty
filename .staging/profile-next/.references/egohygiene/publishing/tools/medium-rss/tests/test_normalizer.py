"""Tests for normalizer.py."""

from __future__ import annotations

import pytest

from medium_rss.models import compute_content_hash
from medium_rss.normalizer import (
    extract_medium_post_id,
    generate_slug,
    normalize_entry,
    _slugify_title,
)

_FEED_URL = "https://articles.egohygiene.io/feed"


# ---------------------------------------------------------------------------
# normalize_entry
# ---------------------------------------------------------------------------


def test_normalize_valid_entry(two_valid_entries: list[dict]) -> None:
    raw = two_valid_entries[0]
    article = normalize_entry(raw, _FEED_URL)
    assert article is not None
    assert article.feed_url == _FEED_URL
    assert article.title == "Mood Colors Your Reality"
    assert article.id  # non-empty stable ID
    assert article.content_hash  # non-empty


def test_normalize_extracts_medium_post_id(two_valid_entries: list[dict]) -> None:
    raw = two_valid_entries[0]
    article = normalize_entry(raw, _FEED_URL)
    assert article is not None
    assert article.id == "f284b362c931"


def test_normalize_extracts_second_post_id(two_valid_entries: list[dict]) -> None:
    raw = two_valid_entries[1]
    article = normalize_entry(raw, _FEED_URL)
    assert article is not None
    assert article.id == "a1b2c3d4e5f6"


def test_normalize_extracts_author(two_valid_entries: list[dict]) -> None:
    raw = two_valid_entries[0]
    article = normalize_entry(raw, _FEED_URL)
    assert article is not None
    assert article.author == "szmyty"


def test_normalize_extracts_categories(two_valid_entries: list[dict]) -> None:
    raw = two_valid_entries[0]
    article = normalize_entry(raw, _FEED_URL)
    assert article is not None
    assert "mental-health" in article.categories
    assert "psychology" in article.categories
    assert "philosophy" in article.categories


def test_normalize_extracts_published_at(two_valid_entries: list[dict]) -> None:
    raw = two_valid_entries[0]
    article = normalize_entry(raw, _FEED_URL)
    assert article is not None
    assert article.published_at is not None
    assert article.published_at.year == 2026
    assert article.published_at.month == 4
    assert article.published_at.day == 6


def test_normalize_extracts_content_html(two_valid_entries: list[dict]) -> None:
    raw = two_valid_entries[0]
    article = normalize_entry(raw, _FEED_URL)
    assert article is not None
    assert "<h2>" in article.content_html


def test_normalize_all_fixture_entries(sample_raw_entries: list[dict]) -> None:
    results = [normalize_entry(e, _FEED_URL) for e in sample_raw_entries]
    non_none = [r for r in results if r is not None]
    assert len(non_none) >= 2


def test_normalize_sets_guid(two_valid_entries: list[dict]) -> None:
    raw = two_valid_entries[0]
    article = normalize_entry(raw, _FEED_URL)
    assert article is not None
    assert article.guid == "https://medium.com/p/f284b362c931"


# ---------------------------------------------------------------------------
# extract_medium_post_id
# ---------------------------------------------------------------------------


def test_extract_post_id_from_medium_guid() -> None:
    assert extract_medium_post_id("https://medium.com/p/f284b362c931") == "f284b362c931"


def test_extract_post_id_from_url_suffix() -> None:
    assert extract_medium_post_id(
        "https://szmyty.medium.com/mood-colors-your-reality-f284b362c931"
    ) == "f284b362c931"


def test_extract_post_id_returns_empty_when_absent() -> None:
    assert extract_medium_post_id("https://example.com/no-id-here") == ""


def test_extract_post_id_returns_empty_for_empty_string() -> None:
    assert extract_medium_post_id("") == ""


# ---------------------------------------------------------------------------
# slug generation
# ---------------------------------------------------------------------------


def test_generate_slug_from_title() -> None:
    assert generate_slug("Mood Colors Your Reality", "f284b362c931") == "mood-colors-your-reality"


def test_generate_slug_falls_back_to_stable_id() -> None:
    slug = generate_slug("", "f284b362c931")
    assert slug
    assert "f284" in slug


def test_generate_slug_deterministic() -> None:
    s1 = generate_slug("Same Input Different Experience", "a1b2c3d4e5f6")
    s2 = generate_slug("Same Input Different Experience", "a1b2c3d4e5f6")
    assert s1 == s2


def test_slugify_title_basic() -> None:
    assert _slugify_title("Context Is Everything") == "context-is-everything"


def test_slugify_title_with_punctuation() -> None:
    assert _slugify_title("Power of Self-Awareness!") == "power-of-self-awareness"


def test_slugify_title_removes_apostrophes() -> None:
    assert _slugify_title("Don't Stop") == "dont-stop"


def test_slugify_title_unicode_normalization() -> None:
    result = _slugify_title("Résilience et Force")
    assert result == "resilience-et-force"


def test_slugify_title_collapses_spaces() -> None:
    assert _slugify_title("too   many   spaces") == "too-many-spaces"


def test_slugify_title_strips_trailing_hyphens() -> None:
    result = _slugify_title("ends with punctuation!!")
    assert not result.startswith("-")
    assert not result.endswith("-")


def test_slugify_title_empty_string() -> None:
    assert _slugify_title("") == ""


def test_slugify_title_max_length() -> None:
    long_title = "word " * 25
    result = _slugify_title(long_title)
    assert len(result) <= 80


# ---------------------------------------------------------------------------
# content hash
# ---------------------------------------------------------------------------


def test_compute_content_hash_deterministic() -> None:
    h1 = compute_content_hash("<p>Hello</p>")
    h2 = compute_content_hash("<p>Hello</p>")
    assert h1 == h2


def test_compute_content_hash_differs_on_change() -> None:
    h1 = compute_content_hash("<p>Hello</p>")
    h2 = compute_content_hash("<p>World</p>")
    assert h1 != h2
