from __future__ import annotations

from pathlib import Path

import structlog

log = structlog.get_logger(__name__)


def discover_article_dirs(target: Path) -> list[Path]:
    log.debug("discovery.start", target=str(target), is_file=target.is_file())
    if target.is_file():
        if target.name == "published.md":
            log.debug("discovery.single_file", article_dir=str(target.parent))
            return [target.parent]
        log.debug("discovery.file_ignored", path=str(target))
        return []

    article_dirs = [
        path.parent for path in target.rglob("published.md") if path.is_file()
    ]
    discovered = sorted(set(article_dirs))
    log.debug(
        "discovery.complete",
        target=str(target),
        article_count=len(discovered),
        article_dirs=[str(path) for path in discovered],
    )
    return discovered
