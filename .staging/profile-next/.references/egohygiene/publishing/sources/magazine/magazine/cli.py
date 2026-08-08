"""CLI entry point for the magazine production engine (Click-based)."""

import sys
from pathlib import Path

import click

import magazine
from magazine.assets.sizes import parse_sizes_list
from magazine.bundler import finalize_edition
from magazine.config import Config
from magazine.edition import build_edition
from magazine.exceptions import MagazineError
from magazine.metadata import gen_page_meta
from magazine.page import build_page
from magazine.utils import log_error, page_dirs, validate_dependencies


def _check_deps(active_stages: list[str] | None = None) -> None:
    """Run stage-aware dependency check, exiting with an error message on failure."""
    try:
        validate_dependencies(active_stages)
    except MagazineError as exc:
        log_error(str(exc))
        sys.exit(1)


@click.group()
@click.version_option(version=magazine.__version__, prog_name="magazine")
@click.option(
    "--reproducible",
    is_flag=True,
    default=False,
    help="Use fixed epoch timestamps in metadata for deterministic builds.",
)
@click.option(
    "--ai-fountain-model",
    default=None,
    metavar="MODEL",
    help="Override the Fountain AI model (overrides MAGAZINE_FOUNTAIN_AI_MODEL env var).",
)
@click.option(
    "--ai-fountain-runtime",
    default=None,
    metavar="RUNTIME",
    help="Override the Fountain AI runtime binary (overrides MAGAZINE_FOUNTAIN_AI_RUNTIME env var).",
)
@click.pass_context
def cli(ctx: click.Context, reproducible: bool, ai_fountain_model: str | None, ai_fountain_runtime: str | None) -> None:
    """magazine — Holistic Production Engine.

    \b
    Commands:
      manifest  <edition_path>
      page      <page_path> [--force]
      edition   <edition_path> [--skip-existing]
      finalize  <edition_path> [--force]
    """
    ctx.ensure_object(dict)
    ctx.obj["reproducible"] = reproducible
    cfg = Config()
    if ai_fountain_model is not None:
        cfg.FOUNTAIN_AI_MODEL = ai_fountain_model
    if ai_fountain_runtime is not None:
        cfg.FOUNTAIN_AI_RUNTIME = ai_fountain_runtime
    ctx.obj["config"] = cfg


@cli.command()
@click.argument("edition_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--metadata-exif-disable", is_flag=True, default=False, help="Skip EXIF extraction when generating metadata.")
@click.pass_context
def manifest(ctx: click.Context, edition_path: Path, metadata_exif_disable: bool) -> None:
    """Generate meta.json for every page in EDITION_PATH."""
    active_stages = ["metadata"]
    if not metadata_exif_disable:
        active_stages.append("exif")
    _check_deps(active_stages)
    reproducible: bool = ctx.obj.get("reproducible", False)
    cfg: Config = ctx.obj["config"]
    try:
        for p in page_dirs(edition_path):
            gen_page_meta(p, reproducible=reproducible, exif_disable=metadata_exif_disable, config=cfg)
    except MagazineError as exc:
        log_error(str(exc))
        sys.exit(1)


