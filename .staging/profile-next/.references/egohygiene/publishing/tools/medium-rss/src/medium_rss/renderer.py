"""Markdown renderer – converts cleaned article HTML to Markdown."""

from __future__ import annotations

import re

import structlog
from markdownify import markdownify

log = structlog.get_logger(__name__)

# markdownify options tuned for Medium article content.
# Note: markdownify accepts either `strip` or `convert`, not both.
# We use `strip` to exclude non-content elements and let everything else convert.
_MARKDOWNIFY_OPTIONS: dict[str, object] = {
    "heading_style": "ATX",
    "bullets": "-",
    "strip": ["script", "style", "head", "meta"],
}


def render_markdown(html: str) -> str:
    """Convert cleaned article HTML into normalized Markdown.

    Preserves headings, paragraphs, emphasis, blockquotes, lists, links,
    figures, image alt text, and captions.  Does not introduce generated
    prose or modify the author's original meaning.
    """
    if not html:
        return ""

    try:
        md = markdownify(html, **_MARKDOWNIFY_OPTIONS)  # type: ignore[arg-type]
    except Exception as exc:
        log.warning("renderer.markdownify_failed", exc=str(exc))
        return ""

    md = _clean_markdown(md)
    log.debug("renderer.rendered", length=len(md))
    return md


def _clean_markdown(md: str) -> str:
    """Apply post-processing to improve Markdown quality."""
    # Collapse more than two consecutive blank lines into two
    md = re.sub(r"\n{3,}", "\n\n", md)
    # Remove trailing whitespace from each line
    md = "\n".join(line.rstrip() for line in md.splitlines())
    # Ensure the document ends with a single newline
    return md.strip() + "\n"
