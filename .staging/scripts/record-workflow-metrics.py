#!/usr/bin/env python3
"""
Record workflow execution metrics.

This script is called by workflows to record execution metrics including
success/failure status, run time, and any error messages.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.metrics import record_workflow_run


def main() -> None:
    """Parse arguments and record workflow execution metrics."""
    parser = argparse.ArgumentParser(
        description="Record workflow execution metrics"
    )
    parser.add_argument(
        "workflow_name",
        help="Name of the workflow (e.g., 'oura', 'weather', 'developer')"
    )
    parser.add_argument(
        "--success",
        action="store_true",
        help="Mark the workflow run as successful"
    )
    parser.add_argument(
        "--failure",
        action="store_true",
        help="Mark the workflow run as failed"
    )
    parser.add_argument(
        "--run-time",
        type=float,
        help="Duration of the workflow run in seconds"
    )
    parser.add_argument(
        "--api-calls",
        help="JSON string of API endpoint call counts (e.g., '{\"oura\": 3, \"github\": 2}')"
    )
    parser.add_argument(
        "--error-message",
        help="Error message if the run failed"
    )
    
    args = parser.parse_args()
    
    # Validate success/failure flags
    if args.success and args.failure:
        print("Error: Cannot specify both --success and --failure", file=sys.stderr)
        sys.exit(1)
    
    if not args.success and not args.failure:
        print("Error: Must specify either --success or --failure", file=sys.stderr)
        sys.exit(1)
    
    success = args.success
    
    # Parse API calls if provided
    api_calls = None
    if args.api_calls:
        import json
        try:
            api_calls = json.loads(args.api_calls)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for --api-calls: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Record the workflow run
    metrics = record_workflow_run(
        workflow_name=args.workflow_name,
        success=success,
        run_time_seconds=args.run_time,
        api_calls=api_calls,
        error_message=args.error_message
    )
    
    # Print summary
    print(f"Metrics recorded for {args.workflow_name}:")
    print(f"  Status: {'✓ Success' if success else '✗ Failure'}")
    print(f"  Total runs: {metrics['total_runs']}")
    print(f"  Success rate: {metrics['successful_runs']}/{metrics['total_runs']} ({metrics['successful_runs']/metrics['total_runs']*100:.1f}%)")
    print(f"  Consecutive failures: {metrics['consecutive_failures']}")
    
    if args.run_time:
        print(f"  Run time: {args.run_time:.2f}s")
        if metrics['avg_run_time_seconds']:
            print(f"  Avg run time: {metrics['avg_run_time_seconds']:.2f}s")
    
    # Exit with failure code if consecutive failures >= 3
    if metrics['consecutive_failures'] >= 3:
        print(f"\n⚠️ WARNING: {metrics['consecutive_failures']} consecutive failures detected!")
        print("Consider investigating this workflow.")


if __name__ == "__main__":
    main()