@cli.command()
@click.argument("page_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--force", is_flag=True, default=False, help="Force rebuild of page artifacts.")
@click.option("--edition", default=None, metavar="NAME", help="Edition name for the Fountain header (overrides env/config).")
@click.option("--metadata-exif-disable", is_flag=True, default=False, help="Skip EXIF extraction when generating metadata.")
@click.option("--latex-disable", is_flag=True, default=False, help="Skip LaTeX generation for this page.")
@click.option("--latex-force", is_flag=True, default=False, help="Force LaTeX regeneration even if inputs are unchanged.")
@click.option("--latex-safe-mode", is_flag=True, default=False, help="Use safe-margin layout instead of full-bleed.")
@click.option("--latex-engine", default=None, metavar="ENGINE", help="LaTeX engine to use (xelatex or pdflatex).")
@click.option("--ai-fountain-disable", is_flag=True, default=False, help="Skip AI Fountain generation for this page.")
@click.option("--sizes-disable", is_flag=True, default=False, help="Skip size variant generation for this page.")
@click.option("--sizes-force", is_flag=True, default=False, help="Force size variant regeneration even if inputs are unchanged.")
@click.option("--sizes", default=None, metavar="SIZES", help="Comma-separated size names to generate, or 'all'.")
@click.option("--sizes-config", default=None, type=click.Path(path_type=Path), metavar="PATH", help="Path to a custom sizes JSON config file.")
@click.option("--sizes-safe-mode", is_flag=True, default=False, help="Record safe-mode in size variant metadata.")
@click.pass_context
def page(
    ctx: click.Context,
    page_path: Path,
    force: bool,
    edition: str | None,
    metadata_exif_disable: bool,
    latex_disable: bool,
    latex_force: bool,
    latex_safe_mode: bool,
    latex_engine: str | None,
    ai_fountain_disable: bool,
    sizes_disable: bool,
    sizes_force: bool,
    sizes: str | None,
    sizes_config: Path | None,
    sizes_safe_mode: bool,
) -> None:
    """Build a single PAGE_PATH."""
    active_stages = ["metadata", "images", "screenplay"]
    if not metadata_exif_disable:
        active_stages.append("exif")
    if not ai_fountain_disable:
        active_stages.append("ai")
    if not latex_disable:
        active_stages.append("latex")
    if not sizes_disable:
        active_stages.append("sizes")
    _check_deps(active_stages)
    reproducible: bool = ctx.obj.get("reproducible", False)
    cfg: Config = ctx.obj["config"]
    try:
        build_page(
            page_path,
            force=force,
            skip_existing=False,
            edition_name=edition if edition is not None else cfg.EDITION_NAME,
            reproducible=reproducible,
            exif_disable=metadata_exif_disable,
            ai_fountain_disable=ai_fountain_disable,
            latex_disable=latex_disable,
            latex_force=latex_force,
            latex_safe_mode=latex_safe_mode,
            latex_engine=latex_engine,
            sizes_disable=sizes_disable,
            sizes_force=sizes_force,
            sizes=parse_sizes_list(sizes),
            sizes_config=sizes_config,
            sizes_safe_mode=sizes_safe_mode,
            config=cfg,
        )
    except MagazineError as exc:
        log_error(str(exc))
        sys.exit(1)


