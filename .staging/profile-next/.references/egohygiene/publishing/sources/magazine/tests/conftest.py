"""Shared pytest fixtures for the magazine test suite."""

import json
from pathlib import Path

import pytest


@pytest.fixture()
def page_dir(tmp_path: Path) -> Path:
    """Return a minimal page directory with a fake page.png."""
    d = tmp_path / "01_test_page"
    d.mkdir()
    (d / "page.png").write_bytes(b"fake png data")
    return d


@pytest.fixture()
def page_dir_with_fountain(page_dir: Path) -> Path:
    """Return a page directory that also has a page.fountain file."""
    (page_dir / "page.fountain").write_text("Title: Test\n\nINT. TEST ROOM – DAY\n")
    return page_dir


@pytest.fixture()
def sizes_config(tmp_path: Path) -> Path:
    """Write a minimal sizes.json and return its path."""
    cfg = {
        "test_size": {
            "width": 100,
            "height": 150,
            "dpi": 72,
            "bleed": 0,
            "safe_margin": 5,
            "output_suffix": "test_size",
            "scaling_strategy": "fit",
        }
    }
    p = tmp_path / "sizes.json"
    p.write_text(json.dumps(cfg))
    return p


@pytest.fixture()
def edition_dir(tmp_path: Path) -> Path:
    """Return a minimal edition directory with two page subdirectories."""
    e = tmp_path / "edition_01"
    e.mkdir()
    pages = e / "pages"
    pages.mkdir()
    for slug in ("01_intro", "02_body"):
        page = pages / slug
        page.mkdir()
        (page / "page.png").write_bytes(b"fake png")
    return e


@pytest.fixture()
def staged_edition_dir(edition_dir: Path) -> Path:
    """Return an edition directory with staged PNGs in final_build_stage."""
    stage = edition_dir / "artifacts" / "final_build_stage"
    stage.mkdir(parents=True)
    (stage / "01_intro.png").write_bytes(b"fake png")
    (stage / "02_body.png").write_bytes(b"fake png")
    return edition_dir
