"""
validate_assets.py
==================
Validate ``assets/profile/`` against the design-system asset contract.

Rules (from docs/DESIGN.md §12)
---------------------------------
1. Required files are present and have allowed extensions.
2. File sizes are within budget.
3. SVGs parse without XML error.
4. SVGs have a ``viewBox`` attribute on the root ``<svg>`` element.
5. SVGs have a ``<title>`` as first child of the root ``<svg>`` element.
6. SVGs contain no ``<script>`` tags or ``javascript:`` URL references.
7. Light/dark banner pair is complete (both files present).
8. ``assets/profile/README.md`` references only files that exist in the
   same directory.

Usage
-----
    python profile/validate_assets.py [path/to/assets/profile]

Exits with code 0 on success, 1 on any validation failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree

# ---------------------------------------------------------------------------
# Asset contract
# ---------------------------------------------------------------------------

# Extensions permitted for assets
ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".svg", ".png", ".jpg", ".jpeg", ".webp"})

# Required files with their max byte budgets
REQUIRED_ASSETS: dict[str, int] = {
    "banner-light.svg": 120 * 1024,  # 120 KB
    "banner-dark.svg": 120 * 1024,
    "mark.svg": 40 * 1024,
    "divider.svg": 8 * 1024,
    "README.md": 100 * 1024,
    "ASSET-BRIEF.md": 100 * 1024,
}

# Files that must form a light/dark pair
BANNER_PAIR: tuple[str, str] = ("banner-light.svg", "banner-dark.svg")

# SVG XML namespace
_SVG_NS = "http://www.w3.org/2000/svg"


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


def check_presence_and_extension(asset_dir: Path) -> list[str]:
    """Check that all required files exist and have allowed extensions."""
    errors: list[str] = []
    for name in REQUIRED_ASSETS:
        path = asset_dir / name
        if not path.exists():
            errors.append(f"Missing required file: {name}")
            continue
        suffix = path.suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS and suffix != ".md":
            errors.append(f"Disallowed extension '{suffix}' for file: {name}")
    return errors


def check_file_sizes(asset_dir: Path) -> list[str]:
    """Check that required files are within their byte budgets."""
    errors: list[str] = []
    for name, budget in REQUIRED_ASSETS.items():
        path = asset_dir / name
        if not path.exists():
            continue  # already reported by check_presence_and_extension
        size = path.stat().st_size
        if size > budget:
            errors.append(
                f"File '{name}' exceeds budget: {size} bytes > {budget} bytes"
            )
    return errors


def check_svg(path: Path) -> list[str]:
    """
    Validate a single SVG file:
    - Parses as valid XML.
    - Root element is ``<svg>`` (with or without namespace).
    - Root has a ``viewBox`` attribute.
    - First child element is ``<title>``.
    - No ``<script>`` elements anywhere.
    - No ``javascript:`` URLs anywhere in attribute values.
    """
    errors: list[str] = []
    name = path.name

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{name}: cannot read file — {exc}")
        return errors

    # Check for javascript: URLs in raw text (catches href="javascript:...")
    if "javascript:" in content.lower():
        errors.append(f"{name}: contains 'javascript:' URL reference (prohibited)")

    try:
        root = ElementTree.fromstring(content)  # noqa: S314 — local files only
    except ElementTree.ParseError as exc:
        errors.append(f"{name}: XML parse error — {exc}")
        return errors

    # Root tag: accept {namespace}svg or svg
    root_local = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    if root_local != "svg":
        errors.append(f"{name}: root element is <{root_local}>, expected <svg>")
        return errors

    # viewBox
    if "viewBox" not in root.attrib:
        errors.append(f"{name}: root <svg> is missing the 'viewBox' attribute")

    # <title> as first child
    children = list(root)
    if not children:
        errors.append(f"{name}: <svg> has no children; expected first child <title>")
    else:
        first_child = children[0]
        first_local = (
            first_child.tag.split("}")[-1] if "}" in first_child.tag else first_child.tag
        )
        if first_local != "title":
            errors.append(
                f"{name}: first child of <svg> is <{first_local}>, expected <title>"
            )
        elif not (first_child.text or "").strip():
            errors.append(f"{name}: <title> element is empty")

    # No <script> elements anywhere
    for elem in root.iter():
        local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if local == "script":
            errors.append(f"{name}: contains a <script> element (prohibited)")
            break

    return errors


def check_all_svgs(asset_dir: Path) -> list[str]:
    """Run SVG checks on every .svg file in the asset directory."""
    errors: list[str] = []
    for svg_path in sorted(asset_dir.glob("*.svg")):
        errors.extend(check_svg(svg_path))
    return errors


def check_banner_pair(asset_dir: Path) -> list[str]:
    """Check that both light and dark banners are present."""
    errors: list[str] = []
    for name in BANNER_PAIR:
        if not (asset_dir / name).exists():
            errors.append(f"Banner pair incomplete: missing '{name}'")
    return errors


def check_readme_references(asset_dir: Path) -> list[str]:
    """
    Parse ``README.md`` and verify that every file path it mentions
    that resolves to the same directory actually exists.
    """
    errors: list[str] = []
    readme = asset_dir / "README.md"
    if not readme.exists():
        return []  # already reported elsewhere

    content = readme.read_text(encoding="utf-8")

    # Match Markdown links: [text](path) and bare file references like `file.svg`
    # We look for any token that looks like a filename with a known extension.
    pattern = re.compile(
        r"[`\[\(]"                         # opening delimiter
        r"([^\s`\[\]\(\)]+\.(?:svg|png|jpg|jpeg|webp|md))"  # filename
        r"[`\]\)]",                        # closing delimiter
        re.IGNORECASE,
    )
    referenced: set[str] = set()
    for match in pattern.finditer(content):
        ref = match.group(1)
        # Only check bare filenames (no directory components)
        if "/" not in ref and "\\" not in ref:
            referenced.add(ref)

    for ref in sorted(referenced):
        if not (asset_dir / ref).exists():
            errors.append(
                f"README.md references '{ref}' but the file does not exist in {asset_dir}"
            )

    return errors


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def validate_directory(asset_dir: Path) -> int:
    """
    Run all checks against *asset_dir*.

    Returns 0 if all checks pass, 1 if any error is found.
    """
    if not asset_dir.exists() or not asset_dir.is_dir():
        print(f"ERROR: asset directory not found: {asset_dir}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    all_errors.extend(check_presence_and_extension(asset_dir))
    all_errors.extend(check_file_sizes(asset_dir))
    all_errors.extend(check_all_svgs(asset_dir))
    all_errors.extend(check_banner_pair(asset_dir))
    all_errors.extend(check_readme_references(asset_dir))

    if all_errors:
        print(f"Asset validation FAILED ({len(all_errors)} error(s)):", file=sys.stderr)
        for err in all_errors:
            print(f"  ERROR: {err}", file=sys.stderr)
        return 1

    print(f"Asset validation passed — {asset_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if args:
        asset_dir = Path(args[0])
    else:
        # Default: assets/profile/ relative to repository root
        asset_dir = Path(__file__).parents[1] / "assets" / "profile"

    return validate_directory(asset_dir)


if __name__ == "__main__":
    sys.exit(main())
