"""Tests for tools/profile_builder/rendering.py.

All tests use inline template strings (render_string) so no filesystem
access to profile/templates/ is required.  No network access is performed.
"""

from __future__ import annotations

import jinja2
import pytest

from tools.profile_builder.rendering import render_string, render_template

# ---------------------------------------------------------------------------
# render_string
# ---------------------------------------------------------------------------


def test_render_string_simple() -> None:
    result = render_string("Hello, {{ name }}!", {"name": "World"})
    assert result == "Hello, World!"


def test_render_string_missing_variable() -> None:
    with pytest.raises(jinja2.UndefinedError):
        render_string("{{ missing }}", {})


def test_render_string_deterministic() -> None:
    tmpl = "{{ a }} + {{ b }} = {{ a + b }}"
    r1 = render_string(tmpl, {"a": 1, "b": 2})
    r2 = render_string(tmpl, {"a": 1, "b": 2})
    assert r1 == r2


def test_render_string_no_timestamp_in_context() -> None:
    """Renderers must not inject volatile timestamps by default."""
    result = render_string("{{ value }}", {"value": "stable"})
    assert "timestamp" not in result


# ---------------------------------------------------------------------------
# render_template (filesystem)
# ---------------------------------------------------------------------------


def test_render_template_example(tmp_path) -> None:
    """render_template loads a template from disk and renders it."""
    tmpl_dir = tmp_path / "templates"
    tmpl_dir.mkdir()
    (tmpl_dir / "greeting.md.j2").write_text("Hi, {{ name }}!")

    result = render_template("greeting.md.j2", {"name": "Alan"}, templates_dir=tmpl_dir)
    assert result == "Hi, Alan!"


def test_render_template_not_found(tmp_path) -> None:
    tmpl_dir = tmp_path / "templates"
    tmpl_dir.mkdir()

    with pytest.raises(jinja2.TemplateNotFound):
        render_template("nonexistent.md.j2", {}, templates_dir=tmpl_dir)


def test_render_template_missing_variable(tmp_path) -> None:
    tmpl_dir = tmp_path / "templates"
    tmpl_dir.mkdir()
    (tmpl_dir / "t.md.j2").write_text("{{ required_var }}")

    with pytest.raises(jinja2.UndefinedError):
        render_template("t.md.j2", {}, templates_dir=tmpl_dir)


def test_render_template_equivalent_input_byte_equivalent(tmp_path) -> None:
    """Equivalent normalized input must produce byte-equivalent output."""
    tmpl_dir = tmp_path / "templates"
    tmpl_dir.mkdir()
    (tmpl_dir / "t.md.j2").write_text("{{ x }} {{ y }}")

    args = {"x": "hello", "y": "world"}
    r1 = render_template("t.md.j2", args, templates_dir=tmpl_dir)
    r2 = render_template("t.md.j2", args, templates_dir=tmpl_dir)
    assert r1 == r2
