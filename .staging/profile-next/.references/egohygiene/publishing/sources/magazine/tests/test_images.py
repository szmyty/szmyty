"""Tests for AVIF image asset generation (magazine.assets.images)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestGenAvif:
    """Tests for gen_avif()."""

    def test_skips_when_pillow_avif_not_installed(self, tmp_path: Path) -> None:
        """gen_avif logs a warning and returns without writing a file when plugin is absent."""
        src = tmp_path / "page.png"
        src.write_bytes(b"fake png")
        out_dir = tmp_path / "artifacts"
        out_dir.mkdir()

        from magazine.assets.images import gen_avif

        with patch.dict(sys.modules, {"pillow_avif": None}):
            gen_avif(src, out_dir)

        assert not (out_dir / "page.avif").exists()

    def test_generates_avif_when_plugin_installed(self, tmp_path: Path) -> None:
        """gen_avif saves page.avif via PIL when pillow_avif is importable."""
        src = tmp_path / "page.png"
        src.write_bytes(b"fake png")
        out_dir = tmp_path / "artifacts"
        out_dir.mkdir()

        mock_pillow_avif = MagicMock()
        mock_image = MagicMock()
        mock_pil = MagicMock()
        mock_pil.Image.open.return_value = mock_image

        from magazine.assets.images import gen_avif

        with patch.dict(sys.modules, {"pillow_avif": mock_pillow_avif, "PIL": mock_pil}):
            gen_avif(src, out_dir)

        mock_pil.Image.open.assert_called_once_with(src)
        mock_image.save.assert_called_once_with(str(out_dir / "page.avif"))

    def test_skips_and_logs_warning_when_plugin_absent(self, tmp_path: Path, capsys) -> None:
        """gen_avif emits the expected warning message when plugin is absent."""
        src = tmp_path / "page.png"
        src.write_bytes(b"fake png")

        from magazine.assets.images import gen_avif

        with patch.dict(sys.modules, {"pillow_avif": None}):
            gen_avif(src, tmp_path)

        captured = capsys.readouterr()
        assert "AVIF plugin not installed" in captured.err

    def test_logs_info_when_plugin_available(self, tmp_path: Path, capsys) -> None:
        """gen_avif emits the generating AVIF info message when plugin is available."""
        src = tmp_path / "page.png"
        src.write_bytes(b"fake png")
        out_dir = tmp_path / "artifacts"
        out_dir.mkdir()

        mock_pillow_avif = MagicMock()
        mock_image = MagicMock()
        mock_pil = MagicMock()
        mock_pil.Image.open.return_value = mock_image

        from magazine.assets.images import gen_avif

        with patch.dict(sys.modules, {"pillow_avif": mock_pillow_avif, "PIL": mock_pil}):
            gen_avif(src, out_dir)

        captured = capsys.readouterr()
        assert "Generating AVIF artifact" in captured.out


class TestGenerateImageAssetsAvif:
    """Tests that generate_image_assets() calls gen_avif."""

    def test_generate_image_assets_calls_gen_avif(self, tmp_path: Path) -> None:
        """generate_image_assets() invokes gen_avif when page.png exists."""
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        (page_dir / "page.png").write_bytes(b"fake png")
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        from magazine.assets.images import generate_image_assets

        with patch("magazine.assets.images.gen_jpg"), \
             patch("magazine.assets.images.gen_webp"), \
             patch("magazine.assets.images.gen_avif") as mock_avif, \
             patch("magazine.assets.images.gen_web_jpg"), \
             patch("magazine.assets.images.gen_instagram"), \
             patch("magazine.assets.images.gen_tiff"), \
             patch("magazine.assets.images.gen_fullbleed_pdf"):
            generate_image_assets(page_dir, artifacts_dir)

        mock_avif.assert_called_once()

    def test_generate_image_assets_skips_avif_when_no_png(self, tmp_path: Path) -> None:
        """generate_image_assets() does not call gen_avif when page.png is absent."""
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        from magazine.assets.images import generate_image_assets

        with patch("magazine.assets.images.gen_avif") as mock_avif:
            generate_image_assets(page_dir, artifacts_dir)

        mock_avif.assert_not_called()
