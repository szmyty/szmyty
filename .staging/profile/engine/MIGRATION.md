# Migration Guide to Profile Engine

This guide helps you migrate from the legacy scripts to the new Profile Engine CLI.

## Overview

The Profile Engine consolidates all Python functionality into a single package with:
- **Unified CLI** (`profile-engine`) for all operations
- **FastAPI service** for the React dashboard
- **Modular architecture** with clear separation of concerns
- **Type safety** via Pydantic models
- **Shared logic** between CLI and API

## Installation

The engine is already included in the repository:

```bash
pip install -e ./engine
```

## Command Mapping

### Fetch Commands

| Legacy Script | New CLI Command |
|--------------|-----------------|
| `python scripts/fetch-developer-stats.py <username> <output>` | `profile-engine fetch developer --username <username> --output <output>` |
| `bash scripts/fetch-weather.sh` | `profile-engine fetch weather` |
| `bash scripts/fetch-oura.sh` | `profile-engine fetch oura --token $OURA_PAT` |
| `bash scripts/fetch-soundcloud.sh <user>` | `profile-engine fetch soundcloud --user <user>` |
| `bash scripts/fetch_quote.sh` | `profile-engine fetch quote` |

### Generate Commands

| Legacy Script | New CLI Command |
|--------------|-----------------|
| `python scripts/generate-weather-card.py <input> <output>` | `profile-engine generate weather-card --input <input> --output <output>` |
| `python scripts/generate-developer-dashboard.py <input> <output>` | `profile-engine generate developer-dashboard --input <input> --output <output>` |
| `python scripts/generate-health-dashboard.py <input> <output>` | `profile-engine generate oura-dashboard --input <input> --output <output>` |
| `python scripts/generate_quote_card.py <input> <output>` | `profile-engine generate quote-card --input <input> --output <output>` |

### Build All

Instead of calling multiple scripts, use:

```bash
profile-engine build-profile
```

This fetches all data and generates all cards in one command.

## GitHub Actions Migration

### Old Composite Action (Example)

```yaml
- name: Fetch Developer Statistics
  shell: bash
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python scripts/fetch-developer-stats.py "$USERNAME" developer/stats.json
```

### New Composite Action

```yaml
- name: Setup Profile Engine
  uses: ./.github/actions/setup-engine

- name: Fetch Developer Statistics
  uses: ./.github/actions/engine-fetch-developer
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    username: ${{ github.repository_owner }}
```

## API Usage

Start the API server:

```bash
profile-engine serve --port 8000
```

### Available Endpoints

- `GET /api/weather` - Weather data
- `GET /api/developer` - Developer statistics
- `GET /api/oura` - Oura health metrics
- `GET /api/mood` - Mood data
- `GET /api/soundcloud` - SoundCloud track
- `GET /api/quote` - Quote of the day
- `GET /api/theme` - Theme configuration
- `GET /health` - Health check

## Benefits of Migration

### 1. **Unified Interface**
- One command-line tool instead of multiple scripts
- Consistent argument naming and behavior
- Better help documentation

### 2. **Type Safety**
- Pydantic models validate all data
- Catch errors early with type checking
- Better IDE support

### 3. **Maintainability**
- Clear module structure
- Separation of concerns (clients, services, generators)
- Easier to test and extend

### 4. **Reusability**
- Same logic for CLI and API
- Services can be used programmatically
- Python package can be imported

### 5. **Better Error Handling**
- Consistent error messages
- Proper logging
- Graceful fallbacks

## Backward Compatibility

The legacy scripts remain in the `scripts/` directory for backward compatibility. They will be removed in a future version once all workflows are migrated.

## Gradual Migration Path

1. **Phase 1**: Install engine, test CLI commands locally
2. **Phase 2**: Update one workflow to use engine actions
3. **Phase 3**: Gradually migrate remaining workflows
4. **Phase 4**: Remove legacy scripts once all workflows migrated

## Getting Help

Run any command with `--help` to see usage:

```bash
profile-engine --help
profile-engine fetch --help
profile-engine generate --help
```

## Troubleshooting

### Issue: Command not found

**Solution**: Make sure the engine is installed:
```bash
pip install -e ./engine
```

### Issue: Import errors

**Solution**: Ensure you're in the repository root or have proper Python path set.

### Issue: Legacy script dependencies

**Solution**: Install both engine and legacy dependencies:
```bash
pip install -e ./engine
pip install -r requirements.txt
```

## Future Improvements

The engine architecture enables future enhancements:

- Direct HTTP API clients (no subprocess calls)
- Caching layer for API responses
- Database backend for historical data
- Real-time data updates via WebSockets
- Plugin system for custom cards
- Multi-language support (Rust/Go alternatives)
