"""Data models for the Pinterest RSS ingestion pipeline."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class PinterestItem:
    """A normalized Pinterest feed item ready for storage."""

    stable_id: str
    title: str
    description: str
    board_id: str
    source_url: str
    canonical_url: str
    image_url: str | None
    pub_date: datetime | None
    first_seen: datetime
    last_updated: datetime
    content_hash: str
    original_metadata: dict[str, Any] = field(default_factory=dict)
    local_paths: dict[str, str] = field(default_factory=dict)
    # Human-readable presentation slug derived from the item title.
    # Set by the sync layer (after collision handling); empty until assigned.
    slug: str = ""
    # Numeric Pinterest pin ID (e.g. "1061301468459923611"); None for non-Pinterest items.
    pin_id: str | None = None
    # Raw RSS GUID value.
    guid: str = ""
    # Archive directory name (e.g. "pin-1061301468459923611").
    # Set by the sync layer; empty until assigned.
    directory: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "stable_id": self.stable_id,
            "slug": self.slug,
            "directory": self.directory,
            "pin_id": self.pin_id,
            "guid": self.guid,
            "title": self.title,
            "description": self.description,
            "board_id": self.board_id,
            "source_url": self.source_url,
            "canonical_url": self.canonical_url,
            "image_url": self.image_url,
            "pub_date": self.pub_date.isoformat() if self.pub_date else None,
            "first_seen": self.first_seen.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "content_hash": self.content_hash,
            "original_metadata": self.original_metadata,
            "local_paths": self.local_paths,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PinterestItem:
        return cls(
            stable_id=data["stable_id"],
            slug=data.get("slug", ""),
            directory=data.get("directory", ""),
            pin_id=data.get("pin_id"),
            guid=data.get("guid", ""),
            title=data["title"],
            description=data["description"],
            board_id=data["board_id"],
            source_url=data["source_url"],
            canonical_url=data["canonical_url"],
            image_url=data.get("image_url"),
            pub_date=_parse_dt(data.get("pub_date")),
            first_seen=_parse_dt(data["first_seen"]) or _utcnow(),
            last_updated=_parse_dt(data["last_updated"]) or _utcnow(),
            content_hash=data["content_hash"],
            original_metadata=data.get("original_metadata", {}),
            local_paths=data.get("local_paths", {}),
        )


@dataclass
class ManifestEntry:
    """A lightweight record of one synced item stored in the manifest."""

    stable_id: str
    source_url: str
    content_hash: str
    first_seen: datetime
    last_updated: datetime
    local_paths: dict[str, str] = field(default_factory=dict)
    # Human-readable presentation slug; empty for items synced before slug support.
    slug: str = ""
    # Archive directory name (e.g. "pin-1061301468459923611"); empty for legacy items.
    directory: str = ""
    # Numeric Pinterest pin ID; None for non-Pinterest items.
    pin_id: str | None = None
    # Raw RSS GUID value.
    guid: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "stable_id": self.stable_id,
            "slug": self.slug,
            "directory": self.directory,
            "pin_id": self.pin_id,
            "guid": self.guid,
            "source_url": self.source_url,
            "content_hash": self.content_hash,
            "first_seen": self.first_seen.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "local_paths": self.local_paths,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManifestEntry:
        return cls(
            stable_id=data["stable_id"],
            slug=data.get("slug", ""),
            directory=data.get("directory", ""),
            pin_id=data.get("pin_id"),
            guid=data.get("guid", ""),
            source_url=data["source_url"],
            content_hash=data["content_hash"],
            first_seen=_parse_dt(data["first_seen"]) or _utcnow(),
            last_updated=_parse_dt(data["last_updated"]) or _utcnow(),
            local_paths=data.get("local_paths", {}),
        )


@dataclass
class Manifest:
    """Top-level manifest for a single board feed."""

    feed_url: str
    board_id: str
    last_sync: datetime | None = None
    items: dict[str, ManifestEntry] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "feed_url": self.feed_url,
            "board_id": self.board_id,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "items": {k: v.to_dict() for k, v in self.items.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Manifest:
        items = {
            k: ManifestEntry.from_dict(v)
            for k, v in data.get("items", {}).items()
        }
        return cls(
            feed_url=data["feed_url"],
            board_id=data["board_id"],
            last_sync=_parse_dt(data.get("last_sync")),
            items=items,
        )


@dataclass
class FeedConfig:
    """Configuration for a single Pinterest board feed."""

    id: str
    url: str
    output: str
    # Additional feed URLs to combine with the primary URL (e.g. legacy board URLs after
    # a Pinterest username migration).  Items are deduplicated by stable_id.
    additional_urls: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeedConfig:
        return cls(
            id=data["id"],
            url=data["url"],
            output=data["output"],
            additional_urls=list(data.get("additional_urls", [])),
        )


@dataclass
class SyncConfig:
    """Parsed configuration from config.yaml."""

    feeds: list[FeedConfig] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SyncConfig:
        feeds = [FeedConfig.from_dict(f) for f in data.get("feeds", [])]
        return cls(feeds=feeds)


def compute_content_hash(title: str, description: str, image_url: str | None) -> str:
    """Produce a deterministic SHA-256 content hash from key item fields."""
    raw = f"{title}\n{description}\n{image_url or ''}".encode()
    return hashlib.sha256(raw).hexdigest()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except (ValueError, TypeError):
        return None


def _utcnow() -> datetime:
    return datetime.now(UTC)
