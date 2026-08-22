"""Render the owner-approved manual 16Personalities working-style snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_snapshot(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("working-style artifact must be a JSON object")
    return payload


def load_template_context(artifact_path: Path) -> dict[str, Any]:
    """Load the manual personality snapshot for the README renderer."""
    snapshot = _load_snapshot(artifact_path)
    traits = snapshot.get("traits")
    is_public = bool(
        snapshot.get("is_public") is True
        and snapshot.get("personality_type")
        and snapshot.get("profile_url")
        and isinstance(traits, list)
        and len(traits) == 5
    )
    return {"snapshot": snapshot, "is_public": is_public}
