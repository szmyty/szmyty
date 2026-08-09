#!/usr/bin/env python3
"""
Generate a styled SVG card for Quote of the Day.
This script reads quote data from JSON and creates an SVG card.
"""

import json
import sys
from pathlib import Path
from typing import Optional

from lib.utils import (
    escape_xml,
    load_theme,
    get_theme_color,
    get_theme_gradient,
    get_theme_typography,
    get_theme_font_size,
    get_theme_card_dimension,
    get_theme_border_radius,
    format_timestamp_local,
    fallback_exists,
    handle_error_with_fallback,
)


# Constants for text layout
MAX_CHARS_PER_LINE = 55  # Maximum characters per line for quote text
AUTHOR_METADATA_SPACE = 60  # Vertical space reserved for author and metadata


def wrap_text(text: str, max_chars_per_line: int = MAX_CHARS_PER_LINE) -> list[str]:
    """
    Wrap text into lines based on maximum characters per line.
    Tries to break at word boundaries.
    
    Args:
        text: The text to wrap.
        max_chars_per_line: Maximum characters per line.
    
    Returns:
        List of text lines.
    """
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        # Check if adding this word would exceed the limit
        test_line = current_line + " " + word if current_line else word
        if len(test_line) <= max_chars_per_line:
            current_line = test_line
        else:
            # Start a new line
            if current_line:
                lines.append(current_line)
            current_line = word
    
    # Add the last line
    if current_line:
        lines.append(current_line)
    
    return lines


def generate_svg(
    text: str,
    author: str,
    source: str,
    fetched_at: str,
    category: Optional[str] = None,
) -> str:
    """
    Generate SVG card markup for Quote of the Day.
    
    Args:
        text: Quote text.
        author: Quote author.
        source: Source of the quote (api name or 'local').
        fetched_at: ISO 8601 timestamp when quote was fetched.
        category: Optional category for the quote.
    
    Returns:
        Complete SVG markup as a string.
    """

    # Load theme values
    theme = load_theme()
    bg_gradient = get_theme_gradient("background.default")
    font_family = get_theme_typography("font_family")
    
    # Colors from theme
    bg_primary = bg_gradient[0]
    bg_secondary = bg_gradient[1]
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    text_muted = get_theme_color("text", "muted")
    accent_teal = get_theme_color("text", "accent")
    accent_cyan = get_theme_color("accent", "cyan")
    
    # Card dimensions from theme - use weather card dimensions
    card_width = get_theme_card_dimension("widths", "weather")
    card_height = get_theme_card_dimension("heights", "weather")
    border_radius = get_theme_border_radius("xl")
    
    # Font sizes from theme
    font_size_xs = get_theme_font_size("xs")
    font_size_base = get_theme_font_size("base")
    font_size_md = get_theme_font_size("md")
    font_size_lg = get_theme_font_size("lg")
    font_size_2xl = get_theme_font_size("2xl")
    font_size_3xl = get_theme_font_size("3xl")
    
    # Spacing from theme
    spacing = theme.get("spacing", {})
    padding = spacing.get("xl", 15)
    
    # Card stroke settings from theme
    stroke_width = theme.get("cards", {}).get("stroke_width", 1)
    stroke_opacity = theme.get("cards", {}).get("stroke_opacity", 0.3)
    
    # Effect settings from theme
    shadow = theme.get("effects", {}).get("shadow", {})
    shadow_dx = shadow.get("dx", 0)
    shadow_dy = shadow.get("dy", 2)
    shadow_std = shadow.get("stdDeviation", 3)
    shadow_opacity = shadow.get("flood_opacity", 0.3)

    # Format date
    date_str = ""
    try:
        date_str = format_timestamp_local(fetched_at)
    except Exception:
        date_str = "Today"

    # Escape text for XML
    text_escaped = escape_xml(text)
    author_escaped = escape_xml(author)
    category_escaped = escape_xml(category) if category else ""
    
    # Wrap quote text to fit card
    text_lines = wrap_text(text_escaped, max_chars_per_line=MAX_CHARS_PER_LINE)
    
    # Calculate vertical positioning for centered text
    line_height = 18
    total_text_height = len(text_lines) * line_height
    start_y = (card_height - total_text_height - AUTHOR_METADATA_SPACE) // 2
    
    # Build text elements
    text_elements = []
    current_y = start_y
    for line in text_lines:
        text_elements.append(
            f'    <text x="{card_width // 2}" y="{current_y}" '
            f'font-family="{font_family}" font-size="{font_size_lg}" '
            f'fill="{text_primary}" text-anchor="middle">{line}</text>'
        )
        current_y += line_height
    
    # Position author below quote
    author_y = current_y + 25
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}">
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_primary}"/>
      <stop offset="100%" style="stop-color:{bg_secondary}"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="{shadow_dx}" dy="{shadow_dy}" stdDeviation="{shadow_std}" flood-opacity="{shadow_opacity}"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="url(#bg-gradient)"/>
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="none" stroke="{accent_cyan}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}"/>

  <!-- Decorative quote marks -->
  <g transform="translate({padding}, {padding})">
    <text font-family="{font_family}" font-size="{font_size_3xl}" fill="{accent_teal}" opacity="0.3">"</text>
  </g>
  <g transform="translate({card_width - padding - 15}, {card_height - padding - 20})">
    <text font-family="{font_family}" font-size="{font_size_3xl}" fill="{accent_teal}" opacity="0.3">"</text>
  </g>

  <!-- Decorative stars/orbs -->
  <circle cx="{padding + 40}" cy="{padding + 5}" r="2" fill="{accent_teal}" opacity="0.6"/>
  <circle cx="{card_width - padding - 40}" cy="{card_height - padding - 5}" r="2" fill="{accent_teal}" opacity="0.6"/>
  <circle cx="{padding + 60}" cy="{padding + 10}" r="1.5" fill="{accent_cyan}" opacity="0.4"/>
  <circle cx="{card_width - padding - 60}" cy="{card_height - padding - 10}" r="1.5" fill="{accent_cyan}" opacity="0.4"/>

  <!-- Header -->
  <g transform="translate({card_width // 2}, 30)">
    <text font-family="{font_family}" font-size="{font_size_2xl}" font-weight="bold" fill="{accent_teal}" text-anchor="middle">
      ✨ Quote of the Day
    </text>
  </g>

  <!-- Quote Text -->
  <g transform="translate(0, 60)">
{chr(10).join(text_elements)}
  </g>

  <!-- Author -->
  <g transform="translate({card_width // 2}, {author_y})">
    <text font-family="{font_family}" font-size="{font_size_md}" fill="{text_secondary}" text-anchor="middle">
      — {author_escaped}
    </text>
  </g>

  <!-- Footer metadata -->
  <g transform="translate({card_width // 2}, {card_height - 20})">
    <text font-family="{font_family}" font-size="{font_size_xs}" fill="{text_muted}" text-anchor="middle">
      {category_escaped if category_escaped else ""}{" • " if category_escaped else ""}{date_str}
    </text>
  </g>
