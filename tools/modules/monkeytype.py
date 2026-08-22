"""Fetch and render a privacy-bounded Monkeytype profile snapshot."""

from __future__ import annotations

import html
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib import error, parse, request

import click

from tools.profile_builder import cache as cache_utils

MODULE_NAME = "monkeytype"
PROFILE_URL = "https://monkeytype.com/profile/szmyty"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = REPO_ROOT / "profile" / "fixtures" / "monkeytype.json"
DEFAULT_OUTPUT = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME / "cache.json"

_API_ROOT = "https://api.monkeytype.com"
_TIMEOUT = 15
_DURATIONS = (15, 30, 60, 120)


class ProviderFailure(RuntimeError):
    """Raised when Monkeytype cannot produce a safe live snapshot."""


def _api_get(
    path: str,
    ape_key: str,
    *,
    params: dict[str, str] | None = None,
) -> dict[str, Any]:
    query = f"?{parse.urlencode(params)}" if params else ""
    req = request.Request(
        f"{_API_ROOT}{path}{query}",
        headers={
            "Accept": "application/json",
            "Authorization": f"ApeKey {ape_key}",
            "User-Agent": "szmyty-profile-builder/1.0",
        },
    )
    try:
        with request.urlopen(req, timeout=_TIMEOUT) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise ProviderFailure(
            f"Monkeytype API request failed: HTTP {exc.code}"
        ) from exc
    except error.URLError as exc:
        raise ProviderFailure("Monkeytype API is unreachable") from exc

    if not isinstance(payload, dict):
        raise ProviderFailure("Monkeytype API returned a non-object response")
    return payload


