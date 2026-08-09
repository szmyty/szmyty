"""README region detection, atomic writes, and content-hash change detection.

Each profile module owns an exclusive pair of HTML-comment markers:

    <!-- START:module-name -->
    … generated content …
    <!-- END:module-name -->

Hand-authored sections outside those markers are never touched.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Content hashing
# ---------------------------------------------------------------------------


def content_hash(text: str) -> str:
    """Return the SHA-256 hex digest of *text* (UTF-8 encoded)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str | None:
    """Return the SHA-256 hex digest of *path* contents, or ``None`` if missing."""
    if not path.exists():
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Atomic file write
# ---------------------------------------------------------------------------


def atomic_write(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    """Write *text* to *path* atomically using a sibling temporary file.

    On failure the original file is left untouched.  The temporary file is
    always removed, even when an error occurs.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as fh:
            fh.write(text)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Region detection and replacement
# ---------------------------------------------------------------------------


class RegionNotFoundError(ValueError):
    """Raised when a region marker pair cannot be located in the target file."""


def extract_region(text: str, start_marker: str, end_marker: str) -> tuple[int, int]:
    """Return the ``(start, end)`` character indices of the *content* between markers.

    The indices point to the first character after *start_marker* and the
    first character of *end_marker*, so ``text[start:end]`` yields only the
    generated content, not the markers themselves.

    Raises :class:`RegionNotFoundError` when either marker is absent.
    """
    start_idx = text.find(start_marker)
    if start_idx == -1:
        raise RegionNotFoundError(f"Start marker not found: {start_marker!r}")
    content_start = start_idx + len(start_marker)

    end_idx = text.find(end_marker, content_start)
    if end_idx == -1:
        raise RegionNotFoundError(f"End marker not found: {end_marker!r}")

    return content_start, end_idx


def replace_region(
    text: str,
    start_marker: str,
    end_marker: str,
    new_content: str,
) -> str:
    """Return a copy of *text* with the region between the markers replaced.

    *new_content* is wrapped with a leading and trailing newline so markers
    appear on their own lines.  Hand-authored sections outside the markers are
    preserved verbatim.

    Raises :class:`RegionNotFoundError` when either marker is absent.
    """
    content_start, content_end = extract_region(text, start_marker, end_marker)
    replacement = f"\n{new_content}\n"
    return text[:content_start] + replacement + text[content_end:]


def update_readme_region(
    readme_path: Path,
    start_marker: str,
    end_marker: str,
    new_content: str,
) -> bool:
    """Replace the owned region in *readme_path* and write atomically.

    Returns ``True`` when the file was changed, ``False`` when the existing
    content is already identical (skips the write).

    Raises :class:`RegionNotFoundError` when either marker is absent.
    Raises :class:`OSError` when the file cannot be read or written.
    """
    original = readme_path.read_text(encoding="utf-8")
    updated = replace_region(original, start_marker, end_marker, new_content)
    if updated == original:
        return False
    atomic_write(readme_path, updated)
    return True


# ---------------------------------------------------------------------------
# Change detection
# ---------------------------------------------------------------------------


def would_change(
    readme_path: Path,
    start_marker: str,
    end_marker: str,
    new_content: str,
) -> bool:
    """Return ``True`` when applying *new_content* would modify *readme_path*.

    Does **not** write anything.  Raises :class:`RegionNotFoundError` or
    :class:`OSError` on failures identical to :func:`update_readme_region`.
    """
    original = readme_path.read_text(encoding="utf-8")
    updated = replace_region(original, start_marker, end_marker, new_content)
    return updated != original
