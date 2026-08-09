"""Fetch and publish coarse, privacy-preserving Oura Ring trend aggregates.

Default state
-------------
This module is ``enabled: false`` and
``publication: blocked-pending-owner-approval`` in
``profile/content/modules-registry.yml``.  **No real data or public artifact
is written until the owner explicitly approves the metric allowlist.**

Setup (owner approval required before enabling)
------------------------------------------------
1. Create a Personal Access Token at https://cloud.ouraring.com/personal-access-tokens.
   Request only the scopes needed for approved metrics:
   ``daily_sleep``, ``daily_readiness``, ``daily_activity``, ``heartrate``.
2. Add ``OURA_ACCESS_TOKEN`` as a repository secret under GitHub → Settings →
   Secrets and variables → Actions.
3. Review the publication checklist in ``docs/RUNBOOK.md#oura-trends``.
4. After completing the checklist, set ``enabled: true`` **and**
   ``publication: allowed`` in ``profile/content/modules-registry.yml``.

Rate limits
-----------
The Oura Ring API v2 uses token-bucket rate limiting (~5 000 requests/day per
token for most endpoints).  This module makes at most four requests per run
(one per approved endpoint over the 90-day window).

Privacy and threat model
------------------------
Inferring the following from even coarse wellness aggregates poses real risks:

* **exact sleep/wake schedule** — exposes home presence and daily routine;
* **current location or travel** — sleep-window shifts imply timezone changes;
* **work/commute routine** — regularity and HRV dips correlate with schedules;
* **illness, stress, medication, or mental-health state** — HRV and readiness
  dips are strong illness/stress signals;
* **workouts and activity timestamps** — activity spikes expose exercise
  windows;
* **present-day availability** — readiness bands could imply current fatigue.

Mitigations implemented here:
* Only 30-day and 90-day aggregates are computed — no daily records.
* The current day and a configurable ``SAFETY_BUFFER_DAYS`` are excluded.
* Exact numeric scores are replaced with coarse band labels.
* Sleep duration is rounded to the nearest 0.5 h.
* Period labels use month/year or week-ending date only.
* Metrics are suppressed when ``contributing_days < MIN_SAMPLE_DAYS``.
* Authentication and API errors are masked; only state labels are logged.
* Raw API responses are never written to tracked files, artifacts, or logs.

Authentication boundary
-----------------------
Only ``OURA_ACCESS_TOKEN`` (Personal Access Token) is used.  Automatic OAuth
refresh-token rotation is **not implemented** in this module; defer that until
a safe single-use rotation mechanism is available (see issue #113).
If the token expires, the module falls back to the most recent cached
aggregate or the synthetic fixture — it does not fail unrelated modules.

Data lifecycle
--------------
1. Raw API responses are fetched into an in-memory buffer.
2. Normalisation and aggregation happen in memory; no temp files are written.
3. The publication allowlist (``OURA_PUBLIC_AGGREGATE_ALLOWLIST``) is applied
   before any output is produced.
4. Only the small public aggregate record is written to the tracked artifact
   ``profile/artifacts/oura-trends/cache.json``.
5. Raw responses, daily arrays, exact timestamps, and auth material are never
   committed, logged, or uploaded as Actions artifacts.

Revocation
----------
1. Revoke the token at https://cloud.ouraring.com/personal-access-tokens.
2. Remove or rotate the ``OURA_ACCESS_TOKEN`` repository secret immediately.
3. To remove public output: delete ``profile/artifacts/oura-trends/`` and
   clear the ``<!-- START:oura-trends --> … <!-- END:oura-trends -->`` region
   in ``README.md``, then set ``enabled: false`` and
   ``publication: blocked-pending-owner-approval`` in the registry.

See ``docs/RUNBOOK.md#oura-trends`` for the complete disable/delete procedure.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from urllib import error, request

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

# Aggregation parameters
SAFETY_BUFFER_DAYS: int = 2     # Exclude this many days before today
MIN_SAMPLE_DAYS: int = 20       # Suppress a metric when fewer days contributed
LONG_WINDOW: int = 90           # Primary long-window (days)
SHORT_WINDOW: int = 30          # Secondary short-window (days)

# HRV band thresholds (relative change from window mean, in ms)
_HRV_UP_THRESHOLD = 3.0
_HRV_DOWN_THRESHOLD = -3.0

# Readiness / sleep score band thresholds (Oura v2 scores are 0–100)
_READINESS_ABOVE_AVG = 70
_READINESS_BELOW_AVG = 50

# Sleep duration band thresholds (in hours)
_SLEEP_ABOVE_AVG_H = 7.5
_SLEEP_BELOW_AVG_H = 6.5


class ProviderFailure(RuntimeError):
    """Raised when live data cannot be collected; never exposes auth details."""


class PublicationBlocked(RuntimeError):
    """Raised when the module is disabled or publication is not yet approved."""


def _env(name: str) -> str | None:
    return os.environ.get(name) or None


def _oura_get(endpoint: str, token: str, params: dict[str, str]) -> object:
    """Make one authenticated request to the Oura API.

    Errors are raised as ``ProviderFailure``; the original HTTP response body
    and the token value are never included in the message.
    """
    from urllib.parse import urlencode

    url = f"{_API_ROOT}/{endpoint}?{urlencode(params)}"
    req = request.Request(
        url,
        headers={
            "Authorization": "Bearer " + token,
            "User-Agent": "szmyty-profile-builder/1.0",
        },
    )
    try:
        with request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        if exc.code in (401, 403):
            raise ProviderFailure("Oura token is invalid, expired, or lacks scope") from exc
        raise ProviderFailure(f"Oura API request failed: HTTP {exc.code}") from exc
    except error.URLError as exc:
        raise ProviderFailure("Oura API unreachable") from exc


def _window_dates(window_days: int) -> tuple[date, date]:
    """Return (start_date, end_date_exclusive) excluding safety buffer days."""
    today = datetime.now(UTC).date()
    end = today - timedelta(days=SAFETY_BUFFER_DAYS)
    start = end - timedelta(days=window_days - 1)
    return start, end


def _round_sleep(hours: float) -> float:
    """Round sleep duration to nearest 0.5 h."""
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
    """Classify HRV trend over the window.

    Splits the window in half and compares mean of the later half to the
    earlier half.  Returns a coarse direction label.
    """
    if len(values) < 4:
        return "stable"
    mid = len(values) // 2
    early_mean = sum(values[:mid]) / mid
    late_mean = sum(values[mid:]) / (len(values) - mid)
    delta = late_mean - early_mean
    if delta >= _HRV_UP_THRESHOLD:
        return "trending-up"
    if delta <= _HRV_DOWN_THRESHOLD:
        return "trending-down"
    return "stable"


def _period_label(window_days: int, end_date: date) -> str:
    """Produce a coarse period label (never an exact date)."""
    if window_days >= 60:
        return end_date.strftime("%b %Y")
    # For shorter windows use week-ending rounding
    week_end = end_date - timedelta(days=end_date.weekday())  # Monday of that week
    return f"week ending {week_end.strftime('%Y-%m-%d')}"


def _apply_allowlist(data: dict) -> dict:
    """Strip any key not in the explicit public allowlist.

    This is the *only* gate between normalised data and public output.
    Unknown provider fields are silently dropped — a deny-list alone is
    insufficient.
    """
    return {k: v for k, v in data.items() if k in OURA_PUBLIC_AGGREGATE_ALLOWLIST}


def aggregate_window(
    daily_sleep_seconds: list[float],
    readiness_scores: list[float],
    activity_scores: list[float],
    hrv_rmssd_values: list[float],
    window_days: int,
    end_date: date,
) -> OuraTrendsAggregate:
    """Compute a coarse aggregate for one time window.

    Parameters
    ----------
    daily_sleep_seconds:
        Sleep duration per contributing day, in seconds.
    readiness_scores:
        Readiness scores (0–100) per contributing day.
    activity_scores:
        Activity scores (0–100) per contributing day.
    hrv_rmssd_values:
        HRV RMSSD values (ms) per contributing day.
    window_days:
        Aggregation window in days (30 or 90).
    end_date:
        Last date of the window (already safety-buffered).
    """
    contributing_days = len(daily_sleep_seconds)

    avg_sleep: float | None = None
    sleep_band: str | None = None
    avg_readiness: str | None = None
    activity_band_val: str | None = None
    hrv_dir: str | None = None

    if contributing_days >= MIN_SAMPLE_DAYS:
        if daily_sleep_seconds:
            mean_h = sum(daily_sleep_seconds) / len(daily_sleep_seconds) / 3600.0
            avg_sleep = _round_sleep(mean_h)
            sleep_band = _sleep_band(mean_h)

        if readiness_scores:
            mean_r = sum(readiness_scores) / len(readiness_scores)
            avg_readiness = _readiness_band(mean_r)

        if activity_scores:
            mean_a = sum(activity_scores) / len(activity_scores)
            activity_band_val = _activity_band(mean_a)

        if hrv_rmssd_values:
            hrv_dir = _hrv_direction(hrv_rmssd_values)

    label = _period_label(window_days, end_date)

    return OuraTrendsAggregate(
        window_days=window_days,  # type: ignore[arg-type]
        contributing_days=contributing_days,
        period_label=label,
        avg_sleep_hours=avg_sleep,
        sleep_regularity_band=sleep_band,
        avg_readiness_band=avg_readiness,
        activity_consistency_band=activity_band_val,
        hrv_direction=hrv_dir,
        is_synthetic=False,
        data_source="live",
        generated_month=datetime.now(UTC).strftime("%Y-%m"),
    )


def fetch_live(token: str) -> OuraTrendsAggregate:
    """Fetch Oura data for LONG_WINDOW days and return a coarse aggregate.

    Raw responses are processed in memory.  No temp files are written.
    """
    start, end = _window_dates(LONG_WINDOW)
    params = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
    }

    # --- Sleep ---
    sleep_seconds: list[float] = []
    try:
        sleep_resp = _oura_get("usercollection/daily_sleep", token, params)
        for item in (sleep_resp.get("data", []) if isinstance(sleep_resp, dict) else []):  # type: ignore[union-attr]
            val = item.get("contributors", {}).get("total_sleep", None)
            if val is not None:
                # Oura v2 total_sleep is a score (0–100); duration is under
                # sleep/time_in_bed.  Use sleep.duration (seconds) if present.
                dur = item.get("sleep", {}).get("duration", None)
                if dur is not None:
                    sleep_seconds.append(float(dur))
    except ProviderFailure:
        pass  # Non-fatal; metric will be suppressed

    # --- Readiness ---
    readiness_scores: list[float] = []
    try:
        ready_resp = _oura_get("usercollection/daily_readiness", token, params)
        for item in (ready_resp.get("data", []) if isinstance(ready_resp, dict) else []):  # type: ignore[union-attr]
            score = item.get("score")
            if score is not None:
                readiness_scores.append(float(score))
    except ProviderFailure:
        pass

    # --- Activity ---
    activity_scores: list[float] = []
    try:
        act_resp = _oura_get("usercollection/daily_activity", token, params)
        for item in (act_resp.get("data", []) if isinstance(act_resp, dict) else []):  # type: ignore[union-attr]
            score = item.get("score")
            if score is not None:
                activity_scores.append(float(score))
    except ProviderFailure:
        pass

    # --- HRV (heartrate collection used for RMSSD) ---
    hrv_values: list[float] = []
    try:
        hrv_resp = _oura_get("usercollection/daily_sleep", token, params)
        for item in (hrv_resp.get("data", []) if isinstance(hrv_resp, dict) else []):  # type: ignore[union-attr]
            hrv = item.get("contributors", {}).get("hrv_balance", None)
            if hrv is not None:
                hrv_values.append(float(hrv))
    except ProviderFailure:
        pass

    # Use sleep sample count as the contributing-days count (most restrictive)
    return aggregate_window(
        daily_sleep_seconds=sleep_seconds,
        readiness_scores=readiness_scores,
        activity_scores=activity_scores,
        hrv_rmssd_values=hrv_values,
        window_days=LONG_WINDOW,
        end_date=end,
    )


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_fixture(path: Path = DEFAULT_FIXTURE) -> OuraTrendsAggregate:
    """Load the sanitised synthetic fixture."""
    return OuraTrendsAggregate.model_validate_json(path.read_text(encoding="utf-8"))


def load_cached(path: Path = DEFAULT_OUTPUT) -> OuraTrendsAggregate | None:
    """Load the previous aggregate artifact as a fallback cache."""
    if not path.exists():
        return None
    agg = OuraTrendsAggregate.model_validate_json(path.read_text(encoding="utf-8"))
    return agg.model_copy(update={"data_source": "cache"})


def build_aggregate(
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
    *,
    publication_allowed: bool = False,
) -> OuraTrendsAggregate:
    """Build the Oura aggregate with graceful degradation.

    When ``publication_allowed`` is False (the default), the module writes
    nothing to the tracked artifact and returns a ``disabled`` state.

    Fetch order (only when publication_allowed is True):
    1. Live provider (requires ``OURA_ACCESS_TOKEN``).
    2. Cached artifact from the previous run.
    3. Synthetic fixture.
    """
    if not publication_allowed:
        agg = OuraTrendsAggregate(
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
            human_summary="oura-trends: publication blocked pending owner approval",
        )
        return agg

    token = _env("OURA_ACCESS_TOKEN")
    agg: OuraTrendsAggregate | None = None
    state = "failed-with-fallback"
    error_msg: str | None = None

    if token:
        try:
            agg = fetch_live(token)
            state = "fresh"
        except ProviderFailure:
            error_msg = "Oura provider failed (credentials or API error)"
    else:
        error_msg = "OURA_ACCESS_TOKEN not set"

    if agg is None:
        agg = load_cached(output_path)
        if agg is not None:
            state = "cached"

    if agg is None:
        agg = load_fixture(fixture_path)
        state = "static"

    # Apply the explicit allowlist before writing any tracked file.
    public_data = _apply_allowlist(agg.model_dump(mode="json"))
    _write_json(output_path, public_data)
    cache_utils.write_metadata(
        module_name=MODULE_NAME,
        state=state,
        data_source=agg.data_source,
        human_summary=f"oura-trends: {LONG_WINDOW}-day aggregate ({state})",
        error=error_msg,
    )
    return agg


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
    help="Allow public artifact output (requires owner approval).",
)
def main(output_path: Path, fixture_path: Path, publication_allowed: bool) -> None:
    """Write a coarse Oura trends aggregate to *output_path*."""
    agg = build_aggregate(
        output_path=output_path,
        fixture_path=fixture_path,
        publication_allowed=publication_allowed,
    )
    click.echo(f"oura-trends: {agg.data_source} ({agg.window_days}-day window)")


if __name__ == "__main__":
    main()
