#!/usr/bin/env python3
"""
Unit tests for scripts/lib/metrics.py
"""

import json
import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from lib.metrics import (
    record_workflow_run,
    load_workflow_metrics,
    save_workflow_metrics,
    check_failure_threshold,
    reset_failure_count,
    get_all_workflow_metrics,
)


@pytest.fixture
def temp_metrics_dir(monkeypatch):
    """Create a temporary metrics directory for testing."""
    temp_dir = tempfile.mkdtemp()
    metrics_dir = Path(temp_dir) / "data" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    
    # Patch the get_metrics_dir function to use temp directory
    def mock_get_metrics_dir():
        return metrics_dir
    
    monkeypatch.setattr('lib.metrics.get_metrics_dir', mock_get_metrics_dir)
    
    yield metrics_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestLoadWorkflowMetrics:
    """Tests for load_workflow_metrics function."""
    
    def test_load_nonexistent_metrics(self, temp_metrics_dir):
        """Loading metrics for a workflow that doesn't exist returns empty structure."""
        metrics = load_workflow_metrics("test_workflow")
        
        assert metrics["workflow_name"] == "test_workflow"
        assert metrics["total_runs"] == 0
        assert metrics["successful_runs"] == 0
        assert metrics["failed_runs"] == 0
        assert metrics["consecutive_failures"] == 0
        assert metrics["last_success"] is None
        assert metrics["last_failure"] is None
        assert metrics["run_history"] == []
    
    def test_load_existing_metrics(self, temp_metrics_dir):
        """Loading existing metrics returns correct data."""
        # Create a metrics file
        test_metrics = {
            "workflow_name": "test_workflow",
            "total_runs": 5,
            "successful_runs": 4,
            "failed_runs": 1,
            "consecutive_failures": 0,
            "last_success": "2025-12-03T12:00:00Z",
            "last_failure": "2025-12-03T10:00:00Z",
            "run_history": []
        }
        
        metrics_file = temp_metrics_dir / "test_workflow.json"
        with open(metrics_file, 'w') as f:
            json.dump(test_metrics, f)
        
        metrics = load_workflow_metrics("test_workflow")
        
        assert metrics["workflow_name"] == "test_workflow"
        assert metrics["total_runs"] == 5
        assert metrics["successful_runs"] == 4
        assert metrics["consecutive_failures"] == 0


