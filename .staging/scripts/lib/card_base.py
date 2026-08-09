#!/usr/bin/env python3
"""
Base class for SVG card generators.

This module provides a reusable base class that handles common SVG card generation
patterns including theme loading, background rendering, gradients, filters, and
file output.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .utils import (
    escape_xml,
    load_theme,
    get_theme_color,
    get_theme_gradient,
    get_theme_typography,
    get_theme_font_size,
    get_theme_card_dimension,
    get_theme_border_radius,
)


class CardBase(ABC):
    """
    Abstract base class for SVG card generators.

    This class provides common functionality for generating SVG cards including:
    - Theme loading and caching
    - SVG document structure (defs, gradients, filters)
    - Background rendering with gradient and border
    - Decorative accent rendering
    - Footer/timestamp rendering
    - Output file writing

    Subclasses must implement the `generate_content()` method to provide
    card-specific content.

    Attributes:
        card_type: The type of card (e.g., 'soundcloud', 'weather').
                   Used to look up card dimensions from theme.
        theme: Cached theme configuration dictionary.
        width: Card width in pixels.
        height: Card height in pixels.
    """

    def __init__(self, card_type: str):
        """
        Initialize the card generator.

        Args:
            card_type: The type of card (e.g., 'soundcloud', 'weather').
                      Used to look up card dimensions from theme.
        """
        self.card_type = card_type
        self.theme = load_theme()
        self.width = get_theme_card_dimension("widths", card_type)
        self.height = get_theme_card_dimension("heights", card_type)

    # -------------------------------------------------------------------------
    # Theme accessors
    # -------------------------------------------------------------------------

    def get_color(self, category: str, name: str, fallback: str = "#ffffff") -> str:
        """
        Get a color value from the theme.

        Args:
            category: Color category (e.g., 'background', 'text', 'accent').
            name: Color name within the category.
            fallback: Default color if not found.

        Returns:
            Hex color string.
        """
        return get_theme_color(category, name, fallback)

    def get_gradient(self, name: str, fallback: Optional[List[str]] = None) -> List[str]:
        """
        Get a gradient definition from the theme.

        Args:
            name: Gradient name (e.g., 'sleep', 'background.default').
            fallback: Default gradient if not found.

        Returns:
            List of two hex color strings [start, end].
        """
        return get_theme_gradient(name, fallback)

    def get_typography(self, key: str, fallback: str = "") -> str:
        """
        Get a typography value from the theme.

        Args:
            key: Typography key (e.g., 'font_family').
            fallback: Default value if not found.

        Returns:
            Typography value string.
        """
        return get_theme_typography(key, fallback) or fallback

    def get_font_size(self, size_name: str, fallback: int = 12) -> int:
        """
        Get a font size from the theme.

        Args:
            size_name: Size name (e.g., 'xs', 'sm', 'base', 'lg', 'xl').
            fallback: Default size if not found.

        Returns:
            Font size in pixels.
        """
        return get_theme_font_size(size_name, fallback)

    def get_border_radius(self, size: str = "xl", fallback: int = 12) -> int:
        """
        Get a border radius from the theme.

        Args:
            size: Size name (e.g., 'sm', 'md', 'lg', 'xl').
            fallback: Default radius if not found.

        Returns:
            Border radius value in pixels.
        """
        return get_theme_border_radius(size, fallback)

    def get_stroke_width(self) -> int:
        """Get the card stroke width from theme."""
        return self.theme.get("cards", {}).get("stroke_width", 1)

    def get_stroke_opacity(self) -> float:
        """Get the card stroke opacity from theme."""
        return self.theme.get("cards", {}).get("stroke_opacity", 0.3)

    def get_glow_settings(self) -> Dict:
        """Get the glow effect settings from theme."""
        return self.theme.get("effects", {}).get("glow", {"stdDeviation": 2})

    def get_shadow_settings(self) -> Dict:
        """Get the shadow effect settings from theme."""
        return self.theme.get("effects", {}).get("shadow", {
            "dx": 0,
            "dy": 2,
            "stdDeviation": 3,
            "flood_opacity": 0.3,
        })

    def get_spacing(self, size: str, fallback: int = 10) -> int:
        """
        Get a spacing value from the theme.

        Args:
            size: Size name (e.g., 'xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl', '4xl').
            fallback: Default value if not found.

        Returns:
            Spacing value in pixels.
        """
        return self.theme.get("spacing", {}).get(size, fallback)

    def get_chart_value(self, key: str, fallback: int = 0) -> int:
        """
        Get a chart-related dimension value from the theme.

        Args:
            key: Chart setting key (e.g., 'bar_height', 'bar_gap', 'label_width').
            fallback: Default value if not found.

        Returns:
            Chart dimension value.
        """
        return self.theme.get("cards", {}).get("chart", {}).get(key, fallback)

    def get_language_color(self, language: str, fallback: str = "#8892b0") -> str:
        """
        Get a color for a programming language from the theme.

        Args:
            language: Language name (e.g., 'Python', 'JavaScript').
            fallback: Default color if not found.

        Returns:
            Hex color string.
        """
        return self.theme.get("colors", {}).get("languages", {}).get(language, fallback)

    def get_status_color(self, status: str, fallback: str = "#6b7280") -> str:
        """
        Get a color for a status indicator from the theme.

        Args:
            status: Status name (e.g., 'success', 'warning', 'error', 'unknown').
            fallback: Default color if not found.

        Returns:
            Hex color string.
        """
        return self.theme.get("colors", {}).get("status", {}).get(status, fallback)

    def get_chart_color(self, name: str, fallback: str = "#2d3748") -> str:
        """
        Get a chart-related color from the theme.

        Args:
            name: Color name (e.g., 'bar_background').
            fallback: Default color if not found.

        Returns:
            Hex color string.
        """
        return self.theme.get("colors", {}).get("chart", {}).get(name, fallback)

    # -------------------------------------------------------------------------
    # SVG building blocks
    # -------------------------------------------------------------------------

    def build_svg_open(self) -> str:
        """
        Build the opening SVG tag with proper namespaces.

        Returns:
            Opening SVG tag string.
        """
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">'
        )

    def build_defs(
        self,
        bg_gradient: Optional[Tuple[str, str]] = None,
        include_glow: bool = True,
        include_shadow: bool = False,
        extra_defs: str = "",
    ) -> str:
        """
        Build the SVG defs section with gradients and filters.

        Args:
            bg_gradient: Tuple of (start_color, end_color) for background gradient.
                        If None, uses theme default background gradient.
            include_glow: Whether to include the glow filter.
            include_shadow: Whether to include the shadow filter.
            extra_defs: Additional defs content to include.

        Returns:
            Complete defs section string.
        """
        if bg_gradient is None:
            gradient = self.get_gradient("background.default")
            bg_gradient = (gradient[0], gradient[1])

        glow = self.get_glow_settings()
        shadow = self.get_shadow_settings()

        defs_parts = ['  <defs>']

        # Background gradient
        defs_parts.append(f'''    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_gradient[0]}"/>
      <stop offset="100%" style="stop-color:{bg_gradient[1]}"/>
    </linearGradient>''')

        # Glow filter
        if include_glow:
            defs_parts.append(f'''    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="{glow.get('stdDeviation', 2)}" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>''')

        # Shadow filter
        if include_shadow:
            defs_parts.append(f'''    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="{shadow.get('dx', 0)}" dy="{shadow.get('dy', 2)}" stdDeviation="{shadow.get('stdDeviation', 3)}" flood-opacity="{shadow.get('flood_opacity', 0.3)}"/>
    </filter>''')

        # Extra defs
        if extra_defs:
            defs_parts.append(extra_defs)

        defs_parts.append('  </defs>')
        return '\n'.join(defs_parts)

    def build_background(
        self,
        stroke_color: Optional[str] = None,
    ) -> str:
        """
        Build the background rectangle with gradient fill and border.

        Args:
            stroke_color: Color for the border stroke. If None, uses theme accent.

        Returns:
            Background rectangle SVG string.
        """
        if stroke_color is None:
            stroke_color = self.get_color("text", "accent")

        border_radius = self.get_border_radius("xl")
        stroke_width = self.get_stroke_width()
        stroke_opacity = self.get_stroke_opacity()

        return f'''
  <!-- Background -->
  <rect width="{self.width}" height="{self.height}" rx="{border_radius}" fill="url(#bg-gradient)"/>
  <rect width="{self.width}" height="{self.height}" rx="{border_radius}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}"/>'''

    def build_decorative_accent(
        self,
        x_offset: int = 20,
        y_start: int = 15,
        accent_width: int = 4,
        accent_height: Optional[int] = None,
        color: Optional[str] = None,
    ) -> str:
        """
        Build a decorative vertical accent bar.

        Args:
            x_offset: Offset from the right edge of the card.
            y_start: Y position to start the accent.
            accent_width: Width of the accent bar.
            accent_height: Height of the accent bar. If None, calculated from card height.
            color: Color of the accent. If None, uses theme accent.

        Returns:
            Decorative accent SVG string.
        """
        if color is None:
            color = self.get_color("text", "accent")

        if accent_height is None:
            accent_height = self.height - (y_start * 2)

        stroke_opacity = self.get_stroke_opacity()
        x = self.width - x_offset

        return f'''
  <!-- Decorative accent -->
  <rect x="{x}" y="{y_start}" width="{accent_width}" height="{accent_height}" rx="2" fill="{color}" fill-opacity="{stroke_opacity}"/>'''

    def build_footer(
        self,
        text: str,
        x: int = 20,
        y: Optional[int] = None,
    ) -> str:
        """
        Build a footer text element (typically for timestamps).

        Args:
            text: Footer text content.
            x: X position of the footer.
            y: Y position of the footer. If None, positioned near bottom of card.

        Returns:
            Footer SVG string.
        """
        if y is None:
            y = self.height - 25

        font_family = self.get_typography("font_family")
        font_size = self.get_font_size("base")
        text_muted = self.get_color("text", "muted")
        escaped_text = escape_xml(str(text))

        return f'''
  <!-- Footer -->
  <g transform="translate({x}, {y})">
    <text font-family="{font_family}" font-size="{font_size}" fill="{text_muted}">
      {escaped_text}
    </text>
  </g>'''

    def build_staleness_badge(
        self,
        updated_at: str,
        x: Optional[int] = None,
        y: int = 10,
        text_anchor: str = "end",
    ) -> str:
        """
        Build a staleness badge showing when data was last updated.
        
        If data is more than 24 hours old, uses a warning color to indicate staleness.
        
        Args:
            updated_at: ISO 8601 timestamp string of when data was last updated.
            x: X position of the badge. If None, positioned at right edge with 10px padding.
            y: Y position of the badge.
            text_anchor: Text anchor position ('start', 'middle', or 'end').
        
        Returns:
            Staleness badge SVG string, or empty string if updated_at is not provided.
        """
        if not updated_at:
            return ""
        
        from .utils import format_time_since, is_data_stale
        
        if x is None:
            x = self.width - 10
        
        time_since = format_time_since(updated_at)
        is_stale = is_data_stale(updated_at, stale_threshold_hours=24)
        
        font_family = self.get_typography("font_family")
        font_size = self.get_font_size("xs")
        
        # Use warning color if data is stale, otherwise use muted text color
        if is_stale:
            badge_color = self.get_color("accent", "heart_rate")  # Warning/error color
            badge_icon = "⚠️ "
        else:
            badge_color = self.get_color("text", "muted")
            badge_icon = ""
        
        escaped_time = escape_xml(time_since)
        
        return f'''
  <!-- Staleness Badge -->
  <g transform="translate({x}, {y})">
    <text x="0" y="12" font-family="{font_family}" font-size="{font_size}" fill="{badge_color}" text-anchor="{text_anchor}">
      {badge_icon}Updated: {escaped_time}
    </text>
  </g>'''

    # -------------------------------------------------------------------------
    # Main generation methods
    # -------------------------------------------------------------------------

    @abstractmethod
    def generate_content(self) -> str:
        """
        Generate the card-specific content.

        This method must be implemented by subclasses to provide the
        unique content of each card type.

        Returns:
            SVG content string (without the opening tag, defs, or closing tag).
        """
        pass

    def generate_svg(
        self,
        bg_gradient: Optional[Tuple[str, str]] = None,
        stroke_color: Optional[str] = None,
        include_glow: bool = True,
        include_shadow: bool = False,
        extra_defs: str = "",
        include_decorative_accent: bool = True,
        footer_text: Optional[str] = None,
    ) -> str:
        """
        Generate the complete SVG card.

        Args:
            bg_gradient: Tuple of (start_color, end_color) for background gradient.
            stroke_color: Color for the border stroke.
            include_glow: Whether to include the glow filter.
            include_shadow: Whether to include the shadow filter.
            extra_defs: Additional defs content to include.
            include_decorative_accent: Whether to include the decorative accent.
            footer_text: Optional footer text (e.g., timestamp).

        Returns:
            Complete SVG string.
        """
        parts = [
            self.build_svg_open(),
            self.build_defs(
                bg_gradient=bg_gradient,
                include_glow=include_glow,
                include_shadow=include_shadow,
                extra_defs=extra_defs,
            ),
            self.build_background(stroke_color=stroke_color),
            self.generate_content(),
        ]

        if include_decorative_accent:
            parts.append(self.build_decorative_accent())

        if footer_text is not None:
            parts.append(self.build_footer(footer_text))

        parts.append('</svg>')

        return '\n'.join(parts)

    def write_svg(self, output_path: str, svg_content: str) -> None:
        """
        Write SVG content to a file.

        Args:
            output_path: Path to the output file.
            svg_content: SVG content to write.
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            f.write(svg_content)
