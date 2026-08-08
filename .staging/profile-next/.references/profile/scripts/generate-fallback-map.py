#!/usr/bin/env python3
"""
Generate a fallback map image when Mapbox API is unavailable.
Creates a simple PNG with location coordinates.
"""

import sys
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont


def generate_fallback_map(output_path: str, lat: float, lon: float) -> None:
    """
    Generate a fallback map image as PNG.
    
    Args:
        output_path: Path where the PNG should be saved
        lat: Latitude coordinate
        lon: Longitude coordinate
    """
    # Create image with dark gradient background
    width, height = 600, 400
    img = Image.new('RGB', (width, height), color='#16213e')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient effect (simple approximation)
    for i in range(height):
        # Interpolate between two colors
        ratio = i / height
        r = int(26 * (1 - ratio) + 22 * ratio)
        g = int(26 * (1 - ratio) + 33 * ratio)
        b = int(46 * (1 - ratio) + 62 * ratio)
        color = (r, g, b)
        draw.rectangle([(0, i), (width, i + 1)], fill=color)
    
    # Draw grid pattern
    grid_color = (15, 52, 96)  # #0f3460
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)
    
    # Try to use a nice font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        coord_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except IOError:
        # Use default font if custom fonts not available
        title_font = ImageFont.load_default()  # type: ignore[assignment]
        text_font = ImageFont.load_default()  # type: ignore[assignment]
        small_font = ImageFont.load_default()  # type: ignore[assignment]
        coord_font = ImageFont.load_default()  # type: ignore[assignment]
    
    # Draw emoji/icon (simplified as text)
    icon_text = "📍"
    # For emoji, we need to use default font
    draw.text((width // 2, 120), icon_text, fill='#e94560', anchor='mm', font=title_font)
    
    # Draw main text
    main_text = "Map Temporarily Unavailable"
    draw.text((width // 2, 175), main_text, fill='#ffffff', anchor='mm', font=text_font)
    
    # Draw subtitle
    subtitle = "Location data is still available"
    draw.text((width // 2, 210), subtitle, fill='#94a3b8', anchor='mm', font=small_font)
    
    # Draw coordinates
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    coords_text = f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}"
    draw.text((width // 2, 240), coords_text, fill='#64748b', anchor='mm', font=coord_font)
    
    # Draw corner accents
    accent_color = '#e94560'
    accent_length = 40
    accent_width = 4
    
    # Top-left
    draw.rectangle([(10, 10), (10 + accent_length, 10 + accent_width)], fill=accent_color)
    draw.rectangle([(10, 10), (10 + accent_width, 10 + accent_length)], fill=accent_color)
    
    # Top-right
    draw.rectangle([(width - 10 - accent_length, 10), (width - 10, 10 + accent_width)], fill=accent_color)
    draw.rectangle([(width - 10 - accent_width, 10), (width - 10, 10 + accent_length)], fill=accent_color)
    
    # Bottom-left
    draw.rectangle([(10, height - 10 - accent_width), (10 + accent_length, height - 10)], fill=accent_color)
    draw.rectangle([(10, height - 10 - accent_length), (10 + accent_width, height - 10)], fill=accent_color)
    
    # Bottom-right
    draw.rectangle([(width - 10 - accent_length, height - 10 - accent_width), (width - 10, height - 10)], fill=accent_color)
    draw.rectangle([(width - 10 - accent_width, height - 10 - accent_length), (width - 10, height - 10)], fill=accent_color)
    
    # Save the image
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, 'PNG')
    
    print(f"✅ Fallback map image saved to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: generate-fallback-map.py <output_path> <lat> <lon>", file=sys.stderr)
        sys.exit(1)
    
    output_path = sys.argv[1]
    
    # Validate and parse coordinates
    try:
        lat = float(sys.argv[2])
        lon = float(sys.argv[3])
    except ValueError as e:
        print(f"❌ Invalid coordinates: {e}", file=sys.stderr)
        print(f"   Latitude and longitude must be numeric values", file=sys.stderr)
        print(f"   Example: 40.7128 -74.0060", file=sys.stderr)
        sys.exit(1)
    
    # Validate coordinate ranges
    if not (-90 <= lat <= 90):
        print(f"❌ Invalid latitude: {lat}", file=sys.stderr)
        print(f"   Latitude must be between -90 and 90 degrees", file=sys.stderr)
        sys.exit(1)
    
    if not (-180 <= lon <= 180):
        print(f"❌ Invalid longitude: {lon}", file=sys.stderr)
        print(f"   Longitude must be between -180 and 180 degrees", file=sys.stderr)
        sys.exit(1)
    
    try:
        generate_fallback_map(output_path, lat, lon)
    except Exception as e:
        print(f"❌ Failed to generate fallback map: {e}", file=sys.stderr)
        sys.exit(1)
