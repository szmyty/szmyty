# Architecture Overview

This document describes the architecture of the GitHub Profile automation system, which generates dynamic SVG dashboard cards displaying various personal metrics.

## System Overview

The repository serves as a GitHub profile automation system that generates dynamic SVG dashboard cards for:

- **Location** — Static map from OpenStreetMap
- **Weather** — Current conditions and forecast via Open-Meteo API
- **SoundCloud** — Latest track display
- **Oura Ring Health Metrics** — Sleep, readiness, activity, and mood dashboards

## Directory Structure

```
profile/
├── .github/workflows/          # GitHub Actions workflow definitions
│   ├── build-profile.yml       # Unified orchestration pipeline (daily)
│   ├── monitoring.yml          # Workflow monitoring and alerts
│   └── tests.yml               # Unit and integration tests
├── scripts/                    # All executable scripts
│   ├── lib/                    # Shared Python/shell libraries
│   │   ├── __init__.py
│   │   ├── card_base.py        # Base class for SVG card generators
│   │   ├── common.sh           # Shared shell functions
│   │   └── utils.py            # Shared Python utilities
│   ├── fetch-*.sh              # Data fetching (shell scripts)
│   ├── generate-*.py           # SVG generation (Python scripts)
│   ├── oura_mood_engine.py     # Mood computation engine
│   └── update_readme.py        # README marker update script
├── config/                     # Configuration files
│   └── theme.json              # Visual theme configuration
├── schemas/                    # JSON schema definitions
├── assets/                     # SoundCloud-related assets
├── location/                   # Location card output
├── oura/                       # Oura health outputs
├── weather/                    # Weather card output
├── data/                       # Runtime data (timezone info)
└── tests/                      # Test files
```

## Data Flow

The system follows a three-stage pipeline for each card type:

```
External APIs → Shell Scripts (fetch) → JSON → Python Scripts (generate) → SVG
```

### Stage 1: Data Fetching (Shell Scripts)

Shell scripts (`scripts/fetch-*.sh`) handle data retrieval:
- Make HTTP requests to external APIs
- Handle authentication (for Oura API)
- Parse and normalize API responses
- Output JSON data for consumption by Python scripts

### Stage 2: Data Processing (Python Scripts)

Python scripts (`scripts/generate-*.py`) handle SVG generation:
- Load and validate JSON data
- Apply theme configuration from `config/theme.json`
- Generate SVG cards with proper styling
- Write output to designated directories

### Stage 3: README Update

The `scripts/update_readme.py` script updates the README.md using placeholder markers:
- `<!-- CARD:START -->...<!-- CARD:END -->` pattern
- Each card type has its own marker (e.g., `LOCATION-CARD`, `WEATHER-CARD`)

## Component Communication

1. **Workflows** invoke **Shell scripts** to fetch data
2. Shell scripts produce **JSON files** as intermediate data
3. **Python scripts** consume JSON and produce **SVG cards**
4. **README.md** is updated by workflows using placeholder markers

## Shared Libraries

### Python (`scripts/lib/`)

- **`utils.py`**: Common utilities including:
  - XML escaping
  - Safe dictionary access
  - JSON loading and validation
  - Theme configuration loading
  - Image optimization
  - Timestamp formatting

- **`card_base.py`**: Abstract base class for card generators providing:
  - Theme loading and caching
  - SVG document structure
  - Background rendering with gradients
  - Decorative accents
  - Footer/timestamp rendering

### Shell (`scripts/lib/common.sh`)

- Shared shell functions for:
  - Location fetching
  - Coordinate geocoding
  - URL encoding

## Theme System

All visual styling is centralized in `config/theme.json`:

```json
{
  "colors": {
    "background": { "primary": "#1a1a2e", "secondary": "#16213e" },
    "text": { "primary": "#ffffff", "accent": "#64ffda" },
    "accent": { "teal": "#64ffda", "sleep": "#4facfe" }
  },
  "typography": {
    "font_family": "'Segoe UI', Arial, sans-serif",
    "sizes": { "sm": 9, "base": 10, "lg": 12 }
  },
  "cards": {
    "widths": { "soundcloud": 480, "weather": 480 },
    "heights": { "soundcloud": 144, "weather": 230 }
  }
}
```

## External Dependencies

### APIs
- **GitHub API**: User profile location
- **Nominatim/OpenStreetMap**: Geocoding and static maps
- **Open-Meteo**: Weather data (no API key required)
- **SoundCloud**: Track metadata and artwork
- **Oura API**: Health and sleep metrics (requires PAT token)

### GitHub Actions
- `actions/checkout@v4`
- `actions/setup-python@v5`
- System packages: `jq`, `curl`
- Python packages: `Pillow`, `jsonschema`
- npm packages: `svgo`

## Security Considerations

- **OURA_PAT**: Stored as GitHub secret, never committed
- **GitHub token**: Used for authenticated API requests to avoid rate limiting
- Debug files (raw API responses) are gitignored
- Personal data (email, user ID) is filtered from committed files

## Workflow Architecture

The repository uses a unified orchestration workflow that consolidates all profile updates:

### Build Profile Pipeline

**File**: `.github/workflows/build-profile.yml`

A single workflow that executes in 10 sequential phases:
1. Setup (environment, dependencies, caching)
2. Fetch All Data (Developer, Weather, Location, SoundCloud, Oura)
3. Validate Data (JSON schema validation)
4. Generate All SVG Cards (with fallback handling)
5. Optimize SVGs (SVGO compression)
6. Update README (inject all cards)
7. Build React Dashboard (optional)
8. Lint with MegaLinter (report-only)
9. Commit & Push (atomic update)
10. Build Summary (comprehensive status)

### Concurrency Control

The unified workflow uses a concurrency group to prevent simultaneous runs:

```yaml
concurrency:
  group: profile-update
  cancel-in-progress: false
```

This ensures atomic updates with no git conflicts or race conditions.

### Error Handling

The workflow implements comprehensive error handling:
- All steps use `continue-on-error: true` where appropriate
- Failed data fetches fall back to cached data
- Failed card generation produces fallback SVG cards
- Never blocks on partial errors

See [UNIFIED_WORKFLOW_MIGRATION.md](UNIFIED_WORKFLOW_MIGRATION.md) for detailed architecture documentation.
