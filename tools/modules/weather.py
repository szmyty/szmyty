"""Publish a weather snapshot derived from the public GitHub profile location.

The only persistent location value is the public city/region label returned by
GitHub. Coordinates from Open-Meteo geocoding are kept in memory only and are
never written to tracked artifacts or logs.
"""

from __future__ import annotations

import html
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from urllib import error, parse, request

import click

from tools.profile_builder import cache as cache_utils

MODULE_NAME = "weather"
GITHUB_USERNAME = "szmyty"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = REPO_ROOT / "profile" / "fixtures" / "weather.json"
DEFAULT_OUTPUT = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME / "cache.json"

_GITHUB_USER_API = f"https://api.github.com/users/{GITHUB_USERNAME}"
_GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_API = "https://api.open-meteo.com/v1/forecast"
_TIMEOUT = 15

_WMO_CONDITIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm with hail",
}


class ProviderFailure(RuntimeError):
    """Raised when a live provider cannot produce a safe snapshot."""


def _json_get(url: str, headers: dict[str, str] | None = None) -> dict:
    req = request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "szmyty-profile-builder/1.0",
            **(headers or {}),
        },
    )
    try:
        with request.urlopen(req, timeout=_TIMEOUT) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise ProviderFailure(f"provider request failed: HTTP {exc.code}") from exc
    except error.URLError as exc:
        raise ProviderFailure("provider request failed: network unavailable") from exc
    if not isinstance(payload, dict):
        raise ProviderFailure("provider returned a non-object response")
    return payload


