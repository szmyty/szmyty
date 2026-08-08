#!/usr/bin/env python3
"""
Validate data quality for workflow outputs.

This script checks for missing fields, NaN values, and out-of-range metrics.
It logs warnings for data quality issues without causing workflow failures.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.data_quality import validate_data_quality, log_data_quality_summary


def main() -> None:
    """Parse arguments and validate data quality of a JSON file."""
    parser = argparse.ArgumentParser(
        description="Validate data quality for JSON files"
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file to validate"
    )
    parser.add_argument(
        "--required-fields",
        nargs="+",
        help="List of required field names"
    )
    parser.add_argument(
        "--ranges",
        help="JSON string of numeric range constraints (e.g., '{\"score\": {\"min\": 0, \"max\": 100}}')"
    )
    parser.add_argument(
        "--context",
        default="data",
        help="Context description for logging (default: 'data')"
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with error code if validation fails"
    )
    
    args = parser.parse_args()
    
    # Load input file
    try:
        with open(args.input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Parse range constraints if provided
    numeric_ranges = None
    if args.ranges:
        try:
            numeric_ranges = json.loads(args.ranges)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for --ranges: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Validate data quality
    result = validate_data_quality(
        data,
        required_fields=args.required_fields,
        numeric_ranges=numeric_ranges,
        context=args.context
    )
    
    # Log summary
    log_data_quality_summary(result, context=args.context)
    
    # Print summary to stdout
    if result["is_valid"]:
        print(f"✓ Data quality validation passed for {args.input_file}")
    else:
        print(f"⚠️ Data quality issues found in {args.input_file}:")
        
        if result["missing_fields"]:
            print(f"  - Missing fields: {', '.join(result['missing_fields'])}")
        
        if result["nan_fields"]:
            print(f"  - NaN/null fields: {', '.join(result['nan_fields'].keys())}")
        
        if result["out_of_range"]:
            for field, info in result["out_of_range"].items():
                print(f"  - {field} = {info['value']} (expected: [{info['min']}, {info['max']}])")
    
    # Exit with error if validation failed and --fail-on-error specified
    if args.fail_on_error and not result["is_valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
