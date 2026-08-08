"""Tests for downloader.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx

from pinterest_rss.downloader import _resolve_extension, download_image


def test_resolve_extension_from_content_type() -> None:
    assert _resolve_extension("image/jpeg", "https://example.com/img") == ".jpg"
    assert _resolve_extension("image/png", "https://example.com/img") == ".png"
    assert _resolve_extension("image/webp", "https://example.com/img") == ".webp"


def test_resolve_extension_fallback_to_url() -> None:
    assert _resolve_extension("application/octet-stream", "https://example.com/photo.png") == ".png"
    assert _resolve_extension("application/octet-stream", "https://example.com/img.gif") == ".gif"


def test_resolve_extension_default_jpg_for_unknown() -> None:
    assert _resolve_extension("", "https://example.com/noext") == ".jpg"


def test_download_image_returns_none_on_http_error(tmp_path: Path) -> None:
    with patch("pinterest_rss.downloader.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = lambda s: mock_client
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=MagicMock()
        )
        mock_client.get.return_value = mock_response

        result = download_image("https://example.com/img.jpg", tmp_path)
        assert result is None


def test_download_image_returns_none_for_empty_url(tmp_path: Path) -> None:
    result = download_image("", tmp_path)
    assert result is None


def test_download_image_writes_file(tmp_path: Path) -> None:
    fake_content = b"\xff\xd8\xff\xe0fake-jpeg-data"
    with patch("pinterest_rss.downloader.httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = lambda s: mock_client
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_response.content = fake_content
        mock_client.get.return_value = mock_response

        result = download_image("https://example.com/photo.jpg", tmp_path)
        assert result is not None
        assert result.exists()
        assert result.read_bytes() == fake_content
        assert result.suffix == ".jpg"
