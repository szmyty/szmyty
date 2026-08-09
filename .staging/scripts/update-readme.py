#!/usr/bin/env python3
"""
Update README.md content between marker comments.

This script replaces content between <!-- MARKER:START --> and <!-- MARKER:END -->
markers in README.md with new content. It is used by GitHub Actions workflows
to update various card sections.

Usage:
    python update-readme.py --marker MARKER_NAME --content "new content"
    python update-readme.py --marker MARKER_NAME --content-file path/to/content.txt

Examples:
    python update-readme.py --marker LOCATION-CARD --content "![Location](./location/card.svg)"
    python update-readme.py --marker WEATHER-CARD --content "![Weather](./weather/card.svg)"
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


def find_readme() -> Path:
    """
    Find README.md relative to this script's location.

    Returns:
        Path to README.md in the repository root.

    Raises:
        SystemExit: If README.md is not found.
    """
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    readme_path = repo_root / "README.md"

    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}", file=sys.stderr)
        sys.exit(1)

    return readme_path


def validate_markers(content: str, marker: str) -> bool:
    """
    Validate that both START and END markers exist in the content.

    Args:
        content: The README content to check.
        marker: The marker name (e.g., 'LOCATION-CARD').

    Returns:
        True if both markers exist.

    Raises:
        SystemExit: If markers are not found.
    """
    start_marker = f"<!-- {marker}:START -->"
    end_marker = f"<!-- {marker}:END -->"

    if start_marker not in content:
        print(f"Error: Start marker not found: {start_marker}", file=sys.stderr)
        sys.exit(1)

    if end_marker not in content:
        print(f"Error: End marker not found: {end_marker}", file=sys.stderr)
        sys.exit(1)

    return True


def update_readme_section(marker: str, new_content: str, readme_path: Optional[Path] = None) -> None:
    """
    Update content between marker comments in README.md.

    Args:
        marker: The marker name (e.g., 'LOCATION-CARD', 'WEATHER-CARD').
        new_content: The new content to insert between markers.
        readme_path: Optional path to README.md. If not provided, uses find_readme().

    Raises:
        SystemExit: If markers are not found or file operations fail.
    """
    if readme_path is None:
        readme_path = find_readme()

    try:
        content = readme_path.read_text(encoding="utf-8")
    except IOError as e:
        print(f"Error reading README.md: {e}", file=sys.stderr)
        sys.exit(1)

    validate_markers(content, marker)

    # Use non-greedy matching (.*?) to match the first occurrence of the marker pair.
    # This correctly handles the case where content exists between START and END markers.
    # Note: Each marker name should only appear once in the README.
    pattern = rf"<!-- {re.escape(marker)}:START -->.*?<!-- {re.escape(marker)}:END -->"
    replacement = f"<!-- {marker}:START -->\n{new_content}\n<!-- {marker}:END -->"

    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    try:
        readme_path.write_text(updated_content, encoding="utf-8")
    except IOError as e:
        print(f"Error writing README.md: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Updated README section: {marker}", flush=True)


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Update README.md content between marker comments."
    )
    parser.add_argument(
        "--marker",
        required=True,
        help="Marker name (e.g., LOCATION-CARD, WEATHER-CARD)",
    )
    parser.add_argument(
        "--content",
        help="Content to insert between markers",
    )
    parser.add_argument(
        "--content-file",
        help="Path to file containing content to insert",
    )
    parser.add_argument(
        "--readme",
        help="Path to README.md (default: auto-detect from repo root)",
    )

    args = parser.parse_args()

    if not args.content and not args.content_file:
        parser.error("Either --content or --content-file must be provided")

    if args.content and args.content_file:
        parser.error("Only one of --content or --content-file can be provided")

    if args.content_file:
        content_path = Path(args.content_file)
        if not content_path.exists():
            print(f"Error: Content file not found: {args.content_file}", file=sys.stderr)
            sys.exit(1)
        try:
            new_content = content_path.read_text(encoding="utf-8").strip()
        except IOError as e:
            print(f"Error reading content file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        new_content = args.content

    readme_path = Path(args.readme) if args.readme else None

    update_readme_section(args.marker, new_content, readme_path)


if __name__ == "__main__":
    main()
