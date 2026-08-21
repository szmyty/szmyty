"""Publish privacy-bounded Oura trends as responsive SVG charts.

Oura Cloud API V2 requires OAuth2. Personal access tokens were removed in
December 2025. This module expects a current OAuth access token in the
``OURA_ACCESS_TOKEN`` Actions secret and requests only the ``daily`` scope.

Raw daily records exist in memory only long enough to compute coarse
aggregates. Public artifacts contain no daily arrays, exact sleep/wake times,
workouts, tags, locations, timestamps, or authentication material.
"""

from __future__ import annotations

import html
import json
import os
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from urllib import error, parse, request

import click

from tools.profile_builder import cache as cache_utils
from tools.profile_builder.models import (
    OURA_PUBLIC_AGGREGATE_ALLOWLIST,
    OuraTrendsAggregate,
)

MODULE_NAME = "oura-trends"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = REPO_ROOT / "profile" / "fixtures" / "oura-trends.json"
DEFAULT_OUTPUT = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME / "cache.json"

_API_ROOT = "https://api.ouraring.com/v2"
_TIMEOUT = 20
SAFETY_BUFFER_DAYS = 2
MIN_SAMPLE_DAYS = 20
LONG_WINDOW = 90
SHORT_WINDOW = 30
_MAX_PAGES = 10

_HRV_UP_THRESHOLD = 3.0
_HRV_DOWN_THRESHOLD = -3.0
_READINESS_ABOVE_AVG = 70
_READINESS_BELOW_AVG = 50
_SLEEP_ABOVE_AVG_H = 7.5
_SLEEP_BELOW_AVG_H = 6.5


class ProviderFailure(RuntimeError):
    """Raised when Oura cannot produce a safe public aggregate."""


class PublicationBlocked(RuntimeError):
    """Raised when publication has not been explicitly approved."""


def _env(name: str) -> str | None:
    return os.environ.get(name) or None


def _oura_get(endpoint: str, token: str, params: dict[str, str]) -> dict:
    """Make one authenticated Oura request without exposing auth material."""
    url = f"{_API_ROOT}/{endpoint}?{parse.urlencode(params)}"
    req = request.Request(
        url,
        headers={
            "Authorization": "Bearer " + token,
            "User-Agent": "szmyty-profile-builder/1.0",
        },
    )
    try:
        with request.urlopen(req, timeout=_TIMEOUT) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        if exc.code in (401, 403):
            raise ProviderFailure(
                "Oura access token is expired, revoked, or lacks daily scope"
            ) from exc
        if exc.code == 429:
            raise ProviderFailure("Oura API rate limit exceeded") from exc
        raise ProviderFailure(f"Oura API request failed: HTTP {exc.code}") from exc
    except error.URLError as exc:
        raise ProviderFailure("Oura API unreachable") from exc

    if not isinstance(payload, dict):
        raise ProviderFailure("Oura API returned a non-object response")
    return payload


def _window_dates(window_days: int) -> tuple[date, date]:
    """Return a date window that excludes the current and recent days."""
    today = datetime.now(UTC).date()
    end = today - timedelta(days=SAFETY_BUFFER_DAYS)
    start = end - timedelta(days=window_days - 1)
    return start, end


def _round_sleep(hours: float) -> float:
    """Round sleep duration to the public half-hour boundary."""
    return round(hours * 2) / 2


def _readiness_band(score: float) -> str:
    if score >= _READINESS_ABOVE_AVG:
        return "above-average"
    if score <= _READINESS_BELOW_AVG:
        return "below-average"
    return "average"


def _sleep_band(hours: float) -> str:
    if hours >= _SLEEP_ABOVE_AVG_H:
        return "above-average"
    if hours <= _SLEEP_BELOW_AVG_H:
        return "below-average"
    return "average"


def _activity_band(score: float) -> str:
    if score >= 80:
        return "consistent"
    if score >= 55:
        return "moderate"
    return "low"


