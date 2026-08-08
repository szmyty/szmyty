"""Synthetic test comic page generator.

Generates deterministic fake comic pages using Pillow for use in
integration testing of the magazine publishing pipeline.

No randomness is used.  All layout, text, and pixel data are fixed.
The same inputs always produce identical PNG binary output.

Usage::

    from tests.fixtures.generate_fake_comic import generate_fake_comic

    edition_dir = generate_fake_comic(tmp_path)
    # edition_dir / "pages" / "01_intro" / "page.png"  ← valid PNG
    # edition_dir / "manifest.json"                     ← page-order manifest
"""

from __future__ import annotations

import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------

#: Primary edition: A4 at 300 DPI (2480 × 3508 px).
PAGE_WIDTH: int = 2480
PAGE_HEIGHT: int = 3508

#: Variant edition: US Comic trim at 300 DPI (1988 × 3075 px).
VARIANT_WIDTH: int = 1988
VARIANT_HEIGHT: int = 3075

# ---------------------------------------------------------------------------
# Colours (RGB tuples, no alpha channel so PNGs stay flat)
# ---------------------------------------------------------------------------
_BG = (255, 255, 255)
_TITLE = (20, 20, 20)
_SUBTITLE = (60, 60, 60)
_DECO = (120, 120, 120)
_FOOTER = (150, 150, 150)
_BORDER = (0, 0, 0)
_PANEL = (230, 230, 230)

# ---------------------------------------------------------------------------
# Page definitions – fully deterministic, no randomness
# ---------------------------------------------------------------------------

_DEFAULT_FOOTER: str = "\u00a9 SYNTHETIC FIXTURE \u2013 NOT FOR DISTRIBUTION"
_VARIANT_FOOTER: str = "\u00a9 SYNTHETIC VARIANT FIXTURE"

_PRIMARY_PAGES: list[dict[str, str]] = [
    {
        "slug": "01_intro",
        "title": "TEST COMIC",
        "page_label": "PAGE: 01",
        "section": "SECTION: INTRO",
        "subtitle": "A Deterministic Journey",
        "footer": _DEFAULT_FOOTER,
    },
    {
        "slug": "02_middle",
        "title": "TEST COMIC",
        "page_label": "PAGE: 02",
        "section": "SECTION: MIDDLE",
        "subtitle": "The Plot Thickens",
        "footer": _DEFAULT_FOOTER,
    },
    {
        "slug": "03_finale",
        "title": "TEST COMIC",
        "page_label": "PAGE: 03",
        "section": "SECTION: FINALE",
        "subtitle": "The Conclusion",
        "footer": _DEFAULT_FOOTER,
    },
]

