"""Tests for the public-location weather snapshot module."""

from __future__ import annotations

import json

from tools.modules import weather


def test_fixture_is_synthetic_and_contains_no_coordinates() -> None:
    snapshot = weather.load_fixture()
    assert snapshot["is_synthetic"] is True
    assert snapshot["data_source"] == "fixture"
    assert "latitude" not in snapshot
    assert "longitude" not in snapshot
    assert "timezone" not in snapshot


def test_fetch_public_github_location_uses_profile_value(monkeypatch) -> None:
    monkeypatch.setattr(
        weather,
        "_json_get",
        lambda url, headers=None: {"location": "Boston, Massachusetts"},
    )
    assert weather.fetch_public_github_location("token") == "Boston, Massachusetts"


def test_fetch_live_never_persists_geocoding_coordinates(monkeypatch) -> None:
    responses = [
        {
            "results": [
                {
                    "name": "Boston",
                    "admin1": "Massachusetts",
                    "country_code": "US",
                    "latitude": 42.36,
                    "longitude": -71.06,
                }
            ]
        },
        {
            "current": {
                "temperature_2m": 74.0,
                "apparent_temperature": 75.0,
                "relative_humidity_2m": 53,
                "precipitation": 0.0,
                "weather_code": 2,
                "wind_speed_10m": 9.0,
            },
            "daily": {
                "temperature_2m_max": [79.0],
                "temperature_2m_min": [63.0],
                "precipitation_probability_max": [20],
            },
        },
    ]

    def fake_get(url: str, headers=None):
        return responses.pop(0)

    monkeypatch.setattr(weather, "_json_get", fake_get)
    snapshot = weather.fetch_live("Boston, Massachusetts")

    assert snapshot["location"] == "Boston, Massachusetts"
    assert snapshot["condition"] == "Partly cloudy"
    for forbidden in ("latitude", "longitude", "timezone", "elevation"):
        assert forbidden not in snapshot


def test_build_snapshot_falls_back_to_fixture_without_live_data(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(
        weather,
        "fetch_public_github_location",
        lambda token=None: (_ for _ in ()).throw(weather.ProviderFailure("offline")),
    )
    output = tmp_path / "weather" / "cache.json"

    snapshot = weather.build_snapshot(
        output_path=output,
        fixture_path=weather.DEFAULT_FIXTURE,
        github_token=None,
    )

    assert snapshot["data_source"] == "fixture"
    assert output.exists()
    assert (output.parent / "card-light.svg").exists()
    assert (output.parent / "card-mobile-dark.svg").exists()


def test_real_cache_is_preferred_over_fixture(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        weather,
        "fetch_public_github_location",
        lambda token=None: (_ for _ in ()).throw(weather.ProviderFailure("offline")),
    )
    output = tmp_path / "weather" / "cache.json"
    output.parent.mkdir(parents=True)
    cached = weather.load_fixture().copy()
    cached.update(
        {
            "location": "Boston, Massachusetts",
            "data_source": "live",
            "is_synthetic": False,
        }
    )
    output.write_text(json.dumps(cached), encoding="utf-8")

    snapshot = weather.build_snapshot(
        output_path=output,
        fixture_path=weather.DEFAULT_FIXTURE,
        github_token=None,
    )
    assert snapshot["data_source"] == "cache"
    assert snapshot["location"] == "Boston, Massachusetts"


def test_synthetic_weather_is_hidden_from_readme(tmp_path) -> None:
    artifact = tmp_path / "cache.json"
    artifact.write_text(
        weather.DEFAULT_FIXTURE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    context = weather.load_template_context(artifact)
    assert context["is_public"] is False


def test_wmo_codes_map_to_distinct_weather_icon_families() -> None:
    expected = {
        0: "clear",
        1: "mostly-clear",
        2: "partly-cloudy",
        3: "overcast",
        45: "fog",
        51: "drizzle",
        61: "rain",
        71: "snow",
        80: "showers",
        95: "thunderstorm",
        96: "hail",
    }

    for code, icon_name in expected.items():
        assert weather._weather_icon_name(code) == icon_name

    assert weather._weather_icon_name(None) == "unknown"
    assert weather._weather_icon_name(999) == "unknown"


def test_rendered_svg_is_compact_and_uses_condition_icon(tmp_path) -> None:
    snapshot = weather.load_fixture().copy()
    snapshot["weather_code"] = 2
    weather.render_cards(snapshot, tmp_path)

    desktop = (tmp_path / "card-light.svg").read_text(encoding="utf-8")
    mobile = (tmp_path / "card-mobile-light.svg").read_text(encoding="utf-8")

    assert 'width="760" height="184"' in desktop
    assert 'width="360" height="236"' in mobile
    assert 'data-weather-icon="partly-cloudy"' in desktop
    assert 'data-weather-icon="partly-cloudy"' in mobile
    assert 'font-size="42"' not in desktop
    assert 'font-size="18" font-weight="650">Partly cloudy' not in desktop


def test_clear_and_overcast_icons_render_different_visuals() -> None:
    palette = weather._palette(False)
    clear = weather._weather_icon_svg(0, x=0, y=0, size=64, palette=palette)
    overcast = weather._weather_icon_svg(3, x=0, y=0, size=64, palette=palette)

    assert 'data-weather-icon="clear"' in clear
    assert 'data-weather-icon="overcast"' in overcast
    assert "<circle" in clear
    assert "<path" in overcast
    assert clear != overcast


def test_rendered_svg_has_accessible_context_without_coordinates(tmp_path) -> None:
    snapshot = weather.load_fixture()
    weather.render_cards(snapshot, tmp_path)
    svg = (tmp_path / "card-light.svg").read_text(encoding="utf-8")

    assert "<title>" in svg
    assert "Open-Meteo" in svg
    assert "latitude" not in svg
    assert "longitude" not in svg