def _hrv_direction(values: list[float]) -> str:
    """Return only a coarse direction label for legacy aggregate compatibility."""
    if len(values) < 4:
        return "stable"
    middle = len(values) // 2
    early_mean = sum(values[:middle]) / middle
    late_mean = sum(values[middle:]) / (len(values) - middle)
    delta = late_mean - early_mean
    if delta >= _HRV_UP_THRESHOLD:
        return "trending-up"
    if delta <= _HRV_DOWN_THRESHOLD:
        return "trending-down"
    return "stable"


def _period_label(window_days: int, end_date: date) -> str:
    """Produce a coarse period label."""
    if window_days >= 60:
        return end_date.strftime("%b %Y")
    week_end = end_date + timedelta(days=6 - end_date.weekday())
    return f"week ending {week_end.strftime('%Y-%m-%d')}"


def _apply_allowlist(data: dict) -> dict:
    """Strip every field that is not explicitly approved for public storage."""
    return {
        key: value
        for key, value in data.items()
        if key in OURA_PUBLIC_AGGREGATE_ALLOWLIST
    }


def aggregate_window(
    daily_sleep_seconds: list[float],
    readiness_scores: list[float],
    activity_scores: list[float],
    hrv_rmssd_values: list[float],
    window_days: int,
    end_date: date,
) -> OuraTrendsAggregate:
    """Compute the legacy coarse aggregate used by the public artifact model."""
    contributing_days = len(daily_sleep_seconds)
    avg_sleep: float | None = None
    sleep_band: str | None = None
    avg_readiness: str | None = None
    activity_band_value: str | None = None
    hrv_direction: str | None = None

    if contributing_days >= MIN_SAMPLE_DAYS:
        if daily_sleep_seconds:
            mean_hours = sum(daily_sleep_seconds) / len(daily_sleep_seconds) / 3600.0
            avg_sleep = _round_sleep(mean_hours)
            sleep_band = _sleep_band(mean_hours)

        if readiness_scores:
            avg_readiness = _readiness_band(
                sum(readiness_scores) / len(readiness_scores)
            )
        if activity_scores:
            activity_band_value = _activity_band(
                sum(activity_scores) / len(activity_scores)
            )
        if hrv_rmssd_values:
            hrv_direction = _hrv_direction(hrv_rmssd_values)

    return OuraTrendsAggregate(
        window_days=window_days,  # type: ignore[arg-type]
        contributing_days=contributing_days,
        period_label=_period_label(window_days, end_date),
        avg_sleep_hours=avg_sleep,
        sleep_regularity_band=sleep_band,
        avg_readiness_band=avg_readiness,
        activity_consistency_band=activity_band_value,
        hrv_direction=hrv_direction,
        is_synthetic=False,
        data_source="live",
        generated_month=datetime.now(UTC).strftime("%Y-%m"),
    )


def _parse_daily_scores(payload: dict) -> list[tuple[date, float]]:
    """Extract only day + score into an ephemeral in-memory series."""
    series: list[tuple[date, float]] = []
    data = payload.get("data")
    if not isinstance(data, list):
        return series
    for item in data:
        if not isinstance(item, dict):
            continue
        raw_day = item.get("day")
        raw_score = item.get("score")
        if not isinstance(raw_day, str) or not isinstance(raw_score, (int, float)):
            continue
        try:
            parsed_day = date.fromisoformat(raw_day)
        except ValueError:
            continue
        series.append((parsed_day, float(raw_score)))
    return series


def _fetch_daily_scores(
    endpoint: str,
    token: str,
    start_date: date,
    end_date: date,
) -> list[tuple[date, float]]:
    """Fetch a bounded daily score series, following Oura pagination in memory."""
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "fields": "day,score",
    }
    all_scores: list[tuple[date, float]] = []

    for _ in range(_MAX_PAGES):
        payload = _oura_get(endpoint, token, params)
        all_scores.extend(_parse_daily_scores(payload))
        next_token = payload.get("next_token")
        if not isinstance(next_token, str) or not next_token:
            break
        params["next_token"] = next_token
    return all_scores


