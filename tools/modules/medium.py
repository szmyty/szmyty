"""Fetch and normalize public Medium RSS feed articles for the profile README.

Uses the documented public profile RSS feed only.  Strips unsafe HTML and
remote tracking markup.  Falls back to a static configured snapshot when
the feed is unavailable or Medium is not yet configured.

Reference:
  https://help.medium.com/hc/en-us/articles/214874118-Using-RSS-feeds-of-profiles-publications-and-topics
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any
from urllib import error, request
from xml.etree import ElementTree

import click
import yaml

from tools.profile_builder.models import MediumArticle, MediumConfig, MediumFeed

MODULE_NAME = "medium"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "profile" / "content" / "medium-config.yml"
DEFAULT_FIXTURE = REPO_ROOT / "profile" / "fixtures" / "medium.json"
DEFAULT_OUTPUT = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME / "cache.json"
MAX_ARTICLES = 5

# Patterns used to strip unsafe content from article summaries.
_TAG_RE = re.compile(r"<[^>]+>")
_TRACKING_RE = re.compile(r"https?://\S*utm_\S*", re.IGNORECASE)
_WHITESPACE_RE = re.compile(r"\s+")

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


class ProviderFailure(RuntimeError):
    """Raised when the Medium RSS feed cannot be fetched or parsed."""


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_config(path: Path = DEFAULT_CONFIG) -> MediumConfig:
    """Load the Medium configuration slot from YAML."""
    if not path.exists():
        return MediumConfig()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return MediumConfig()
    return MediumConfig.model_validate(raw)


def load_fixture(path: Path = DEFAULT_FIXTURE) -> MediumFeed:
    """Load static fallback fixture data."""
    return MediumFeed.model_validate_json(path.read_text(encoding="utf-8"))


def load_cached(output_path: Path) -> MediumFeed | None:
    """Load the last known-good cached output, if present."""
    if not output_path.exists():
        return None
    try:
        data = MediumFeed.model_validate_json(output_path.read_text(encoding="utf-8"))
        return data.model_copy(update={"data_source": "cache"})
    except Exception:  # noqa: BLE001
        return None


def _safe_summary(raw_html: str, max_chars: int = 280) -> str:
    """Strip HTML tags and tracking URLs, decode entities, and truncate."""
    text = _TRACKING_RE.sub("", raw_html)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "…"
    return text


def _parse_date(raw: str) -> str:
    """Normalise an RFC-2822 or ISO-8601 date string to YYYY-MM-DD."""
    raw = raw.strip()
    # Try ISO-8601 prefix first (handles 2024-01-15T... or 2024-01-15)
    m = re.match(r"(\d{4}-\d{2}-\d{2})", raw)
    if m:
        return m.group(1)
    # RFC-2822 e.g. "Mon, 15 Jan 2024 00:00:00 +0000"
    _MONTHS = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }
    m2 = re.search(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", raw)
    if m2:
        day, mon, year = m2.group(1), m2.group(2), m2.group(3)
        month = _MONTHS.get(mon[:3].capitalize(), "01")
        return f"{year}-{month}-{int(day):02d}"
    return raw[:10]


def fetch_live_feed(config: MediumConfig) -> MediumFeed:
    """Fetch and normalise the public Medium RSS feed for *config.username*."""
    feed_url = config.feed_url
    if not feed_url:
        raise ProviderFailure("Medium username is not configured.")

    headers = {"User-Agent": "szmyty-profile-builder/1.0"}
    req = request.Request(feed_url, headers=headers)
    try:
        with request.urlopen(req) as response:  # noqa: S310
            raw_xml = response.read()
    except error.HTTPError as exc:
        raise ProviderFailure(f"Medium RSS error: HTTP {exc.code}") from exc
    except error.URLError as exc:
        raise ProviderFailure(f"Medium RSS unavailable: {exc.reason}") from exc

    try:
        raw_str = raw_xml.decode("utf-8", errors="replace")
        # Guard against XML entity expansion attacks by rejecting DOCTYPE declarations.
        if "<!DOCTYPE" in raw_str.upper():
            raise ProviderFailure(
                "Medium RSS feed contains a DOCTYPE declaration; rejected."
            )
        root = ElementTree.fromstring(raw_str)  # noqa: S314  # DOCTYPE blocked above
    except ElementTree.ParseError as exc:
        raise ProviderFailure(f"Medium RSS parse error: {exc}") from exc

    channel = root.find("channel")
    items = channel.findall("item") if channel is not None else root.findall("item")

    articles: list[MediumArticle] = []
    for item in items:
        title_el = item.find("title")
        link_el = item.find("link")
        date_el = item.find("pubDate")
        desc_el = item.find("description")

        title = (title_el.text or "").strip() if title_el is not None else ""
        link = (link_el.text or "").strip() if link_el is not None else ""
        date_raw = (date_el.text or "").strip() if date_el is not None else ""
        desc_raw = (desc_el.text or "") if desc_el is not None else ""

        if not title or not link:
            continue

        # Strip tracking query parameters from the canonical URL.
        canonical = link.split("?")[0]

        articles.append(
            MediumArticle(
                title=title,
                canonical_url=canonical,
                published_date=_parse_date(date_raw) if date_raw else "",
                summary=_safe_summary(desc_raw) if desc_raw else None,
            )
        )
        if len(articles) >= MAX_ARTICLES:
            break

    profile_url = f"https://medium.com/@{config.username}" if config.username else None
    return MediumFeed(
        username=config.username,
        profile_url=profile_url,
        articles=articles,
        data_source="live",
    )


def build_medium(
    config_path: Path = DEFAULT_CONFIG,
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
) -> MediumFeed:
    """Build the Medium artifact, falling back through cache then fixture."""
    config = load_config(config_path)

    if not config.enabled or not config.username:
        data = MediumFeed(data_source="disabled")
        _write_json(output_path, data.model_dump(mode="json"))
        return data

    try:
        data = fetch_live_feed(config)
        _write_json(output_path, data.model_dump(mode="json"))
        return data
    except ProviderFailure:
        cached = load_cached(output_path)
        if cached is not None:
            return cached
        if fixture_path.exists():
            return load_fixture(fixture_path)
        return MediumFeed(data_source="disabled")


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_CONFIG),
    show_default=True,
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_OUTPUT),
    show_default=True,
)
@click.option(
    "--fixture",
    "fixture_path",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_FIXTURE),
    show_default=True,
)
def main(config_path: Path, output_path: Path, fixture_path: Path) -> None:
    """Write normalized Medium feed data to *output_path*."""
    data = build_medium(
        config_path=config_path,
        output_path=output_path,
        fixture_path=fixture_path,
    )
    click.echo(f"medium: wrote {output_path} ({data.data_source})")


if __name__ == "__main__":
    main()
