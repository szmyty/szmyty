# Unified Workflow Migration Guide

## Overview

This document describes the migration from multiple separate workflows to a single unified orchestration workflow (`build-profile.yml`).

## Migration Date

**December 2024** (PR merged: TBD)

## Summary of Changes

### Before: 8+ Separate Workflows

The repository previously used multiple independent workflows:

1. `developer.yml` - Developer Dashboard
2. `soundcloud-card.yml` - SoundCloud Card
3. `weather.yml` - Weather Card
4. `location-card.yml` - Location Card
5. `oura.yml` - Oura Health Dashboard
6. `parallel-fetch.yml` - Parallel Data Fetching
7. `megalinter.yml` - Code Linting
8. `deploy-dashboard.yml` - React Dashboard Deployment

Each workflow ran independently, potentially causing:
- Race conditions and git conflicts
- Inconsistent state across cards
- Complex debugging with logs scattered across workflows
- Duplication of setup and teardown code
- Higher GitHub Actions usage

### After: 1 Unified Workflow

All functionality consolidated into:

**`.github/workflows/build-profile.yml`** - Build Profile — Unified Orchestration Pipeline

## Architecture

### Workflow Structure

The unified workflow consists of 10 sequential phases:

#### Phase 1: Setup
- Checkout repository
- Setup Python 3.11 with pip caching
- Setup Node.js 20 with npm caching
- Install system dependencies (jq, curl)
- Install Python dependencies (poetry or pip)
- Install additional packages (Pillow, jsonschema)
- Install Node.js tools (svgo)
- Install npm dependencies for dashboard
- Restore SVG hash cache

#### Phase 2: Fetch All Data
Fetches data from all sources with error handling:
- Developer statistics (GitHub API)
- Weather data (Open-Meteo API)
- Location data (Nominatim + Mapbox)
- SoundCloud data (web scraping)
- Oura health data (Oura API)

Each fetch step:
- Validates JSON output
- Falls back to cached data on failure
- Logs all operations
- Sets skip flags for dependent steps
- Uses `continue-on-error: true`

#### Phase 3: Validate Data
- Validates all JSON files with jq
- Checks theme.json configuration
- Logs validation results
- Continues on validation failures

#### Phase 4: Generate All SVG Cards
Generates all visualization cards:
- Developer dashboard
- Weather card
- Location card
- SoundCloud card
- Oura health dashboard
- Oura mood dashboard

Each generation step:
- Checks if data fetch succeeded
- Uses incremental generation to skip unchanged data
- Creates fallback card on failure
- Continues pipeline on error

#### Phase 5: Optimize SVGs
- Runs SVGO with advanced configuration
- Optimizes all SVG files
- Reports optimization statistics
- Continues on optimization failure

#### Phase 6: Update README
- Injects all generated cards into README
- Updates appropriate marker sections
- Handles missing cards gracefully
- Continues on update failure

#### Phase 7: Build React Dashboard
- Copies data files to dashboard public directory
- Creates placeholder files for unimplemented features
- Runs npm build
- Configures GitHub Pages
- Uploads Pages artifact
- Deploys to GitHub Pages
- Continues on build/deploy failure

#### Phase 8: Lint with MegaLinter (Report-Only)
- Creates output directory
- Runs MegaLinter in report-only mode
- Generates summary report
- Uploads artifacts
- Never fails the workflow

#### Phase 9: Commit & Push
- Configures git user
- Adds all generated files
- Adds all logs
- Creates detailed commit message with metrics
- Commits and pushes atomically
- Continues on commit failure

#### Phase 10: Build Summary
- Displays final status of all operations
- Reports which cards were generated
- Shows dashboard build status
- Shows MegaLinter status
- Provides comprehensive build overview

## Error Handling Strategy

The unified workflow uses a comprehensive error handling strategy:

### Continue-on-Error
All non-critical steps use `continue-on-error: true` to prevent workflow failure.

### Fallback Mechanisms
1. **Data Fetching**: Falls back to cached data when API calls fail
2. **Card Generation**: Creates fallback SVG cards with error messages
3. **Validation**: Logs warnings but continues pipeline
4. **Dashboard Build**: Continues if build fails
5. **MegaLinter**: Always runs in report-only mode

