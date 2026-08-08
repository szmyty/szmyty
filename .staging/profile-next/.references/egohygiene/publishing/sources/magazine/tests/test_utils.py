"""Tests for shared utility functions in magazine.utils."""

from pathlib import Path
from unittest.mock import patch

import pytest

from magazine.exceptions import DependencyError
from magazine.utils import _STAGE_TOOLS, page_dirs, timestamp, validate_dependencies


class TestTimestamp:
    """Tests for timestamp()."""

    def test_timestamp_format(self) -> None:
        ts = timestamp()
        assert ts.endswith("Z")
        assert "T" in ts



class TestPageDirs:
    """Tests for page_dirs()."""

    def _make_edition(self, tmp_path: Path, slugs: list[str]) -> Path:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        for slug in slugs:
            (pages / slug).mkdir()
        return edition_dir

    def test_returns_sorted_list(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path, ["03_end", "01_intro", "02_body"])
        result = page_dirs(edition_dir)
        names = [p.name for p in result]
        assert names == ["01_intro", "02_body", "03_end"]

    def test_returns_list_of_paths(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path, ["01_page"])
        result = page_dirs(edition_dir)
        assert all(isinstance(p, Path) for p in result)

    def test_ignores_non_directory_entries(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path, ["01_page"])
        (edition_dir / "pages" / "not_a_dir.txt").write_text("ignored")
        result = page_dirs(edition_dir)
        names = [p.name for p in result]
        assert "not_a_dir.txt" not in names
        assert names == ["01_page"]

    def test_empty_pages_dir_returns_empty_list(self, tmp_path: Path) -> None:
        edition_dir = self._make_edition(tmp_path, [])
        result = page_dirs(edition_dir)
        assert result == []


class TestCheckDependencies:
    """Tests for validate_dependencies()."""

    # ------------------------------------------------------------------ #
    # _STAGE_TOOLS accuracy
    # ------------------------------------------------------------------ #

    def test_pandoc_not_in_any_stage(self) -> None:
        all_stage_tools = [t for tools in _STAGE_TOOLS.values() for t in tools]
        assert "pandoc" not in all_stage_tools

    def test_screenplay_tools_in_stage_map(self) -> None:
        screenplay_tools = _STAGE_TOOLS.get("screenplay", [])
        for tool in ("afterwriting", "scripttool", "wrap"):
            assert tool in screenplay_tools

    # ------------------------------------------------------------------ #
    # validate_dependencies() – stage-aware
    # ------------------------------------------------------------------ #

    def test_validate_raises_when_stage_tool_missing(self) -> None:
        with patch("magazine.utils.shutil.which", return_value=None):
            with pytest.raises(DependencyError):
                validate_dependencies(["images"])

    def test_validate_no_error_when_stage_tools_present(self) -> None:
        with patch("magazine.utils.shutil.which", return_value="/usr/bin/tool"):
            validate_dependencies(["images"])  # should not raise

    def test_validate_screenplay_disabled_skips_afterwriting(self) -> None:
        # Only validate the 'images' stage; screenplay tools should NOT be checked
        def which_side_effect(tool: str) -> str | None:
            if tool in ("afterwriting", "scripttool", "wrap", "jq"):
                return None  # Simulate missing screenplay tools
            return "/usr/bin/tool"

        with patch("magazine.utils.shutil.which", side_effect=which_side_effect):
            # Should not raise because screenplay stage is not active
            validate_dependencies(["images"])

    def test_validate_latex_disabled_skips_latex_engines(self) -> None:
        def which_side_effect(tool: str) -> str | None:
            if tool in ("xelatex", "pdflatex"):
                return None  # Simulate missing LaTeX engines
            return "/usr/bin/tool"

        with patch("magazine.utils.shutil.which", side_effect=which_side_effect):
            # Should not raise because latex stage is not active
            validate_dependencies(["images", "screenplay"])

    def test_validate_ai_disabled_skips_ollama(self) -> None:
        def which_side_effect(tool: str) -> str | None:
            if tool == "ollama":
                return None
            return "/usr/bin/tool"

        with patch("magazine.utils.shutil.which", side_effect=which_side_effect):
            validate_dependencies(["images"])  # ai not in active stages → no error

    def test_validate_sizes_disabled_skips_magick_and_img2pdf(self) -> None:
        def which_side_effect(tool: str) -> str | None:
            if tool in ("magick", "img2pdf"):
                return None
            return "/usr/bin/tool"

        with patch("magazine.utils.shutil.which", side_effect=which_side_effect):
            # Should not raise when only non-image/sizes stages are active
            validate_dependencies(["metadata", "bundle"])

    def test_validate_latex_passes_when_one_engine_present(self) -> None:
        def which_side_effect(tool: str) -> str | None:
            if tool == "xelatex":
                return None  # xelatex missing
            if tool == "pdflatex":
                return "/usr/bin/pdflatex"  # pdflatex present
            return "/usr/bin/tool"

        with patch("magazine.utils.shutil.which", side_effect=which_side_effect):
            validate_dependencies(["latex"])  # should not raise

    def test_validate_latex_fails_when_both_engines_missing(self) -> None:
        def which_side_effect(tool: str) -> str | None:
            if tool in ("xelatex", "pdflatex"):
                return None
            return "/usr/bin/tool"

        with patch("magazine.utils.shutil.which", side_effect=which_side_effect):
            with pytest.raises(DependencyError, match="xelatex or pdflatex"):
                validate_dependencies(["latex"])

    def test_validate_all_stages_when_active_stages_is_none(self) -> None:
        with patch("magazine.utils.shutil.which", return_value="/usr/bin/tool"):
            validate_dependencies(None)  # should not raise

    def test_validate_error_message_contains_tool_name(self) -> None:
        with patch("magazine.utils.shutil.which", return_value=None):
            with pytest.raises(DependencyError, match="afterwriting"):
                validate_dependencies(["screenplay"])

    def test_exif_stage_requires_exiftool(self) -> None:
        def which_side_effect(tool: str) -> str | None:
            if tool == "exiftool":
                return None
            return "/usr/bin/tool"

        with patch("magazine.utils.shutil.which", side_effect=which_side_effect):
            with pytest.raises(DependencyError, match="exiftool"):
                validate_dependencies(["exif"])

    def test_metadata_stage_does_not_require_exiftool(self) -> None:
        def which_side_effect(tool: str) -> str | None:
            if tool == "exiftool":
                return None
            return "/usr/bin/tool"

        with patch("magazine.utils.shutil.which", side_effect=which_side_effect):
            # Should not raise because exiftool is no longer required by metadata stage
            validate_dependencies(["metadata"])

    def test_exif_stage_not_in_metadata_stage_tools(self) -> None:
        assert "exiftool" not in _STAGE_TOOLS.get("metadata", [])

    def test_exiftool_in_exif_stage_tools(self) -> None:
        assert "exiftool" in _STAGE_TOOLS.get("exif", [])
