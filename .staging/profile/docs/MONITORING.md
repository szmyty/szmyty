# Monitoring, Observability, and Alerts

This document describes the monitoring and observability features implemented in the profile repository.

## Overview

The monitoring system provides:

1. **Workflow Metrics Tracking** - Record and analyze workflow execution metrics
2. **Status Page** - Visual dashboard showing system health
3. **Automated Alerts** - Automatic issue creation for repeated failures
4. **Data Quality Checks** - Validation and logging of data quality issues

## Features

### 1. Workflow Metrics Tracking

Each workflow execution is tracked with the following metrics:

- **Run Time**: Duration of workflow execution in seconds
- **Success/Failure Status**: Whether the workflow completed successfully
- **Consecutive Failures**: Count of consecutive failed runs
- **Success Rate**: Percentage of successful runs
- **API Call Counts**: Number of calls to external APIs
- **Run History**: Last 20 workflow executions with timestamps

#### Recording Metrics

Workflows can record metrics using the `record-workflow-metrics.py` script:

```bash
# Record a successful run
python scripts/record-workflow-metrics.py oura --success --run-time 120.5

# Record a failed run
python scripts/record-workflow-metrics.py oura --failure --error-message "API timeout"

# Include API call counts
python scripts/record-workflow-metrics.py weather --success --run-time 45.2 \
  --api-calls '{"openweather": 2, "geocoding": 1}'
```

#### Metrics Storage

Metrics are stored as JSON files in `data/metrics/`:

```
data/metrics/
├── oura.json
├── weather.json
├── developer.json
└── ...
```

Each metrics file contains:

```json
{
  "workflow_name": "oura",
  "total_runs": 10,
  "successful_runs": 9,
  "failed_runs": 1,
  "consecutive_failures": 0,
  "last_success": "2025-12-03T12:00:00Z",
  "last_failure": "2025-12-02T10:00:00Z",
  "last_run_time_seconds": 120.5,
  "avg_run_time_seconds": 115.3,
  "api_calls": {
    "oura": 15,
    "github": 5
  },
  "run_history": [...]
}
```

### 2. Status Page

The status page provides a visual dashboard showing the health of all workflows.

#### Generating the Status Page

```bash
python scripts/generate-status-page.py data/status/status-page.svg
```

The status page displays:

- **Status Indicator**: Green (success), yellow (warning), or red (error)
- **Workflow Name**: Name of each monitored workflow
- **Last Success**: Time since last successful run
- **Last Failure**: Time since last failure (with consecutive count)
- **Success Rate**: Percentage of successful runs

#### Status Determination

- **Success** (🟢): No recent failures
- **Warning** (🟡): 1-2 consecutive failures
- **Error** (🔴): 3+ consecutive failures

### 3. Automated Alerts

The monitoring workflow automatically creates GitHub Issues when a workflow has 3 or more consecutive failures.

#### Alert Workflow

The `.github/workflows/monitoring.yml` workflow:

1. Runs on a schedule (hourly)
2. Checks metrics for all workflows
3. Creates an issue if consecutive failures ≥ 3
4. Includes detailed metrics and run history in the issue

#### Issue Content

Automatically created issues include:

- Current metrics (consecutive failures, success rate)
- Recent run history (last 5 runs)
- Recommended actions for investigation
- Links to workflow runs

#### Preventing Duplicate Issues

The system checks for existing open issues before creating new ones, preventing duplicate alerts for the same workflow.

### 4. Data Quality Checks

Data quality validation helps ensure workflow outputs meet expected standards.

#### Using Data Quality Checks

```bash
# Basic validation
python scripts/validate-data-quality.py data.json \
  --required-fields name score value \
  --context "oura metrics"

# With range validation
python scripts/validate-data-quality.py oura/metrics.json \
  --required-fields sleep_score readiness_score \
  --ranges '{"sleep_score": {"min": 0, "max": 100}}' \
  --context "oura health data"
```

#### Validation Checks

1. **Missing Fields**: Detects required fields that are absent
2. **NaN/Null Values**: Identifies invalid numeric values
3. **Range Validation**: Checks if values are within expected bounds

#### Logging

Data quality issues are logged to stderr with warnings:

```
⚠️ DATA_QUALITY: Missing required field 'score' in oura health data
⚠️ DATA_QUALITY: NaN value in field 'readiness' in weather data
⚠️ DATA_QUALITY: Value 150 in field 'score' is above maximum 100 in metrics
```

## Integration with Workflows

### Example: Adding Metrics to a Workflow

