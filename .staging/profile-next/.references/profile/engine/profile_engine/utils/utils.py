#!/usr/bin/env python3
"""
Shared utility functions for profile card generators.

This module provides common helper functions used across multiple card generator
scripts, including XML escaping, safe dictionary access, JSON loading, and
SVG visualization helpers.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


# Configure module logger for fallback operations
_fallback_logger: Optional[logging.Logger] = None


def _get_fallback_logger() -> logging.Logger:
    """Get or create the fallback logger."""
    global _fallback_logger
    if _fallback_logger is None:
        _fallback_logger = logging.getLogger("card_fallback")
        _fallback_logger.setLevel(logging.DEBUG)
        # Add console handler if none exists
        if not _fallback_logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            _fallback_logger.addHandler(handler)
    return _fallback_logger

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    ValidationError = Exception  # Fallback type for type hints

# Cache for loaded theme to avoid re-reading file
_theme_cache: Optional[Dict] = None
# Cache for loaded schemas to avoid re-reading files
_schema_cache: Dict[str, Dict] = {}


def escape_xml(text: str) -> str:
    """
    Escape special characters for XML/SVG.

    Args:
        text: The text string to escape.

    Returns:
        The escaped string safe for use in XML/SVG content.
    """
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def safe_get(data: dict, *keys, default: Any = None) -> Any:
    """
    Safely get nested dictionary values.

    Args:
        data: The dictionary to traverse.
        *keys: Variable number of keys to traverse.
        default: Default value if key path not found.

    Returns:
        The value at the key path, or default if not found.
    """
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, default)
        else:
            return default
    return value if value is not None else default


def safe_value(value: Any, default: str = "—", suffix: str = "") -> str:
    """
    Return value or default placeholder if None.

    Args:
        value: The value to format.
        default: Default string if value is None.
        suffix: Optional suffix to append to the value.

    Returns:
        Formatted string value or default.
    """
    if value is None:
        return default
    return f"{value}{suffix}"


def load_json(path: str, description: str = "file") -> dict:
    """
    Load and parse a JSON file with error handling.

    Args:
        path: Path to the JSON file.
        description: Human-readable description for error messages.

    Returns:
        Parsed JSON as a dictionary.

    Raises:
        SystemExit: If file not found or JSON is invalid.
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {description} not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {description}: {e}", file=sys.stderr)
        sys.exit(1)


def load_schema(schema_name: str) -> Dict:
    """
    Load a JSON schema from the schemas directory.

    Args:
        schema_name: Name of the schema file. Can be provided with the full
                     '.schema.json' suffix (e.g., 'weather.schema.json') or
                     without it (e.g., 'weather'), in which case the suffix
                     will be automatically appended.

    Returns:
        Parsed schema as a dictionary.

    Raises:
        SystemExit: If schema file not found or invalid.
    """
    global _schema_cache

    # Normalize schema name
    if not schema_name.endswith('.schema.json'):
        schema_name = f"{schema_name}.schema.json"

    if schema_name in _schema_cache:
        return _schema_cache[schema_name]

    # Find schema relative to this file's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    schema_path = os.path.join(repo_root, "schemas", schema_name)

    schema = load_json(schema_path, f"Schema file '{schema_name}'")
    _schema_cache[schema_name] = schema
    return schema


def validate_json(data: Dict, schema_name: str, description: str = "data") -> None:
    """
    Validate JSON data against a schema.

    Args:
        data: The data dictionary to validate.
        schema_name: Name of the schema file (e.g., 'weather' or 'weather.schema.json').
        description: Human-readable description for error messages.

    Raises:
        SystemExit: If validation fails or jsonschema is not available.
    """
    if not JSONSCHEMA_AVAILABLE:
        print(
            "Warning: jsonschema not installed, skipping validation",
            file=sys.stderr,
        )
        return

    schema = load_schema(schema_name)

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        print(
            f"Error: {description} validation failed: {e.message}",
            file=sys.stderr,
        )
        # Provide more context for nested errors
        if e.absolute_path:
            path = ".".join(str(p) for p in e.absolute_path)
            print(f"  At path: {path}", file=sys.stderr)
        sys.exit(1)


def load_and_validate_json(
    path: str, schema_name: str, description: str = "file"
) -> Dict:
    """
    Load a JSON file and validate it against a schema.

    Args:
        path: Path to the JSON file.
        schema_name: Name of the schema to validate against.
        description: Human-readable description for error messages.

    Returns:
        Parsed and validated JSON as a dictionary.

    Raises:
        SystemExit: If file not found, JSON invalid, or validation fails.
    """
    data = load_json(path, description)
    validate_json(data, schema_name, description)
    return data


