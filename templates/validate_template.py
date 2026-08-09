"""
validate_template.py
====================
Validate a README (or any Markdown file) produced from the template kit.

Checks
------
1. No unresolved ``{{TOKEN}}`` placeholders remain.
2. Exactly one H1 heading is present.
3. Headings do not skip levels (e.g. H2 → H4 without an H3).
4. Every ``<!-- BEGIN:name -->`` marker has a matching ``<!-- END:name -->``.
5. No two headings produce the same GitHub-style anchor.
6. No empty link targets (``[text]()``) and no missing link text (``[](url)``).
7. No images with empty alt text (``![](url)``).
8. File size is within the 500 KB byte budget.
9. No personal identifiers from the block-list appear in the file.

Usage
-----
    python templates/validate_template.py path/to/README.md [--personal-ids-ok]

Options
-------
--personal-ids-ok
    Skip the personal-identifier check.  Use this flag when validating a
    profile README that intentionally contains the profile owner's username.

Exit codes
----------
0  All checks pass.
1  One or more checks failed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BYTE_BUDGET: int = 500 * 1024  # 500 KB

# Regex matching an unresolved template token
_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")

# Regex matching a Markdown ATX heading
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

# Regex matching BEGIN/END region markers
_BEGIN_RE = re.compile(r"<!--\s*BEGIN:(\S+)\s*-->")
_END_RE = re.compile(r"<!--\s*END:(\S+)\s*-->")

# Regex matching Markdown image syntax
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")

# Regex matching Markdown link syntax (not images)
_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)]*)\)")

# Personal identifiers that must not appear in universal templates.
# This list covers the repository owner's real name, GitHub username,
# and common variants.  It is intentionally kept minimal and generic enough
# to be useful for other adopters who add their own entries.
_PERSONAL_IDS: list[str] = [
    "szmyty",
    "alan szmyt",
    "Alan Szmyt",
]


# ---------------------------------------------------------------------------
# Anchor generation
# ---------------------------------------------------------------------------


def _github_anchor(heading_text: str) -> str:
    """
    Compute the GitHub-style anchor for a heading line.

    GitHub converts heading text to lower-case, replaces spaces with ``-``,
    and strips all characters that are not alphanumeric, hyphens, or spaces
    (before the replacement step).
    """
    text = re.sub(r"[`*_~\[\]()]", "", heading_text)  # strip inline markup
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.ASCII)
    text = re.sub(r"\s+", "-", text.strip())
    return text


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_unresolved_tokens(content: str) -> list[str]:
    """Fail if any ``{{TOKEN}}`` placeholders remain."""
    errors: list[str] = []
    for match in _TOKEN_RE.finditer(content):
        lineno = content[: match.start()].count("\n") + 1
        errors.append(f"Line {lineno}: unresolved token '{match.group()}'")
    return errors


def _strip_code_blocks(content: str) -> str:
    """Return *content* with fenced and indented code blocks replaced by blank lines."""
    # Replace fenced code blocks delimited by ``` or ~~~ with equivalent blank lines
    result = re.sub(
        r"(?:```|~~~)[^\n]*\n.*?(?:```|~~~)",
        lambda m: "\n" * m.group(0).count("\n"),
        content,
        flags=re.DOTALL,
    )
    # Replace indented code blocks (4-space / tab indented lines)
    result = re.sub(r"(?m)^(    |\t).+$", "", result)
    return result


def check_heading_structure(content: str) -> list[str]:
    """
    Verify exactly one H1 and no skipped heading levels.

    A skipped level is when the next heading is more than one level deeper
    than the previous heading (e.g. H2 immediately followed by H4).
    Code blocks are excluded from heading detection.
    """
    errors: list[str] = []
    headings: list[tuple[int, str, int]] = []  # (level, text, lineno)

    stripped = _strip_code_blocks(content)
    for match in _HEADING_RE.finditer(stripped):
        level = len(match.group(1))
        text = match.group(2).strip()
        lineno = content[: match.start()].count("\n") + 1
        headings.append((level, text, lineno))

    h1_count = sum(1 for level, _, _ in headings if level == 1)
    if h1_count == 0:
        errors.append("No H1 heading found — exactly one is required")
    elif h1_count > 1:
        lines = [str(ln) for lvl, _, ln in headings if lvl == 1]
        errors.append(
            f"Multiple H1 headings found (lines {', '.join(lines)})"
            " — exactly one is required"
        )

    prev_level = 0
    for level, text, lineno in headings:
        if prev_level > 0 and level > prev_level + 1:
            errors.append(
                f"Line {lineno}: heading level skips from H{prev_level} to H{level} "
                f"(heading: '{text}')"
            )
        prev_level = level

    return errors


def check_generated_regions(content: str) -> list[str]:
    """Verify that every BEGIN marker has a matching END marker."""
    errors: list[str] = []
    open_regions: dict[str, int] = {}  # name → line number where BEGIN appears

    lines = content.splitlines()
    for lineno, line in enumerate(lines, start=1):
        for match in _BEGIN_RE.finditer(line):
            name = match.group(1)
            if name in open_regions:
                errors.append(
                    f"Line {lineno}: nested or duplicate BEGIN for region '{name}' "
                    f"(already opened at line {open_regions[name]})"
                )
            else:
                open_regions[name] = lineno

        for match in _END_RE.finditer(line):
            name = match.group(1)
            if name not in open_regions:
                errors.append(
                    f"Line {lineno}: END for region '{name}' has no matching BEGIN"
                )
            else:
                del open_regions[name]

    for name, lineno in sorted(open_regions.items(), key=lambda kv: kv[1]):
        errors.append(f"Line {lineno}: BEGIN for region '{name}' has no matching END")

    return errors


def check_duplicate_anchors(content: str) -> list[str]:
    """Fail if two headings produce the same GitHub anchor.

    Code blocks are excluded from heading detection.
    """
    errors: list[str] = []
    seen: dict[str, int] = {}  # anchor → first lineno

    stripped = _strip_code_blocks(content)
    for match in _HEADING_RE.finditer(stripped):
        text = match.group(2).strip()
        lineno = content[: match.start()].count("\n") + 1
        anchor = _github_anchor(text)
        if anchor in seen:
            errors.append(
                f"Line {lineno}: duplicate anchor '#{anchor}' "
                f"(first seen at line {seen[anchor]}, heading: '{text}')"
            )
        else:
            seen[anchor] = lineno

    return errors


def check_links_and_images(content: str) -> list[str]:
    """
    Reject:
    - Empty link targets: ``[text]()``
    - Empty link text:    ``[](url)``
    - Missing alt text:   ``![](url)``
    """
    errors: list[str] = []

    for match in _IMAGE_RE.finditer(content):
        alt = match.group(1)
        url = match.group(2).strip()
        lineno = content[: match.start()].count("\n") + 1
        if not alt.strip():
            errors.append(f"Line {lineno}: image missing alt text — '{match.group()}'")
        if not url:
            errors.append(f"Line {lineno}: image has empty URL — '{match.group()}'")

    for match in _LINK_RE.finditer(content):
        text = match.group(1)
        url = match.group(2).strip()
        lineno = content[: match.start()].count("\n") + 1
        if not text.strip():
            errors.append(f"Line {lineno}: link has empty text — '{match.group()}'")
        if not url:
            errors.append(f"Line {lineno}: link has empty target — '{match.group()}'")

    return errors


def check_byte_budget(path: Path) -> list[str]:
    """Fail if the file exceeds BYTE_BUDGET bytes."""
    size = path.stat().st_size
    if size > BYTE_BUDGET:
        return [
            f"File size {size} bytes exceeds {BYTE_BUDGET} byte budget "
            f"({size - BYTE_BUDGET} bytes over)"
        ]
    return []


def check_personal_identifiers(content: str) -> list[str]:
    """
    Fail if any personal identifier from ``_PERSONAL_IDS`` appears in the
    content.  Case-insensitive.
    """
    errors: list[str] = []
    lower = content.lower()
    for identifier in _PERSONAL_IDS:
        if identifier.lower() in lower:
            # Find the first occurrence for a line number
            idx = lower.find(identifier.lower())
            lineno = content[:idx].count("\n") + 1
            errors.append(
                f"Line {lineno}: personal identifier '{identifier}'"
                " found in universal template"
            )
    return errors


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def validate_file(path: Path, *, skip_personal_ids: bool = False) -> int:
    """
    Run all checks against *path*.

    Returns 0 on success, 1 on any failure.
    """
    if not path.exists() or not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    all_errors.extend(check_unresolved_tokens(content))
    all_errors.extend(check_heading_structure(content))
    all_errors.extend(check_generated_regions(content))
    all_errors.extend(check_duplicate_anchors(content))
    all_errors.extend(check_links_and_images(content))
    all_errors.extend(check_byte_budget(path))
    if not skip_personal_ids:
        all_errors.extend(check_personal_identifiers(content))

    if all_errors:
        print(
            f"Template validation FAILED ({len(all_errors)} error(s)) — {path}:",
            file=sys.stderr,
        )
        for err in all_errors:
            print(f"  ERROR: {err}", file=sys.stderr)
        return 1

    print(f"Template validation passed — {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    skip_personal = "--personal-ids-ok" in args
    paths = [a for a in args if not a.startswith("--")]

    if not paths:
        print(
            "Usage: validate_template.py <README.md> [<README.md> ...]"
            " [--personal-ids-ok]",
            file=sys.stderr,
        )
        return 1

    exit_code = 0
    for raw_path in paths:
        result = validate_file(Path(raw_path), skip_personal_ids=skip_personal)
        if result != 0:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
