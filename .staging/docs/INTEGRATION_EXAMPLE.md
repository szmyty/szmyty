# Monitoring Integration Example

This document shows how to integrate monitoring features into your GitHub Actions workflows.

## Complete Example Workflow

Here's a complete example showing all monitoring features integrated into a workflow:

```yaml
name: Example Workflow with Monitoring

on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  fetch-and-generate:
    runs-on: ubuntu-latest
    steps:
      - name: Setup environment
        uses: ./.github/actions/setup-environment

      # Track workflow start time
      - name: Record start time
        id: start
        run: echo "start_time=$(date +%s)" >> $GITHUB_OUTPUT

      # Fetch data with error handling
      - name: Fetch data
        id: fetch
        continue-on-error: true
        run: |
          if scripts/fetch-data.sh > data/output.json; then
            echo "success=true" >> $GITHUB_OUTPUT
          else
            echo "success=false" >> $GITHUB_OUTPUT
            echo "error=Failed to fetch data" >> $GITHUB_OUTPUT
          fi

      # Validate data quality
      - name: Validate data quality
        if: steps.fetch.outputs.success == 'true'
        continue-on-error: true
        run: |
          python scripts/validate-data-quality.py data/output.json \
            --required-fields field1 field2 field3 \
            --ranges '{"score": {"min": 0, "max": 100}}' \
            --context "example workflow output"

      # Generate output
      - name: Generate card
        if: steps.fetch.outputs.success == 'true'
        continue-on-error: true
        run: |
          if python scripts/generate-card.py data/output.json output.svg; then
            echo "card_success=true" >> $GITHUB_OUTPUT
          else
            echo "card_success=false" >> $GITHUB_OUTPUT
          fi

      # Calculate run time
      - name: Calculate run time
        id: timing
        if: always()
        run: |
          END_TIME=$(date +%s)
          START_TIME=${{ steps.start.outputs.start_time }}
          RUN_TIME=$((END_TIME - START_TIME))
          echo "run_time=$RUN_TIME" >> $GITHUB_OUTPUT

      # Record successful run metrics
      - name: Record success metrics
        if: steps.fetch.outputs.success == 'true'
        run: |
          python scripts/record-workflow-metrics.py example-workflow \
            --success \
            --run-time ${{ steps.timing.outputs.run_time }} \
            --api-calls '{"example_api": 3}'

      # Record failure metrics
      - name: Record failure metrics
        if: steps.fetch.outputs.success != 'true'
        run: |
          ERROR_MSG="${{ steps.fetch.outputs.error }}"
          python scripts/record-workflow-metrics.py example-workflow \
            --failure \
            --run-time ${{ steps.timing.outputs.run_time }} \
            --error-message "$ERROR_MSG"

      # Commit changes if successful
      - name: Commit changes
        if: steps.fetch.outputs.success == 'true'
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          
          git add data/output.json output.svg data/metrics/example-workflow.json
          
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "🔄 Update example workflow output"
            git push
          fi
```

## Step-by-Step Integration

### 1. Track Workflow Timing

Add timing tracking at the start and end of your workflow:

```yaml
- name: Record start time
  id: start
  run: echo "start_time=$(date +%s)" >> $GITHUB_OUTPUT

# ... your workflow steps ...

- name: Calculate run time
  id: timing
  if: always()
  run: |
    END_TIME=$(date +%s)
    START_TIME=${{ steps.start.outputs.start_time }}
    RUN_TIME=$((END_TIME - START_TIME))
    echo "run_time=$RUN_TIME" >> $GITHUB_OUTPUT
```

### 2. Add Data Quality Validation

After fetching data, validate its quality:

```yaml
- name: Validate data quality
  if: steps.fetch.outputs.success == 'true'
  continue-on-error: true
  run: |
    python scripts/validate-data-quality.py data/output.json \
      --required-fields timestamp value status \
      --ranges '{"temperature": {"min": -50, "max": 50}}' \
      --context "weather data"
```

### 3. Record Success Metrics

When your workflow succeeds, record the metrics:

```yaml
- name: Record success metrics
  if: success()
  run: |
    python scripts/record-workflow-metrics.py my-workflow \
      --success \
      --run-time ${{ steps.timing.outputs.run_time }} \
      --api-calls '{"api_name": 2, "other_api": 1}'
```

### 4. Record Failure Metrics

When your workflow fails, record the failure:

```yaml
- name: Record failure metrics
  if: failure()
  run: |
    python scripts/record-workflow-metrics.py my-workflow \
      --failure \
      --run-time ${{ steps.timing.outputs.run_time }} \
      --error-message "Workflow failed at step X"
```

### 5. Commit Metrics Files

Include metrics files in your commits:

