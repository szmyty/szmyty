"""Fetch and normalize public ORCID record data for the profile README.

Uses the ORCID public API only.  Falls back to a static configured fixture
when the API is unavailable or the ORCID iD is not yet configured.

Reference: https://info.orcid.org/what-is-orcid/services/public-api/
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib import error, request

import click
import yaml

from tools.profile_builder.models import OrcidConfig, OrcidData, OrcidWork

MODULE_NAME = "orcid"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "profile" / "content" / "orcid-config.yml"
DEFAULT_FIXTURE = REPO_ROOT / "profile" / "fixtures" / "orcid.json"
DEFAULT_OUTPUT = REPO_ROOT / "profile" / "artifacts" / MODULE_NAME / "cache.json"
ORCID_API_ROOT = "https://pub.orcid.org/v3.0"
MAX_WORKS = 10


class ProviderFailure(RuntimeError):
    """Raised when the ORCID public API cannot be reached or returns an error."""


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_config(path: Path = DEFAULT_CONFIG) -> OrcidConfig:
    """Load the ORCID configuration slot from YAML."""
    if not path.exists():
        return OrcidConfig()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return OrcidConfig()
    return OrcidConfig.model_validate(raw)


def load_fixture(path: Path = DEFAULT_FIXTURE) -> OrcidData:
    """Load static fallback fixture data."""
    return OrcidData.model_validate_json(path.read_text(encoding="utf-8"))


def load_cached(output_path: Path) -> OrcidData | None:
    """Load the last known-good cached output, if present."""
    if not output_path.exists():
        return None
    try:
        data = OrcidData.model_validate_json(output_path.read_text(encoding="utf-8"))
        return data.model_copy(update={"data_source": "cache"})
    except Exception:  # noqa: BLE001
        return None


def _orcid_get_json(url: str) -> Any:
    headers = {
        "Accept": "application/json",
        "User-Agent": "szmyty-profile-builder/1.0",
    }
    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise ProviderFailure(f"ORCID API error: HTTP {exc.code}") from exc
    except error.URLError as exc:
        raise ProviderFailure(f"ORCID API unavailable: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise ProviderFailure(f"ORCID API returned invalid JSON: {exc}") from exc


def _normalise_work(raw: dict[str, Any]) -> OrcidWork | None:
    """Normalise one raw ORCID work summary into an OrcidWork, or None to skip."""
    summary = raw.get("work-summary")
    if not isinstance(summary, list) or not summary:
        return None
    first = summary[0]
    if not isinstance(first, dict):
        return None

    title_data = first.get("title") or {}
    title_value = (title_data.get("title") or {}).get("value")
    if not title_value:
        return None

    work_type = first.get("type")
    year_val = ((first.get("publication-date") or {}).get("year") or {}).get("value")
    year = int(year_val) if year_val and str(year_val).isdigit() else None

    # Extract DOI or first available external id
    doi: str | None = None
    public_url: str | None = None
    ext_ids = (first.get("external-ids") or {}).get("external-id") or []
    for ext in ext_ids:
        if not isinstance(ext, dict):
            continue
        if ext.get("external-id-type") == "doi":
            doi = ext.get("external-id-value")
        if ext.get("external-id-url", {}).get("value"):
            public_url = ext["external-id-url"]["value"]

    # Contributor role is not always present in the summary; default to author.
    contributor_role = "author"

    return OrcidWork(
        title=str(title_value),
        work_type=work_type,
        year=year,
        doi=doi,
        public_url=public_url,
        contributor_role=contributor_role,
    )


def fetch_live_data(orcid_id: str) -> OrcidData:
    """Fetch and normalise the public ORCID record for *orcid_id*."""
    record = _orcid_get_json(f"{ORCID_API_ROOT}/{orcid_id}/works")
    if not isinstance(record, dict):
        raise ProviderFailure("Unexpected ORCID API payload structure.")

    works_raw = record.get("group") or []
    seen_dois: set[str] = set()
    works: list[OrcidWork] = []
    for group in works_raw:
        if not isinstance(group, dict):
            continue
        work = _normalise_work(group)
        if work is None:
            continue
        # Deduplicate by DOI
        if work.doi:
            if work.doi in seen_dois:
                continue
            seen_dois.add(work.doi)
        works.append(work)
        if len(works) >= MAX_WORKS:
            break

    profile_url = f"https://orcid.org/{orcid_id}"
    return OrcidData(
        orcid_id=orcid_id,
        profile_url=profile_url,
        works=works,
        data_source="live",
    )


def build_orcid(
    config_path: Path = DEFAULT_CONFIG,
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
) -> OrcidData:
    """Build the ORCID artifact, falling back through cache then fixture."""
    config = load_config(config_path)

    if not config.enabled or not config.orcid_id:
        data = OrcidData(data_source="disabled")
        _write_json(output_path, data.model_dump(mode="json"))
        return data

    try:
        data = fetch_live_data(config.orcid_id)
        _write_json(output_path, data.model_dump(mode="json"))
        return data
    except ProviderFailure:
        cached = load_cached(output_path)
        if cached is not None:
            return cached
        if fixture_path.exists():
            return load_fixture(fixture_path)
        return OrcidData(data_source="disabled")


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_CONFIG),
    show_default=True,
)
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
    type=click.Path(path_type=Path),
    default=str(DEFAULT_FIXTURE),
    show_default=True,
)
def main(config_path: Path, output_path: Path, fixture_path: Path) -> None:
    """Write normalized ORCID data to *output_path*."""
    data = build_orcid(
        config_path=config_path,
        output_path=output_path,
        fixture_path=fixture_path,
    )
    click.echo(f"orcid: wrote {output_path} ({data.data_source})")


if __name__ == "__main__":
    main()
