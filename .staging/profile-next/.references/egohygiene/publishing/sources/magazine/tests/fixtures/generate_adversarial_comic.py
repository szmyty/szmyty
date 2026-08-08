"""Adversarial test comic fixture generator.

Generates deterministic "broken" editions to stress-test the publishing
pipeline under non-ideal and edge-case conditions.

Each public function returns the path to the generated edition root and
produces the same directory structure on every run (deterministic).

Scenarios
---------
A  Missing page.png       – page dir exists but page.png is absent
B  Corrupt PNG            – page.png contains invalid binary data
C  Manifest references missing page – manifest lists a page that has no dir
D  Extra folder not in manifest     – directory not listed in manifest
E  Stale artifacts                  – pre-existing artifacts with newer page.png
F  Mixed valid / invalid pages      – some pages OK, some missing page.png
G  Inconsistent page naming         – folders without the ``NN_`` numeric prefix

Usage::

    from tests.fixtures.generate_adversarial_comic import (
        generate_scenario_a,
        generate_scenario_b,
        generate_scenario_c,
        generate_scenario_d,
        generate_scenario_e,
        generate_scenario_f,
        generate_scenario_g,
    )

    edition_dir = generate_scenario_a(tmp_path)
"""

from __future__ import annotations

import io
import json
from pathlib import Path

from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

#: Small page size for adversarial fixtures – fast to generate.
ADV_WIDTH: int = 400
ADV_HEIGHT: int = 566

