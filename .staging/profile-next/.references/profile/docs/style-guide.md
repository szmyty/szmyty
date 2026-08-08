# Style Guide

This document outlines the code style conventions, theming system, and visual design patterns used throughout the repository.

## Code Style

### Shell Scripts

All shell scripts follow these conventions:

- **Strict mode**: Use `set -euo pipefail` at the start
- **Error logging**: Log errors to stderr with `>&2`
- **Function documentation**: Include comments explaining function purpose
- **Local variables**: Use `local` keyword for function-scoped variables
- **Exit codes**: Return meaningful exit codes for error handling

Example:
```bash
#!/usr/bin/env bash
set -euo pipefail

# Fetch user location from GitHub API
get_github_location() {
    local owner="$1"
    echo "Fetching location for $owner" >&2
    # ... implementation
}
```

### Python Scripts

Python code follows these conventions:

- **Docstrings**: Use Google-style docstrings for all functions
- **Type hints**: Include type annotations for function parameters and returns
- **Error handling**: Use try/except with proper error messages
- **Imports**: Standard library first, then third-party, then local modules

Example:
```python
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
    return str(text).replace("&", "&amp;").replace("<", "&lt;")
```

### Naming Conventions

- **Shell scripts**: `fetch-*.sh` for data fetching, `generate-*.py` for SVG generation
- **Python functions**: `snake_case`
- **Python classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **JSON keys**: `snake_case`

## Theme System

### Configuration File

All visual styling is centralized in `config/theme.json`. This enables consistent styling across all cards and simplifies theme changes.

### Color Palette

#### Background Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `background.primary` | `#1a1a2e` | Main card background |
| `background.secondary` | `#16213e` | Secondary backgrounds |
| `background.dark` | `#0f0f23` | Darkest backgrounds |
| `background.panel` | `#1e1e2e` | Panel backgrounds |
| `background.panel_sleep` | `#1a1a3e` | Sleep metric panels |
| `background.panel_readiness` | `#1a2e2e` | Readiness metric panels |
| `background.panel_activity` | `#2e2a1a` | Activity metric panels |

#### Text Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `text.primary` | `#ffffff` | Main text |
| `text.secondary` | `#8892b0` | Secondary text |
| `text.muted` | `#4a5568` | Muted/footnote text |
| `text.accent` | `#64ffda` | Accent/highlight text |

#### Accent Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `accent.teal` | `#64ffda` | Primary accent |
| `accent.cyan` | `#4ecdc4` | Secondary accent |
| `accent.orange` | `#ff5500` | SoundCloud brand |
| `accent.sleep` | `#4facfe` | Sleep metrics |
| `accent.readiness` | `#38ef7d` | Readiness metrics |
| `accent.activity` | `#f5576c` | Activity metrics |

#### Score Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `scores.high` | `#4ade80` | Good scores (≥70) |
| `scores.medium` | `#fbbf24` | Medium scores (50-69) |
| `scores.low` | `#f87171` | Low scores (<50) |

### Gradients

Gradients are defined for backgrounds and metric categories:

```json
{
  "gradients": {
    "background": {
      "default": ["#1a1a2e", "#16213e"],
      "dark": ["#0f0f23", "#1a1a2e"]
    },
    "sleep": ["#667eea", "#764ba2"],
    "readiness": ["#11998e", "#38ef7d"],
    "activity": ["#f093fb", "#f5576c"]
  }
}
```

### Typography

#### Font Family
- Primary: `'Segoe UI', Arial, sans-serif`
- Emoji/Icons: `Arial, sans-serif`

#### Font Sizes (pixels)
| Token | Size | Usage |
|-------|------|-------|
| `xs` | 8 | Extra small labels |
| `sm` | 9 | Small text |
| `base` | 10 | Default text |
| `md` | 11 | Medium text |
| `lg` | 12 | Large text |
| `xl` | 14 | Headers |
| `2xl` | 16 | Large headers |
| `3xl` | 18 | Extra large headers |

### Spacing

Spacing values in pixels:
| Token | Value |
|-------|-------|
| `xs` | 4 |
| `sm` | 8 |
| `md` | 10 |
| `lg` | 12 |
| `xl` | 15 |
| `2xl` | 20 |
| `3xl` | 25 |

### Card Dimensions

All cards use standardized dimensions:

| Card Type | Width | Height |
|-----------|-------|--------|
| SoundCloud | 480 | 144 |
| Weather | 480 | 230 |
| Mood | 480 | 250 |
| Health Dashboard | 480 | 365 |
| Location | 480 | 400 |

### Border Radius

| Size | Value |
|------|-------|
| `sm` | 3 |
| `md` | 6 |
| `lg` | 8 |
| `xl` | 12 |

## SVG Patterns

### Document Structure

All SVG cards follow this structure:

```xml
<svg xmlns="..." width="..." height="..." viewBox="...">
  <defs>
    <!-- Gradients -->
    <linearGradient id="bg-gradient">...</linearGradient>
    <!-- Filters -->
    <filter id="glow">...</filter>
  </defs>
  
  <!-- Background -->
  <rect fill="url(#bg-gradient)"/>
  <rect fill="none" stroke="..."/>
  
  <!-- Content -->
  ...
  
  <!-- Decorative accent -->
  <rect x="..." y="..." width="4"/>
  
  <!-- Footer -->
  <text>...</text>
</svg>
```

### Using CardBase

For new card generators, extend the `CardBase` class:

```python
from lib.card_base import CardBase

class WeatherCard(CardBase):
    def __init__(self):
        super().__init__("weather")  # Card type from theme
    
    def generate_content(self) -> str:
        # Return card-specific SVG content
        return """
          <text x="20" y="40" fill="#fff">Weather</text>
        """

# Usage
card = WeatherCard()
svg = card.generate_svg(footer_text="Updated 2025-01-01")
card.write_svg("output.svg", svg)
```

### SVG Best Practices

1. **Use `<defs>`** for reusable elements (gradients, filters)
2. **Include proper namespaces** (`xmlns`, `xmlns:xlink`)
3. **Escape text content** using `escape_xml()` function
4. **Use consistent styling** from theme configuration
5. **Apply filters sparingly** (glow, shadow) for performance

## JSON Data Formats

### Date/Time Format

Use ISO 8601 format with timezone:
```
2025-12-01T06:22:41Z
```

### Null Handling

Always include fields with `null` for missing data rather than omitting them:
```json
{
  "temperature": 72,
  "humidity": null
}
```

### Units

Store values in SI units, convert at display time:
- Temperature: Celsius
- Distance: Meters
- Weight: Kilograms

## Commit Message Format

Use emoji prefixes for different card types:
- 📍 Location updates
- 🌦️ Weather updates
- 🎵 SoundCloud updates
- 🧬 Oura health updates

### Examples

```
📍 Update location card for San Francisco
🌦️ Update weather card for Boston, MA
🎵 Update SoundCloud card: New Track Title
🧬 Update Oura health dashboard: Cosmic Clarity (85/100)
```

The emoji prefix indicates the card type, followed by a brief description of the update. For Oura updates, the mood name and score are included.
