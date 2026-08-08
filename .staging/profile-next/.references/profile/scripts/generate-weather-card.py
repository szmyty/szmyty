#!/usr/bin/env python3
"""
Generate a styled SVG card for daily weather conditions and forecast.
This script reads weather metadata from JSON and creates an SVG card.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from lib.utils import (
    escape_xml,
    load_and_validate_json,
    load_theme,
    get_theme_color,
    get_theme_gradient,
    get_theme_typography,
    get_theme_font_size,
    get_theme_card_dimension,
    get_theme_border_radius,
    format_timestamp_local,
    format_time_since,
    is_data_stale,
    generate_card_with_fallback,
)
from lib.weather_alerts import get_weather_alert, format_alert_badge


def format_time(time_str: str) -> str:
    """Format ISO time string to readable format (HH:MM AM/PM)."""
    try:
        dt = datetime.fromisoformat(time_str)
        # Use %I for 12-hour format and strip leading zero manually for cross-platform compatibility
        formatted = dt.strftime("%I:%M %p")
        # Remove leading zero from hour if present
        if formatted.startswith("0"):
            formatted = formatted[1:]
        return formatted
    except (ValueError, AttributeError):
        return time_str


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


def kmh_to_mph(kmh: float) -> float:
    """Convert km/h to mph."""
    return kmh * 0.621371


def get_background_gradient(is_day: int, weathercode: int) -> tuple[str, str]:
    """
    Get background gradient colors based on time of day and weather.
    
    Args:
        is_day: 1 if daytime, 0 if nighttime.
        weathercode: WMO weather code (0-99).
    
    Returns:
        Tuple of (start_color, end_color) for background gradient.
    """
    # Load weather gradients from theme
    theme = load_theme()
    weather_gradients = theme.get("gradients", {}).get("weather", {})
    
    if is_day:
        if weathercode in [0, 1]:  # Clear/Mainly clear
            gradient = weather_gradients.get("clear_day", ["#1e3a5f", "#2d5a7b"])
        elif weathercode in [2, 3]:  # Cloudy
            gradient = weather_gradients.get("cloudy", ["#3d4f5f", "#4a5d6e"])
        elif weathercode in [45, 48]:  # Fog
            gradient = weather_gradients.get("fog", ["#4a5568", "#5a6578"])
        elif weathercode in range(51, 68) or weathercode in range(80, 83):  # Rain
            gradient = weather_gradients.get("rain", ["#2d3748", "#3d4758"])
        elif weathercode in range(71, 78) or weathercode in range(85, 87):  # Snow
            gradient = weather_gradients.get("snow", ["#4a5568", "#6b7280"])
        elif weathercode in range(95, 100):  # Thunderstorm
            gradient = weather_gradients.get("storm", ["#1a202c", "#2d3748"])
        else:
            bg_default = get_theme_gradient("background.default")
            gradient = bg_default
    else:
        gradient = weather_gradients.get("night", ["#0f0f23", "#1a1a2e"])
    
    return (gradient[0], gradient[1])


def generate_svg(
    location: str,
    condition: str,
    emoji: str,
    current_temp: float,
    temp_max: float,
    temp_min: float,
    wind_speed: float,
    sunrise: str,
    sunset: str,
    updated_at: str,
    is_day: int,
    weathercode: int,
) -> str:
    """Generate SVG card markup."""
    
    # Load theme values
    theme = load_theme()
    font_family = get_theme_typography("font_family")
    
    # Colors from theme
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    text_muted = get_theme_color("text", "muted")
    accent_teal = get_theme_color("text", "accent")
    accent_cyan = get_theme_color("accent", "cyan")
    accent_hr = get_theme_color("accent", "heart_rate")
    
    # Card dimensions from theme
    card_width = get_theme_card_dimension("widths", "weather")
    card_height = get_theme_card_dimension("heights", "weather")
    border_radius = get_theme_border_radius("xl")
    
    # Font sizes from theme
    font_size_base = get_theme_font_size("base")
    font_size_lg = get_theme_font_size("lg")
    font_size_lg_plus = get_theme_font_size("lg-plus")
    font_size_xl = get_theme_font_size("xl")
    font_size_2xl = get_theme_font_size("2xl")
    font_size_7xl = get_theme_font_size("7xl")
    
    # Card stroke settings from theme
    stroke_width = theme.get("cards", {}).get("stroke_width", 1)
    stroke_opacity = theme.get("cards", {}).get("stroke_opacity", 0.3)
    
    # Effect settings from theme
    glow = theme.get("effects", {}).get("glow", {})
    glow_std = glow.get("stdDeviation", 2)

    # Convert units (API returns Celsius and km/h by default)
    current_temp_f = celsius_to_fahrenheit(current_temp)
    temp_max_f = celsius_to_fahrenheit(temp_max)
    temp_min_f = celsius_to_fahrenheit(temp_min)
    wind_mph = kmh_to_mph(wind_speed)

    # Format times
    sunrise_formatted = format_time(sunrise)
    sunset_formatted = format_time(sunset)

    # Escape text for XML
    location_escaped = escape_xml(location)
    condition_escaped = escape_xml(condition)
    emoji_escaped = escape_xml(emoji)

    # Truncate location if too long
    display_location = (
        location_escaped[:30] + "..." if len(location_escaped) > 30 else location_escaped
    )

    # Get background colors
    bg_start, bg_end = get_background_gradient(is_day, weathercode)
    
    # Calculate staleness badge
    font_size_xs = get_theme_font_size("xs")
    staleness_badge = ""
    if updated_at:
        time_since = format_time_since(updated_at)
        is_stale = is_data_stale(updated_at, stale_threshold_hours=24)
        
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
    
    # Check for weather alerts
    weather_alert = get_weather_alert(weathercode, current_temp, wind_speed, is_day)
    alert_badge = ""
    if weather_alert:
        alert_type, alert_message, alert_emoji = weather_alert
        alert_color = accent_hr if alert_type in ["heat", "severe_thunderstorm", "blizzard"] else accent_cyan
        alert_badge = format_alert_badge(
            alert_type, alert_message, alert_emoji,
            20, 200, font_family, alert_color
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}">
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_start}"/>
      <stop offset="100%" style="stop-color:{bg_end}"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="{glow_std}" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="url(#bg-gradient)"/>
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="none" stroke="{accent_teal}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}"/>

  <!-- Header: Location + Weather Icon -->
  <g transform="translate(20, 30)">
    <text font-family="{font_family}" font-size="{font_size_xl}" fill="{accent_teal}" font-weight="600">
      {emoji_escaped} {display_location}
    </text>
  </g>

  <!-- Current Condition -->
  <g transform="translate(20, 60)">
    <text font-family="{font_family}" font-size="{font_size_7xl}" fill="{text_primary}" font-weight="bold" filter="url(#glow)">
      {current_temp_f:.0f}°F
    </text>
    <text x="110" y="0" font-family="{font_family}" font-size="{font_size_2xl}" fill="{text_secondary}">
      {condition_escaped}
    </text>
  </g>

  <!-- High/Low -->
  <g transform="translate(20, 95)">
    <text font-family="{font_family}" font-size="{font_size_lg_plus}" fill="{text_secondary}">
      <tspan fill="{accent_hr}">High: {temp_max_f:.0f}°F</tspan>
      <tspan fill="{text_muted}">  •  </tspan>
      <tspan fill="{accent_cyan}">Low: {temp_min_f:.0f}°F</tspan>
    </text>
  </g>

  <!-- Wind -->
  <g transform="translate(20, 120)">
    <text font-family="{font_family}" font-size="{font_size_lg}" fill="{text_secondary}">
      💨 Wind: {wind_mph:.0f} mph
    </text>
  </g>

  <!-- Sunrise/Sunset -->
  <g transform="translate(20, 145)">
    <text font-family="{font_family}" font-size="{font_size_lg}" fill="{text_secondary}">
      🌅 {sunrise_formatted}
      <tspan fill="{text_muted}">  •  </tspan>
      🌇 {sunset_formatted}
    </text>
  </g>

  <!-- Weather Alert Badge -->
  {alert_badge}

  {staleness_badge}

  <!-- Decorative accent -->
  <rect x="{card_width - 20}" y="15" width="4" height="170" rx="2" fill="{accent_teal}" fill-opacity="{stroke_opacity}"/>
</svg>"""

    return svg


