"""Fetch and normalize public SoundCloud profile data for the profile README.

Setup
-----
1. Register an application at https://soundcloud.com/you/apps and note the
   client ID and client secret.
2. Add ``SOUNDCLOUD_CLIENT_ID`` and ``SOUNDCLOUD_CLIENT_SECRET`` as repository
   secrets in GitHub → Settings → Secrets and variables → Actions.
3. Set ``SOUNDCLOUD_USER_ID`` (numeric) or ``SOUNDCLOUD_USERNAME`` (slug) as a
   repository variable (non-secret).
4. Set ``enabled: true`` for this module in ``profile/content/modules-registry.yml``
   once Alan has supplied the identifiers and verified the credentials.

Rate limits and expiry
----------------------
SoundCloud's client-credentials flow issues access tokens that expire after
3600 seconds.  This module requests a fresh token on each run and never stores
tokens in caches or logs.  If the token request fails the module falls back to
cached then fixture data and records ``failed-with-fallback`` state.

Revocation
----------
Revoke the application at https://soundcloud.com/you/apps.  Rotate the secret
in GitHub Settings immediately if a token is ever accidentally logged.

Privacy
-------
Only public tracks are fetched.  Unlisted and private tracks are excluded.
Audio files are never downloaded into the repository.  Artwork URLs are stored
as plain text only and are never embedded as active content.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from urllib import error, request

import click

from tools.profile_builder import cache as cache_utils
from tools.profile_builder.models import SoundCloudSnapshot

MODULE_NAME = "soundcloud"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = REPO_ROOT / "profile" / "fixtures" / "soundcloud.json"
DEFAULT_OUTPUT = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME / "cache.json"
_API_ROOT = "https://api.soundcloud.com"
_AUTH_URL = "https://api.soundcloud.com/oauth2/token"
_MAX_TRACKS = 1
_TIMEOUT = 15


class ProviderFailure(RuntimeError):
    """Raised when live data cannot be collected."""


class ConfigurationMissing(ProviderFailure):
    """Raised when required environment variables are absent."""


def _env(name: str) -> str | None:
    return os.environ.get(name) or None


def _request_token(client_id: str, client_secret: str) -> str:
    """Exchange client credentials for an access token (never stored)."""
    payload = parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode()
    req = request.Request(
        _AUTH_URL,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json; charset=utf-8",
            "User-Agent": "szmyty-profile-builder/1.0",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310
            body = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise ProviderFailure(
            f"SoundCloud token request failed: HTTP {exc.code}"
        ) from exc
    except error.URLError as exc:
        raise ProviderFailure(f"SoundCloud auth unreachable: {exc.reason}") from exc
    token = body.get("access_token")
    if not token:
        raise ProviderFailure("SoundCloud token response missing access_token")
    return token  # type: ignore[return-value]


def _api_get(path: str, token: str) -> object:
    url = f"{_API_ROOT}{path}"
    req = request.Request(
        url,
        headers={
            "Authorization": f"OAuth {token}",
            "Accept": "application/json; charset=utf-8",
            "User-Agent": "szmyty-profile-builder/1.0",
        },
    )
    try:
        with request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise ProviderFailure(
            f"SoundCloud API request failed: HTTP {exc.code}"
        ) from exc
    except error.URLError as exc:
        raise ProviderFailure(f"SoundCloud API unreachable: {exc.reason}") from exc


def _resolve_user_identifier() -> tuple[str, str]:
    """Return (lookup_path, display_kind) from environment variables."""
    user_id = _env("SOUNDCLOUD_USER_ID")
    username = _env("SOUNDCLOUD_USERNAME")
    if user_id:
        return f"/users/{user_id}", "user_id"
    if username:
        return f"/resolve?url=https://soundcloud.com/{username}", "username"
    raise ConfigurationMissing(
        "Neither SOUNDCLOUD_USER_ID nor SOUNDCLOUD_USERNAME is set; "
        "module will use fixture fallback."
    )


def fetch_live(client_id: str, client_secret: str) -> SoundCloudSnapshot:
    """Fetch a public SoundCloud snapshot using client-credentials flow."""
    token = _request_token(client_id, client_secret)
    user_path, _ = _resolve_user_identifier()
    user = _api_get(user_path, token)
    if not isinstance(user, dict):
        raise ProviderFailure("Unexpected SoundCloud user response shape")

    # Fetch most recent public track
    uid = user.get("id")
    latest_track_title: str | None = None
    latest_track_url: str | None = None
    if uid:
        try:
            tracks = _api_get(
                f"/users/{uid}/tracks?limit={_MAX_TRACKS}&access=playable&linked_partitioning=0",
                token,
            )
            if isinstance(tracks, list) and tracks:
                t = tracks[0]
                latest_track_title = t.get("title")
                latest_track_url = t.get("permalink_url")
        except ProviderFailure:
            pass  # Non-fatal; snapshot still valid without latest track

    return SoundCloudSnapshot(
        artist_name=user.get("username"),
        profile_url=user.get("permalink_url"),
        latest_track_title=latest_track_title,
        latest_track_url=latest_track_url,
        track_count=user.get("track_count"),
        data_source="live",
        data_at=datetime.now(UTC).isoformat(),
    )


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_fixture(path: Path = DEFAULT_FIXTURE) -> SoundCloudSnapshot:
    """Load sanitized offline fixture data."""
    return SoundCloudSnapshot.model_validate_json(path.read_text(encoding="utf-8"))


def load_cached(path: Path = DEFAULT_OUTPUT) -> SoundCloudSnapshot | None:
    """Load the previous artifact as a fallback cache."""
    if not path.exists():
        return None
    snap = SoundCloudSnapshot.model_validate_json(path.read_text(encoding="utf-8"))
    return snap.model_copy(update={"data_source": "cache"})


def build_snapshot(
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
) -> SoundCloudSnapshot:
    """Build the SoundCloud snapshot with graceful degradation.

    Fetch order:
    1. Live provider (requires SOUNDCLOUD_CLIENT_ID + SOUNDCLOUD_CLIENT_SECRET).
    2. Cached artifact from the previous run.
    3. Sanitized fixture.
    """
    client_id = _env("SOUNDCLOUD_CLIENT_ID")
    client_secret = _env("SOUNDCLOUD_CLIENT_SECRET")

    snap: SoundCloudSnapshot | None = None
    state = "failed-with-fallback"
    error_msg: str | None = None

    if client_id and client_secret:
        try:
            snap = fetch_live(client_id, client_secret)
            state = "fresh"
        except ProviderFailure as exc:
            error_msg = str(exc)
    else:
        error_msg = "SOUNDCLOUD_CLIENT_ID or SOUNDCLOUD_CLIENT_SECRET not set"

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
        human_summary=f"SoundCloud snapshot ({state})",
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
    """Write a SoundCloud profile snapshot to *output_path*."""
    snap = build_snapshot(output_path=output_path, fixture_path=fixture_path)
    click.echo(f"soundcloud: wrote {output_path} ({snap.data_source})")


if __name__ == "__main__":
    main()