_BG = (255, 255, 255)
_FG = (20, 20, 20)
_PANEL = (200, 200, 200)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _make_valid_png(label: str = "PAGE") -> bytes:
    """Return minimal valid RGB PNG bytes with *label* drawn on it."""
    img = Image.new("RGB", (ADV_WIDTH, ADV_HEIGHT), color=_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, ADV_WIDTH - 10, ADV_HEIGHT - 10], outline=_FG, width=3)
    draw.text((ADV_WIDTH // 2, ADV_HEIGHT // 2), label, fill=_FG, anchor="mm")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def _make_corrupt_png() -> bytes:
    """Return bytes that begin with the PNG magic header but are otherwise invalid."""
    # Valid PNG magic: \x89PNG\r\n\x1a\n  followed by junk
    return b"\x89PNG\r\n\x1a\n" + b"\x00\xff\xde\xad\xbe\xef" * 16


def _write_manifest(edition_dir: Path, edition_name: str, slugs: list[str]) -> None:
    manifest = {"edition": edition_name, "pages": slugs}
    (edition_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


def _make_edition_dir(dest: Path, name: str) -> Path:
    edition_dir = dest / name
    (edition_dir / "pages").mkdir(parents=True, exist_ok=True)
    return edition_dir


# ---------------------------------------------------------------------------
# Scenario A – Missing page.png
# ---------------------------------------------------------------------------


def generate_scenario_a(dest: Path, edition_name: str = "scenario_a_missing_png") -> Path:
    """Edition where ``01_intro`` has no page.png; ``02_middle`` is valid.

    Structure::

        <edition>/
            pages/
                01_intro/          ← directory exists, page.png absent
                02_middle/
                    page.png       ← valid PNG
            manifest.json          ← lists both pages
    """
    edition_dir = _make_edition_dir(dest, edition_name)
    pages_dir = edition_dir / "pages"

    # 01_intro: directory only, no page.png
    (pages_dir / "01_intro").mkdir(exist_ok=True)

    # 02_middle: valid page
    middle = pages_dir / "02_middle"
    middle.mkdir(exist_ok=True)
    (middle / "page.png").write_bytes(_make_valid_png("PAGE 02"))

    _write_manifest(edition_dir, edition_name, ["01_intro", "02_middle"])
    return edition_dir


# ---------------------------------------------------------------------------
# Scenario B – Corrupt PNG file
# ---------------------------------------------------------------------------


def generate_scenario_b(dest: Path, edition_name: str = "scenario_b_corrupt_png") -> Path:
    """Edition where ``01_intro/page.png`` contains invalid binary data.

    Structure::

        <edition>/
            pages/
                01_intro/
                    page.png       ← PNG magic header + junk bytes (invalid)
                02_middle/
                    page.png       ← valid PNG
            manifest.json
    """
    edition_dir = _make_edition_dir(dest, edition_name)
    pages_dir = edition_dir / "pages"

    intro = pages_dir / "01_intro"
    intro.mkdir(exist_ok=True)
    (intro / "page.png").write_bytes(_make_corrupt_png())

    middle = pages_dir / "02_middle"
    middle.mkdir(exist_ok=True)
    (middle / "page.png").write_bytes(_make_valid_png("PAGE 02"))

    _write_manifest(edition_dir, edition_name, ["01_intro", "02_middle"])
    return edition_dir


# ---------------------------------------------------------------------------
# Scenario C – Manifest references a missing page directory
# ---------------------------------------------------------------------------


def generate_scenario_c(dest: Path, edition_name: str = "scenario_c_missing_dir") -> Path:
    """Manifest lists ``03_finale`` which has no corresponding directory.

    Structure::

        <edition>/
            pages/
                01_intro/
                    page.png
                02_middle/
                    page.png
            manifest.json          ← lists 01_intro, 02_middle, 03_finale
    """
    edition_dir = _make_edition_dir(dest, edition_name)
    pages_dir = edition_dir / "pages"

    for slug, label in [("01_intro", "PAGE 01"), ("02_middle", "PAGE 02")]:
        d = pages_dir / slug
        d.mkdir(exist_ok=True)
        (d / "page.png").write_bytes(_make_valid_png(label))

    # 03_finale listed but directory intentionally absent
    _write_manifest(edition_dir, edition_name, ["01_intro", "02_middle", "03_finale"])
    return edition_dir


# ---------------------------------------------------------------------------
# Scenario D – Extra folder not in manifest
# ---------------------------------------------------------------------------


def generate_scenario_d(dest: Path, edition_name: str = "scenario_d_extra_folder") -> Path:
    """An extra page directory exists that is not listed in the manifest.

    Structure::

        <edition>/
            pages/
                01_intro/
                    page.png
                02_middle/
                    page.png
                99_unlisted/       ← real directory, not in manifest
                    page.png
            manifest.json          ← lists only 01_intro, 02_middle
    """
    edition_dir = _make_edition_dir(dest, edition_name)
    pages_dir = edition_dir / "pages"

    for slug, label in [
        ("01_intro", "PAGE 01"),
        ("02_middle", "PAGE 02"),
        ("99_unlisted", "UNLISTED"),
    ]:
        d = pages_dir / slug
        d.mkdir(exist_ok=True)
        (d / "page.png").write_bytes(_make_valid_png(label))

    # 99_unlisted intentionally absent from manifest
    _write_manifest(edition_dir, edition_name, ["01_intro", "02_middle"])
    return edition_dir


# ---------------------------------------------------------------------------
# Scenario E – Stale artifacts present
# ---------------------------------------------------------------------------


def generate_scenario_e(dest: Path, edition_name: str = "scenario_e_stale_artifacts") -> Path:
    """Pre-existing artifact files with a later-modified page.png.

    The artifacts directory is pre-populated before the page.png is
    (re-)written, simulating a stale build state that should trigger
    hash invalidation.

    Structure::

        <edition>/
            pages/
                01_intro/
                    page.png          ← newer content (written after artifacts)
                    artifacts/
                        page.jpg          ← stale artifact
                        page.tiff         ← stale artifact
                        page.fountain.pdf ← stale artifact
            manifest.json
    """
    edition_dir = _make_edition_dir(dest, edition_name)
    pages_dir = edition_dir / "pages"

    intro = pages_dir / "01_intro"
    intro.mkdir(exist_ok=True)

    # Write stale artifacts first
    artifacts = intro / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "page.jpg").write_bytes(b"stale-jpeg-data")
    (artifacts / "page.tiff").write_bytes(b"stale-tiff-data")
    (artifacts / "page.fountain.pdf").write_bytes(b"stale-pdf-data")

    # Then write (or overwrite) page.png to simulate a content change
    (intro / "page.png").write_bytes(_make_valid_png("PAGE 01 UPDATED"))

    _write_manifest(edition_dir, edition_name, ["01_intro"])
    return edition_dir


# ---------------------------------------------------------------------------
# Scenario F – Mixed valid / invalid pages
# ---------------------------------------------------------------------------


def generate_scenario_f(
    dest: Path, edition_name: str = "scenario_f_mixed_pages"
) -> Path:
    """Edition with a mix of valid pages and a page missing page.png.

    Structure::

        <edition>/
            pages/
                01_intro/
                    page.png       ← valid
                02_middle/         ← directory only, page.png absent
                03_finale/
                    page.png       ← valid
            manifest.json
    """
    edition_dir = _make_edition_dir(dest, edition_name)
    pages_dir = edition_dir / "pages"

    for slug, label in [("01_intro", "PAGE 01"), ("03_finale", "PAGE 03")]:
        d = pages_dir / slug
        d.mkdir(exist_ok=True)
        (d / "page.png").write_bytes(_make_valid_png(label))

    # 02_middle: directory exists, page.png absent
    (pages_dir / "02_middle").mkdir(exist_ok=True)

    _write_manifest(edition_dir, edition_name, ["01_intro", "02_middle", "03_finale"])
    return edition_dir


# ---------------------------------------------------------------------------
# Scenario G – Inconsistent page naming (no numeric prefix)
# ---------------------------------------------------------------------------


def generate_scenario_g(
    dest: Path, edition_name: str = "scenario_g_bad_names"
) -> Path:
    """Edition with page directory names that lack the ``NN_`` numeric prefix.

    Structure::

        <edition>/
            pages/
                intro/             ← no numeric prefix
                02_middle/         ← valid name
                final/             ← no numeric prefix
            manifest.json
    """
    edition_dir = _make_edition_dir(dest, edition_name)
    pages_dir = edition_dir / "pages"

    for slug, label in [
        ("intro", "INTRO"),
        ("02_middle", "PAGE 02"),
        ("final", "FINAL"),
    ]:
        d = pages_dir / slug
        d.mkdir(exist_ok=True)
        (d / "page.png").write_bytes(_make_valid_png(label))

    _write_manifest(edition_dir, edition_name, ["intro", "02_middle", "final"])
    return edition_dir
