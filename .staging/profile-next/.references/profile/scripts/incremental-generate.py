#!/usr/bin/env python3
"""
Incremental SVG generation wrapper with change detection.
This script checks if source data has changed before regenerating SVGs,
significantly reducing unnecessary processing.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Optional

from lib.change_detection import should_regenerate_svg, update_hash_cache


# Define cache location
CACHE_DIR = Path(".cache")
HASH_CACHE_FILE = CACHE_DIR / "svg_hashes.json"


def generate_with_change_detection(
    data_path: str,
    svg_path: str,
    generator_script: str,
    cache_key: str,
    extra_args: Optional[List[str]] = None,
    force: bool = False
) -> bool:
    """
    Generate SVG only if data has changed.
    
    Args:
        data_path: Path to source data file
        svg_path: Path to output SVG file
        generator_script: Path to the generator script (must be in scripts/ directory)
        cache_key: Unique key for this generation task
        extra_args: Additional arguments for the generator
        force: Force regeneration even if data unchanged
        
    Returns:
        True if SVG was regenerated, False if skipped
    """
    data_file = Path(data_path)
    svg_file = Path(svg_path)
    generator_path = Path(generator_script)
    
    # Validate generator script is in scripts/ directory for security
    # This prevents arbitrary code execution
    scripts_dir = Path(__file__).parent.parent / "scripts"
    try:
        generator_path.resolve().relative_to(scripts_dir.resolve())
    except (ValueError, RuntimeError):
        print(f"❌ Error: Generator script must be in scripts/ directory: {generator_script}", file=sys.stderr)
        return False
    
    # Check if we should regenerate
    if not should_regenerate_svg(data_file, svg_file, HASH_CACHE_FILE, cache_key, force):
        print(f"⏭️  Skipping {svg_file.name} - data unchanged")
        return False
    
    print(f"🔄 Generating {svg_file.name} - data changed or new")
    
    # Build command
    cmd = ["python", generator_script, data_path, svg_path]
    if extra_args:
        cmd.extend(extra_args)
    
    # Run generator
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        
        # Update hash cache on success
        update_hash_cache(data_file, HASH_CACHE_FILE, cache_key)
        print(f"✅ Generated {svg_file.name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating {svg_file.name}: {e}", file=sys.stderr)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return False


def main() -> None:
    """Main entry point for CLI usage."""
    if len(sys.argv) < 5:
        print("Usage: incremental-generate.py <data_path> <svg_path> <generator_script> <cache_key> [extra_args...]")
        sys.exit(1)
    
    data_path = sys.argv[1]
    svg_path = sys.argv[2]
    generator_script = sys.argv[3]
    cache_key = sys.argv[4]
    extra_args = sys.argv[5:] if len(sys.argv) > 5 else []
    
    # Check for force flag
    force = "--force" in extra_args
    if force:
        extra_args.remove("--force")
    
    success = generate_with_change_detection(
        data_path, svg_path, generator_script, cache_key, extra_args, force
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
