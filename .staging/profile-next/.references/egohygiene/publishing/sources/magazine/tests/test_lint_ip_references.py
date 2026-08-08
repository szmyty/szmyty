"""Tests for scripts/lint_ip_references.py – IP reference linting logic."""

import json
import sys
from pathlib import Path

import pytest

# Make the scripts/ directory importable without modifying production code.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import lint_ip_references as _module  # noqa: E402

from lint_ip_references import (  # noqa: E402
    EXCLUDE_PATTERNS,
    FORBIDDEN_TERMS,
    SCHEMA_PATTERNS,
    find_schema_files,
    main,
    scan_file,
    should_exclude,
)


# ===========================================================================
# TestShouldExclude
# ===========================================================================


class TestShouldExclude:
    """Tests for should_exclude().

    Note: should_exclude() uses Path.match() which only matches files that are
    exactly ONE level deep inside the excluded directory (e.g. dist/file.json).
    Files nested deeper (e.g. node_modules/pkg/file.json) are NOT excluded by
    the current implementation.
    """

    def test_node_modules_direct_child_is_excluded(self, tmp_path: Path) -> None:
        p = tmp_path / "node_modules" / "meta.json"
        assert should_exclude(p) is True

    def test_git_direct_child_is_excluded(self, tmp_path: Path) -> None:
        p = tmp_path / ".git" / "config"
        assert should_exclude(p) is True

    def test_dist_dir_is_excluded(self, tmp_path: Path) -> None:
        p = tmp_path / "dist" / "bundle.page.json"
        assert should_exclude(p) is True

    def test_build_dir_is_excluded(self, tmp_path: Path) -> None:
        p = tmp_path / "build" / "meta.json"
        assert should_exclude(p) is True

    def test_regular_page_json_is_not_excluded(self, tmp_path: Path) -> None:
        p = tmp_path / "editions" / "01" / "pages" / "01_intro" / "01_intro.page.json"
        assert should_exclude(p) is False

    def test_meta_json_in_edition_is_not_excluded(self, tmp_path: Path) -> None:
        p = tmp_path / "editions" / "01" / "meta.json"
        assert should_exclude(p) is False

    def test_path_not_in_any_excluded_dir_returns_false(self, tmp_path: Path) -> None:
        p = tmp_path / "schemas" / "my_schema.page.json"
        assert should_exclude(p) is False


# ===========================================================================
# TestScanFile
# ===========================================================================


