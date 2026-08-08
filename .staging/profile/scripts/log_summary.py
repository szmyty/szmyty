#!/usr/bin/env python3
"""
Log aggregation and workflow performance dashboard generator.

This script:
1. Aggregates logs across all workflows
2. Extracts metrics: run time, failures, errors
3. Loads existing metrics from data/metrics/*.json
4. Generates dashboard.svg summarizing performance data
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.card_base import CardBase  # noqa: E402
from lib.utils import escape_xml  # noqa: E402
from lib.metrics import get_all_workflow_metrics  # noqa: E402


class WorkflowPerformanceCard(CardBase):
    """
    SVG card generator for workflow performance dashboard.
    """

    def __init__(self, workflow_metrics: List[Dict]):
        """
        Initialize the workflow performance card.

        Args:
            workflow_metrics: List of workflow metrics dictionaries
        """
        super().__init__("default")
        self.workflow_metrics = workflow_metrics
        self.width = 800
        self.height = 400

    def generate_content(self) -> str:
        """Generate the card content with workflow performance metrics."""
        if not self.workflow_metrics:
            return self._generate_no_data_content()

        # Calculate aggregate statistics
        total_workflows = len(self.workflow_metrics)
        total_runs = sum(m.get("total_runs", 0) for m in self.workflow_metrics)
        total_successes = sum(m.get("successful_runs", 0) for m in self.workflow_metrics)

        success_rate = (total_successes / total_runs * 100) if total_runs > 0 else 0

        # Calculate average run times
        workflows_with_times = [
            m for m in self.workflow_metrics if m.get("avg_run_time_seconds") is not None
        ]
        avg_run_time = (
            sum(m.get("avg_run_time_seconds", 0) for m in workflows_with_times)
            / len(workflows_with_times)
            if workflows_with_times
            else 0
        )

        font_family = self.get_typography("font_family")
        title_size = self.get_font_size("2xl")
        heading_size = self.get_font_size("lg")
        base_size = self.get_font_size("base")
        small_size = self.get_font_size("sm")

        text_primary = self.get_color("text", "primary")
        text_secondary = self.get_color("text", "secondary")
        success_color = self.get_status_color("success", "#10b981")
        error_color = self.get_status_color("error", "#ef4444")
        warning_color = self.get_status_color("warning", "#f59e0b")

        parts = []

        # Title
        parts.append(
            f"""
  <!-- Title -->
  <g transform="translate(30, 40)">
    <text font-family="{font_family}" font-size="{title_size}" font-weight="bold" fill="{text_primary}"  # noqa: E501>
      Workflow Performance Dashboard
    </text>
  </g>"""
        )

        # Summary stats
        y_offset = 90
        parts.append(
            f"""
  <!-- Summary Statistics -->
  <g transform="translate(30, {y_offset})">
    <text font-family="{font_family}" font-size="{heading_size}" font-weight="600" fill="{text_primary}"  # noqa: E501>
      Summary
    </text>
  </g>"""
        )

        y_offset += 35
        stats = [
            ("Total Workflows", str(total_workflows), text_primary),
            ("Total Runs", str(total_runs), text_primary),
            (
                "Success Rate",
                f"{success_rate:.1f}%",
                success_color if success_rate >= 90 else warning_color,
            ),
            ("Avg Run Time", f"{avg_run_time:.1f}s" if avg_run_time > 0 else "N/A", text_secondary),
        ]

        x_positions = [30, 220, 410, 600]
        for i, (label, value, color) in enumerate(stats):
            parts.append(
                f"""
  <g transform="translate({x_positions[i]}, {y_offset})">
    <text font-family="{font_family}" font-size="{small_size}" fill="{text_secondary}">
      {escape_xml(label)}
    </text>
    <text font-family="{font_family}" font-size="{heading_size}" font-weight="600" fill="{color}" y="25"> # noqa: E501
      {escape_xml(value)}
    </text>
  </g>"""
            )

        # Workflow details
        y_offset += 80
        parts.append(
            f"""
  <!-- Workflow Details -->
  <g transform="translate(30, {y_offset})">
    <text font-family="{font_family}" font-size="{heading_size}" font-weight="600" fill="{text_primary}"  # noqa: E501>
      Workflows
    </text>
  </g>"""
        )

        # Table header
        y_offset += 35
        parts.append(
            f"""
  <g transform="translate(30, {y_offset})">
    <text font-family="{font_family}" font-size="{small_size}" fill="{text_secondary}" font-weight="600"  # noqa: E501>
      Name
    </text>
  </g>
  <g transform="translate(220, {y_offset})">
    <text font-family="{font_family}" font-size="{small_size}" fill="{text_secondary}" font-weight="600"  # noqa: E501>
      Runs
    </text>
  </g>
  <g transform="translate(300, {y_offset})">
    <text font-family="{font_family}" font-size="{small_size}" fill="{text_secondary}" font-weight="600"  # noqa: E501>
      Success Rate
    </text>
  </g>
  <g transform="translate(440, {y_offset})">
    <text font-family="{font_family}" font-size="{small_size}" fill="{text_secondary}" font-weight="600"  # noqa: E501>
      Avg Time
    </text>
  </g>
  <g transform="translate(560, {y_offset})">
    <text font-family="{font_family}" font-size="{small_size}" fill="{text_secondary}" font-weight="600"  # noqa: E501>
      Status
    </text>
  </g>"""
        )

        # Workflow rows (show first 4)
        y_offset += 25
        for i, workflow in enumerate(self.workflow_metrics[:4]):
            name = workflow.get("workflow_name", "unknown")
            runs = workflow.get("total_runs", 0)
            successes = workflow.get("successful_runs", 0)
            wf_success_rate = (successes / runs * 100) if runs > 0 else 0
            avg_time = workflow.get("avg_run_time_seconds") or 0
            consecutive_failures = workflow.get("consecutive_failures", 0)

            # Determine status
            if consecutive_failures >= 3:
                status = "⚠ Failing"
                status_color = error_color
            elif consecutive_failures > 0:
                status = "⚡ Warning"
                status_color = warning_color
            elif runs > 0:
                status = "✓ Healthy"
                status_color = success_color
            else:
                status = "— No Data"
                status_color = text_secondary

            parts.append(
                f"""
  <g transform="translate(30, {y_offset})">
    <text font-family="{font_family}" font-size="{base_size}" fill="{text_primary}">
      {escape_xml(name)}
    </text>
  </g>
  <g transform="translate(220, {y_offset})">
    <text font-family="{font_family}" font-size="{base_size}" fill="{text_secondary}">
      {runs}
    </text>
  </g>
  <g transform="translate(300, {y_offset})">
    <text font-family="{font_family}" font-size="{base_size}" \
