"""Integration tests for adversarial / edge-case comic fixtures.

These tests exercise the publishing pipeline against intentionally broken or
incomplete editions in order to validate:

- Force behaviour
- Validation logic
- Idempotency guarantees
- Manifest integrity enforcement
- Robust error handling
- Partial rebuild safety

All adversarial editions are generated deterministically via
:mod:`tests.fixtures.generate_adversarial_comic`.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("PIL", reason="Pillow is required for adversarial fixture tests")

from tests.fixtures.generate_adversarial_comic import (
    ADV_HEIGHT,
    ADV_WIDTH,
    generate_scenario_a,
    generate_scenario_b,
    generate_scenario_c,
    generate_scenario_d,
    generate_scenario_e,
    generate_scenario_f,
    generate_scenario_g,
)


# ---------------------------------------------------------------------------
# Fixture generator self-validation
# ---------------------------------------------------------------------------


class TestScenarioAFixture:
    """Scenario A – Missing page.png."""

    def test_creates_edition_directory(self, tmp_path: Path) -> None:
        ed = generate_scenario_a(tmp_path)
        assert ed.is_dir()

    def test_intro_page_dir_exists_without_png(self, tmp_path: Path) -> None:
        ed = generate_scenario_a(tmp_path)
        intro = ed / "pages" / "01_intro"
        assert intro.is_dir()
        assert not (intro / "page.png").exists()

    def test_middle_page_has_valid_png(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_scenario_a(tmp_path)
        img_path = ed / "pages" / "02_middle" / "page.png"
        assert img_path.is_file()
        img = Image.open(img_path)
        assert img.format == "PNG"

    def test_manifest_lists_both_pages(self, tmp_path: Path) -> None:
        ed = generate_scenario_a(tmp_path)
        manifest = json.loads((ed / "manifest.json").read_text())
        assert manifest["pages"] == ["01_intro", "02_middle"]

    def test_deterministic_across_runs(self, tmp_path: Path) -> None:
        ed1 = generate_scenario_a(tmp_path / "r1")
        ed2 = generate_scenario_a(tmp_path / "r2")
        h1 = (ed1 / "pages" / "02_middle" / "page.png").read_bytes()
        h2 = (ed2 / "pages" / "02_middle" / "page.png").read_bytes()
        assert h1 == h2


class TestScenarioBFixture:
    """Scenario B – Corrupt PNG file."""

    def test_corrupt_png_file_exists(self, tmp_path: Path) -> None:
        ed = generate_scenario_b(tmp_path)
        assert (ed / "pages" / "01_intro" / "page.png").is_file()

    def test_corrupt_png_has_png_magic_header(self, tmp_path: Path) -> None:
        ed = generate_scenario_b(tmp_path)
        data = (ed / "pages" / "01_intro" / "page.png").read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_corrupt_png_fails_pil_open(self, tmp_path: Path) -> None:
        from PIL import Image, UnidentifiedImageError

        ed = generate_scenario_b(tmp_path)
        with pytest.raises((UnidentifiedImageError, Exception)):
            img = Image.open(ed / "pages" / "01_intro" / "page.png")
            img.verify()

    def test_middle_page_is_valid(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_scenario_b(tmp_path)
        img = Image.open(ed / "pages" / "02_middle" / "page.png")
        assert img.format == "PNG"

    def test_manifest_lists_both_pages(self, tmp_path: Path) -> None:
        ed = generate_scenario_b(tmp_path)
        manifest = json.loads((ed / "manifest.json").read_text())
        assert manifest["pages"] == ["01_intro", "02_middle"]


class TestScenarioCFixture:
    """Scenario C – Manifest references missing page directory."""

    def test_only_two_page_dirs_exist(self, tmp_path: Path) -> None:
        ed = generate_scenario_c(tmp_path)
        dirs = list((ed / "pages").iterdir())
        assert len(dirs) == 2

    def test_manifest_lists_three_pages(self, tmp_path: Path) -> None:
        ed = generate_scenario_c(tmp_path)
        manifest = json.loads((ed / "manifest.json").read_text())
        assert manifest["pages"] == ["01_intro", "02_middle", "03_finale"]

    def test_missing_dir_is_absent(self, tmp_path: Path) -> None:
        ed = generate_scenario_c(tmp_path)
        assert not (ed / "pages" / "03_finale").exists()

    def test_existing_pages_have_valid_pngs(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_scenario_c(tmp_path)
        for slug in ("01_intro", "02_middle"):
            img = Image.open(ed / "pages" / slug / "page.png")
            assert img.format == "PNG"


class TestScenarioDFixture:
    """Scenario D – Extra folder not in manifest."""

    def test_three_page_dirs_exist(self, tmp_path: Path) -> None:
        ed = generate_scenario_d(tmp_path)
        dirs = list((ed / "pages").iterdir())
        assert len(dirs) == 3

    def test_manifest_lists_only_two_pages(self, tmp_path: Path) -> None:
        ed = generate_scenario_d(tmp_path)
        manifest = json.loads((ed / "manifest.json").read_text())
        assert manifest["pages"] == ["01_intro", "02_middle"]

    def test_unlisted_dir_exists_on_disk(self, tmp_path: Path) -> None:
        ed = generate_scenario_d(tmp_path)
        assert (ed / "pages" / "99_unlisted").is_dir()

    def test_unlisted_dir_has_page_png(self, tmp_path: Path) -> None:
        ed = generate_scenario_d(tmp_path)
        assert (ed / "pages" / "99_unlisted" / "page.png").is_file()


class TestScenarioEFixture:
    """Scenario E – Stale artifacts present."""

    def test_artifacts_dir_exists(self, tmp_path: Path) -> None:
        ed = generate_scenario_e(tmp_path)
        assert (ed / "pages" / "01_intro" / "artifacts").is_dir()

    def test_stale_artifacts_present(self, tmp_path: Path) -> None:
        ed = generate_scenario_e(tmp_path)
        artifacts = ed / "pages" / "01_intro" / "artifacts"
        assert (artifacts / "page.jpg").is_file()
        assert (artifacts / "page.tiff").is_file()
        assert (artifacts / "page.fountain.pdf").is_file()

    def test_page_png_exists_and_is_valid(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_scenario_e(tmp_path)
        img = Image.open(ed / "pages" / "01_intro" / "page.png")
        assert img.format == "PNG"

    def test_stale_artifact_content_differs_from_png(self, tmp_path: Path) -> None:
        ed = generate_scenario_e(tmp_path)
        png_bytes = (ed / "pages" / "01_intro" / "page.png").read_bytes()
        jpg_bytes = (ed / "pages" / "01_intro" / "artifacts" / "page.jpg").read_bytes()
        assert png_bytes != jpg_bytes


class TestScenarioFFixture:
    """Scenario F – Mixed valid / invalid pages."""

    def test_three_page_dirs_exist(self, tmp_path: Path) -> None:
        ed = generate_scenario_f(tmp_path)
        dirs = sorted((ed / "pages").iterdir())
        assert len(dirs) == 3

    def test_valid_pages_have_pngs(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_scenario_f(tmp_path)
        for slug in ("01_intro", "03_finale"):
            img = Image.open(ed / "pages" / slug / "page.png")
            assert img.format == "PNG"

    def test_middle_page_missing_png(self, tmp_path: Path) -> None:
        ed = generate_scenario_f(tmp_path)
        assert not (ed / "pages" / "02_middle" / "page.png").exists()

    def test_manifest_lists_all_three(self, tmp_path: Path) -> None:
        ed = generate_scenario_f(tmp_path)
        manifest = json.loads((ed / "manifest.json").read_text())
        assert manifest["pages"] == ["01_intro", "02_middle", "03_finale"]


class TestScenarioGFixture:
    """Scenario G – Inconsistent page naming."""

    def test_three_page_dirs_exist(self, tmp_path: Path) -> None:
        ed = generate_scenario_g(tmp_path)
        dirs = list((ed / "pages").iterdir())
        assert len(dirs) == 3

    def test_non_prefixed_dirs_exist(self, tmp_path: Path) -> None:
        ed = generate_scenario_g(tmp_path)
        assert (ed / "pages" / "intro").is_dir()
        assert (ed / "pages" / "final").is_dir()

    def test_prefixed_dir_exists(self, tmp_path: Path) -> None:
        ed = generate_scenario_g(tmp_path)
        assert (ed / "pages" / "02_middle").is_dir()

    def test_all_pages_have_pngs(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_scenario_g(tmp_path)
        for slug in ("intro", "02_middle", "final"):
            img = Image.open(ed / "pages" / slug / "page.png")
            assert img.format == "PNG"

    def test_manifest_reflects_bad_names(self, tmp_path: Path) -> None:
        ed = generate_scenario_g(tmp_path)
        manifest = json.loads((ed / "manifest.json").read_text())
        assert "intro" in manifest["pages"]
        assert "final" in manifest["pages"]


# ---------------------------------------------------------------------------
# PNG validity helper shared across scenarios
# ---------------------------------------------------------------------------


class TestAdversarialPngDimensions:
    """Confirm adversarial valid PNGs use ADV_WIDTH × ADV_HEIGHT dimensions."""

    def test_scenario_a_valid_page_dimensions(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_scenario_a(tmp_path)
        img = Image.open(ed / "pages" / "02_middle" / "page.png")
        assert img.size == (ADV_WIDTH, ADV_HEIGHT)

    def test_scenario_b_valid_page_dimensions(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_scenario_b(tmp_path)
        img = Image.open(ed / "pages" / "02_middle" / "page.png")
        assert img.size == (ADV_WIDTH, ADV_HEIGHT)

    def test_scenario_f_valid_page_dimensions(self, tmp_path: Path) -> None:
        from PIL import Image

        ed = generate_scenario_f(tmp_path)
        img = Image.open(ed / "pages" / "01_intro" / "page.png")
        assert img.size == (ADV_WIDTH, ADV_HEIGHT)


# ---------------------------------------------------------------------------
# Determinism across scenarios
# ---------------------------------------------------------------------------


class TestAdversarialDeterminism:
    """Verify that every scenario generator is deterministic."""

    @pytest.mark.parametrize(
        "generator",
        [
            generate_scenario_a,
            generate_scenario_b,
            generate_scenario_c,
            generate_scenario_d,
            generate_scenario_e,
            generate_scenario_f,
            generate_scenario_g,
        ],
    )
    def test_manifest_identical_across_runs(self, tmp_path: Path, generator) -> None:
        ed1 = generator(tmp_path / "r1")
        ed2 = generator(tmp_path / "r2")
        m1 = (ed1 / "manifest.json").read_text()
        m2 = (ed2 / "manifest.json").read_text()
        assert m1 == m2

    def test_scenario_e_png_identical_across_runs(self, tmp_path: Path) -> None:
        ed1 = generate_scenario_e(tmp_path / "r1")
        ed2 = generate_scenario_e(tmp_path / "r2")
        b1 = (ed1 / "pages" / "01_intro" / "page.png").read_bytes()
        b2 = (ed2 / "pages" / "01_intro" / "page.png").read_bytes()
        assert b1 == b2


# ---------------------------------------------------------------------------
# Pipeline behaviour: scenario A (missing page.png)
# ---------------------------------------------------------------------------


class TestPipelineScenarioA:
    """Pipeline behaviour when page.png is absent."""

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

    def test_build_valid_page_succeeds(self, tmp_path: Path) -> None:
        """The valid page (02_middle) should build without error."""
        ed = generate_scenario_a(tmp_path)
        mocks = self._run_build_page(ed / "pages" / "02_middle")
        assert mocks["meta"].call_count == 1

    def test_artifacts_dir_created_for_valid_page(self, tmp_path: Path) -> None:
        ed = generate_scenario_a(tmp_path)
        page_dir = ed / "pages" / "02_middle"
        self._run_build_page(page_dir)
        assert (page_dir / "artifacts").is_dir()

    def test_force_clears_artifacts_on_valid_page(self, tmp_path: Path) -> None:
        ed = generate_scenario_a(tmp_path)
        page_dir = ed / "pages" / "02_middle"
        artifacts = page_dir / "artifacts"
        artifacts.mkdir()
        sentinel = artifacts / "old_file.txt"
        sentinel.write_text("stale")

        self._run_build_page(page_dir, force=True)

        assert not sentinel.exists()


# ---------------------------------------------------------------------------
# Pipeline behaviour: scenario E (stale artifacts)
# ---------------------------------------------------------------------------


class TestPipelineScenarioE:
    """Build pipeline respects force flag and stale artifact state."""

    def _run_build_page(self, page_dir: Path, **kwargs) -> dict:
        mock_ai = MagicMock()
        kwargs.setdefault("ai_stage", mock_ai)
        with (
            patch("magazine.pipeline.gen_page_meta"),
            patch("magazine.pipeline.generate_image_assets"),
            patch("magazine.pipeline.generate_screenplay_assets"),
            patch("magazine.pipeline.generate_latex_page"),
            patch("magazine.pipeline.generate_size_variants") as m_sizes,
        ):
            from magazine.page import build_page

            build_page(page_dir, **kwargs)
        return {"sizes": m_sizes}

    def test_force_removes_stale_artifacts(self, tmp_path: Path) -> None:
        """force=True must wipe the existing artifacts directory."""
        ed = generate_scenario_e(tmp_path)
        page_dir = ed / "pages" / "01_intro"
        stale_jpg = page_dir / "artifacts" / "page.jpg"
        assert stale_jpg.is_file()  # pre-condition: stale artifact present

        self._run_build_page(page_dir, force=True)

        # After build_page with force=True the old artifacts dir is recreated
        # empty (stale_jpg was wiped by shutil.rmtree then artifacts.mkdir)
        assert not stale_jpg.exists()

    def test_no_force_preserves_existing_artifacts_dir(self, tmp_path: Path) -> None:
        """Without force the artifacts directory should survive the build."""
        ed = generate_scenario_e(tmp_path)
        page_dir = ed / "pages" / "01_intro"
        stale_jpg = page_dir / "artifacts" / "page.jpg"
        assert stale_jpg.is_file()

        self._run_build_page(page_dir, force=False)

        assert (page_dir / "artifacts").is_dir()


# ---------------------------------------------------------------------------
# Pipeline behaviour: scenario F (mixed pages)
# ---------------------------------------------------------------------------


class TestPipelineScenarioF:
    """Edition pipeline with mixed valid / invalid pages."""

    def _run_build_edition(self, edition_dir: Path, **kwargs) -> dict:
        with (
            patch("magazine.edition.build_page") as m_page,
            patch("magazine.edition.assemble_latex_edition") as m_latex,
        ):
            from magazine.edition import build_edition

            build_edition(edition_dir, **kwargs)
        return {"build_page": m_page, "latex": m_latex}

    def test_build_edition_calls_build_page_for_all_dirs(self, tmp_path: Path) -> None:
        """build_edition iterates all page directories regardless of page.png."""
        ed = generate_scenario_f(tmp_path)
        mocks = self._run_build_edition(ed)
        # 3 page dirs exist on disk
        assert mocks["build_page"].call_count == 3

    def test_build_edition_pages_called_in_sorted_order(self, tmp_path: Path) -> None:
        ed = generate_scenario_f(tmp_path)
        mocks = self._run_build_edition(ed)
        names = [c.args[0].name for c in mocks["build_page"].call_args_list]
        assert names == sorted(names)

    def test_latex_disabled_skips_assembly(self, tmp_path: Path) -> None:
        ed = generate_scenario_f(tmp_path)
        mocks = self._run_build_edition(ed, latex_disable=True)
        mocks["latex"].assert_not_called()


# ---------------------------------------------------------------------------
# Manifest integrity checks
# ---------------------------------------------------------------------------


class TestManifestIntegrity:
    """Structural assertions on adversarial manifests."""

    def test_scenario_c_manifest_references_nonexistent_page(
        self, tmp_path: Path
    ) -> None:
        ed = generate_scenario_c(tmp_path)
        manifest = json.loads((ed / "manifest.json").read_text())
        listed = set(manifest["pages"])
        on_disk = {p.name for p in (ed / "pages").iterdir()}
        # at least one manifest entry has no corresponding directory
        assert listed - on_disk, "Expected at least one missing page directory"

    def test_scenario_d_disk_has_more_dirs_than_manifest(
        self, tmp_path: Path
    ) -> None:
        ed = generate_scenario_d(tmp_path)
        manifest = json.loads((ed / "manifest.json").read_text())
        listed = set(manifest["pages"])
        on_disk = {p.name for p in (ed / "pages").iterdir()}
        # at least one on-disk directory is not in manifest
        assert on_disk - listed, "Expected at least one unlisted page directory"

    def test_all_manifests_have_edition_key(self, tmp_path: Path) -> None:
        generators = [
            generate_scenario_a,
            generate_scenario_b,
            generate_scenario_c,
            generate_scenario_d,
            generate_scenario_e,
            generate_scenario_f,
            generate_scenario_g,
        ]
        for i, gen in enumerate(generators):
            ed = gen(tmp_path / f"ed{i}")
            manifest = json.loads((ed / "manifest.json").read_text())
            assert "edition" in manifest
            assert "pages" in manifest

    def test_all_manifests_are_valid_json(self, tmp_path: Path) -> None:
        generators = [
            generate_scenario_a,
            generate_scenario_b,
            generate_scenario_c,
            generate_scenario_d,
            generate_scenario_e,
            generate_scenario_f,
            generate_scenario_g,
        ]
        for i, gen in enumerate(generators):
            ed = gen(tmp_path / f"ed{i}")
            raw = (ed / "manifest.json").read_text()
            data = json.loads(raw)
            assert isinstance(data, dict)