```yaml
- name: Commit changes
  run: |
    git config --local user.email "github-actions[bot]@users.noreply.github.com"
    git config --local user.name "github-actions[bot]"
    
    # Include metrics file
    git add data/output.json data/metrics/my-workflow.json
    
    if git diff --staged --quiet; then
      echo "No changes to commit"
    else
      git commit -m "🔄 Update workflow output"
      git push
    fi
```

## Simplified Integration Pattern

For a simpler integration, wrap your main workflow logic:

```yaml
- name: Main workflow logic
  id: main
  run: |
    START_TIME=$(date +%s)
    
    # Your workflow logic here
    if scripts/your-workflow.sh; then
      SUCCESS=true
      ERROR=""
    else
      SUCCESS=false
      ERROR="Workflow failed"
    fi
    
    END_TIME=$(date +%s)
    RUN_TIME=$((END_TIME - START_TIME))
    
    # Record metrics
    if [ "$SUCCESS" = true ]; then
      python scripts/record-workflow-metrics.py my-workflow \
        --success --run-time $RUN_TIME
    else
      python scripts/record-workflow-metrics.py my-workflow \
        --failure --run-time $RUN_TIME --error-message "$ERROR"
      exit 1
    fi
```

## Data Quality Validation Patterns

### Pattern 1: Basic Required Fields

```yaml
- name: Validate required fields
  run: |
    python scripts/validate-data-quality.py data.json \
      --required-fields name timestamp value \
      --context "API response"
```

### Pattern 2: Numeric Range Validation

```yaml
- name: Validate ranges
  run: |
    python scripts/validate-data-quality.py metrics.json \
      --required-fields score readiness activity \
      --ranges '{
        "score": {"min": 0, "max": 100},
        "readiness": {"min": 0, "max": 100},
        "activity": {"min": 0, "max": 100}
      }' \
      --context "health metrics"
```

### Pattern 3: Fail on Validation Errors

```yaml
- name: Validate with hard failure
  run: |
    python scripts/validate-data-quality.py data.json \
      --required-fields critical_field \
      --fail-on-error \
      --context "critical data"
```

## API Call Tracking

Track API calls for better observability:

```yaml
- name: Fetch data from multiple APIs
  id: fetch
  run: |
    GITHUB_CALLS=0
    OURA_CALLS=0
    WEATHER_CALLS=0
    
    # Track API calls
    curl -s https://api.github.com/... && ((GITHUB_CALLS++))
    curl -s https://api.ouraring.com/... && ((OURA_CALLS++))
    curl -s https://api.openweathermap.org/... && ((WEATHER_CALLS++))
    
    echo "api_calls={\"github\": $GITHUB_CALLS, \"oura\": $OURA_CALLS, \"weather\": $WEATHER_CALLS}" >> $GITHUB_OUTPUT

- name: Record metrics with API calls
  run: |
    python scripts/record-workflow-metrics.py my-workflow \
      --success \
      --api-calls '${{ steps.fetch.outputs.api_calls }}'
```

## Monitoring Dashboard Integration

Include the status page in your README:

```markdown
## System Status

<!-- STATUS-PAGE:START -->
![System Status](./data/status/status-page.svg)
<!-- STATUS-PAGE:END -->
```

Then have the monitoring workflow update it:

```yaml
- name: Update README with status
  run: |
    python scripts/update-readme.py \
      --marker STATUS-PAGE \
      --content "![System Status](./data/status/status-page.svg)"
```

## Best Practices

1. **Always use `if: always()`** when recording metrics to ensure they're captured even on failure
2. **Track timing** for all workflows to identify performance issues
3. **Validate critical data** to catch issues early
4. **Use meaningful context strings** to make logs easier to understand
5. **Include metrics files in commits** to maintain history
6. **Set up the monitoring workflow** to automatically check for failures

## Troubleshooting

### Metrics not recording on failure

Make sure to use `if: always()` or `if: failure()` for the metrics recording step:

```yaml
- name: Record metrics
  if: always()  # This ensures it runs even on failure
  run: python scripts/record-workflow-metrics.py ...
```

### Permission denied errors

Ensure your workflow has the necessary permissions:

```yaml
permissions:
  contents: write  # Required to commit metrics
  issues: write    # Required for automated issue creation (monitoring workflow)
```

### Data quality checks too strict

Use `continue-on-error: true` for validation steps that should warn but not fail:

```yaml
- name: Validate data
  continue-on-error: true  # Log warnings but don't fail workflow
  run: python scripts/validate-data-quality.py ...
```

## See Also

- [Monitoring Guide](MONITORING.md) - Complete monitoring documentation
- [Workflows Guide](WORKFLOWS.md) - Workflow architecture documentation
- [Optimization Guide](OPTIMIZATION_GUIDE.md) - Performance optimization strategies
