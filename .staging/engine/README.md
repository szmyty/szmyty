# Profile Engine

A unified Python package for generating dynamic GitHub profile cards, providing both CLI tools for GitHub Actions and a FastAPI service for the React dashboard.

## Features

- **Unified CLI**: Single command-line interface for all profile operations
- **FastAPI Service**: REST API for the React dashboard
- **Modular Architecture**: Clean separation of concerns (clients, services, generators)
- **Type Safety**: Pydantic models for data validation
- **Shared Logic**: DRY principle - same code powers CLI and API

## Installation

```bash
cd engine
pip install -e .
```

## CLI Usage

### Fetch Data
```bash
profile-engine fetch weather
profile-engine fetch oura
profile-engine fetch developer --username <username>
profile-engine fetch soundcloud
profile-engine fetch quote
```

### Generate Cards
```bash
profile-engine generate weather-card
profile-engine generate developer-dashboard
profile-engine generate oura-dashboard
profile-engine generate soundcloud-card
profile-engine generate quote-card
```

### Build Complete Profile
```bash
profile-engine build-profile
```

## API Usage

Start the FastAPI server:

```bash
profile-engine serve --port 8000
```

Available endpoints:
- `GET /api/weather` - Get weather data
- `GET /api/developer` - Get developer statistics
- `GET /api/oura` - Get Oura health metrics
- `GET /api/soundcloud` - Get SoundCloud data
- `GET /api/quote` - Get quote of the day
- `GET /api/theme` - Get theme configuration

## Architecture

```
profile_engine/
├── clients/       # API clients (GitHub, Weather, Oura, SoundCloud)
├── services/      # Business logic layer
├── generators/    # SVG card generators
├── models/        # Pydantic data models
├── utils/         # Shared utilities
├── theme/         # Theme handling
├── cli.py         # CLI interface
└── api.py         # FastAPI app
```

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black profile_engine/
isort profile_engine/
```

## License

See repository LICENSE file.