def try_load_json(path: str, description: str = "file") -> Tuple[Optional[Dict], Optional[str]]:
    """
    Try to load a JSON file, returning the data or an error message.

    Unlike load_json, this function does not exit on failure but returns
    None and an error message instead.

    Args:
        path: Path to the JSON file.
        description: Human-readable description for error messages.

    Returns:
        A tuple of (data, error). If successful, data is the parsed JSON
        and error is None. If failed, data is None and error contains
        the error message.
    """
    try:
        with open(path, "r") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"{description} not found: {path}"
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in {description}: {e}"


def try_validate_json(
    data: Dict, schema_name: str, description: str = "data"
) -> Optional[str]:
    """
    Try to validate JSON data against a schema.

    Unlike validate_json, this function does not exit on failure but returns
    an error message instead.

    Args:
        data: The data dictionary to validate.
        schema_name: Name of the schema file.
        description: Human-readable description for error messages.

    Returns:
        None if validation succeeds, or an error message if it fails.
    """
    if not JSONSCHEMA_AVAILABLE:
        return None  # Skip validation if jsonschema not available

    try:
        schema = load_schema(schema_name)
    except SystemExit:
        return f"Failed to load schema: {schema_name}"

    try:
        validate(instance=data, schema=schema)
        return None
    except ValidationError as e:
        error_msg = f"{description} validation failed: {e.message}"
        if e.absolute_path:
            path_str = ".".join(str(p) for p in e.absolute_path)
            error_msg += f" (at path: {path_str})"
        return error_msg


