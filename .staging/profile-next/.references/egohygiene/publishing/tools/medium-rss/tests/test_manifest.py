"""Tests for manifest.py."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from medium_rss.manifest import (
    classify_article,
    load_manifest,
    save_manifest,
    update_manifest,
)
from medium_rss.models import Manifest, ManifestEntry, MediumArticle


def _make_article(
    article_id: str = "f284b362c931",
    slug: str = "mood-colors-your-reality",
    content_hash: str = "abc123",
) -> MediumArticle:
    now = datetime.now(timezone.utc)
    return MediumArticle(
        id=article_id,
        slug=slug,
        title="Mood Colors Your Reality",
        author="szmyty",
        source_url="https://szmyty.medium.com/mood-colors-your-reality-f284b362c931",
        guid="https://medium.com/p/f284b362c931",
        canonical_url="https://szmyty.medium.com/mood-colors-your-reality-f284b362c931",
        published_at=now,
        updated_at=now,
        categories=["mental-health", "psychology"],
        content_html="<p>Test content</p>",
        content_hash=content_hash,
        feed_url="https://articles.egohygiene.io/feed",
        first_seen=now,
        last_synced=now,
    )


def test_load_manifest_new(tmp_path: Path) -> None:
    manifest = load_manifest(tmp_path, "https://articles.egohygiene.io/feed")
    assert manifest.feed_url == "https://articles.egohygiene.io/feed"
    assert manifest.articles == {}


def test_save_and_load_manifest_round_trip(tmp_path: Path) -> None:
    manifest = load_manifest(tmp_path, "https://articles.egohygiene.io/feed")
    article = _make_article()
    update_manifest(manifest, article, "new", None)
    save_manifest(manifest, tmp_path)

    loaded = load_manifest(tmp_path, "https://articles.egohygiene.io/feed")
    assert "f284b362c931" in loaded.articles
    assert loaded.articles["f284b362c931"].content_hash == "abc123"


def test_manifest_json_written_to_disk(tmp_path: Path) -> None:
    manifest = load_manifest(tmp_path, "https://articles.egohygiene.io/feed")
    save_manifest(manifest, tmp_path)
    assert (tmp_path / "manifest.json").exists()


def test_classify_new_article() -> None:
    manifest = Manifest(feed_url="https://articles.egohygiene.io/feed")
    article = _make_article()
    status, existing = classify_article(article, manifest)
    assert status == "new"
    assert existing is None


def test_classify_unchanged_article() -> None:
    manifest = Manifest(feed_url="https://articles.egohygiene.io/feed")
    article = _make_article(content_hash="same-hash")
    update_manifest(manifest, article, "new", None)

    status, existing = classify_article(article, manifest)
    assert status == "unchanged"
    assert existing is not None


def test_classify_changed_article() -> None:
    manifest = Manifest(feed_url="https://articles.egohygiene.io/feed")
    article_v1 = _make_article(content_hash="hash-v1")
    update_manifest(manifest, article_v1, "new", None)

    article_v2 = _make_article(content_hash="hash-v2")
    status, existing = classify_article(article_v2, manifest)
    assert status == "changed"
    assert existing is not None
    assert existing.content_hash == "hash-v1"


def test_update_manifest_preserves_first_seen() -> None:
    manifest = Manifest(feed_url="https://articles.egohygiene.io/feed")
    article = _make_article()
    entry_v1 = update_manifest(manifest, article, "new", None)
    first_seen_v1 = entry_v1.first_seen

    article_v2 = _make_article(content_hash="new-hash")
    entry_v2 = update_manifest(manifest, article_v2, "changed", entry_v1)
    assert entry_v2.first_seen == first_seen_v1


def test_idempotent_repeated_sync(tmp_path: Path) -> None:
    """Running sync twice with same content should not change the manifest."""
    manifest = load_manifest(tmp_path, "https://articles.egohygiene.io/feed")
    article = _make_article()
    update_manifest(manifest, article, "new", None)
    save_manifest(manifest, tmp_path)

    manifest2 = load_manifest(tmp_path, "https://articles.egohygiene.io/feed")
    status, _ = classify_article(article, manifest2)
    assert status == "unchanged"


def test_load_manifest_handles_corrupt_json(tmp_path: Path) -> None:
    (tmp_path / "manifest.json").write_text("not-valid-json", encoding="utf-8")
    manifest = load_manifest(tmp_path, "https://articles.egohygiene.io/feed")
    assert manifest.articles == {}


def test_manifest_preserves_unknown_articles_not_in_feed(tmp_path: Path) -> None:
    """Articles already in manifest must not be removed if absent from the current feed."""
    manifest = load_manifest(tmp_path, "https://articles.egohygiene.io/feed")
    old_article = _make_article(article_id="old000000001", slug="old-article")
    update_manifest(manifest, old_article, "new", None)
    save_manifest(manifest, tmp_path)

    # Simulate a new sync run that only returns one new article
    manifest2 = load_manifest(tmp_path, "https://articles.egohygiene.io/feed")
    new_article = _make_article(article_id="new000000002", slug="new-article")
    update_manifest(manifest2, new_article, "new", None)
    save_manifest(manifest2, tmp_path)

    manifest3 = load_manifest(tmp_path, "https://articles.egohygiene.io/feed")
    assert "old000000001" in manifest3.articles  # old article preserved
    assert "new000000002" in manifest3.articles  # new article added


def test_update_manifest_stores_slug() -> None:
    manifest = Manifest(feed_url="https://articles.egohygiene.io/feed")
    article = _make_article(slug="mood-colors-your-reality")
    entry = update_manifest(manifest, article, "new", None)
    assert entry.slug == "mood-colors-your-reality"


def test_update_manifest_stores_asset_paths() -> None:
    manifest = Manifest(feed_url="https://articles.egohygiene.io/feed")
    article = _make_article()
    article.asset_paths["https://cdn.example.com/photo.jpg"] = "publishing/medium/articles/test/assets/photo.jpg"
    entry = update_manifest(manifest, article, "new", None)
    assert "https://cdn.example.com/photo.jpg" in entry.asset_paths
