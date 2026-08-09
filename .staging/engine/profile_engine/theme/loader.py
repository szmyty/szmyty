"""Theme loading and management for profile cards."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

# Cache for loaded theme to avoid re-reading file
_theme_cache: Optional[Dict] = None


def load_theme(theme_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load theme configuration from JSON file.
    
    Args:
        theme_path: Path to theme.json file. If None, uses default location.
        
    Returns:
        Dictionary containing theme configuration
    """
    global _theme_cache
    
    if _theme_cache is not None:
        return _theme_cache
    
    if theme_path is None:
        # Default to config/theme.json relative to repository root
        # When running as installed package, this will be relative to current working directory
        theme_path = Path("config/theme.json")
    
    try:
        with open(theme_path, "r") as f:
            _theme_cache = json.load(f)
            return _theme_cache
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Return minimal default theme if file not found
        print(f"Warning: Could not load theme from {theme_path}: {e}")
        _theme_cache = {
            "colors": {
                "light": {"primary": "#0969da", "background": "#ffffff", "text": "#1f2328"},
                "dark": {"primary": "#58a6ff", "background": "#0d1117", "text": "#e6edf3"}
            },
            "typography": {"font-family": "system-ui, sans-serif"},
            "spacing": {"base": 16},
            "borders": {"radius": 6}
        }
        return _theme_cache


def get_theme_color(theme: Dict[str, Any], color_key: str, mode: str = "light") -> str:
    """
    Get a theme color value.
    
    Args:
        theme: Theme dictionary
        color_key: Key for the color (e.g., 'primary', 'background')
        mode: Theme mode ('light' or 'dark')
        
    Returns:
        Color value as string
    """
    colors = theme.get("colors", {}).get(mode, {})
    return colors.get(color_key, "#000000")


def get_theme_gradient(theme: Dict[str, Any], gradient_key: str, mode: str = "light") -> str:
    """
    Get a theme gradient definition.
    
    Args:
        theme: Theme dictionary
        gradient_key: Key for the gradient
        mode: Theme mode ('light' or 'dark')
        
    Returns:
        Gradient definition as string
    """
    gradients = theme.get("gradients", {}).get(mode, {})
    return gradients.get(gradient_key, "")


def get_theme_typography(theme: Dict[str, Any], key: str) -> str:
    """
    Get a typography value from theme.
    
    Args:
        theme: Theme dictionary
        key: Typography key (e.g., 'font-family')
        
    Returns:
        Typography value as string
    """
    return theme.get("typography", {}).get(key, "system-ui, sans-serif")


def get_theme_font_size(theme: Dict[str, Any], size_key: str) -> int:
    """
    Get a font size from theme.
    
    Args:
        theme: Theme dictionary
        size_key: Size key (e.g., 'base', 'large')
        
    Returns:
        Font size as integer
    """
    sizes = theme.get("typography", {}).get("sizes", {})
    return sizes.get(size_key, 14)


def get_theme_spacing(theme: Dict[str, Any]) -> int:
    """
    Get base spacing from theme.
    
    Args:
        theme: Theme dictionary
        
    Returns:
        Base spacing as integer
    """
    return theme.get("spacing", {}).get("base", 16)


def get_theme_border_radius(theme: Dict[str, Any]) -> int:
    """
    Get border radius from theme.
    
    Args:
        theme: Theme dictionary
        
    Returns:
        Border radius as integer
    """
    return theme.get("borders", {}).get("radius", 6)


def get_theme_card_dimension(theme: Dict[str, Any], dimension: str) -> int:
    """
    Get card dimension from theme.
    
    Args:
        theme: Theme dictionary
        dimension: Dimension key ('width' or 'height')
        
    Returns:
        Dimension value as integer
    """
    cards = theme.get("cards", {})
    return cards.get(dimension, 800 if dimension == "width" else 400)
