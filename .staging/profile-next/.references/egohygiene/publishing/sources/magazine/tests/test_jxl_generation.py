"""Tests for JPEG XL artifact generation (gen_jxl)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magazine.assets.images import gen_jxl, generate_image_assets


class TestGenJxl:
    """Tests for gen_jxl() function."""

    def test_skips_gracefully_when_plugin_missing(self, tmp_path: Path) -> None:
        """When pillow_jxl is not importable, no JXL file is created."""
        src = tmp_path / "page.png"
        src.write_bytes(b"fake png")

        with patch.dict(sys.modules, {"pillow_jxl": None}):
            gen_jxl(src, tmp_path)

        assert not (tmp_path / "page.jxl").exists()

    def test_logs_warning_when_plugin_missing(self, tmp_path: Path, capsys) -> None:
        """When pillow_jxl is not importable, a warning is logged to stderr."""
        src = tmp_path / "page.png"
        src.write_bytes(b"fake png")

        with patch.dict(sys.modules, {"pillow_jxl": None}):
            gen_jxl(src, tmp_path)

        captured = capsys.readouterr()
        assert "JPEG XL plugin not installed" in captured.err
        assert "skipping JXL generation" in captured.err

    def test_generates_jxl_when_plugin_available(self, tmp_path: Path) -> None:
        """When pillow_jxl is available, page.jxl is created in out_dir."""
        src = tmp_path / "page.png"
        src.write_bytes(b"fake png")
        out_dir = tmp_path / "artifacts"
        out_dir.mkdir()

        mock_pillow_jxl = MagicMock()
        mock_image = MagicMock()
        mock_img_ctx = MagicMock()
        mock_img_ctx.__enter__ = MagicMock(return_value=mock_image)
        mock_img_ctx.__exit__ = MagicMock(return_value=False)

        with patch.dict(sys.modules, {"pillow_jxl": mock_pillow_jxl}), \
             patch("PIL.Image.open", return_value=mock_img_ctx):
            gen_jxl(src, out_dir)

        mock_image.save.assert_called_once_with(out_dir / "page.jxl")

    def test_logs_info_when_generating(self, tmp_path: Path, capsys) -> None:
        """When generating JXL, an info message is logged."""
        src = tmp_path / "page.png"
        src.write_bytes(b"fake png")

        mock_pillow_jxl = MagicMock()
        mock_image = MagicMock()
        mock_img_ctx = MagicMock()
        mock_img_ctx.__enter__ = MagicMock(return_value=mock_image)
        mock_img_ctx.__exit__ = MagicMock(return_value=False)

        with patch.dict(sys.modules, {"pillow_jxl": mock_pillow_jxl}), \
             patch("PIL.Image.open", return_value=mock_img_ctx):
            gen_jxl(src, tmp_path)

        captured = capsys.readouterr()
        assert "Generating JPEG XL artifact" in captured.out


class TestGenerateImageAssetsCallsJxl:
    """Tests that generate_image_assets() calls gen_jxl()."""

    def test_generate_image_assets_calls_gen_jxl(self, page_dir: Path) -> None:
        """generate_image_assets() invokes gen_jxl() when page.png exists."""
        artifacts = page_dir / "artifacts"
        artifacts.mkdir()

        with patch("magazine.assets.images.gen_jpg"), \
             patch("magazine.assets.images.gen_webp"), \
             patch("magazine.assets.images.gen_web_jpg"), \
             patch("magazine.assets.images.gen_instagram"), \
             patch("magazine.assets.images.gen_tiff"), \
             patch("magazine.assets.images.gen_fullbleed_pdf"), \
             patch("magazine.assets.images.gen_jxl") as mock_jxl:
            generate_image_assets(page_dir, artifacts)

        mock_jxl.assert_called_once_with(page_dir / "page.png", artifacts)
