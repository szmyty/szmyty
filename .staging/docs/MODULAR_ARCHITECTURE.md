# Modular Composite-Action Architecture

## Overview

The profile build system has been refactored into a modular, maintainable architecture using GitHub composite actions. This design provides:

- **Modularity**: Each task (fetch, generate, optimize) is a reusable composite action
- **Maintainability**: Changes to specific tasks only require updating one action file
- **Testability**: Individual actions can be tested in isolation
- **act-Friendly**: Compatible with `act` for local workflow testing

## Architecture

### Composite Actions

All composite actions are located in `.github/actions/`:

#### Setup
- **`setup/`**: Complete environment setup (Python, Node.js, dependencies, tools)

#### Fetch Actions
- **`fetch-developer/`**: Fetch GitHub developer statistics
- **`fetch-location/`**: Fetch location data from GitHub profile
- **`fetch-weather/`**: Fetch weather data for the user's location
- **`fetch-soundcloud/`**: Fetch SoundCloud track metadata
- **`fetch-oura/`**: Fetch Oura Ring health metrics
- **`fetch-quote/`**: Fetch inspirational quote of the day

#### Generation Actions
- **`generate-developer-dashboard/`**: Generate developer statistics SVG
- **`generate-quote-card/`**: Generate quote card SVG
- **`generate-weather-card/`**: Generate weather card SVG
- **`generate-location-card/`**: Generate location card SVG
- **`generate-soundcloud-card/`**: Generate SoundCloud card SVG
- **`generate-oura-dashboard/`**: Generate Oura health dashboard SVG
- **`generate-oura-mood/`**: Generate Oura mood dashboard SVG

#### Utility Actions
- **`optimize-svgs/`**: Optimize all SVG files with SVGO
- **`update-readme/`**: Update README.md with generated cards
- **`deploy-pages/`**: Build React dashboard and deploy to GitHub Pages

### Main Workflow

The main workflow (`.github/workflows/build-profile.yml`) orchestrates all tasks:

```yaml
jobs:
  build-profile:    # Main job - fetches data and generates all cards
  deploy-pages:     # Deploys to GitHub Pages
  commit-changes:   # Commits and pushes changes to the repository
  build-summary:    # Displays build summary
```

## Running with act

### Prerequisites

