#!/usr/bin/env python3
"""
Generate a styled SVG card for SoundCloud latest release.
This script reads track metadata from JSON and creates an SVG card.
"""

import sys
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional

from lib.utils import (
    escape_xml,
    load_and_validate_json,
    try_load_and_validate_json,
    load_theme,
    get_theme_color,
    get_theme_gradient,
    get_theme_typography,
    get_theme_font_size,
    get_theme_card_dimension,
    get_theme_border_radius,
    format_timestamp_local,
    format_time_since,
    format_large_number,
    format_duration_ms,
    optimize_image_file,
    fallback_exists,
    log_fallback_used,
    handle_error_with_fallback,
)


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format using local timezone."""
    try:
        # Use the standardized format_timestamp_local function
        return format_timestamp_local(date_str)
    except (ValueError, AttributeError):
        return date_str


def get_artwork_base64(artwork_path: str) -> str:
    """Read artwork file, optimize it, and return base64 encoded data URI.
    
    The image is optimized for embedding by:
    - Reducing resolution to max 100x100 (artwork thumbnail size)
    - Compressing JPEG with quality setting from theme
    """
    try:
        path = Path(artwork_path)
        if path.exists():
            # Optimize image before encoding (100x100 is the artwork display size)
            optimized_data = optimize_image_file(
                artwork_path,
                max_width=100,
                max_height=100,
            )
            data = base64.b64encode(optimized_data).decode("utf-8")
            # Determine MIME type
            suffix = path.suffix.lower()
            mime = "image/jpeg" if suffix in [".jpg", ".jpeg"] else "image/png"
            return f"data:{mime};base64,{data}"
    except (OSError, IOError) as e:
        print(f"Warning: Could not load artwork: {e}", file=sys.stderr)
    return ""


def generate_svg(
    title: str,
    artist: str,
    genre: str,
    duration_ms: int,
    playback_count: int,
    created_at: str,
    permalink_url: str,
    artwork_data_uri: str,
    updated_at: Optional[str] = None,
) -> str:
    """
    Generate SVG card markup for SoundCloud track.
    
    Args:
        title: Track title.
        artist: Artist name.
        genre: Music genre.
        duration_ms: Track duration in milliseconds.
        playback_count: Number of plays.
        created_at: ISO 8601 timestamp when track was created.
        permalink_url: SoundCloud track URL.
        artwork_data_uri: Base64-encoded data URI for artwork image.
        updated_at: Optional ISO 8601 timestamp when card was generated.
    
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
    accent_orange = get_theme_color("accent", "orange")
    
    # Card dimensions from theme
    card_width = get_theme_card_dimension("widths", "soundcloud")
    card_height = get_theme_card_dimension("heights", "soundcloud")
    border_radius = get_theme_border_radius("xl")
    border_radius_lg = get_theme_border_radius("lg")
    
    # Font sizes from theme
    font_size_base = get_theme_font_size("base")
    font_size_md = get_theme_font_size("md")
    font_size_lg = get_theme_font_size("lg")
    font_size_2xl = get_theme_font_size("2xl")
    font_size_xs = get_theme_font_size("xs")
    
    # Card stroke settings from theme
    stroke_width = theme.get("cards", {}).get("stroke_width", 1)
    stroke_opacity = theme.get("cards", {}).get("stroke_opacity", 0.3)
    
    # Effect settings from theme
    shadow = theme.get("effects", {}).get("shadow", {})
    shadow_dx = shadow.get("dx", 0)
    shadow_dy = shadow.get("dy", 2)
    shadow_std = shadow.get("stdDeviation", 3)
    shadow_opacity = shadow.get("flood_opacity", 0.3)

    # Format values
    duration = format_duration_ms(duration_ms)
    plays = format_large_number(playback_count)
    date = format_date(created_at)
    
    # Calculate staleness indicator
    staleness = ""
    if updated_at:
        staleness = format_time_since(updated_at)

    # Escape text for XML
    title_escaped = escape_xml(title)
    artist_escaped = escape_xml(artist)
    genre_escaped = escape_xml(genre)
    permalink_escaped = escape_xml(permalink_url)
    staleness_escaped = escape_xml(staleness)

    # Truncate title if too long
    display_title = title_escaped[:35] + "..." if len(title_escaped) > 35 else title_escaped

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}">
  <defs>
    <clipPath id="artwork-clip">
      <rect x="10" y="10" width="100" height="100" rx="{border_radius_lg}"/>
    </clipPath>
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
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="none" stroke="{accent_orange}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}"/>

  <!-- Artwork -->
  <g clip-path="url(#artwork-clip)">
    <image x="10" y="10" width="100" height="100" preserveAspectRatio="xMidYMid slice" href="{artwork_data_uri}"/>
  </g>
  <rect x="10" y="10" width="100" height="100" rx="{border_radius_lg}" fill="none" stroke="{accent_orange}" stroke-width="2" stroke-opacity="0.5"/>

  <!-- SoundCloud Logo/Icon -->
  <g transform="translate(370, 10)">
    <circle cx="10" cy="10" r="10" fill="{accent_orange}"/>
    <text x="10" y="14" font-family="Arial, sans-serif" font-size="{font_size_base}" fill="white" text-anchor="middle" font-weight="bold">SC</text>
  </g>

  <!-- Staleness Badge -->
  {f'''<g transform="translate({card_width - 10}, 10)">
    <text x="0" y="12" font-family="{font_family}" font-size="{font_size_xs}" fill="{text_muted}" text-anchor="end">Updated: {staleness_escaped}</text>
  </g>''' if staleness else ''}

  <!-- Track Info -->
  <g transform="translate(125, 25)">
    <!-- Title -->
    <text font-family="{font_family}" font-size="{font_size_2xl}" font-weight="bold" fill="{text_primary}">
      {display_title}
    </text>

    <!-- Artist -->
    <text y="22" font-family="{font_family}" font-size="{font_size_lg}" fill="{accent_orange}">
      {artist_escaped}
    </text>

    <!-- Genre & Duration -->
    <text y="42" font-family="{font_family}" font-size="{font_size_md}" fill="{text_secondary}">
      <tspan fill="{accent_teal}">{genre_escaped}</tspan>
      <tspan fill="{text_muted}"> · </tspan>
      <tspan>{duration}</tspan>
    </text>

    <!-- Stats -->
    <g transform="translate(0, 58)">
      <!-- Play count icon -->
      <polygon points="0,0 0,10 8,5" fill="{text_secondary}"/>
      <text x="12" y="9" font-family="{font_family}" font-size="{font_size_base}" fill="{text_secondary}">{plays} plays</text>

      <!-- Date -->
      <text x="80" y="9" font-family="{font_family}" font-size="{font_size_base}" fill="{text_secondary}">Released {date}</text>
    </g>
  </g>

  <!-- Clickable overlay (for GitHub markdown) -->
  <a href="{permalink_escaped}" target="_blank">
    <rect width="{card_width}" height="{card_height}" fill="transparent" style="cursor: pointer;"/>
  </a>