def try_load_and_validate_json(
    path: str, schema_name: str, description: str = "file"
) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Try to load and validate a JSON file.

    Unlike load_and_validate_json, this function does not exit on failure
    but returns None and an error message instead.

    Args:
        path: Path to the JSON file.
        schema_name: Name of the schema to validate against.
        description: Human-readable description for error messages.

    Returns:
        A tuple of (data, error). If successful, data is the parsed and
        validated JSON and error is None. If failed, data is None and
        error contains the error message.
    """
    data, error = try_load_json(path, description)
    if error or data is None:
        return None, error

    validation_error = try_validate_json(data, schema_name, description)
    if validation_error:
        return None, validation_error

    return data, None


def fallback_exists(output_path: str) -> bool:
    """
    Check if a valid fallback SVG exists at the given path.

    Args:
        output_path: Path where the SVG would be written.

    Returns:
        True if a valid SVG file exists at the path, False otherwise.
    """
    path = Path(output_path)
    if not path.exists():
        return False

    # Only SVG files can be valid fallbacks
    if path.suffix.lower() != ".svg":
        return False

    # Check if file has content and looks like a valid SVG
    try:
        content = path.read_text()
        return content.strip().startswith("<svg") and "</svg>" in content
    except (IOError, OSError, UnicodeDecodeError):
        return False


def log_fallback_used(
    card_type: str,
    error: str,
    output_path: str,
) -> None:
    """
    Log that a fallback SVG is being used due to an error.

    This preserves error information for debugging while allowing
    the workflow to continue with the existing SVG.

    Args:
        card_type: Type of card being generated (e.g., "weather", "location").
        error: The error message that triggered the fallback.
        output_path: Path to the fallback SVG being used.
    """
    logger = _get_fallback_logger()
    # Use a formatted message that includes emoji for workflow visibility
    logger.warning(
        "⚠️ FALLBACK: %s card generation failed: %s. "
        "Preserving existing SVG at: %s",
        card_type,
        error,
        output_path,
    )


def handle_error_with_fallback(
    card_type: str,
    error: str,
    output_path: str,
    has_fallback: bool,
) -> bool:
    """
    Handle an error during card generation, using fallback if available.

    This is a helper function to reduce code duplication in card generators
    that have complex generation flows (e.g., multiple input files).

    Args:
        card_type: Type of card being generated (e.g., "weather", "location").
        error: The error message that occurred.
        output_path: Path where the SVG would be written.
        has_fallback: Whether a valid fallback SVG exists at output_path.

    Returns:
        True if fallback was used (caller should return early).
        False is never returned; this function calls sys.exit(1) if no fallback.
    """
    if has_fallback:
        log_fallback_used(card_type, error, output_path)
        return True
    else:
        print(f"Error: {error}", file=sys.stderr)
        print(
            f"No fallback SVG available at {output_path}. Cannot recover.",
            file=sys.stderr,
        )
        sys.exit(1)


def generate_card_with_fallback(
    card_type: str,
    output_path: str,
    json_path: str,
    schema_name: Optional[str],
    generator_func: Callable[[Dict], str],
    description: str = "data file",
) -> bool:
    """
    Generate an SVG card with fallback to the existing card on failure.

    This function attempts to:
    1. Load and optionally validate the JSON data
    2. Generate a new SVG using the provided generator function
    3. Write the SVG to the output path

    If any step fails and a valid SVG already exists at the output path,
    the existing SVG is preserved and the error is logged.

    Args:
        card_type: Type of card (e.g., "weather", "location") for logging.
        output_path: Path where the SVG should be written.
        json_path: Path to the JSON data file.
        schema_name: Optional schema name for validation. If None, skips validation.
        generator_func: Function that takes the loaded JSON dict and returns SVG string.
        description: Human-readable description of the JSON file for error messages.

    Returns:
        True if a new card was generated successfully, False if fallback was used.

    Raises:
        SystemExit: If generation fails and no fallback SVG exists.
    """
    # Check if fallback exists before attempting generation
    has_fallback = fallback_exists(output_path)

    # Try to load and validate JSON
    if schema_name:
        data, error = try_load_and_validate_json(json_path, schema_name, description)
    else:
        data, error = try_load_json(json_path, description)

    if error or data is None:
        if has_fallback:
            log_fallback_used(card_type, error or "No data loaded", output_path)
            return False
        else:
            print(f"Error: {error}", file=sys.stderr)
            print(
                f"No fallback SVG available at {output_path}. Cannot recover.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Try to generate the SVG
    try:
        svg = generator_func(data)
    except Exception as e:
        error_msg = f"SVG generation failed: {e}"
        if has_fallback:
            log_fallback_used(card_type, error_msg, output_path)
            return False
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
            print(
                f"No fallback SVG available at {output_path}. Cannot recover.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Validate the generated SVG looks correct
    if not svg or not svg.strip().startswith("<svg"):
        error_msg = "Generated SVG appears invalid (missing <svg> tag)"
        if has_fallback:
            log_fallback_used(card_type, error_msg, output_path)
            return False
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
            print(
                f"No fallback SVG available at {output_path}. Cannot recover.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Try to write the SVG
    try:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            f.write(svg)
        return True
    except (IOError, OSError) as e:
        error_msg = f"Failed to write SVG: {e}"
        if has_fallback:
            log_fallback_used(card_type, error_msg, output_path)
            return False
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
            print(
                f"No fallback SVG available at {output_path}. Cannot recover.",
                file=sys.stderr,
            )
            sys.exit(1)


def generate_sparkline_path(
    values: List[Optional[float]], width: int = 100, height: int = 25
) -> str:
    """
    Generate SVG path data for a sparkline visualization.

    Args:
        values: List of numeric values (None values are filtered out).
        width: Width of the sparkline in pixels.
        height: Height of the sparkline in pixels.

    Returns:
        SVG path data string (e.g., "M0,10 L5,15 L10,8").
    """
    if not values or len(values) < 2:
        return f"M0,{height // 2} L{width},{height // 2}"

    # Filter out None values and convert to floats
    clean_values = [v for v in values if v is not None]
    if len(clean_values) < 2:
        return f"M0,{height // 2} L{width},{height // 2}"

    min_val = min(clean_values)
    max_val = max(clean_values)
    val_range = max_val - min_val if max_val != min_val else 1

    step = width / (len(clean_values) - 1)
    points = []

    for i, val in enumerate(clean_values):
        x = i * step
        # Normalize to height (invert Y axis for SVG)
        y = height - ((val - min_val) / val_range * height)
        points.append(f"{x:.1f},{y:.1f}")

    return f"M{' L'.join(points)}"


def load_theme(theme_path: Optional[str] = None, theme_name: Optional[str] = None) -> Dict:
    """
    Load theme configuration from JSON file with schema validation.

    Args:
        theme_path: Optional path to theme.json. If not provided,
                   defaults to config/theme.json relative to the repository root.
        theme_name: Optional theme name ('dark' or 'light'). If not provided,
                   uses the default theme or returns the full config for backward compatibility.

    Returns:
        Theme configuration dictionary.

    Note:
        The theme is cached after first load to avoid repeated file reads.
        When theme_name is specified, returns merged theme data with selected theme's
        colors and gradients overriding the defaults. Cache is invalidated when
        switching themes to ensure correct theme data is returned.
        
        Theme validation is performed on first load to ensure structural integrity.
        If validation fails, the script exits with a readable error message.
    """
    global _theme_cache

    # Check cache only if no theme_name specified (backward compatibility)
    if _theme_cache is not None and theme_name is None:
        return _theme_cache

    if theme_path is None:
        # Find theme.json relative to this file's location
        # scripts/lib/utils.py -> scripts/lib -> scripts -> repo root -> config/theme.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        theme_path = os.path.join(repo_root, "config", "theme.json")

    # Load and validate theme config (only if not cached or theme switching requested)
    theme_config = load_and_validate_json(theme_path, "theme", "Theme configuration file")
    
    # If no theme_name specified, return the full config for backward compatibility
    if theme_name is None:
        if _theme_cache is None:
            _theme_cache = theme_config
        return theme_config
    
    # If themes section exists, merge the selected theme
    if "themes" in theme_config and theme_name in theme_config["themes"]:
        selected_theme = theme_config["themes"][theme_name]
        # Create a merged theme by copying base and overriding with selected theme
        merged = theme_config.copy()
        # Override colors and gradients from selected theme
        if "colors" in selected_theme:
            merged["colors"] = selected_theme["colors"]
        if "gradients" in selected_theme:
            merged["gradients"] = selected_theme["gradients"]
        # Update the cache with the selected theme (note: theme switching between calls
        # is not currently supported as it would require cache invalidation logic)
        _theme_cache = merged
        return merged
    
    # Fallback to full config if theme not found
    _theme_cache = theme_config
    return theme_config


def get_theme_color(category: str, name: str, fallback: str = "#ffffff") -> str:
    """
    Get a color value from the theme.

    Args:
        category: Color category (e.g., 'background', 'text', 'accent').
        name: Color name within the category.
        fallback: Default color if not found.

    Returns:
        Hex color string.
    """
    theme = load_theme()
    return safe_get(theme, "colors", category, name, default=fallback)


def get_theme_gradient(name: str, fallback: Optional[List[str]] = None) -> List[str]:
    """
    Get a gradient definition from the theme.

    Args:
        name: Gradient name (e.g., 'sleep', 'readiness', 'activity').
        fallback: Default gradient if not found.

    Returns:
        List of two hex color strings [start, end].
    """
    if fallback is None:
        fallback = ["#1a1a2e", "#16213e"]

    theme = load_theme()
    gradients = theme.get("gradients", {})

    # Check for nested gradient (e.g., weather.clear_day)
    if "." in name:
        parts = name.split(".", 1)
        return safe_get(gradients, parts[0], parts[1], default=fallback)

    return gradients.get(name, fallback)


def get_theme_typography(key: str, fallback: Any = None) -> Any:
    """
    Get a typography value from the theme.

    Args:
        key: Typography key (e.g., 'font_family', 'sizes').
        fallback: Default value if not found.

    Returns:
        Typography value (string for font_family, dict for sizes).
    """
    theme = load_theme()
    return safe_get(theme, "typography", key, default=fallback)


def get_theme_font_size(size_name: str, fallback: int = 12) -> int:
    """
    Get a font size from the theme.

    Args:
        size_name: Size name (e.g., 'xs', 'sm', 'base', 'lg', 'xl', '2xl').
        fallback: Default size if not found.

    Returns:
        Font size in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "typography", "sizes", size_name, default=fallback)


