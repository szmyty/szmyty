"""
Tests for templates/validate_template.py.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------
# Load module under test
# ---------------------------------------------------------------------------


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_template",
        Path(__file__).parents[1] / "templates" / "validate_template.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vt = _load_validator()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MINIMAL_VALID = """\
# My Project

A short description.

## Overview

Some content here.

## License

MIT
"""

_EXAMPLE_REPO = (
    Path(__file__).parents[1] / "templates" / "repository" / "example" / "README.md"
)
_EXAMPLE_PROFILE = (
    Path(__file__).parents[1] / "templates" / "profile" / "example" / "README.md"
)
_TEMPLATE_REPO = Path(__file__).parents[1] / "templates" / "repository" / "README.md"
_TEMPLATE_PROFILE = Path(__file__).parents[1] / "templates" / "profile" / "README.md"


# ---------------------------------------------------------------------------
# check_unresolved_tokens
# ---------------------------------------------------------------------------


class TestCheckUnresolvedTokens:
    def test_no_tokens(self):
        assert vt.check_unresolved_tokens(_MINIMAL_VALID) == []

    def test_single_token(self):
        errors = vt.check_unresolved_tokens("Hello {{PROJECT_NAME}}!")
        assert len(errors) == 1
        assert "PROJECT_NAME" in errors[0]

    def test_multiple_tokens(self):
        errors = vt.check_unresolved_tokens("{{OWNER}}/{{REPO}}")
        assert len(errors) == 2

    def test_partial_braces_ignored(self):
        # {single} and {{lowercase}} are not template tokens
        assert vt.check_unresolved_tokens("{not-a-token}") == []
        assert vt.check_unresolved_tokens("{{not_a_token}}") == []  # lowercase


# ---------------------------------------------------------------------------
# check_heading_structure
# ---------------------------------------------------------------------------


class TestCheckHeadingStructure:
    def test_valid_structure(self):
        content = "# Title\n\n## Section\n\n### Subsection\n"
        assert vt.check_heading_structure(content) == []

    def test_no_h1(self):
        errors = vt.check_heading_structure("## Section\n")
        assert any("No H1" in e for e in errors)

    def test_multiple_h1(self):
        errors = vt.check_heading_structure("# First\n\n# Second\n")
        assert any("Multiple H1" in e for e in errors)

    def test_level_skip_inside_tilde_fence_ignored(self):
        content = "# Title\n\n~~~sh\n#### not-a-heading\n~~~\n\n## H2\n"
        assert vt.check_heading_structure(content) == []

    def test_level_skip(self):
        errors = vt.check_heading_structure("# Title\n\n## H2\n\n#### H4\n")
        assert any("skips" in e for e in errors)

    def test_h2_to_h3_is_fine(self):
        content = "# Title\n\n## H2\n\n### H3\n"
        assert vt.check_heading_structure(content) == []


# ---------------------------------------------------------------------------
# check_generated_regions
# ---------------------------------------------------------------------------


class TestCheckGeneratedRegions:
    def test_balanced_markers(self):
        content = "<!-- BEGIN:toc -->\ncontent\n<!-- END:toc -->\n"
        assert vt.check_generated_regions(content) == []

    def test_missing_end(self):
        errors = vt.check_generated_regions("<!-- BEGIN:toc -->\n")
        assert any("BEGIN" in e and "toc" in e for e in errors)

    def test_missing_begin(self):
        errors = vt.check_generated_regions("<!-- END:toc -->\n")
        assert any("END" in e and "toc" in e for e in errors)

    def test_nested_same_name(self):
        content = "<!-- BEGIN:x -->\n<!-- BEGIN:x -->\n<!-- END:x -->\n<!-- END:x -->\n"
        errors = vt.check_generated_regions(content)
        assert any("nested or duplicate" in e for e in errors)

    def test_multiple_balanced(self):
        content = "<!-- BEGIN:a -->\n<!-- END:a -->\n<!-- BEGIN:b -->\n<!-- END:b -->\n"
        assert vt.check_generated_regions(content) == []


# ---------------------------------------------------------------------------
# check_duplicate_anchors
# ---------------------------------------------------------------------------


class TestCheckDuplicateAnchors:
    def test_unique_anchors(self):
        content = "# Title\n\n## Overview\n\n## License\n"
        assert vt.check_duplicate_anchors(content) == []

    def test_duplicate_anchors(self):
        errors = vt.check_duplicate_anchors("# Title\n\n## Usage\n\n## Usage\n")
        assert any("duplicate anchor" in e for e in errors)

    def test_case_difference_is_duplicate(self):
        # "Usage" and "USAGE" both produce anchor #usage
        errors = vt.check_duplicate_anchors("# Title\n\n## Usage\n\n## USAGE\n")
        assert any("duplicate anchor" in e for e in errors)


# ---------------------------------------------------------------------------
# check_links_and_images
# ---------------------------------------------------------------------------


class TestCheckLinksAndImages:
    def test_valid_link(self):
        assert vt.check_links_and_images("[text](https://example.com)") == []

    def test_empty_link_target(self):
        errors = vt.check_links_and_images("[text]()")
        assert any("empty target" in e for e in errors)

    def test_empty_link_text(self):
        errors = vt.check_links_and_images("[](https://example.com)")
        assert any("empty text" in e for e in errors)

    def test_valid_image(self):
        assert vt.check_links_and_images("![alt text](image.png)") == []

    def test_image_missing_alt(self):
        errors = vt.check_links_and_images("![](image.png)")
        assert any("missing alt text" in e for e in errors)

    def test_image_empty_alt(self):
        errors = vt.check_links_and_images("![   ](image.png)")
        assert any("missing alt text" in e for e in errors)

    def test_image_empty_url(self):
        errors = vt.check_links_and_images("![alt]()")
        assert any("empty URL" in e for e in errors)


# ---------------------------------------------------------------------------
# check_byte_budget
# ---------------------------------------------------------------------------


class TestCheckByteBudget:
    def test_within_budget(self, tmp_path):
        p = tmp_path / "README.md"
        p.write_text("x" * 1024, encoding="utf-8")
        assert vt.check_byte_budget(p) == []

    def test_exceeds_budget(self, tmp_path):
        p = tmp_path / "README.md"
        p.write_bytes(b"x" * (500 * 1024 + 1))
        errors = vt.check_byte_budget(p)
        assert any("exceeds" in e for e in errors)


# ---------------------------------------------------------------------------
# check_personal_identifiers
# ---------------------------------------------------------------------------


class TestCheckPersonalIdentifiers:
    def test_clean_content(self):
        assert vt.check_personal_identifiers(_MINIMAL_VALID) == []

    def test_detects_username(self):
        errors = vt.check_personal_identifiers("See github.com/szmyty for details.")
        assert any("szmyty" in e for e in errors)

    def test_detects_real_name(self):
        errors = vt.check_personal_identifiers("Maintained by Alan Szmyt.")
        assert any("Alan Szmyt" in e for e in errors)

    def test_case_insensitive(self):
        errors = vt.check_personal_identifiers("SZMYTY is the author.")
        assert any("szmyty" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# validate_file — integration
# ---------------------------------------------------------------------------


class TestValidateFile:
    def test_valid_file_passes(self, tmp_path):
        p = tmp_path / "README.md"
        p.write_text(_MINIMAL_VALID, encoding="utf-8")
        assert vt.validate_file(p) == 0

    def test_missing_file_fails(self, tmp_path):
        assert vt.validate_file(tmp_path / "missing.md") == 1

    def test_unresolved_token_fails(self, tmp_path):
        p = tmp_path / "README.md"
        p.write_text("# {{PROJECT_NAME}}\n\nDesc.\n", encoding="utf-8")
        assert vt.validate_file(p) == 1

    def test_no_h1_fails(self, tmp_path):
        p = tmp_path / "README.md"
        p.write_text("## Section only\n\nContent.\n", encoding="utf-8")
        assert vt.validate_file(p) == 1

    def test_skip_personal_ids_flag(self, tmp_path):
        p = tmp_path / "README.md"
        p.write_text("# szmyty\n\nProfile.\n", encoding="utf-8")
        # Without flag: fails
        assert vt.validate_file(p, skip_personal_ids=False) == 1
        # With flag: passes
        assert vt.validate_file(p, skip_personal_ids=True) == 0


# ---------------------------------------------------------------------------
# Example files — integration
# ---------------------------------------------------------------------------


class TestExampleFiles:
    def test_repository_example_passes(self):
        """The generic repository example must pass all checks."""
        assert vt.validate_file(_EXAMPLE_REPO) == 0

    def test_profile_example_passes(self):
        """The generic profile example must pass all checks."""
        assert vt.validate_file(_EXAMPLE_PROFILE) == 0

    def test_repository_template_has_tokens(self):
        """The repository template must still contain unresolved tokens."""
        content = _TEMPLATE_REPO.read_text(encoding="utf-8")
        assert vt._TOKEN_RE.search(content), (
            "templates/repository/README.md has no {{TOKEN}} placeholders — "
            "it may have been accidentally resolved"
        )

    def test_profile_template_has_tokens(self):
        """The profile template must still contain unresolved tokens."""
        content = _TEMPLATE_PROFILE.read_text(encoding="utf-8")
        assert vt._TOKEN_RE.search(content), (
            "templates/profile/README.md has no {{TOKEN}} placeholders — "
            "it may have been accidentally resolved"
        )

    def test_repository_example_no_personal_ids(self):
        """The repository example must contain no personal identifiers."""
        content = _EXAMPLE_REPO.read_text(encoding="utf-8")
        errors = vt.check_personal_identifiers(content)
        assert errors == [], f"Personal identifiers found: {errors}"

    def test_profile_example_no_personal_ids(self):
        """The profile example must contain no personal identifiers."""
        content = _EXAMPLE_PROFILE.read_text(encoding="utf-8")
        errors = vt.check_personal_identifiers(content)
        assert errors == [], f"Personal identifiers found: {errors}"