fill="{'#4ade80' if wf_success_rate >= 90 else '#fbbf24'}">
      {wf_success_rate:.1f}%
    </text>
  </g>
  <g transform="translate(440, {y_offset})">
    <text font-family="{font_family}" font-size="{base_size}" fill="{text_secondary}">
      {f"{avg_time:.1f}s" if avg_time > 0 else "N/A"}
    </text>
  </g>
  <g transform="translate(560, {y_offset})">
    <text font-family="{font_family}" font-size="{base_size}" fill="{status_color}">
      {escape_xml(status)}
    </text>
  </g>"""
            )
            y_offset += 25

        return "\n".join(parts)

    def _generate_no_data_content(self) -> str:
        """Generate content when no metrics are available."""
        font_family = self.get_typography("font_family")
        title_size = self.get_font_size("2xl")
        base_size = self.get_font_size("base")
        text_primary = self.get_color("text", "primary")
        text_secondary = self.get_color("text", "secondary")

        return f"""
  <!-- Title -->
  <g transform="translate(30, 40)">
    <text font-family="{font_family}" font-size="{title_size}" font-weight="bold" fill="{text_primary}"  # noqa: E501>
      Workflow Performance Dashboard
    </text>
  </g>

  <!-- No Data Message -->
  <g transform="translate(30, 120)">
    <text font-family="{font_family}" font-size="{base_size}" fill="{text_secondary}">
      No workflow metrics available yet.
    </text>
    <text font-family="{font_family}" font-size="{base_size}" fill="{text_secondary}" y="30">
      Metrics will appear after workflows run and record their execution data.
    </text>
  </g>"""


def aggregate_log_summary() -> Dict:
    """
    Aggregate logs across all workflows and extract key metrics.

    Returns:
        Dictionary containing aggregated log summary
    """
    logs_dir = Path(__file__).parent.parent / "logs"
    summary = {
        "total_log_files": 0,
        "total_log_size_bytes": 0,
        "workflows_with_logs": [],
        "errors_found": [],
    }

    # Scan all workflow log directories
    if logs_dir.exists():
        for workflow_dir in logs_dir.iterdir():
            if workflow_dir.is_dir() and not workflow_dir.name.startswith("."):
                log_files = list(workflow_dir.glob("*.log"))
                if log_files:
                    summary["workflows_with_logs"].append(workflow_dir.name)
                    for log_file in log_files:
                        summary["total_log_files"] += 1
                        try:
                            summary["total_log_size_bytes"] += log_file.stat().st_size

                            # Scan for errors in recent lines
                            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                                lines = f.readlines()
                                for line in lines[-50:]:  # Check last 50 lines
                                    if any(
                                        keyword in line.lower()
                                        for keyword in ["error", "failed", "exception"]
                                    ):
                                        summary["errors_found"].append(
                                            {
                                                "workflow": workflow_dir.name,
                                                "file": log_file.name,
                                                "line": line.strip()[:200],
                                            }
                                        )
                        except Exception as e:
                            print(
                                f"Warning: Failed to process {log_file}: {e}",
                                file=sys.stderr,
                            )

    return summary


def generate_dashboard_svg(output_path: str = "dashboard.svg") -> None:
    """
    Generate workflow performance dashboard SVG.

    Args:
        output_path: Path to save the dashboard SVG
    """
    # Load all workflow metrics
    workflow_metrics = get_all_workflow_metrics()

    # Sort by workflow name for consistent display
    workflow_metrics.sort(key=lambda m: m.get("workflow_name", ""))

    # Create the card
    card = WorkflowPerformanceCard(workflow_metrics)

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).strftime("Updated: %Y-%m-%d %H:%M UTC")

    # Generate SVG
    svg_content = card.generate_svg(footer_text=timestamp)

    # Write to file
    card.write_svg(output_path, svg_content)

    print(f"Dashboard generated: {output_path}")
    print(f"  Workflows: {len(workflow_metrics)}")
    if workflow_metrics:
        total_runs = sum(m.get("total_runs", 0) for m in workflow_metrics)
        total_successes = sum(m.get("successful_runs", 0) for m in workflow_metrics)
        success_rate = (total_successes / total_runs * 100) if total_runs > 0 else 0
        print(f"  Total runs: {total_runs}")
        print(f"  Success rate: {success_rate:.1f}%")


def print_log_summary() -> None:
    """Print aggregated log summary to stdout."""
    summary = aggregate_log_summary()

    print("\n=== Log Summary ===")
    print(f"Total log files: {summary['total_log_files']}")
    print(f"Total log size: {summary['total_log_size_bytes']:,} bytes")
    print(f"Workflows with logs: {', '.join(summary['workflows_with_logs']) or 'None'}")

    if summary["errors_found"]:
        print(f"\nRecent errors found: {len(summary['errors_found'])}")
        for error in summary["errors_found"][:5]:  # Show first 5
            print(f"  [{error['workflow']}] {error['line'][:100]}")
    else:
        print("\nNo recent errors found in logs.")


def main() -> None:
    """Main entry point for log summary script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Aggregate logs and generate workflow performance dashboard"
    )
    parser.add_argument(
        "--output",
        default="dashboard.svg",
        help="Output path for dashboard SVG (default: dashboard.svg)",
    )
    parser.add_argument(
        "--print-summary",
        action="store_true",
        help="Print log summary to stdout",
    )

    args = parser.parse_args()

    # Print log summary if requested
    if args.print_summary:
        print_log_summary()

    # Generate dashboard
    generate_dashboard_svg(args.output)


if __name__ == "__main__":
    main()