def generate_weather_svg(metadata: dict) -> str:
    """Generate weather SVG from metadata dictionary."""
    # Pass raw updated_at timestamp for staleness calculation
    updated_at_raw = metadata.get("updated_at", "")

    return generate_svg(
        location=metadata.get("location", "Unknown Location"),
        condition=metadata.get("current", {}).get("condition", "Unknown"),
        emoji=metadata.get("current", {}).get("emoji", "🌡️"),
        current_temp=metadata.get("current", {}).get("temperature", 0),
        temp_max=metadata.get("daily", {}).get("temperature_max", 0),
        temp_min=metadata.get("daily", {}).get("temperature_min", 0),
        wind_speed=metadata.get("current", {}).get("wind_speed", 0),
        sunrise=metadata.get("daily", {}).get("sunrise", ""),
        sunset=metadata.get("daily", {}).get("sunset", ""),
        updated_at=updated_at_raw,
        is_day=metadata.get("current", {}).get("is_day", 1),
        weathercode=metadata.get("current", {}).get("weathercode", 0),
    )


def main() -> None:
    """
    Main entry point for weather card generation.
    
    Reads weather data from JSON file and generates an SVG card.
    Uses fallback mechanism to preserve existing card on errors.
    """
    if len(sys.argv) < 2:
        print(
            "Usage: generate-weather-card.py <weather.json> [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    metadata_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "weather/weather-today.svg"

    # Use fallback mechanism to generate the card
    success = generate_card_with_fallback(
        card_type="weather",
        output_path=output_path,
        json_path=metadata_path,
        schema_name="weather",
        generator_func=generate_weather_svg,
        description="Weather metadata file",
    )

    if success:
        print(f"Generated weather SVG card: {output_path}", file=sys.stderr)
    else:
        print(f"Using fallback weather SVG card: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