def get_theme_spacing(size_name: str, fallback: int = 10) -> int:
    """
    Get a spacing value from the theme.

    Args:
        size_name: Size name (e.g., 'xs', 'sm', 'md', 'lg', 'xl').
        fallback: Default spacing if not found.

    Returns:
        Spacing value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "spacing", size_name, default=fallback)


def get_theme_card_dimension(dimension: str, card_type: str, fallback: int = 400) -> int:
    """
    Get a card dimension from the theme.

    Args:
        dimension: 'widths' or 'heights'.
        card_type: Card type name (e.g., 'soundcloud', 'weather').
        fallback: Default dimension if not found.

    Returns:
        Dimension value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "cards", dimension, card_type, default=fallback)


def get_theme_border_radius(size: str = "xl", fallback: int = 12) -> int:
    """
    Get a border radius from the theme.

    Args:
        size: Size name (e.g., 'sm', 'md', 'lg', 'xl').
        fallback: Default radius if not found.

    Returns:
        Border radius value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "cards", "border_radius", size, default=fallback)


def get_theme_chart_value(key: str, fallback: int = 10) -> int:
    """
    Get a chart dimension value from the theme.

    Args:
        key: Key name (e.g., 'bar_height', 'bar_gap', 'label_width').
        fallback: Default value if not found.

    Returns:
        Chart dimension value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "cards", "chart", key, default=fallback)


def get_theme_sparkline_value(key: str, fallback: int = 100) -> int:
    """
    Get a sparkline dimension value from the theme.

    Args:
        key: Key name (e.g., 'width', 'height', 'stroke_width').
        fallback: Default value if not found.

    Returns:
        Sparkline dimension value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "cards", "chart", "sparkline", key, default=fallback)


def get_theme_score_bar_value(key: str, fallback: int = 6) -> int:
    """
    Get a score bar dimension value from the theme.

    Args:
        key: Key name (e.g., 'height', 'width', 'text_offset').
        fallback: Default value if not found.

    Returns:
        Score bar dimension value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "cards", "score_bar", key, default=fallback)


def get_theme_radial_bar_value(key: str, fallback: Union[int, float] = 6.0) -> Union[int, float]:
    """
    Get a radial bar value from the theme.

    Args:
        key: Key name (e.g., 'stroke_width', 'opacity', 'ring_spacing').
        fallback: Default value if not found (use float for opacity, int for dimensions).

    Returns:
        Radial bar value (int for dimensions like stroke_width/ring_spacing, 
        float for opacity).
    """
    theme = load_theme()
    return safe_get(theme, "cards", "radial_bar", key, default=fallback)


