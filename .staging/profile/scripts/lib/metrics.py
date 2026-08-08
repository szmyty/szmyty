#!/usr/bin/env python3
"""
Workflow metrics tracking module for monitoring and observability.

This module provides utilities to track workflow execution metrics including:
- Workflow run times
- Success/failure rates
- API call counts
- Timestamps for successful updates and failures
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, List


def get_metrics_dir() -> Path:
    """Get the metrics data directory path."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    metrics_dir = Path(repo_root) / "data" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    return metrics_dir


def get_workflow_metrics_file(workflow_name: str) -> Path:
    """Get the metrics file path for a specific workflow."""
    metrics_dir = get_metrics_dir()
    return metrics_dir / f"{workflow_name}.json"


def load_workflow_metrics(workflow_name: str) -> Dict:
    """
    Load existing metrics for a workflow.
    
    Args:
        workflow_name: Name of the workflow (e.g., 'oura', 'weather', 'developer')
    
    Returns:
        Dictionary containing workflow metrics or empty structure if not found
    """
    metrics_file = get_workflow_metrics_file(workflow_name)
    
    if not metrics_file.exists():
        return {
            "workflow_name": workflow_name,
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "consecutive_failures": 0,
            "last_success": None,
            "last_failure": None,
            "last_run_time_seconds": None,
            "avg_run_time_seconds": None,
            "api_calls": {},
            "run_history": []
        }
    
    try:
        with open(metrics_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load metrics for {workflow_name}: {e}", file=sys.stderr)
        return {
            "workflow_name": workflow_name,
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "consecutive_failures": 0,
            "last_success": None,
            "last_failure": None,
            "last_run_time_seconds": None,
            "avg_run_time_seconds": None,
            "api_calls": {},
            "run_history": []
        }


def save_workflow_metrics(workflow_name: str, metrics: Dict) -> None:
    """
    Save workflow metrics to file using safe write pattern.
    
    Args:
        workflow_name: Name of the workflow
        metrics: Dictionary containing workflow metrics
    """
    metrics_file = get_workflow_metrics_file(workflow_name)
    temp_file = metrics_file.parent / f"{metrics_file.name}.tmp"
    
    try:
        # Write to temporary file
        with open(temp_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Validate the temp file can be loaded
        with open(temp_file, 'r') as f:
            json.load(f)
        
        # Atomic move to final location
        temp_file.replace(metrics_file)
        
    except (IOError, OSError, json.JSONDecodeError) as e:
        # Clean up temp file on failure (missing_ok=True available in Python 3.8+)
        temp_file.unlink(missing_ok=True)
        print(f"Error: Failed to save metrics for {workflow_name}: {e}", file=sys.stderr)
        sys.exit(1)


def record_workflow_run(
    workflow_name: str,
    success: bool,
    run_time_seconds: Optional[float] = None,
    api_calls: Optional[Dict[str, int]] = None,
    error_message: Optional[str] = None
) -> Dict:
    """
    Record a workflow run and update metrics.
    
    Args:
        workflow_name: Name of the workflow
        success: Whether the workflow run was successful
        run_time_seconds: Duration of the workflow run in seconds
        api_calls: Dictionary of API endpoint names and call counts
        error_message: Error message if the run failed
    
    Returns:
        Updated metrics dictionary
    """
    metrics = load_workflow_metrics(workflow_name)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Update counters
    metrics["total_runs"] += 1
    
    if success:
        metrics["successful_runs"] += 1
        metrics["consecutive_failures"] = 0
        metrics["last_success"] = timestamp
    else:
        metrics["failed_runs"] += 1
        metrics["consecutive_failures"] += 1
        metrics["last_failure"] = timestamp
    
    # Update run time metrics
    if run_time_seconds is not None:
        metrics["last_run_time_seconds"] = run_time_seconds
        
        # Calculate moving average (last 10 runs)
        if metrics["avg_run_time_seconds"] is None:
            metrics["avg_run_time_seconds"] = run_time_seconds
        else:
            # Simple exponential moving average
            alpha = 0.2  # Weight for new value
            metrics["avg_run_time_seconds"] = (
                alpha * run_time_seconds + 
                (1 - alpha) * metrics["avg_run_time_seconds"]
            )
    
    # Update API call metrics
    if api_calls:
        for endpoint, count in api_calls.items():
            if endpoint not in metrics["api_calls"]:
                metrics["api_calls"][endpoint] = 0
            metrics["api_calls"][endpoint] += count
    
    # Add to run history (keep last 20 runs)
    run_record = {
        "timestamp": timestamp,
        "success": success,
        "run_time_seconds": run_time_seconds,
        "error_message": error_message
    }
    
    metrics["run_history"].append(run_record)
    if len(metrics["run_history"]) > 20:
        metrics["run_history"] = metrics["run_history"][-20:]
    
    # Save updated metrics
    save_workflow_metrics(workflow_name, metrics)
    
    return metrics


def get_all_workflow_metrics() -> List[Dict]:
    """
    Load metrics for all workflows.
    
    Returns:
        List of metrics dictionaries for all workflows
    """
    metrics_dir = get_metrics_dir()
    all_metrics = []
    
    for metrics_file in metrics_dir.glob("*.json"):
        try:
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
                all_metrics.append(metrics)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load {metrics_file}: {e}", file=sys.stderr)
    
    return all_metrics


def check_failure_threshold(workflow_name: str, threshold: int = 3) -> bool:
    """
    Check if a workflow has exceeded the failure threshold.
    
    Args:
        workflow_name: Name of the workflow
        threshold: Number of consecutive failures to trigger alert (default: 3)
    
    Returns:
        True if consecutive failures >= threshold, False otherwise
    """
    metrics = load_workflow_metrics(workflow_name)
    return metrics.get("consecutive_failures", 0) >= threshold


def reset_failure_count(workflow_name: str) -> None:
    """
    Reset the consecutive failure count for a workflow.
    
    Args:
        workflow_name: Name of the workflow
    """
    metrics = load_workflow_metrics(workflow_name)
    metrics["consecutive_failures"] = 0
    save_workflow_metrics(workflow_name, metrics)
