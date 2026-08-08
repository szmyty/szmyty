from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Severity = Literal["info", "warning", "error"]


@dataclass(frozen=True)
class Issue:
    rule_id: str
    severity: Severity
    message: str
    article_path: Path | None = None
    line_number: int | None = None
    suggestion: str | None = None

