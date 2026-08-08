#!/usr/bin/env python3
"""
IP Reference Lint Check

Purpose:
    Scans edition schema files for forbidden references to external intellectual
    property (IP), franchises, or licensed universes.  Violations must be
    replaced with neutral aesthetic descriptors before assets can be published.

Usage:
    Run from the repository root:

        python scripts/lint_ip_references.py

    The script exits with code 0 when no violations are found, or code 1 when
    one or more violations are detected.

Expected inputs:
    All ``*.page.json`` and ``meta.json`` files found recursively beneath the
    repository root (excluding node_modules, .git, dist, and build trees).

Expected outputs:
    A plain-text report written to stdout listing each violation by file path,
    line number, and offending line content.  A summary line indicates PASSED
    or FAILED.
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple

# Forbidden terms representing external IP or franchises
# These should be replaced with neutral aesthetic descriptors
FORBIDDEN_TERMS = [
    "fallout",
    # Add more forbidden terms here as needed
]

# File patterns to check
SCHEMA_PATTERNS = [
    "**/*.page.json",
    "**/meta.json",
]

# File patterns to exclude
EXCLUDE_PATTERNS = [
    "**/node_modules/**",
    "**/.git/**",
    "**/dist/**",
    "**/build/**",
]


def should_exclude(file_path: Path) -> bool:
    """Check if file should be excluded from scanning."""
    path_str = str(file_path)
    return any(file_path.match(pattern) for pattern in EXCLUDE_PATTERNS)


def scan_file(file_path: Path, forbidden_terms: List[str]) -> List[Tuple[str, int, str]]:
    """
    Scan a file for forbidden terms (case-insensitive).
    Returns list of (term, line_number, line_content) tuples.
    """
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, start=1):
            line_lower = line.lower()
            for term in forbidden_terms:
                if term.lower() in line_lower:
                    violations.append((term, line_num, line.strip()))
    
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
    
    return violations


def find_schema_files(root_dir: Path) -> List[Path]:
    """Find all schema files matching the patterns."""
    schema_files = []
    
    for pattern in SCHEMA_PATTERNS:
        for file_path in root_dir.glob(pattern):
            if file_path.is_file() and not should_exclude(file_path):
                schema_files.append(file_path)
    
    return sorted(schema_files)


def main():
    """Main entry point."""
    root_dir = Path(__file__).parent.parent
    
    print("IP Reference Lint Check")
    print("=" * 60)
    print(f"Scanning directory: {root_dir}")
    print(f"Forbidden terms: {', '.join(FORBIDDEN_TERMS)}")
    print()
    
    schema_files = find_schema_files(root_dir)
    print(f"Found {len(schema_files)} schema files to check")
    print()
    
    total_violations = 0
    files_with_violations = []
    
    for file_path in schema_files:
        violations = scan_file(file_path, FORBIDDEN_TERMS)
        
        if violations:
            files_with_violations.append(file_path)
            relative_path = file_path.relative_to(root_dir)
            print(f"❌ {relative_path}")
            
            for term, line_num, line_content in violations:
                print(f"   Line {line_num}: Found '{term}'")
                truncated = line_content[:100]
                ellipsis = '...' if len(line_content) > 100 else ''
                print(f"   > {truncated}{ellipsis}")
                total_violations += 1
            print()
    
    if total_violations > 0:
        print("=" * 60)
        print(f"FAILED: Found {total_violations} violation(s) in {len(files_with_violations)} file(s)")
        print()
        print("External IP references are not allowed in schema files.")
        print("Please replace them with neutral aesthetic descriptors.")
        print()
        print("Examples of acceptable replacements:")
        print("  - Instead of franchise names: 'retro print', 'aged paper', 'weathered artifact'")
        print("  - Instead of game references: 'distressed ink', 'analog texture', 'field manual tone'")
        print("  - Instead of universe names: 'mystic symbolism', 'post-collapse aesthetic'")
        sys.exit(1)
    else:
        print("=" * 60)
        print("✅ PASSED: No IP references found")
        sys.exit(0)


if __name__ == "__main__":
    main()
