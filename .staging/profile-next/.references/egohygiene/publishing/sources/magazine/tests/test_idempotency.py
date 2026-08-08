"""Tests for idempotency guarantees across stages."""

import json
from pathlib import Path
from unittest.mock import patch, call, MagicMock


class TestFountainIdempotency:
    def test_no_regeneration_when_hash_unchanged(self, tmp_path: Path) -> None:
        """FountainAIStage.generate_or_skip() must not re-invoke AI when image is stable."""
        from magazine.ai.fountain import FountainAIStage
        from magazine.hashing import hash_file
        from unittest.mock import MagicMock

        img = tmp_path / "page.png"
        img.write_bytes(b"stable image content")

        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = "Title: Test\n\nINT. ROOM – DAY\n"

        with patch.object(stage, "ensure_model"), \
             patch("magazine.ai.fountain.run", return_value=mock_result) as mock_run:
            stage.generate_or_skip(tmp_path)   # first run → AI invoked
            stage.generate_or_skip(tmp_path)   # second run → hash matches → skip

        assert mock_run.call_count == 1, "AI should only run once for stable image"

    def test_regeneration_when_image_changes(self, tmp_path: Path) -> None:
        """FountainAIStage.generate() must re-invoke AI when image bytes change."""
        from magazine.ai.fountain import FountainAIStage
        from unittest.mock import MagicMock

        img = tmp_path / "page.png"
        img.write_bytes(b"original content")

        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = "Title: Test\n\nINT. ROOM – DAY\n\nA quiet space.\n"

        with patch.object(stage, "ensure_model"), \
             patch("magazine.ai.fountain.run", return_value=mock_result) as mock_run:
            stage.generate(tmp_path)
            img.write_bytes(b"updated content")   # image changed
            stage.generate(tmp_path)

        assert mock_run.call_count == 2


class TestLatexIdempotency:
    def test_no_recompile_when_png_unchanged(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        img = tmp_path / "page.png"
        img.write_bytes(b"stable png data")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()

        with patch("magazine.assets.latex._compile_latex") as mock_compile:
            generate_latex_page(tmp_path, artifacts)
            generate_latex_page(tmp_path, artifacts)

        assert mock_compile.call_count == 1

    def test_recompile_when_png_changes(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        img = tmp_path / "page.png"
        img.write_bytes(b"original")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()

        with patch("magazine.assets.latex._compile_latex") as mock_compile:
            generate_latex_page(tmp_path, artifacts)
            img.write_bytes(b"updated")
            generate_latex_page(tmp_path, artifacts)

        assert mock_compile.call_count == 2

    def test_recompile_when_force(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        img = tmp_path / "page.png"
        img.write_bytes(b"stable")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()

        with patch("magazine.assets.latex._compile_latex") as mock_compile:
            generate_latex_page(tmp_path, artifacts)
            generate_latex_page(tmp_path, artifacts, force=True)

        assert mock_compile.call_count == 2

    def test_recompile_when_engine_changes(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        import shutil
        img = tmp_path / "page.png"
        img.write_bytes(b"stable")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()

        # Use pdflatex fallback if xelatex is absent, else just toggle
        has_xelatex = shutil.which("xelatex") is not None
        has_pdflatex = shutil.which("pdflatex") is not None
        if not (has_xelatex or has_pdflatex):
            # Neither engine is available; _resolve_engine returns the name as-is.
            eng1, eng2 = "xelatex", "pdflatex"
        elif has_xelatex and has_pdflatex:
            eng1, eng2 = "xelatex", "pdflatex"
        else:
            # Only one engine; skip this specific check (still generates config hash diff)
            eng1, eng2 = "xelatex", "pdflatex"

        with patch("magazine.assets.latex._compile_latex") as mock_compile, \
             patch("magazine.assets.latex._resolve_engine", side_effect=lambda e: e):
            generate_latex_page(tmp_path, artifacts, engine=eng1)
            generate_latex_page(tmp_path, artifacts, engine=eng2)

        assert mock_compile.call_count == 2


class TestSizesIdempotency:
    def _cfg(self, tmp_path: Path) -> Path:
        p = tmp_path / "sizes.json"
        p.write_text(json.dumps({
            "sm": {"width": 50, "height": 75, "dpi": 72,
                   "bleed": 0, "safe_margin": 0,
                   "output_suffix": "sm", "scaling_strategy": "fit"},
        }))
        return p

    def test_no_rerun_when_image_unchanged(self, tmp_path: Path) -> None:
        from magazine.assets.sizes import generate_size_variants
        img = tmp_path / "page.png"
        img.write_bytes(b"stable image")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        cfg = self._cfg(tmp_path)

        with patch("magazine.assets.sizes.run") as mock_run:
            generate_size_variants(tmp_path, artifacts, config_path=cfg)
            (artifacts / "sizes" / "sm" / "page.png").write_bytes(b"sized")
            generate_size_variants(tmp_path, artifacts, config_path=cfg)

        assert mock_run.call_count == 1

    def test_rerun_when_image_changes(self, tmp_path: Path) -> None:
        from magazine.assets.sizes import generate_size_variants
        img = tmp_path / "page.png"
        img.write_bytes(b"original")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        cfg = self._cfg(tmp_path)

        with patch("magazine.assets.sizes.run") as mock_run:
            generate_size_variants(tmp_path, artifacts, config_path=cfg)
            (artifacts / "sizes" / "sm" / "page.png").write_bytes(b"sized")
            img.write_bytes(b"changed")
            generate_size_variants(tmp_path, artifacts, config_path=cfg)

        assert mock_run.call_count == 2


class TestBuildPageIdempotency:
    """Full build_page() idempotency: no stage re-runs when inputs are stable."""

    def _run_mocked(self, page_dir: Path, **kwargs):
        from magazine.page import build_page
        mock_stage = MagicMock()
        kwargs.setdefault("ai_stage", mock_stage)
        calls = {}
        with patch("magazine.pipeline.gen_page_meta") as m_meta, \
             patch("magazine.pipeline.generate_image_assets") as m_img, \
             patch("magazine.pipeline.generate_screenplay_assets") as m_screen, \
             patch("magazine.pipeline.generate_latex_page") as m_latex, \
             patch("magazine.pipeline.generate_size_variants") as m_sizes:
            build_page(page_dir, **kwargs)
            calls = {
                "meta": m_meta.call_count,
                "images": m_img.call_count,
                "fountain_generate": mock_stage.generate_or_skip.call_count,
                "screenplay": m_screen.call_count,
                "latex": m_latex.call_count,
                "sizes": m_sizes.call_count,
            }
        return calls

    def test_all_stages_called_once(self, page_dir: Path) -> None:
        calls = self._run_mocked(page_dir)
        assert calls["meta"] == 1
        assert calls["images"] == 1
        assert calls["fountain_generate"] == 1
        assert calls["screenplay"] == 1
        assert calls["latex"] == 1
        assert calls["sizes"] == 1

    def test_latex_stage_skipped_when_disabled(self, page_dir: Path) -> None:
        calls = self._run_mocked(page_dir, latex_disable=True)
        assert calls["latex"] == 0

    def test_sizes_stage_skipped_when_disabled(self, page_dir: Path) -> None:
        calls = self._run_mocked(page_dir, sizes_disable=True)
        assert calls["sizes"] == 0