def _round_score(score: float) -> int:
    """Round public chart values to five-point buckets."""
    return int(round(score / 5.0) * 5)


def _weekly_scores(
    series: list[tuple[date, float]],
    *,
    max_weeks: int = 8,
) -> list[int]:
    """Aggregate daily scores into coarse unlabeled weekly means."""
    buckets: dict[tuple[int, int], list[float]] = defaultdict(list)
    for day, score in series:
        iso_year, iso_week, _ = day.isocalendar()
        buckets[(iso_year, iso_week)].append(score)

    values = [
        _round_score(sum(scores) / len(scores))
        for _, scores in sorted(buckets.items())[-max_weeks:]
        if scores
    ]
    return values


def fetch_live_with_trends(
    token: str,
) -> tuple[OuraTrendsAggregate, dict[str, list[int]]]:
    """Fetch daily summary scores and immediately reduce them to public trends."""
    start_date, end_date = _window_dates(LONG_WINDOW)
    endpoint_map = {
        "sleep": "usercollection/daily_sleep",
        "readiness": "usercollection/daily_readiness",
        "activity": "usercollection/daily_activity",
    }
    series: dict[str, list[tuple[date, float]]] = {}
    failures = 0

    for name, endpoint in endpoint_map.items():
        try:
            series[name] = _fetch_daily_scores(
                endpoint,
                token,
                start_date,
                end_date,
            )
        except ProviderFailure:
            series[name] = []
            failures += 1

    if failures == len(endpoint_map):
        raise ProviderFailure("Oura daily summary endpoints are unavailable")

    non_empty_counts = [len(values) for values in series.values() if values]
    contributing_days = min(non_empty_counts) if non_empty_counts else 0

    readiness_scores = [score for _, score in series["readiness"]]
    activity_scores = [score for _, score in series["activity"]]
    readiness_band = None
    activity_band = None
    if contributing_days >= MIN_SAMPLE_DAYS:
        if readiness_scores:
            readiness_band = _readiness_band(
                sum(readiness_scores) / len(readiness_scores)
            )
        if activity_scores:
            activity_band = _activity_band(sum(activity_scores) / len(activity_scores))

    aggregate = OuraTrendsAggregate(
        window_days=LONG_WINDOW,  # type: ignore[arg-type]
        contributing_days=contributing_days,
        period_label=_period_label(LONG_WINDOW, end_date),
        avg_sleep_hours=None,
        sleep_regularity_band=None,
        avg_readiness_band=readiness_band,
        activity_consistency_band=activity_band,
        hrv_direction=None,
        is_synthetic=False,
        data_source="live",
        generated_month=datetime.now(UTC).strftime("%Y-%m"),
    )
    trends = {name: _weekly_scores(values) for name, values in series.items()}
    return aggregate, trends


def fetch_live(token: str) -> OuraTrendsAggregate:
    """Compatibility wrapper returning only the public aggregate."""
    aggregate, _ = fetch_live_with_trends(token)
    return aggregate


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_fixture(path: Path = DEFAULT_FIXTURE) -> OuraTrendsAggregate:
    """Load the sanitized synthetic aggregate fixture."""
    return OuraTrendsAggregate.model_validate_json(path.read_text(encoding="utf-8"))


def load_cached(path: Path = DEFAULT_OUTPUT) -> OuraTrendsAggregate | None:
    """Load only a previously published real aggregate."""
    if not path.exists():
        return None
    aggregate = OuraTrendsAggregate.model_validate_json(
        path.read_text(encoding="utf-8")
    )
    if aggregate.is_synthetic:
        return None
    return aggregate.model_copy(update={"data_source": "cache"})


def _palette(dark: bool) -> dict[str, str]:
    if dark:
        return {
            "background": "#0D1117",
            "border": "#30363D",
            "text": "#F0F6FC",
            "muted": "#8B949E",
            "grid": "#30363D",
        }
    return {
        "background": "#FFFFFF",
        "border": "#D0D7DE",
        "text": "#1F2328",
        "muted": "#59636E",
        "grid": "#D8DEE4",
    }


