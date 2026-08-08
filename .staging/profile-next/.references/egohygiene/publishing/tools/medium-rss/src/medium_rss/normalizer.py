"""Normalizer – converts raw feedparser entries into MediumArticle instances."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

import structlog

from medium_rss.models import MediumArticle, compute_content_hash

log = structlog.get_logger(__name__)

# Pattern to extract the stable Medium post ID from a GUID or URL.
# Example: https://medium.com/p/f284b362c931  →  f284b362c931
_MEDIUM_POST_ID_RE = re.compile(r"[/-]([a-f0-9]{12})(?:[/?#]|$)")


def normalize_entry(raw: dict[str, Any], feed_url: str) -> MediumArticle | None:
    """Normalize a single raw feedparser entry dict into a MediumArticle.

    Returns ``None`` and logs a warning when the entry is too malformed to use.
    """
    try:
        return _normalize(raw, feed_url)
    except Exception as exc:
        log.warning(
            "normalizer.entry_skipped",
            exc=str(exc),
            entry_id=raw.get("id") or raw.get("link") or "<unknown>",
        )
        return None


def _normalize(raw: dict[str, Any], feed_url: str) -> MediumArticle:
    title = _clean_text(raw.get("title", ""))
    author = _extract_author(raw)
    guid = raw.get("id") or ""
    source_url = raw.get("link") or guid or ""
    canonical_url = _extract_canonical_url(raw, source_url)
    categories = _extract_categories(raw)
    published_at = _extract_published_at(raw)
    updated_at = _extract_updated_at(raw)
    content_html = raw.get("content_html", "")

    post_id = extract_medium_post_id(guid) or extract_medium_post_id(source_url)
    if not post_id:
        # Deterministic fallback from canonical URL then content hash
        post_id = _derive_stable_id(canonical_url or source_url, content_html)

    content_hash = compute_content_hash(content_html)

    now = datetime.now(timezone.utc)

    return MediumArticle(
        id=post_id,
        slug="",  # assigned by sync layer after collision handling
        title=title,
        author=author,
        source_url=source_url,
        guid=guid,
        canonical_url=canonical_url,
        published_at=published_at,
        updated_at=updated_at,
        categories=categories,
        content_html=content_html,
        content_hash=content_hash,
        feed_url=feed_url,
        first_seen=now,
        last_synced=now,
    )


def extract_medium_post_id(value: str) -> str:
    """Extract the stable 12-character hex Medium post ID from a URL or GUID.

    Returns an empty string when no ID is found.
    """
    if not value:
        return ""
    match = _MEDIUM_POST_ID_RE.search(value)
    if match:
        return match.group(1)
    return ""


def generate_slug(title: str, stable_id: str) -> str:
    """Generate a human-readable presentation slug from the article title.

    Falls back to the stable ID when the title is empty.
    The returned slug is deterministic and safe for use as a directory name.
    Collision handling (appending ``-2``, ``-3``, …) is the caller's responsibility.
    """
    if title and title.strip():
        slug = _slugify_title(title)
        if slug:
            return slug
    return _slugify_title(stable_id) or stable_id[:64]


def _slugify_title(value: str) -> str:
    """Convert a plain-text title into a human-readable slug.

    Normalization steps:
    - Normalize unicode (NFKD) and transliterate to ASCII
    - Strip residual HTML tags
    - Lowercase
    - Remove characters that are not alphanumeric, spaces, or hyphens
    - Replace one or more spaces with a single hyphen
    - Collapse repeated hyphens
    - Strip leading / trailing hyphens
    - Limit to 80 characters
    """
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"<[^>]+>", "", value)
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    value = value.strip("-")
    return value[:80]


def _derive_stable_id(url: str, content_html: str) -> str:
    """Produce a deterministic stable ID when no Medium post ID is extractable."""
    if url:
        digest = hashlib.sha256(url.encode()).hexdigest()
    else:
        digest = hashlib.sha256(content_html.encode("utf-8")).hexdigest()
    return digest[:16]


def _clean_text(raw: str) -> str:
    return re.sub(r"\s+", " ", raw).strip()


def _extract_author(raw: dict[str, Any]) -> str:
    # dc:creator maps to raw["author"] in feedparser
    author = raw.get("author") or ""
    # Also check authors list
    if not author:
        authors = raw.get("authors", [])
        if authors and isinstance(authors, list):
            author = authors[0].get("name", "") if isinstance(authors[0], dict) else ""
    return _clean_text(author)


def _extract_canonical_url(raw: dict[str, Any], fallback: str) -> str:
    for link in raw.get("links", []):
        if isinstance(link, dict) and link.get("rel") == "alternate":
            href = link.get("href", "")
            if href:
                return href
    return fallback


def _extract_categories(raw: dict[str, Any]) -> list[str]:
    tags = raw.get("tags", [])
    if not tags:
        return []
    categories: list[str] = []
    for tag in tags:
        if isinstance(tag, dict):
            term = tag.get("term") or tag.get("label") or ""
        else:
            term = str(tag)
        term = _clean_text(term)
        if term:
            categories.append(term)
    return categories


def _extract_published_at(raw: dict[str, Any]) -> datetime | None:
    return _parse_date_field(raw, "published", "published_parsed")


def _extract_updated_at(raw: dict[str, Any]) -> datetime | None:
    return _parse_date_field(raw, "updated", "updated_parsed")


def _parse_date_field(raw: dict[str, Any], str_key: str, struct_key: str) -> datetime | None:
    value = raw.get(str_key)
    if value:
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(str(value))
        except Exception:
            pass
        try:
            dt = datetime.fromisoformat(str(value))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            pass

    struct = raw.get(struct_key)
    if struct:
        try:
            return datetime(*struct[:6], tzinfo=timezone.utc)
        except Exception:
            pass

    return None