Install [act](https://github.com/nektos/act):
```bash
# macOS
brew install act

# Linux
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Windows (with chocolatey)
choco install act-cli
```

### Running the Main Workflow

Run the entire workflow locally:
```bash
act -W .github/workflows/build-profile.yml
```

### Running Individual Jobs

Run specific jobs:
```bash
# Run only the main build job
act -j build-profile

# Run only the deployment
act -j deploy-pages

# Run only the commit step
act -j commit-changes

# Run only the summary
act -j build-summary
```

### Testing Individual Actions

Use the test workflow to test individual composite actions:

1. Via GitHub UI:
   - Go to Actions tab
   - Select "Test Individual Actions"
   - Click "Run workflow"
   - Choose the action to test

2. Locally with act:
   ```bash
   # Test fetch-developer action
   act workflow_dispatch -W .github/workflows/test-individual-actions.yml --input action=fetch-developer

   # Test generate-weather-card action
   act workflow_dispatch -W .github/workflows/test-individual-actions.yml --input action=generate-weather-card
   ```

### Using Environment Variables

Create a `.secrets` file for local testing:
```bash
GITHUB_TOKEN=your_github_token_here
MAPBOX_TOKEN=your_mapbox_token_here
OURA_PAT=your_oura_token_here
```

Run with secrets:
```bash
act -j build-profile --secret-file .secrets
```

## Workflow Structure

### Data Flow

1. **Setup Phase**: Install all dependencies (Python, Node.js, system packages)
2. **Fetch Phase**: Retrieve data from various APIs (GitHub, weather, Oura, etc.)
3. **Validation Phase**: Validate JSON data integrity
4. **Generation Phase**: Create SVG cards from fetched data
5. **Optimization Phase**: Optimize SVGs for size
6. **Update Phase**: Update README with generated cards
7. **Deploy Phase**: Build and deploy React dashboard
8. **Commit Phase**: Commit and push all changes

### Artifact Management

The workflow uses GitHub Actions artifacts to share data between jobs:

- **`profile-data`**: Contains all fetched data, generated SVGs, and logs
- Uploaded after the build job completes
- Downloaded by deployment and commit jobs

### Output Variables

Jobs expose output variables for conditional execution:

```yaml
outputs:
  fetch-developer-skip: 'true' or 'false'
  fetch-location-skip: 'true' or 'false'
  fetch-weather-skip: 'true' or 'false'
  # ... etc
```

Generation jobs only run if their corresponding fetch didn't skip.

## Extending the System

### Adding a New Data Source

1. Create a new fetch action:
   ```bash
   mkdir -p .github/actions/fetch-newsource
   ```

2. Create `action.yml`:
   ```yaml
   name: 'Fetch New Source Data'
   description: 'Fetch data from new source'
   
   outputs:
     skip:
       description: 'Whether this step should be skipped'
       value: ${{ steps.fetch.outputs.skip }}
   
   runs:
     using: 'composite'
     steps:
       - name: Fetch data
         id: fetch
         shell: bash
         run: |
           # Your fetch logic here
           echo "skip=false" >> $GITHUB_OUTPUT
   ```

3. Add to main workflow:
   ```yaml
   - name: Fetch new source data
     id: fetch-newsource
     uses: ./.github/actions/fetch-newsource
     continue-on-error: true
   ```

### Adding a New Card Generator

1. Create a new generation action:
   ```bash
   mkdir -p .github/actions/generate-newsource-card
   ```

2. Create `action.yml`:
   ```yaml
   name: 'Generate New Source Card'
   description: 'Generate SVG card for new source'
   
   runs:
     using: 'composite'
     steps:
       - name: Generate card
         shell: bash
         run: |
           python scripts/generate-newsource-card.py
   ```

3. Add to main workflow:
   ```yaml
   - name: Generate new source card
     if: steps.fetch-newsource.outputs.skip != 'true'
     uses: ./.github/actions/generate-newsource-card
     continue-on-error: true
   ```

## Troubleshooting

### Action Not Found

Ensure you're checking out the repository with sufficient depth:
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 1
```

### Setup Action Fails

The setup action installs all dependencies. If it fails:
1. Check Python and Node.js versions
2. Verify `pyproject.toml` and `package-lock.json` are valid
3. Check system package availability

### Artifacts Not Found

If artifacts are missing between jobs:
1. Ensure the `build-profile` job completed successfully
2. Check artifact upload step didn't fail
3. Verify artifact retention settings

### act Execution Issues

Common issues with act:
1. **Docker required**: act uses Docker containers
2. **Large images**: Use medium or full image for better compatibility
3. **Secrets**: Pass via `--secret-file` or environment variables

## Best Practices

1. **Always use setup action**: Every job should start with the setup action
2. **Continue on error**: Use `continue-on-error: true` for non-critical steps
3. **Output variables**: Use outputs to control conditional execution
4. **Artifact management**: Upload/download artifacts for data sharing
5. **Validation**: Always validate JSON before processing
6. **Fallbacks**: Provide fallback SVGs when generation fails

## Performance Considerations

- **Setup caching**: Python and Node.js caches speed up dependency installation
- **SVG hash cache**: Prevents regenerating unchanged SVGs
- **Parallel execution**: Most fetch actions run in parallel within the job
- **Artifact compression**: Artifacts are automatically compressed

## Maintenance

### Updating Dependencies

1. Update Python dependencies in `pyproject.toml` or `requirements.txt`
2. Update Node dependencies in `dashboard-app/package.json`
3. The setup action will automatically install updated versions

### Updating Actions Versions

Update action versions in:
- `.github/actions/setup/action.yml`
- `.github/actions/deploy-pages/action.yml`
- `.github/workflows/build-profile.yml`

### Adding New Secrets

1. Add secret to repository settings
2. Reference in workflow: `${{ secrets.NEW_SECRET }}`
3. Pass to composite action as input
4. Use in action via `${{ inputs.new-secret }}`