```yaml
- name: Fetch Oura Data
  id: fetch
  run: |
    START_TIME=$(date +%s)
    
    if scripts/fetch-oura.sh > oura/metrics.json; then
      END_TIME=$(date +%s)
      RUN_TIME=$((END_TIME - START_TIME))
      
      python scripts/record-workflow-metrics.py oura \
        --success \
        --run-time $RUN_TIME \
        --api-calls '{"oura": 3}'
    else
      END_TIME=$(date +%s)
      RUN_TIME=$((END_TIME - START_TIME))
      
      python scripts/record-workflow-metrics.py oura \
        --failure \
        --run-time $RUN_TIME \
        --error-message "Failed to fetch Oura data"
      
      exit 1
    fi

- name: Validate Data Quality
  if: success()
  run: |
    python scripts/validate-data-quality.py oura/metrics.json \
      --required-fields sleep_score readiness_score activity_score \
      --ranges '{"sleep_score": {"min": 0, "max": 100}, "readiness_score": {"min": 0, "max": 100}}' \
      --context "Oura health metrics"
```

## API Reference

### Metrics Module (`lib/metrics.py`)

#### `record_workflow_run(workflow_name, success, run_time_seconds=None, api_calls=None, error_message=None)`

Record a workflow execution and update metrics.

**Parameters:**
- `workflow_name` (str): Name of the workflow
- `success` (bool): Whether the run was successful
- `run_time_seconds` (float, optional): Duration in seconds
- `api_calls` (dict, optional): API endpoint call counts
- `error_message` (str, optional): Error message if failed

**Returns:** Updated metrics dictionary

#### `check_failure_threshold(workflow_name, threshold=3)`

Check if consecutive failures exceed threshold.

**Returns:** `True` if threshold exceeded, `False` otherwise

### Data Quality Module (`lib/data_quality.py`)

#### `validate_data_quality(data, required_fields=None, numeric_ranges=None, context="data")`

Perform comprehensive data quality validation.

**Parameters:**
- `data` (dict): Data dictionary to validate
- `required_fields` (list, optional): Required field names
- `numeric_ranges` (dict, optional): Range specifications for numeric fields
- `context` (str): Description for logging

**Returns:** Validation results dictionary with:
- `is_valid` (bool): Overall validation status
- `missing_fields` (list): Missing required fields
- `nan_fields` (dict): Fields with NaN values
- `out_of_range` (dict): Fields with out-of-range values

## Monitoring Workflow

The monitoring workflow (`.github/workflows/monitoring.yml`) runs automatically:

- **Schedule**: Every hour
- **Triggers**: After any workflow completion
- **Actions**:
  1. Generate updated status page
  2. Check for consecutive failures
  3. Create issues for repeated failures
  4. Commit metrics and status page

## Best Practices

### 1. Record Metrics for All Workflows

Add metrics recording to every workflow to enable comprehensive monitoring:

```yaml
- name: Record Success
  if: success()
  run: python scripts/record-workflow-metrics.py <workflow-name> --success

- name: Record Failure
  if: failure()
  run: python scripts/record-workflow-metrics.py <workflow-name> --failure
```

### 2. Validate Critical Data

Add data quality checks for important workflow outputs:

```yaml
- name: Validate Output
  run: |
    python scripts/validate-data-quality.py output.json \
      --required-fields <fields> \
      --context "<workflow> output"
```

### 3. Monitor the Status Page

Include the status page in your README or documentation to provide visibility into system health.

### 4. Respond to Automated Issues

When an automated issue is created:

1. Review the workflow runs linked in the issue
2. Check for recent changes to the workflow or dependencies
3. Verify external service status (APIs, secrets)
4. Fix the underlying issue
5. Close the issue once resolved

## Troubleshooting

### Metrics Not Recording

**Problem**: Metrics are not being recorded for a workflow.

**Solution**: 
- Ensure `record-workflow-metrics.py` is called in the workflow
- Check that the script has execute permissions
- Verify the workflow has `contents: write` permission

### Status Page Not Updating

**Problem**: Status page shows outdated information.

**Solution**:
- Check that the monitoring workflow is running on schedule
- Verify metrics files exist in `data/metrics/`
- Ensure the workflow can commit changes to the repository

### False Positive Alerts

**Problem**: Issues are created for transient failures.

**Solution**:
- The threshold is set to 3 consecutive failures by default
- Adjust the threshold in `monitoring.yml` if needed
- Implement retry logic in workflows for transient errors

## Future Enhancements

Potential improvements to the monitoring system:

- [ ] Metrics aggregation and trending over time
- [ ] Slack/email notifications for failures
- [ ] Performance dashboards with charts
- [ ] Anomaly detection for unusual patterns
- [ ] Custom alerting rules per workflow
- [ ] Integration with external monitoring tools

## Related Documentation

- [Workflows Guide](WORKFLOWS.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Optimization Guide](OPTIMIZATION_GUIDE.md)
- [Development Guide](../README.md#development)
