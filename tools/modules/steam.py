"""Fetch and render a public Steam profile snapshot for the profile README.

Setup
-----
1. Obtain a Steam Web API key at https://steamcommunity.com/dev/apikey.
2. Add ``STEAM_WEB_API_KEY`` as a repository Actions secret.
3. Add the public SteamID64 as the repository Actions variable ``STEAM_ID64``.

The public card uses Steam-native profile signals rather than inventing an
Xbox-style "Gamerscore": Steam level, player XP, badge count, owned-game count,
and bounded recent playtime. Steam privacy settings remain authoritative.
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
from tools.profile_builder.models import SteamRecentGame, SteamSnapshot

MODULE_NAME = "steam"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = REPO_ROOT / "profile" / "fixtures" / "steam.json"
DEFAULT_OUTPUT = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME / "cache.json"
_API_ROOT = "https://api.steampowered.com"
_MAX_RECENT_GAMES = 5
_TIMEOUT = 15


class ProviderFailure(RuntimeError):
    """Raised when live data cannot be collected."""


class ConfigurationMissing(ProviderFailure):
    """Raised when required environment variables are absent."""


class PrivacyRestricted(ProviderFailure):
    """Raised when Steam privacy settings prevent data access."""


def _env(name: str) -> str | None:
    return os.environ.get(name) or None


def _steam_get(endpoint: str, params: dict[str, str], api_key: str) -> object:
    params = {"key": api_key, **params}
    url = f"{_API_ROOT}/{endpoint}?{parse.urlencode(params)}"
    req = request.Request(
        url,
        headers={"User-Agent": "szmyty-profile-builder/1.0"},
    )
    try:
        with request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        if exc.code == 401:
            raise ProviderFailure("Steam API key is invalid or revoked") from exc
        if exc.code == 403:
            raise PrivacyRestricted(
                "Steam privacy settings block this endpoint"
            ) from exc
        raise ProviderFailure(f"Steam API request failed: HTTP {exc.code}") from exc
    except error.URLError as exc:
        raise ProviderFailure(f"Steam API unreachable: {exc.reason}") from exc


def fetch_live(api_key: str, steam_id: str) -> SteamSnapshot:
    """Fetch the bounded public Steam profile snapshot."""
    summary_resp = _steam_get(
        "ISteamUser/GetPlayerSummaries/v0002",
        {"steamids": steam_id},
        api_key,
    )
    players = (
        summary_resp.get("response", {}).get("players", [])
        if isinstance(summary_resp, dict)
        else []
    )
    if not players:
        raise PrivacyRestricted(
            f"GetPlayerSummaries returned no players for SteamID64 {steam_id}"
        )
    player = players[0]
    display_name: str | None = player.get("personaname")
    profile_url: str | None = player.get("profileurl")

    steam_level: int | None = None
    try:
        level_resp = _steam_get(
            "IPlayerService/GetSteamLevel/v1",
            {"steamid": steam_id},
            api_key,
        )
        steam_level = (
            level_resp.get("response", {}).get("player_level")
            if isinstance(level_resp, dict)
            else None
        )
    except ProviderFailure:
        pass

    recent_games: list[SteamRecentGame] = []
    try:
        games_resp = _steam_get(
            "IPlayerService/GetRecentlyPlayedGames/v0001",
            {"steamid": steam_id, "count": str(_MAX_RECENT_GAMES)},
            api_key,
        )
        raw_games = (
            games_resp.get("response", {}).get("games", [])
            if isinstance(games_resp, dict)
            else []
        )
        for game in raw_games[:_MAX_RECENT_GAMES]:
            appid = game.get("appid")
            recent_games.append(
                SteamRecentGame(
                    name=game.get("name", "Unknown"),
                    appid=appid or 0,
                    playtime_2weeks=game.get("playtime_2weeks"),
                    store_url=(
                        f"https://store.steampowered.com/app/{appid}/"
                        if appid
                        else None
                    ),
                )
            )
    except ProviderFailure:
        pass

    return SteamSnapshot(
        display_name=display_name,
        profile_url=profile_url,
        steam_level=steam_level,
        recent_games=recent_games,
        data_source="live",
        data_at=datetime.now(UTC).isoformat(),
    )


def fetch_extended_stats(api_key: str, steam_id: str) -> dict:
    """Fetch public Steam-native score-like metrics for the SVG card."""
    owned_games: int | None = None
    badge_count: int | None = None
    player_xp: int | None = None

    try:
        owned_resp = _steam_get(
            "IPlayerService/GetOwnedGames/v1",
            {
                "steamid": steam_id,
                "include_appinfo": "false",
                "include_played_free_games": "true",
            },
            api_key,
        )
        response = (
            owned_resp.get("response", {}) if isinstance(owned_resp, dict) else {}
        )
        game_count = response.get("game_count") if isinstance(response, dict) else None
        if isinstance(game_count, int):
            owned_games = game_count
    except ProviderFailure:
        pass

    try:
        badge_resp = _steam_get(
            "IPlayerService/GetBadges/v1",
            {"steamid": steam_id},
            api_key,
        )
        response = (
            badge_resp.get("response", {}) if isinstance(badge_resp, dict) else {}
        )
        if isinstance(response, dict):
            badges = response.get("badges")
            if isinstance(badges, list):
                badge_count = len(badges)
            xp = response.get("player_xp")
            if isinstance(xp, int):
                player_xp = xp
    except ProviderFailure:
        pass

    return {
        "owned_games": owned_games,
        "badge_count": badge_count,
        "player_xp": player_xp,
        "data_source": "live",
        "is_synthetic": False,
    }


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def load_fixture(path: Path = DEFAULT_FIXTURE) -> SteamSnapshot:
    """Load sanitized offline fixture data."""
    return SteamSnapshot.model_validate_json(path.read_text(encoding="utf-8"))


def load_cached(path: Path = DEFAULT_OUTPUT) -> SteamSnapshot | None:
    """Load the previous real artifact, never promoting fixture data as real."""
    if not path.exists():
        return None
    snap = SteamSnapshot.model_validate_json(path.read_text(encoding="utf-8"))
    if snap.data_source == "fixture":
        return None
    return snap.model_copy(update={"data_source": "cache"})


def _load_cached_stats(path: Path) -> dict | None:
    stats = _read_json(path)
    if stats is None or stats.get("is_synthetic") is True:
        return None
    stats["data_source"] = "cache"
    return stats


def _empty_stats() -> dict:
    return {
        "owned_games": None,
        "badge_count": None,
        "player_xp": None,
        "data_source": "fixture",
        "is_synthetic": True,
    }


def _palette(dark: bool) -> dict[str, str]:
    if dark:
        return {
            "background": "#0D1117",
            "panel": "#161B22",
            "border": "#30363D",
            "text": "#F0F6FC",
            "muted": "#8B949E",
            "accent": "#66C0F4",
        }
    return {
        "background": "#FFFFFF",
        "panel": "#F6F8FA",
        "border": "#D0D7DE",
        "text": "#1F2328",
        "muted": "#59636E",
        "accent": "#1B75BB",
    }


def _number(value: object) -> str:
    return f"{value:,}" if isinstance(value, int) else "—"


def _recent_hours(snapshot: SteamSnapshot) -> int | None:
    values = [
        game.playtime_2weeks
        for game in snapshot.recent_games
        if game.playtime_2weeks is not None
    ]
    if not values:
        return None
    return round(sum(values) / 60)


def _render_svg(
    snapshot: SteamSnapshot,
    stats: dict,
    *,
    dark: bool,
    mobile: bool,
) -> str:
    palette = _palette(dark)
    width = 360 if mobile else 760
    height = 420 if mobile else 285
    font = "-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"
    display_name = html.escape(snapshot.display_name or "Steam player")
    level = _number(snapshot.steam_level)
    games = _number(stats.get("owned_games"))
    badges = _number(stats.get("badge_count"))
    xp = _number(stats.get("player_xp"))
    recent_hours = _recent_hours(snapshot)
    recent = f"{recent_hours} h" if recent_hours is not None else "—"

    metrics = [
        ("LEVEL", level),
        ("PLAYER XP", xp),
        ("OWNED GAMES", games),
        ("BADGES", badges),
        ("RECENT PLAYTIME", recent),
    ]
    if mobile:
        positions = [(28, 125), (190, 125), (28, 190), (190, 190), (28, 255)]
    else:
        positions = [(30, 125), (165, 125), (300, 125), (455, 125), (590, 125)]

    metric_markup = "".join(
        f'<text x="{x}" y="{y}" fill="{palette["muted"]}" font-size="11" '
        f'font-weight="650">{label}</text>'
        f'<text x="{x}" y="{y + 26}" fill="{palette["text"]}" font-size="20" '
        f'font-weight="720">{html.escape(value)}</text>'
        for (label, value), (x, y) in zip(metrics, positions, strict=True)
    )

    recent_games = snapshot.recent_games[:3]
    if mobile:
        start_y = 320
        game_markup = "".join(
            f'<text x="28" y="{start_y + index * 28}" fill="{palette["text"]}" '
            f'font-size="13">{html.escape(game.name[:38])}</text>'
            for index, game in enumerate(recent_games)
        )
    else:
        game_text = " · ".join(game.name for game in recent_games) or "No recent games"
        game_markup = (
            f'<text x="30" y="225" fill="{palette["text"]}" font-size="13">'
            f"{html.escape(game_text[:95])}</text>"
        )

    footer_y = height - 22
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
        f"<title>Steam profile snapshot for {display_name}</title>"
        "<desc>Public Steam level, XP, badges, owned games, and recent playtime.</desc>"
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" '
        f'fill="{palette["background"]}" stroke="{palette["border"]}"/>'
        f'<g font-family="{font}">'
        f'<text x="28" y="42" fill="{palette["accent"]}" font-size="13" '
        'font-weight="700">STEAM SNAPSHOT</text>'
        f'<text x="28" y="78" fill="{palette["text"]}" font-size="24" '
        f'font-weight="750">{display_name}</text>'
        f"{metric_markup}"
        f'<text x="28" y="{300 if mobile else 197}" fill="{palette["muted"]}" '
        'font-size="11" font-weight="650">RECENT GAMES</text>'
        f"{game_markup}"
        f'<text x="28" y="{footer_y}" fill="{palette["muted"]}" font-size="11">'
        "Public Steam Web API data · private fields remain hidden by Steam"
        "</text></g></svg>"
    )


def render_cards(snapshot: SteamSnapshot, stats: dict, artifact_dir: Path) -> None:
    """Render responsive light/dark SVG cards."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    variants = {
        "card-light.svg": (False, False),
        "card-dark.svg": (True, False),
        "card-mobile-light.svg": (False, True),
        "card-mobile-dark.svg": (True, True),
    }
    for filename, (dark, mobile) in variants.items():
        (artifact_dir / filename).write_text(
            _render_svg(snapshot, stats, dark=dark, mobile=mobile),
            encoding="utf-8",
        )


