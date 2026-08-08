# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the profile repository.

## Active Workflows

| Workflow | File | Description | Trigger |
|----------|------|-------------|---------|
| **Build Profile** | `build-profile.yml` | Main orchestration pipeline that fetches data and generates all cards | Push, Schedule (daily), Manual |
| **Unit Tests** | `tests.yml` | Runs Python and shell script tests | Push, PR, Manual |
| **Monitoring** | `monitoring.yml` | Generates status pages and monitors workflow health | Schedule (hourly), Workflow runs, Manual |
| **Release** | `release.yml` | Creates releases when version tags are pushed | Tag push, Manual |
| **Greetings** | `greetings.yml` | Welcomes new contributors | Issue/PR opened |
| **act Demo** | `act-demo.yml` | Demo workflow for testing act locally | Push, Manual |

## Local Development with act

You can run workflows locally using `act` in the devcontainer. See:

- **[Local Development Guide](../../docs/LOCAL_DEVELOPMENT.md)** - Full development documentation

### Quick Start

```bash
# List all workflows
act -l

# Run the demo workflow (recommended for testing)
act -j list-files -W .github/workflows/act-demo.yml

# Test individual scripts (recommended for this repo)
python -m pytest tests/ -v
./scripts/dev-mode.sh all
```

### Important Notes

⚠️ Some workflows use custom composite actions (`.github/actions/*`) which have limited support in act. For these workflows:
- Test scripts directly instead of using act
- Use act for syntax validation only
- Use GitHub Actions for full integration testing

## Workflow Event Payloads

The `act-events/` directory contains example event payloads for testing workflows locally:

- `push.json` - Push event payload
- `pull_request.json` - Pull request event payload
- `workflow_dispatch.json` - Manual trigger payload

Use these with act:

```bash
act push --eventpath .github/workflows/act-events/push.json
```

## Composite Actions

This repository uses custom composite actions in `.github/actions/`:

- **setup-environment** - Sets up the complete development environment
- **pip-install** - Installs Python dependencies

These actions are reused across multiple workflows to reduce duplication.

## Workflow Dependencies

### build-profile.yml

**Dependencies**:
- Python 3.11 with Poetry
- Node.js 20 with npm
- System packages: jq, curl, bc
- Optional: GitHub token, API tokens (MAPBOX, OURA)

**Outputs**:
- SVG dashboard cards
- JSON data files
- React dashboard (deployed to GitHub Pages)

### tests.yml

**Dependencies**:
- Python 3.11 with Poetry
- Test dependencies (pytest, mypy)
- Shell utilities (bash, shellcheck)

**Outputs**:
- Test results
- Type checking results

### monitoring.yml

**Dependencies**:
- Python 3.11
- Previous workflow run data
- GitHub API access

**Outputs**:
- Status page SVG
- Workflow metrics JSON files
- GitHub issues (for failures)

## Development

### Testing Changes Locally

1. **Test scripts directly** (fastest):
   ```bash
   python -m pytest tests/ -v
   bash tests/test_retry_logic.sh
   ```

2. **Use development mode** (with mock data):
   ```bash
   ./scripts/dev-mode.sh all
   ```

3. **Test with act** (syntax validation):
   ```bash
   act -n -W .github/workflows/tests.yml
   ```

4. **Push to feature branch** (full integration):
   ```bash
   git push origin feature/my-changes
   # Watch GitHub Actions run the workflows
   ```

### Adding New Workflows

1. Create workflow file in `.github/workflows/`
2. Test locally with act or direct script execution
3. Document in this README

### Modifying Existing Workflows

1. Make changes to workflow file
2. Test syntax: `act -n -W .github/workflows/your-workflow.yml`
3. Test execution: Push to feature branch or test scripts directly
4. Update documentation if behavior changes

## Troubleshooting

### Workflow Fails in CI

1. Check workflow logs in GitHub Actions
2. Look for error messages in specific steps
3. Test the failing script locally
4. Check for missing secrets or environment variables

### act Not Working

Common solutions:
- Use `act-demo.yml` workflow for testing
- Test scripts directly instead of full workflows
- Check Docker is running: `docker ps`

### Composite Action Issues

If workflows fail with "failed to read 'action.yml'":
- This is a known limitation of act with local composite actions
- Test the scripts directly instead
- Or use GitHub Actions for full testing

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [act Documentation](https://github.com/nektos/act)
- [Repository Workflows Guide](../../docs/WORKFLOWS.md)
- [Local Development Guide](../../docs/LOCAL_DEVELOPMENT.md)

## Summary

This repository has comprehensive GitHub Actions workflows for:
- ✅ Automated data fetching and card generation
- ✅ Continuous testing and validation
- ✅ Monitoring and alerting
- ✅ Release management
- ✅ Local development with act

For the best local development experience:
1. Use direct script testing (`pytest`, shell scripts)
2. Use development mode (`dev-mode.sh`)
3. Use act for syntax validation
4. Use GitHub Actions for full integration testing