def get_theme_score_ring_value(key: str, fallback: int = 4) -> int:
    """
    Get a score ring value from the theme.

    Args:
        key: Key name (e.g., 'stroke_width', 'label_offset').
        fallback: Default value if not found.

    Returns:
        Score ring dimension value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "cards", "score_ring", key, default=fallback)


def get_theme_decorative_accent_value(key: str, fallback: int = 4) -> int:
    """
    Get a decorative accent dimension value from the theme.

    Args:
        key: Key name (e.g., 'width', 'x_offset', 'y_offset').
        fallback: Default value if not found.

    Returns:
        Decorative accent dimension value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "cards", "decorative_accent", key, default=fallback)


def get_theme_language_color(language: str, fallback: str = "#8892b0") -> str:
    """
    Get a color for a programming language from the theme.

    Args:
        language: Language name (e.g., 'Python', 'JavaScript').
        fallback: Default color if not found.

    Returns:
        Hex color string.
    """
    theme = load_theme()
    return safe_get(theme, "colors", "languages", language, default=fallback)


def get_theme_status_color(status: str, fallback: str = "#6b7280") -> str:
    """
    Get a color for a status indicator from the theme.

    Args:
        status: Status name (e.g., 'success', 'warning', 'error', 'unknown').
        fallback: Default color if not found.

    Returns:
        Hex color string.
    """
    theme = load_theme()
    return safe_get(theme, "colors", "status", status, default=fallback)


def get_theme_chart_color(name: str, fallback: str = "#2d3748") -> str:
    """
    Get a chart-related color from the theme.

    Args:
        name: Color name (e.g., 'bar_background').
        fallback: Default color if not found.

    Returns:
        Hex color string.
    """
    theme = load_theme()
    return safe_get(theme, "colors", "chart", name, default=fallback)


# Cache for loaded timezone to avoid re-reading file
_timezone_cache: Optional[Dict] = None


def load_timezone(timezone_path: Optional[str] = None) -> Dict:
    """
    Load timezone configuration from JSON file.

    Args:
        timezone_path: Optional path to timezone.json. If not provided,
                      defaults to data/timezone.json relative to the repository root.

    Returns:
        Timezone configuration dictionary with keys:
        - timezone: Timezone identifier (e.g., "America/New_York")
        - utc_offset_hours: UTC offset in hours (e.g., -5)
        - abbreviation: Timezone abbreviation (e.g., "EST")

    Note:
        The timezone is cached after first load to avoid repeated file reads.
        Returns default UTC timezone if file not found.
    """
    global _timezone_cache

    if _timezone_cache is not None:
        return _timezone_cache

    if timezone_path is None:
        # Find timezone.json relative to this file's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        timezone_path = os.path.join(repo_root, "data", "timezone.json")

    try:
        with open(timezone_path, "r") as f:
            _timezone_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default to UTC if timezone file not found
        _timezone_cache = {
            "timezone": "UTC",
            "utc_offset_hours": 0,
            "abbreviation": "UTC"
        }

    return _timezone_cache


def format_timestamp_local(dt_utc_str: str, tzinfo_str: Optional[str] = None) -> str:
    """
    Convert ISO 8601 UTC timestamp to local time display format.

    Args:
        dt_utc_str: UTC timestamp string in ISO 8601 format (e.g., "2025-12-01T06:22:41Z")
        tzinfo_str: Optional timezone identifier (e.g., "America/New_York").
                   If not provided, uses timezone from data/timezone.json.

    Returns:
        Human-readable local time string in format "YYYY-MM-DD HH:MM AM/PM"

    Example:
        >>> format_timestamp_local("2025-12-01T06:22:41Z", "America/New_York")
        "2025-12-01 01:22 AM"
    """
    try:
        # Parse the UTC timestamp
        # Handle various ISO 8601 formats
        dt_utc_str = dt_utc_str.strip()
        if dt_utc_str.endswith('Z'):
            dt_utc_str = dt_utc_str[:-1] + '+00:00'
        elif not (dt_utc_str.endswith('+00:00') or '+' in dt_utc_str[-6:] or dt_utc_str.endswith('Z')):
            # No timezone info, assume UTC
            dt_utc_str = dt_utc_str + '+00:00'

        dt_utc = datetime.fromisoformat(dt_utc_str)

        # Ensure it's UTC
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)

        # Get timezone info - always use loaded timezone offset as the source of truth
        tz_data = load_timezone()
        loaded_timezone = tz_data.get("timezone", "UTC")
        loaded_offset = tz_data.get("utc_offset_hours", 0)

        if tzinfo_str is None:
            # Use loaded timezone
            offset_hours = loaded_offset
        elif tzinfo_str == loaded_timezone:
            # Requested timezone matches loaded, use loaded offset
            offset_hours = loaded_offset
        else:
            # Requested timezone differs - use loaded timezone offset as fallback
            # This ensures consistent behavior even if the requested timezone differs
            offset_hours = loaded_offset

        # Apply timezone offset manually (since zoneinfo may not be available)
        offset = timedelta(hours=offset_hours)
        dt_local = dt_utc + offset

        # Format as "YYYY-MM-DD HH:MM AM/PM"
        formatted = dt_local.strftime("%Y-%m-%d %I:%M %p")

        return formatted

    except (ValueError, AttributeError, TypeError):
        # Return original string if parsing fails
        return dt_utc_str


