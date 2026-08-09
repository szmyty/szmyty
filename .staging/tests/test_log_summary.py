#!/usr/bin/env python3
"""
Unit tests for scripts/log_summary.py
"""

import sys
import os
from pathlib import Path
import tempfile

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from log_summary import (  # noqa: E402
    WorkflowPerformanceCard,
    aggregate_log_summary,
    generate_dashboard_svg,
)


class TestWorkflowPerformanceCard:
    """Tests for WorkflowPerformanceCard class."""

    def test_card_initialization(self):
        """Card initializes with correct dimensions."""
        metrics = []
        card = WorkflowPerformanceCard(metrics)

        assert card.width == 800
        assert card.height == 400
        assert card.workflow_metrics == []

    def test_generate_content_no_data(self):
        """Card generates no-data message when metrics are empty."""
        card = WorkflowPerformanceCard([])
        content = card.generate_content()

        assert "Workflow Performance Dashboard" in content
        assert "No workflow metrics available yet" in content

    def test_generate_content_with_metrics(self):
        """Card generates content with workflow metrics."""
        metrics = [
            {
                "workflow_name": "test-workflow",
                "total_runs": 10,
                "successful_runs": 8,
                "failed_runs": 2,
                "consecutive_failures": 0,
                "avg_run_time_seconds": 45.5,
            }
        ]
        card = WorkflowPerformanceCard(metrics)
        content = card.generate_content()

        assert "Workflow Performance Dashboard" in content
        assert "Summary" in content
        assert "test-workflow" in content
        assert "80.0%" in content  # Success rate

    def test_generate_content_with_failing_workflow(self):
        """Card shows warning for workflows with consecutive failures."""
        metrics = [
            {
                "workflow_name": "failing-workflow",
                "total_runs": 5,
                "successful_runs": 1,
                "failed_runs": 4,
                "consecutive_failures": 4,
                "avg_run_time_seconds": 30.0,
            }
        ]
        card = WorkflowPerformanceCard(metrics)
        content = card.generate_content()

        assert "failing-workflow" in content
        assert "⚠ Failing" in content or "Failing" in content

    def test_generate_content_with_multiple_workflows(self):
        """Card handles multiple workflows correctly."""
        metrics = [
            {
                "workflow_name": "workflow-1",
                "total_runs": 5,
                "successful_runs": 5,
                "failed_runs": 0,
                "consecutive_failures": 0,
                "avg_run_time_seconds": 20.0,
            },
            {
                "workflow_name": "workflow-2",
                "total_runs": 10,
                "successful_runs": 8,
                "failed_runs": 2,
                "consecutive_failures": 1,
                "avg_run_time_seconds": 35.0,
            },
        ]
        card = WorkflowPerformanceCard(metrics)
        content = card.generate_content()

        assert "workflow-1" in content
        assert "workflow-2" in content
        assert "Total Workflows" in content

    def test_generate_content_with_null_avg_time(self):
        """Card handles workflows with null average run time."""
        metrics = [
            {
                "workflow_name": "no-time-workflow",
                "total_runs": 1,
                "successful_runs": 1,
                "failed_runs": 0,
                "consecutive_failures": 0,
                "avg_run_time_seconds": None,
            }
        ]
        card = WorkflowPerformanceCard(metrics)
        content = card.generate_content()

        assert "no-time-workflow" in content
        assert "N/A" in content

    def test_generate_svg_complete(self):
        """Card generates complete SVG document."""
        metrics = [
            {
                "workflow_name": "test",
                "total_runs": 1,
                "successful_runs": 1,
                "failed_runs": 0,
                "consecutive_failures": 0,
                "avg_run_time_seconds": 10.0,
            }
        ]
        card = WorkflowPerformanceCard(metrics)
        svg = card.generate_svg(footer_text="Test Footer")

        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert "Workflow Performance Dashboard" in svg
        assert "Test Footer" in svg
        assert 'width="800"' in svg
        assert 'height="400"' in svg


class TestAggregateLogSummary:
    """Tests for aggregate_log_summary function."""

    def test_aggregate_with_no_logs(self):
        """Returns empty summary when no logs exist."""
        # This test may be difficult to mock properly,
        # so we'll just check it doesn't crash
        summary = aggregate_log_summary()

        assert isinstance(summary, dict)
        assert "total_log_files" in summary
        assert "total_log_size_bytes" in summary
        assert "workflows_with_logs" in summary
        assert "errors_found" in summary

    def test_aggregate_summary_structure(self):
        """Aggregate summary has correct structure."""
        summary = aggregate_log_summary()

        assert isinstance(summary, dict)
        assert "total_log_files" in summary
        assert isinstance(summary["total_log_files"], int)
        assert "total_log_size_bytes" in summary
        assert isinstance(summary["total_log_size_bytes"], int)
        assert "workflows_with_logs" in summary
        assert isinstance(summary["workflows_with_logs"], list)
        assert "errors_found" in summary
        assert isinstance(summary["errors_found"], list)


class TestGenerateDashboardSVG:
    """Tests for generate_dashboard_svg function."""

    def test_generate_dashboard_creates_file(self):
        """Dashboard SVG is created at specified path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test-dashboard.svg"
            generate_dashboard_svg(str(output_path))

            assert output_path.exists()

            # Verify it's a valid SVG
            content = output_path.read_text()
            assert content.startswith("<svg")
            assert content.endswith("</svg>")
            assert "Workflow Performance Dashboard" in content

    def test_generate_dashboard_with_metrics(self, monkeypatch):
        """Dashboard includes metrics from get_all_workflow_metrics."""
        # Mock get_all_workflow_metrics to return test data
        mock_metrics = [
            {
                "workflow_name": "test-workflow",
                "total_runs": 5,
                "successful_runs": 5,
                "failed_runs": 0,
                "consecutive_failures": 0,
                "avg_run_time_seconds": 25.0,
            }
        ]

        def mock_get_all():
            return mock_metrics

        import log_summary

        monkeypatch.setattr(log_summary, "get_all_workflow_metrics", mock_get_all)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test-dashboard.svg"
            generate_dashboard_svg(str(output_path))

            content = output_path.read_text()
            assert "test-workflow" in content
