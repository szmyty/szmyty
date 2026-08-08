"""Tests for the edition bundler / finalize stage (magazine.bundler)."""

import json
from pathlib import Path
from unittest.mock import patch, call, MagicMock

import pytest

from magazine.exceptions import EditionBuildError

# Minimal valid 1×1 white RGB PNG – accepted by Pillow and the cbz library.
_MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff"
    b"?\x00\x05\xfe\x02\xfe\r\xefF\xb8\x00\x00\x00\x00IEND\xaeB`\x82"
)


class TestFinalizeEdition:
    """Tests for finalize_edition() with subprocess mocked out."""

    def _make_edition(self, tmp_path: Path, page_count: int = 2) -> Path:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        for i in range(1, page_count + 1):
            p = pages / f"{i:02d}_page"
            p.mkdir()
            (p / "page.png").write_bytes(_MINIMAL_PNG)
        return edition_dir

    def _run_finalize(self, edition_dir: Path, **kwargs) -> None:
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants") as m_sizes:
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir, **kwargs)
        return m_sub, m_sizes

    def test_raises_when_page_png_missing(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        p = pages / "01_page"
        p.mkdir()
        # No page.png written
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run"), \
             patch("magazine.bundler.generate_bundle_size_variants"):
            with pytest.raises(EditionBuildError, match="Missing page.png"):
                finalize_edition(edition_dir, force=False)

    def test_force_continues_despite_missing_png(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        p = pages / "01_page"
        p.mkdir()
        # No page.png → force=True should not raise
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir, force=True)  # should not raise

    def test_creates_pub_dir_structure(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        assert (edition_dir / "publishing" / "digital").is_dir()
        assert (edition_dir / "publishing" / "print").is_dir()

    def test_stages_page_pngs(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        stage_dir = edition_dir / "artifacts" / "final_build_stage"
        staged = list(stage_dir.glob("*.png"))
        assert len(staged) == 2

    def test_writes_publishing_meta_json(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        meta_path = edition_dir / "publishing" / "meta.json"
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text())
        assert meta["edition_id"] == "edition_01"
        assert meta["page_count"] == 2
        assert "published_at" in meta
        assert "format_version" in meta
        assert "publisher" in meta
        assert "author" in meta

    def test_calls_cbz_command(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        cbz_path = edition_dir / "publishing" / "digital" / "comic.cbz"
        assert cbz_path.exists(), "comic.cbz must be created by the Python cbz library"
        assert cbz_path.stat().st_size > 0
        commands = [c.args[0] for c in m_sub.call_args_list]
        assert not any(args[0] == "zip" for args in commands), "zip subprocess must not be called"

    def test_calls_reader_pdf_command(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        commands = [c.args[0] for c in m_sub.call_args_list]
        assert any(args[0] == "img2pdf" for args in commands)

    def test_skips_size_variants_when_disabled(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants") as m_sizes:
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir, sizes_disable=True)
        m_sizes.assert_not_called()

    def test_calls_size_variants_by_default(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants") as m_sizes:
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        m_sizes.assert_called_once()

    def test_sizes_force_passed_to_variants(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants") as m_sizes:
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir, sizes_force=True)
        _, kwargs = m_sizes.call_args
        assert kwargs["force"] is True

    def test_page_count_in_meta_matches_pages(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path, page_count=3)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        meta = json.loads((edition_dir / "publishing" / "meta.json").read_text())
        assert meta["page_count"] == 3

    def test_tiff_files_staged_when_present(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path, page_count=1)
        pages = edition_dir / "pages"
        page_dir = list(pages.iterdir())[0]
        (page_dir / "artifacts").mkdir()
        (page_dir / "artifacts" / "page.tiff").write_bytes(b"fake tiff")
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        stage_dir = edition_dir / "artifacts" / "final_build_stage"
        tiffs = list(stage_dir.glob("*.tiff"))
        assert len(tiffs) == 1

    def test_press_pdf_attempted_when_tiffs_present(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path, page_count=1)
        pages = edition_dir / "pages"
        page_dir = list(pages.iterdir())[0]
        (page_dir / "artifacts").mkdir()
        (page_dir / "artifacts" / "page.tiff").write_bytes(b"fake tiff")
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        # img2pdf should be called twice: reader.pdf + press.pdf
        img2pdf_calls = [
            c for c in m_sub.call_args_list if c.args[0][0] == "img2pdf"
        ]
        assert len(img2pdf_calls) == 2

    def test_stage_dir_nested_subdirs_are_removed(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        stage_dir = edition_dir / "artifacts" / "final_build_stage"
        stage_dir.mkdir(parents=True, exist_ok=True)
        # Create a nested subdirectory with a file inside stage_dir
        nested = stage_dir / "subdir" / "deep"
        nested.mkdir(parents=True)
        (nested / "stale.txt").write_text("stale")
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        # The nested subdirectory must be gone after finalize
        assert not (stage_dir / "subdir").exists()

    def test_repeated_finalize_does_not_accumulate_stale_files(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition

        def run_finalize():
            with patch("magazine.utils.subprocess.run") as m_sub, \
                 patch("magazine.bundler.generate_bundle_size_variants"):
                m_sub.return_value.returncode = 0
                finalize_edition(edition_dir)

        run_finalize()
        stage_dir = edition_dir / "artifacts" / "final_build_stage"
        first_run_files = set(p.name for p in stage_dir.iterdir())

        # Inject a stale file that shouldn't persist
        (stage_dir / "stale_artifact.png").write_bytes(b"stale")
        run_finalize()
        second_run_files = set(p.name for p in stage_dir.iterdir())

        assert "stale_artifact.png" not in second_run_files
        assert first_run_files == second_run_files

    def test_dry_run_does_not_delete_stage_dir_contents(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        stage_dir = edition_dir / "artifacts" / "final_build_stage"
        stage_dir.mkdir(parents=True, exist_ok=True)
        existing_file = stage_dir / "existing.png"
        existing_file.write_bytes(_MINIMAL_PNG)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"):
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir, dry_run=True)
        # The pre-existing file must still be present in dry-run mode
        assert existing_file.exists()

    def test_assemble_latex_edition_called_during_finalize(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"), \
             patch("magazine.bundler.assemble_latex_edition") as m_latex:
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir)
        m_latex.assert_called_once()
        assert m_latex.call_args.args[0] == edition_dir.resolve()
        assert m_latex.call_args.kwargs["force"] is False

    def test_assemble_latex_edition_receives_force_flag(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path)
        from magazine.bundler import finalize_edition
        with patch("magazine.utils.subprocess.run") as m_sub, \
             patch("magazine.bundler.generate_bundle_size_variants"), \
             patch("magazine.bundler.assemble_latex_edition") as m_latex:
            m_sub.return_value.returncode = 0
            finalize_edition(edition_dir, force=True)
        m_latex.assert_called_once()
        assert m_latex.call_args.kwargs["force"] is True