def format_timestamp_iso(dt: Optional[datetime] = None) -> str:
    """
    Format a datetime object to ISO 8601 UTC format with Zulu time.

    Args:
        dt: datetime object to format. If None, uses current UTC time.

    Returns:
        ISO 8601 formatted string (e.g., "2025-12-01T06:22:41Z")
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse an ISO 8601 timestamp string to a UTC datetime object.
    
    Handles various timestamp formats:
    - With 'Z' suffix (e.g., "2025-12-01T06:22:41Z")
    - With timezone offset (e.g., "2025-12-01T06:22:41+00:00")
    - Without timezone (assumes UTC)
    
    Args:
        timestamp_str: ISO 8601 timestamp string
    
    Returns:
        datetime object in UTC, or None if parsing fails
    
    Example:
        >>> dt = parse_timestamp("2025-12-01T06:22:41Z")
        >>> dt.tzinfo == timezone.utc
        True
    """
    try:
        timestamp_str = timestamp_str.strip()
        
        # Normalize timestamp format
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
        elif not (timestamp_str.endswith('+00:00') or '+' in timestamp_str[-6:]):
            # No timezone info, assume UTC
            timestamp_str = timestamp_str + '+00:00'
        
        dt = datetime.fromisoformat(timestamp_str)
        
        # Ensure it's UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt
        
    except (ValueError, AttributeError, TypeError):
        return None


def format_time_since(timestamp_str: str) -> str:
    """
    Calculate and format the time elapsed since a given timestamp.
    
    Args:
        timestamp_str: ISO 8601 timestamp string (e.g., "2025-12-01T06:22:41Z")
    
    Returns:
        Human-readable time elapsed string (e.g., "2h ago", "5m ago", "just now")
    
    Example:
        >>> format_time_since("2025-12-01T06:22:41Z")
        "2h ago"
    """
    dt = parse_timestamp(timestamp_str)
    if dt is None:
        return "unknown"
    
    # Calculate time difference
    now = datetime.now(timezone.utc)
    delta = now - dt
    
    # Format based on duration
    total_seconds = int(delta.total_seconds())
    
    if total_seconds < 60:
        return "just now"
    elif total_seconds < 3600:  # Less than 1 hour
        minutes = total_seconds // 60
        return f"{minutes}m ago"
    elif total_seconds < 86400:  # Less than 1 day
        hours = total_seconds // 3600
        return f"{hours}h ago"
    else:  # 1 day or more
        days = total_seconds // 86400
        return f"{days}d ago"


def is_data_stale(timestamp_str: str, stale_threshold_hours: int = 24) -> bool:
    """
    Check if data is stale based on the timestamp.
    
    Args:
        timestamp_str: ISO 8601 timestamp string (e.g., "2025-12-01T06:22:41Z")
        stale_threshold_hours: Number of hours after which data is considered stale (default: 24)
    
    Returns:
        True if the data is older than the threshold, False otherwise
    
    Example:
        >>> is_data_stale("2025-12-01T06:22:41Z", 24)
        True  # if more than 24 hours old
    """
    dt = parse_timestamp(timestamp_str)
    if dt is None:
        # If we can't parse the timestamp, consider it stale to be safe
        return True
    
    # Calculate time difference
    now = datetime.now(timezone.utc)
    delta = now - dt
    
    # Check if data is stale
    return delta.total_seconds() > (stale_threshold_hours * 3600)


def generate_staleness_badge_svg(
    updated_at: str,
    card_width: int,
    font_family: str = "'Segoe UI', Arial, sans-serif",
    font_size: int = 8,
    x_offset: int = 10,
    y_offset: int = 10,
    stale_threshold_hours: int = 24,
) -> str:
    """
    Generate SVG markup for a staleness badge showing data freshness.
    
    Fresh data (<24h): Shows time in muted color without icon
    Stale data (≥24h): Shows "⚠️" icon in warning color
    
    Args:
        updated_at: ISO 8601 timestamp string
        card_width: Width of the card in pixels (badge positioned relative to right edge)
        font_family: Font family for badge text
        font_size: Font size for badge text
        x_offset: Offset from right edge of card
        y_offset: Offset from top of card
        stale_threshold_hours: Hours after which data is considered stale
    
    Returns:
        SVG markup string for the staleness badge, or empty string if no timestamp
    
    Example:
        >>> badge = generate_staleness_badge_svg("2025-12-03T19:45:45Z", 480)
        >>> "Updated:" in badge
        True
    """
    if not updated_at:
        return ""
    
    time_since = format_time_since(updated_at)
    is_stale = is_data_stale(updated_at, stale_threshold_hours=stale_threshold_hours)
    
    # Use warning color if data is stale
    if is_stale:
        badge_color = "#ff6b6b"  # Warning/error color
        badge_icon = "⚠️ "
    else:
        badge_color = "#4a5568"  # Muted text color
        badge_icon = ""
    
    time_since_escaped = escape_xml(time_since)
    x_position = card_width - x_offset
    
    return f'''
  <!-- Staleness Badge -->
  <g transform="translate({x_position}, {y_offset})">
    <text x="0" y="12" font-family="{font_family}" font-size="{font_size}" fill="{badge_color}" text-anchor="end">
      {badge_icon}Updated: {time_since_escaped}
    </text>
  </g>'''


