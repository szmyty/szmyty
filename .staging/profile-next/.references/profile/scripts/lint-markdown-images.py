#!/usr/bin/env python3
"""
Lint Markdown Images in HTML Blocks

This script scans for markdown image syntax (![]()) inside HTML blocks
and reports them as errors. GitHub Markdown does not render markdown syntax
inside HTML elements like <p>, <div>, etc.

Usage:
    python lint-markdown-images.py [file1.md file2.md ...]
    python lint-markdown-images.py README.md

Exit codes:
    0 - No issues found
    1 - Markdown images found inside HTML blocks
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


def find_markdown_images_in_html(content: str, filepath: str) -> List[Tuple[int, str]]:
    """
    Find markdown image syntax inside HTML blocks.

    Args:
        content: The markdown file content.
        filepath: Path to the file being checked (for error messages).

    Returns:
        List of tuples containing (line_number, problematic_line).
    """
    issues = []
    lines = content.split("\n")
    html_block_depth = 0  # Track nesting depth of HTML blocks

    # HTML block opening tags that should not contain markdown syntax
    html_block_opening_tags = [
        (r"<p\s", r"</p>"),
        (r"<p>", r"</p>"),
        (r"<div\s", r"</div>"),
        (r"<div>", r"</div>"),
        (r"<section\s", r"</section>"),
        (r"<section>", r"</section>"),
        (r"<article\s", r"</article>"),
        (r"<article>", r"</article>"),
    ]

    # Markdown image pattern
    markdown_image_pattern = re.compile(r"!\[.*?\]\(.*?\)")
    
    # Badge patterns to exclude (these render fine in GitHub)
    badge_patterns = [
        r"img\.shields\.io",
        r"komarev\.com/ghpvc",
        r"badge\.svg",
    ]

    for i, line in enumerate(lines, start=1):
        # Check if we're entering an HTML block
        for opening_tag, closing_tag in html_block_opening_tags:
            if re.search(opening_tag, line):
                html_block_depth += 1
            if re.search(closing_tag, line):
                html_block_depth = max(0, html_block_depth - 1)

        # If we're inside an HTML block, check for markdown images
        if html_block_depth > 0 and markdown_image_pattern.search(line):
            # Skip if it's a badge (these render fine in GitHub)
            is_badge = any(re.search(pattern, line) for pattern in badge_patterns)
            if not is_badge:
                issues.append((i, line.strip()))

    return issues


def lint_file(filepath: Path) -> bool:
    """
    Lint a single markdown file for markdown images in HTML blocks.

    Args:
        filepath: Path to the markdown file.

    Returns:
        True if issues were found, False otherwise.
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except IOError as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False

    issues = find_markdown_images_in_html(content, str(filepath))

    if issues:
        print(f"\n❌ {filepath}:")
        print(f"   Found {len(issues)} markdown image(s) inside HTML blocks:")
        for line_num, line_content in issues:
            print(f"   Line {line_num}: {line_content}")
            # Extract the markdown image syntax
            match = re.search(r"!\[.*?\]\(.*?\)", line_content)
            if match:
                markdown_img = match.group(0)
                # Suggest conversion to <img> tag
                alt_text = re.search(r"!\[(.*?)\]", markdown_img)
                src = re.search(r"\((.*?)\)", markdown_img)
                if alt_text and src:
                    suggestion = (
                        f'<img src="{src.group(1)}" alt="{alt_text.group(1)}" width="100%"/>'
                    )
                    print(f"   Suggestion: {suggestion}")
        return True

    return False


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Lint markdown files for markdown images inside HTML blocks."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Markdown files to lint (default: README.md)",
    )

    args = parser.parse_args()

    # Default to README.md if no files specified
    if not args.files:
        files = [Path("README.md")]
    else:
        files = [Path(f) for f in args.files]

    # Check that all files exist
    for filepath in files:
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)

    # Lint all files
    has_issues = False
    for filepath in files:
        if lint_file(filepath):
            has_issues = True

    if has_issues:
        print(
            "\n⚠️  Markdown images found inside HTML blocks. "
            "Convert them to <img> tags for proper GitHub rendering."
        )
        sys.exit(1)
    else:
        print("✅ No markdown images found inside HTML blocks.")
        sys.exit(0)


if __name__ == "__main__":
    main()