def _numeric(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _candidate_records(value: object) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if _numeric(value.get("wpm")) is not None:
            records.append(value)
        for child in value.values():
            records.extend(_candidate_records(child))
    elif isinstance(value, list):
        for child in value:
            records.extend(_candidate_records(child))
    return records


def _best_record(payload: dict[str, Any]) -> dict[str, Any] | None:
    records = _candidate_records(payload.get("data"))
    if not records:
        return None
    return max(records, key=lambda item: _numeric(item.get("wpm")) or 0.0)


def _normalize_personal_best(
    payload: dict[str, Any],
    duration: int,
) -> dict[str, int | float | None]:
    record = _best_record(payload)
    if record is None:
        return {
            "duration_seconds": duration,
            "wpm": None,
            "accuracy_pct": None,
            "consistency_pct": None,
        }

    return {
        "duration_seconds": duration,
        "wpm": round(_numeric(record.get("wpm")) or 0.0, 1),
        "accuracy_pct": round(_numeric(record.get("acc")) or 0.0, 1),
        "consistency_pct": round(
            _numeric(record.get("consistency")) or 0.0,
            1,
        ),
    }


def fetch_live(ape_key: str) -> dict[str, Any]:
    """Fetch aggregate typing stats and selected time-mode personal bests."""
    stats_payload = _api_get("/users/stats", ape_key)
    stats = stats_payload.get("data")
    if not isinstance(stats, dict):
        raise ProviderFailure("Monkeytype stats payload is missing data")

    personal_bests = []
    for duration in _DURATIONS:
        payload = _api_get(
            "/users/personalBests",
            ape_key,
            params={"mode": "time", "mode2": str(duration)},
        )
        personal_bests.append(_normalize_personal_best(payload, duration))

    completed = stats.get("completedTests")
    started = stats.get("startedTests")
    time_typing = stats.get("timeTyping")
    if not all(isinstance(value, int) for value in (completed, started, time_typing)):
        raise ProviderFailure("Monkeytype stats payload has invalid aggregate values")

    return {
        "profile_url": PROFILE_URL,
        "completed_tests": completed,
        "started_tests": started,
        "time_typing_seconds": time_typing,
        "personal_bests": personal_bests,
        "data_source": "live",
        "data_at": datetime.now(UTC).isoformat(),
        "is_synthetic": False,
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def load_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    """Load the synthetic fixture used only for tests and hidden fallback."""
    snapshot = _load_json(path)
    if snapshot is None:
        raise ProviderFailure(f"Monkeytype fixture is unreadable: {path}")
    return snapshot


def load_cached(path: Path = DEFAULT_OUTPUT) -> dict[str, Any] | None:
    """Load only a prior real snapshot, never promoting synthetic data."""
    snapshot = _load_json(path)
    if snapshot is None or snapshot.get("is_synthetic") is True:
        return None
    snapshot["data_source"] = "cache"
    return snapshot


def _palette(dark: bool) -> dict[str, str]:
    if dark:
        return {
            "background": "#0D1117",
            "panel": "#161B22",
            "border": "#30363D",
            "text": "#F0F6FC",
            "muted": "#8B949E",
            "accent": "#E2B714",
            "accent_text": "#0D1117",
        }
    return {
        "background": "#FFFFFF",
        "panel": "#F6F8FA",
        "border": "#D0D7DE",
        "text": "#1F2328",
        "muted": "#59636E",
        "accent": "#C49A00",
        "accent_text": "#FFFFFF",
    }


def _number(value: object) -> str:
    return f"{value:,}" if isinstance(value, int) else "—"


def _typing_time(seconds: object) -> str:
    if not isinstance(seconds, int) or seconds < 0:
        return "—"
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    if hours:
        return f"{hours:,}h {minutes:02d}m"
    return f"{minutes}m"


def _best_label(best: dict[str, Any]) -> str:
    wpm = best.get("wpm")
    accuracy = best.get("accuracy_pct")
    consistency = best.get("consistency_pct")
    if not isinstance(wpm, (int, float)):
        return "No PB yet"

    value = f"{wpm:g} WPM"
    if isinstance(accuracy, (int, float)):
        value += f" · {accuracy:g}% acc"
    if isinstance(consistency, (int, float)):
        value += f" · {consistency:g}% con"
    return value


def _render_svg(
    snapshot: dict[str, Any],
    *,
    dark: bool,
    mobile: bool,
) -> str:
    palette = _palette(dark)
    width = 360 if mobile else 760
    height = 430 if mobile else 286
    font = "-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"
    completed = _number(snapshot.get("completed_tests"))
    started = _number(snapshot.get("started_tests"))
    typing_time = _typing_time(snapshot.get("time_typing_seconds"))

    raw_bests = snapshot.get("personal_bests")
    bests = raw_bests if isinstance(raw_bests, list) else []
    by_duration = {
        item.get("duration_seconds"): item
        for item in bests
        if isinstance(item, dict)
    }

    if mobile:
        metric_markup = (
            f'<text x="28" y="116" fill="{palette["muted"]}" font-size="10" '
            f'font-weight="650">COMPLETED</text>'
            f'<text x="28" y="141" fill="{palette["text"]}" font-size="19" '
            f'font-weight="700">{completed}</text>'
            f'<text x="188" y="116" fill="{palette["muted"]}" font-size="10" '
            f'font-weight="650">STARTED</text>'
            f'<text x="188" y="141" fill="{palette["text"]}" font-size="19" '
            f'font-weight="700">{started}</text>'
            f'<text x="28" y="175" fill="{palette["muted"]}" font-size="10" '
            f'font-weight="650">TYPING TIME</text>'
            f'<text x="28" y="200" fill="{palette["text"]}" font-size="19" '
            f'font-weight="700">{html.escape(typing_time)}</text>'
        )
        start_y = 248
        row_gap = 40
        best_markup = ""
        for index, duration in enumerate(_DURATIONS):
            y = start_y + index * row_gap
            label = html.escape(_best_label(by_duration.get(duration, {})))
            best_markup += (
                f'<text x="28" y="{y}" fill="{palette["accent"]}" '
                f'font-size="11" font-weight="700">{duration}s</text>'
                f'<text x="72" y="{y}" fill="{palette["text"]}" '
                f'font-size="12">{label}</text>'
            )
    else:
        metric_markup = (
            f'<text x="300" y="54" fill="{palette["muted"]}" font-size="10" '
            f'font-weight="650">COMPLETED</text>'
            f'<text x="300" y="82" fill="{palette["text"]}" font-size="22" '
            f'font-weight="700">{completed}</text>'
            f'<text x="430" y="54" fill="{palette["muted"]}" font-size="10" '
            f'font-weight="650">STARTED</text>'
            f'<text x="430" y="82" fill="{palette["text"]}" font-size="22" '
            f'font-weight="700">{started}</text>'
            f'<text x="545" y="54" fill="{palette["muted"]}" font-size="10" '
            f'font-weight="650">TYPING TIME</text>'
            f'<text x="545" y="82" fill="{palette["text"]}" font-size="22" '
            f'font-weight="700">{html.escape(typing_time)}</text>'
        )
        best_markup = ""
        positions = ((28, 154), (390, 154), (28, 214), (390, 214))
        for duration, (x, y) in zip(_DURATIONS, positions, strict=True):
            label = html.escape(_best_label(by_duration.get(duration, {})))
            best_markup += (
                f'<rect x="{x}" y="{y - 30}" width="330" height="46" rx="10" '
                f'fill="{palette["panel"]}" stroke="{palette["border"]}"/>'
                f'<text x="{x + 14}" y="{y - 8}" fill="{palette["accent"]}" '
                f'font-size="11" font-weight="700">{duration}s PB</text>'
                f'<text x="{x + 76}" y="{y - 8}" fill="{palette["text"]}" '
                f'font-size="12">{label}</text>'
            )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" role="img">'
        "<title>Monkeytype typing statistics for szmyty</title>"
        "<desc>Completed tests, typing time, and selected time-mode "
        "personal bests from the official Monkeytype API.</desc>"
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" '
        f'rx="18" fill="{palette["background"]}" '
        f'stroke="{palette["border"]}"/>'
        f'<g font-family="{font}">'
        f'<rect x="28" y="28" width="34" height="34" rx="8" '
        f'fill="{palette["accent"]}"/>'
        f'<text x="45" y="51" text-anchor="middle" '
        f'fill="{palette["accent_text"]}" font-size="14" '
        'font-weight="800">MT</text>'
        f'<text x="76" y="45" fill="{palette["text"]}" font-size="20" '
        'font-weight="750">Monkeytype</text>'
        f'<text x="76" y="63" fill="{palette["muted"]}" '
        'font-size="11">@szmyty · time-mode personal bests</text>'
        f"{metric_markup}{best_markup}"
        f'<text x="28" y="{height - 18}" fill="{palette["muted"]}" '
        'font-size="10">Official Monkeytype API · first-party snapshot</text>'
        "</g></svg>"
    )


def render_cards(snapshot: dict[str, Any], artifact_dir: Path) -> None:
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
            _render_svg(snapshot, dark=dark, mobile=mobile),
            encoding="utf-8",
        )


