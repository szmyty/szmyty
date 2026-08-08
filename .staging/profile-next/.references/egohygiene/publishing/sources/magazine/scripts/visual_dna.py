#!/usr/bin/env python3
"""
Visual DNA Propagator

Purpose:
    Ensures consistent aesthetic language across all pages within an edition.
    Extracts the most frequently used visual style elements (textures, colors,
    iconography, and aesthetic tags) from existing page schemas and synthesises
    a canonical "visual DNA" for the edition.  Each page is then audited against
    this canonical identity to surface divergent elements.

Usage:
    Run from the repository root, passing an edition directory as the sole
    argument:

        python scripts/visual_dna.py <edition_directory>

    Example:

        python scripts/visual_dna.py projects/egohygiene/edition_1

Expected inputs:
    An edition directory containing a ``pages/`` sub-directory.  Each page
    sub-directory may contain one or more ``*.page.json`` schema files with a
    top-level ``visual_style`` key.

Expected outputs:
    - A human-readable adherence report printed to stdout.
    - A ``visual_dna.json`` file written to the edition directory containing
      the synthesised canonical visual language for reuse.
"""

import json
from pathlib import Path
from collections import Counter


def harvest_visual_patterns(edition_path: Path):
    """Collect all visual_style elements from existing pages"""
    pages_dir = edition_path / "pages"
    
    all_textures = []
    all_colors = []
    all_iconography = []
    all_aesthetics = []
    
    for page_dir in pages_dir.iterdir():
        if not page_dir.is_dir():
            continue
        
        schema_files = list(page_dir.glob("*.page.json"))
        if not schema_files:
            continue
        
        with open(schema_files[0]) as f:
            schema = json.load(f)
        
        visual_style = schema.get("visual_style", {})
        
        all_textures.extend(visual_style.get("texture", []))
        all_iconography.extend(visual_style.get("iconography", []))
        
        # Handle different schema variations
        if "aesthetic" in visual_style:
            all_aesthetics.extend(visual_style["aesthetic"])
        
        color_palette = visual_style.get("color_palette", {})
        for category, colors in color_palette.items():
            all_colors.extend(colors)
    
    return {
        "texture_vocabulary": Counter(all_textures),
        "color_vocabulary": Counter(all_colors),
        "icon_vocabulary": Counter(all_iconography),
        "aesthetic_vocabulary": Counter(all_aesthetics)
    }


def synthesize_edition_visual_dna(patterns: dict) -> dict:
    """Create canonical visual DNA from observed patterns"""
    
    # Take most common elements as the edition's visual identity
    core_textures = [t for t, count in patterns["texture_vocabulary"].most_common(5)]
    core_colors = [c for c, count in patterns["color_vocabulary"].most_common(8)]
    core_icons = [i for i, count in patterns["icon_vocabulary"].most_common(6)]
    core_aesthetics = [a for a, count in patterns["aesthetic_vocabulary"].most_common(4)]
    
    return {
        "canonical_textures": core_textures,
        "canonical_colors": core_colors,
        "canonical_iconography": core_icons,
        "canonical_aesthetics": core_aesthetics
    }


def verify_page_adherence(page_schema: dict, edition_dna: dict) -> dict:
    """Check if a page follows the edition's visual DNA"""
    page_visual = page_schema.get("visual_style", {})
    
    page_textures = set(page_visual.get("texture", []))
    page_colors = set()
    for colors in page_visual.get("color_palette", {}).values():
        page_colors.update(colors)
    
    canonical_textures = set(edition_dna["canonical_textures"])
    canonical_colors = set(edition_dna["canonical_colors"])
    
    texture_compliance = len(page_textures & canonical_textures) / len(canonical_textures) if canonical_textures else 0
    color_compliance = len(page_colors & canonical_colors) / len(canonical_colors) if canonical_colors else 0
    
    return {
        "texture_match_ratio": texture_compliance,
        "color_match_ratio": color_compliance,
        "divergent_textures": list(page_textures - canonical_textures),
        "divergent_colors": list(page_colors - canonical_colors)
    }


def generate_visual_dna_report(edition_path: Path):
    """Create comprehensive visual DNA analysis for edition"""
    print(f"\n🎨 Visual DNA Analysis: {edition_path.name}\n")
    
    patterns = harvest_visual_patterns(edition_path)
    dna = synthesize_edition_visual_dna(patterns)
    
    print("CANONICAL VISUAL LANGUAGE")
    print("=" * 60)
    print(f"\nTextures ({len(dna['canonical_textures'])}):")
    for texture in dna['canonical_textures']:
        print(f"  • {texture}")
    
    print(f"\nColors ({len(dna['canonical_colors'])}):")
    for color in dna['canonical_colors']:
        print(f"  • {color}")
    
    print(f"\nIconography ({len(dna['canonical_iconography'])}):")
    for icon in dna['canonical_iconography']:
        print(f"  • {icon}")
    
    if dna['canonical_aesthetics']:
        print(f"\nAesthetics ({len(dna['canonical_aesthetics'])}):")
        for aesthetic in dna['canonical_aesthetics']:
            print(f"  • {aesthetic}")
    
    print("\n" + "=" * 60)
    print("\nPAGE ADHERENCE AUDIT")
    print("=" * 60)
    
    pages_dir = edition_path / "pages"
    for page_dir in sorted(pages_dir.iterdir()):
        if not page_dir.is_dir():
            continue
        
        schema_files = list(page_dir.glob("*.page.json"))
        if not schema_files:
            continue
        
        with open(schema_files[0]) as f:
            schema = json.load(f)
        
        adherence = verify_page_adherence(schema, dna)
        
        print(f"\n{page_dir.name}:")
        print(f"  Texture adherence: {adherence['texture_match_ratio']:.0%}")
        print(f"  Color adherence: {adherence['color_match_ratio']:.0%}")
        
        if adherence['divergent_textures']:
            print(f"  Unique textures: {', '.join(adherence['divergent_textures'][:3])}")
        
        if adherence['divergent_colors']:
            print(f"  Unique colors: {', '.join(adherence['divergent_colors'][:3])}")
    
    print()
    
    # Save the DNA for reuse
    dna_output = edition_path / "visual_dna.json"
    with open(dna_output, 'w') as f:
        json.dump(dna, f, indent=2)
    print(f"✓ Visual DNA saved to: {dna_output}\n")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/visual_dna.py <edition_directory>")
        print("\nExample: python scripts/visual_dna.py projects/egohygiene/edition_1")
        sys.exit(1)
    
    edition_path = Path(sys.argv[1])
    
    if not edition_path.exists():
        print(f"Error: {edition_path} does not exist")
        sys.exit(1)
    
    generate_visual_dna_report(edition_path)


if __name__ == "__main__":
    main()
