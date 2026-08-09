"""Last-known-good cache for profile module data.

Each module writes its normalized data to a JSON artifact file. On provider
failure, the cached artifact is read back and returned unchanged, keeping the
README stable without network access.
"""

from __future__ import annotations

import json
import logging
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