def format_large_number(count: int) -> str:
    """
    Format large numbers with K/M suffixes for readability.
    
    Args:
        count: The number to format.
    
    Returns:
        Formatted string with K/M suffix (e.g., "1.5K", "2.3M").
    
    Examples:
        >>> format_large_number(1500)
        "1.5K"
        >>> format_large_number(2_300_000)
        "2.3M"
        >>> format_large_number(500)
        "500"
    """
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def format_duration_ms(duration_ms: int) -> str:
    """
    Convert milliseconds to MM:SS format.
    
    Args:
        duration_ms: Duration in milliseconds.
    
    Returns:
        Formatted duration string (e.g., "3:45", "12:03").
    
    Examples:
        >>> format_duration_ms(225000)
        "3:45"
        >>> format_duration_ms(60000)
        "1:00"
    """
    seconds = duration_ms // 1000
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"


# Image optimization utilities

# Try to import Pillow for image optimization
try:
    from PIL import Image
    import io
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


def get_image_optimization_settings() -> Dict[str, Union[int, bool]]:
    """
    Get image optimization settings from theme configuration.

    Returns:
        Dictionary with optimization settings:
        - jpeg_quality: JPEG compression quality (1-100, default 85)
        - png_colors: Number of colors for PNG quantization (default 256)
        - max_width: Maximum width for image resizing (default 600)
        - max_height: Maximum height for image resizing (default 400)
        - enabled: Whether optimization is enabled (default True)
    """
    theme = load_theme()
    optimization = theme.get("image_optimization", {})
    return {
        "jpeg_quality": optimization.get("jpeg_quality", 85),
        "png_colors": optimization.get("png_colors", 256),
        "max_width": optimization.get("max_width", 600),
        "max_height": optimization.get("max_height", 400),
        "enabled": optimization.get("enabled", True),
    }


