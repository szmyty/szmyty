"""
Tests for profile/validate_assets.py.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------
# Load module under test
# ---------------------------------------------------------------------------


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_assets",
        Path(__file__).parents[1] / "profile" / "validate_assets.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


va = _load_validator()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MINIMAL_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <title>Test title</title>
  <rect width="100" height="100" fill="#ffffff"/>
</svg>
"""

_REQUIRED_SVG_FILES = ("banner-light.svg", "banner-dark.svg", "mark.svg", "divider.svg")


def _write_minimal_svg(path: Path) -> None:
    path.write_text(_MINIMAL_SVG, encoding="utf-8")


def _populate_valid_dir(d: Path) -> None:
    """Populate *d* with a passing set of asset files."""
    for name in _REQUIRED_SVG_FILES:
        _write_minimal_svg(d / name)
    (d / "README.md").write_text("# Assets\n", encoding="utf-8")
    (d / "ASSET-BRIEF.md").write_text("# Briefs\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# check_presence_and_extension
# ---------------------------------------------------------------------------


class TestCheckPresenceAndExtension:
    def test_all_present(self, tmp_path):
        _populate_valid_dir(tmp_path)
        assert va.check_presence_and_extension(tmp_path) == []

    def test_missing_banner_light(self, tmp_path):
        _populate_valid_dir(tmp_path)
        (tmp_path / "banner-light.svg").unlink()
        errors = va.check_presence_and_extension(tmp_path)
        assert any("banner-light.svg" in e for e in errors)

    def test_missing_all_svgs(self, tmp_path):
        # No files at all
        (tmp_path / "README.md").write_text("# x\n")
        (tmp_path / "ASSET-BRIEF.md").write_text("# x\n")
        errors = va.check_presence_and_extension(tmp_path)
        assert len(errors) >= 4


# ---------------------------------------------------------------------------
# check_file_sizes
# ---------------------------------------------------------------------------


class TestCheckFileSizes:
    def test_within_budget(self, tmp_path):
        _populate_valid_dir(tmp_path)
        assert va.check_file_sizes(tmp_path) == []

    def test_exceeds_divider_budget(self, tmp_path):
        _populate_valid_dir(tmp_path)
        # Write more than 8 KB to divider.svg
        (tmp_path / "divider.svg").write_text("x" * (9 * 1024), encoding="utf-8")
        errors = va.check_file_sizes(tmp_path)
        assert any("divider.svg" in e and "budget" in e for e in errors)


# ---------------------------------------------------------------------------
# check_svg
# ---------------------------------------------------------------------------


class TestCheckSvg:
    def test_valid_svg(self, tmp_path):
        p = tmp_path / "test.svg"
        _write_minimal_svg(p)
        assert va.check_svg(p) == []

    def test_missing_viewbox(self, tmp_path):
        p = tmp_path / "test.svg"
        p.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><title>T</title></svg>',
            encoding="utf-8",
        )
        errors = va.check_svg(p)
        assert any("viewBox" in e for e in errors)

    def test_missing_title(self, tmp_path):
        p = tmp_path / "test.svg"
        p.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect/></svg>',
            encoding="utf-8",
        )
        errors = va.check_svg(p)
        assert any("title" in e.lower() for e in errors)

    def test_empty_title(self, tmp_path):
        p = tmp_path / "test.svg"
        p.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            "<title>  </title></svg>",
            encoding="utf-8",
        )
        errors = va.check_svg(p)
        assert any("empty" in e.lower() for e in errors)

    def test_script_element_rejected(self, tmp_path):
        p = tmp_path / "test.svg"
        p.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            "<title>T</title><script>alert(1)</script></svg>",
            encoding="utf-8",
        )
        errors = va.check_svg(p)
        assert any("script" in e.lower() for e in errors)

    def test_javascript_url_rejected(self, tmp_path):
        p = tmp_path / "test.svg"
        p.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            '<title>T</title><a href="javascript:void(0)"/></svg>',
            encoding="utf-8",
        )
        errors = va.check_svg(p)
        assert any("javascript:" in e.lower() for e in errors)

    def test_invalid_xml(self, tmp_path):
        p = tmp_path / "test.svg"
        p.write_text("<svg><unclosed>", encoding="utf-8")
        errors = va.check_svg(p)
        assert any("parse error" in e.lower() for e in errors)

    def test_non_svg_root_rejected(self, tmp_path):
        p = tmp_path / "test.svg"
        p.write_text("<html><body/></html>", encoding="utf-8")
        errors = va.check_svg(p)
        assert any("expected <svg>" in e for e in errors)


# ---------------------------------------------------------------------------
# check_banner_pair
# ---------------------------------------------------------------------------


class TestCheckBannerPair:
    def test_both_present(self, tmp_path):
        _populate_valid_dir(tmp_path)
        assert va.check_banner_pair(tmp_path) == []

    def test_missing_dark(self, tmp_path):
        _populate_valid_dir(tmp_path)
        (tmp_path / "banner-dark.svg").unlink()
        errors = va.check_banner_pair(tmp_path)
        assert any("banner-dark.svg" in e for e in errors)

    def test_missing_light(self, tmp_path):
        _populate_valid_dir(tmp_path)
        (tmp_path / "banner-light.svg").unlink()
        errors = va.check_banner_pair(tmp_path)
        assert any("banner-light.svg" in e for e in errors)


# ---------------------------------------------------------------------------
# check_readme_references
# ---------------------------------------------------------------------------


class TestCheckReadmeReferences:
    def test_no_references(self, tmp_path):
        (tmp_path / "README.md").write_text("# Assets\n\nNo links here.\n")
        assert va.check_readme_references(tmp_path) == []

    def test_valid_reference(self, tmp_path):
        _write_minimal_svg(tmp_path / "banner-light.svg")
        (tmp_path / "README.md").write_text(
            "See `banner-light.svg` for the light banner.\n"
        )
        assert va.check_readme_references(tmp_path) == []

    def test_broken_reference(self, tmp_path):
        (tmp_path / "README.md").write_text("See `nonexistent.svg`\n")
        errors = va.check_readme_references(tmp_path)
        assert any("nonexistent.svg" in e for e in errors)

    def test_no_readme(self, tmp_path):
        # Should not raise; just return empty list
        assert va.check_readme_references(tmp_path) == []


# ---------------------------------------------------------------------------
# validate_directory — integration
# ---------------------------------------------------------------------------


class TestValidateDirectory:
    def test_valid_directory_passes(self, tmp_path):
        _populate_valid_dir(tmp_path)
        assert va.validate_directory(tmp_path) == 0

    def test_nonexistent_directory_fails(self, tmp_path):
        assert va.validate_directory(tmp_path / "missing") == 1

    def test_missing_required_file_fails(self, tmp_path):
        _populate_valid_dir(tmp_path)
        (tmp_path / "banner-light.svg").unlink()
        assert va.validate_directory(tmp_path) == 1

    def test_invalid_svg_fails(self, tmp_path):
        _populate_valid_dir(tmp_path)
        (tmp_path / "mark.svg").write_text("<svg><unclosed>", encoding="utf-8")
        assert va.validate_directory(tmp_path) == 1

    def test_production_assets_pass(self):
        """The production assets/profile/ directory must pass validation."""
        prod = Path(__file__).parents[1] / "assets" / "profile"
        assert va.validate_directory(prod) == 0