class TestRecordWorkflowRun:
    """Tests for record_workflow_run function."""
    
    def test_record_successful_run(self, temp_metrics_dir):
        """Recording a successful run updates metrics correctly."""
        metrics = record_workflow_run(
            workflow_name="test_workflow",
            success=True,
            run_time_seconds=120.5
        )
        
        assert metrics["total_runs"] == 1
        assert metrics["successful_runs"] == 1
        assert metrics["failed_runs"] == 0
        assert metrics["consecutive_failures"] == 0
        assert metrics["last_success"] is not None
        assert metrics["last_run_time_seconds"] == 120.5
        assert len(metrics["run_history"]) == 1
        assert metrics["run_history"][0]["success"] is True
    
    def test_record_failed_run(self, temp_metrics_dir):
        """Recording a failed run updates metrics correctly."""
        metrics = record_workflow_run(
            workflow_name="test_workflow",
            success=False,
            error_message="Test error"
        )
        
        assert metrics["total_runs"] == 1
        assert metrics["successful_runs"] == 0
        assert metrics["failed_runs"] == 1
        assert metrics["consecutive_failures"] == 1
        assert metrics["last_failure"] is not None
        assert len(metrics["run_history"]) == 1
        assert metrics["run_history"][0]["success"] is False
        assert metrics["run_history"][0]["error_message"] == "Test error"
    
    def test_consecutive_failures_increment(self, temp_metrics_dir):
        """Consecutive failures counter increments on repeated failures."""
        # First failure
        metrics = record_workflow_run("test_workflow", success=False)
        assert metrics["consecutive_failures"] == 1
        
        # Second failure
        metrics = record_workflow_run("test_workflow", success=False)
        assert metrics["consecutive_failures"] == 2
        
        # Third failure
        metrics = record_workflow_run("test_workflow", success=False)
        assert metrics["consecutive_failures"] == 3
    
    def test_consecutive_failures_reset_on_success(self, temp_metrics_dir):
        """Consecutive failures reset to 0 on successful run."""
        # Record failures
        record_workflow_run("test_workflow", success=False)
        record_workflow_run("test_workflow", success=False)
        
        # Record success
        metrics = record_workflow_run("test_workflow", success=True)
        
        assert metrics["consecutive_failures"] == 0
        assert metrics["successful_runs"] == 1
        assert metrics["failed_runs"] == 2
    
    def test_run_time_average_calculation(self, temp_metrics_dir):
        """Average run time is calculated correctly."""
        # First run
        metrics = record_workflow_run("test_workflow", success=True, run_time_seconds=100)
        assert metrics["avg_run_time_seconds"] == 100
        
        # Second run - should update average
        metrics = record_workflow_run("test_workflow", success=True, run_time_seconds=200)
        # Using exponential moving average with alpha=0.2
        expected_avg = 0.2 * 200 + 0.8 * 100
        assert abs(metrics["avg_run_time_seconds"] - expected_avg) < 0.01
    
    def test_api_calls_tracking(self, temp_metrics_dir):
        """API calls are tracked correctly."""
        # First run
        metrics = record_workflow_run(
            "test_workflow",
            success=True,
            api_calls={"github": 2, "oura": 1}
        )
        assert metrics["api_calls"]["github"] == 2
        assert metrics["api_calls"]["oura"] == 1
        
        # Second run
        metrics = record_workflow_run(
            "test_workflow",
            success=True,
            api_calls={"github": 1, "weather": 3}
        )
        assert metrics["api_calls"]["github"] == 3  # 2 + 1
        assert metrics["api_calls"]["oura"] == 1    # unchanged
        assert metrics["api_calls"]["weather"] == 3  # new
    
    def test_run_history_limit(self, temp_metrics_dir):
        """Run history is limited to last 20 runs."""
        # Record 25 runs
        for i in range(25):
            record_workflow_run("test_workflow", success=True)
        
        metrics = load_workflow_metrics("test_workflow")
        assert len(metrics["run_history"]) == 20


class TestCheckFailureThreshold:
    """Tests for check_failure_threshold function."""
    
    def test_threshold_not_exceeded(self, temp_metrics_dir):
        """Returns False when threshold not exceeded."""
        record_workflow_run("test_workflow", success=False)
        record_workflow_run("test_workflow", success=False)
        
        assert check_failure_threshold("test_workflow", threshold=3) is False
    
    def test_threshold_exceeded(self, temp_metrics_dir):
        """Returns True when threshold exceeded."""
        for _ in range(3):
            record_workflow_run("test_workflow", success=False)
        
        assert check_failure_threshold("test_workflow", threshold=3) is True
    
    def test_custom_threshold(self, temp_metrics_dir):
        """Works with custom threshold values."""
        record_workflow_run("test_workflow", success=False)
        
        assert check_failure_threshold("test_workflow", threshold=1) is True
        assert check_failure_threshold("test_workflow", threshold=2) is False


class TestResetFailureCount:
    """Tests for reset_failure_count function."""
    
    def test_reset_failure_count(self, temp_metrics_dir):
        """Failure count is reset to 0."""
        # Record failures
        for _ in range(3):
            record_workflow_run("test_workflow", success=False)
        
        # Reset
        reset_failure_count("test_workflow")
        
        metrics = load_workflow_metrics("test_workflow")
        assert metrics["consecutive_failures"] == 0


class TestGetAllWorkflowMetrics:
    """Tests for get_all_workflow_metrics function."""
    
    def test_get_all_metrics_empty(self, temp_metrics_dir):
        """Returns empty list when no metrics exist."""
        all_metrics = get_all_workflow_metrics()
        assert all_metrics == []
    
    def test_get_all_metrics_multiple_workflows(self, temp_metrics_dir):
        """Returns all workflow metrics."""
        # Record runs for multiple workflows
        record_workflow_run("workflow1", success=True)
        record_workflow_run("workflow2", success=True)
        record_workflow_run("workflow3", success=False)
        
        all_metrics = get_all_workflow_metrics()
        
        assert len(all_metrics) == 3
        workflow_names = [m["workflow_name"] for m in all_metrics]
        assert "workflow1" in workflow_names
        assert "workflow2" in workflow_names
        assert "workflow3" in workflow_names
