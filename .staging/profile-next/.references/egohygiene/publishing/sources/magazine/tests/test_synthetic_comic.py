"""Integration tests using deterministic synthetic comic fixtures.

These tests exercise the full publishing pipeline against real PIL-generated
PNG images, providing a higher level of confidence than tests that rely on
fake binary data.  External subprocess calls (magick, img2pdf, etc.) are
mocked so the suite runs without system dependencies.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("PIL", reason="Pillow is required for synthetic fixture tests")

from tests.fixtures.generate_fake_comic import (
    PAGE_HEIGHT,
    PAGE_WIDTH,
    VARIANT_HEIGHT,
    VARIANT_WIDTH,
    generate_fake_comic,
    generate_variant_comic,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash_path(p: Path) -> str:
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    return h


# ---------------------------------------------------------------------------
# Fixture generation
# ---------------------------------------------------------------------------


class TestGenerateFakeComic:
    """Validate the fixture generator itself."""

    def test_creates_edition_directory(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        assert ed.is_dir()

    def test_creates_pages_directory(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        assert (ed / "pages").is_dir()

    def test_creates_three_pages(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        page_dirs = sorted((ed / "pages").iterdir())
        assert len(page_dirs) == 3

    def test_page_directories_sorted(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        names = [p.name for p in sorted((ed / "pages").iterdir())]
        assert names == sorted(names)

    def test_page_slugs(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        names = {p.name for p in (ed / "pages").iterdir()}
        assert names == {"01_intro", "02_middle", "03_finale"}

    def test_each_page_has_png(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        for page_dir in (ed / "pages").iterdir():
            assert (page_dir / "page.png").is_file(), f"Missing page.png in {page_dir.name}"

    def test_png_files_are_valid(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_fake_comic(tmp_path)
        for page_dir in (ed / "pages").iterdir():
            img = Image.open(page_dir / "page.png")
            assert img.format == "PNG"
            img.verify()

    def test_png_dimensions(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_fake_comic(tmp_path)
        for page_dir in (ed / "pages").iterdir():
            img = Image.open(page_dir / "page.png")
            assert img.size == (PAGE_WIDTH, PAGE_HEIGHT)

    def test_png_mode_rgb(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_fake_comic(tmp_path)
        for page_dir in (ed / "pages").iterdir():
            img = Image.open(page_dir / "page.png")
            assert img.mode == "RGB"

    def test_manifest_exists(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        assert (ed / "manifest.json").is_file()

    def test_manifest_structure(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        manifest = json.loads((ed / "manifest.json").read_text())
        assert "edition" in manifest
        assert "pages" in manifest
        assert isinstance(manifest["pages"], list)

    def test_manifest_page_order_deterministic(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        manifest = json.loads((ed / "manifest.json").read_text())
        assert manifest["pages"] == ["01_intro", "02_middle", "03_finale"]

    def test_manifest_edition_name(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path, edition_name="my_edition")
        manifest = json.loads((ed / "manifest.json").read_text())
        assert manifest["edition"] == "my_edition"

    def test_non_zero_file_sizes(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        for page_dir in (ed / "pages").iterdir():
            assert (page_dir / "page.png").stat().st_size > 1000


class TestDeterminism:
    """Verify that the generator produces bit-identical output on repeated runs."""

    def test_same_content_same_hash(self, tmp_path: Path) -> None:
        ed1 = generate_fake_comic(tmp_path / "run1")
        ed2 = generate_fake_comic(tmp_path / "run2")
        for slug in ("01_intro", "02_middle", "03_finale"):
            h1 = _hash_path(ed1 / "pages" / slug / "page.png")
            h2 = _hash_path(ed2 / "pages" / slug / "page.png")
            assert h1 == h2, f"Non-deterministic output for {slug}"

    def test_different_pages_different_hashes(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        hashes = [
            _hash_path(ed / "pages" / slug / "page.png")
            for slug in ("01_intro", "02_middle", "03_finale")
        ]
        assert len(set(hashes)) == 3, "Pages should have distinct hashes"

    def test_hash_stable_across_five_runs(self, tmp_path: Path) -> None:
        hashes = set()
        for i in range(5):
            ed = generate_fake_comic(tmp_path / f"run{i}")
            hashes.add(_hash_path(ed / "pages" / "01_intro" / "page.png"))
        assert len(hashes) == 1, "Hash must be stable across runs"


class TestVariantComic:
    """Validate the optional variant fixture."""

    def test_creates_variant_directory(self, tmp_path: Path) -> None:
        var = generate_variant_comic(tmp_path)
        assert var.is_dir()

    def test_variant_has_two_pages(self, tmp_path: Path) -> None:
        var = generate_variant_comic(tmp_path)
        assert len(list((var / "pages").iterdir())) == 2

    def test_variant_page_slugs(self, tmp_path: Path) -> None:
        var = generate_variant_comic(tmp_path)
        names = {p.name for p in (var / "pages").iterdir()}
        assert names == {"01_chapter", "02_climax"}

    def test_variant_dimensions(self, tmp_path: Path) -> None:
        from PIL import Image

        var = generate_variant_comic(tmp_path)
        for page_dir in (var / "pages").iterdir():
            img = Image.open(page_dir / "page.png")
            assert img.size == (VARIANT_WIDTH, VARIANT_HEIGHT)

    def test_variant_hashes_differ_from_primary(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        var = generate_variant_comic(tmp_path)
        primary_hash = _hash_path(ed / "pages" / "01_intro" / "page.png")
        variant_hash = _hash_path(var / "pages" / "01_chapter" / "page.png")
        assert primary_hash != variant_hash


# ---------------------------------------------------------------------------
# Hash invalidation using synthetic images
# ---------------------------------------------------------------------------


class TestHashInvalidationWithSyntheticImages:
    """Exercise magazine.hashing against real PIL-generated PNG bytes."""

    def test_hash_changes_when_page_content_changes(self, tmp_path: Path) -> None:
        from magazine.hashing import hash_file

        ed = generate_fake_comic(tmp_path)
        var = generate_variant_comic(tmp_path)
        h_primary = hash_file(ed / "pages" / "01_intro" / "page.png")
        h_variant = hash_file(var / "pages" / "01_chapter" / "page.png")
        assert h_primary != h_variant

    def test_hash_stable_for_identical_images(self, tmp_path: Path) -> None:
        from magazine.hashing import hash_file

        ed1 = generate_fake_comic(tmp_path / "a")
        ed2 = generate_fake_comic(tmp_path / "b")
        h1 = hash_file(ed1 / "pages" / "01_intro" / "page.png")
        h2 = hash_file(ed2 / "pages" / "01_intro" / "page.png")
        assert h1 == h2

    def test_hash_is_sha256(self, tmp_path: Path) -> None:
        from magazine.hashing import hash_file

        ed = generate_fake_comic(tmp_path)
        png = ed / "pages" / "01_intro" / "page.png"
        digest = hash_file(png)
        expected = hashlib.sha256(png.read_bytes()).hexdigest()
        assert digest == expected

    def test_all_three_pages_have_unique_hashes(self, tmp_path: Path) -> None:
        from magazine.hashing import hash_file

        ed = generate_fake_comic(tmp_path)
        hashes = [
            hash_file(ed / "pages" / slug / "page.png")
            for slug in ("01_intro", "02_middle", "03_finale")
        ]
        assert len(set(hashes)) == 3


# ---------------------------------------------------------------------------
# Edition build pipeline (AI stage mocked)
# ---------------------------------------------------------------------------


class TestEditionBuildPipelineWithSyntheticImages:
    """Run build_edition() against synthetic pages; all subprocess calls mocked."""

    def _run_build_edition(self, edition_dir: Path, **kwargs) -> dict:
        mock_ai = MagicMock()
        with (
            patch("magazine.edition.build_page") as m_page,
            patch("magazine.edition.assemble_latex_edition") as m_latex,
        ):
            from magazine.edition import build_edition

            build_edition(edition_dir, **kwargs)
        return {"build_page": m_page, "latex": m_latex}

    def test_build_page_called_for_each_page(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        mocks = self._run_build_edition(ed)
        assert mocks["build_page"].call_count == 3

    def test_build_page_called_in_sorted_order(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        mocks = self._run_build_edition(ed)
        names = [c.args[0].name for c in mocks["build_page"].call_args_list]
        assert names == sorted(names)

    def test_latex_assembly_called_by_default(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        mocks = self._run_build_edition(ed)
        mocks["latex"].assert_called_once()

    def test_latex_skipped_when_disabled(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        mocks = self._run_build_edition(ed, latex_disable=True)
        mocks["latex"].assert_not_called()

    def test_variant_edition_two_pages(self, tmp_path: Path) -> None:
        var = generate_variant_comic(tmp_path)
        mocks = self._run_build_edition(var)
        assert mocks["build_page"].call_count == 2


# ---------------------------------------------------------------------------
# Page build pipeline (all external stages mocked)
# ---------------------------------------------------------------------------


class TestPageBuildPipelineWithSyntheticImages:
    """Run build_page() against real PNG images; all subprocess calls mocked."""

    def _run_build_page(self, page_dir: Path, **kwargs) -> dict:
        mock_ai = MagicMock()
        kwargs.setdefault("ai_stage", mock_ai)
        with (
            patch("magazine.pipeline.gen_page_meta") as m_meta,
            patch("magazine.pipeline.generate_image_assets") as m_images,
            patch("magazine.pipeline.generate_screenplay_assets") as m_screen,
            patch("magazine.pipeline.generate_latex_page") as m_latex,
            patch("magazine.pipeline.generate_size_variants") as m_sizes,
        ):
            from magazine.page import build_page

            build_page(page_dir, **kwargs)
        return {
            "meta": m_meta,
            "images": m_images,
            "ai": mock_ai,
            "screenplay": m_screen,
            "latex": m_latex,
            "sizes": m_sizes,
        }

    def test_all_stages_called_for_each_page(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        for slug in ("01_intro", "02_middle", "03_finale"):
            page_dir = ed / "pages" / slug
            mocks = self._run_build_page(page_dir)
            assert mocks["meta"].call_count == 1
            assert mocks["images"].call_count == 1
            assert mocks["ai"].generate_or_skip.call_count == 1
            assert mocks["screenplay"].call_count == 1
            assert mocks["latex"].call_count == 1
            assert mocks["sizes"].call_count == 1

    def test_artifacts_dir_created(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        page_dir = ed / "pages" / "01_intro"
        self._run_build_page(page_dir)
        assert (page_dir / "artifacts").is_dir()

    def test_sizes_stage_skipped_when_disabled(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        page_dir = ed / "pages" / "01_intro"
        mocks = self._run_build_page(page_dir, sizes_disable=True)
        mocks["sizes"].assert_not_called()

    def test_latex_stage_skipped_when_disabled(self, tmp_path: Path) -> None:
        ed = generate_fake_comic(tmp_path)
        page_dir = ed / "pages" / "01_intro"
        mocks = self._run_build_page(page_dir, latex_disable=True)
        mocks["latex"].assert_not_called()

    def test_variant_page_build(self, tmp_path: Path) -> None:
        var = generate_variant_comic(tmp_path)
        page_dir = var / "pages" / "01_chapter"
        mocks = self._run_build_page(page_dir)
        assert mocks["meta"].call_count == 1


# ---------------------------------------------------------------------------
# Size stage with synthetic images
# ---------------------------------------------------------------------------


class TestSizeStageWithSyntheticImages:
    """Validate size-variant idempotency using real PIL images as source."""

    def _sizes_cfg(self, tmp_path: Path) -> Path:
        p = tmp_path / "sizes.json"
        p.write_text(
            json.dumps(
                {
                    "thumb": {
                        "width": 100,
                        "height": 141,
                        "dpi": 72,
                        "bleed": 0,
                        "safe_margin": 0,
                        "output_suffix": "thumb",
                        "scaling_strategy": "fit",
                    }
                }
            )
        )
        return p

    def test_size_variant_generated_first_run(self, tmp_path: Path) -> None:
        from magazine.assets.sizes import generate_size_variants

        ed = generate_fake_comic(tmp_path)
        page_dir = ed / "pages" / "01_intro"
        artifacts = page_dir / "artifacts"
        artifacts.mkdir()
        cfg = self._sizes_cfg(tmp_path)

        with patch("magazine.assets.sizes.run") as mock_run:
            generate_size_variants(page_dir, artifacts, config_path=cfg)

        assert mock_run.call_count == 1

    def test_no_rerun_when_image_unchanged(self, tmp_path: Path) -> None:
        from magazine.assets.sizes import generate_size_variants

        ed = generate_fake_comic(tmp_path)
        page_dir = ed / "pages" / "01_intro"
        artifacts = page_dir / "artifacts"
        artifacts.mkdir()
        cfg = self._sizes_cfg(tmp_path)

        with patch("magazine.assets.sizes.run") as mock_run:
            generate_size_variants(page_dir, artifacts, config_path=cfg)
            # Simulate the sized output existing so the second call sees it
            sized_dir = artifacts / "sizes" / "thumb"
            sized_dir.mkdir(parents=True, exist_ok=True)
            (sized_dir / "page.png").write_bytes(b"resized")
            generate_size_variants(page_dir, artifacts, config_path=cfg)

        assert mock_run.call_count == 1, "Should not re-run when image is unchanged"

    def test_rerun_when_image_changes(self, tmp_path: Path) -> None:
        from magazine.assets.sizes import generate_size_variants

        ed = generate_fake_comic(tmp_path)
        page_dir = ed / "pages" / "01_intro"
        artifacts = page_dir / "artifacts"
        artifacts.mkdir()
        cfg = self._sizes_cfg(tmp_path)

        with patch("magazine.assets.sizes.run") as mock_run:
            generate_size_variants(page_dir, artifacts, config_path=cfg)
            sized_dir = artifacts / "sizes" / "thumb"
            sized_dir.mkdir(parents=True, exist_ok=True)
            (sized_dir / "page.png").write_bytes(b"resized")
            # Replace page.png with variant content to trigger invalidation
            var = generate_variant_comic(tmp_path)
            (page_dir / "page.png").write_bytes(
                (var / "pages" / "01_chapter" / "page.png").read_bytes()
            )
            generate_size_variants(page_dir, artifacts, config_path=cfg)

        assert mock_run.call_count == 2, "Should re-run when image content changes"

    def test_force_flag_triggers_rerun(self, tmp_path: Path) -> None:
        from magazine.assets.sizes import generate_size_variants

        ed = generate_fake_comic(tmp_path)
        page_dir = ed / "pages" / "01_intro"
        artifacts = page_dir / "artifacts"
        artifacts.mkdir()
        cfg = self._sizes_cfg(tmp_path)

        with patch("magazine.assets.sizes.run") as mock_run:
            generate_size_variants(page_dir, artifacts, config_path=cfg)
            sized_dir = artifacts / "sizes" / "thumb"
            sized_dir.mkdir(parents=True, exist_ok=True)
            (sized_dir / "page.png").write_bytes(b"resized")
            generate_size_variants(page_dir, artifacts, config_path=cfg, force=True)

        assert mock_run.call_count == 2, "force=True must always regenerate"


# ---------------------------------------------------------------------------
# Bundler stage with synthetic images
# ---------------------------------------------------------------------------


class TestBundlerWithSyntheticImages:
    """Run finalize_edition() with synthetic page PNGs staged as masters."""

    def _stage_edition(self, edition_dir: Path) -> None:
        """Copy page PNGs to the final_build_stage directory."""
        from magazine.utils import page_dirs

        stage_dir = edition_dir / "artifacts" / "final_build_stage"
        stage_dir.mkdir(parents=True, exist_ok=True)
        for page_dir in page_dirs(edition_dir):
            slug = page_dir.name
            src = page_dir / "page.png"
            if src.exists():
                import shutil

                shutil.copy2(src, stage_dir / f"{slug}.png")

    def test_finalize_stages_all_pages(self, tmp_path: Path) -> None:
        from magazine.bundler import finalize_edition

        ed = generate_fake_comic(tmp_path)
        with (
            patch("magazine.utils.subprocess.run") as m_sub,
            patch("magazine.bundler.generate_bundle_size_variants"),
        ):
            m_sub.return_value.returncode = 0
            finalize_edition(ed)

        stage_dir = ed / "artifacts" / "final_build_stage"
        staged = sorted(stage_dir.glob("*.png"))
        assert len(staged) == 3

    def test_finalize_creates_publishing_structure(self, tmp_path: Path) -> None:
        from magazine.bundler import finalize_edition

        ed = generate_fake_comic(tmp_path)
        with (
            patch("magazine.utils.subprocess.run") as m_sub,
            patch("magazine.bundler.generate_bundle_size_variants"),
        ):
            m_sub.return_value.returncode = 0
            finalize_edition(ed)

        assert (ed / "publishing" / "digital").is_dir()
        assert (ed / "publishing" / "print").is_dir()

    def test_finalize_writes_meta_json(self, tmp_path: Path) -> None:
        from magazine.bundler import finalize_edition

        ed = generate_fake_comic(tmp_path)
        with (
            patch("magazine.utils.subprocess.run") as m_sub,
            patch("magazine.bundler.generate_bundle_size_variants"),
        ):
            m_sub.return_value.returncode = 0
            finalize_edition(ed)

        meta = json.loads((ed / "publishing" / "meta.json").read_text())
        assert meta["page_count"] == 3
        assert meta["edition_id"] == "edition_fake"

    def test_finalize_variant_two_pages(self, tmp_path: Path) -> None:
        from magazine.bundler import finalize_edition

        var = generate_variant_comic(tmp_path)
        with (
            patch("magazine.utils.subprocess.run") as m_sub,
            patch("magazine.bundler.generate_bundle_size_variants"),
        ):
            m_sub.return_value.returncode = 0
            finalize_edition(var)

        meta = json.loads((var / "publishing" / "meta.json").read_text())
        assert meta["page_count"] == 2

    def test_bundle_size_variants_called(self, tmp_path: Path) -> None:
        from magazine.bundler import finalize_edition

        ed = generate_fake_comic(tmp_path)
        with (
            patch("magazine.utils.subprocess.run") as m_sub,
            patch("magazine.bundler.generate_bundle_size_variants") as m_sizes,
        ):
            m_sub.return_value.returncode = 0
            finalize_edition(ed)

        m_sizes.assert_called_once()

    def test_bundle_size_variants_skipped_when_disabled(self, tmp_path: Path) -> None:
        from magazine.bundler import finalize_edition

        ed = generate_fake_comic(tmp_path)
        with (
            patch("magazine.utils.subprocess.run") as m_sub,
            patch("magazine.bundler.generate_bundle_size_variants") as m_sizes,
        ):
            m_sub.return_value.returncode = 0
            finalize_edition(ed, sizes_disable=True)

        m_sizes.assert_not_called()


# ---------------------------------------------------------------------------
# Metadata integrity with synthetic images
# ---------------------------------------------------------------------------


class TestMetadataIntegrityWithSyntheticImages:
    """Ensure gen_page_meta() writes correct metadata for synthetic pages."""

    def test_meta_json_written(self, tmp_path: Path) -> None:
        from magazine.metadata import gen_page_meta

        ed = generate_fake_comic(tmp_path)
        page_dir = ed / "pages" / "01_intro"
        with patch("magazine.metadata.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="[]")
            gen_page_meta(page_dir)
        assert (page_dir / "meta.json").is_file()

    def test_meta_contains_page_id(self, tmp_path: Path) -> None:
        from magazine.metadata import gen_page_meta

        ed = generate_fake_comic(tmp_path)
        page_dir = ed / "pages" / "02_middle"
        with patch("magazine.metadata.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="[]")
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["page_id"] == "02_middle"

    def test_meta_sequence_index(self, tmp_path: Path) -> None:
        from magazine.metadata import gen_page_meta

        ed = generate_fake_comic(tmp_path)
        page_dir = ed / "pages" / "03_finale"
        with patch("magazine.metadata.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="[]")
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["sequence_index"] == 3

    def test_meta_written_for_all_pages(self, tmp_path: Path) -> None:
        from magazine.metadata import gen_page_meta

        ed = generate_fake_comic(tmp_path)
        for page_dir in sorted((ed / "pages").iterdir()):
            with patch("magazine.metadata.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="[]")
                gen_page_meta(page_dir)
            assert (page_dir / "meta.json").is_file()