def _polyline(
    values: list[int],
    *,
    x: int,
    y: int,
    width: int,
    height: int,
) -> str:
    if not values:
        return ""
    if len(values) == 1:
        values = [values[0], values[0]]
    step = width / (len(values) - 1)
    points = []
    for index, value in enumerate(values):
        bounded = min(100, max(0, value))
        point_x = x + index * step
        point_y = y + height - (bounded / 100.0) * height
        points.append(f"{point_x:.1f},{point_y:.1f}")
    return " ".join(points)


def _render_svg(
    aggregate: OuraTrendsAggregate,
    trends: dict[str, list[int]],
    *,
    dark: bool,
    mobile: bool,
) -> str:
    palette = _palette(dark)
    width = 360 if mobile else 760
    height = 500 if mobile else 360
    font = "-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"
    colors = {
        "sleep": "#8B5CF6",
        "readiness": "#EC4899",
        "activity": "#10B981",
    }
    labels = {
        "sleep": "SLEEP SCORE",
        "readiness": "READINESS SCORE",
        "activity": "ACTIVITY SCORE",
    }

    if mobile:
        chart_x = 30
        chart_width = 300
        row_y = {"sleep": 145, "readiness": 255, "activity": 365}
        chart_height = 58
    else:
        chart_x = 190
        chart_width = 530
        row_y = {"sleep": 105, "readiness": 190, "activity": 275}
        chart_height = 52

    chart_markup = ""
    for name in ("sleep", "readiness", "activity"):
        values = trends.get(name, [])
        row = row_y[name]
        polyline = _polyline(
            values,
            x=chart_x,
            y=row,
            width=chart_width,
            height=chart_height,
        )
        latest = f"{values[-1]}" if values else "—"
        if mobile:
            label_y = row - 18
            chart_markup += (
                f'<text x="30" y="{label_y}" fill="{palette["muted"]}" '
                f'font-size="11" font-weight="650">{labels[name]}</text>'
                f'<text x="330" y="{label_y}" text-anchor="end" '
                f'fill="{colors[name]}" font-size="15" '
                f'font-weight="720">{latest}</text>'
            )
        else:
            chart_markup += (
                f'<text x="30" y="{row + 22}" fill="{palette["muted"]}" '
                f'font-size="11" font-weight="650">{labels[name]}</text>'
                f'<text x="155" y="{row + 22}" text-anchor="end" '
                f'fill="{colors[name]}" font-size="17" '
                f'font-weight="720">{latest}</text>'
            )

        chart_markup += (
            f'<line x1="{chart_x}" y1="{row + chart_height}" '
            f'x2="{chart_x + chart_width}" y2="{row + chart_height}" '
            f'stroke="{palette["grid"]}" stroke-width="1"/>'
        )
        if polyline:
            chart_markup += (
                f'<polyline points="{polyline}" fill="none" '
                f'stroke="{colors[name]}" stroke-width="3" '
                'stroke-linecap="round" stroke-linejoin="round"/>'
            )

    title = html.escape(str(aggregate.period_label))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
        "<title>Oura aggregate wellness trends</title>"
        "<desc>Coarse weekly sleep, readiness, and activity score trends. "
        "No daily records or exact schedules are published.</desc>"
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" '
        f'fill="{palette["background"]}" stroke="{palette["border"]}"/>'
        f'<g font-family="{font}">'
        f'<text x="28" y="42" fill="{palette["text"]}" font-size="13" '
        'font-weight="700">OURA · AGGREGATE TRENDS</text>'
        f'<text x="28" y="70" fill="{palette["muted"]}" font-size="12">'
        f"{title} · {aggregate.contributing_days} contributing days</text>"
        f"{chart_markup}"
        f'<text x="28" y="{height - 22}" fill="{palette["muted"]}" font-size="11">'
        "Weekly averages rounded to 5-point buckets · recent days excluded"
        "</text></g></svg>"
    )


