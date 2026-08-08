# GitHub Actions Workflows

This document describes the GitHub Actions workflows that power the profile automation system.

## Overview

The repository uses a **unified orchestration workflow** (`build-profile.yml`) that consolidates all profile updates into a single cohesive pipeline. This replaced the previous architecture of 8+ separate workflows.

> **Migration Note**: The old separate workflows were consolidated in December 2024. See [UNIFIED_WORKFLOW_MIGRATION.md](UNIFIED_WORKFLOW_MIGRATION.md) for details.

## Active Workflows

### 1. Build Profile — Unified Orchestration Pipeline

**File**: `.github/workflows/build-profile.yml`

The main workflow that handles all profile updates in a single orchestrated pipeline.

#### Schedule
- **Cron**: `0 6 * * *` (Daily at 6 AM UTC)
- **Manual**: `workflow_dispatch`
- **Push**: On commits to `main`/`master`

#### Pipeline Phases

1. **Setup** - Environment, dependencies, and caching
2. **Fetch All Data** - Developer stats, Weather, Location, SoundCloud, Oura health
3. **Validate Data** - JSON schema validation and sanity checks
4. **Generate SVG Cards** - All card types with fallback handling
5. **Optimize SVGs** - SVGO compression with advanced configuration
6. **Update README** - Inject all cards into appropriate sections
7. **Build Dashboard** - React dashboard compilation and deployment
8. **Lint (Report-Only)** - MegaLinter diagnostics without blocking
9. **Commit & Push** - Atomic commit of all changes
10. **Build Summary** - Comprehensive status report

#### Data Sources
- GitHub API (Developer statistics)
- Open-Meteo API (Weather data)
- Nominatim + Mapbox (Location data)
- SoundCloud web scraping (Latest track)
- Oura API (Health metrics)

#### Generated Outputs
- `developer/developer_dashboard.svg` - Developer statistics card
- `weather/weather-today.svg` - Current weather card
- `location/location-card.svg` - Location map card
- `assets/soundcloud-card.svg` - Latest SoundCloud track card
- `oura/health_dashboard.svg` - Oura health metrics dashboard
- `oura/mood_dashboard.svg` - Oura mood analysis card
- `dashboard-app/dist/` - React dashboard build (deployed to GitHub Pages)

#### Error Handling
- All steps use `continue-on-error: true` where appropriate
- Failed data fetches fall back to cached data
- Failed card generation produces fallback SVG cards
- Failed validations log warnings but continue
- Never blocks on partial errors

#### Required Secrets
- `GITHUB_TOKEN` - Automatically provided (GitHub API access)
- `OURA_PAT` - Oura API Personal Access Token (optional)
- `MAPBOX_TOKEN` - Mapbox API token (optional)

### 2. Monitoring & Alerts

**File**: `.github/workflows/monitoring.yml`

Monitors workflow health and creates automated alerts for failures.

#### Schedule
- **Cron**: `0 * * * *` (Every hour)
- **Workflow Run**: Triggers after `build-profile.yml` completion
- **Manual**: `workflow_dispatch`
- **Push**: On commits to `main`/`master`

#### Features
- Generates status page (`data/status/status-page.svg`)
- Tracks workflow metrics (run times, success rates, consecutive failures)
- Automatically creates issues for repeated failures (3+ consecutive)
- Logs MegaLinter results when applicable

#### Outputs
- `data/status/status-page.svg` - Visual status dashboard
- `data/metrics/*.json` - Workflow metrics files
- GitHub Issues for persistent failures

### 3. Unit Tests

**File**: `.github/workflows/tests.yml`

Runs Python and shell script tests to validate code changes.

#### Schedule
- **Push**: On commits to `main`/`master` affecting test files or scripts
- **Pull Request**: On PRs to `main`
- **Manual**: `workflow_dispatch`

#### Test Jobs
1. **Python Tests** - Type checking with mypy and pytest tests
2. **Shell Script Tests** - Retry logic, health checks, and cache tests

## Common Configuration

### Concurrency Control

```yaml
concurrency:
  group: profile-update
  cancel-in-progress: false
```

The `build-profile.yml` workflow uses this concurrency group to ensure only one profile update runs at a time, preventing git conflicts and race conditions.

### Permissions

The unified workflow requires these permissions:

```yaml
permissions:
  contents: write        # Push commits, update files
  pages: write          # Deploy to GitHub Pages
  id-token: write       # GitHub Pages deployment
  issues: write         # Create monitoring issues
  pull-requests: write  # Comment on PRs (MegaLinter)
```

### Caching Strategy

The workflow implements multi-level caching:

1. **Pip Cache** - Python package caching (60-75% faster setup)
2. **NPM Cache** - Node.js package caching
3. **SVG Hash Cache** - Incremental generation optimization
4. **Data Cache** - Fallback for failed API calls

## Workflow Architecture Benefits

### 1. Atomic Updates
All cards and data updated in a single commit, ensuring consistency.

