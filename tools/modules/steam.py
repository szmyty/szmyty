"""Fetch and normalize public Steam profile data for the profile README.

Setup
-----
1. Obtain a Steam Web API key at https://steamcommunity.com/dev/apikey.
2. Add ``STEAM_WEB_API_KEY`` as a repository secret in GitHub → Settings →
   Secrets and variables → Actions.
3. Find your 64-bit Steam ID (SteamID64) from your profile URL or a tool such
   as https://www.steamidfinder.com/.  Add ``STEAM_ID64`` as a repository
   *variable* (non-secret) — it is a public identifier visible in profile URLs.
4. Set ``enabled: true`` for this module in ``profile/content/modules-registry.yml``
   once Alan has supplied the identifiers and verified the credentials.

Rate limits
-----------
The Steam Web API is capped at 100,000 calls per day per key.  This module
makes at most three calls per run: ``GetPlayerSummaries``, ``GetSteamLevel``,
and ``GetRecentlyPlayedGames``.

Privacy
-------
Steam privacy settings control what the Web API returns.  If a player's game
details are private, ``GetRecentlyPlayedGames`` returns an empty list and
``GetSteamLevel`` may be unavailable.  These conditions are recorded as
``failed-with-fallback`` state rather than empty successful records.  The
module never exposes exact online status, session timestamps, or data hidden
by the player's privacy configuration.

Revocation
----------
Revoke the API key at https://steamcommunity.com/dev/apikey and issue a new
one.  Update the ``STEAM_WEB_API_KEY`` secret immediately.  ``STEAM_ID64`` is
a public identifier and does not require rotation.
"""

from __future__ import annotations

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
    """Fetch a public Steam profile snapshot from the official Web API."""
    # --- Player summary ---
    summary_resp = _steam_get(
        "ISteamUser/GetPlayerSummaries/v0002",
        {"steamids": steam_id},
        api_key,
    )
    players = (
        summary_resp.get("response", {}).get("players", [])  # type: ignore[union-attr]
        if isinstance(summary_resp, dict)
        else []
    )
    if not players:
        raise PrivacyRestricted(
            f"GetPlayerSummaries returned no players for SteamID64 {steam_id}; "
            "check privacy settings."
        )
    player = players[0]
    display_name: str | None = player.get("personaname")
    profile_url: str | None = player.get("profileurl")

    # --- Steam level ---
    steam_level: int | None = None
    try:
        level_resp = _steam_get(
            "IPlayerService/GetSteamLevel/v1",
            {"steamid": steam_id},
            api_key,
        )
        steam_level = (
            level_resp.get("response", {}).get("player_level")  # type: ignore[union-attr]
            if isinstance(level_resp, dict)
            else None
        )
    except ProviderFailure:
        pass  # Non-fatal; profile still valid without level

    # --- Recent games ---
    recent_games: list[SteamRecentGame] = []
    try:
        games_resp = _steam_get(
            "IPlayerService/GetRecentlyPlayedGames/v0001",
            {"steamid": steam_id, "count": str(_MAX_RECENT_GAMES)},
            api_key,
        )
        raw_games = (
            games_resp.get("response", {}).get("games", [])  # type: ignore[union-attr]
            if isinstance(games_resp, dict)
            else []
        )
        for g in raw_games[:_MAX_RECENT_GAMES]:
            appid = g.get("appid")
            recent_games.append(
                SteamRecentGame(
                    name=g.get("name", "Unknown"),
                    appid=appid or 0,
                    playtime_2weeks=g.get("playtime_2weeks"),
                    store_url=(
                        f"https://store.steampowered.com/app/{appid}/"
                        if appid
                        else None
                    ),
                )
            )
    except PrivacyRestricted:
        pass  # Recorded implicitly via empty list
    except ProviderFailure:
        pass  # Non-fatal

    return SteamSnapshot(
        display_name=display_name,
        profile_url=profile_url,
        steam_level=steam_level,
        recent_games=recent_games,
        data_source="live",
        data_at=datetime.now(UTC).isoformat(),
    )


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_fixture(path: Path = DEFAULT_FIXTURE) -> SteamSnapshot:
    """Load sanitized offline fixture data."""
    return SteamSnapshot.model_validate_json(path.read_text(encoding="utf-8"))


def load_cached(path: Path = DEFAULT_OUTPUT) -> SteamSnapshot | None:
    """Load the previous artifact as a fallback cache."""
    if not path.exists():
        return None
    snap = SteamSnapshot.model_validate_json(path.read_text(encoding="utf-8"))
    return snap.model_copy(update={"data_source": "cache"})


def build_snapshot(
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
) -> SteamSnapshot:
    """Build the Steam snapshot with graceful degradation.

    Fetch order:
    1. Live provider (requires STEAM_WEB_API_KEY + STEAM_ID64).
    2. Cached artifact from the previous run.
    3. Sanitized fixture.
    """
    api_key = _env("STEAM_WEB_API_KEY")
    steam_id = _env("STEAM_ID64")

    snap: SteamSnapshot | None = None
    state = "failed-with-fallback"
    error_msg: str | None = None

    if api_key and steam_id:
        try:
            snap = fetch_live(api_key, steam_id)
            state = "fresh"
        except ProviderFailure as exc:
            error_msg = str(exc)
    else:
        error_msg = "STEAM_WEB_API_KEY or STEAM_ID64 not set"

    if snap is None:
        snap = load_cached(output_path)
        if snap is not None:
            state = "cached"

    if snap is None:
        snap = load_fixture(fixture_path)
        state = "static"

    _write_json(output_path, snap.model_dump(mode="json"))
    cache_utils.write_metadata(
        module_name=MODULE_NAME,
        state=state,
        data_source=snap.data_source,
        human_summary=f"Steam snapshot ({state})",
        error=error_msg,
    )
    return snap


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
    """Write a Steam profile snapshot to *output_path*."""
    snap = build_snapshot(output_path=output_path, fixture_path=fixture_path)
    click.echo(f"steam: wrote {output_path} ({snap.data_source})")


if __name__ == "__main__":
    main()
