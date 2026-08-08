"""Manifest persistence – read and write the per-feed manifest.json."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import structlog

from medium_rss.models import Manifest, ManifestEntry, MediumArticle

log = structlog.get_logger(__name__)

_MANIFEST_FILENAME = "manifest.json"


def load_manifest(output_dir: Path, feed_url: str) -> Manifest:
    """Load the manifest from *output_dir*, or return an empty one."""
    path = output_dir / _MANIFEST_FILENAME
    if not path.exists():
        log.debug("manifest.load.new", path=str(path))
        return Manifest(feed_url=feed_url)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        manifest = Manifest.from_dict(data)
        log.debug(
            "manifest.load.ok",
            path=str(path),
            article_count=len(manifest.articles),
        )
        return manifest
    except Exception as exc:
        log.warning("manifest.load.failed", path=str(path), exc=str(exc))
        return Manifest(feed_url=feed_url)


def save_manifest(manifest: Manifest, output_dir: Path) -> None:
    """Atomically write the manifest to *output_dir/manifest.json*."""
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / _MANIFEST_FILENAME
    data = json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False)
    _atomic_write(dest, data.encode("utf-8"))
    log.debug("manifest.save.ok", path=str(dest), article_count=len(manifest.articles))


def classify_article(
    article: MediumArticle, manifest: Manifest
) -> tuple[str, ManifestEntry | None]:
    """Return (status, existing_entry) where status is 'new', 'changed', or 'unchanged'."""
    existing = manifest.articles.get(article.id)
    if existing is None:
        return "new", None
    if existing.content_hash != article.content_hash:
        return "changed", existing
    return "unchanged", existing


def update_manifest(
    manifest: Manifest,
    article: MediumArticle,
    status: str,
    existing: ManifestEntry | None,
) -> ManifestEntry:
    """Upsert a manifest entry and return it."""
    now = datetime.now(timezone.utc)
    first_seen = existing.first_seen if existing else now

    entry = ManifestEntry(
        id=article.id,
        slug=article.slug,
        canonical_url=article.canonical_url,
        guid=article.guid,
        published_at=article.published_at,
        updated_at=article.updated_at,
        content_hash=article.content_hash,
        feed_url=article.feed_url,
        first_seen=first_seen,
        last_synced=now if status != "unchanged" else (existing.last_synced if existing else now),
        sync_status="ok",
        asset_paths=article.asset_paths,
    )
    manifest.articles[article.id] = entry
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
