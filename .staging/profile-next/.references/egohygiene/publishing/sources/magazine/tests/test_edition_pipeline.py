"""Tests for the edition build pipeline (magazine.edition)."""

from pathlib import Path
from unittest.mock import call, patch

import pytest


class TestBuildEdition:
    def test_calls_build_page_for_each_page(self, edition_dir: Path) -> None:
        with patch("magazine.edition.build_page") as m_page, \
             patch("magazine.edition.assemble_latex_edition"):
            from magazine.edition import build_edition
            build_edition(edition_dir)
        assert m_page.call_count == 2

    def test_page_order_sorted(self, edition_dir: Path) -> None:
        with patch("magazine.edition.build_page") as m_page, \
             patch("magazine.edition.assemble_latex_edition"):
            from magazine.edition import build_edition
            build_edition(edition_dir)
        page_names = [c.args[0].name for c in m_page.call_args_list]
        assert page_names == sorted(page_names)

    def test_calls_latex_assembly_by_default(self, edition_dir: Path) -> None:
        with patch("magazine.edition.build_page"), \
             patch("magazine.edition.assemble_latex_edition") as m_latex:
            from magazine.edition import build_edition
            build_edition(edition_dir)
        assert m_latex.call_count == 1

    def test_skips_latex_when_disabled(self, edition_dir: Path) -> None:
        with patch("magazine.edition.build_page"), \
             patch("magazine.edition.assemble_latex_edition") as m_latex:
            from magazine.edition import build_edition
            build_edition(edition_dir, latex_disable=True)
        m_latex.assert_not_called()

    def test_latex_force_passed_to_assembly(self, edition_dir: Path) -> None:
        with patch("magazine.edition.build_page"), \
             patch("magazine.edition.assemble_latex_edition") as m_latex:
            from magazine.edition import build_edition
            build_edition(edition_dir, latex_force=True)
        _, kwargs = m_latex.call_args
        assert kwargs["force"] is True

    def test_latex_safe_mode_passed_to_assembly(self, edition_dir: Path) -> None:
        with patch("magazine.edition.build_page"), \
             patch("magazine.edition.assemble_latex_edition") as m_latex:
            from magazine.edition import build_edition
            build_edition(edition_dir, latex_safe_mode=True)
        _, kwargs = m_latex.call_args
        assert kwargs["safe_mode"] is True

    def test_sizes_flags_passed_to_build_page(self, edition_dir: Path) -> None:
        with patch("magazine.edition.build_page") as m_page, \
             patch("magazine.edition.assemble_latex_edition"):
            from magazine.edition import build_edition
            build_edition(edition_dir, sizes_disable=True, sizes_force=True)
        for c in m_page.call_args_list:
            _, kwargs = c
            assert kwargs["sizes_disable"] is True
            assert kwargs["sizes_force"] is True

    def test_skip_existing_passed_to_build_page(self, edition_dir: Path) -> None:
        with patch("magazine.edition.build_page") as m_page, \
             patch("magazine.edition.assemble_latex_edition"):
            from magazine.edition import build_edition
            build_edition(edition_dir, skip_existing=True)
        for c in m_page.call_args_list:
            _, kwargs = c
            assert kwargs["skip_existing"] is True

    def test_empty_pages_dir_no_build_page_calls(self, tmp_path: Path) -> None:
        e = tmp_path / "empty_edition"
        e.mkdir()
        (e / "pages").mkdir()
        with patch("magazine.edition.build_page") as m_page, \
             patch("magazine.edition.assemble_latex_edition"):
            from magazine.edition import build_edition
            build_edition(e)
        m_page.assert_not_called()