def fetch_public_github_location(token: str | None = None) -> str:
    """Return the public GitHub profile location exactly as configured."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    payload = _json_get(_GITHUB_USER_API, headers=headers)
    location = payload.get("location")
    if not isinstance(location, str) or not location.strip():
        raise ProviderFailure("GitHub profile does not expose a public location")
    return location.strip()


def _geocode(location: str) -> tuple[float, float]:
    search_name = location.split(",", 1)[0].strip() or location
    query = parse.urlencode(
        {
            "name": search_name,
            "count": "5",
            "language": "en",
            "format": "json",
            "countryCode": "US",
        }
    )
    payload = _json_get(f"{_GEOCODING_API}?{query}")
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        raise ProviderFailure(
            "Open-Meteo could not resolve the GitHub profile location"
        )

    selected = results[0]
    for result in results:
        if not isinstance(result, dict):
            continue
        admin1 = str(result.get("admin1") or "").casefold()
        source = location.casefold()
        is_massachusetts = "massachusetts" in source or ", ma" in source
        if is_massachusetts and admin1 == "massachusetts":
            selected = result
            break

    if not isinstance(selected, dict):
        raise ProviderFailure("Open-Meteo geocoding result is invalid")
    latitude = selected.get("latitude")
    longitude = selected.get("longitude")
    if not isinstance(latitude, (int, float)) or not isinstance(
        longitude, (int, float)
    ):
        raise ProviderFailure("Open-Meteo geocoding result has no coordinates")
    return float(latitude), float(longitude)


def _first_number(values: object) -> float | None:
    if not isinstance(values, list) or not values:
        return None
    value = values[0]
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _first_int(values: object) -> int | None:
    value = _first_number(values)
    return int(round(value)) if value is not None else None


def fetch_live(location: str) -> dict:
    """Fetch a normalized weather snapshot without persisting coordinates."""
    latitude, longitude = _geocode(location)
    query = parse.urlencode(
        {
            "latitude": f"{latitude:.5f}",
            "longitude": f"{longitude:.5f}",
            "current": (
                "temperature_2m,apparent_temperature,relative_humidity_2m,"
                "precipitation,weather_code,wind_speed_10m"
            ),
            "daily": (
                "temperature_2m_max,temperature_2m_min,precipitation_probability_max"
            ),
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "auto",
            "forecast_days": "1",
        }
    )
    payload = _json_get(f"{_FORECAST_API}?{query}")
    current = payload.get("current")
    daily = payload.get("daily")
    if not isinstance(current, dict) or not isinstance(daily, dict):
        raise ProviderFailure("Open-Meteo forecast response is incomplete")

    weather_code = current.get("weather_code")
    condition = _WMO_CONDITIONS.get(
        int(weather_code) if isinstance(weather_code, (int, float)) else -1,
        "Current conditions",
    )

    snapshot = {
        "location": location,
        "condition": condition,
        "temperature_f": current.get("temperature_2m"),
        "apparent_temperature_f": current.get("apparent_temperature"),
        "relative_humidity_pct": current.get("relative_humidity_2m"),
        "precipitation_in": current.get("precipitation"),
        "wind_mph": current.get("wind_speed_10m"),
        "high_f": _first_number(daily.get("temperature_2m_max")),
        "low_f": _first_number(daily.get("temperature_2m_min")),
        "precipitation_probability_pct": _first_int(
            daily.get("precipitation_probability_max")
        ),
        "weather_code": (
            int(weather_code) if isinstance(weather_code, (int, float)) else None
        ),
        "data_source": "live",
        "data_at": datetime.now(UTC).isoformat(),
        "attribution": "Weather data by Open-Meteo.com",
        "is_synthetic": False,
    }
    forbidden = {"latitude", "longitude", "timezone", "elevation"}
    if forbidden.intersection(snapshot):
        raise ProviderFailure("normalized weather snapshot contains forbidden fields")
    return snapshot


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def load_fixture(path: Path = DEFAULT_FIXTURE) -> dict:
    """Load a synthetic fixture used only for deterministic tests and fallback."""
    snapshot = _load_json(path)
    if snapshot is None:
        raise ProviderFailure(f"weather fixture is unreadable: {path}")
    return snapshot


def load_cached(path: Path = DEFAULT_OUTPUT) -> dict | None:
    """Load the last real snapshot, never promoting a fixture to public cache."""
    snapshot = _load_json(path)
    if snapshot is None or snapshot.get("is_synthetic") is True:
        return None
    snapshot["data_source"] = "cache"
    return snapshot


def _format_number(value: object, suffix: str = "", digits: int = 0) -> str:
    if not isinstance(value, (int, float)):
        return "—"
    return f"{value:.{digits}f}{suffix}"


def _weather_icon_name(code: object) -> str:
    """Map an Open-Meteo WMO weather code to one icon family."""
    if not isinstance(code, (int, float)):
        return "unknown"

    weather_code = int(code)
    if weather_code == 0:
        return "clear"
    if weather_code == 1:
        return "mostly-clear"
    if weather_code == 2:
        return "partly-cloudy"
    if weather_code == 3:
        return "overcast"
    if weather_code in {45, 48}:
        return "fog"
    if weather_code in {51, 53, 55, 56, 57}:
        return "drizzle"
    if weather_code in {61, 63, 65, 66, 67}:
        return "rain"
    if weather_code in {71, 73, 75, 77, 85, 86}:
        return "snow"
    if weather_code in {80, 81, 82}:
        return "showers"
    if weather_code == 95:
        return "thunderstorm"
    if weather_code in {96, 99}:
        return "hail"
    return "unknown"


def _palette(dark: bool) -> dict[str, str]:
    if dark:
        return {
            "background": "#0D1117",
            "panel": "#161B22",
            "border": "#30363D",
            "text": "#F0F6FC",
            "muted": "#8B949E",
            "accent": "#58A6FF",
            "sun": "#E3B341",
            "cloud": "#8B949E",
            "precipitation": "#79C0FF",
            "snow": "#B6E3FF",
            "lightning": "#F2CC60",
        }
    return {
        "background": "#FFFFFF",
        "panel": "#F6F8FA",
        "border": "#D0D7DE",
        "text": "#1F2328",
        "muted": "#59636E",
        "accent": "#0969DA",
        "sun": "#BF8700",
        "cloud": "#57606A",
        "precipitation": "#0969DA",
        "snow": "#54AEFF",
        "lightning": "#9A6700",
    }


def _sun_icon(palette: dict[str, str]) -> str:
    color = palette["sun"]
    rays = (
        '<line x1="32" y1="5" x2="32" y2="13"/>'
        '<line x1="32" y1="51" x2="32" y2="59"/>'
        '<line x1="5" y1="32" x2="13" y2="32"/>'
        '<line x1="51" y1="32" x2="59" y2="32"/>'
        '<line x1="13" y1="13" x2="18.5" y2="18.5"/>'
        '<line x1="45.5" y1="45.5" x2="51" y2="51"/>'
        '<line x1="13" y1="51" x2="18.5" y2="45.5"/>'
        '<line x1="45.5" y1="18.5" x2="51" y2="13"/>'
    )
    return (
        f'<g fill="none" stroke="{color}" stroke-width="3" '
        f'stroke-linecap="round">{rays}'
        '<circle cx="32" cy="32" r="12"/></g>'
    )


def _cloud_icon(palette: dict[str, str]) -> str:
    return (
        '<path d="M16 45h31c7 0 12-5 12-11s-5-11-12-11h-1C43 14 36 9 '
        '27 9c-10 0-18 8-19 18-5 2-8 6-8 10 0 5 4 8 9 8h7z" '
        f'fill="{palette["cloud"]}" opacity="0.94"/>'
    )


def _weather_icon_svg(
    code: object,
    *,
    x: float,
    y: float,
    size: float,
    palette: dict[str, str],
) -> str:
    """Render one repository-owned icon for a WMO weather-code family."""
    icon = _weather_icon_name(code)
    cloud = _cloud_icon(palette)
    rain = palette["precipitation"]
    snow = palette["snow"]
    lightning = palette["lightning"]

    if icon == "clear":
        body = _sun_icon(palette)
    elif icon in {"mostly-clear", "partly-cloudy"}:
        body = (
            '<g transform="translate(-10 -10) scale(.72)">'
            f"{_sun_icon(palette)}</g>{cloud}"
        )
    elif icon in {"overcast", "unknown"}:
        body = cloud
    elif icon == "fog":
        body = (
            f"{cloud}"
            f'<g stroke="{palette["muted"]}" stroke-width="3" '
            'stroke-linecap="round">'
            '<line x1="11" y1="51" x2="53" y2="51"/>'
            '<line x1="18" y1="59" x2="46" y2="59"/></g>'
        )
    elif icon in {"drizzle", "rain", "showers"}:
        stroke_width = "2" if icon == "drizzle" else "3"
        y2 = "58" if icon == "drizzle" else "61"
        body = (
            f'{cloud}<g stroke="{rain}" stroke-width="{stroke_width}" '
            'stroke-linecap="round">'
            f'<line x1="22" y1="49" x2="18" y2="{y2}"/>'
            f'<line x1="36" y1="49" x2="32" y2="{y2}"/>'
            f'<line x1="50" y1="49" x2="46" y2="{y2}"/></g>'
        )
    elif icon == "snow":
        body = (
            f'{cloud}<g stroke="{snow}" stroke-width="2" '
            'stroke-linecap="round">'
            '<path d="M21 50v11M16 55.5h10M17.5 52l7 7M24.5 52l-7 7"/>'
            '<path d="M45 50v11M40 55.5h10M41.5 52l7 7M48.5 52l-7 7"/>'
            "</g>"
        )
    elif icon in {"thunderstorm", "hail"}:
        hail = ""
        if icon == "hail":
            hail = (
                f'<circle cx="20" cy="57" r="3" fill="{snow}"/>'
                f'<circle cx="50" cy="57" r="3" fill="{snow}"/>'
            )
        body = (
            f'{cloud}<path d="M37 45 27 57h9l-4 7 16-16h-9l4-3z" '
            f'fill="{lightning}"/>{hail}'
        )
    else:
        body = cloud

    scale = size / 64
    return (
        f'<g data-weather-icon="{icon}" aria-hidden="true" '
        f'transform="translate({x:.1f} {y:.1f}) scale({scale:.4f})">'
        f"{body}</g>"
    )


def _render_svg(snapshot: dict, *, dark: bool, mobile: bool) -> str:
    palette = _palette(dark)
    width = 360 if mobile else 760
    height = 236 if mobile else 184
    location = html.escape(str(snapshot.get("location") or "GitHub profile location"))
    condition = html.escape(str(snapshot.get("condition") or "Weather"))
    temperature = _format_number(snapshot.get("temperature_f"), "°F")
    feels = _format_number(snapshot.get("apparent_temperature_f"), "°F")
    high = _format_number(snapshot.get("high_f"), "°")
    low = _format_number(snapshot.get("low_f"), "°")
    humidity = _format_number(snapshot.get("relative_humidity_pct"), "%")
    wind = _format_number(snapshot.get("wind_mph"), " mph")
    precip = _format_number(snapshot.get("precipitation_probability_pct"), "%")
    font = "-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"

    if mobile:
        icon = _weather_icon_svg(
            snapshot.get("weather_code"),
            x=282,
            y=30,
            size=46,
            palette=palette,
        )
        metrics = [
            ("FEELS", feels, 28, 143),
            ("HUMIDITY", humidity, 190, 143),
            ("WIND", wind, 28, 178),
            ("PRECIP", precip, 190, 178),
        ]
        metric_markup = "".join(
            f'<text x="{x}" y="{y}" fill="{palette["muted"]}" '
            f'font-size="9" font-weight="700">{label}</text>'
            f'<text x="{x}" y="{y + 16}" fill="{palette["text"]}" '
            f'font-size="14" font-weight="650">{html.escape(value)}</text>'
            for label, value, x, y in metrics
        )
        summary_markup = (
            f'<text x="28" y="94" fill="{palette["text"]}" font-size="36" '
            f'font-weight="750">{temperature}</text>'
            f'<text x="112" y="80" fill="{palette["text"]}" font-size="15" '
            f'font-weight="650">{condition}</text>'
            f'<text x="112" y="99" fill="{palette["muted"]}" font-size="11">'
            f"High {high} · Low {low}</text>"
        )
        panel_markup = (
            f'<rect x="18" y="119" width="324" height="76" rx="12" '
            f'fill="{palette["panel"]}" stroke="{palette["border"]}"/>'
        )
    else:
        icon = _weather_icon_svg(
            snapshot.get("weather_code"),
            x=685,
            y=23,
            size=52,
            palette=palette,
        )
        metrics = [
            ("FEELS", feels, 302),
            ("HUMIDITY", humidity, 417),
            ("WIND", wind, 532),
            ("PRECIP", precip, 640),
        ]
        metric_markup = "".join(
            f'<text x="{x}" y="121" fill="{palette["muted"]}" '
            f'font-size="9" font-weight="700">{label}</text>'
            f'<text x="{x}" y="139" fill="{palette["text"]}" '
            f'font-size="14" font-weight="650">{html.escape(value)}</text>'
            for label, value, x in metrics
        )
        summary_markup = (
            f'<text x="28" y="94" fill="{palette["text"]}" font-size="36" '
            f'font-weight="750">{temperature}</text>'
            f'<text x="120" y="80" fill="{palette["text"]}" font-size="15" '
            f'font-weight="650">{condition}</text>'
            f'<text x="120" y="99" fill="{palette["muted"]}" font-size="11">'
            f"High {high} · Low {low}</text>"
        )
        panel_markup = (
            f'<rect x="286" y="104" width="446" height="48" rx="12" '
            f'fill="{palette["panel"]}" stroke="{palette["border"]}"/>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" role="img">'
        f"<title>Weather for {location}</title>"
        f"<desc>{condition}, {temperature}. {snapshot.get('attribution', '')}</desc>"
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" '
        f'fill="{palette["background"]}" stroke="{palette["border"]}"/>'
        f'<g font-family="{font}">'
        f'<text x="28" y="30" fill="{palette["accent"]}" font-size="10" '
        f'font-weight="800" letter-spacing="0.7">LOCAL WEATHER</text>'
        f'<text x="28" y="49" fill="{palette["muted"]}" font-size="11">'
        f"{location}</text>"
        f"{summary_markup}{panel_markup}{metric_markup}{icon}"
        f'<text x="28" y="{height - 15}" fill="{palette["muted"]}" '
        f'font-size="9">Open-Meteo · location from public GitHub profile</text>'
        "</g></svg>"
    )


def render_cards(snapshot: dict, artifact_dir: Path) -> None:
    """Render light/dark desktop/mobile SVG variants."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    variants = {
        "card-light.svg": (False, False),
        "card-dark.svg": (True, False),
        "card-mobile-light.svg": (False, True),
        "card-mobile-dark.svg": (True, True),
    }
    for filename, (dark, mobile) in variants.items():
        (artifact_dir / filename).write_text(
            _render_svg(snapshot, dark=dark, mobile=mobile),
            encoding="utf-8",
        )


