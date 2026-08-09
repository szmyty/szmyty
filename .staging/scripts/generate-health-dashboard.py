#!/usr/bin/env python3
"""
Generate a holistic health dashboard SVG from Oura Ring metrics.
This script reads the health snapshot JSON and creates a comprehensive SVG dashboard
with personal stats, sleep, readiness, activity panels, and optional HR trend chart.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List

from lib.utils import (
    escape_xml,
    safe_value,
    load_and_validate_json,
    generate_sparkline_path,
    load_theme,
    get_theme_color,
    get_theme_gradient,
    get_theme_typography,
    get_theme_font_size,
    get_theme_card_dimension,
    get_theme_border_radius,
    get_theme_score_ring_value,
    get_theme_chart_color,
    format_timestamp_local,
    format_time_since,
    is_data_stale,
    generate_card_with_fallback,
)


def format_temp(value: Optional[float]) -> str:
    """Format temperature deviation value."""
    if value is None:
        return "—"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}°C"


def generate_score_ring(value: Optional[int], cx: int, cy: int, radius: int, color: str, label: str) -> str:
    """Generate a circular score indicator."""
    # Load theme values
    font_family = get_theme_typography("font_family")
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    font_size_xs = get_theme_font_size("xs")
    font_size_xl = get_theme_font_size("xl")
    stroke_width = get_theme_score_ring_value("stroke_width", 4)
    label_offset = get_theme_score_ring_value("label_offset", 14)
    ring_background = get_theme_chart_color("bar_background")
    
    score = value if value is not None else 0
    score = min(100, max(0, score))
    circumference = 2 * 3.14159 * radius
    dash_offset = circumference * (1 - score / 100)
    
    return f"""
    <g transform="translate({cx}, {cy})">
      <circle r="{radius}" fill="none" stroke="{ring_background}" stroke-width="{stroke_width}"/>
      <circle r="{radius}" fill="none" stroke="{color}" stroke-width="{stroke_width}"
              stroke-dasharray="{circumference}" stroke-dashoffset="{dash_offset}"
              stroke-linecap="round" transform="rotate(-90)"/>
      <text y="5" font-family="{font_family}" font-size="{font_size_xl}" fill="{text_primary}" 
            font-weight="bold" text-anchor="middle">{score}</text>
      <text y="{radius + label_offset}" font-family="{font_family}" font-size="{font_size_xs}" 
            fill="{text_secondary}" text-anchor="middle">{escape_xml(label)}</text>
    </g>"""


def generate_metric_row(label: str, value: str, x: int, y: int, icon: str = "") -> str:
    """Generate a single metric row."""
    # Load theme values
    font_family = get_theme_typography("font_family")
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    font_size_sm = get_theme_font_size("sm")
    font_size_base = get_theme_font_size("base")
    
    return f"""
    <g transform="translate({x}, {y})">
      <text font-family="{font_family}" font-size="{font_size_sm}" fill="{text_secondary}">
        {icon} {escape_xml(label)}
      </text>
      <text x="100" font-family="{font_family}" font-size="{font_size_base}" fill="{text_primary}" 
            text-anchor="end" font-weight="500">{escape_xml(value)}</text>
    </g>"""


def generate_svg(snapshot: dict) -> str:
    """Generate the holistic health dashboard SVG."""
    
    # Load theme values
    theme = load_theme()
    bg_gradient = get_theme_gradient("background.dark")
    sleep_gradient = get_theme_gradient("sleep")
    readiness_gradient = get_theme_gradient("readiness")
    activity_gradient = get_theme_gradient("activity")
    hr_gradient = get_theme_gradient("heart_rate")
    font_family = get_theme_typography("font_family")
    
    # Colors from theme
    bg_dark = bg_gradient[0]
    bg_primary = bg_gradient[1]
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    text_muted = get_theme_color("text", "muted")
    accent_teal = get_theme_color("text", "accent")
    accent_sleep = get_theme_color("accent", "sleep")
    accent_readiness = get_theme_color("accent", "readiness")
    accent_activity = get_theme_color("accent", "activity")
    accent_hr = get_theme_color("accent", "heart_rate")
    panel_bg = get_theme_color("background", "panel")
    panel_sleep = get_theme_color("background", "panel_sleep")
    panel_readiness = get_theme_color("background", "panel_readiness")
    panel_activity = get_theme_color("background", "panel_activity")
    
    # Card dimensions from theme
    card_width = get_theme_card_dimension("widths", "health_dashboard")
    card_height = get_theme_card_dimension("heights", "health_dashboard")
    border_radius = get_theme_border_radius("xl")
    border_radius_md = get_theme_border_radius("md")
    border_radius_sm = get_theme_border_radius("sm")
    
    # Font sizes from theme
    font_size_xs = get_theme_font_size("xs")
    font_size_base = get_theme_font_size("base")
    font_size_lg = get_theme_font_size("lg")
    font_size_xl = get_theme_font_size("xl")
    
    # Card stroke settings from theme
    stroke_width = theme.get("cards", {}).get("stroke_width", 1)
    stroke_opacity = theme.get("cards", {}).get("stroke_opacity", 0.3)
    
    # Effect settings from theme
    glow = theme.get("effects", {}).get("glow", {})
    glow_std = glow.get("stdDeviation", 2)
    
    # Extract data sections
    personal = snapshot.get("personal", {})
    sleep = snapshot.get("sleep", {})
    readiness = snapshot.get("readiness", {})
    activity = snapshot.get("activity", {})
    heart_rate = snapshot.get("heart_rate", {})
    updated_at_raw = snapshot.get("updated_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    
    # Personal stats
    age = personal.get("age")
    height_cm = personal.get("height_cm")
    weight_kg = personal.get("weight_kg")
    weight_lbs = personal.get("weight_lbs")
    bmi = personal.get("bmi")
    sex = personal.get("sex")
    
    # Scores
    sleep_score = sleep.get("score")
    readiness_score = readiness.get("score")
    activity_score = activity.get("score")
    
    # Sleep metrics
    deep_sleep = sleep.get("deep_sleep")
    rem_sleep = sleep.get("rem_sleep")
    total_sleep = sleep.get("total_sleep")
    efficiency = sleep.get("efficiency")
    
    # Readiness metrics
    recovery_index = readiness.get("recovery_index")
    hrv_balance = readiness.get("hrv_balance")
    temp_deviation = readiness.get("temperature_deviation")
    
    # Activity metrics
    steps = activity.get("steps")
    total_calories = activity.get("total_calories")
    active_calories = activity.get("active_calories")
    inactivity_alerts = activity.get("inactivity_alerts")
    avg_met = activity.get("average_met_minutes")
    
    # Heart rate - use heart_rate.resting_bpm as primary, fallback to readiness
    latest_bpm = heart_rate.get("latest_bpm")
    hr_trend = heart_rate.get("trend_values", [])
    resting_hr = heart_rate.get("resting_bpm") or readiness.get("resting_heart_rate")
    
    # Generate sparkline for HR trend
    sparkline_path = generate_sparkline_path(hr_trend, 90, 22)
    
    # Generate score rings with theme colors
    sleep_ring = generate_score_ring(sleep_score, 55, 45, 30, accent_sleep, "Sleep")
    readiness_ring = generate_score_ring(readiness_score, 135, 45, 30, accent_readiness, "Ready")
    activity_ring = generate_score_ring(activity_score, 215, 45, 30, accent_activity, "Active")
    
    # Format weight display
    weight_display = "—"
    if weight_kg is not None:
        weight_display = f"{weight_kg}kg"
        if weight_lbs is not None:
            weight_display += f" ({weight_lbs}lb)"
    
    # Format height display
    height_display = safe_value(height_cm, suffix="cm") if height_cm else "—"
    
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
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_dark}"/>
      <stop offset="100%" style="stop-color:{bg_primary}"/>
    </linearGradient>
    <linearGradient id="sleep-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{sleep_gradient[0]}"/>
      <stop offset="100%" style="stop-color:{sleep_gradient[1]}"/>
    </linearGradient>
    <linearGradient id="readiness-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{readiness_gradient[0]}"/>
      <stop offset="100%" style="stop-color:{readiness_gradient[1]}"/>
    </linearGradient>
    <linearGradient id="activity-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{activity_gradient[0]}"/>
      <stop offset="100%" style="stop-color:{activity_gradient[1]}"/>
    </linearGradient>
    <linearGradient id="hr-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{hr_gradient[0]}"/>
      <stop offset="100%" style="stop-color:{hr_gradient[1]}"/>
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

  <!-- Header -->
  <g transform="translate(20, 20)">
    <text font-family="{font_family}" font-size="{font_size_xl}" fill="{accent_teal}" font-weight="600">
      🧬 OURA HEALTH DASHBOARD
    </text>
  </g>

  <!-- Score Rings Row -->
  <g transform="translate(20, 45)">
    {sleep_ring}
    {readiness_ring}
    {activity_ring}
  </g>

  <!-- Personal Stats Panel (grey/white) -->
  <g transform="translate(280, 45)">
    <rect width="200" height="75" rx="{border_radius_md}" fill="{panel_bg}" stroke="{text_muted}" stroke-width="{stroke_width}"/>
    <text x="10" y="18" font-family="{font_family}" font-size="{font_size_base}" fill="{accent_teal}" font-weight="600">
      👤 Personal Stats
    </text>
    {generate_metric_row("Age", safe_value(age, suffix=" yrs") if age else "—", 10, 35)}
    {generate_metric_row("Height", height_display, 10, 50)}
    {generate_metric_row("Weight", weight_display, 10, 65)}
    <text x="180" y="65" font-family="{font_family}" font-size="{font_size_xs}" fill="{text_secondary}">
      BMI: {safe_value(bmi)}
    </text>
  </g>

  <!-- Sleep Panel (blue/purple) -->
  <g transform="translate(20, 130)">
    <rect width="145" height="105" rx="{border_radius_md}" fill="{panel_sleep}" stroke="{sleep_gradient[0]}" stroke-width="{stroke_width}" stroke-opacity="0.5"/>
    <text x="10" y="18" font-family="{font_family}" font-size="{font_size_base}" fill="{accent_sleep}" font-weight="600">
      😴 Sleep
    </text>
    {generate_metric_row("Deep Sleep", safe_value(deep_sleep), 10, 35)}
    {generate_metric_row("REM Sleep", safe_value(rem_sleep), 10, 50)}
    {generate_metric_row("Total Sleep", safe_value(total_sleep), 10, 65)}
    {generate_metric_row("Efficiency", safe_value(efficiency, suffix="%") if efficiency else "—", 10, 80)}
    {generate_metric_row("Timing", safe_value(sleep.get("timing")), 10, 95)}
  </g>

  <!-- Readiness Panel (teal/green) -->
  <g transform="translate(175, 130)">
    <rect width="145" height="105" rx="{border_radius_md}" fill="{panel_readiness}" stroke="{accent_readiness}" stroke-width="{stroke_width}" stroke-opacity="0.5"/>
    <text x="10" y="18" font-family="{font_family}" font-size="{font_size_base}" fill="{accent_readiness}" font-weight="600">
      💪 Readiness
    </text>
    {generate_metric_row("Recovery", safe_value(recovery_index), 10, 35)}
    {generate_metric_row("HRV Balance", safe_value(hrv_balance), 10, 50)}
    {generate_metric_row("Resting HR", safe_value(resting_hr), 10, 65)}
    {generate_metric_row("Temp Dev", format_temp(temp_deviation), 10, 80)}
    {generate_metric_row("Sleep Bal", safe_value(readiness.get("sleep_balance")), 10, 95)}
  </g>

  <!-- Activity Panel (orange/yellow) -->
  <g transform="translate(330, 130)">
    <rect width="150" height="105" rx="{border_radius_md}" fill="{panel_activity}" stroke="{accent_activity}" stroke-width="{stroke_width}" stroke-opacity="0.5"/>
    <text x="10" y="18" font-family="{font_family}" font-size="{font_size_base}" fill="{accent_activity}" font-weight="600">
      🏃 Activity
    </text>
    {generate_metric_row("Steps", safe_value(steps, default="0"), 10, 35)}
    {generate_metric_row("Total Cal", safe_value(total_calories, suffix=" kcal") if total_calories else "—", 10, 50)}
    {generate_metric_row("Active Cal", safe_value(active_calories, suffix=" kcal") if active_calories else "—", 10, 65)}
    {generate_metric_row("Inact Alerts", safe_value(inactivity_alerts, default="0"), 10, 80)}
    {generate_metric_row("Avg MET", f"{avg_met:.2f}" if avg_met is not None else "—", 10, 95)}
  </g>

  <!-- Heart Rate Mini Chart -->
  <g transform="translate(20, 245)">
    <rect width="225" height="70" rx="{border_radius_md}" fill="{panel_bg}" stroke="{accent_hr}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}"/>
    <text x="10" y="18" font-family="{font_family}" font-size="{font_size_base}" fill="{accent_hr}" font-weight="600">
      ❤️ Heart Rate Trend
    </text>
    <text x="200" y="18" font-family="{font_family}" font-size="{font_size_lg}" fill="{text_primary}" font-weight="bold" text-anchor="end">
      {safe_value(latest_bpm, suffix=" bpm") if latest_bpm else "— bpm"}
    </text>
    <g transform="translate(10, 38)">
      <rect width="100" height="25" rx="{border_radius_sm}" fill="{bg_dark}"/>
      <g transform="translate(5, 1)">
        <path d="{sparkline_path}" fill="none" stroke="url(#hr-gradient)" stroke-width="1.5" stroke-linecap="round"/>
      </g>
    </g>
    <g transform="translate(120, 35)">
      <text font-family="{font_family}" font-size="{font_size_xs}" fill="{text_secondary}">
        Latest: {safe_value(latest_bpm, default="—")} bpm
      </text>
      <text y="14" font-family="{font_family}" font-size="{font_size_xs}" fill="{text_secondary}">
        Resting: {safe_value(resting_hr, default="—")}
      </text>
      <text y="28" font-family="{font_family}" font-size="{font_size_xs}" fill="{text_secondary}">
        HRV: {safe_value(hrv_balance, default="—")}
      </text>
    </g>
  </g>

  <!-- Additional Metrics Panel -->
  <g transform="translate(255, 245)">
    <rect width="225" height="70" rx="{border_radius_md}" fill="{panel_bg}" stroke="{accent_teal}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}"/>
    <text x="10" y="18" font-family="{font_family}" font-size="{font_size_base}" fill="{accent_teal}" font-weight="600">
      📊 Contributors
    </text>
    <g transform="translate(10, 32)">
      <text font-family="{font_family}" font-size="{font_size_xs}" fill="{text_secondary}">
        Training Freq: {safe_value(activity.get("training_frequency"))}
      </text>
      <text y="12" font-family="{font_family}" font-size="{font_size_xs}" fill="{text_secondary}">
        Recovery Time: {safe_value(activity.get("recovery_time"))}
      </text>
      <text y="24" font-family="{font_family}" font-size="{font_size_xs}" fill="{text_secondary}">
        Previous Night: {safe_value(readiness.get("previous_night"))}
      </text>
    </g>
    <g transform="translate(120, 32)">
      <text font-family="{font_family}" font-size="{font_size_xs}" fill="{text_secondary}">
        Move/Hour: {safe_value(activity.get("move_every_hour"))}
      </text>
      <text y="12" font-family="{font_family}" font-size="{font_size_xs}" fill="{text_secondary}">
        Stay Active: {safe_value(activity.get("stay_active"))}
      </text>
      <text y="24" font-family="{font_family}" font-size="{font_size_xs}" fill="{text_secondary}">
        Activity Bal: {safe_value(readiness.get("activity_balance"))}
      </text>
    </g>
  </g>

  {staleness_badge}

  <!-- Sex indicator if available -->
  <g transform="translate(465, 340)">
    <text font-family="{font_family}" font-size="{font_size_xs}" fill="{text_muted}" text-anchor="end">
      {escape_xml(sex) if sex else ""}
    </text>
  </g>

  <!-- Decorative accent -->
  <rect x="{card_width - 16}" y="15" width="4" height="350" rx="2" fill="{accent_teal}" fill-opacity="{stroke_opacity}"/>
</svg>"""

    return svg


def main() -> None:
    """
    Main entry point for health dashboard generation.
    
    Reads health snapshot data and generates a holistic SVG dashboard
    with personal stats, sleep, readiness, and activity metrics.
    Uses fallback mechanism to preserve existing card on errors.
    """
    if len(sys.argv) < 2:
        print(
            "Usage: generate-health-dashboard.py <health_snapshot.json> [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    snapshot_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "oura/health_dashboard.svg"

    # Use fallback mechanism to generate the card
    success = generate_card_with_fallback(
        card_type="health_dashboard",
        output_path=output_path,
        json_path=snapshot_path,
        schema_name="health-snapshot",
        generator_func=generate_svg,
        description="Health snapshot file",
    )

    if success:
        print(f"Generated Oura health dashboard SVG: {output_path}", file=sys.stderr)
    else:
        print(f"Using fallback health dashboard SVG: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