### 2. Error Resilience
- No single point of failure
- Graceful degradation with fallbacks
- Continues on partial errors

### 3. Simplified Maintenance
- One workflow file instead of 8+
- Centralized configuration
- Easier to understand and modify

### 4. Better Orchestration
- Sequential phases with clear dependencies
- Proper data flow between steps
- Consolidated setup and teardown

### 5. Easier Debugging
- All logs in one workflow run
- Comprehensive build summary
- Clear phase separation

### 6. Resource Efficiency
- Single environment setup
- Shared caching across operations
- Reduced GitHub Actions usage

## Archived Workflows

The following workflows were consolidated into `build-profile.yml`:

- `developer.yml` - Developer Dashboard
- `soundcloud-card.yml` - SoundCloud Card
- `weather.yml` - Weather Card
- `location-card.yml` - Location Card
- `oura.yml` - Oura Health Dashboard
- `parallel-fetch.yml` - Parallel Data Fetching
- `megalinter.yml` - Code Linting
- `deploy-dashboard.yml` - React Dashboard Deployment

These workflows were removed during the December 2024 repository cleanup. They can be found in the Git history if needed.

## Triggering Workflows

### Manual Trigger

You can manually trigger the build profile workflow:

1. Go to the [Actions tab](https://github.com/szmyty/profile/actions)
2. Select "Build Profile — Unified Orchestration Pipeline"
3. Click "Run workflow"
4. Select the branch (usually `main`)
5. Click "Run workflow"

### Automatic Triggers

The workflow automatically runs:
- Daily at 6 AM UTC (scheduled)
- On every push to `main`/`master`
- When related files are modified

## Monitoring Workflow Runs

### View Workflow Status

1. Go to the [Actions tab](https://github.com/szmyty/profile/actions)
2. Click on a workflow run to see details
3. Expand steps to view logs
4. Check the "Build Summary" step for overall status

### Check Logs

Logs are committed to the repository in the `logs/` directory:

```
logs/
├── developer/     # Developer stats fetching logs
├── weather/       # Weather data fetching logs
├── location/      # Location data fetching logs
├── soundcloud/    # SoundCloud data fetching logs
├── oura/          # Oura health data fetching logs
└── megalinter/    # MegaLinter diagnostic reports
```

### Download Artifacts

The workflow uploads these artifacts:
- **megalinter-reports** - Full MegaLinter analysis (30 day retention)
- **pages-artifact** - Built React dashboard (GitHub Pages deployment)

## Troubleshooting

### Workflow Fails

If the unified workflow fails:

1. **Check the Build Summary** - Shows which phases succeeded/failed
2. **Review Phase Logs** - Expand failed steps to see error messages
3. **Check Repository Logs** - Look in `logs/` directory for detailed logs
4. **Verify Secrets** - Ensure required secrets are configured
5. **Check API Status** - Verify external APIs (GitHub, Oura, Mapbox) are operational

### Common Issues

#### Data Fetch Failures
- **Symptom**: Card shows "Unavailable" message
- **Solution**: Check API rate limits, verify secrets, review logs in `logs/` directory
- **Note**: Workflow continues with cached data

#### Card Generation Failures
- **Symptom**: Fallback card displayed
- **Solution**: Check script logs, verify data format, ensure dependencies installed
- **Note**: Workflow continues with fallback cards

#### Dashboard Build Failures
- **Symptom**: Dashboard not updated on GitHub Pages
- **Solution**: Check npm build logs, verify data files copied, review Pages deployment
- **Note**: Workflow continues and commits other changes

#### MegaLinter Issues
- **Symptom**: Linting warnings in logs
- **Solution**: Review MegaLinter reports in artifacts or `logs/megalinter/`
- **Note**: MegaLinter runs in report-only mode and never fails workflow

### Getting Help

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Review [UNIFIED_WORKFLOW_MIGRATION.md](UNIFIED_WORKFLOW_MIGRATION.md) for architecture details
- Create an issue for persistent problems
- Review workflow run logs for specific error messages

## Performance Metrics

The unified workflow typically takes:
- **Full Run**: 8-12 minutes (all phases)
- **With Cache Hits**: 5-8 minutes
- **Incremental Generation**: 3-5 minutes (no card changes)

Performance optimizations:
- Pip caching (60-75% faster Python setup)
- NPM caching (faster dashboard builds)
- SVG hash caching (50-80% time savings on unchanged data)
- Parallel SVG optimization

## Related Documentation

- [UNIFIED_WORKFLOW_MIGRATION.md](UNIFIED_WORKFLOW_MIGRATION.md) - Migration guide and architecture
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [MONITORING.md](MONITORING.md) - Monitoring and alerting system
- [WORKFLOW_CACHING.md](WORKFLOW_CACHING.md) - Caching strategy and optimization
- [cards.md](cards.md) - Card generation and customization
- [architecture.md](architecture.md) - System architecture overview