class TestScanFile:
    """Tests for scan_file()."""

    def test_clean_file_returns_no_violations(self, tmp_path: Path) -> None:
        f = tmp_path / "clean.page.json"
        f.write_text(json.dumps({"description": "retro print aesthetic"}))
        result = scan_file(f, FORBIDDEN_TERMS)
        assert result == []

    def test_forbidden_term_is_detected(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.page.json"
        f.write_text('{"description": "fallout vibes"}')
        result = scan_file(f, FORBIDDEN_TERMS)
        assert len(result) == 1
        term, line_num, line_content = result[0]
        assert term == "fallout"
        assert line_num == 1
        assert "fallout" in line_content

    def test_detection_is_case_insensitive(self, tmp_path: Path) -> None:
        f = tmp_path / "upper.page.json"
        f.write_text('{"description": "FALLOUT themed"}')
        result = scan_file(f, FORBIDDEN_TERMS)
        assert len(result) == 1

    def test_mixed_case_detection(self, tmp_path: Path) -> None:
        f = tmp_path / "mixed.page.json"
        f.write_text('{"description": "Fallout inspired"}')
        result = scan_file(f, FORBIDDEN_TERMS)
        assert len(result) == 1

    def test_multiple_violations_on_separate_lines(self, tmp_path: Path) -> None:
        content = "line one\nfallout reference here\nanother fallout mention\n"
        f = tmp_path / "multi.page.json"
        f.write_text(content)
        result = scan_file(f, FORBIDDEN_TERMS)
        assert len(result) == 2

    def test_multiple_violations_correct_line_numbers(self, tmp_path: Path) -> None:
        content = "clean line\nfallout here\nstill clean\nfallout again\n"
        f = tmp_path / "lines.page.json"
        f.write_text(content)
        result = scan_file(f, FORBIDDEN_TERMS)
        line_numbers = [r[1] for r in result]
        assert line_numbers == [2, 4]

    def test_empty_file_returns_no_violations(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.page.json"
        f.write_text("")
        result = scan_file(f, FORBIDDEN_TERMS)
        assert result == []

    def test_custom_forbidden_terms_are_respected(self, tmp_path: Path) -> None:
        f = tmp_path / "custom.page.json"
        f.write_text('{"description": "starwars themed page"}')
        result = scan_file(f, ["starwars"])
        assert len(result) == 1
        assert result[0][0] == "starwars"

    def test_term_not_in_file_returns_empty(self, tmp_path: Path) -> None:
        f = tmp_path / "safe.page.json"
        f.write_text('{"description": "aged paper texture"}')
        result = scan_file(f, ["starwars"])
        assert result == []

    def test_unreadable_file_returns_empty_and_does_not_raise(self, tmp_path: Path) -> None:
        f = tmp_path / "ghost.page.json"
        # File does not exist – should be caught silently
        result = scan_file(f, FORBIDDEN_TERMS)
        assert result == []

    def test_result_tuples_have_correct_structure(self, tmp_path: Path) -> None:
        f = tmp_path / "struct.page.json"
        f.write_text("fallout reference\n")
        result = scan_file(f, FORBIDDEN_TERMS)
        assert len(result) == 1
        term, line_num, line_content = result[0]
        assert isinstance(term, str)
        assert isinstance(line_num, int)
        assert isinstance(line_content, str)

    def test_line_content_is_stripped(self, tmp_path: Path) -> None:
        f = tmp_path / "strip.page.json"
        f.write_text("  fallout reference  \n")
        result = scan_file(f, FORBIDDEN_TERMS)
        assert len(result) == 1
        _, _, line_content = result[0]
        assert not line_content.startswith(" ")
        assert not line_content.endswith(" ")

    def test_empty_forbidden_terms_returns_no_violations(self, tmp_path: Path) -> None:
        f = tmp_path / "any.page.json"
        f.write_text("fallout reference\n")
        result = scan_file(f, [])
        assert result == []

    def test_long_line_content_is_preserved_in_full(self, tmp_path: Path) -> None:
        long_line = "fallout " + ("x" * 200)
        f = tmp_path / "long.page.json"
        f.write_text(long_line + "\n")
        result = scan_file(f, FORBIDDEN_TERMS)
        assert len(result) == 1
        _, _, line_content = result[0]
        # scan_file returns the full stripped line (truncation is in main())
        assert len(line_content) > 100


# ===========================================================================
# TestFindSchemaFiles
# ===========================================================================


class TestFindSchemaFiles:
    """Tests for find_schema_files()."""

    def _make_page_json(self, directory: Path, name: str, content: dict | None = None) -> Path:
        f = directory / f"{name}.page.json"
        f.write_text(json.dumps(content or {}))
        return f

    def _make_meta_json(self, directory: Path, content: dict | None = None) -> Path:
        f = directory / "meta.json"
        f.write_text(json.dumps(content or {}))
        return f

    def test_finds_page_json_files(self, tmp_path: Path) -> None:
        self._make_page_json(tmp_path, "01_intro")
        result = find_schema_files(tmp_path)
        assert any(f.name == "01_intro.page.json" for f in result)

    def test_finds_meta_json_files(self, tmp_path: Path) -> None:
        self._make_meta_json(tmp_path)
        result = find_schema_files(tmp_path)
        assert any(f.name == "meta.json" for f in result)

    def test_finds_nested_page_json_files(self, tmp_path: Path) -> None:
        nested = tmp_path / "editions" / "01" / "pages" / "01_intro"
        nested.mkdir(parents=True)
        self._make_page_json(nested, "01_intro")
        result = find_schema_files(tmp_path)
        assert len(result) == 1

    def test_excludes_node_modules_direct_child(self, tmp_path: Path) -> None:
        nm = tmp_path / "node_modules"
        nm.mkdir()
        self._make_meta_json(nm)
        result = find_schema_files(tmp_path)
        assert result == []

    def test_excludes_git_direct_child(self, tmp_path: Path) -> None:
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        self._make_meta_json(git_dir)
        result = find_schema_files(tmp_path)
        assert result == []

    def test_excludes_dist_directory(self, tmp_path: Path) -> None:
        dist = tmp_path / "dist"
        dist.mkdir()
        self._make_page_json(dist, "page")
        result = find_schema_files(tmp_path)
        assert result == []

    def test_excludes_build_directory(self, tmp_path: Path) -> None:
        build = tmp_path / "build"
        build.mkdir()
        self._make_meta_json(build)
        result = find_schema_files(tmp_path)
        assert result == []

    def test_returns_sorted_paths(self, tmp_path: Path) -> None:
        pages = tmp_path / "pages"
        pages.mkdir()
        self._make_page_json(pages, "03_end")
        self._make_page_json(pages, "01_intro")
        self._make_page_json(pages, "02_body")
        result = find_schema_files(tmp_path)
        assert result == sorted(result)

    def test_empty_directory_returns_empty_list(self, tmp_path: Path) -> None:
        result = find_schema_files(tmp_path)
        assert result == []

    def test_non_schema_files_are_ignored(self, tmp_path: Path) -> None:
        (tmp_path / "README.md").write_text("# readme")
        (tmp_path / "config.yaml").write_text("key: value")
        result = find_schema_files(tmp_path)
        assert result == []

    def test_finds_both_page_json_and_meta_json(self, tmp_path: Path) -> None:
        self._make_page_json(tmp_path, "01_intro")
        self._make_meta_json(tmp_path)
        result = find_schema_files(tmp_path)
        names = {f.name for f in result}
        assert "01_intro.page.json" in names
        assert "meta.json" in names


# ===========================================================================
# TestMain
# ===========================================================================


class TestMain:
    """Integration tests for main().

    main() derives its root_dir from Path(__file__).parent.parent, which
    points at the repository root when run normally.  In tests we monkeypatch
    the module's __file__ attribute to redirect root_dir to tmp_path and also
    monkeypatch find_schema_files to avoid accidentally scanning real files.
    """

    def _setup(self, tmp_path: Path, monkeypatch) -> None:
        """Point main()'s root_dir at tmp_path by redirecting module __file__."""
        fake_script = tmp_path / "scripts" / "lint_ip_references.py"
        fake_script.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(_module, "__file__", str(fake_script))

    def test_exits_zero_when_no_violations(self, tmp_path: Path, monkeypatch) -> None:
        self._setup(tmp_path, monkeypatch)
        f = tmp_path / "clean.page.json"
        f.write_text(json.dumps({"description": "retro print aesthetic"}))
        monkeypatch.setattr(_module, "find_schema_files", lambda _: [f])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    def test_exits_one_when_violations_found(self, tmp_path: Path, monkeypatch) -> None:
        self._setup(tmp_path, monkeypatch)
        f = tmp_path / "bad.page.json"
        f.write_text(json.dumps({"description": "fallout vibes"}))
        monkeypatch.setattr(_module, "find_schema_files", lambda _: [f])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_passed_message_on_clean_run(self, tmp_path: Path, monkeypatch, capsys) -> None:
        self._setup(tmp_path, monkeypatch)
        monkeypatch.setattr(_module, "find_schema_files", lambda _: [])
        with pytest.raises(SystemExit):
            main()
        assert "PASSED" in capsys.readouterr().out

    def test_failed_message_on_violation(self, tmp_path: Path, monkeypatch, capsys) -> None:
        self._setup(tmp_path, monkeypatch)
        f = tmp_path / "bad.page.json"
        f.write_text('{"description": "fallout"}')
        monkeypatch.setattr(_module, "find_schema_files", lambda _: [f])
        with pytest.raises(SystemExit):
            main()
        assert "FAILED" in capsys.readouterr().out

    def test_no_schema_files_exits_zero(self, tmp_path: Path, monkeypatch) -> None:
        self._setup(tmp_path, monkeypatch)
        monkeypatch.setattr(_module, "find_schema_files", lambda _: [])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    def test_violation_count_reported_in_output(self, tmp_path: Path, monkeypatch, capsys) -> None:
        self._setup(tmp_path, monkeypatch)
        f = tmp_path / "bad.page.json"
        f.write_text("fallout line one\nfallout line two\n")
        monkeypatch.setattr(_module, "find_schema_files", lambda _: [f])
        with pytest.raises(SystemExit):
            main()
        out = capsys.readouterr().out
        assert "2" in out  # two violations counted

    def test_multiple_clean_files_exits_zero(self, tmp_path: Path, monkeypatch) -> None:
        self._setup(tmp_path, monkeypatch)
        files = []
        for i in range(3):
            f = tmp_path / f"{i:02d}.page.json"
            f.write_text(json.dumps({"description": "aged paper texture"}))
            files.append(f)
        monkeypatch.setattr(_module, "find_schema_files", lambda _: files)
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
