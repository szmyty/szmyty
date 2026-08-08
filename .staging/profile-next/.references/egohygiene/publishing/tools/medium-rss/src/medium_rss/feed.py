"""RSS feed fetching and parsing with Medium namespace support."""

from __future__ import annotations

from typing import Any

import feedparser
import httpx
import structlog

log = structlog.get_logger(__name__)

_DEFAULT_TIMEOUT = 30.0
_USER_AGENT = "EgoHygiene-MediumRSS/0.1 (+https://github.com/egohygiene/egohygiene)"

# Medium RSS feeds use these XML namespaces.
# feedparser automatically registers them, but we document them here for clarity.
# xmlns:content="http://purl.org/rss/1.0/modules/content/"  → content:encoded
# xmlns:dc="http://purl.org/dc/elements/1.1/"               → dc:creator
# xmlns:atom="http://www.w3.org/2005/Atom"                  → atom:updated


def fetch_feed(url: str, timeout: float = _DEFAULT_TIMEOUT) -> list[dict[str, Any]]:
    """Fetch a Medium RSS feed URL and return a list of raw entry dicts.

    Raises ``httpx.HTTPError`` on network-level failures.
    Raises ``ValueError`` when the feed cannot be parsed.
    """
    log.debug("feed.fetch.start", url=url)
    content = _download_feed(url, timeout)
    entries = _parse_feed(content, url)
    log.debug("feed.fetch.complete", url=url, entry_count=len(entries))
    return entries


def _download_feed(url: str, timeout: float) -> bytes:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": _USER_AGENT})
        response.raise_for_status()
        log.debug(
            "feed.download.complete",
            url=url,
            status_code=response.status_code,
            content_length=len(response.content),
        )
        return response.content


def _parse_feed(content: bytes, source_url: str) -> list[dict[str, Any]]:
    parsed = feedparser.parse(content)

    if parsed.get("bozo") and not parsed.get("entries"):
        exc = parsed.get("bozo_exception")
        raise ValueError(
            f"Feed could not be parsed from {source_url}: {exc}"
        )

    entries: list[dict[str, Any]] = []
    for entry in parsed.get("entries", []):
        raw = dict(entry)
        # feedparser maps content:encoded to entry.content[0].value when the
        # content module is registered; expose it under a predictable key.
        if "content_html" not in raw:
            content_list = raw.get("content", [])
            if content_list and isinstance(content_list, list):
                raw["content_html"] = content_list[0].get("value", "")
            else:
                raw["content_html"] = ""
        entries.append(raw)

    log.debug("feed.parse.complete", source_url=source_url, entry_count=len(entries))
    return entries
