#!/usr/bin/env python3
"""
Unit tests for theme.json schema validation.
"""

import pytest
import sys
import os
import json
import tempfile
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from lib.utils import load_theme, load_schema, try_validate_json


class TestThemeSchema:
    """Tests for theme schema validation."""

    @pytest.fixture
    def theme_schema(self):
        """Load the theme schema."""
        return load_schema("theme")

    @pytest.fixture
    def valid_theme(self):
        """Load the actual theme.json as a valid example."""
        repo_root = Path(__file__).parent.parent
        theme_path = repo_root / "config" / "theme.json"
        with open(theme_path) as f:
            return json.load(f)

    def test_schema_exists(self):
        """Test that theme schema file exists."""
        repo_root = Path(__file__).parent.parent
        schema_path = repo_root / "schemas" / "theme.schema.json"
        assert schema_path.exists(), "theme.schema.json should exist"

    def test_schema_is_valid_json(self, theme_schema):
        """Test that theme schema is valid JSON."""
        assert isinstance(theme_schema, dict)
        assert "$schema" in theme_schema
        assert theme_schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"

    def test_actual_theme_validates(self, valid_theme, theme_schema):
        """Test that the actual theme.json validates against the schema."""
        error = try_validate_json(valid_theme, "theme", "theme.json")
        assert error is None, f"Theme validation should succeed but got: {error}"

    def test_minimal_valid_theme(self, theme_schema):
        """Test that a minimal valid theme passes validation."""
        minimal_theme = {
            "colors": {
                "background": {
                    "primary": "#1a1a2e",
                    "secondary": "#16213e",
                    "dark": "#0f0f23",
                    "panel": "#1e1e2e"
                },
                "text": {
                    "primary": "#ffffff",
                    "secondary": "#8892b0",
                    "muted": "#4a5568",
                    "accent": "#64ffda"
                },
                "accent": {
                    "teal": "#64ffda",
                    "cyan": "#4ecdc4",
                    "orange": "#ff5500"
                },
                "scores": {
                    "high": "#4ade80",
                    "medium": "#fbbf24",
                    "low": "#f87171"
                }
            },
            "gradients": {
                "background": {
                    "default": ["#1a1a2e", "#16213e"],
                    "dark": ["#0f0f23", "#1a1a2e"]
                }
            },
            "typography": {
                "font_family": "Arial, sans-serif",
                "sizes": {
                    "xs": 8,
                    "sm": 9,
                    "base": 10,
                    "md": 11,
                    "lg": 12,
                    "xl": 14
                }
            },
            "spacing": {
                "xs": 4,
                "sm": 8,
                "md": 10,
                "lg": 12,
                "xl": 15
            },
            "cards": {
                "border_radius": {
                    "sm": 3,
                    "md": 6,
                    "lg": 8,
                    "xl": 12
                },
                "widths": {},
                "heights": {}
            }
        }
        error = try_validate_json(minimal_theme, "theme", "minimal theme")
        assert error is None, f"Minimal theme should validate but got: {error}"

    def test_missing_required_colors(self, theme_schema):
        """Test that missing required color fields fails validation."""
        invalid_theme = {
            "colors": {
                "background": {"primary": "#000000"}  # Missing required fields
            },
            "gradients": {
                "background": {
                    "default": ["#1a1a2e", "#16213e"],
                    "dark": ["#0f0f23", "#1a1a2e"]
                }
            },
            "typography": {
                "font_family": "Arial",
                "sizes": {"xs": 8, "sm": 9, "base": 10, "md": 11, "lg": 12, "xl": 14}
            },
            "spacing": {"xs": 4, "sm": 8, "md": 10, "lg": 12, "xl": 15},
            "cards": {
                "border_radius": {"sm": 3, "md": 6, "lg": 8, "xl": 12},
                "widths": {},
                "heights": {}
            }
        }
        error = try_validate_json(invalid_theme, "theme", "invalid theme")
        assert error is not None, "Theme with missing color fields should fail validation"
        assert "required" in error.lower() or "text" in error.lower()

    def test_invalid_hex_color(self, theme_schema):
        """Test that invalid hex color fails validation."""
        invalid_theme = {
            "colors": {
                "background": {
                    "primary": "not-a-hex-color",  # Invalid hex color
                    "secondary": "#16213e",
                    "dark": "#0f0f23",
                    "panel": "#1e1e2e"
                },
                "text": {
                    "primary": "#ffffff",
                    "secondary": "#8892b0",
                    "muted": "#4a5568",
                    "accent": "#64ffda"
                },
                "accent": {
                    "teal": "#64ffda",
                    "cyan": "#4ecdc4",
                    "orange": "#ff5500"
                },
                "scores": {
                    "high": "#4ade80",
                    "medium": "#fbbf24",
                    "low": "#f87171"
                }
            },
            "gradients": {
                "background": {
                    "default": ["#1a1a2e", "#16213e"],
                    "dark": ["#0f0f23", "#1a1a2e"]
                }
            },
            "typography": {
                "font_family": "Arial",
                "sizes": {"xs": 8, "sm": 9, "base": 10, "md": 11, "lg": 12, "xl": 14}
            },
            "spacing": {"xs": 4, "sm": 8, "md": 10, "lg": 12, "xl": 15},
            "cards": {
                "border_radius": {"sm": 3, "md": 6, "lg": 8, "xl": 12},
                "widths": {},
                "heights": {}
            }
        }
        error = try_validate_json(invalid_theme, "theme", "invalid theme")
        assert error is not None, "Theme with invalid hex color should fail validation"

    def test_invalid_gradient_format(self, theme_schema):
        """Test that invalid gradient format fails validation."""
        invalid_theme = {
            "colors": {
                "background": {
                    "primary": "#1a1a2e",
                    "secondary": "#16213e",
                    "dark": "#0f0f23",
                    "panel": "#1e1e2e"
                },
                "text": {
                    "primary": "#ffffff",
                    "secondary": "#8892b0",
                    "muted": "#4a5568",
                    "accent": "#64ffda"
                },
                "accent": {
                    "teal": "#64ffda",
                    "cyan": "#4ecdc4",
                    "orange": "#ff5500"
                },
                "scores": {
                    "high": "#4ade80",
                    "medium": "#fbbf24",
                    "low": "#f87171"
                }
            },
            "gradients": {
                "background": {
                    "default": ["#1a1a2e"],  # Should have 2 colors, not 1
                    "dark": ["#0f0f23", "#1a1a2e"]
                }
            },
            "typography": {
                "font_family": "Arial",
                "sizes": {"xs": 8, "sm": 9, "base": 10, "md": 11, "lg": 12, "xl": 14}
            },
            "spacing": {"xs": 4, "sm": 8, "md": 10, "lg": 12, "xl": 15},
            "cards": {
                "border_radius": {"sm": 3, "md": 6, "lg": 8, "xl": 12},
                "widths": {},
                "heights": {}
            }
        }
        error = try_validate_json(invalid_theme, "theme", "invalid theme")
        assert error is not None, "Theme with invalid gradient should fail validation"

    def test_negative_font_size(self, theme_schema):
        """Test that negative font sizes fail validation."""
        invalid_theme = {
            "colors": {
                "background": {
                    "primary": "#1a1a2e",
                    "secondary": "#16213e",
                    "dark": "#0f0f23",
                    "panel": "#1e1e2e"
                },
                "text": {
                    "primary": "#ffffff",
                    "secondary": "#8892b0",
                    "muted": "#4a5568",
                    "accent": "#64ffda"
                },
                "accent": {
                    "teal": "#64ffda",
                    "cyan": "#4ecdc4",
                    "orange": "#ff5500"
                },
                "scores": {
                    "high": "#4ade80",
                    "medium": "#fbbf24",
                    "low": "#f87171"
                }
            },
            "gradients": {
                "background": {
                    "default": ["#1a1a2e", "#16213e"],
                    "dark": ["#0f0f23", "#1a1a2e"]
                }
            },
            "typography": {
                "font_family": "Arial",
                "sizes": {
                    "xs": -1,  # Invalid negative size
                    "sm": 9,
                    "base": 10,
                    "md": 11,
                    "lg": 12,
                    "xl": 14
                }
            },
            "spacing": {"xs": 4, "sm": 8, "md": 10, "lg": 12, "xl": 15},
            "cards": {
                "border_radius": {"sm": 3, "md": 6, "lg": 8, "xl": 12},
                "widths": {},
                "heights": {}
            }
        }
        error = try_validate_json(invalid_theme, "theme", "invalid theme")
        assert error is not None, "Theme with negative font size should fail validation"

    def test_missing_typography(self, theme_schema):
        """Test that missing typography section fails validation."""
        invalid_theme = {
            "colors": {
                "background": {
                    "primary": "#1a1a2e",
                    "secondary": "#16213e",
                    "dark": "#0f0f23",
                    "panel": "#1e1e2e"
                },
                "text": {
                    "primary": "#ffffff",
                    "secondary": "#8892b0",
                    "muted": "#4a5568",
                    "accent": "#64ffda"
                },
                "accent": {
                    "teal": "#64ffda",
                    "cyan": "#4ecdc4",
                    "orange": "#ff5500"
                },
                "scores": {
                    "high": "#4ade80",
                    "medium": "#fbbf24",
                    "low": "#f87171"
                }
            },
            "gradients": {
                "background": {
                    "default": ["#1a1a2e", "#16213e"],
                    "dark": ["#0f0f23", "#1a1a2e"]
                }
            },
            # Missing typography
            "spacing": {"xs": 4, "sm": 8, "md": 10, "lg": 12, "xl": 15},
            "cards": {
                "border_radius": {"sm": 3, "md": 6, "lg": 8, "xl": 12},
                "widths": {},
                "heights": {}
            }
        }
        error = try_validate_json(invalid_theme, "theme", "invalid theme")
        assert error is not None, "Theme without typography should fail validation"
        assert "typography" in error.lower()


