#!/usr/bin/env python3
"""
Generate a Developer Stats Dashboard SVG card from GitHub statistics.

This script creates a comprehensive SVG visualization including:
- Summary metrics row (repos, stars, PRs, issues, followers)
- Mini activity sparkline (commits over last 30 days)
- Developer rhythm heatmap (7×24 grid)
- Top repositories bar chart
- Languages distribution chart

Usage:
    python generate-developer-dashboard.py <stats.json> [output_path]
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

from lib.utils import (
    escape_xml,
    safe_value,
    load_theme,
    get_theme_color,
    get_theme_gradient,
    get_theme_typography,
    get_theme_font_size,
    get_theme_card_dimension,
    get_theme_border_radius,
    get_theme_chart_value,
    get_theme_language_color,
    format_timestamp_local,
    format_time_since,
    is_data_stale,
    format_large_number,
    generate_card_with_fallback,
    generate_sparkline_path,
)


def generate_metric_badge(
    label: str,
    value: str,
    icon: str,
    x: int,
    color: str,
    font_family: str,
    text_primary: str,
    text_secondary: str,
) -> str:
    """Generate a metric badge with icon, value, and label."""
    return f"""
    <g transform="translate({x}, 0)">
      <text font-family="{font_family}" font-size="18" fill="{text_primary}" font-weight="bold">
        {icon} {escape_xml(value)}
      </text>
      <text y="16" font-family="{font_family}" font-size="10" fill="{text_secondary}">
        {escape_xml(label)}
      </text>
    </g>"""


def generate_activity_heatmap(
    activity_grid: List[List[int]],
    x: int,
    y: int,
    width: int,
    height: int,
    accent_color: str,
) -> str:
    """Generate a 7×24 heatmap of commit activity."""
    if not activity_grid or len(activity_grid) != 7:
        return ""
    
    cell_width = width / 24
    cell_height = height / 7
    
    # Find max for normalization
    max_commits = max(max(row) for row in activity_grid) if activity_grid else 1
    if max_commits == 0:
        max_commits = 1
    
    cells = []
    for day_idx, day_row in enumerate(activity_grid):
        for hour_idx, count in enumerate(day_row):
            # Calculate opacity based on commit count
            if count == 0:
                opacity = 0.1
            else:
                # Use a logarithmic scale for better visibility
                opacity = 0.2 + (count / max_commits) * 0.8
            
            cx = x + hour_idx * cell_width
            cy = y + day_idx * cell_height
            
            cells.append(
                f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cell_width - 1:.1f}" '
                f'height="{cell_height - 1:.1f}" rx="1" fill="{accent_color}" '
                f'fill-opacity="{opacity:.2f}"/>'
            )
    
    return "\n".join(cells)


def generate_sparkline_chart(
    values: List[int],
    x: int,
    y: int,
    width: int,
    height: int,
    color: str,
    bg_color: str,
) -> str:
    """Generate a sparkline chart for activity."""
    path = generate_sparkline_path(values, width, height)  # type: ignore[arg-type]
    
    return f"""
    <g transform="translate({x}, {y})">
      <rect width="{width}" height="{height}" rx="4" fill="{bg_color}"/>
      <g transform="translate(0, 0)">
        <path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
      </g>
    </g>"""


def generate_bar_chart(
    items: List[Dict],
    x: int,
    y: int,
    width: int,
    max_bars: int,
    bar_height: int,
    bar_gap: int,
    color: str,
    font_family: str,
    text_primary: str,
    text_secondary: str,
) -> str:
    """Generate a horizontal bar chart for top repositories or languages."""
    if not items:
        return ""
    
    items = items[:max_bars]
    max_value = max(item.get("value", item.get("commits", 0)) for item in items)
    if max_value == 0:
        max_value = 1
    
    bars = []
    label_width = get_theme_chart_value("label_width", 100)
    bar_width = width - label_width - 40
    
    for idx, item in enumerate(items):
        name = item.get("name", "")
        value = item.get("value", item.get("commits", 0))
        bar_len = (value / max_value) * bar_width if max_value > 0 else 0
        
        by = y + idx * (bar_height + bar_gap)
        
        # Truncate long names
        display_name = name[:12] + "..." if len(name) > 12 else name
        
        bars.append(f"""
        <g transform="translate({x}, {by})">
          <text font-family="{font_family}" font-size="10" fill="{text_secondary}" 
                dominant-baseline="middle" y="{bar_height // 2}">{escape_xml(display_name)}</text>
          <rect x="{label_width}" y="0" width="{bar_len:.1f}" height="{bar_height}" 
                rx="2" fill="{color}"/>
          <text x="{label_width + bar_len + 5}" y="{bar_height // 2}" font-family="{font_family}" 
                font-size="9" fill="{text_secondary}" dominant-baseline="middle">
            {format_large_number(int(value))}
          </text>
        </g>""")
    
    return "\n".join(bars)


def generate_language_bars(
    languages: Dict[str, float],
    x: int,
    y: int,
    width: int,
    font_family: str,
    text_primary: str,
    text_secondary: str,
) -> str:
    """Generate stacked horizontal bar for language distribution."""
    if not languages:
        return ""
    
    # Sort languages by percentage
    sorted_langs = sorted(languages.items(), key=lambda x: -x[1])[:6]
    
    bar_height = get_theme_chart_value("bar_height", 16)
    current_x: float = float(x)
    bars = []
    legends = []
    
    for idx, (lang, pct) in enumerate(sorted_langs):
        bar_width = (pct / 100) * width
        color = get_theme_language_color(lang)
        
        if bar_width > 1:
            bars.append(
                f'<rect x="{current_x:.1f}" y="{y}" width="{bar_width:.1f}" height="{bar_height}" '
                f'fill="{color}"/>'
            )
            current_x += bar_width
        
        # Add legend item
        legend_x = x + (idx % 3) * (width // 3)
        legend_y = y + bar_height + 10 + (idx // 3) * 14
        legends.append(f"""
        <g transform="translate({legend_x}, {legend_y})">
          <rect width="8" height="8" rx="2" fill="{color}"/>
          <text x="12" font-family="{font_family}" font-size="9" fill="{text_secondary}" 
                dominant-baseline="middle" y="4">
            {escape_xml(lang)} {pct:.1f}%
          </text>
        </g>""")
    
    # Add rounded corners container
    bar_svg = f"""
    <g clip-path="url(#lang-clip)">
      {"".join(bars)}
    </g>
    <defs>
      <clipPath id="lang-clip">
        <rect x="{x}" y="{y}" width="{width}" height="{bar_height}" rx="4"/>
      </clipPath>
    </defs>
    {"".join(legends)}
    """
    
    return bar_svg


def generate_svg(stats: Dict) -> str:
    """Generate the Developer Stats Dashboard SVG."""
    
    # Load theme values
    theme = load_theme()
    font_family = get_theme_typography("font_family")
    
    # Colors from theme
    bg_gradient = get_theme_gradient("developer")
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    text_muted = get_theme_color("text", "muted")
    accent_teal = get_theme_color("text", "accent")
    accent_commits = get_theme_color("accent", "commits")
    accent_repos = get_theme_color("accent", "repos")
    accent_stars = get_theme_color("accent", "stars")
    accent_prs = get_theme_color("accent", "prs")
    accent_issues = get_theme_color("accent", "issues")
    panel_bg = get_theme_color("background", "panel")
    
    # Card dimensions from theme
    card_width = get_theme_card_dimension("widths", "developer_dashboard")
    card_height = get_theme_card_dimension("heights", "developer_dashboard")
    border_radius = get_theme_border_radius("xl")
    border_radius_md = get_theme_border_radius("md")
    
    # Card stroke settings
    stroke_width = theme.get("cards", {}).get("stroke_width", 1)
    stroke_opacity = theme.get("cards", {}).get("stroke_opacity", 0.3)
    
    # Effect settings
    glow = theme.get("effects", {}).get("glow", {})
    glow_std = glow.get("stdDeviation", 2)
    
    # Extract data
    username = stats.get("username", "Developer")
    name = stats.get("name", username)
    repos = stats.get("repos", 0)
    stars = stats.get("stars", 0)
    followers = stats.get("followers", 0)
    prs = stats.get("prs", {})
    issues = stats.get("issues", {})
    languages = stats.get("languages", {})
    top_repos = stats.get("top_repositories", [])
    commit_activity = stats.get("commit_activity", {})
    daily_commits = commit_activity.get("last_30_days", [])
    activity_grid = commit_activity.get("activity_grid", [])
    total_commits = commit_activity.get("total_30_days", sum(daily_commits))
    updated_at_raw = stats.get("updated_at", "")
    
    prs_opened = prs.get("opened", 0)
    prs_merged = prs.get("merged", 0)
    issues_opened = issues.get("opened", 0)
    
    # Generate metric badges
    metrics_y = 50
    metrics_row = f"""
    <g transform="translate(25, {metrics_y})">
      {generate_metric_badge("Repos", str(repos), "📦", 0, accent_repos, font_family, text_primary, text_secondary)}
      {generate_metric_badge("Stars", format_large_number(stars), "⭐", 120, accent_stars, font_family, text_primary, text_secondary)}
      {generate_metric_badge("PRs", f"{prs_opened}/{prs_merged}", "🔀", 240, accent_prs, font_family, text_primary, text_secondary)}
      {generate_metric_badge("Issues", str(issues_opened), "🐛", 360, accent_issues, font_family, text_primary, text_secondary)}
      {generate_metric_badge("Followers", format_large_number(followers), "👥", 480, accent_teal, font_family, text_primary, text_secondary)}
      {generate_metric_badge("Commits", format_large_number(total_commits), "📊", 600, accent_commits, font_family, text_primary, text_secondary)}
    </g>"""
    
    # Generate sparkline for recent commits
    sparkline = generate_sparkline_chart(
        daily_commits, 25, 100, 350, 50, accent_commits, panel_bg
    )
    
    # Generate activity heatmap
    heatmap = generate_activity_heatmap(
        activity_grid, 400, 100, 375, 50, accent_commits
    )
    
    # Generate top repositories bar chart
    top_repos_chart = generate_bar_chart(
        top_repos,
        25, 185,
        350,
        5, 14, 4,
        accent_repos,
        font_family,
        text_primary,
        text_secondary,
    )
    
    # Generate language bars
    language_chart = generate_language_bars(
        languages,
        400, 185, 375,
        font_family,
        text_primary,
        text_secondary,
    )
    
    # Calculate staleness badge
    staleness_badge = ""
    if updated_at_raw:
        time_since = format_time_since(updated_at_raw)
        is_stale = is_data_stale(updated_at_raw, stale_threshold_hours=24)
        
        # Use warning color if data is stale
        if is_stale:
            badge_color = accent_issues  # Warning color
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
      <stop offset="0%" style="stop-color:{bg_gradient[0]}"/>
      <stop offset="100%" style="stop-color:{bg_gradient[1]}"/>
    </linearGradient>
    <linearGradient id="commit-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{accent_commits}"/>
      <stop offset="100%" style="stop-color:{accent_teal}"/>
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
  <g transform="translate(25, 25)">
    <text font-family="{font_family}" font-size="16" fill="{accent_teal}" font-weight="600">
      💻 {escape_xml(name)}'s Developer Dashboard
    </text>
  </g>

  <!-- Metrics Row -->
  {metrics_row}

  <!-- Section Labels -->
  <g transform="translate(25, 95)">
    <text font-family="{font_family}" font-size="11" fill="{text_secondary}" font-weight="500">
      📈 Commits (Last 30 Days)
    </text>
  </g>
  <g transform="translate(400, 95)">
    <text font-family="{font_family}" font-size="11" fill="{text_secondary}" font-weight="500">
      🕐 Activity Pattern (Day × Hour)
    </text>
  </g>

  <!-- Sparkline Panel -->
  <g transform="translate(0, 5)">
    {sparkline}
  </g>

  <!-- Activity Heatmap -->
  {heatmap}

  <!-- Section Labels for Bottom Row -->
  <g transform="translate(25, 175)">
    <text font-family="{font_family}" font-size="11" fill="{text_secondary}" font-weight="500">
      🏆 Top Repositories
    </text>
  </g>
  <g transform="translate(400, 175)">
    <text font-family="{font_family}" font-size="11" fill="{text_secondary}" font-weight="500">
      💬 Languages
    </text>
  </g>

  <!-- Top Repositories -->
  {top_repos_chart}

  <!-- Languages Distribution -->
  {language_chart}

  {staleness_badge}

  <!-- Decorative accent -->
  <rect x="{card_width - 16}" y="15" width="4" height="{card_height - 30}" rx="2" fill="{accent_teal}" fill-opacity="{stroke_opacity}"/>
</svg>"""

    return svg


def main() -> None:
    """
    Main entry point for developer dashboard generation.
    
    Reads developer statistics and generates a comprehensive SVG dashboard
    with metrics, activity charts, and language statistics.
    """
    if len(sys.argv) < 2:
        print(
            "Usage: generate-developer-dashboard.py <stats.json> [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    stats_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "developer/developer_dashboard.svg"

    # Use fallback mechanism to generate the card
    success = generate_card_with_fallback(
        card_type="developer_dashboard",
        output_path=output_path,
        json_path=stats_path,
        schema_name="developer-stats",
        generator_func=generate_svg,
        description="Developer stats file",
    )

    if success:
        print(f"Generated developer dashboard SVG: {output_path}", file=sys.stderr)
    else:
        print(f"Using fallback developer dashboard SVG: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
