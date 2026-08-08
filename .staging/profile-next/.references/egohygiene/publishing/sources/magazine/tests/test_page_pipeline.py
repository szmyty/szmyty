"""Tests for the page build pipeline (magazine.page)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest


class TestBuildPage:
    """Tests for build_page() orchestration."""

    def _make_mock_stage(self) -> MagicMock:
        """Return a mock AIStage."""
        return MagicMock()

    def _build_page_mocked(
        self,
        page_dir: Path,
        **kwargs,
    ) -> MagicMock:
        """Call build_page with all external stages fully mocked."""
        mock_stage = self._make_mock_stage()
        kwargs.setdefault("ai_stage", mock_stage)
        with patch("magazine.pipeline.gen_page_meta") as m_meta, \
             patch("magazine.pipeline.generate_image_assets") as m_images, \
             patch("magazine.pipeline.generate_screenplay_assets") as m_screen, \
             patch("magazine.pipeline.generate_latex_page") as m_latex, \
             patch("magazine.pipeline.generate_size_variants") as m_sizes:
            from magazine.page import build_page
            build_page(page_dir, **kwargs)
        return {
            "meta": m_meta,
            "images": m_images,
            "fountain": mock_stage,
            "screenplay": m_screen,
            "latex": m_latex,
            "sizes": m_sizes,
        }

    def test_calls_metadata_stage(self, page_dir: Path) -> None:
        mocks = self._build_page_mocked(page_dir)
        call_args = mocks["meta"].call_args
        assert call_args.args[0] == page_dir.resolve()
        assert call_args.kwargs.get("reproducible") is False
        assert "config" in call_args.kwargs

    def test_calls_image_assets(self, page_dir: Path) -> None:
        mocks = self._build_page_mocked(page_dir)
        assert mocks["images"].call_count == 1

    def test_skips_fountain_when_disabled(self, page_dir: Path) -> None:
        mocks = self._build_page_mocked(page_dir, ai_fountain_disable=True)
        mocks["fountain"].generate_or_skip.assert_not_called()

    def test_calls_fountain_generate(self, page_dir: Path) -> None:
        mocks = self._build_page_mocked(page_dir)
        mocks["fountain"].generate_or_skip.assert_called_once()

    def test_calls_screenplay_assets(self, page_dir: Path) -> None:
        mocks = self._build_page_mocked(page_dir)
        assert mocks["screenplay"].call_count == 1

    def test_calls_latex_by_default(self, page_dir: Path) -> None:
        mocks = self._build_page_mocked(page_dir)
        assert mocks["latex"].call_count == 1

    def test_skips_latex_when_disabled(self, page_dir: Path) -> None:
        mocks = self._build_page_mocked(page_dir, latex_disable=True)
        mocks["latex"].assert_not_called()

    def test_calls_size_variants_by_default(self, page_dir: Path) -> None:
        mocks = self._build_page_mocked(page_dir)
        assert mocks["sizes"].call_count == 1

    def test_skips_sizes_when_disabled(self, page_dir: Path) -> None:
        mocks = self._build_page_mocked(page_dir, sizes_disable=True)
        mocks["sizes"].assert_not_called()

    def test_latex_force_flag_passed_through(self, page_dir: Path) -> None:
        mock_stage = self._make_mock_stage()
        with patch("magazine.pipeline.gen_page_meta"), \
             patch("magazine.pipeline.generate_image_assets"), \
             patch("magazine.pipeline.generate_screenplay_assets"), \
             patch("magazine.pipeline.generate_latex_page") as m_latex, \
             patch("magazine.pipeline.generate_size_variants"):
            from magazine.page import build_page
            build_page(page_dir, ai_stage=mock_stage, latex_force=True)
        _, kwargs = m_latex.call_args
        assert kwargs["force"] is True

    def test_latex_safe_mode_flag_passed_through(self, page_dir: Path) -> None:
        mock_stage = self._make_mock_stage()
        with patch("magazine.pipeline.gen_page_meta"), \
             patch("magazine.pipeline.generate_image_assets"), \
             patch("magazine.pipeline.generate_screenplay_assets"), \
             patch("magazine.pipeline.generate_latex_page") as m_latex, \
             patch("magazine.pipeline.generate_size_variants"):
            from magazine.page import build_page
            build_page(page_dir, ai_stage=mock_stage, latex_safe_mode=True)
        _, kwargs = m_latex.call_args
        assert kwargs["safe_mode"] is True

    def test_sizes_force_flag_passed_through(self, page_dir: Path) -> None:
        mock_stage = self._make_mock_stage()
        with patch("magazine.pipeline.gen_page_meta"), \
             patch("magazine.pipeline.generate_image_assets"), \
             patch("magazine.pipeline.generate_screenplay_assets"), \
             patch("magazine.pipeline.generate_latex_page"), \
             patch("magazine.pipeline.generate_size_variants") as m_sizes:
            from magazine.page import build_page
            build_page(page_dir, ai_stage=mock_stage, sizes_force=True)
        _, kwargs = m_sizes.call_args
        assert kwargs["force"] is True

    def test_sizes_safe_mode_flag_passed_through(self, page_dir: Path) -> None:
        mock_stage = self._make_mock_stage()
        with patch("magazine.pipeline.gen_page_meta"), \
             patch("magazine.pipeline.generate_image_assets"), \
             patch("magazine.pipeline.generate_screenplay_assets"), \
             patch("magazine.pipeline.generate_latex_page"), \
             patch("magazine.pipeline.generate_size_variants") as m_sizes:
            from magazine.page import build_page
            build_page(page_dir, ai_stage=mock_stage, sizes_safe_mode=True)
        _, kwargs = m_sizes.call_args
        assert kwargs["safe_mode"] is True

    def test_artifacts_dir_created(self, page_dir: Path) -> None:
        mock_stage = self._make_mock_stage()
        with patch("magazine.pipeline.gen_page_meta"), \
             patch("magazine.pipeline.generate_image_assets"), \
             patch("magazine.pipeline.generate_screenplay_assets"), \
             patch("magazine.pipeline.generate_latex_page"), \
             patch("magazine.pipeline.generate_size_variants"):
            from magazine.page import build_page
            build_page(page_dir, ai_stage=mock_stage, force=False)
        assert (page_dir / "artifacts").is_dir()

    def test_force_clears_artifacts(self, page_dir: Path) -> None:
        artifacts = page_dir / "artifacts"
        artifacts.mkdir()
        leftover = artifacts / "leftover.txt"
        leftover.write_text("old")
        mock_stage = self._make_mock_stage()
        with patch("magazine.pipeline.gen_page_meta"), \
             patch("magazine.pipeline.generate_image_assets"), \
             patch("magazine.pipeline.generate_screenplay_assets"), \
             patch("magazine.pipeline.generate_latex_page"), \
             patch("magazine.pipeline.generate_size_variants"):
            from magazine.page import build_page
            build_page(page_dir, ai_stage=mock_stage, force=True)
        assert not leftover.exists()

    def test_sizes_list_passed_through(self, page_dir: Path) -> None:
        mock_stage = self._make_mock_stage()
        with patch("magazine.pipeline.gen_page_meta"), \
             patch("magazine.pipeline.generate_image_assets"), \
             patch("magazine.pipeline.generate_screenplay_assets"), \
             patch("magazine.pipeline.generate_latex_page"), \
             patch("magazine.pipeline.generate_size_variants") as m_sizes:
            from magazine.page import build_page
            build_page(page_dir, ai_stage=mock_stage, sizes=["modern", "manga"])
        _, kwargs = m_sizes.call_args
        assert kwargs["sizes"] == ["modern", "manga"]

    def test_default_ai_stage_is_fountain(self, page_dir: Path) -> None:
        """When no ai_stage is provided, FountainAIStage is instantiated by default."""
        with patch("magazine.pipeline.gen_page_meta"), \
             patch("magazine.pipeline.generate_image_assets"), \
             patch("magazine.pipeline.generate_screenplay_assets"), \
             patch("magazine.pipeline.generate_latex_page"), \
             patch("magazine.pipeline.generate_size_variants"), \
             patch("magazine.page.FountainAIStage") as MockFountain:
            mock_instance = MagicMock()
            MockFountain.return_value = mock_instance
            from magazine.page import build_page
            build_page(page_dir)
        MockFountain.assert_called_once()
        mock_instance.generate_or_skip.assert_called_once()

