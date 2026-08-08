"""Edition build pipeline orchestration."""

import json
from pathlib import Path

from magazine.assets.latex import assemble_latex_edition
from magazine.config import Config
from magazine.page import build_page
from magazine.utils import log_info, log_success, log_warn, page_dirs


def build_edition(
    edition_dir: Path,
    *,
    skip_existing: bool = False,
    edition_name: str | None = None,
    reproducible: bool = False,
    exif_disable: bool = False,
    ai_fountain_disable: bool = False,
    latex_disable: bool = False,
    latex_force: bool = False,
    latex_safe_mode: bool = False,
    latex_engine: str | None = None,
    sizes_disable: bool = False,
    sizes_force: bool = False,
    sizes: list[str] | None = None,
    sizes_config: Path | None = None,
    sizes_safe_mode: bool = False,
    config: Config | None = None,
) -> None:
    """Build every page in an edition, then assemble the master LaTeX document.

    Pipeline:
        1. For each page directory (sorted):
               build_page(page_dir, force=True, skip_existing=skip_existing, ...)
        2. assemble_latex_edition(edition_dir, ...)  (unless latex_disable=True)

    ``edition_name`` precedence: passed argument > ``MAGAZINE_EDITION_NAME`` env var
    > ``edition_dir/meta.json`` ``name`` field > empty string.
    """
    if config is None:
        config = Config()
    edition_dir = edition_dir.resolve()
    log_info(f"Building edition: {edition_dir.name}")

    # Resolve edition name following precedence rules
    resolved_name: str = edition_name if edition_name is not None else ""
    if not resolved_name:
        resolved_name = config.EDITION_NAME
    if not resolved_name:
        meta_path = edition_dir / "meta.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
                resolved_name = meta.get("name", "")
            except Exception:  # noqa: BLE001
                log_warn(f"Unable to parse {meta_path}, using fallback edition name.")

    page_dirs_list = page_dirs(edition_dir)
    for page_dir in page_dirs_list:
        build_page(
            page_dir,
            force=True,
            skip_existing=skip_existing,
            edition_name=resolved_name,
            reproducible=reproducible,
            exif_disable=exif_disable,
            ai_fountain_disable=ai_fountain_disable,
            latex_disable=latex_disable,
            latex_force=latex_force,
            latex_safe_mode=latex_safe_mode,
            latex_engine=latex_engine,
            sizes_disable=sizes_disable,
            sizes_force=sizes_force,
            sizes=sizes,
            sizes_config=sizes_config,
            sizes_safe_mode=sizes_safe_mode,
            config=config,
        )

    log_success("Individual page builds complete.")

    if not latex_disable:
        assemble_latex_edition(
            edition_dir,
            safe_mode=latex_safe_mode,
            engine=latex_engine,
            force=latex_force,
            config=config,
        )
