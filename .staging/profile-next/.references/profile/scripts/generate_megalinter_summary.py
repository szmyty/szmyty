#!/usr/bin/env python3
"""
Generate a summary report from MegaLinter output.

This script parses MegaLinter JSON reports and creates a concise summary
with error counts, warnings, and recommendations.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import Counter
from datetime import datetime, timezone


class MegaLinterSummaryGenerator:
    """Generator for MegaLinter summary reports."""

    def __init__(self, reports_dir: Path):
        """Initialize the summary generator."""
        self.reports_dir = reports_dir
        self.json_report: Dict[str, Any] = {}
        self.errors = 0
        self.warnings = 0
        self.fixed = 0
        self.linters_run = 0
        self.linters_success = 0
        self.linters_errors = 0
        self.total_files = 0
        self.issues_by_linter: Dict[str, int] = {}

    def load_json_report(self) -> bool:
        """Load the MegaLinter JSON report."""
        # Try multiple possible locations
        possible_paths = [
            self.reports_dir / "report.json",
            self.reports_dir / "megalinter-report.json",
            self.reports_dir.parent / "megalinter-reports" / "megalinter-report.json",
        ]

        for json_path in possible_paths:
            if json_path.exists():
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        self.json_report = json.load(f)
                    return True
                except Exception as e:
                    print(f"Warning: Error reading {json_path}: {e}", file=sys.stderr)

        print("Warning: No JSON report found", file=sys.stderr)
        return False

    def parse_report(self) -> None:
        """Parse the JSON report and extract statistics."""
        if not self.json_report:
            return

        # Get linters array
        linters = self.json_report.get("linters", [])
        self.linters_run = len(linters)

        for linter in linters:
            linter_name = linter.get("linter_name", "Unknown")
            status = linter.get("status", "unknown")
            total_errors = linter.get("total_number_errors", 0)
            files_fixed = linter.get("files_fixed", 0)

            # Track statistics
            if status == "success":
                self.linters_success += 1
            elif total_errors > 0:
                self.linters_errors += 1

            self.errors += total_errors
            self.fixed += files_fixed

            # Track issues by linter
            if total_errors > 0:
                self.issues_by_linter[linter_name] = total_errors

            # Count files linted
            total_files_linted = linter.get("total_files_linted", 0)
            self.total_files += total_files_linted

        # Some reports have a summary section
        summary = self.json_report.get("summary", {})
        if summary:
            # Use summary if available
            self.errors = summary.get("total_errors", self.errors)
            self.warnings = summary.get("total_warnings", self.warnings)

    def get_top_issues(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get the top N linters with the most issues."""
        return Counter(self.issues_by_linter).most_common(limit)

    def generate_markdown_summary(self) -> str:
        """Generate a markdown summary report."""
        lines = [
            "# MegaLinter Analysis Summary",
            "",
            f"**Report Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "---",
            "",
            "## 📊 Overall Statistics",
            "",
            f"- **Total Linters Run:** {self.linters_run}",
            f"- **Successful Linters:** {self.linters_success}",
            f"- **Linters with Errors:** {self.linters_errors}",
            f"- **Total Files Analyzed:** {self.total_files}",
            "",
            "## 🐛 Issues Summary",
            "",
            f"- **Total Errors:** {self.errors}",
            f"- **Total Warnings:** {self.warnings}",
            f"- **Files Fixed:** {self.fixed}",
            "",
        ]

        # Top issues section
        top_issues = self.get_top_issues(10)
        if top_issues:
            lines.extend(
                [
                    "## 🔝 Top 10 Linters with Issues",
                    "",
                    "| Rank | Linter | Error Count |",
                    "|------|--------|-------------|",
                ]
            )

            for rank, (linter, count) in enumerate(top_issues, 1):
                lines.append(f"| {rank} | `{linter}` | {count} |")

            lines.append("")

        # Status indicator
        if self.errors == 0 and self.warnings == 0:
            status = "✅ **No issues found!**"
            severity = "success"
        elif self.errors == 0:
            status = f"⚠️ **{self.warnings} warnings found**"
            severity = "warning"
        elif self.errors < 50:
            status = f"⚠️ **{self.errors} errors found**"
            severity = "warning"
        else:
            status = f"❌ **{self.errors} errors found**"
            severity = "error"

        lines.extend(
            [
                "## 📈 Analysis Status",
                "",
                status,
                "",
            ]
        )

        # Recommendations
        lines.extend(
            [
                "## 💡 Recommended Next Steps",
                "",
            ]
        )

        if self.errors > 0:
            lines.extend(
                [
                    "1. **Review the top linters with errors** listed above",
                    "2. Check the full reports in the artifacts for detailed error messages",
                    "3. Consider creating GitHub Issues for systematic error resolution",
                    "4. Run `megalinter-runner` locally to fix issues before committing",
                ]
            )
        else:
            lines.extend(
                [
                    "1. ✅ Your code quality is excellent!",
                    "2. Continue monitoring with regular MegaLinter runs",
                    "3. Consider enabling additional linters for broader coverage",
                ]
            )

        lines.extend(
            [
                "",
                "## 📁 Available Reports",
                "",
                "- `report.txt` - Full text log of linter execution",
                "- `report.json` - Detailed JSON report with all linter results",
                "- `config_audit.txt` - Audit of .megalinter.yml configuration",
                "- Check GitHub Actions artifacts for additional reports",
                "",
                "---",
                "",
                "*This is a diagnostic report. No changes were made to your codebase.*",
            ]
        )

        return "\n".join(lines)

    def generate(self, output_path: Path) -> bool:
        """Generate and save the summary report."""
        # Load and parse report
        if self.load_json_report():
            self.parse_report()

        # Generate summary
        summary = self.generate_markdown_summary()

        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)

        # Also print to stdout
        print(summary)

        return True


def main() -> int:
    """Main entry point for the summary generator."""
    parser = argparse.ArgumentParser(
        description="Generate summary report from MegaLinter output"
    )
    parser.add_argument(
        "reports_dir",
        help="Directory containing MegaLinter reports",
    )
    parser.add_argument(
        "output_file",
        help="Path to write summary markdown file",
    )

    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    output_path = Path(args.output_file)

    # Generate summary
    generator = MegaLinterSummaryGenerator(reports_dir)
    success = generator.generate(output_path)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
