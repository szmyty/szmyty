#!/usr/bin/env python3
"""
Generate weekly or monthly summary cards from historical snapshots.

This script creates SVG cards showing aggregated metrics over time periods.

Usage:
    python generate-summary-card.py --period weekly [output_path]
    python generate-summary-card.py --period monthly [output_path]
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional

from lib.utils import (
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


def load_latest_snapshot(period: str, snapshots_dir: str = "data/snapshots") -> Optional[Dict]:
    """Load the latest weekly or monthly snapshot."""
    now = datetime.now(timezone.utc)
    snapshots_path = Path(snapshots_dir)
    
    if period == "weekly":
        year, week, _ = now.isocalendar()
        snapshot_file = snapshots_path / "weekly" / f"{year}-W{week:02d}.json"
    elif period == "monthly":
        snapshot_file = snapshots_path / "monthly" / f"{now.strftime('%Y-%m')}.json"
    else:
        return None
    
    if snapshot_file.exists():
        data, error = try_load_json(str(snapshot_file))
        return data
    
    return None


def generate_metric_row_summary(label: str, value: str, x: int, y: int) -> str:
    """
    Generate a metric row for the summary card.
    
    Uses theme colors from the global theme context.
    """
    font_family = get_theme_typography("font_family")
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    
    return f"""
    <g transform="translate({x}, {y})">
      <text font-family="{font_family}" font-size="11" fill="{text_secondary}" font-weight="500">
        {escape_xml(label)}
      </text>
      <text x="220" font-family="{font_family}" font-size="12" fill="{text_primary}" font-weight="600" text-anchor="end">
        {escape_xml(value)}
      </text>
    </g>"""


def generate_summary_svg(snapshot: Dict, period: str) -> str:
    """Generate SVG for weekly or monthly summary card."""
    
    # Load theme values
    theme = load_theme()
    font_family = get_theme_typography("font_family")
    bg_gradient = get_theme_gradient("background.default")
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    text_muted = get_theme_color("text", "muted")
    accent_teal = get_theme_color("text", "accent")
    accent_sleep = get_theme_color("accent", "sleep")
    accent_readiness = get_theme_color("accent", "readiness")
    accent_activity = get_theme_color("accent", "activity")
    accent_developer = get_theme_color("accent", "developer")
    panel_bg = get_theme_color("background", "panel")
    border_radius = get_theme_border_radius("xl")
    border_radius_md = get_theme_border_radius("md")
    
    # Card dimensions
    card_width = 480
    card_height = 400
    
    # Effect settings
    stroke_width = theme.get("cards", {}).get("stroke_width", 1)
    stroke_opacity = theme.get("cards", {}).get("stroke_opacity", 0.3)
    
    # Extract data
    health = snapshot.get("health", {})
    developer = snapshot.get("developer", {})
    start_date = snapshot.get("start_date", "")
    end_date = snapshot.get("end_date", "")
    days_count = snapshot.get("days_count", 0)
    
    # Format period title
    period_title = f"{period.capitalize()} Summary"
    period_subtitle = f"{start_date} to {end_date} ({days_count} days)"
    
    # Health metrics
    avg_sleep = health.get("avg_sleep_score")
    avg_readiness = health.get("avg_readiness_score")
    avg_activity = health.get("avg_activity_score")
    total_steps = health.get("total_steps")
    avg_steps = health.get("avg_steps")
    
    # Developer metrics
    avg_commits = developer.get("avg_commits")
    
    # Generate metric rows
    y_start = 120
    y_step = 30
    metrics = [
        ("💤 Avg Sleep Score", safe_value(avg_sleep), accent_sleep),
        ("💪 Avg Readiness Score", safe_value(avg_readiness), accent_readiness),
        ("🏃 Avg Activity Score", safe_value(avg_activity), accent_activity),
        ("👣 Total Steps", format_large_number(total_steps) if total_steps else "—", accent_activity),
        ("📊 Avg Steps/Day", format_large_number(avg_steps) if avg_steps else "—", accent_activity),
        ("💻 Avg Commits", safe_value(avg_commits), accent_developer),
    ]
    
    metric_rows = []
    for i, (label, value, color) in enumerate(metrics):
        y = y_start + (i * y_step)
        metric_rows.append(f"""
    <g transform="translate(30, {y})">
      <rect width="4" height="20" rx="2" fill="{color}"/>
      <text x="15" font-family="{font_family}" font-size="11" fill="{text_secondary}" font-weight="500" dominant-baseline="middle" y="10">
        {escape_xml(label)}
      </text>
      <text x="430" font-family="{font_family}" font-size="12" fill="{text_primary}" font-weight="600" text-anchor="end" dominant-baseline="middle" y="10">
        {escape_xml(value)}
      </text>
    </g>""")
    
    # Additional stats for monthly
    extra_stats = ""
    if period == "monthly":
        max_sleep = health.get("max_sleep_score")
        min_sleep = health.get("min_sleep_score")
        if max_sleep is not None and min_sleep is not None:
            extra_stats = f"""
    <g transform="translate(30, 310)">
      <rect width="420" height="60" rx="{border_radius_md}" fill="{panel_bg}" stroke="{accent_sleep}" stroke-width="1" stroke-opacity="0.2"/>
      <text x="10" y="20" font-family="{font_family}" font-size="11" fill="{accent_sleep}" font-weight="600">
        📈 Sleep Score Range
      </text>
      <text x="10" y="40" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        Best: <tspan fill="{text_primary}">{max_sleep}</tspan>  •  Worst: <tspan fill="{text_primary}">{min_sleep}</tspan>  •  Range: <tspan fill="{text_primary}">{max_sleep - min_sleep}</tspan>
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
  <g transform="translate(30, 30)">
    <text font-family="{font_family}" font-size="18" fill="{accent_teal}" font-weight="600">
      📊 {escape_xml(period_title)}
    </text>
  </g>
  
  <!-- Period Subtitle -->
  <g transform="translate(30, 55)">
    <text font-family="{font_family}" font-size="10" fill="{text_secondary}">
      {escape_xml(period_subtitle)}
    </text>
  </g>
  
  <!-- Divider -->
  <line x1="30" y1="75" x2="450" y2="75" stroke="{accent_teal}" stroke-width="1" stroke-opacity="0.3"/>

  <!-- Metrics -->
  {"".join(metric_rows)}
  
  <!-- Extra Stats (Monthly only) -->
  {extra_stats}

  <!-- Footer -->
  <g transform="translate(30, {card_height - 15})">
    <text font-family="{font_family}" font-size="9" fill="{text_muted}">
      Generated: {escape_xml(format_timestamp_local(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))}
    </text>
  </g>

  <!-- Decorative accent -->
  <rect x="{card_width - 20}" y="20" width="4" height="{card_height - 40}" rx="2" fill="{accent_teal}" fill-opacity="{stroke_opacity}"/>
</svg>"""
    
    return svg


def main() -> None:
    """Main entry point for summary card generation."""
    import argparse
    import traceback
    
    parser = argparse.ArgumentParser(description="Generate weekly or monthly summary cards")
    parser.add_argument("output", nargs="?", help="Output file path")
    parser.add_argument("--period", choices=["weekly", "monthly"], required=True, help="Summary period")
    parser.add_argument("--snapshots-dir", default="data/snapshots", help="Snapshots directory")
    
    args = parser.parse_args()
    
    # Default output path based on period
    if not args.output:
        args.output = f"summary-{args.period}.svg"
    
    try:
        # Load latest snapshot for the period
        snapshot = load_latest_snapshot(args.period, args.snapshots_dir)
        
        if not snapshot:
            print(f"No {args.period} snapshot found. Please run store-historical-snapshot.py first.", file=sys.stderr)
            sys.exit(1)
        
        # Generate SVG
        svg_content = generate_summary_svg(snapshot, args.period)
        
        # Write to file
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(svg_content, encoding="utf-8")
        
        print(f"Generated {args.period} summary card: {args.output}", file=sys.stderr)
    except Exception as e:
        print(f"Error generating summary card: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
