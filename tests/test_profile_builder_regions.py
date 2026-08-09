"""Tests for tools/profile_builder/regions.py."""

from __future__ import annotations

import pytest

from tools.profile_builder.regions import (
    RegionNotFoundError,
    atomic_write,
    content_hash,
    extract_region,
    file_hash,
    replace_region,
    update_readme_region,
    would_change,
)


# ---------------------------------------------------------------------------
# content_hash
# ---------------------------------------------------------------------------


def test_content_hash_deterministic() -> None:
    assert content_hash("hello") == content_hash("hello")


def test_content_hash_distinct() -> None:
    assert content_hash("hello") != content_hash("world")


def test_content_hash_empty() -> None:
    h = content_hash("")
    assert isinstance(h, str) and len(h) == 64


# ---------------------------------------------------------------------------
# file_hash
# ---------------------------------------------------------------------------


def test_file_hash_missing(tmp_path) -> None:
    assert file_hash(tmp_path / "nonexistent.txt") is None


def test_file_hash_matches(tmp_path) -> None:
    p = tmp_path / "data.txt"
    p.write_bytes(b"hello")
    h = file_hash(p)
    assert h is not None and len(h) == 64


# ---------------------------------------------------------------------------
# atomic_write
# ---------------------------------------------------------------------------


def test_atomic_write_creates_file(tmp_path) -> None:
    dest = tmp_path / "out.md"
    atomic_write(dest, "hello world")
    assert dest.read_text() == "hello world"


def test_atomic_write_overwrites(tmp_path) -> None:
    dest = tmp_path / "out.md"
    dest.write_text("old content")
    atomic_write(dest, "new content")
    assert dest.read_text() == "new content"


def test_atomic_write_creates_parents(tmp_path) -> None:
    dest = tmp_path / "a" / "b" / "out.md"
    atomic_write(dest, "nested")
    assert dest.read_text() == "nested"


# ---------------------------------------------------------------------------
# extract_region
# ---------------------------------------------------------------------------

START = "<!-- START:test -->"
END = "<!-- END:test -->"

_SAMPLE = f"before\n{START}\ngenerated\n{END}\nafter"


def test_extract_region_indices() -> None:
    s, e = extract_region(_SAMPLE, START, END)
    assert _SAMPLE[s:e] == "\ngenerated\n"


def test_extract_region_missing_start() -> None:
    with pytest.raises(RegionNotFoundError, match="Start marker"):
        extract_region("no markers here", START, END)


def test_extract_region_missing_end() -> None:
    with pytest.raises(RegionNotFoundError, match="End marker"):
        extract_region(f"before\n{START}\ncontent", START, END)


# ---------------------------------------------------------------------------
# replace_region
# ---------------------------------------------------------------------------


def test_replace_region_basic() -> None:
    result = replace_region(_SAMPLE, START, END, "new content")
    assert f"{START}\nnew content\n{END}" in result
    assert "before" in result
    assert "after" in result


def test_replace_region_preserves_outside() -> None:
    doc = f"HAND AUTHORED\n{START}\nold\n{END}\nMORE HAND AUTHORED"
    result = replace_region(doc, START, END, "rendered")
    assert "HAND AUTHORED" in result
    assert "MORE HAND AUTHORED" in result
    assert "old" not in result


def test_replace_region_missing_marker() -> None:
    with pytest.raises(RegionNotFoundError):
        replace_region("no markers", START, END, "x")


# ---------------------------------------------------------------------------
# update_readme_region / would_change
# ---------------------------------------------------------------------------


def test_update_readme_region_changed(tmp_path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(_SAMPLE)
    changed = update_readme_region(readme, START, END, "fresh content")
    assert changed is True
    assert "fresh content" in readme.read_text()


def test_update_readme_region_unchanged(tmp_path) -> None:
    doc = f"before\n{START}\nexisting\n{END}\nafter"
    readme = tmp_path / "README.md"
    readme.write_text(doc)
    changed = update_readme_region(readme, START, END, "existing")
    assert changed is False


def test_would_change_true(tmp_path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(_SAMPLE)
    assert would_change(readme, START, END, "different") is True


def test_would_change_false(tmp_path) -> None:
    doc = f"before\n{START}\nsame\n{END}\nafter"
    readme = tmp_path / "README.md"
    readme.write_text(doc)
    assert would_change(readme, START, END, "same") is False
