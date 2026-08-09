# JSON Schemas

This directory contains JSON Schema definitions for validating data files used throughout the profile card generation system.

## Available Schemas

### theme.schema.json
Validates the theme configuration file (`config/theme.json`).

**Purpose**: Ensures theme.json has the correct structure with valid colors, gradients, typography, spacing, and card dimensions.

**Usage**: Automatically validated when `load_theme()` is called in `scripts/lib/utils.py`.

**Key requirements**:
- All hex colors must be 6-digit format (e.g., `#1a1a2e`)
- Gradients must be arrays of exactly 2 hex colors
- Font sizes and spacing values must be positive integers
- Required sections: `colors`, `gradients`, `typography`, `spacing`, `cards`

**Example validation error**:
```
Error: Theme configuration file validation failed: 'gradients' is a required property
```

### weather.schema.json
Validates weather data files used for weather card generation.

**Required fields**: `location`, `current`, `daily`

### health-snapshot.schema.json
Validates Oura health snapshot data.

### oura-metrics.schema.json
Validates Oura ring metrics data.

### developer-stats.schema.json
Validates GitHub developer statistics data.

### soundcloud-track.schema.json
Validates SoundCloud track data for music card generation.

## Validation Usage

All schemas are automatically used by the utility functions in `scripts/lib/utils.py`:

```python
# Automatic validation when loading JSON with schema
data = load_and_validate_json("data.json", "weather", "Weather data")

# Manual validation
validate_json(data, "theme", "Theme config")

# Non-throwing validation (returns error message or None)
error = try_validate_json(data, "theme", "Theme config")
if error:
    print(f"Validation failed: {error}")
```

## Schema Format

All schemas follow [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/schema) specification.

Each schema includes:
- `$schema`: JSON Schema version
- `$id`: Unique identifier for the schema
- `title`: Human-readable name
- `description`: Purpose and usage
- `type`: Expected root type (usually "object")
- `required`: List of required properties
- `properties`: Detailed property definitions
- `$defs`: Reusable definitions (e.g., color patterns, gradient formats)

## Adding New Schemas

When adding a new schema:

1. Create `<name>.schema.json` in this directory
2. Follow the JSON Schema 2020-12 specification
3. Include descriptive `title` and `description` fields
4. Define `required` properties and validation rules
5. Use `$defs` for reusable patterns
6. Test the schema against valid and invalid data
7. Update this README with the new schema

## Benefits of Schema Validation

- **Early error detection**: Catches structural issues before card generation
- **Clear error messages**: Provides specific information about what's wrong
- **Documentation**: Schemas serve as machine-readable documentation
- **Refactoring safety**: Prevents silent breakage when structure changes
- **Type safety**: Ensures data types and formats are correct

## Testing

All schemas have corresponding tests in `tests/`:
- `tests/test_theme_validation.py` - Theme schema validation tests
- `tests/test_utils.py` - General validation utility tests
- `tests/test_data_quality.py` - Data quality and validation tests

Run tests with:
```bash
python -m pytest tests/test_theme_validation.py -v
```