def build_snapshot(
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
    *,
    ape_key: str | None = None,
) -> dict[str, Any]:
    """Build live -> last-known-good real cache -> hidden synthetic fixture."""
    key = ape_key if ape_key is not None else os.environ.get("MONKEYTYPE_APE_KEY")
    snapshot: dict[str, Any] | None = None
    state = "failed-with-fallback"
    error_message: str | None = None

    if key:
        try:
            snapshot = fetch_live(key)
            state = "fresh"
        except ProviderFailure as exc:
            error_message = str(exc)
    else:
        error_message = "MONKEYTYPE_APE_KEY not set"

    if snapshot is None:
        snapshot = load_cached(output_path)
        if snapshot is not None:
            state = "cached"

    if snapshot is None:
        snapshot = load_fixture(fixture_path)
        state = "static"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    render_cards(snapshot, output_path.parent)
    cache_utils.write_metadata(
        module_name=MODULE_NAME,
        state=state,
        data_source=str(snapshot.get("data_source") or "fixture"),
        human_summary=f"Monkeytype snapshot ({state})",
        data_at=(
            str(snapshot["data_at"])
            if snapshot.get("data_at") is not None
            else None
        ),
        error=error_message,
        artifact_dir=output_path.parent,
    )
    return snapshot


def load_template_context(artifact_path: Path) -> dict[str, Any]:
    """Hide synthetic Monkeytype data from the public README."""
    snapshot = _load_json(artifact_path) or {}
    is_public = (
        snapshot.get("is_synthetic") is not True
        and snapshot.get("data_source") in {"live", "cache"}
    )
    return {"snapshot": snapshot, "is_public": is_public}


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
    """Refresh Monkeytype stats and render responsive cards."""
    snapshot = build_snapshot(
        output_path=output_path,
        fixture_path=fixture_path,
    )
    click.echo(
        f"monkeytype: wrote {output_path} "
        f"({snapshot.get('data_source', 'unknown')})"
    )


if __name__ == "__main__":
    main()