def build_snapshot(
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
) -> SteamSnapshot:
    """Build the Steam snapshot with graceful degradation.

    Fetch order:
    1. Live provider using ``STEAM_WEB_API_KEY`` + ``STEAM_ID64``.
    2. Last-known real cache.
    3. Sanitized synthetic fixture.
    """
    api_key = _env("STEAM_WEB_API_KEY")
    steam_id = _env("STEAM_ID64")
    artifact_dir = output_path.parent
    stats_path = artifact_dir / "stats.json"

    snap: SteamSnapshot | None = None
    stats: dict | None = None
    state = "failed-with-fallback"
    error_message: str | None = None

    if api_key and steam_id:
        try:
            snap = fetch_live(api_key, steam_id)
            stats = fetch_extended_stats(api_key, steam_id)
            state = "fresh"
        except ProviderFailure as exc:
            error_message = str(exc)
    else:
        error_message = "STEAM_WEB_API_KEY or STEAM_ID64 not set"

    if snap is None:
        snap = load_cached(output_path)
        if snap is not None:
            state = "cached"

    if stats is None:
        stats = _load_cached_stats(stats_path)

    if snap is None:
        snap = load_fixture(fixture_path)
        state = "static"

    if stats is None:
        stats = _empty_stats()

    _write_json(output_path, snap.model_dump(mode="json"))
    _write_json(stats_path, stats)
    render_cards(snap, stats, artifact_dir)
    cache_utils.write_metadata(
        module_name=MODULE_NAME,
        state=state,
        data_source=snap.data_source,
        human_summary=f"Steam snapshot ({state})",
        data_at=snap.data_at,
        error=error_message,
        artifact_dir=artifact_dir,
    )
    return snap


def load_template_context(artifact_path: Path) -> dict:
    """Load the Steam README context and hide synthetic fixture output."""
    snapshot = SteamSnapshot.model_validate_json(
        artifact_path.read_text(encoding="utf-8")
    )
    stats = _read_json(artifact_path.parent / "stats.json") or _empty_stats()
    is_public = snapshot.data_source in {"live", "cache"}
    return {
        "snapshot": snapshot,
        "stats": stats,
        "is_public": is_public,
    }


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
    """Write a public Steam profile snapshot and responsive cards."""
    snap = build_snapshot(output_path=output_path, fixture_path=fixture_path)
    click.echo(f"steam: wrote {output_path} ({snap.data_source})")


if __name__ == "__main__":
    main()
