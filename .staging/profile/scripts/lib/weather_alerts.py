#!/usr/bin/env python3
"""
Weather alerts detection from Open-Meteo data.

This module provides functions to detect extreme weather conditions
based on WMO weather codes and meteorological data.
"""

from typing import Optional, List, Tuple


def get_weather_alert(
    weathercode: int,
    temperature: Optional[float] = None,
    wind_speed: Optional[float] = None,
    is_day: Optional[int] = None,
) -> Optional[Tuple[str, str, str]]:
    """
    Detect extreme weather conditions and return alert information.
    
    Args:
        weathercode: WMO weather code (0-99)
        temperature: Current temperature in Celsius
        wind_speed: Wind speed in km/h
        is_day: 1 if daytime, 0 if nighttime
    
    Returns:
        Tuple of (alert_type, alert_message, alert_emoji) or None if no alert
        
    WMO Weather Codes:
        0: Clear sky
        1-3: Mainly clear, partly cloudy, overcast
        45,48: Fog
        51-55: Drizzle
        56-57: Freezing drizzle
        61-65: Rain
        66-67: Freezing rain
        71-77: Snow
        80-82: Rain showers
        85-86: Snow showers
        95-99: Thunderstorm
    """
    alerts: List[Tuple[str, str, str]] = []
    
    # Thunderstorm alerts (95-99)
    if 95 <= weathercode <= 99:
        if weathercode == 95:
            return ("thunderstorm", "Thunderstorm in area", "⚠️")
        elif weathercode in [96, 99]:
            return ("severe_thunderstorm", "Severe thunderstorm with hail", "🌩️")
        else:
            return ("thunderstorm", "Thunderstorm approaching", "⚡")
    
    # Blizzard/Snow storm (71-77, 85-86)
    if weathercode in [75, 77, 85, 86]:
        if weathercode in [75, 77]:
            return ("blizzard", "Heavy snowfall - blizzard conditions", "❄️")
        else:
            return ("snow_alert", "Heavy snow showers", "🌨️")
    
    # Freezing conditions (56-57, 66-67)
    if weathercode in [56, 57, 66, 67]:
        return ("freezing", "Freezing precipitation - icy conditions", "🧊")
    
    # Extreme temperature alerts
    if temperature is not None:
        if temperature >= 35:  # 95°F
            return ("heat", "Extreme heat warning", "🔥")
        elif temperature <= -20:  # -4°F
            return ("cold", "Extreme cold warning", "🥶")
        elif temperature <= 0 and temperature > -20:
            return ("freeze", "Freezing temperature alert", "❄️")
    
    # High wind alerts
    if wind_speed is not None:
        # Check combined conditions first (more specific alert)
        if wind_speed >= 40 and weathercode in range(61, 68):  # Wind + Rain
            return ("wind_rain", "Strong winds with rain", "🌧️")
        # Then check high wind alone (general alert)
        elif wind_speed >= 60:  # ~37 mph - High wind
            return ("wind", "High wind warning", "💨")
    
    # Dense fog (45, 48)
    if weathercode in [45, 48]:
        return ("fog", "Dense fog - reduced visibility", "🌫️")
    
    return None


def format_alert_badge(
    alert_type: str,
    alert_message: str,
    alert_emoji: str,
    x: int,
    y: int,
    font_family: str,
    alert_color: str = "#ff5500",
) -> str:
    """
    Generate SVG markup for a weather alert badge.
    
    Args:
        alert_type: Type of alert (for styling)
        alert_message: Alert message text
        alert_emoji: Emoji icon for the alert
        x: X position of the badge
        y: Y position of the badge
        font_family: Font family for text
        alert_color: Color for the alert badge
    
    Returns:
        SVG markup string
    """
    badge_width = len(alert_message) * 5.5 + 40  # Approximate width
    badge_width = min(badge_width, 400)  # Max width
    
    return f"""
    <g transform="translate({x}, {y})">
      <rect width="{badge_width}" height="26" rx="4" fill="{alert_color}" fill-opacity="0.9"/>
      <rect width="{badge_width}" height="26" rx="4" fill="none" stroke="{alert_color}" stroke-width="2"/>
      <text x="10" y="17" font-family="{font_family}" font-size="11" fill="#ffffff" font-weight="600">
        {alert_emoji} {alert_message}
      </text>
    </g>"""


def get_all_weather_alerts(weather_data: dict) -> List[Tuple[str, str, str]]:
    """
    Get all applicable weather alerts from weather data.
    
    Args:
        weather_data: Weather data dictionary from API
    
    Returns:
        List of alert tuples (alert_type, message, emoji)
    """
    alerts = []
    
    current = weather_data.get("current", {})
    daily = weather_data.get("daily", {})
    
    # Check current conditions
    current_alert = get_weather_alert(
        weathercode=current.get("weathercode", 0),
        temperature=current.get("temperature"),
        wind_speed=current.get("wind_speed"),
        is_day=current.get("is_day", 1),
    )
    
    if current_alert:
        alerts.append(current_alert)
    
    # Check if daily forecast shows extreme conditions
    daily_code = daily.get("weathercode", 0)
    temp_max = daily.get("temperature_max")
    temp_min = daily.get("temperature_min")
    
    # Check for extreme daily temperatures if not already alerted
    if temp_max is not None and temp_max >= 35 and not any(a[0] == "heat" for a in alerts):
        alerts.append(("heat", f"Expected high: {temp_max:.0f}°C", "🔥"))
    
    if temp_min is not None and temp_min <= -20 and not any(a[0] == "cold" for a in alerts):
        alerts.append(("cold", f"Expected low: {temp_min:.0f}°C", "🥶"))
    
    # Check daily forecast for severe weather if different from current
    if daily_code != current.get("weathercode", 0):
        daily_alert = get_weather_alert(weathercode=daily_code)
        if daily_alert and daily_alert not in alerts:
            # Modify message to indicate it's in the forecast
            alerts.append((daily_alert[0], f"Later: {daily_alert[1]}", daily_alert[2]))
    
    return alerts
