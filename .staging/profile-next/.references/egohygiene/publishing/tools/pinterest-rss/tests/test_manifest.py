"""Tests for manifest.py."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pinterest_rss.manifest import (
    classify_item,
    load_manifest,
    save_manifest,
    update_manifest,
)
from pinterest_rss.models import Manifest, PinterestItem


def _make_item(
    stable_id: str = "item-001",
    content_hash: str = "abc123",
    image_url: str | None = "https://img.example.com/photo.jpg",
) -> PinterestItem:
    now = datetime.now(UTC)
    return PinterestItem(
        stable_id=stable_id,
        title="Test Pin",
        description="A test description",
        board_id="ego-hygiene",
        source_url="https://www.pinterest.com/pin/001/",
        canonical_url="https://www.pinterest.com/pin/001/",
        image_url=image_url,
        pub_date=now,
        first_seen=now,
        last_updated=now,
        content_hash=content_hash,
    )


def test_load_manifest_new(tmp_path: Path) -> None:
    manifest = load_manifest(tmp_path, "https://feed.url/rss", "ego-hygiene")
    assert manifest.feed_url == "https://feed.url/rss"
    assert manifest.board_id == "ego-hygiene"
    assert manifest.items == {}


def test_save_and_load_manifest_round_trip(tmp_path: Path) -> None:
    manifest = load_manifest(tmp_path, "https://feed.url/rss", "ego-hygiene")
    item = _make_item()
    update_manifest(manifest, item, "new", None)
    save_manifest(manifest, tmp_path)

    loaded = load_manifest(tmp_path, "https://feed.url/rss", "ego-hygiene")
    assert "item-001" in loaded.items
    assert loaded.items["item-001"].content_hash == "abc123"


def test_manifest_json_written_to_disk(tmp_path: Path) -> None:
    manifest = load_manifest(tmp_path, "https://feed.url/rss", "ego-hygiene")
    save_manifest(manifest, tmp_path)
    assert (tmp_path / "manifest.json").exists()


def test_classify_new_item() -> None:
    manifest = Manifest(feed_url="https://feed.url/rss", board_id="ego-hygiene")
    item = _make_item()
    status, existing = classify_item(item, manifest)
    assert status == "new"
    assert existing is None


def test_classify_unchanged_item() -> None:
    manifest = Manifest(feed_url="https://feed.url/rss", board_id="ego-hygiene")
    item = _make_item(content_hash="same-hash")
    update_manifest(manifest, item, "new", None)

    status, existing = classify_item(item, manifest)
    assert status == "unchanged"
    assert existing is not None


def test_classify_changed_item() -> None:
    manifest = Manifest(feed_url="https://feed.url/rss", board_id="ego-hygiene")
    item_v1 = _make_item(content_hash="hash-v1")
    update_manifest(manifest, item_v1, "new", None)

    item_v2 = _make_item(content_hash="hash-v2")
    status, existing = classify_item(item_v2, manifest)
    assert status == "changed"
    assert existing is not None
    assert existing.content_hash == "hash-v1"


def test_update_manifest_preserves_first_seen() -> None:
    manifest = Manifest(feed_url="https://feed.url/rss", board_id="ego-hygiene")
    item = _make_item()
    entry_v1 = update_manifest(manifest, item, "new", None)
    first_seen_v1 = entry_v1.first_seen

    item_v2 = _make_item(content_hash="new-hash")
    entry_v2 = update_manifest(manifest, item_v2, "changed", entry_v1)
    assert entry_v2.first_seen == first_seen_v1


def test_idempotent_repeated_sync(tmp_path: Path) -> None:
    """Running sync twice with same content should not change the manifest."""
    manifest = load_manifest(tmp_path, "https://feed.url/rss", "ego-hygiene")
    item = _make_item()
    update_manifest(manifest, item, "new", None)
    save_manifest(manifest, tmp_path)

    # Second run: same item
    manifest2 = load_manifest(tmp_path, "https://feed.url/rss", "ego-hygiene")
    status, _ = classify_item(item, manifest2)
    assert status == "unchanged"


def test_load_manifest_handles_corrupt_json(tmp_path: Path) -> None:
    (tmp_path / "manifest.json").write_text("not-valid-json", encoding="utf-8")
    manifest = load_manifest(tmp_path, "https://feed.url/rss", "ego-hygiene")
    assert manifest.items == {}
