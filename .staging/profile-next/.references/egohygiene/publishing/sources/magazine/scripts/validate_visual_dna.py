#!/usr/bin/env python3
"""
Visual DNA Validator

Validates page.json files against the edition's visual_dna.json to ensure
new or updated pages remain consistent with the established visual system.

A page is considered divergent when it shares no canonical textures AND no
canonical colours with the edition's visual DNA.

Usage:
    python scripts/validate_visual_dna.py <page.json> [<page.json> ...]

Example:
    python scripts/validate_visual_dna.py projects/egohygiene/edition_1/pages/06_rest/page.json
"""

import json
import sys
from pathlib import Path


def load_edition_dna(page_path: Path) -> dict | None:
    """Locate and load the visual_dna.json for the edition containing the page."""
    candidate = page_path.resolve().parent
    while candidate != candidate.parent:
        dna_file = candidate / "visual_dna.json"
        if dna_file.exists():
            with open(dna_file) as f:
                return json.load(f)
        candidate = candidate.parent
    return None


def verify_page_adherence(page_schema: dict, edition_dna: dict) -> dict:
    """Check if a page follows the edition's visual DNA."""
    page_visual = page_schema.get("visual_style", {})

    page_textures = set(page_visual.get("texture", []))
    page_colors = set()
    for colors in page_visual.get("color_palette", {}).values():
        page_colors.update(colors)

    canonical_textures = set(edition_dna.get("canonical_textures", []))
    canonical_colors = set(edition_dna.get("canonical_colors", []))

    texture_match_ratio = (
        len(page_textures & canonical_textures) / len(canonical_textures)
        if canonical_textures
        else 0.0
    )
    color_match_ratio = (
        len(page_colors & canonical_colors) / len(canonical_colors)
        if canonical_colors
        else 0.0
    )

    return {
        "texture_match_ratio": texture_match_ratio,
        "color_match_ratio": color_match_ratio,
        "divergent_textures": sorted(page_textures - canonical_textures),
        "divergent_colors": sorted(page_colors - canonical_colors),
    }


def validate_page(page_json_path: Path) -> bool:
    """Validate a single page.json against its edition's visual DNA.

    Returns True if the page passes validation, False otherwise.
    """
    if not page_json_path.exists():
        print(f"  ✗ File not found: {page_json_path}")
        return False

    with open(page_json_path) as f:
        page_schema = json.load(f)

    edition_dna = load_edition_dna(page_json_path)
    if edition_dna is None:
        print(f"  ✗ No visual_dna.json found for: {page_json_path}")
        return False

    visual_style = page_schema.get("visual_style", {})
    if not visual_style:
        print(f"  ⚠  No visual_style defined, skipping: {page_json_path}")
        return True

    adherence = verify_page_adherence(page_schema, edition_dna)

    texture_ratio = adherence["texture_match_ratio"]
    color_ratio = adherence["color_match_ratio"]

    # A page fails only when it shares nothing with the canonical visual DNA.
    passed = not (texture_ratio == 0.0 and color_ratio == 0.0)

    if passed:
        print(
            f"  ✓ {page_json_path}"
            f"  (texture {texture_ratio:.0%}, color {color_ratio:.0%})"
        )
    else:
        print(
            f"  ✗ {page_json_path}"
            f"  (texture {texture_ratio:.0%}, color {color_ratio:.0%})"
            f" — visual drift detected"
        )
        if adherence["divergent_textures"]:
            print(f"    Divergent textures: {', '.join(adherence['divergent_textures'][:5])}")
        if adherence["divergent_colors"]:
            print(f"    Divergent colors: {', '.join(adherence['divergent_colors'][:5])}")

    return passed


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_visual_dna.py <page.json> [<page.json> ...]")
        print("\nExample:")
        print("  python scripts/validate_visual_dna.py projects/egohygiene/edition_1/pages/06_rest/page.json")
        sys.exit(1)

    page_paths = [Path(p) for p in sys.argv[1:]]

    print(f"\n🔍 Visual DNA Validation ({len(page_paths)} file(s))\n")

    failures: list[Path] = []
    for page_path in page_paths:
        if not validate_page(page_path):
            failures.append(page_path)

    print()
    if failures:
        print(f"❌ Validation failed: {len(failures)} page(s) diverged from visual DNA")
        for f in failures:
            print(f"   • {f}")
        sys.exit(1)
    else:
        print(f"✅ All {len(page_paths)} page(s) passed visual DNA validation")
        sys.exit(0)


if __name__ == "__main__":
    main()
