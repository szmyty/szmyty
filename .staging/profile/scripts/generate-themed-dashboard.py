#!/usr/bin/env python3
"""
Generate a consolidated dashboard with theme selection support.

This script is a wrapper around generate-consolidated-dashboard that allows
theme selection via command line arguments.

Usage:
    python generate-themed-dashboard.py [output_path] [--theme dark|light]
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional

# Add lib to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from utils import (  # type: ignore[import-not-found]
    escape_xml,
    safe_value,
    load_theme,
    get_theme_color,
    get_theme_gradient,
    get_theme_typography,
    get_theme_font_size,
    get_theme_border_radius,
    format_timestamp_local,
    format_large_number,
    try_load_json,
)


def load_developer_stats() -> Optional[Dict]:
    """Load developer statistics from JSON file."""
    data, error = try_load_json("developer/stats.json")
    return data


def load_soundcloud_data() -> Optional[Dict]:
    """Load SoundCloud track metadata."""
    data, error = try_load_json("assets/metadata.json")
    return data


def load_weather_data() -> Optional[Dict]:
    """Load weather data."""
    data, error = try_load_json("weather/weather.json")
    return data


def load_location_data() -> Optional[Dict]:
    """Load location data."""
    weather_data, error = try_load_json("weather/weather.json")
    if weather_data:
        return {
            "location": weather_data.get("location", "Unknown"),
            "display_name": weather_data.get("display_name", "Unknown"),
            "coordinates": weather_data.get("coordinates", {}),
        }
    return None


def load_oura_mood_data() -> Optional[Dict]:
    """Load Oura mood data."""
    data, error = try_load_json("oura/mood.json")
    return data


def generate_developer_section(stats: Optional[Dict], x: int, y: int, theme_name: str) -> str:
    """Generate developer stats section."""
    if not stats:
        return ""
    
    font_family = get_theme_typography("font_family")
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    accent_developer = get_theme_color("accent", "developer")
    panel_bg = get_theme_color("background", "panel")
    border_radius = get_theme_border_radius("md")
    
    repos = stats.get("repos", 0)
    stars = stats.get("stars", 0)
    commits = stats.get("commit_activity", {}).get("total_30_days", 0)
    
    return f"""
    <g transform="translate({x}, {y})">
      <rect width="260" height="90" rx="{border_radius}" fill="{panel_bg}" stroke="{accent_developer}" stroke-width="1" stroke-opacity="0.3"/>
      <text x="10" y="20" font-family="{font_family}" font-size="12" fill="{accent_developer}" font-weight="600">
        💻 Developer Stats
      </text>
      <text x="10" y="40" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Repos: <tspan fill="{text_primary}" font-weight="500">{repos}</tspan>
      </text>
      <text x="10" y="55" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Stars: <tspan fill="{text_primary}" font-weight="500">{format_large_number(stars)}</tspan>
      </text>
      <text x="10" y="70" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Commits (30d): <tspan fill="{text_primary}" font-weight="500">{format_large_number(commits)}</tspan>
      </text>
    </g>"""


def generate_soundcloud_section(data: Optional[Dict], x: int, y: int, theme_name: str) -> str:
    """Generate SoundCloud track section."""
    if not data:
        return ""
    
    font_family = get_theme_typography("font_family")
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    accent_orange = get_theme_color("accent", "orange")
    panel_bg = get_theme_color("background", "panel")
    border_radius = get_theme_border_radius("md")
    
    title = data.get("title", "Unknown")
    artist = data.get("artist", "Unknown")
    plays = data.get("playback_count", 0)
    
    display_title = title[:20] + "..." if len(title) > 20 else title
    
    return f"""
    <g transform="translate({x}, {y})">
      <rect width="260" height="90" rx="{border_radius}" fill="{panel_bg}" stroke="{accent_orange}" stroke-width="1" stroke-opacity="0.3"/>
      <text x="10" y="20" font-family="{font_family}" font-size="12" fill="{accent_orange}" font-weight="600">
        🎵 SoundCloud
      </text>
      <text x="10" y="40" font-family="{font_family}" font-size="10" fill="{text_primary}" font-weight="500">
        {escape_xml(display_title)}
      </text>
      <text x="10" y="55" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Artist: <tspan fill="{text_primary}">{escape_xml(artist)}</tspan>
      </text>
      <text x="10" y="70" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Plays: <tspan fill="{text_primary}">{format_large_number(plays)}</tspan>
      </text>
    </g>"""


def generate_weather_section(data: Optional[Dict], x: int, y: int, theme_name: str) -> str:
    """Generate weather section."""
    if not data:
        return ""
    
    font_family = get_theme_typography("font_family")
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    accent_cyan = get_theme_color("accent", "cyan")
    panel_bg = get_theme_color("background", "panel")
    border_radius = get_theme_border_radius("md")
    
    current = data.get("current", {})
    daily = data.get("daily", {})
    temp = current.get("temperature", 0)
    condition = current.get("condition", "Unknown")
    emoji = current.get("emoji", "🌤️")
    temp_max = daily.get("temperature_max", 0)
    temp_min = daily.get("temperature_min", 0)
    
    return f"""
    <g transform="translate({x}, {y})">
      <rect width="260" height="90" rx="{border_radius}" fill="{panel_bg}" stroke="{accent_cyan}" stroke-width="1" stroke-opacity="0.3"/>
      <text x="10" y="20" font-family="{font_family}" font-size="12" fill="{accent_cyan}" font-weight="600">
        🌦️ Weather
      </text>
      <text x="10" y="40" font-family="{font_family}" font-size="10" fill="{text_primary}" font-weight="500">
        {emoji} {escape_xml(condition)}
      </text>
      <text x="10" y="55" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Current: <tspan fill="{text_primary}">{temp:.1f}°C</tspan>
      </text>
      <text x="10" y="70" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Range: <tspan fill="{text_primary}">{temp_min:.1f}°C - {temp_max:.1f}°C</tspan>
      </text>
    </g>"""


def generate_location_section(data: Optional[Dict], x: int, y: int, theme_name: str) -> str:
    """Generate location section."""
    if not data:
        return ""
    
    font_family = get_theme_typography("font_family")
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    accent_teal = get_theme_color("text", "accent")
    panel_bg = get_theme_color("background", "panel")
    border_radius = get_theme_border_radius("md")
    
    location = data.get("location", "Unknown")
    coords = data.get("coordinates", {})
    lat = coords.get("lat", 0)
    lon = coords.get("lon", 0)
    
    return f"""
    <g transform="translate({x}, {y})">
      <rect width="260" height="90" rx="{border_radius}" fill="{panel_bg}" stroke="{accent_teal}" stroke-width="1" stroke-opacity="0.3"/>
      <text x="10" y="20" font-family="{font_family}" font-size="12" fill="{accent_teal}" font-weight="600">
        📍 Location
      </text>
      <text x="10" y="40" font-family="{font_family}" font-size="10" fill="{text_primary}" font-weight="500">
        {escape_xml(location)}
      </text>
      <text x="10" y="55" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Lat: <tspan fill="{text_primary}">{lat:.4f}</tspan>
      </text>
      <text x="10" y="70" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Lon: <tspan fill="{text_primary}">{lon:.4f}</tspan>
      </text>
    </g>"""


def generate_oura_mood_section(data: Optional[Dict], x: int, y: int, theme_name: str) -> str:
    """Generate Oura mood section."""
    if not data:
        return ""
    
    font_family = get_theme_typography("font_family")
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    accent_sleep = get_theme_color("accent", "sleep")
    panel_bg = get_theme_color("background", "panel")
    border_radius = get_theme_border_radius("md")
    
    mood_name = data.get("mood_name", "Unknown")
    mood_score = data.get("mood_score", 0)
    mood_icon = data.get("mood_icon", "😊")
    
    raw_scores = data.get("raw_scores", {})
    sleep_score = raw_scores.get("sleep_score", 0)
    readiness_score = raw_scores.get("readiness_score", 0)
    
    return f"""
    <g transform="translate({x}, {y})">
      <rect width="260" height="90" rx="{border_radius}" fill="{panel_bg}" stroke="{accent_sleep}" stroke-width="1" stroke-opacity="0.3"/>
      <text x="10" y="20" font-family="{font_family}" font-size="12" fill="{accent_sleep}" font-weight="600">
        💫 Oura Mood
      </text>
      <text x="10" y="40" font-family="{font_family}" font-size="10" fill="{text_primary}" font-weight="500">
        {mood_icon} {escape_xml(mood_name)}
      </text>
      <text x="10" y="55" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Sleep: <tspan fill="{text_primary}">{safe_value(sleep_score)}</tspan> | Readiness: <tspan fill="{text_primary}">{safe_value(readiness_score)}</tspan>
      </text>
      <text x="10" y="70" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Mood Score: <tspan fill="{text_primary}">{mood_score:.1f}</tspan>
      </text>
    </g>"""


def generate_themed_dashboard(theme_name: str = "dark") -> str:
    """Generate the consolidated dashboard SVG with specified theme."""
    
    # Load theme first to initialize theme context
    theme = load_theme(theme_name=theme_name)
    
    # Load all data sources
    developer_stats = load_developer_stats()
    soundcloud_data = load_soundcloud_data()
    weather_data = load_weather_data()
    location_data = load_location_data()
    oura_mood_data = load_oura_mood_data()
    
    # Load theme values (these will now use the selected theme)
    font_family = get_theme_typography("font_family")
    bg_gradient = get_theme_gradient("background.dark")
    text_primary = get_theme_color("text", "primary")
    text_muted = get_theme_color("text", "muted")
    accent_teal = get_theme_color("text", "accent")
    border_radius = get_theme_border_radius("xl")
    
    # Card dimensions
    card_width = 800
    card_height = 350
    
    # Effect settings
    stroke_width = theme.get("cards", {}).get("stroke_width", 1)
    stroke_opacity = theme.get("cards", {}).get("stroke_opacity", 0.3)
    
    # Generate sections in a 2x3 grid layout
    developer_section = generate_developer_section(developer_stats, 20, 50, theme_name)
    soundcloud_section = generate_soundcloud_section(soundcloud_data, 300, 50, theme_name)
    weather_section = generate_weather_section(weather_data, 20, 160, theme_name)
    location_section = generate_location_section(location_data, 300, 160, theme_name)
    oura_mood_section = generate_oura_mood_section(oura_mood_data, 20, 270, theme_name)
    
    # Add theme indicator
    theme_indicator = f"""
    <g transform="translate(300, 270)">
      <rect width="260" height="90" rx="6" fill="{get_theme_color('background', 'panel')}" stroke="{accent_teal}" stroke-width="1" stroke-opacity="0.2" stroke-dasharray="4,4"/>
      <text x="130" y="35" font-family="{font_family}" font-size="10" fill="{text_muted}" text-anchor="middle">
        Theme: {theme_name.capitalize()}
      </text>
      <text x="130" y="55" font-family="{font_family}" font-size="9" fill="{text_muted}" text-anchor="middle">
        Switch with --theme flag
      </text>
    </g>"""
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}">
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_gradient[0]}"/>
      <stop offset="100%" style="stop-color:{bg_gradient[1]}"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="url(#bg-gradient)"/>
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="none" stroke="{accent_teal}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}"/>

  <!-- Header -->
  <g transform="translate(20, 25)">
    <text font-family="{font_family}" font-size="16" fill="{accent_teal}" font-weight="600">
      📊 Consolidated Dashboard ({theme_name.capitalize()} Theme)
    </text>
  </g>

  <!-- Sections -->
  {developer_section}
  {soundcloud_section}
  {weather_section}
  {location_section}
  {oura_mood_section}
  {theme_indicator}

  <!-- Footer -->
  <g transform="translate(20, {card_height - 10})">
    <text font-family="{font_family}" font-size="9" fill="{text_muted}">
      Updated: {escape_xml(format_timestamp_local(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))}
    </text>
  </g>

  <!-- Decorative accent -->
  <rect x="{card_width - 16}" y="15" width="4" height="{card_height - 30}" rx="2" fill="{accent_teal}" fill-opacity="{stroke_opacity}"/>
</svg>"""
    
    return svg


def main() -> None:
    """Main entry point for themed dashboard generation."""
    import traceback
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate consolidated dashboard with theme support")
    parser.add_argument("output", nargs="?", default="dashboard.svg", help="Output file path")
    parser.add_argument("--theme", choices=["dark", "light"], default="dark", help="Theme to use")
    
    args = parser.parse_args()
    
    try:
        # Generate the SVG
        svg_content = generate_themed_dashboard(args.theme)
        
        # Write to file
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(svg_content, encoding="utf-8")
        
        print(f"Generated {args.theme} themed dashboard: {args.output}", file=sys.stderr)
    except Exception as e:
        print(f"Error generating themed dashboard: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