</svg>"""

    return svg


def main() -> None:
    """
    Main entry point for SoundCloud card generation.
    
    Reads track metadata and artwork, generates SVG card.
    Uses fallback mechanism to preserve existing card on errors.
    """
    if len(sys.argv) < 2:
        print("Usage: generate-card.py <metadata.json> [artwork_path] [output_path]", file=sys.stderr)
        sys.exit(1)

    metadata_path = sys.argv[1]
    artwork_path = sys.argv[2] if len(sys.argv) > 2 else "assets/soundcloud-artwork.jpg"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "assets/soundcloud-card.svg"

    # Check if fallback exists before attempting generation
    has_fallback = fallback_exists(output_path)

    # Try to read and validate metadata
    metadata, error = try_load_and_validate_json(
        metadata_path, "soundcloud-track", "SoundCloud track metadata file"
    )
    if error or metadata is None:
        if handle_error_with_fallback("soundcloud", error or "No data loaded", output_path, has_fallback):
            print(f"Using fallback SoundCloud SVG card: {output_path}", file=sys.stderr)
            return
        # If we get here without a fallback, metadata must be None and we should exit
        sys.exit(1)

    # Get artwork as base64 (optional, continue without it if missing)
    artwork_data_uri = get_artwork_base64(artwork_path)

    # Try to generate SVG
    try:
        svg = generate_svg(
            title=metadata.get("title", "Unknown Track"),
            artist=metadata.get("artist", "Unknown Artist"),
            genre=metadata.get("genre", "Music"),
            duration_ms=metadata.get("duration_ms", 0),
            playback_count=metadata.get("playback_count", 0),
            created_at=metadata.get("created_at", ""),
            permalink_url=metadata.get("permalink_url", "https://soundcloud.com"),
            artwork_data_uri=artwork_data_uri,
            updated_at=metadata.get("updated_at"),
        )
    except Exception as e:
        if handle_error_with_fallback("soundcloud", f"SVG generation failed: {e}", output_path, has_fallback):
            print(f"Using fallback SoundCloud SVG card: {output_path}", file=sys.stderr)
            return

    # Validate SVG looks correct
    if not svg or not svg.strip().startswith("<svg"):
        error_msg = "Generated SVG appears invalid (missing <svg> tag)"
        if handle_error_with_fallback("soundcloud", error_msg, output_path, has_fallback):
            print(f"Using fallback SoundCloud SVG card: {output_path}", file=sys.stderr)
            return

    # Try to write output
    try:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            f.write(svg)
        print(f"Generated SVG card: {output_path}", file=sys.stderr)
    except (IOError, OSError) as e:
        if handle_error_with_fallback("soundcloud", f"Failed to write SVG: {e}", output_path, has_fallback):
            print(f"Using fallback SoundCloud SVG card: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