</svg>"""

    return svg


def main() -> None:
    """
    Main entry point for Quote card generation.
    
    Reads quote metadata and generates SVG card.
    Uses fallback mechanism to preserve existing card on errors.
    """
    if len(sys.argv) < 2:
        print("Usage: generate_quote_card.py <quote.json> [output_path]", file=sys.stderr)
        sys.exit(1)

    quote_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "quotes/quote_card.svg"

    # Check if fallback exists before attempting generation
    has_fallback = fallback_exists(output_path)

    # Try to read quote data
    try:
        with open(quote_path, 'r') as f:
            quote = json.load(f)
    except (IOError, OSError, json.JSONDecodeError) as error:
        if handle_error_with_fallback("quote", str(error), output_path, has_fallback):
            print(f"Using fallback Quote SVG card: {output_path}", file=sys.stderr)
            return
        sys.exit(1)

    # Validate required fields
    if not quote.get("text") or not quote.get("author"):
        error_msg = "Missing required fields (text or author) in quote data"
        if handle_error_with_fallback("quote", error_msg, output_path, has_fallback):
            print(f"Using fallback Quote SVG card: {output_path}", file=sys.stderr)
            return
        sys.exit(1)

    # Try to generate SVG
    try:
        svg = generate_svg(
            text=quote.get("text", ""),
            author=quote.get("author", "Unknown"),
            source=quote.get("source", "unknown"),
            fetched_at=quote.get("fetched_at", ""),
            category=quote.get("category"),
        )
    except Exception as e:
        if handle_error_with_fallback("quote", f"SVG generation failed: {e}", output_path, has_fallback):
            print(f"Using fallback Quote SVG card: {output_path}", file=sys.stderr)
            return
        sys.exit(1)

    # Validate SVG looks correct
    if not svg or not svg.strip().startswith("<svg"):
        error_msg = "Generated SVG appears invalid (missing <svg> tag)"
        if handle_error_with_fallback("quote", error_msg, output_path, has_fallback):
            print(f"Using fallback Quote SVG card: {output_path}", file=sys.stderr)
            return
        sys.exit(1)

    # Try to write output
    try:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            f.write(svg)
        print(f"Generated SVG card: {output_path}", file=sys.stderr)
    except (IOError, OSError) as e:
        if handle_error_with_fallback("quote", f"Failed to write SVG: {e}", output_path, has_fallback):
            print(f"Using fallback Quote SVG card: {output_path}", file=sys.stderr)
            return
        sys.exit(1)


if __name__ == "__main__":
    main()
