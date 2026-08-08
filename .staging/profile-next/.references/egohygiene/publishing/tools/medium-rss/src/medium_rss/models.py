"""Data models for the Medium RSS ingestion pipeline."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MediumArticle:
    """A normalized Medium article entry ready for storage."""

    # Stable canonical identity (Medium post ID, e.g. ``f284b362c931``).
    id: str
    # Human-readable slug derived from the article title.
    slug: str
    title: str
    author: str
    source_url: str
    guid: str
    canonical_url: str
    published_at: datetime | None
    updated_at: datetime | None
    categories: list[str]
    # Raw HTML from content:encoded.
    content_html: str
    # SHA-256 hex digest of the raw HTML content.
    content_hash: str
    feed_url: str
    first_seen: datetime
    last_synced: datetime
    # Paths to locally downloaded assets, keyed by asset URL.
    asset_paths: dict[str, str] = field(default_factory=dict)

    def to_metadata_dict(self) -> dict[str, Any]:
        """Return the metadata.json representation."""
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "author": self.author,
            "source_url": self.source_url,
            "guid": self.guid,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "categories": self.categories,
            "content_hash": f"sha256:{self.content_hash}",
        }


@dataclass
class ManifestEntry:
    """A lightweight record of one synced article stored in the manifest."""

    id: str
    slug: str
    canonical_url: str
    guid: str
    published_at: datetime | None
    updated_at: datetime | None
    content_hash: str
    feed_url: str
    first_seen: datetime
    last_synced: datetime
    sync_status: str = "ok"
    asset_paths: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "slug": self.slug,
            "canonical_url": self.canonical_url,
            "guid": self.guid,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "content_hash": self.content_hash,
            "feed_url": self.feed_url,
            "first_seen": self.first_seen.isoformat(),
            "last_synced": self.last_synced.isoformat(),
            "sync_status": self.sync_status,
            "asset_paths": self.asset_paths,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManifestEntry:
        return cls(
            id=data["id"],
            slug=data.get("slug", ""),
            canonical_url=data.get("canonical_url", ""),
            guid=data.get("guid", ""),
            published_at=_parse_dt(data.get("published_at")),
            updated_at=_parse_dt(data.get("updated_at")),
            content_hash=data["content_hash"],
            feed_url=data.get("feed_url", ""),
            first_seen=_parse_dt(data.get("first_seen")) or _utcnow(),
            last_synced=_parse_dt(data.get("last_synced")) or _utcnow(),
            sync_status=data.get("sync_status", "ok"),
            asset_paths=data.get("asset_paths", {}),
        )


@dataclass
class Manifest:
    """Top-level manifest for a Medium feed."""

    feed_url: str
    last_sync: datetime | None = None
    articles: dict[str, ManifestEntry] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "feed_url": self.feed_url,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "articles": {k: v.to_dict() for k, v in self.articles.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Manifest:
        articles = {
            k: ManifestEntry.from_dict(v)
            for k, v in data.get("articles", {}).items()
        }
        return cls(
            feed_url=data["feed_url"],
            last_sync=_parse_dt(data.get("last_sync")),
            articles=articles,
        )


@dataclass
class FeedConfig:
    """Configuration for a single Medium feed."""

    id: str
    url: str
    output: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeedConfig:
        return cls(
            id=data["id"],
            url=data["url"],
            output=data["output"],
        )


@dataclass
class SyncConfig:
    """Parsed configuration from config.yaml."""

    feeds: list[FeedConfig] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SyncConfig:
        feeds = [FeedConfig.from_dict(f) for f in data.get("feeds", [])]
        return cls(feeds=feeds)


def compute_content_hash(html_content: str) -> str:
    """Produce a deterministic SHA-256 content hash from the raw HTML."""
    return hashlib.sha256(html_content.encode("utf-8")).hexdigest()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
