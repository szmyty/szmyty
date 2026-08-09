"""Pure renderers for profile modules.

Every renderer accepts normalized Pydantic model instances and returns a
rendered string.  No network access, no filesystem side effects.  The caller
is responsible for writing the result via :mod:`tools.profile_builder.regions`.

Renderers use Jinja2 templates stored under ``profile/templates/``.  The
template loader root defaults to the repository root so paths are stable
regardless of the caller's working directory.

Templates are rendered without HTML autoescaping because profile output is
Markdown, not HTML.  Template authors are responsible for any escaping needed
within embedded HTML fragments.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jinja2


# ---------------------------------------------------------------------------
# Template environment
# ---------------------------------------------------------------------------

#: Default path to the ``profile/templates/`` directory, resolved relative to
#: *this file* so the package works regardless of CWD.
_REPO_ROOT = Path(__file__).parent.parent.parent
_TEMPLATES_DIR = _REPO_ROOT / "profile" / "templates"


def _make_env(templates_dir: Path | None = None) -> jinja2.Environment:
    """Return a Jinja2 :class:`~jinja2.Environment` for Markdown templates.

    *templates_dir* defaults to ``profile/templates/`` in the repository root.
    Autoescaping is disabled because templates produce Markdown, not HTML.
    Undefined variables raise :class:`~jinja2.StrictUndefined` so template
    errors are caught early.
    """
    loader_dir = templates_dir or _TEMPLATES_DIR
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(loader_dir)),
        autoescape=False,
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
    )


# ---------------------------------------------------------------------------
# Public rendering helpers
# ---------------------------------------------------------------------------


def render_template(
    template_name: str,
    context: dict[str, Any],
    *,
    templates_dir: Path | None = None,
) -> str:
    """Render *template_name* with *context* and return the result string.

    Args:
        template_name: Filename relative to ``profile/templates/``.
        context: Template variables; must match what the template expects.
        templates_dir: Override the default ``profile/templates/`` directory.

    Returns:
        Rendered string (may include trailing newline).

    Raises:
        jinja2.TemplateNotFound: When *template_name* does not exist.
        jinja2.UndefinedError: When a required template variable is missing.
    """
    env = _make_env(templates_dir)
    tmpl = env.get_template(template_name)
    return tmpl.render(**context)


def render_string(template_source: str, context: dict[str, Any]) -> str:
    """Render an inline *template_source* string with *context*.

    Useful for testing renderers without touching the filesystem.

    Args:
        template_source: A Jinja2 template string.
        context: Template variables.

    Returns:
        Rendered string.
    """
    env = jinja2.Environment(
        autoescape=False,
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
    )
    tmpl = env.from_string(template_source)
    return tmpl.render(**context)
