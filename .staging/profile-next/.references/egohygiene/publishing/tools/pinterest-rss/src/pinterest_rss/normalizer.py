"""Normalizer – converts raw feedparser entries into PinterestItem instances."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

import structlog

from pinterest_rss.models import PinterestItem, compute_content_hash

log = structlog.get_logger(__name__)

_PINTEREST_IMAGE_RE = re.compile(
    r'<img\s[^>]*src=["\']([^"\']+)["\']', re.IGNORECASE
)

# Matches Pinterest pin IDs in URLs of the form /.../pin/<numeric-id>/
_PINTEREST_PIN_ID_RE = re.compile(r'pinterest\.com/pin/(\d+)', re.IGNORECASE)


def extract_pin_id(url: str) -> str | None:
    """Extract the numeric Pinterest pin ID from a Pinterest URL or GUID.

    Examples::

        extract_pin_id("https://www.pinterest.com/pin/1061301468459923611/")
        # → "1061301468459923611"

        extract_pin_id("https://www.pinterest.com/pin/123/")
        # → "123"

        extract_pin_id("https://example.com/not-a-pin/")
        # → None

    Returns ``None`` when no pin ID can be extracted.
    """
    if not url:
        return None
    match = _PINTEREST_PIN_ID_RE.search(url)
    if match:
        return match.group(1)
    return None


def pin_directory_name(pin_id: str) -> str:
    """Return the canonical archive directory name for a Pinterest pin.

    The directory name is ``pin-<numeric-id>``.  This is the stable identity
    used for all new archives and migrations.

    Examples::

        pin_directory_name("1061301468459923611")
        # → "pin-1061301468459923611"
    """
    return f"pin-{pin_id}"


def normalize_entry(raw: dict[str, Any], board_id: str) -> PinterestItem | None:
    """Normalize a single raw feedparser entry dict.

    Returns ``None`` and logs a warning when the entry is too malformed to use.
    """
    try:
        return _normalize(raw, board_id)
    except Exception as exc:
        log.warning(
            "normalizer.entry_skipped",
            exc=str(exc),
            entry_id=raw.get("id") or raw.get("link") or "<unknown>",
        )
        return None


def _normalize(raw: dict[str, Any], board_id: str) -> PinterestItem:
    title = _clean_text(raw.get("title", ""))
    description = _extract_description(raw)
    source_url = _extract_source_url(raw)
    canonical_url = _extract_canonical_url(raw, source_url)
    guid = raw.get("id") or ""
    image_url = _extract_image_url(raw)
    pub_date = _extract_pub_date(raw)

    content_hash = compute_content_hash(title, description, image_url)
    stable_id, pin_id = _generate_stable_id(raw, canonical_url, content_hash)

    now = datetime.now(UTC)

    return PinterestItem(
        stable_id=stable_id,
        pin_id=pin_id,
        guid=guid,
        title=title,
        description=description,
        board_id=board_id,
        source_url=source_url,
        canonical_url=canonical_url,
        image_url=image_url,
        pub_date=pub_date,
        first_seen=now,
        last_updated=now,
        content_hash=content_hash,
        original_metadata=_safe_original(raw),
    )


def _generate_stable_id(
    raw: dict[str, Any], canonical_url: str, content_hash: str
) -> tuple[str, str | None]:
    """Generate a stable identifier and return ``(stable_id, pin_id)``.

    Priority:
    1. Pinterest pin ID extracted from the RSS GUID (canonical identity).
    2. Pinterest pin ID extracted from the canonical URL.
    3. Slugified GUID URL (for non-Pinterest or legacy items).
    4. Slugified canonical URL.
    5. Content hash prefix (last resort).
    """
    guid = raw.get("id") or ""

    # Try GUID first (most reliable for Pinterest items)
    if guid and _looks_like_url(guid):
        pin_id = extract_pin_id(guid)
        if pin_id:
            return pin_id, pin_id
        return _slugify(guid), None

    # Try canonical URL
    if canonical_url:
        pin_id = extract_pin_id(canonical_url)
        if pin_id:
            return pin_id, pin_id
        return _slugify(canonical_url), None

    return content_hash[:16], None


def generate_slug(title: str, description: str, stable_id: str) -> str:
    """Generate a human-readable presentation slug from item fields.

    Priority:
    1. Title (preferred – most descriptive)
    2. Description (fallback when title is empty)
    3. Stable ID (last resort – always non-empty)

    The returned slug is deterministic and safe for use as a directory name.
    Collision handling (appending ``-2``, ``-3``, …) is the caller's responsibility.
    """
    for source in (title, description):
        if source and source.strip():
            slug = _slugify_title(source)
            if slug:
                return slug
    return _slugify_title(stable_id) or stable_id[:64]


def _slugify_title(value: str) -> str:
    """Convert a plain-text title into a human-readable slug.

    Normalization steps:
    - Normalize unicode (NFKD) and transliterate to ASCII
    - Strip any residual HTML tags
    - Lowercase
    - Remove characters that are not alphanumeric, spaces, or hyphens
    - Replace one or more spaces with a single hyphen
    - Collapse repeated hyphens
    - Strip leading / trailing hyphens
    - Limit to 64 characters
    """
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"<[^>]+>", "", value)
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    value = value.strip("-")
    return value[:64]


def _slugify(value: str) -> str:
    """Convert a URL or arbitrary string into a safe directory-name slug.

    When the value reduces to an empty string after transformation, the original
    raw bytes are hashed to produce a deterministic 16-character fallback.
    """
    original = value
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"https?://", "", value)
    value = re.sub(r"[^\w\-]", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    value = value.strip("-").lower()
    if not value:
        # Hash the original (pre-transformation) bytes so the fallback is
        # stable across repeated calls with the same input.
        value = hashlib.sha256(original.encode()).hexdigest()[:16]
    return value[:128]


def _looks_like_url(value: str) -> bool:
    """Return True when *value* appears to be an absolute HTTP(S) URL."""
    return value.startswith("http://") or value.startswith("https://")


def _clean_text(raw: str) -> str:
    return re.sub(r"\s+", " ", raw).strip()


def _extract_description(raw: dict[str, Any]) -> str:
    summary = raw.get("summary") or raw.get("description") or ""
    return _strip_html(_clean_text(summary))


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def _extract_source_url(raw: dict[str, Any]) -> str:
    return raw.get("link") or raw.get("id") or ""


def _extract_canonical_url(raw: dict[str, Any], fallback: str) -> str:
    for link in raw.get("links", []):
        if link.get("rel") == "alternate":
            return link.get("href", fallback)
    return fallback


def _extract_image_url(raw: dict[str, Any]) -> str | None:
    # Try media content first (common in RSS 2.0 + media: namespace)
    for media in raw.get("media_content", []):
        url = media.get("url")
        if url:
            return url

    # Try enclosures
    for enclosure in raw.get("enclosures", []):
        url = enclosure.get("href") or enclosure.get("url")
        if url:
            return url

    # Fallback: parse from HTML summary
    summary = raw.get("summary") or raw.get("description") or ""
    match = _PINTEREST_IMAGE_RE.search(summary)
    if match:
        return match.group(1)

    return None


def _extract_pub_date(raw: dict[str, Any]) -> datetime | None:
    published = raw.get("published") or raw.get("updated")
    if not published:
        struct = raw.get("published_parsed") or raw.get("updated_parsed")
        if struct:
            try:
                return datetime(*struct[:6], tzinfo=UTC)
            except Exception:
                pass
        return None
    try:
        return parsedate_to_datetime(published)
    except Exception:
        pass
    try:
        return datetime.fromisoformat(published)
    except Exception:
        return None


def _safe_original(raw: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-safe subset of the raw feedparser entry."""
    safe: dict[str, Any] = {}
    for key, value in raw.items():
        try:
            import json
            json.dumps(value)
            safe[key] = value
        except (TypeError, ValueError):
            safe[key] = str(value)
    return safe