def optimize_image(
    image_data: bytes,
    image_format: str,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    jpeg_quality: Optional[int] = None,
    png_colors: Optional[int] = None,
) -> bytes:
    """
    Optimize an image for embedding in SVG.

    This function reduces image file size while preserving visual quality by:
    - Resizing large images to a maximum dimension
    - Compressing JPEG images with configurable quality
    - Quantizing PNG images to reduce color palette

    Args:
        image_data: Raw image bytes.
        image_format: Image format ('jpeg', 'jpg', or 'png').
        max_width: Maximum width in pixels. Uses theme default if None.
        max_height: Maximum height in pixels. Uses theme default if None.
        jpeg_quality: JPEG quality (1-100). Uses theme default if None.
        png_colors: Number of colors for PNG quantization. Uses theme default if None.

    Returns:
        Optimized image bytes. Returns original if Pillow not available
        or optimization disabled.
    """
    if not PILLOW_AVAILABLE:
        print("Warning: Pillow not installed, skipping image optimization", file=sys.stderr)
        return image_data

    settings = get_image_optimization_settings()
    if not settings["enabled"]:
        return image_data

    # Use provided values or fall back to theme settings
    max_width = max_width if max_width is not None else settings["max_width"]
    max_height = max_height if max_height is not None else settings["max_height"]
    jpeg_quality = jpeg_quality if jpeg_quality is not None else settings["jpeg_quality"]
    png_colors = png_colors if png_colors is not None else settings["png_colors"]

    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(image_data))

        # Get original size for logging
        original_size = len(image_data)
        
        # Track if we need to resize
        needs_resize = img.width > max_width or img.height > max_height

        # Normalize format
        fmt = image_format.lower()
        
        # For PNG, try multiple optimization strategies and use the smallest result
        if fmt == "png":
            candidates = []
            
            # Strategy 1: Quantize + optimize (often best for photos/maps)
            # Skip quantization for RGBA images to preserve transparency
            try:
                img_work = Image.open(io.BytesIO(image_data))
                if needs_resize:
                    img_work.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                if img_work.mode == "RGBA":
                    # Preserve transparency - skip quantization, just optimize
                    output1 = io.BytesIO()
                    img_work.save(output1, format="PNG", optimize=True)
                    candidates.append(("rgba_optimized", output1.getvalue()))
                elif img_work.mode == "RGB":
                    img_quant = img_work.quantize(
                        colors=png_colors, method=Image.Quantize.MEDIANCUT
                    )
                    output1 = io.BytesIO()
                    img_quant.save(output1, format="PNG", optimize=True)
                    candidates.append(("quantized", output1.getvalue()))
                elif img_work.mode != "P":
                    img_quant = img_work.convert("RGB").quantize(
                        colors=png_colors, method=Image.Quantize.MEDIANCUT
                    )
                    output1 = io.BytesIO()
                    img_quant.save(output1, format="PNG", optimize=True)
                    candidates.append(("quantized", output1.getvalue()))
                else:
                    output1 = io.BytesIO()
                    img_work.save(output1, format="PNG", optimize=True)
                    candidates.append(("palette_optimized", output1.getvalue()))
            except (OSError, ValueError):
                pass
            
            # Strategy 2: Just resize + optimize (better for some images)
            try:
                img_work = Image.open(io.BytesIO(image_data))
                if needs_resize:
                    img_work.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                output2 = io.BytesIO()
                img_work.save(output2, format="PNG", optimize=True)
                candidates.append(("resized", output2.getvalue()))
            except (OSError, ValueError):
                pass
            
            # Strategy 3: Original (if already optimal)
            candidates.append(("original", image_data))
            
            # Pick the smallest
            best_name, best_data = min(candidates, key=lambda x: len(x[1]))
            optimized_data = best_data
            optimized_size = len(optimized_data)
            
        elif fmt in ["jpeg", "jpg"]:
            # Resize if needed
            if needs_resize:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary (JPEG doesn't support alpha)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")  # type: ignore[assignment]
            
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=jpeg_quality, optimize=True)
            optimized_data = output.getvalue()
            optimized_size = len(optimized_data)
            
            # Use original if optimization didn't help
            if optimized_size >= original_size:
                optimized_data = image_data
                optimized_size = original_size
        else:
            # Unknown format, return original
            return image_data

        # Log optimization results
        if optimized_size < original_size:
            reduction_pct = ((original_size - optimized_size) / original_size) * 100
            print(
                f"Image optimized: {original_size:,} -> {optimized_size:,} bytes "
                f"({reduction_pct:.1f}% reduction)",
                file=sys.stderr,
            )
        else:
            print(
                f"Image optimization skipped (no size reduction): "
                f"{original_size:,} bytes",
                file=sys.stderr,
            )

        return optimized_data

    except (OSError, IOError, ValueError) as e:
        print(f"Warning: Image optimization failed: {e}", file=sys.stderr)
        return image_data


def optimize_image_file(
    file_path: str,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    jpeg_quality: Optional[int] = None,
    png_colors: Optional[int] = None,
) -> bytes:
    """
    Read and optimize an image file for embedding in SVG.

    Args:
        file_path: Path to the image file.
        max_width: Maximum width in pixels.
        max_height: Maximum height in pixels.
        jpeg_quality: JPEG quality (1-100).
        png_colors: Number of colors for PNG quantization.

    Returns:
        Optimized image bytes.

    Raises:
        FileNotFoundError: If the image file doesn't exist.
        IOError: If the file cannot be read.
    """
    from pathlib import Path

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")

    # Determine format from extension
    suffix = path.suffix.lower()
    if suffix in [".jpg", ".jpeg"]:
        image_format = "jpeg"
    elif suffix == ".png":
        image_format = "png"
    else:
        image_format = suffix.lstrip(".")

    # Read file
    with open(path, "rb") as f:
        image_data = f.read()

    # Optimize
    return optimize_image(
        image_data,
        image_format,
        max_width=max_width,
        max_height=max_height,
        jpeg_quality=jpeg_quality,
        png_colors=png_colors,
    )


def safe_write_json(data: Dict, output_path: str, indent: int = 2) -> None:
    """
    Safely write JSON data to a file using the temp→validate→move pattern.
    
    This function implements the repository-wide safe JSON write pattern:
    1. Write to a temporary file
    2. Validate the JSON can be loaded
    3. Atomically move to the final location
    4. Clean up on failure
    
    Args:
        data: Dictionary to write as JSON.
        output_path: Path where the JSON file should be written.
        indent: JSON indentation level (default: 2).
    
    Raises:
        IOError: If file cannot be written.
        ValueError: If data cannot be serialized to JSON.
    """
    output = Path(output_path)
    temp_path = output.parent / f"{output.name}.tmp"
    
    try:
        # Ensure parent directory exists
        output.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temporary file
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
        
        # Validate the temp file can be loaded
        with open(temp_path, 'r', encoding='utf-8') as f:
            json.load(f)
        
        # Atomic move to final location
        temp_path.replace(output)
        
    except (IOError, OSError, ValueError, json.JSONDecodeError) as e:
        # Clean up temp file on failure (missing_ok=True available in Python 3.8+)
        temp_path.unlink(missing_ok=True)
        raise IOError(f"Failed to write JSON to {output_path}: {e}") from e
