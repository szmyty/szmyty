#!/usr/bin/env python3
"""
Generate a status page SVG showing system health and recent updates.

This script creates a visual status dashboard displaying:
- Workflow execution status (success/failure)
- Last successful update timestamps
- Last failure timestamps
- Success rates
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.metrics import get_all_workflow_metrics
from lib.utils import (
    escape_xml,
    format_time_since,
    get_theme_color,
    get_theme_font_size,
    get_theme_spacing,
    get_theme_status_color,
    load_theme
)


def generate_status_indicator(status: str, x: int, y: int) -> str:
    """Generate a colored status indicator circle."""
    color = get_theme_status_color(status)
    
    return f'''
        <circle cx="{x}" cy="{y}" r="6" fill="{color}">
            <animate attributeName="opacity" 
                     values="1;0.4;1" 
                     dur="2s" 
                     repeatCount="indefinite" />
        </circle>
    '''


def determine_workflow_status(metrics: Dict[str, Any]) -> str:
    """Determine the status of a workflow based on metrics."""
    if metrics["total_runs"] == 0:
        return "unknown"
    
    consecutive_failures = metrics.get("consecutive_failures", 0)
    if consecutive_failures >= 3:
        return "error"
    elif consecutive_failures > 0:
        return "warning"
    else:
        return "success"


def generate_status_page_svg(output_path: str = "data/status/status-page.svg") -> None:
    """Generate the status page SVG."""
    
    # Load all workflow metrics
    all_metrics = get_all_workflow_metrics()
    
    # Sort by workflow name for consistent display
    all_metrics.sort(key=lambda m: m.get("workflow_name", ""))
    
    # Theme configuration
    theme = load_theme()
    bg_color = get_theme_color("background", "primary", "#0d1117")
    card_bg = get_theme_color("background", "secondary", "#161b22")
    text_color = get_theme_color("text", "primary", "#c9d1d9")
    text_secondary = get_theme_color("text", "secondary", "#8b949e")
    border_color = get_theme_color("border", "primary", "#30363d")
    
    font_size_lg = get_theme_font_size("lg", 16)
    font_size_base = get_theme_font_size("base", 14)
    font_size_sm = get_theme_font_size("sm", 12)
    spacing_md = get_theme_spacing("md", 16)
    
    # Calculate dimensions
    card_padding = 20
    row_height = 70
    header_height = 60
    num_workflows = len(all_metrics)
    
    if num_workflows == 0:
        # Show a message if no metrics available
        width = 600
        height = 200
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
            <defs>
                <style>
                    .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
                </style>
            </defs>
            <rect width="{width}" height="{height}" fill="{bg_color}" rx="12"/>
            <text x="{width/2}" y="{height/2}" font-size="{font_size_base}" fill="{text_secondary}" 
                  text-anchor="middle" class="title">
                No workflow metrics available yet
            </text>
        </svg>'''
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(svg)
        return
    
    width = 800
    height = header_height + (num_workflows * row_height) + card_padding * 2
    
    # Start building SVG
    svg_parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs>
        <style>
            .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-weight: 600; }}
            .label {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-weight: 500; }}
            .value {{ font-family: ui-monospace, 'SF Mono', monospace; }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="{bg_color}" rx="12"/>
    
    <!-- Header -->
    <text x="{card_padding}" y="{card_padding + 24}" 
          font-size="{font_size_lg + 4}" fill="{text_color}" class="title">
        System Status
    </text>
    <text x="{card_padding}" y="{card_padding + 45}" 
          font-size="{font_size_sm}" fill="{text_secondary}" class="value">
        Last updated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
    </text>
    
    <!-- Column headers -->
    <text x="{card_padding + 30}" y="{header_height + 10}" 
          font-size="{font_size_sm}" fill="{text_secondary}" class="label">
        Workflow
    </text>
    <text x="{width - 400}" y="{header_height + 10}" 
          font-size="{font_size_sm}" fill="{text_secondary}" class="label">
        Last Success
    </text>
    <text x="{width - 240}" y="{header_height + 10}" 
          font-size="{font_size_sm}" fill="{text_secondary}" class="label">
        Last Failure
    </text>
    <text x="{width - 90}" y="{header_height + 10}" 
          font-size="{font_size_sm}" fill="{text_secondary}" text-anchor="end" class="label">
        Success Rate
    </text>
''']
    
    # Add workflow status rows
    for i, metrics in enumerate(all_metrics):
        y_pos = header_height + 30 + (i * row_height)
        
        workflow_name = metrics.get("workflow_name", "Unknown")
        status = determine_workflow_status(metrics)
        
        # Status indicator
        svg_parts.append(generate_status_indicator(status, card_padding + 10, y_pos + 15))
        
        # Workflow name
        display_name = workflow_name.replace("-", " ").title()
        svg_parts.append(f'''
        <text x="{card_padding + 30}" y="{y_pos + 20}" 
              font-size="{font_size_base}" fill="{text_color}" class="label">
            {escape_xml(display_name)}
        </text>
        ''')
        
        # Stats
        total_runs = metrics.get("total_runs", 0)
        successful_runs = metrics.get("successful_runs", 0)
        
        # Last success timestamp
        last_success = metrics.get("last_success")
        if last_success:
            time_ago = format_time_since(last_success)
            svg_parts.append(f'''
        <text x="{width - 400}" y="{y_pos + 20}" 
              font-size="{font_size_sm}" fill="{text_color}" class="value">
            {escape_xml(time_ago)}
        </text>
            ''')
        else:
            svg_parts.append(f'''
        <text x="{width - 400}" y="{y_pos + 20}" 
              font-size="{font_size_sm}" fill="{text_secondary}" class="value">
            Never
        </text>
            ''')
        
        # Last failure timestamp
        last_failure = metrics.get("last_failure")
        consecutive_failures = metrics.get("consecutive_failures", 0)
        
        if last_failure:
            time_ago = format_time_since(last_failure)
            failure_color = get_theme_status_color("error") if consecutive_failures >= 3 else text_color
            svg_parts.append(f'''
        <text x="{width - 240}" y="{y_pos + 20}" 
              font-size="{font_size_sm}" fill="{failure_color}" class="value">
            {escape_xml(time_ago)}
        </text>
            ''')
            
            if consecutive_failures > 0:
                svg_parts.append(f'''
        <text x="{width - 240}" y="{y_pos + 38}" 
              font-size="{font_size_sm - 2}" fill="{failure_color}" class="value">
            ({consecutive_failures} consecutive)
        </text>
                ''')
        else:
            svg_parts.append(f'''
        <text x="{width - 240}" y="{y_pos + 20}" 
              font-size="{font_size_sm}" fill="{text_secondary}" class="value">
            Never
        </text>
            ''')
        
        # Success rate
        if total_runs > 0:
            success_rate = (successful_runs / total_runs) * 100
            rate_color = get_theme_status_color("success") if success_rate >= 90 else get_theme_status_color("warning") if success_rate >= 70 else get_theme_status_color("error")
            svg_parts.append(f'''
        <text x="{width - 90}" y="{y_pos + 20}" 
              font-size="{font_size_base}" fill="{rate_color}" class="value" text-anchor="end">
            {success_rate:.1f}%
        </text>
        <text x="{width - 90}" y="{y_pos + 38}" 
              font-size="{font_size_sm - 2}" fill="{text_secondary}" class="value" text-anchor="end">
            {successful_runs}/{total_runs}
        </text>
            ''')
        else:
            svg_parts.append(f'''
        <text x="{width - 90}" y="{y_pos + 20}" 
              font-size="{font_size_base}" fill="{text_secondary}" class="value" text-anchor="end">
            N/A
        </text>
            ''')
        
        # Separator line
        if i < num_workflows - 1:
            svg_parts.append(f'''
        <line x1="{card_padding}" y1="{y_pos + 50}" 
              x2="{width - card_padding}" y2="{y_pos + 50}" 
              stroke="{border_color}" stroke-width="1" opacity="0.5"/>
            ''')
    
    svg_parts.append('</svg>')
    
    # Write to file
    svg = '\n'.join(svg_parts)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(svg)
    
    print(f"Status page generated: {output_path}")


if __name__ == "__main__":
    output_path = sys.argv[1] if len(sys.argv) > 1 else "data/status/status-page.svg"
    generate_status_page_svg(output_path)
