"""Tests for downloader.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from medium_rss.downloader import _deterministic_stem, _resolve_extension, download_asset


def test_resolve_extension_from_content_type() -> None:
    assert _resolve_extension("image/png", "https://example.com/image") == ".png"
    assert _resolve_extension("image/jpeg", "https://example.com/image") == ".jpg"
    assert _resolve_extension("image/webp", "https://example.com/image") == ".webp"


def test_resolve_extension_from_url_fallback() -> None:
    assert _resolve_extension("", "https://example.com/photo.png") == ".png"
    assert _resolve_extension("application/octet-stream", "https://example.com/photo.gif") == ".gif"


def test_resolve_extension_default_jpg() -> None:
    assert _resolve_extension("", "https://example.com/image") == ".jpg"


def test_deterministic_stem_with_hint() -> None:
    stem1 = _deterministic_stem("https://cdn.example.com/image.jpg", "mood-hero")
    stem2 = _deterministic_stem("https://cdn.example.com/image.jpg", "mood-hero")
    assert stem1 == stem2
    assert "mood-hero" in stem1


def test_deterministic_stem_without_hint() -> None:
    stem = _deterministic_stem("https://cdn.example.com/photo.jpg", "")
    assert stem
    assert "-" in stem  # should have hash suffix


def test_deterministic_stem_sanitizes_hint() -> None:
    stem = _deterministic_stem("https://cdn.example.com/image.jpg", "Hello World!")
    assert " " not in stem
    assert "!" not in stem


def test_download_asset_returns_none_for_empty_url(tmp_path: Path) -> None:
    result = download_asset("", tmp_path)
    assert result is None


def test_download_asset_returns_none_on_http_error(tmp_path: Path) -> None:
    with patch("medium_rss.downloader._download_with_retry", side_effect=Exception("fail")):
        result = download_asset("https://example.com/photo.jpg", tmp_path)
        assert result is None


def test_download_asset_skips_existing_file(tmp_path: Path) -> None:
    """If the file already exists and has content, it should not be re-downloaded."""
    dest_dir = tmp_path / "assets"
    dest_dir.mkdir()
    existing_file = dest_dir / "photo-abc12345.jpg"
    existing_file.write_bytes(b"image data")

    call_count = 0

    def fake_download(url: str, dest_dir: Path, hint: str, timeout: float, max_retries: int) -> Path:
        nonlocal call_count
        call_count += 1
        return existing_file

    with patch("medium_rss.downloader._download_with_retry", side_effect=fake_download):
        result = download_asset("https://cdn.example.com/photo.jpg", dest_dir)

    assert result is not None
