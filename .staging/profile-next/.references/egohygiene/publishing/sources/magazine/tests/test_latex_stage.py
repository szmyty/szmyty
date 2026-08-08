"""Tests for the LaTeX asset generation stage (magazine.assets.latex)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest


class TestLatexHelpers:
    def test_latex_config_hash_deterministic(self) -> None:
        from magazine.assets.latex import _latex_config_hash
        h1 = _latex_config_hash("xelatex", False, "0.25in")
        h2 = _latex_config_hash("xelatex", False, "0.25in")
        assert h1 == h2
        assert len(h1) == 16

    def test_latex_config_hash_differs_on_change(self) -> None:
        from magazine.assets.latex import _latex_config_hash
        h1 = _latex_config_hash("xelatex", False, "0.25in")
        h2 = _latex_config_hash("pdflatex", False, "0.25in")
        h3 = _latex_config_hash("xelatex", True, "0.25in")
        h4 = _latex_config_hash("xelatex", False, "0.5in")
        assert h1 != h2
        assert h1 != h3
        assert h1 != h4

    def test_page_tex_content_full_bleed(self) -> None:
        from magazine.assets.latex import _page_tex_content
        tex = _page_tex_content(
            "../page.png",
            safe_mode=False,
            safe_margin="0.25in",
            paper_width="8.5in",
            paper_height="11in",
        )
        assert "margin=0in" in tex
        assert "../page.png" in tex
        assert "\\includegraphics" in tex
        assert "\\documentclass" in tex
        assert "geometry" in tex

    def test_page_tex_content_safe_mode(self) -> None:
        from magazine.assets.latex import _page_tex_content
        tex = _page_tex_content(
            "../page.png",
            safe_mode=True,
            safe_margin="0.25in",
            paper_width="8.5in",
            paper_height="11in",
        )
        assert "margin=0.25in" in tex
        assert "margin=0in" not in tex

    def test_edition_tex_content_page_breaks(self) -> None:
        from magazine.assets.latex import _edition_tex_content
        paths = ["../pages/01_a/page.png", "../pages/02_b/page.png", "../pages/03_c/page.png"]
        tex = _edition_tex_content(
            paths,
            safe_mode=False,
            safe_margin="0.25in",
            paper_width="8.5in",
            paper_height="11in",
        )
        assert tex.count("\\clearpage") == 2  # n-1 clearpage for n pages
        assert tex.count("\\includegraphics") == 3
        for p in paths:
            assert p in tex

    def test_edition_tex_content_single_page_no_clearpage(self) -> None:
        from magazine.assets.latex import _edition_tex_content
        tex = _edition_tex_content(
            ["../pages/01_a/page.png"],
            safe_mode=False,
            safe_margin="0.25in",
            paper_width="8.5in",
            paper_height="11in",
        )
        assert "\\clearpage" not in tex

    def test_page_set_hash_deterministic(self, tmp_path: Path) -> None:
        from magazine.assets.latex import _page_set_hash
        dirs = [tmp_path / "01_a", tmp_path / "02_b"]
        assert _page_set_hash(dirs) == _page_set_hash(dirs)

    def test_page_set_hash_order_sensitive(self, tmp_path: Path) -> None:
        from magazine.assets.latex import _page_set_hash
        d1 = tmp_path / "01_a"
        d2 = tmp_path / "02_b"
        assert _page_set_hash([d1, d2]) != _page_set_hash([d2, d1])


class TestGenerateLatexPage:
    def test_skips_when_no_page_png(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        generate_latex_page(tmp_path, artifacts)
        assert not (artifacts / "page.tex").exists()

    def test_generates_tex_when_png_exists(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        (tmp_path / "page.png").write_bytes(b"fake png")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.latex._compile_latex"):
            generate_latex_page(tmp_path, artifacts)
        assert (artifacts / "page.tex").exists()
        tex = (artifacts / "page.tex").read_text()
        assert "../page.png" in tex

    def test_updates_build_state_after_generation(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        img = tmp_path / "page.png"
        img.write_bytes(b"fake png data")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.latex._compile_latex"):
            generate_latex_page(tmp_path, artifacts)
        build_state = json.loads((tmp_path / ".build_state.json").read_text())
        assert "latex_generated_at" not in build_state, (
            "latex_generated_at is a timestamp and must not appear in .build_state.json"
        )
        assert build_state["latex_layout_mode"] == "full_bleed"
        assert "latex_page_png_hash" in build_state
        assert "latex_config_hash" in build_state

    def test_safe_mode_written_to_build_state(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        (tmp_path / "page.png").write_bytes(b"fake png data")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.latex._compile_latex"):
            generate_latex_page(tmp_path, artifacts, safe_mode=True)
        build_state = json.loads((tmp_path / ".build_state.json").read_text())
        assert build_state["latex_layout_mode"] == "safe_margin"

    def test_idempotent_when_hash_unchanged(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        img = tmp_path / "page.png"
        img.write_bytes(b"stable png data")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.latex._compile_latex") as mock_compile:
            generate_latex_page(tmp_path, artifacts)
            generate_latex_page(tmp_path, artifacts)
        assert mock_compile.call_count == 1

    def test_force_reruns_compilation(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        img = tmp_path / "page.png"
        img.write_bytes(b"stable png data")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.latex._compile_latex") as mock_compile:
            generate_latex_page(tmp_path, artifacts)
            generate_latex_page(tmp_path, artifacts, force=True)
        assert mock_compile.call_count == 2

    def test_regenerates_when_png_changes(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        img = tmp_path / "page.png"
        img.write_bytes(b"original png data")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.latex._compile_latex") as mock_compile:
            generate_latex_page(tmp_path, artifacts)
            img.write_bytes(b"updated png data")
            generate_latex_page(tmp_path, artifacts)
        assert mock_compile.call_count == 2


class TestAssembleLatexEdition:
    def _make_edition(self, tmp_path: Path, page_names: list[str]) -> Path:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages_root = edition_dir / "pages"
        pages_root.mkdir()
        for name in page_names:
            p = pages_root / name
            p.mkdir()
            (p / "page.png").write_bytes(b"fake png")
        return edition_dir

    def test_skips_when_no_pages(self, tmp_path: Path) -> None:
        from magazine.assets.latex import assemble_latex_edition
        edition_dir = tmp_path / "edition_empty"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        assemble_latex_edition(edition_dir)
        assert not (edition_dir / "build").exists()

    def test_generates_edition_tex(self, tmp_path: Path) -> None:
        from magazine.assets.latex import assemble_latex_edition
        edition_dir = self._make_edition(tmp_path, ["01_intro", "02_body"])
        with patch("magazine.assets.latex._compile_latex"):
            assemble_latex_edition(edition_dir)
        tex_path = edition_dir / "build" / "edition_01.tex"
        assert tex_path.exists()
        tex = tex_path.read_text()
        assert "../pages/01_intro/page.png" in tex
        assert "../pages/02_body/page.png" in tex
        assert tex.count("\\clearpage") == 1  # n-1 for 2 pages

    def test_page_order_preserved(self, tmp_path: Path) -> None:
        from magazine.assets.latex import assemble_latex_edition
        edition_dir = self._make_edition(tmp_path, ["03_last", "01_first", "02_middle"])
        with patch("magazine.assets.latex._compile_latex"):
            assemble_latex_edition(edition_dir)
        tex = (edition_dir / "build" / "edition_01.tex").read_text()
        pos_first = tex.index("01_first")
        pos_middle = tex.index("02_middle")
        pos_last = tex.index("03_last")
        assert pos_first < pos_middle < pos_last

    def test_idempotent_skips_second_run(self, tmp_path: Path) -> None:
        from magazine.assets.latex import assemble_latex_edition
        edition_dir = self._make_edition(tmp_path, ["01_a", "02_b"])
        with patch("magazine.assets.latex._compile_latex") as mock_compile:
            assemble_latex_edition(edition_dir)
            assemble_latex_edition(edition_dir)
        assert mock_compile.call_count == 1

    def test_force_reruns(self, tmp_path: Path) -> None:
        from magazine.assets.latex import assemble_latex_edition
        edition_dir = self._make_edition(tmp_path, ["01_a"])
        with patch("magazine.assets.latex._compile_latex") as mock_compile:
            assemble_latex_edition(edition_dir)
            assemble_latex_edition(edition_dir, force=True)
        assert mock_compile.call_count == 2

    def test_writes_build_state_json(self, tmp_path: Path) -> None:
        from magazine.assets.latex import assemble_latex_edition
        edition_dir = self._make_edition(tmp_path, ["01_a"])
        with patch("magazine.assets.latex._compile_latex"):
            assemble_latex_edition(edition_dir)
        meta_path = edition_dir / "build" / ".build_state.json"
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text())
        assert meta["edition_id"] == "edition_01"
        assert "page_set_hash" in meta
        assert "latex_config_hash" in meta

    def test_edition_build_state_excludes_timestamps(self, tmp_path: Path) -> None:
        from magazine.assets.latex import assemble_latex_edition
        edition_dir = self._make_edition(tmp_path, ["01_a"])
        with patch("magazine.assets.latex._compile_latex"):
            assemble_latex_edition(edition_dir)
        meta = json.loads((edition_dir / "build" / ".build_state.json").read_text())
        timestamp_fields = {"generated_at", "latex_generated_at", "created_at"}
        for field in timestamp_fields:
            assert field not in meta, (
                f"Timestamp field '{field}' must not appear in .build_state.json"
            )


class TestBuildStateTimestampBoundary:
    """Verify that .build_state.json contains only deterministic fields."""

    def test_page_build_state_excludes_timestamps(self, tmp_path: Path) -> None:
        from magazine.assets.latex import generate_latex_page
        (tmp_path / "page.png").write_bytes(b"data")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        with patch("magazine.assets.latex._compile_latex"):
            generate_latex_page(tmp_path, artifacts)
        build_state = json.loads((tmp_path / ".build_state.json").read_text())
        timestamp_fields = {"latex_generated_at", "generated_at", "created_at"}
        for field in timestamp_fields:
            assert field not in build_state, (
                f"Timestamp field '{field}' must not appear in .build_state.json"
            )

    def test_hash_invalidation_unaffected_by_injected_timestamps(self, tmp_path: Path) -> None:
        """Hash invalidation checks must be stable even when legacy timestamp
        fields are present in an existing .build_state.json."""
        from magazine.assets.latex import generate_latex_page, _latex_config_hash
        from magazine.hashing import hash_file
        img = tmp_path / "page.png"
        img.write_bytes(b"stable png data")
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()

        # Simulate an older .build_state.json that contains a timestamp
        (artifacts / "page.tex").write_text("old tex content")
        import shutil
        engine = "pdflatex" if shutil.which("pdflatex") else "xelatex"
        (tmp_path / ".build_state.json").write_text(
            json.dumps({
                "latex_page_png_hash": hash_file(img),
                "latex_config_hash": _latex_config_hash(engine, False, "0.25in"),
                "latex_generated_at": "2024-01-01T00:00:00Z",  # legacy field
            })
        )
        with patch("magazine.assets.latex._compile_latex") as mock_compile, \
             patch("magazine.assets.latex._resolve_engine", return_value=engine):
            generate_latex_page(tmp_path, artifacts)

        # No recompilation: hash fields match, timestamp is irrelevant
        assert mock_compile.call_count == 0
