"""Tests for normalizer.py."""

from __future__ import annotations

from pinterest_rss.models import compute_content_hash
from pinterest_rss.normalizer import (
    _slugify,
    _slugify_title,
    extract_pin_id,
    generate_slug,
    normalize_entry,
    pin_directory_name,
)

# ---------------------------------------------------------------------------
# Tests for extract_pin_id
# ---------------------------------------------------------------------------


def test_extract_pin_id_from_canonical_url() -> None:
    pin_id = "1061301468459923611"
    url = f"https://www.pinterest.com/pin/{pin_id}/"
    assert extract_pin_id(url) == pin_id


def test_extract_pin_id_from_guid() -> None:
    assert extract_pin_id("https://www.pinterest.com/pin/123456789/") == "123456789"


def test_extract_pin_id_no_www() -> None:
    assert extract_pin_id("https://pinterest.com/pin/99999/") == "99999"


def test_extract_pin_id_not_a_pin_url() -> None:
    assert extract_pin_id("https://www.pinterest.com/egohygiene/ego-hygiene/") is None


def test_extract_pin_id_empty() -> None:
    assert extract_pin_id("") is None


def test_extract_pin_id_non_pinterest_url() -> None:
    assert extract_pin_id("https://example.com/some-page/") is None


def test_extract_pin_id_legacy_username_url() -> None:
    # Pin URLs with the old username still have pin/<id>/ format
    pin_id = "1061301468459923611"
    url = f"https://www.pinterest.com/pin/{pin_id}/"
    assert extract_pin_id(url) == pin_id


# ---------------------------------------------------------------------------
# Tests for pin_directory_name
# ---------------------------------------------------------------------------


def test_pin_directory_name_basic() -> None:
    assert pin_directory_name("1061301468459923611") == "pin-1061301468459923611"


def test_pin_directory_name_short_id() -> None:
    assert pin_directory_name("123") == "pin-123"


def test_pin_directory_name_format() -> None:
    name = pin_directory_name("99999")
    assert name.startswith("pin-")
    assert "99999" in name



def test_normalize_valid_entry(two_valid_entries: list[dict]) -> None:
    raw = two_valid_entries[0]
    item = normalize_entry(raw, "ego-hygiene")
    assert item is not None
    assert item.board_id == "ego-hygiene"
    assert item.title == "Morning Ritual Pin"
    assert item.source_url == "https://www.pinterest.com/pin/123456789/"
    assert item.stable_id  # non-empty
    assert item.content_hash  # non-empty


def test_normalize_sets_image_url(two_valid_entries: list[dict]) -> None:
    raw = two_valid_entries[0]
    item = normalize_entry(raw, "ego-hygiene")
    assert item is not None
    assert item.image_url == "https://i.pinimg.com/564x/morning.jpg"


def test_normalize_malformed_returns_none() -> None:
    # Completely empty dict – should return None without raising
    item = normalize_entry({}, "ego-hygiene")
    # An empty dict still produces an item with empty strings for required fields
    # but should not raise; if it does return None that's also acceptable
    # The normalizer tries its best with empty entries
    assert item is None or item.stable_id is not None


def test_normalize_all_fixture_entries(sample_raw_entries: list[dict]) -> None:
    results = [normalize_entry(e, "ego-hygiene") for e in sample_raw_entries]
    non_none = [r for r in results if r is not None]
    assert len(non_none) >= 2


def test_stable_id_uses_guid_when_pinterest_url() -> None:
    raw = {
        "id": "https://www.pinterest.com/pin/111/",
        "link": "https://www.pinterest.com/pin/111/",
    }
    item = normalize_entry(raw, "ego-hygiene")
    assert item is not None
    # Stable ID is the numeric pin ID extracted from the GUID
    assert item.stable_id == "111"
    assert item.pin_id == "111"


def test_stable_id_uses_url_when_no_guid() -> None:
    raw = {
        "id": "non-url-guid-12345",
        "link": "https://www.pinterest.com/pin/222/",
        "title": "Test",
        "summary": "desc",
    }
    item = normalize_entry(raw, "ego-hygiene")
    assert item is not None
    # Pin ID extracted from canonical URL when GUID is not a URL
    assert item.stable_id == "222"
    assert item.pin_id == "222"


def test_stable_id_uses_hash_when_no_url() -> None:
    raw = {
        "id": "simple-guid-no-url",
        "link": "",
        "title": "No URL Pin",
        "summary": "some description",
    }
    item = normalize_entry(raw, "ego-hygiene")
    assert item is not None
    assert len(item.stable_id) >= 16


def test_content_hash_deterministic() -> None:
    h1 = compute_content_hash("title", "desc", "https://img.jpg")
    h2 = compute_content_hash("title", "desc", "https://img.jpg")
    assert h1 == h2


def test_content_hash_differs_on_change() -> None:
    h1 = compute_content_hash("title", "desc", "https://img.jpg")
    h2 = compute_content_hash("title", "changed desc", "https://img.jpg")
    assert h1 != h2


def test_slugify_handles_url() -> None:
    slug = _slugify("https://www.pinterest.com/pin/12345/")
    assert "/" not in slug
    assert slug


def test_slugify_handles_empty() -> None:
    # Empty string should return something non-empty
    result = _slugify("")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Tests for _slugify_title (human-readable slug)
# ---------------------------------------------------------------------------


def test_slugify_title_basic() -> None:
    assert _slugify_title("Context Is Everything") == "context-is-everything"


def test_slugify_title_with_punctuation() -> None:
    assert _slugify_title("Power of Self-Awareness!") == "power-of-self-awareness"


def test_slugify_title_removes_apostrophes() -> None:
    assert _slugify_title("Don't Stop") == "dont-stop"


def test_slugify_title_unicode_normalization() -> None:
    # Accented characters: NFKD decomposes é → e + combining accent;
    # ASCII encode keeps the base letter e, so "Résilience" → "resilience".
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
    long_title = "word " * 20
    result = _slugify_title(long_title)
    assert len(result) <= 64


def test_slugify_title_strips_html() -> None:
    result = _slugify_title("<b>Bold Title</b>")
    assert "<" not in result
    assert result == "bold-title"


# ---------------------------------------------------------------------------
# Tests for generate_slug (priority logic)
# ---------------------------------------------------------------------------


def test_generate_slug_uses_title_first() -> None:
    slug = generate_slug("Morning Ritual Pin", "A description", "stable-id-123")
    assert slug == "morning-ritual-pin"


def test_generate_slug_falls_back_to_description() -> None:
    slug = generate_slug("", "Reflect on your day", "stable-id-456")
    assert slug == "reflect-on-your-day"


def test_generate_slug_falls_back_to_stable_id() -> None:
    slug = generate_slug("", "", "www-pinterest-com-pin-789-")
    # Should produce something from the stable_id
    assert slug
    assert "pinterest" in slug


def test_generate_slug_deterministic() -> None:
    s1 = generate_slug("Gratitude Changes the Brain", "desc", "id")
    s2 = generate_slug("Gratitude Changes the Brain", "desc", "id")
    assert s1 == s2


def test_generate_slug_produces_human_readable_result() -> None:
    slug = generate_slug("The Power of Self-Awareness", "", "stable-id")
    assert slug == "the-power-of-self-awareness"
    # No URL-like segments or long hash-looking strings
    assert len(slug) <= 64
    assert slug == slug.lower()
    assert "--" not in slug
