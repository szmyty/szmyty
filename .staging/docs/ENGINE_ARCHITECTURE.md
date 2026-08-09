# Profile Engine Architecture

## Overview

The Profile Engine is a unified Python package that consolidates all profile card generation and data fetching logic into a single, maintainable codebase.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Profile Engine                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │              │         │              │                │
│  │  CLI (Click) │         │ FastAPI App  │                │
│  │              │         │              │                │
│  └──────┬───────┘         └──────┬───────┘                │
│         │                        │                         │
│         └────────────┬───────────┘                         │
│                      │                                     │
│              ┌───────▼────────┐                           │
│              │                │                           │
│              │   Services     │                           │
│              │  (Business     │                           │
│              │   Logic)       │                           │
│              └───────┬────────┘                           │
│                      │                                     │
│         ┌────────────┼────────────┐                       │
│         │            │            │                       │
│    ┌────▼───┐  ┌────▼────┐  ┌────▼────┐                 │
│    │        │  │         │  │         │                 │
│    │Clients │  │Generators│ │ Models  │                 │
│    │        │  │         │  │(Pydantic)│                │
│    └────┬───┘  └────┬────┘  └─────────┘                 │
│         │           │                                     │
│         │           │                                     │
│    ┌────▼───────────▼──┐    ┌──────────┐                │
│    │                   │    │          │                │
│    │  External APIs    │    │  Utils   │                │
│    │  (GitHub, Weather)│    │  Theme   │                │
│    └───────────────────┘    └──────────┘                │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### `/engine/profile_engine/`

Main package directory containing all engine code.

#### `cli.py`
Command-line interface built with Click. Provides commands for:
- Fetching data from external sources
- Generating SVG cards
- Building complete profile
- Starting API server

#### `api.py`
FastAPI application providing REST endpoints for:
- Weather data
- Developer statistics
- Oura health metrics
- SoundCloud tracks
- Quotes
- Theme configuration

#### `/clients/`
API clients for external services:
- `github.py` - GitHub API client for developer stats
- `weather.py` - Weather API client
- `oura.py` - Oura health API client
- `soundcloud.py` - SoundCloud API client
- `quote.py` - Quote API client

**Design Pattern**: Wrapper pattern around legacy scripts initially, with plans to migrate to direct HTTP clients using `httpx`.

#### `/services/`
Business logic layer:
- `data_service.py` - Orchestrates data fetching with error handling and logging

**Purpose**: Separates business logic from presentation (CLI/API) and data access (clients).

#### `/generators/`
SVG card generation:
- `card_generator.py` - Service for generating SVG cards from JSON data

**Design Pattern**: Wrapper pattern around legacy generator scripts, providing consistent interface.

#### `/models/`
Pydantic data models for type safety and validation:
- `developer.py` - Developer statistics models
- `weather.py` - Weather data models
- `oura.py` - Health metrics and mood models
- `quote.py` - Quote models
- `soundcloud.py` - Track models

**Benefits**:
- Runtime validation
- IDE autocomplete
- Documentation generation
- API schema generation

#### `/utils/`
Shared utilities:
- `utils.py` - Common helpers (XML escaping, JSON loading, theme handling)
- `logging_utils.py` - Logging configuration
- `weather_alerts.py` - Weather alert formatting
- `data_quality.py` - Data validation utilities
- `change_detection.py` - Change detection for incremental generation

#### `/theme/`
Theme management:
- `loader.py` - Theme configuration loading and color extraction

## Data Flow

### Fetch Flow

```
CLI Command
    │
    ▼
DataService.fetch_developer_stats()
    │
    ▼
GitHubClient.fetch_developer_stats()
    │
    ▼
Legacy Script (subprocess)
    │
    ▼
GitHub API (HTTP)
    │
    ▼
Save JSON to disk
    │
    ▼
Load & Validate with Pydantic
    │
    ▼
Return DeveloperStats model
```

### Generate Flow

```
CLI Command
    │
    ▼
CardGenerator.generate_developer_dashboard()
    │
    ▼
Legacy Generator Script (subprocess)
    │
    ▼
Load JSON data
    │
    ▼
Apply theme
    │
    ▼
Generate SVG
    │
    ▼
Save SVG to disk
```

### API Flow

```
HTTP GET /api/developer
    │
    ▼
FastAPI Route Handler
    │
    ▼
load_json_file("developer/stats.json")
    │
    ▼
Return JSON response
```