_VARIANT_PAGES: list[dict[str, str]] = [
    {
        "slug": "01_chapter",
        "title": "VARIANT COMIC",
        "page_label": "PAGE: 01",
        "section": "SECTION: CHAPTER",
        "subtitle": "Slightly Different Content",
        "footer": _VARIANT_FOOTER,
    },
    {
        "slug": "02_climax",
        "title": "VARIANT COMIC",
        "page_label": "PAGE: 02",
        "section": "SECTION: CLIMAX",
        "subtitle": "Trigger Invalidation",
        "footer": _VARIANT_FOOTER,
    },
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Return the built-in Pillow bitmap font scaled to *size*.

    Uses ``load_default(size=size)`` which is available from Pillow ≥ 9.2.
    Falls back to the un-scaled default font for older versions.
    """
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _draw_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    """Draw a light-grey filled rectangle with a black border."""
    draw.rectangle(box, fill=_PANEL, outline=_BORDER, width=4)


def _make_page(
    width: int,
    height: int,
    page_def: dict[str, str],
) -> bytes:
    """Return deterministic PNG bytes for a single comic page.

    The layout is:
        - 1 px white border padding
        - Outer border rectangle
        - Title band (top)
        - Three simulated panel boxes (middle)
        - Page label + section text (lower-middle)
        - Subtitle band
        - Footer band (bottom)

    All positions are computed from *width* / *height* so the layout
    scales proportionally between the primary and variant editions.
    """
    img = Image.new("RGB", (width, height), color=_BG)
    draw = ImageDraw.Draw(img)

    margin = width // 40  # ~62 px for 2480-wide image

    # Outer border
    draw.rectangle(
        [margin, margin, width - margin, height - margin],
        outline=_BORDER,
        width=6,
    )

    # ---- Title band --------------------------------------------------------
    title_h = height // 10
    draw.rectangle(
        [margin, margin, width - margin, margin + title_h],
        fill=_BORDER,
        outline=_BORDER,
        width=4,
    )
    title_font = _font(width // 10)
    draw.text(
        (width // 2, margin + title_h // 2),
        page_def["title"],
        font=title_font,
        fill=_BG,
        anchor="mm",
    )

    # ---- Three simulated panel boxes ---------------------------------------
    panel_top = margin + title_h + margin
    panel_height = height // 5
    panel_width = (width - margin * 4) // 3
    for col in range(3):
        x0 = margin + col * (panel_width + margin)
        box = (x0, panel_top, x0 + panel_width, panel_top + panel_height)
        _draw_panel(draw, box)
        panel_font = _font(width // 30)
        draw.text(
            ((x0 + x0 + panel_width) // 2, panel_top + panel_height // 2),
            f"PANEL {col + 1}",
            font=panel_font,
            fill=_DECO,
            anchor="mm",
        )

    # ---- Second row of panels (larger) -------------------------------------
    panel2_top = panel_top + panel_height + margin
    panel2_height = height // 4
    panel2_width = (width - margin * 3) // 2
    for col in range(2):
        x0 = margin + col * (panel2_width + margin)
        box = (x0, panel2_top, x0 + panel2_width, panel2_top + panel2_height)
        _draw_panel(draw, box)

    # ---- Page label + section text -----------------------------------------
    text_top = panel2_top + panel2_height + margin * 2
    label_font = _font(width // 20)
    section_font = _font(width // 25)
    draw.text(
        (width // 2, text_top),
        page_def["page_label"],
        font=label_font,
        fill=_TITLE,
        anchor="mt",
    )
    draw.text(
        (width // 2, text_top + width // 18),
        page_def["section"],
        font=section_font,
        fill=_SUBTITLE,
        anchor="mt",
    )

    # ---- Subtitle band -----------------------------------------------------
    sub_top = height - margin * 5 - height // 15
    subtitle_font = _font(width // 28)
    draw.text(
        (width // 2, sub_top),
        page_def["subtitle"],
        font=subtitle_font,
        fill=_SUBTITLE,
        anchor="mt",
    )

    # ---- Footer band -------------------------------------------------------
    footer_top = height - margin * 3
    draw.line(
        [(margin, footer_top - margin), (width - margin, footer_top - margin)],
        fill=_DECO,
        width=2,
    )
    footer_font = _font(width // 50)
    draw.text(
        (width // 2, height - margin * 2),
        page_def["footer"],
        font=footer_font,
        fill=_FOOTER,
        anchor="mm",
    )

    # Serialise to PNG bytes without any metadata that could vary across runs.
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def _write_edition(
    dest: Path,
    edition_name: str,
    pages: list[dict[str, str]],
    width: int,
    height: int,
) -> Path:
    """Write an edition directory tree and return its path.

    Structure::

        <dest>/<edition_name>/
            pages/
                <slug>/
                    page.png
            manifest.json
    """
    edition_dir = dest / edition_name
    pages_dir = edition_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    slugs: list[str] = []
    for page_def in pages:
        slug = page_def["slug"]
        page_dir = pages_dir / slug
        page_dir.mkdir(exist_ok=True)
        png_bytes = _make_page(width, height, page_def)
        (page_dir / "page.png").write_bytes(png_bytes)
        slugs.append(slug)

    manifest = {"edition": edition_name, "pages": slugs}
    (edition_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    return edition_dir


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_fake_comic(dest: Path, edition_name: str = "edition_fake") -> Path:
    """Generate the primary synthetic test edition.

    Creates 3 pages at 2480 × 3508 px (A4 @ 300 DPI) with fixed layout and
    text.  Identical inputs always produce identical PNG binary output.

    Args:
        dest:          Directory under which the edition tree is written.
        edition_name:  Name of the edition subdirectory (default
                       ``"edition_fake"``).

    Returns:
        Path to the edition root directory (contains ``pages/`` and
        ``manifest.json``).
    """
    return _write_edition(dest, edition_name, _PRIMARY_PAGES, PAGE_WIDTH, PAGE_HEIGHT)


def generate_variant_comic(dest: Path, edition_name: str = "edition_variant") -> Path:
    """Generate a second synthetic edition with different dimensions and content.

    Creates 2 pages at 1988 × 3075 px (US Comic trim @ 300 DPI).  Intended
    for testing hash-invalidation logic when source images change.

    Args:
        dest:          Directory under which the edition tree is written.
        edition_name:  Name of the edition subdirectory (default
                       ``"edition_variant"``).

    Returns:
        Path to the edition root directory (contains ``pages/`` and
        ``manifest.json``).
    """
    return _write_edition(
        dest, edition_name, _VARIANT_PAGES, VARIANT_WIDTH, VARIANT_HEIGHT
    )
