# Mock Data for Development

This directory contains mock JSON data files for local development and testing without requiring real API keys.

## Available Mock Data

### 1. `soundcloud-metadata.json`
Mock SoundCloud track metadata for testing card generation.

**Schema**: [`schemas/soundcloud-track.schema.json`](../../schemas/soundcloud-track.schema.json)

### 2. `weather.json`
Mock weather data with current conditions and daily forecast.

**Schema**: [`schemas/weather.schema.json`](../../schemas/weather.schema.json)

### 3. `developer-stats.json`
Mock GitHub developer statistics including commits, PRs, languages, etc.

**Schema**: [`schemas/developer-stats.schema.json`](../../schemas/developer-stats.schema.json)

### 4. `oura-metrics.json`
Mock Oura Ring health metrics including sleep, readiness, and activity scores.

**Schema**: [`schemas/oura-metrics.schema.json`](../../schemas/oura-metrics.schema.json)

## Usage

### Option 1: Using the Development Mode Script

Run all card generators with mock data:

```bash
./scripts/dev-mode.sh all
```

Or generate a specific card:

```bash
./scripts/dev-mode.sh soundcloud
./scripts/dev-mode.sh weather
./scripts/dev-mode.sh developer
./scripts/dev-mode.sh oura
```

Output will be saved to `dev-output/` directory.

### Option 2: Manual Generation

You can also manually run individual scripts with mock data:

```bash
# SoundCloud card
python scripts/generate-card.py \
    data/mock/soundcloud-metadata.json \
    data/mock/soundcloud-artwork.jpg \
    dev-output/soundcloud-card.svg

# Weather card
python scripts/generate-weather-card.py \
    data/mock/weather.json \
    dev-output/weather-today.svg

# Developer dashboard
python scripts/generate-developer-dashboard.py \
    data/mock/developer-stats.json \
    dev-output/developer-dashboard.svg

# Oura health dashboard
python scripts/generate-health-snapshot.py \
    data/mock/oura-metrics.json \
    dev-output/health-snapshot.json
python scripts/generate-health-dashboard.py \
    dev-output/health-snapshot.json \
    dev-output/health-dashboard.svg
```

## Customizing Mock Data

Feel free to edit these JSON files to test different scenarios:

- Different weather conditions
- Various commit activity patterns
- Different health scores
- Edge cases and error conditions

All mock data files follow the JSON schemas defined in the `schemas/` directory and are validated by pre-commit hooks.

## Validation

Validate mock data against schemas:

```bash
# Install check-jsonschema
pip install check-jsonschema

# Validate a specific file
check-jsonschema --schemafile schemas/weather.schema.json data/mock/weather.json

# Or run pre-commit to validate all
pre-commit run check-jsonschema --all-files
```