## Design Decisions

### 1. Wrapper Pattern (Current)

**Decision**: Use subprocess calls to existing scripts initially.

**Rationale**:
- Maintain backward compatibility
- Reduce initial refactoring effort
- Establish architecture first
- Allow gradual migration

**Future**: Replace with direct implementations using `httpx` for HTTP calls and native Python for generation.

### 2. Pydantic Models

**Decision**: Use Pydantic for all data models.

**Rationale**:
- Runtime validation catches errors early
- Type hints improve IDE support
- Automatic OpenAPI schema generation
- Clear data contracts

### 3. Service Layer

**Decision**: Separate service layer between CLI/API and clients.

**Rationale**:
- Business logic reusable across interfaces
- Consistent error handling
- Easier testing
- Single source of truth

### 4. Click for CLI

**Decision**: Use Click framework for CLI.

**Rationale**:
- Excellent documentation
- Subcommand support
- Automatic help generation
- Context management

**Alternative Considered**: Typer (Click-based with type hints)

### 5. FastAPI for API

**Decision**: Use FastAPI for REST API.

**Rationale**:
- Async support for better performance
- Automatic OpenAPI documentation
- Pydantic integration
- Modern Python features

## Testing Strategy

### Unit Tests
- Model validation (Pydantic)
- CLI command parsing
- Utility functions

### Integration Tests
- End-to-end CLI flows
- API endpoint responses
- Data fetching workflows

### Current Coverage
- CLI commands: ✅ 5/5 tests passing
- Models: ✅ 6/6 tests passing
- Legacy scripts: ✅ 235/235 tests passing

## Performance Considerations

### Current
- Subprocess overhead for legacy scripts (~100-500ms per call)
- Sequential execution for multiple operations
- File-based communication

### Future Optimizations
1. **Direct HTTP Clients**: Remove subprocess overhead
2. **Async Operations**: Parallel fetching with `asyncio`
3. **Caching Layer**: Redis/Memory cache for API responses
4. **Connection Pooling**: Reuse HTTP connections
5. **Incremental Generation**: Only regenerate changed cards

## Security Considerations

1. **API Token Management**
   - Environment variables for secrets
   - No tokens in logs or outputs
   - Separate tokens per service

2. **Input Validation**
   - Pydantic models validate all inputs
   - Path traversal prevention
   - SQL injection N/A (no database yet)

3. **CORS Configuration**
   - Restrictive in production
   - Configurable per environment

4. **Rate Limiting**
   - Respect GitHub API rate limits
   - Implement backoff strategies
   - Cache responses when appropriate

## Deployment Options

### 1. GitHub Actions (Current)
- CLI commands in composite actions
- Scheduled workflows
- Artifact uploads

### 2. Docker Container
```bash
docker build -t profile-engine ./engine
docker run -p 8000:8000 profile-engine serve
```

### 3. Kubernetes/Cloud Run
- FastAPI as web service
- Horizontal scaling
- Health checks via `/health`

### 4. Serverless
- AWS Lambda / Google Cloud Functions
- API Gateway integration
- Scheduled EventBridge/Cloud Scheduler

## Migration Path

See [MIGRATION.md](../MIGRATION.md) for detailed migration guide.

### Phase 1: Parallel Run ✅ (Current)
- Both legacy and engine available
- Engine tested in isolation
- Gradual action migration

### Phase 2: Primary Use
- Main workflows use engine
- Legacy as fallback
- Deprecation warnings

### Phase 3: Legacy Removal
- Remove legacy scripts
- Engine as sole implementation
- Complete migration

## Future Enhancements

### Short Term
1. Direct HTTP clients (remove subprocess)
2. Async data fetching
3. Better error messages
4. More granular logging

### Medium Term
1. Database backend for history
2. Real-time WebSocket updates
3. Caching layer
4. Plugin system for custom cards

### Long Term
1. Multi-language ports (Rust/Go)
2. GraphQL API
3. Machine learning for insights
4. Distributed generation
5. Community card marketplace

## Contributing

Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### Key Areas
- Direct HTTP client implementations
- New card generators
- Additional data sources
- Performance improvements
- Documentation

## References

- [Click Documentation](https://click.palletsprojects.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [GitHub API Documentation](https://docs.github.com/en/rest)