def build_snapshot(
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
    *,
    github_token: str | None = None,
) -> dict:
    """Build live -> real cache -> synthetic fixture, then render SVG variants."""
    token = github_token if github_token is not None else os.environ.get("GITHUB_TOKEN")
    snapshot: dict | None = None
    state = "failed-with-fallback"
    error_message: str | None = None

    try:
        location = fetch_public_github_location(token)
        snapshot = fetch_live(location)
        state = "fresh"
    except ProviderFailure as exc:
        error_message = str(exc)

    if snapshot is None:
        snapshot = load_cached(output_path)
        if snapshot is not None:
            state = "cached"

    if snapshot is None:
        snapshot = load_fixture(fixture_path)
        state = "static"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    render_cards(snapshot, output_path.parent)
    cache_utils.write_metadata(
        module_name=MODULE_NAME,
        state=state,
        data_source=str(snapshot.get("data_source") or "fixture"),
        human_summary=f"Weather snapshot ({state})",
        data_at=(
            str(snapshot["data_at"]) if snapshot.get("data_at") is not None else None
        ),
        error=error_message,
        artifact_dir=output_path.parent,
    )
    return snapshot


def load_template_context(artifact_path: Path) -> dict:
    """Return README context; synthetic weather is never rendered publicly."""
    snapshot = _load_json(artifact_path)
    is_public = bool(snapshot and snapshot.get("is_synthetic") is not True)
    return {"snapshot": snapshot or {}, "is_public": is_public}


@click.command()
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_OUTPUT),
    show_default=True,
)
@click.option(
    "--fixture",
    "fixture_path",
    type=click.Path(exists=True, path_type=Path),
    default=str(DEFAULT_FIXTURE),
    show_default=True,
)
def main(output_path: Path, fixture_path: Path) -> None:
    """Refresh the public-location weather snapshot and SVG cards."""
    snapshot = build_snapshot(output_path=output_path, fixture_path=fixture_path)
    click.echo(
        f"weather: wrote {output_path} ({snapshot.get('data_source', 'unknown')})"
    )


if __name__ == "__main__":
    main()