class TestThemeLoadWithValidation:
    """Tests for load_theme with validation."""

    def test_load_theme_validates_successfully(self):
        """Test that load_theme validates the actual theme file."""
        # This should not raise an error
        theme = load_theme()
        assert isinstance(theme, dict)
        assert "colors" in theme
        assert "gradients" in theme

    def test_load_theme_fails_with_invalid_file(self):
        """Test that load_theme fails with invalid theme file."""
        import lib.utils
        
        invalid_theme = {
            "colors": {
                "background": {"primary": "#000000"}  # Missing many required fields
            }
        }

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_theme, f)
            temp_path = f.name

        # Clear the theme cache to ensure validation happens
        lib.utils._theme_cache = None
        
        # Try to load invalid theme - should raise SystemExit
        with pytest.raises(SystemExit) as exc_info:
            load_theme(theme_path=temp_path)
        
        assert exc_info.value.code == 1

        # Cleanup
        os.unlink(temp_path)
        # Reset cache for subsequent tests
        lib.utils._theme_cache = None

    def test_theme_cache_preserves_validation(self):
        """Test that cached theme was validated on first load."""
        # First call validates and caches
        theme1 = load_theme()
        
        # Second call uses cache (validation already done)
        theme2 = load_theme()
        
        # Should be the same object (cached)
        assert theme1 is theme2
        assert "colors" in theme2