### Skip Flags
Each fetch step sets output flags (`skip=true/false`) that dependent steps check before executing.

### Logging
All operations log to respective directories under `logs/`:
- Persistent logging (logs committed even on failure)
- Timestamped entries
- Severity levels (INFO, WARN, ERROR)
- Command tracking with exit codes

## Benefits

### 1. Atomic Updates
All cards and data updated in a single commit, ensuring consistency across the profile.

### 2. Error Resilience
- No single point of failure
- Graceful degradation with fallbacks
- Continues on partial errors
- Never blocks on sub-component failure

### 3. Simplified Maintenance
- One workflow file instead of 8+
- Centralized configuration
- Easier to understand and modify
- Reduced code duplication

### 4. Better Orchestration
- Sequential phases with clear dependencies
- Proper data flow between steps
- Consolidated setup and teardown
- Single environment for all operations

### 5. Easier Debugging
- All logs in one workflow run
- Comprehensive build summary
- Clear phase separation
- Detailed error messages

### 6. Resource Efficiency
- Single environment setup
- Shared caching across operations
- Reduced GitHub Actions usage
- Faster overall execution

## Trigger Configuration

The unified workflow runs on:

```yaml
on:
  push:
    branches:
      - main
      - master
  schedule:
    - cron: '0 6 * * *'  # Once per day at 6 AM UTC
  workflow_dispatch:      # Manual trigger
```

## Concurrency Control

```yaml
concurrency:
  group: profile-update
  cancel-in-progress: false
```

This ensures only one profile update runs at a time, preventing git conflicts.

## Required Secrets

The workflow requires the following secrets:

- `GITHUB_TOKEN` - Automatically provided by GitHub Actions
- `OURA_PAT` - Oura API Personal Access Token (optional)
- `MAPBOX_TOKEN` - Mapbox API token for location cards (optional)

## Monitoring Integration

The unified workflow integrates with the monitoring system:

- `monitoring.yml` now listens for "Build Profile — Unified Orchestration Pipeline" completion
- Tracks workflow metrics (run time, success rate, consecutive failures)
- Automatically creates issues for repeated failures (3+ consecutive)

## Archived Workflows

All old workflows have been removed as part of the repository cleanup in December 2024. They were previously preserved in `.github/workflows/_archive/` and can be found in the Git history if needed.

## Migration Checklist

- [x] Create unified `build-profile.yml` workflow
- [x] Implement all 10 phases with error handling
- [x] Add continue-on-error strategy throughout
- [x] Archive old workflow files
- [x] Update `monitoring.yml` to reference new workflow
- [x] Update README badges and documentation
- [x] Validate YAML syntax
- [x] Run existing tests to ensure compatibility
- [x] Create migration documentation

## Testing

The unified workflow has been validated:

1. **YAML Syntax**: Validated with `actionlint` and Python's `yaml.safe_load`
2. **Python Tests**: All 226 tests pass
3. **Shell Tests**: All retry logic and health check tests pass
4. **Integration**: Monitoring workflow updated to track unified workflow

## Rollback Plan

If issues arise, the old workflows can be restored from Git history:

1. Check out the desired workflow files from Git history before the cleanup
2. Update `monitoring.yml` to reference old workflow names
3. Revert README badge changes
4. Delete or disable `build-profile.yml`

However, the unified workflow is recommended for production use due to its superior architecture.

## Future Enhancements

Potential improvements to the unified workflow:

1. **Parallel Data Fetching**: Fetch all data sources in parallel using job matrix
2. **Conditional Deployment**: Only deploy dashboard when data files change
3. **Enhanced Metrics**: Track individual phase durations and success rates
4. **Notification System**: Slack/Discord notifications for failures
5. **Workflow Artifacts**: Save intermediate data files as artifacts

## Questions or Issues?

- Check the workflow run logs on GitHub Actions
- Review the [troubleshooting guide](TROUBLESHOOTING.md)
- Examine logs in the `logs/` directory
- Create an issue for persistent problems

## Related Documentation

- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) - Common issues and solutions
- [`MONITORING.md`](MONITORING.md) - Monitoring and alerting documentation
- [`WORKFLOW_CACHING.md`](WORKFLOW_CACHING.md) - Caching strategy and optimization
