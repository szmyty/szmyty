"""Last-known-good cache for profile module data.

Each module writes its normalized data to a JSON artifact file. On provider
failure, the cached artifact is read back and returned unchanged, keeping the
README stable without network access.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CACHE_ROOT = Path(__file__).parent.parent.parent / 'profile' / 'artifacts'


def read_cache(module_name: str) -> dict[str, Any] | None:
    """Read last-known-good JSON for *module_name*, or None if unavailable."""
    cache_path = CACHE_ROOT / module_name / 'cache.json'
    if not cache_path.exists():
        return None
    try:
        return json.loads(cache_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning('cache read failed for %s: %s', module_name, exc)
        return None


def write_cache(module_name: str, data: dict[str, Any]) -> None:
    """Write *data* as the last-known-good JSON for *module_name*."""
    cache_path = CACHE_ROOT / module_name / 'cache.json'
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )


def write_metadata(
    module_name: str,
    state: str,
    data_source: str,
    human_summary: str,
    ttl_seconds: int | None = None,
    data_at: str | None = None,
    data_hash: str | None = None,
    is_stale: bool = False,
    seconds_until_stale: int | None = None,
    error: str | None = None,
    artifact_dir: Path | None = None,
) -> None:
    """Write a metadata.json file into the module artifact directory.

    By default the file is placed at ``CACHE_ROOT / module_name /
    metadata.json``, which resolves to
    ``profile/artifacts/<module_name>/metadata.json`` relative to the repo
    root.  Pass *artifact_dir* (an absolute path) to write to a different
    location — this must match the ``artifact_dir`` field declared in the
    module registry so that the ``snapshot`` CLI command can read it back.
    """
    metadata: dict[str, Any] = {
        "module_name": module_name,
        "version": "1.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "state": state,
        "data_source": data_source,
        "data_at": data_at,
        "data_hash": data_hash,
        "ttl_seconds": ttl_seconds,
        "is_stale": is_stale,
        "seconds_until_stale": seconds_until_stale,
        "human_summary": human_summary,
        "error": error,
    }
    target_dir = artifact_dir if artifact_dir is not None else CACHE_ROOT / module_name
    metadata_path = target_dir / "metadata.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
