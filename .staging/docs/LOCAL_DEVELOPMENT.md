# Local Development with GitHub Actions

This guide shows you how to run and test GitHub Actions workflows locally using `act` in the devcontainer.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Running Workflows](#running-workflows)
- [Workflow Examples](#workflow-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Prerequisites

The devcontainer is pre-configured with everything you need:

✅ Docker-in-Docker for running containers  
✅ `act` CLI tool automatically installed  
✅ Configuration files (`.actrc`, `.secrets.example`)  
✅ Helper scripts for common tasks

### Starting the Devcontainer

1. Open the repository in VS Code
2. Press `F1` and select "Dev Containers: Reopen in Container"
3. Wait for the container to build and install dependencies
4. Docker will be available inside the container

## Quick Start

### 1. Check Installation

```bash
# Verify act is installed
act --version

# Verify Docker is running
docker ps

# List all available workflows and jobs
act -l
```

### 2. Set Up Secrets (Optional)

Many workflows require API tokens. Copy the example secrets file:

```bash
cp .secrets.example .secrets
```

Edit `.secrets` with your actual tokens:

```bash
GITHUB_TOKEN=ghp_yourPersonalAccessToken
MAPBOX_TOKEN=pk.yourMapboxToken
OURA_PAT=yourOuraPersonalAccessToken
```

> **Note**: The `.secrets` file is already in `.gitignore` and will never be committed.

### 3. Run Your First Workflow

```bash
# Run the Python tests (simplest workflow)
act -j test-python

# Or use the helper script
./scripts/act-test.sh tests test-python
```

## Running Workflows

### Using act Directly

```bash
# List all jobs in all workflows
act -l

# Run a specific job
act -j <job-name>

# Run all jobs in a workflow file
act -W .github/workflows/tests.yml

# Run with secrets from file
act -j test-python --secret-file .secrets

# Dry run (see what would execute)
act -j test-python -n
```

### Using the Helper Script

The `scripts/act-test.sh` helper script simplifies common operations:

```bash
# Show help and list workflows
./scripts/act-test.sh

# Run all jobs in a workflow
./scripts/act-test.sh tests

# Run a specific job
./scripts/act-test.sh tests test-python

# Run build-profile workflow
./scripts/act-test.sh build-profile
```

## Workflow Examples

### 1. Unit Tests Workflow

**File**: `.github/workflows/tests.yml`

This is the best workflow to start with - fast and requires no secrets.

```bash
# Run all test jobs
act -W .github/workflows/tests.yml

# Run only Python tests
act -j test-python

# Run only shell script tests
act -j test-shell
```

**What it does**:
- Checks out the repository
- Sets up Python environment
- Installs dependencies
- Runs pytest or shell tests

### 2. Build Profile Workflow

**File**: `.github/workflows/build-profile.yml`

This is a complex workflow that fetches data and generates SVG cards.

```bash
# Run the entire workflow (requires secrets)
act -W .github/workflows/build-profile.yml --secret-file .secrets

# Run only the main build job
act -j build-profile --secret-file .secrets
```

**Requirements**:
- GitHub token in `.secrets` file
- Optional: MAPBOX_TOKEN, OURA_PAT for full functionality
- Docker with sufficient resources (2GB+ RAM)

**What it does**:
- Fetches data from multiple APIs (GitHub, weather, location, etc.)
- Generates SVG dashboard cards
- Builds React dashboard application
- Updates README with generated cards

### 3. Monitoring Workflow

**File**: `.github/workflows/monitoring.yml`

```bash
# Run status page generation
act -j generate-status-page
```

### 4. Release Workflow

**File**: `.github/workflows/release.yml`

```bash
# Test release validation
act workflow_dispatch -W .github/workflows/release.yml \
  --eventpath .github/workflows/act-events/workflow_dispatch.json
```

## Configuration

### .actrc Configuration

The `.actrc` file in the repository root contains default settings:

```
# Use compatible Ubuntu images
-P ubuntu-latest=catthehacker/ubuntu:act-latest

# Enable verbose output
--verbose

# Use GitHub token from environment
--env GITHUB_TOKEN
```

You can override these with command-line flags or create a local `.actrc.local` file.

### Runner Images

act uses Docker images that simulate GitHub's hosted runners:

- `ubuntu-latest` → `catthehacker/ubuntu:act-latest` (recommended)
- `ubuntu-22.04` → `catthehacker/ubuntu:act-22.04`
- `ubuntu-20.04` → `catthehacker/ubuntu:act-20.04`

**Image sizes**:
- Small (~500MB): Basic tools only
- Medium (~5GB): Most common tools (default)
- Large (~20GB): All GitHub-hosted runner tools

The devcontainer uses the medium-sized image for the best balance.

### Custom Event Payloads

Pre-configured event payloads are in `.github/workflows/act-events/`:

```bash
# Push event
act push --eventpath .github/workflows/act-events/push.json

# Pull request event
act pull_request --eventpath .github/workflows/act-events/pull_request.json

# Workflow dispatch
act workflow_dispatch --eventpath .github/workflows/act-events/workflow_dispatch.json
```

Edit these files to customize the event data for testing.

## Known Limitations

⚠️ **Important**: This repository uses custom composite actions (`.github/actions/*`) that have limited support in act.

**What this means**:
- Some workflows may fail with "failed to read 'action.yml'" errors
- The `tests.yml` workflow requires workarounds
- Full end-to-end testing should use actual GitHub Actions

**Recommended approach**:
- ✅ Test individual scripts directly (see examples below)
- ✅ Use act for workflow syntax validation
- ✅ Use act-demo.yml workflow which is designed to work with act
- ⚠️ Use GitHub Actions for full integration testing of complex workflows

### Direct Script Testing (Recommended)

Instead of using act with the full workflows, test scripts directly:

```bash
# Python tests
python -m pytest tests/ -v

# Shell script tests  
bash tests/test_retry_logic.sh
bash tests/test_health_checks.sh

# Type checking
python -m mypy scripts/

# Card generation with mock data
./scripts/dev-mode.sh all

# Individual card generation
python scripts/generate-developer-dashboard.py developer/stats.json output.svg
```

## Troubleshooting

### Docker Issues

**Problem**: "Cannot connect to Docker daemon"

```bash
# Check if Docker is running
docker ps

# Inside devcontainer, Docker should work automatically
# If not, try restarting the devcontainer
```

**Problem**: "Permission denied on /var/run/docker.sock"

```bash
# This shouldn't happen in the devcontainer
# If it does, the Docker-in-Docker feature may not be working
# Rebuild the devcontainer: F1 → "Dev Containers: Rebuild Container"
```

### act Issues

**Problem**: "Job requires missing secrets"

```bash
# Create .secrets file from example
cp .secrets.example .secrets

# Add your tokens
nano .secrets

# Run with secrets file
act -j job-name --secret-file .secrets
```

**Problem**: "Container image pull failed"

```bash
# Pull the image manually
docker pull catthehacker/ubuntu:act-latest

# Or use a different image
act -j job-name -P ubuntu-latest=node:16-buster
```

**Problem**: "Composite action failed"

Some workflows use composite actions from `.github/actions/`. These should work but may have limitations:

- Ensure Docker-in-Docker is working
- Try running individual steps instead of the full workflow
- Check that all dependencies are available in the runner image

### Workflow-Specific Issues

**build-profile.yml is slow or fails**

This workflow is resource-intensive:

1. **Run specific jobs instead of the full workflow**:
   ```bash
   # Run only the developer stats step
   act -j build-profile --secret-file .secrets
   ```

2. **Increase Docker resources**:
   - Docker Desktop: Settings → Resources → Increase CPU/Memory
   - Allocate at least 4GB RAM and 2 CPUs

3. **Skip expensive steps**:
   Some steps like MegaLinter can be skipped when testing locally.

**Tests pass locally but fail in CI**

This can happen due to differences between:
- Local environment vs GitHub-hosted runners
- Docker image differences
- Secrets/environment variables

Always verify your changes in actual CI after local testing.

### Getting Help

1. **Check act logs**: Use `-v` or `--verbose` for detailed output
2. **Dry run first**: Use `-n` flag to see what would execute
3. **Simplify**: Start with simple workflows like `tests.yml`
4. **Compare**: Check workflow logs in GitHub Actions to see differences

## Advanced Usage

### Running Specific Steps

You can't run individual steps, but you can modify workflows temporarily for testing:

```bash
# Create a test workflow with only the steps you need
cp .github/workflows/tests.yml /tmp/test-minimal.yml
# Edit the file to include only needed steps
act -W /tmp/test-minimal.yml
```

### Environment Variables

```bash
# Set environment variables
act -j test-python --env CUSTOM_VAR=value

# Use .env file
echo "CUSTOM_VAR=value" > .env
act -j test-python --env-file .env
```

### Debugging

```bash
# Run with extra verbose output
act -j test-python -v

# Keep containers after run (for inspection)
act -j test-python --container-architecture linux/amd64 --reuse

# Inspect the container
docker ps -a
docker logs <container-id>
```

### Matrix Builds

If workflows use matrix strategies, act will run all matrix combinations:

```bash
# Run all matrix jobs
act -W .github/workflows/tests.yml

# Filter to specific matrix value (not directly supported)
# You'll need to modify the workflow temporarily
```

### Caching

act supports caching similar to GitHub Actions:

```bash
# Cache is automatically handled
# Cache location: ~/.cache/act/

# Clear cache if needed
rm -rf ~/.cache/act/
```

## Best Practices

1. **Start Simple**: Test with `tests.yml` before complex workflows
2. **Use Secrets File**: Keep tokens in `.secrets` (never commit)
3. **Iterate Quickly**: Use specific jobs (`-j`) instead of full workflows
4. **Resource Management**: Allocate sufficient Docker resources
5. **Keep Images Updated**: Periodically pull latest runner images
6. **Document Changes**: Update act configs when workflow requirements change

## Resources

- [act GitHub Repository](https://github.com/nektos/act)
- [act Documentation](https://nektosact.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Repository Workflow Documentation](../.github/workflows/README.md)

## Summary

With `act` in the devcontainer, you can:

✅ Test workflow changes before pushing  
✅ Debug failing jobs locally  
✅ Iterate quickly without using CI minutes  
✅ Develop workflows in isolation  
✅ Validate composite actions

Happy local development! 🚀
