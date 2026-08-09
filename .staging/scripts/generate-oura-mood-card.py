#!/usr/bin/env python3
"""
Generate a styled SVG card for Oura Ring mood dashboard.
This script reads mood and metrics data from JSON and creates an SVG card
with mood visualization, key metrics, and a sparkline chart.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from lib.utils import (
    escape_xml,
    safe_value,
    load_json,
    try_load_json,
    generate_sparkline_path,
    load_theme,
    get_theme_color,
    get_theme_gradient,
    get_theme_typography,
    get_theme_font_size,
    get_theme_card_dimension,
    get_theme_border_radius,
    get_theme_sparkline_value,
    get_theme_score_bar_value,
    get_theme_radial_bar_value,
    get_theme_decorative_accent_value,
    get_theme_chart_color,
    format_timestamp_local,
    format_time_since,
    is_data_stale,
    fallback_exists,
    log_fallback_used,
    handle_error_with_fallback,
)


def generate_radial_bars(scores: Dict[str, Any], cx: int = 60, cy: int = 50, radius: int = 40) -> str:
    """
    Generate SVG elements for radial progress bars showing scores.
    """
    # Load colors from theme
    accent_sleep = get_theme_color("accent", "sleep")
    sleep_gradient = get_theme_gradient("sleep")
    activity_gradient = get_theme_gradient("activity")
    
    # Load dimensions from theme
    stroke_width = get_theme_radial_bar_value("stroke_width", 6)
    opacity = get_theme_radial_bar_value("opacity", 0.8)
    ring_spacing = get_theme_radial_bar_value("ring_spacing", 8)
    
    elements = []
    metrics = [
        ("sleep_score", accent_sleep, "Sleep"),
        ("readiness_score", sleep_gradient[0], "Ready"),
        ("activity_score", activity_gradient[0], "Active"),
    ]

    for i, (key, color, _) in enumerate(metrics):
        value = scores.get(key, 50) or 50
        # Normalize to 0-100
        value = min(100, max(0, value))
        circumference = 2 * 3.14159 * radius
        dash_offset = circumference * (1 - value / 100)

        # Each bar is offset by rotation
        rotation = -90 + (i * 120)

        elements.append(f"""
    <circle cx="{cx}" cy="{cy}" r="{radius - (i * ring_spacing)}"
            fill="none" stroke="{color}" stroke-width="{stroke_width}"
            stroke-dasharray="{circumference * 0.33} {circumference}"
            stroke-dashoffset="{dash_offset * 0.33}"
            stroke-linecap="round" opacity="{opacity}"
            transform="rotate({rotation} {cx} {cy})"/>""")

    return "".join(elements)


def generate_score_bar(value: Any, x: int, y: int, width: Optional[int] = None, label: str = "") -> str:
    """Generate a horizontal score bar."""
    # Load colors from theme
    theme = load_theme()
    font_family = get_theme_typography("font_family")
    font_size_base = get_theme_font_size("base")
    text_secondary = get_theme_color("text", "secondary")
    text_primary = get_theme_color("text", "primary")
    score_high = get_theme_color("scores", "high")
    score_medium = get_theme_color("scores", "medium")
    score_low = get_theme_color("scores", "low")
    bar_background = get_theme_chart_color("bar_background")
    
    # Load dimensions from theme
    if width is None:
        width = get_theme_score_bar_value("width", 80)
    bar_height = get_theme_score_bar_value("height", 6)
    text_offset = get_theme_score_bar_value("text_offset", 8)
    
    score = value if value is not None else 0
    score = min(100, max(0, score))
    fill_width = int((score / 100) * width)

    # Color based on score
    if score >= 75:
        color = score_high
    elif score >= 50:
        color = score_medium
    else:
        color = score_low

    return f"""
    <g transform="translate({x}, {y})">
      <text font-family="{font_family}" font-size="{font_size_base}" fill="{text_secondary}" y="-3">{escape_xml(label)}</text>
      <rect width="{width}" height="{bar_height}" rx="3" fill="{bar_background}"/>
      <rect width="{fill_width}" height="{bar_height}" rx="3" fill="{color}"/>
      <text x="{width + text_offset}" y="5" font-family="{font_family}" font-size="{font_size_base}" fill="{text_primary}">{score}</text>
    </g>"""


def generate_svg(mood: dict, metrics: dict) -> str:
    """Generate SVG card markup."""
    
    # Load theme values
    theme = load_theme()
    bg_gradient_default = get_theme_gradient("background.default")
    font_family = get_theme_typography("font_family")
    font_family_emoji = get_theme_typography("font_family_emoji")
    
    # Colors from theme
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    text_muted = get_theme_color("text", "muted")
    accent_teal = get_theme_color("text", "accent")
    bg_dark = get_theme_color("background", "dark")
    
    # Card dimensions from theme
    card_width = get_theme_card_dimension("widths", "mood")
    card_height = get_theme_card_dimension("heights", "mood")
    border_radius = get_theme_border_radius("xl")
    
    # Font sizes from theme
    font_size_sm = get_theme_font_size("sm")
    font_size_base = get_theme_font_size("base")
    font_size_md = get_theme_font_size("md")
    font_size_2xl = get_theme_font_size("2xl")
    font_size_4xl = get_theme_font_size("4xl")
    font_size_5xl = get_theme_font_size("5xl")
    font_size_6xl = get_theme_font_size("6xl")
    
    # Card stroke settings from theme
    stroke_width = theme.get("cards", {}).get("stroke_width", 1)
    stroke_opacity = theme.get("cards", {}).get("stroke_opacity", 0.3)
    
    # Effect settings from theme
    glow = theme.get("effects", {}).get("glow", {})
    glow_std = glow.get("stdDeviation", 2)
    shadow = theme.get("effects", {}).get("shadow", {})
    shadow_dx = shadow.get("dx", 0)
    shadow_dy = shadow.get("dy", 2)
    shadow_std = shadow.get("stdDeviation", 3)
    shadow_opacity = shadow.get("flood_opacity", 0.3)

    # Extract mood data
    mood_name = escape_xml(mood.get("mood_name", "Unknown"))
    mood_icon = mood.get("mood_icon", "🌙")
    mood_score = mood.get("mood_score", 50)
    gradient = mood.get("mood_color_gradient", bg_gradient_default)
    mood_description = escape_xml(mood.get("mood_description", ""))

    # Extract raw scores
    raw_scores = mood.get("raw_scores", {})
    sleep_score = raw_scores.get("sleep_score")
    readiness_score = raw_scores.get("readiness_score")
    activity_score = raw_scores.get("activity_score")
    hrv = raw_scores.get("hrv")
    resting_hr = raw_scores.get("resting_hr")
    temp_deviation = raw_scores.get("temp_deviation")

    # Get interpretations
    interpreted = mood.get("interpreted_metrics", {})

    # Get timestamp
    updated_at_raw = mood.get("computed_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    # Generate sparkline from available scores
    sparkline_values = [sleep_score, readiness_score, activity_score, hrv or 50]
    sparkline_width = get_theme_sparkline_value("width", 120)
    sparkline_height = get_theme_sparkline_value("height", 30)
    sparkline_stroke_width = get_theme_sparkline_value("stroke_width", 2)
    sparkline_path = generate_sparkline_path(sparkline_values, width=sparkline_width, height=sparkline_height)

    # Generate score bars
    sleep_bar = generate_score_bar(sleep_score, 200, 75, 100, "😴 Sleep")
    readiness_bar = generate_score_bar(readiness_score, 200, 105, 100, "💪 Readiness")
    activity_bar = generate_score_bar(activity_score, 200, 135, 100, "🏃 Activity")
    
    # Calculate staleness badge
    staleness_badge = ""
    if updated_at_raw:
        time_since = format_time_since(updated_at_raw)
        is_stale = is_data_stale(updated_at_raw, stale_threshold_hours=24)
        
        # Use warning color if data is stale
        if is_stale:
            badge_color = accent_hr  # Warning/error color
            badge_icon = "⚠️ "
        else:
            badge_color = text_muted
            badge_icon = ""
        
        time_since_escaped = escape_xml(time_since)
        staleness_badge = f'''
  <!-- Staleness Badge -->
  <g transform="translate({card_width - 10}, 10)">
    <text x="0" y="12" font-family="{font_family}" font-size="{font_size_xs}" fill="{badge_color}" text-anchor="end">
      {badge_icon}Updated: {time_since_escaped}
    </text>
  </g>'''

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}">
  <defs>
    <linearGradient id="mood-bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{gradient[0]}"/>
      <stop offset="100%" style="stop-color:{gradient[1]}"/>
    </linearGradient>
    <linearGradient id="sparkline-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{gradient[0]}"/>
      <stop offset="100%" style="stop-color:{gradient[1]}"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="{glow_std}" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="soft-shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="{shadow_dx}" dy="{shadow_dy}" stdDeviation="{shadow_std}" flood-opacity="{shadow_opacity}"/>
    </filter>
  </defs>

  <!-- Background with mood gradient -->
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="url(#mood-bg-gradient)"/>
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="none" stroke="{accent_teal}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}"/>

  <!-- Header: Oura Ring badge -->
  <g transform="translate(20, 25)">
    <text font-family="{font_family}" font-size="{font_size_md}" fill="{accent_teal}" font-weight="500">
      ⭕ OURA RING
    </text>
  </g>

  <!-- Mood icon and name -->
  <g transform="translate(20, 55)">
    <text font-family="{font_family_emoji}" font-size="{font_size_6xl}" filter="url(#glow)">
      {mood_icon}
    </text>
    <text x="45" y="5" font-family="{font_family}" font-size="{font_size_4xl}" fill="{text_primary}" font-weight="bold" filter="url(#glow)">
      {mood_name}
    </text>
    <text x="45" y="22" font-family="{font_family}" font-size="{font_size_md}" fill="{text_secondary}">
      {mood_description}
    </text>
  </g>

  <!-- Score bars -->
  {sleep_bar}
  {readiness_bar}
  {activity_bar}

  <!-- HRV and Resting HR display -->
  <g transform="translate(20, 95)">
    <text font-family="{font_family}" font-size="{font_size_base}" fill="{text_secondary}">
      ❤️ HRV Balance
    </text>
    <text y="14" font-family="{font_family}" font-size="{font_size_2xl}" fill="{text_primary}" font-weight="600">
      {safe_value(hrv)}
    </text>
  </g>

  <g transform="translate(100, 95)">
    <text font-family="{font_family}" font-size="{font_size_base}" fill="{text_secondary}">
      💓 Rest HR
    </text>
    <text y="14" font-family="{font_family}" font-size="{font_size_2xl}" fill="{text_primary}" font-weight="600">
      {safe_value(resting_hr)}
    </text>
  </g>

  <!-- Mood Score indicator -->
  <g transform="translate(20, 145)">
    <text font-family="{font_family}" font-size="{font_size_base}" fill="{text_secondary}">
      🎯 Mood Score
    </text>
    <text y="18" font-family="{font_family}" font-size="{font_size_5xl}" fill="{accent_teal}" font-weight="bold" filter="url(#glow)">
      {mood_score}
    </text>
    <text x="45" y="14" font-family="{font_family}" font-size="{font_size_base}" fill="{text_muted}">
      / 100
    </text>
  </g>

  <!-- Sparkline visualization -->
  <g transform="translate(280, 165)">
    <text font-family="{font_family}" font-size="{font_size_sm}" fill="{text_muted}" y="-5">
      Metrics Trend
    </text>
    <rect width="{sparkline_width}" height="35" rx="4" fill="{bg_dark}" fill-opacity="0.5"/>
    <g transform="translate(5, 2)">
      <path d="{sparkline_path}" fill="none" stroke="url(#sparkline-gradient)" stroke-width="{sparkline_stroke_width}" stroke-linecap="round"/>
    </g>
  </g>

  {staleness_badge}

  <!-- Decorative accent -->"""
    
    # Calculate decorative accent position and dimensions
    accent_x_offset = get_theme_decorative_accent_value('x_offset', 20)
    accent_y_offset = get_theme_decorative_accent_value('y_offset', 15)
    accent_width = get_theme_decorative_accent_value('width', 4)
    
    svg += f"""
  <rect x="{card_width - accent_x_offset}" y="{accent_y_offset}" width="{accent_width}" height="190" rx="2" fill="{accent_teal}" fill-opacity="{stroke_opacity}"/>
</svg>"""

    return svg


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: generate-oura-mood-card.py <mood.json> [metrics.json] [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    mood_path = sys.argv[1]
    metrics_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = sys.argv[3] if len(sys.argv) > 3 else "oura/mood_dashboard.svg"

    # Check if fallback exists before attempting generation
    has_fallback = fallback_exists(output_path)

    # Try to read mood data
    mood, error = try_load_json(mood_path, "Mood file")
    if error or mood is None:
        if handle_error_with_fallback("mood", error or "No data loaded", output_path, has_fallback):
            print(f"Using fallback mood dashboard SVG: {output_path}", file=sys.stderr)
            return
        # If we get here without a fallback, mood must be None and we should exit
        sys.exit(1)

    # Read metrics data (optional, for additional visualizations)
    metrics = {}
    if metrics_path:
        try:
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Continue without metrics

    # Try to generate SVG
    try:
        svg = generate_svg(mood, metrics)
    except Exception as e:
        if handle_error_with_fallback("mood", f"SVG generation failed: {e}", output_path, has_fallback):
            print(f"Using fallback mood dashboard SVG: {output_path}", file=sys.stderr)
            return

    # Validate SVG looks correct
    if not svg or not svg.strip().startswith("<svg"):
        error_msg = "Generated SVG appears invalid (missing <svg> tag)"
        if handle_error_with_fallback("mood", error_msg, output_path, has_fallback):
            print(f"Using fallback mood dashboard SVG: {output_path}", file=sys.stderr)
            return

    # Try to write output
    try:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            f.write(svg)
        print(f"Generated Oura mood dashboard SVG: {output_path}", file=sys.stderr)
    except (IOError, OSError) as e:
        if handle_error_with_fallback("mood", f"Failed to write SVG: {e}", output_path, has_fallback):
            print(f"Using fallback mood dashboard SVG: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
