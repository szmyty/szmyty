"""Click CLI for the Medium RSS ingestion tool."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
import structlog
import yaml
from rich.console import Console
from rich.table import Table

from medium_rss.content_parser import parse_article, rewrite_image_references
from medium_rss.downloader import download_asset
from medium_rss.feed import fetch_feed
from medium_rss.manifest import (
    classify_article,
    load_manifest,
    save_manifest,
    update_manifest,
)
from medium_rss.models import FeedConfig, MediumArticle, Manifest, SyncConfig
from medium_rss.normalizer import generate_slug, normalize_entry
from medium_rss.renderer import render_markdown

log = structlog.get_logger(__name__)
console = Console()


@click.group()
@click.option("--debug", is_flag=True, help="Enable structured debug logging.")
def main(debug: bool) -> None:
    """Medium RSS ingestion tool for Ego Hygiene."""
    _configure_logging(debug)


@main.command()
@click.option(
    "--config",
    "config_path",
    default="publishing/medium/config.yaml",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the YAML configuration file.",
)
@click.option("--dry-run", is_flag=True, help="Report what would change without writing.")
@click.option(
    "--download-images/--no-download-images",
    default=True,
    show_default=True,
    help="Download article images into assets/ directories.",
)
@click.option(
    "--render-markdown/--no-render-markdown",
    default=True,
    show_default=True,
    help="Produce article.md alongside article.html.",
)
def sync(
    config_path: Path,
    dry_run: bool,
    download_images: bool,
    render_markdown: bool,
) -> None:
    """Synchronize Medium RSS feeds into the repository."""
    download_images = _env_bool("MEDIUM_DOWNLOAD_IMAGES", download_images)
    render_markdown = _env_bool("MEDIUM_RENDER_MARKDOWN", render_markdown)
    config, workspace_root, _ = _load_config(config_path)

    totals: dict[str, int] = {
        "feeds": 0,
        "new": 0,
        "updated": 0,
        "unchanged": 0,
        "assets_downloaded": 0,
        "assets_skipped": 0,
        "failed": 0,
    }

    for feed_cfg in config.feeds:
        _apply_env_overrides(feed_cfg)
        output_dir = _resolve_output_path(Path(feed_cfg.output), workspace_root)
        _sync_feed(
            feed_cfg, output_dir, workspace_root, dry_run,
            download_images, render_markdown, totals,
        )

    _print_summary(totals, dry_run)

    if totals["failed"] > 0:
        sys.exit(1)


@main.command()
@click.option(
    "--config",
    "config_path",
    default="publishing/medium/config.yaml",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the YAML configuration file.",
)
def validate(config_path: Path) -> None:
    """Validate the configuration file and print a summary."""
    config, workspace_root, resolved_config_path = _load_config(config_path)
    console.print(f"[bold green]✔[/bold green] Configuration valid: {resolved_config_path}")
    for feed in config.feeds:
        console.print(f"  • [bold]{feed.id}[/bold] → {feed.url}")
        console.print(
            f"    output: {_resolve_output_path(Path(feed.output), workspace_root)}"
        )


@main.command()
@click.option(
    "--config",
    "config_path",
    default="publishing/medium/config.yaml",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the YAML configuration file.",
)
def inspect(config_path: Path) -> None:
    """Print the current manifest state for all configured feeds."""
    config, workspace_root, _ = _load_config(config_path)
    for feed_cfg in config.feeds:
        output_dir = _resolve_output_path(Path(feed_cfg.output), workspace_root)
        manifest = load_manifest(output_dir, feed_cfg.url)
        table = Table(title=f"Feed: {feed_cfg.id}", show_lines=True)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Slug", style="green", no_wrap=True)
        table.add_column("Title")
        table.add_column("Content Hash", style="dim")
        table.add_column("Published")
        table.add_column("Last Synced")
        for entry in manifest.articles.values():
            table.add_row(
                entry.id[:16],
                entry.slug or "(none)",
                entry.canonical_url[:60],
                entry.content_hash[:12] + "…",
                entry.published_at.strftime("%Y-%m-%d") if entry.published_at else "—",
                entry.last_synced.strftime("%Y-%m-%d"),
            )
        console.print(table)
        console.print(
            f"Total: [bold]{len(manifest.articles)}[/bold] articles | "
            f"Last sync: {manifest.last_sync or 'never'}"
        )


@main.command("migrate-slugs")
@click.option(
    "--config",
    "config_path",
    default="publishing/medium/config.yaml",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the YAML configuration file.",
)
@click.option("--dry-run", is_flag=True, help="Report what would change without writing.")
def migrate_slugs(config_path: Path, dry_run: bool) -> None:
    """Regenerate article slugs and rename article directories.

    Idempotent – articles that already have a slug are skipped.
    """
    config, workspace_root, _ = _load_config(config_path)

    for feed_cfg in config.feeds:
        output_dir = _resolve_output_path(Path(feed_cfg.output), workspace_root)
        _migrate_feed_slugs(feed_cfg, output_dir, dry_run)


# ---------------------------------------------------------------------------
# Internal sync logic
# ---------------------------------------------------------------------------


def _sync_feed(
    feed_cfg: FeedConfig,
    output_dir: Path,
    workspace_root: Path,
    dry_run: bool,
    download_images: bool,
    render_md: bool,
    totals: dict[str, int],
) -> None:
    totals["feeds"] += 1
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold]📰 Syncing feed:[/bold] {feed_cfg.id}")
    console.print(f"   URL: {feed_cfg.url}")

    try:
        raw_entries = fetch_feed(feed_cfg.url)
    except Exception as exc:
        console.print(f"[red]✗ Failed to fetch feed {feed_cfg.id}: {exc}[/red]")
        totals["failed"] += 1
        return

    manifest = load_manifest(output_dir, feed_cfg.url)
    slug_registry = _build_slug_registry(manifest)
    changed = False

    for raw in raw_entries:
        article = normalize_entry(raw, feed_cfg.url)
        if article is None:
            totals["failed"] += 1
            continue

        status, existing = classify_article(article, manifest)

        if status == "unchanged":
            totals["unchanged"] += 1
            log.debug("sync.unchanged", article_id=article.id)
            continue

        # Assign human-readable slug
        article.slug = _assign_slug(article, existing, slug_registry)
        article_dir = output_dir / "articles" / article.slug

        log.debug(
            "sync.article",
            article_id=article.id,
            slug=article.slug,
            status=status,
        )

        if not dry_run:
            article_dir.mkdir(parents=True, exist_ok=True)
            assets_dir = article_dir / "assets"

            # Parse and clean article HTML
            parsed = parse_article(article.content_html)

            # Download images
            if download_images:
                for img in parsed.images:
                    local_path = download_asset(img.src, assets_dir)
                    if local_path:
                        img.local_path = _display_path(local_path, workspace_root)
                        article.asset_paths[img.src] = img.local_path
                        totals["assets_downloaded"] += 1
                    else:
                        totals["assets_skipped"] += 1

            # Rewrite image references to local paths
            final_html = rewrite_image_references(parsed.clean_html, parsed.images)

            # Preserve first_seen from existing entry
            if existing:
                article.first_seen = existing.first_seen  # type: ignore[misc]

            _write_article_files(article, article_dir, final_html, render_md)
            update_manifest(manifest, article, status, existing)
            changed = True

        if status == "new":
            totals["new"] += 1
            console.print(f"  [green]+[/green] new: {article.slug}")
        else:
            totals["updated"] += 1
            console.print(f"  [yellow]~[/yellow] updated: {article.slug}")

    if not dry_run and changed:
        manifest.last_sync = datetime.now(timezone.utc)
        save_manifest(manifest, output_dir)


def _write_article_files(
    article: MediumArticle,
    article_dir: Path,
    clean_html: str,
    render_md: bool,
) -> None:
    """Write metadata.json, article.html, and optionally article.md."""
    # metadata.json
    meta_path = article_dir / "metadata.json"
    meta_path.write_text(
        json.dumps(article.to_metadata_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # article.html – preserve original cleaned HTML
    html_path = article_dir / "article.html"
    html_path.write_text(clean_html, encoding="utf-8")

    # article.md – normalized Markdown representation
    if render_md:
        md = render_markdown(clean_html)
        md_path = article_dir / "article.md"
        md_path.write_text(md, encoding="utf-8")


def _build_slug_registry(manifest: Manifest) -> dict[str, str]:
    """Return a mapping of *slug → article_id* for all articles in the manifest."""
    registry: dict[str, str] = {}
    for article_id, entry in manifest.articles.items():
        if entry.slug:
            registry[entry.slug] = article_id
    return registry


def _assign_slug(
    article: MediumArticle,
    existing: Any,
    slug_registry: dict[str, str],
) -> str:
    """Return the slug to use for *article*, registering it in *slug_registry*."""
    if existing and existing.slug:
        return existing.slug

    base_slug = generate_slug(article.title, article.id)
    slug = base_slug
    counter = 2
    while slug in slug_registry and slug_registry[slug] != article.id:
        slug = f"{base_slug}-{counter}"
        counter += 1

    slug_registry[slug] = article.id
    return slug


def _migrate_feed_slugs(
    feed_cfg: FeedConfig,
    output_dir: Path,
    dry_run: bool,
) -> None:
    """Regenerate slugs for articles that lack one and rename directories."""
    console.print(f"\n[bold]🔄 Migrating slugs for feed:[/bold] {feed_cfg.id}")
    manifest = load_manifest(output_dir, feed_cfg.url)

    if not manifest.articles:
        console.print("   No articles in manifest – nothing to migrate.")
        return

    slug_registry: dict[str, str] = {}
    for entry in manifest.articles.values():
        if entry.slug:
            slug_registry[entry.slug] = entry.id

    migrated = 0
    skipped = 0

    for article_id, entry in list(manifest.articles.items()):
        if entry.slug:
            skipped += 1
            continue

        # Load title from on-disk metadata if available
        title = _load_article_title(output_dir, article_id)
        base_slug = generate_slug(title, article_id)
        slug = base_slug
        counter = 2
        while slug in slug_registry and slug_registry[slug] != article_id:
            slug = f"{base_slug}-{counter}"
            counter += 1
        slug_registry[slug] = article_id

        old_dir = output_dir / "articles" / article_id
        new_dir = output_dir / "articles" / slug

        if dry_run:
            console.print(f"  [dim](dry-run)[/dim] {article_id[:16]} → {slug}")
        else:
            if old_dir.exists() and not new_dir.exists():
                old_dir.rename(new_dir)
            entry.slug = slug
            manifest.articles[article_id] = entry
            console.print(f"  [green]→[/green] {article_id[:16]} → {slug}")

        migrated += 1

    if not dry_run and migrated > 0:
        save_manifest(manifest, output_dir)

    mode = " [dim](dry-run)[/dim]" if dry_run else ""
    console.print(
        f"\n  Migrated: [green]{migrated}[/green]{mode}  "
        f"Already done: {skipped}"
    )


def _load_article_title(output_dir: Path, article_id: str) -> str:
    meta_path = output_dir / "articles" / article_id / "metadata.json"
    if meta_path.exists():
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            return str(data.get("title", ""))
        except Exception:
            pass
    return ""


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------


def _load_config(config_path: Path) -> tuple[SyncConfig, Path, Path]:
    resolved_config_path = _resolve_config_path(config_path)
    workspace_root = _find_workspace_root(resolved_config_path.parent)
    try:
        data = yaml.safe_load(resolved_config_path.read_text(encoding="utf-8")) or {}
        return SyncConfig.from_dict(data), workspace_root, resolved_config_path
    except Exception as exc:
        raise click.ClickException(
            f"Failed to parse config {resolved_config_path}: {exc}"
        ) from exc


def _apply_env_overrides(feed_cfg: FeedConfig) -> None:
    url_override = os.environ.get("MEDIUM_RSS_URL")
    if url_override:
        feed_cfg.url = url_override
    output_override = os.environ.get("MEDIUM_OUTPUT_DIRECTORY")
    if output_override:
        feed_cfg.output = output_override


def _env_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() not in {"0", "false", "no", "off"}


def _print_summary(totals: dict[str, int], dry_run: bool) -> None:
    mode = " [dim](dry-run)[/dim]" if dry_run else ""
    console.print(f"\n[bold]📊 Sync summary{mode}[/bold]")
    console.print(f"  Feeds processed    : {totals['feeds']}")
    console.print(f"  New articles       : [green]{totals['new']}[/green]")
    console.print(f"  Updated articles   : [yellow]{totals['updated']}[/yellow]")
    console.print(f"  Unchanged articles : {totals['unchanged']}")
    console.print(f"  Assets downloaded  : [cyan]{totals['assets_downloaded']}[/cyan]")
    console.print(f"  Assets skipped     : {totals['assets_skipped']}")
    console.print(f"  Failed             : [red]{totals['failed']}[/red]")


def _resolve_config_path(config_path: Path) -> Path:
    if config_path.is_absolute():
        if config_path.exists():
            return config_path
        raise click.ClickException(f"Configuration file not found: {config_path}")

    candidate = (Path.cwd() / config_path).resolve()
    if candidate.exists():
        return candidate

    workspace_root = _find_workspace_root(Path.cwd())
    workspace_candidate = (workspace_root / config_path).resolve()
    if workspace_candidate.exists():
        return workspace_candidate

    raise click.ClickException(f"Configuration file not found: {config_path}")


def _resolve_output_path(output_path: Path, workspace_root: Path) -> Path:
    if output_path.is_absolute():
        return output_path
    return (workspace_root / output_path).resolve()


def _display_path(path: Path, workspace_root: Path) -> str:
    resolved_path = path.resolve()
    try:
        return str(resolved_path.relative_to(workspace_root))
    except ValueError:
        return str(resolved_path)


def _find_workspace_root(start: Path) -> Path:
    resolved_start = start.resolve()
    for candidate in (resolved_start,):
        if (candidate / ".git").exists():
            return candidate
    for candidate in resolved_start.parents:
        if (candidate / ".git").exists():
            return candidate
    return resolved_start


def _configure_logging(debug: bool) -> None:
    import logging

    level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(format="%(message)s", level=level)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=False,
    )
