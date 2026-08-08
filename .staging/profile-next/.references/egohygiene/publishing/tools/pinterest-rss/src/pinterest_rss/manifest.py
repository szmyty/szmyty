"""Manifest persistence – read and write the per-board manifest.json."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import structlog

from pinterest_rss.models import Manifest, ManifestEntry, PinterestItem

log = structlog.get_logger(__name__)

_MANIFEST_FILENAME = "manifest.json"


def load_manifest(output_dir: Path, feed_url: str, board_id: str) -> Manifest:
    """Load the manifest from *output_dir*, or return an empty one."""
    path = output_dir / _MANIFEST_FILENAME
    if not path.exists():
        log.debug("manifest.load.new", path=str(path))
        return Manifest(feed_url=feed_url, board_id=board_id)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        manifest = Manifest.from_dict(data)
        log.debug(
            "manifest.load.ok",
            path=str(path),
            item_count=len(manifest.items),
        )
        return manifest
    except Exception as exc:
        log.warning("manifest.load.failed", path=str(path), exc=str(exc))
        return Manifest(feed_url=feed_url, board_id=board_id)


def save_manifest(manifest: Manifest, output_dir: Path) -> None:
    """Atomically write the manifest to *output_dir/manifest.json*."""
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / _MANIFEST_FILENAME
    data = json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False)
    _atomic_write(dest, data.encode("utf-8"))
    log.debug("manifest.save.ok", path=str(dest), item_count=len(manifest.items))


def classify_item(
    item: PinterestItem, manifest: Manifest
) -> tuple[str, ManifestEntry | None]:
    """Return (status, existing_entry) where status is 'new', 'changed', or 'unchanged'."""
    existing = manifest.items.get(item.stable_id)
    if existing is None:
        return "new", None
    if existing.content_hash != item.content_hash:
        return "changed", existing
    return "unchanged", existing


def update_manifest(
    manifest: Manifest,
    item: PinterestItem,
    status: str,
    existing: ManifestEntry | None,
) -> ManifestEntry:
    """Upsert a manifest entry and return it."""
    now = datetime.now(UTC)
    first_seen = existing.first_seen if existing else now

    entry = ManifestEntry(
        stable_id=item.stable_id,
        slug=item.slug,
        directory=item.directory,
        pin_id=item.pin_id,
        guid=item.guid,
        source_url=item.source_url,
        content_hash=item.content_hash,
        first_seen=first_seen,
        last_updated=now if status != "unchanged" else (existing.last_updated if existing else now),
        local_paths=item.local_paths,
    )
    manifest.items[item.stable_id] = entry
    return entry


def _atomic_write(path: Path, data: bytes) -> None:
    """Write *data* to *path* atomically using a temp file + rename."""
    dir_ = path.parent
    dir_.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_, prefix=".manifest-")
    try:
        os.write(fd, data)
        os.close(fd)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