def render_cards(
    aggregate: OuraTrendsAggregate,
    trends: dict[str, list[int]],
    artifact_dir: Path,
) -> None:
    """Render responsive SVG trend charts without storing raw daily inputs."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    variants = {
        "card-light.svg": (False, False),
        "card-dark.svg": (True, False),
        "card-mobile-light.svg": (False, True),
        "card-mobile-dark.svg": (True, True),
    }
    for filename, (dark, mobile) in variants.items():
        (artifact_dir / filename).write_text(
            _render_svg(aggregate, trends, dark=dark, mobile=mobile),
            encoding="utf-8",
        )


def _cards_exist(artifact_dir: Path) -> bool:
    return all(
        (artifact_dir / filename).exists()
        for filename in (
            "card-light.svg",
            "card-dark.svg",
            "card-mobile-light.svg",
            "card-mobile-dark.svg",
        )
    )


def build_aggregate(
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
    *,
    publication_allowed: bool = False,
) -> OuraTrendsAggregate:
    """Build a live aggregate with real-cache and synthetic-fixture fallbacks."""
    artifact_dir = output_path.parent
    if not publication_allowed:
        aggregate = OuraTrendsAggregate(
            window_days=LONG_WINDOW,  # type: ignore[arg-type]
            contributing_days=0,
            period_label="—",
            is_synthetic=True,
            data_source="disabled",
            generated_month=datetime.now(UTC).strftime("%Y-%m"),
        )
        cache_utils.write_metadata(
            module_name=MODULE_NAME,
            state="disabled",
            data_source="disabled",
            human_summary="oura-trends: publication blocked",
            artifact_dir=artifact_dir,
        )
        return aggregate

    token = _env("OURA_ACCESS_TOKEN")
    aggregate: OuraTrendsAggregate | None = None
    trends: dict[str, list[int]] = {}
    state = "failed-with-fallback"
    error_message: str | None = None

    if token:
        try:
            aggregate, trends = fetch_live_with_trends(token)
            state = "fresh"
        except ProviderFailure:
            error_message = "Oura provider failed (OAuth token or API error)"
    else:
        error_message = "OURA_ACCESS_TOKEN not set"

    if aggregate is None:
        aggregate = load_cached(output_path)
        if aggregate is not None:
            state = "cached"

    if aggregate is None:
        aggregate = load_fixture(fixture_path)
        state = "static"

    public_data = _apply_allowlist(aggregate.model_dump(mode="json"))
    _write_json(output_path, public_data)

    if state == "fresh":
        render_cards(aggregate, trends, artifact_dir)
    elif not _cards_exist(artifact_dir):
        render_cards(aggregate, {}, artifact_dir)

    cache_utils.write_metadata(
        module_name=MODULE_NAME,
        state=state,
        data_source=aggregate.data_source,
        human_summary=f"oura-trends: {LONG_WINDOW}-day aggregate ({state})",
        error=error_message,
        artifact_dir=artifact_dir,
    )
    return aggregate


def load_template_context(artifact_path: Path) -> dict:
    """Expose only sufficiently aggregated, non-synthetic output to README."""
    aggregate = OuraTrendsAggregate.model_validate_json(
        artifact_path.read_text(encoding="utf-8")
    )
    is_public = (
        not aggregate.is_synthetic
        and aggregate.data_source in {"live", "cache"}
        and aggregate.contributing_days >= MIN_SAMPLE_DAYS
    )
    return {"aggregate": aggregate, "is_public": is_public}


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
@click.option(
    "--allow-publication",
    "publication_allowed",
    is_flag=True,
    default=False,
    help="Allow publication of the owner-approved aggregate metric allowlist.",
)
def main(output_path: Path, fixture_path: Path, publication_allowed: bool) -> None:
    """Write the Oura aggregate and responsive SVG charts."""
    aggregate = build_aggregate(
        output_path=output_path,
        fixture_path=fixture_path,
        publication_allowed=publication_allowed,
    )
    click.echo(
        f"oura-trends: {aggregate.data_source} ({aggregate.window_days}-day window)"
    )


if __name__ == "__main__":
    main()