@cli.command()
@click.argument("edition_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--skip-existing", is_flag=True, default=False, help="Skip pages that already have artifacts.")
@click.option("--edition", default=None, metavar="NAME", help="Edition name for the Fountain header (overrides env/meta.json).")
@click.option("--metadata-exif-disable", is_flag=True, default=False, help="Skip EXIF extraction when generating metadata.")
@click.option("--latex-disable", is_flag=True, default=False, help="Skip LaTeX generation for this edition.")
@click.option("--latex-force", is_flag=True, default=False, help="Force LaTeX regeneration even if inputs are unchanged.")
@click.option("--latex-safe-mode", is_flag=True, default=False, help="Use safe-margin layout instead of full-bleed.")
@click.option("--latex-engine", default=None, metavar="ENGINE", help="LaTeX engine to use (xelatex or pdflatex).")
@click.option("--ai-fountain-disable", is_flag=True, default=False, help="Skip AI Fountain generation for this edition.")
@click.option("--sizes-disable", is_flag=True, default=False, help="Skip size variant generation for this edition.")
@click.option("--sizes-force", is_flag=True, default=False, help="Force size variant regeneration even if inputs are unchanged.")
@click.option("--sizes", default=None, metavar="SIZES", help="Comma-separated size names to generate, or 'all'.")
@click.option("--sizes-config", default=None, type=click.Path(path_type=Path), metavar="PATH", help="Path to a custom sizes JSON config file.")
@click.option("--sizes-safe-mode", is_flag=True, default=False, help="Record safe-mode in size variant metadata.")
@click.pass_context
def edition(
    ctx: click.Context,
    edition_path: Path,
    skip_existing: bool,
    edition: str | None,
    metadata_exif_disable: bool,
    latex_disable: bool,
    latex_force: bool,
    latex_safe_mode: bool,
    latex_engine: str | None,
    ai_fountain_disable: bool,
    sizes_disable: bool,
    sizes_force: bool,
    sizes: str | None,
    sizes_config: Path | None,
    sizes_safe_mode: bool,
) -> None:
    """Build all pages in EDITION_PATH."""
    active_stages = ["metadata", "images", "screenplay"]
    if not metadata_exif_disable:
        active_stages.append("exif")
    if not ai_fountain_disable:
        active_stages.append("ai")
    if not latex_disable:
        active_stages.append("latex")
    if not sizes_disable:
        active_stages.append("sizes")
    _check_deps(active_stages)
    reproducible: bool = ctx.obj.get("reproducible", False)
    cfg: Config = ctx.obj["config"]
    try:
        build_edition(
            edition_path,
            skip_existing=skip_existing,
            edition_name=edition,
            reproducible=reproducible,
            exif_disable=metadata_exif_disable,
            ai_fountain_disable=ai_fountain_disable,
            latex_disable=latex_disable,
            latex_force=latex_force,
            latex_safe_mode=latex_safe_mode,
            latex_engine=latex_engine,
            sizes_disable=sizes_disable,
            sizes_force=sizes_force,
            sizes=parse_sizes_list(sizes),
            sizes_config=sizes_config,
            sizes_safe_mode=sizes_safe_mode,
            config=cfg,
        )
    except MagazineError as exc:
        log_error(str(exc))
        sys.exit(1)


@cli.command()
@click.argument("edition_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--force", is_flag=True, default=False, help="Continue even if page.png files are missing.")
@click.option("--dry-run", is_flag=True, default=False, help="Log intended cleanup actions without modifying the filesystem.")
@click.option("--sizes-disable", is_flag=True, default=False, help="Skip bundle size variant generation.")
@click.option("--sizes-force", is_flag=True, default=False, help="Force bundle size variant regeneration even if inputs are unchanged.")
@click.option("--sizes", default=None, metavar="SIZES", help="Comma-separated size names to generate, or 'all'.")
@click.option("--sizes-config", default=None, type=click.Path(path_type=Path), metavar="PATH", help="Path to a custom sizes JSON config file.")
@click.option("--sizes-safe-mode", is_flag=True, default=False, help="Record safe-mode in bundle size variant metadata.")
@click.pass_context
def finalize(
    ctx: click.Context,
    edition_path: Path,
    force: bool,
    dry_run: bool,
    sizes_disable: bool,
    sizes_force: bool,
    sizes: str | None,
    sizes_config: Path | None,
    sizes_safe_mode: bool,
) -> None:
    """Bundle EDITION_PATH into publishing artifacts (CBZ, PDFs, metadata)."""
    active_stages = ["bundle", "images"]
    if not sizes_disable:
        active_stages.append("sizes")
    _check_deps(active_stages)
    reproducible: bool = ctx.obj.get("reproducible", False)
    cfg: Config = ctx.obj["config"]
    try:
        finalize_edition(
            edition_path,
            force=force,
            dry_run=dry_run,
            reproducible=reproducible,
            sizes_disable=sizes_disable,
            sizes_force=sizes_force,
            sizes=parse_sizes_list(sizes),
            sizes_config=sizes_config,
            sizes_safe_mode=sizes_safe_mode,
            config=cfg,
        )
    except MagazineError as exc:
        log_error(str(exc))
        sys.exit(1)

