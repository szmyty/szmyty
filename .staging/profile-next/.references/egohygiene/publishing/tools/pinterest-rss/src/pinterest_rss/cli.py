"""Click CLI for the Pinterest RSS ingestion tool."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import click
import structlog
import yaml
from rich.console import Console
from rich.table import Table

from pinterest_rss.downloader import download_image
from pinterest_rss.feed import fetch_feed
from pinterest_rss.manifest import (
    classify_item,
    load_manifest,
    save_manifest,
    update_manifest,
)
from pinterest_rss.models import FeedConfig, Manifest, SyncConfig
from pinterest_rss.normalizer import generate_slug, normalize_entry, pin_directory_name

log = structlog.get_logger(__name__)
console = Console()


@click.group()
@click.option("--debug", is_flag=True, help="Enable structured debug logging.")
def main(debug: bool) -> None:
    """Pinterest RSS ingestion tool for Ego Hygiene."""
    _configure_logging(debug)


@main.command()
@click.option(
    "--config",
    "config_path",
    default="publishing/pinterest/config.yaml",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the YAML configuration file.",
)
@click.option("--dry-run", is_flag=True, help="Report what would change without writing.")
@click.option(
    "--download-images/--no-download-images",
    default=True,
    show_default=True,
    help="Download associated images.",
)
def sync(config_path: Path, dry_run: bool, download_images: bool) -> None:
    """Synchronize Pinterest RSS feeds into the repository."""
    download_images = _env_bool("PINTEREST_DOWNLOAD_IMAGES", download_images)
    config, workspace_root, _ = _load_config(config_path)

    totals: dict[str, int] = {
        "feeds": 0,
        "new": 0,
        "updated": 0,
        "unchanged": 0,
        "failed": 0,
    }

    for feed_cfg in config.feeds:
        _apply_env_overrides(feed_cfg)
        output_dir = _resolve_output_path(Path(feed_cfg.output), workspace_root)
        _sync_feed(feed_cfg, output_dir, workspace_root, dry_run, download_images, totals)

    _print_summary(totals, dry_run)

    if totals["failed"] > 0:
        sys.exit(1)


@main.command()
@click.option(
    "--config",
    "config_path",
    default="publishing/pinterest/config.yaml",
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
    default="publishing/pinterest/config.yaml",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the YAML configuration file.",
)
def inspect(config_path: Path) -> None:
    """Print the current manifest state for all configured feeds."""
    config, workspace_root, _ = _load_config(config_path)
    for feed_cfg in config.feeds:
        output_dir = _resolve_output_path(Path(feed_cfg.output), workspace_root)
        manifest = load_manifest(output_dir, feed_cfg.url, feed_cfg.id)
        table = Table(title=f"Board: {feed_cfg.id}", show_lines=True)
        table.add_column("Stable ID", style="cyan", no_wrap=True)
        table.add_column("Directory", style="green", no_wrap=True)
        table.add_column("Source URL")
        table.add_column("Content Hash", style="dim")
        table.add_column("First Seen")
        table.add_column("Last Updated")
        for entry in manifest.items.values():
            table.add_row(
                entry.stable_id[:40],
                entry.directory or entry.slug or "(none)",
                entry.source_url[:60],
                entry.content_hash[:12] + "…",
                entry.first_seen.strftime("%Y-%m-%d"),
                entry.last_updated.strftime("%Y-%m-%d"),
            )
        console.print(table)
        console.print(
            f"Total: [bold]{len(manifest.items)}[/bold] items | "
            f"Last sync: {manifest.last_sync or 'never'}"
        )


@main.command()
@click.option(
    "--config",
    "config_path",
    default="publishing/pinterest/config.yaml",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the YAML configuration file.",
)
@click.option("--dry-run", is_flag=True, help="Report what would change without writing.")
def migrate(config_path: Path, dry_run: bool) -> None:
    """Migrate existing archive folders to human-readable slug-based names.

    Inspects every item in each board manifest that does not yet have a slug,
    computes a deterministic slug from its title or description, renames the
    item directory, and updates the manifest.  Idempotent – already-migrated
    items are skipped.
    """
    config, workspace_root, _ = _load_config(config_path)

    for feed_cfg in config.feeds:
        output_dir = _resolve_output_path(Path(feed_cfg.output), workspace_root)
        _migrate_feed(feed_cfg, output_dir, workspace_root, dry_run)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _sync_feed(
    feed_cfg: FeedConfig,
    output_dir: Path,
    workspace_root: Path,
    dry_run: bool,
    download_images: bool,
    totals: dict[str, int],
) -> None:
    totals["feeds"] += 1
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold]📌 Syncing feed:[/bold] {feed_cfg.id}")
    console.print(f"   URL: {feed_cfg.url}")

    all_urls = [feed_cfg.url] + list(feed_cfg.additional_urls)
    raw_entries: list[dict] = []
    seen_in_fetch: set[str] = set()

    for url in all_urls:
        is_primary = url == feed_cfg.url
        try:
            entries = fetch_feed(url)
        except Exception as exc:
            if is_primary:
                console.print(f"[red]✗ Failed to fetch feed {feed_cfg.id}: {exc}[/red]")
                totals["failed"] += 1
                return
            else:
                console.print(f"[yellow]⚠ Could not fetch additional URL {url}: {exc}[/yellow]")
                log.warning("sync.additional_url_failed", url=url, exc=str(exc))
                continue

        for entry in entries:
            dedup_key = entry.get("id") or entry.get("link") or ""
            if dedup_key and dedup_key in seen_in_fetch:
                log.debug("sync.dedup_skip", key=dedup_key, url=url)
                continue
            if dedup_key:
                seen_in_fetch.add(dedup_key)
            raw_entries.append(entry)

    if len(all_urls) > 1:
        console.print(
            f"   Additional URLs: {len(feed_cfg.additional_urls)}"
            f" | Total entries: {len(raw_entries)}"
        )

    manifest = load_manifest(output_dir, feed_cfg.url, feed_cfg.id)

    # Build a registry of directory names already in use so collision handling is
    # consistent across unchanged items (already in manifest) and newly processed items.
    directory_registry = _build_directory_registry(manifest, output_dir)
    changed = False

    for raw in raw_entries:
        item = normalize_entry(raw, feed_cfg.id)
        if item is None:
            totals["failed"] += 1
            continue

        status, existing = classify_item(item, manifest)

        if status == "unchanged":
            totals["unchanged"] += 1
            log.debug("sync.unchanged", stable_id=item.stable_id)
            continue

        # Determine the archive directory name (reuse existing one when updating).
        item.directory = _assign_directory(item, existing, directory_registry)
        # Keep the human-readable slug for backward compat.
        if existing and existing.slug:
            item.slug = existing.slug
        else:
            item.slug = generate_slug(item.title, item.description, item.stable_id)
        item_dir = output_dir / "items" / item.directory
        log.debug("sync.item", stable_id=item.stable_id, directory=item.directory, status=status)

        if not dry_run:
            item_dir.mkdir(parents=True, exist_ok=True)

            # Download image
            if download_images and item.image_url:
                image_path = download_image(item.image_url, item_dir)
                if image_path:
                    item.local_paths["image"] = _display_path(image_path, workspace_root)
                else:
                    totals["failed"] += 1
                    console.print(
                        f"[yellow]⚠ Image download failed for {item.stable_id}[/yellow]"
                    )

            # Preserve first_seen from existing entry
            if existing:
                item.first_seen = existing.first_seen  # type: ignore[misc]

            _write_item_files(item, item_dir)
            update_manifest(manifest, item, status, existing)
            changed = True

        if status == "new":
            totals["new"] += 1
            console.print(f"  [green]+[/green] new: {item.directory}")
        else:
            totals["updated"] += 1
            console.print(f"  [yellow]~[/yellow] updated: {item.directory}")

    if not dry_run and changed:
        manifest.last_sync = datetime.now(UTC)
        save_manifest(manifest, output_dir)


def _build_directory_registry(manifest: Manifest, output_dir: Path) -> dict[str, str]:
    """Return a mapping of *directory → stable_id* for all items currently in the manifest.

    Items that were synced before directory support was added have their
    directories computed from metadata.json on disk so that new items don't
    collide with them before a ``migrate`` run.
    """
    registry: dict[str, str] = {}
    for stable_id, entry in manifest.items.items():
        if entry.directory:
            registry[entry.directory] = stable_id
        elif entry.slug:
            registry[entry.slug] = stable_id
        else:
            provisional = _provisional_directory(stable_id, output_dir)
            if provisional:
                registry[provisional] = stable_id
    return registry


def _provisional_directory(stable_id: str, output_dir: Path) -> str:
    """Compute the directory an item *would* receive after migration, without migrating.

    Returns a ``pin-<id>`` name when the pin ID can be recovered, otherwise
    falls back to a title slug derived from metadata.json.
    """
    from pinterest_rss.normalizer import extract_pin_id

    meta_path = output_dir / "items" / stable_id / "metadata.json"
    if meta_path.exists():
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            # Try to recover pin ID from stored guid or URL fields
            for field in ("guid", "canonical_url", "source_url"):
                pin_id = extract_pin_id(data.get(field, "") or "")
                if pin_id:
                    return pin_directory_name(pin_id)
            # Fall back to slug from title
            title = data.get("title", "")
            description = data.get("description", "")
            return generate_slug(title, description, stable_id)
        except Exception:
            pass
    return generate_slug("", "", stable_id)


def _assign_directory(
    item: Any,
    existing: Any,
    directory_registry: dict[str, str],
) -> str:
    """Return the archive directory name to use for *item*.

    For Pinterest items with a known pin ID, always use ``pin-<id>`` (stable
    and deterministic).  For other items, fall back to a collision-handled slug.
    Existing directory names are preserved for updated items.
    """

    # Reuse existing directory for updated items.
    if existing and existing.directory:
        return existing.directory
    if existing and existing.slug:
        # Upgrade legacy slug-only items to pin-<id> if pin_id is available.
        if item.pin_id:
            directory = pin_directory_name(item.pin_id)
            directory_registry[directory] = item.stable_id
            return directory
        return existing.slug

    # New item: use pin-based name when available (no collision possible – pin IDs unique).
    if item.pin_id:
        directory = pin_directory_name(item.pin_id)
        directory_registry[directory] = item.stable_id
        return directory

    # Non-Pinterest item: generate a collision-handled slug.
    base = generate_slug(item.title, item.description, item.stable_id)
    directory = base
    counter = 2
    while directory in directory_registry and directory_registry[directory] != item.stable_id:
        directory = f"{base}-{counter}"
        counter += 1

    directory_registry[directory] = item.stable_id
    return directory


def _migrate_feed(
    feed_cfg: FeedConfig,
    output_dir: Path,
    workspace_root: Path,
    dry_run: bool,
) -> None:
    """Migrate one board feed to ``pin-<id>`` archive directories.

    Handles archives in any of these three states:

    1. Legacy stable-ID directories  (``www-pinterest-com-pin-123-``)
    2. Title-slug directories         (``morning-ritual-pin``)
    3. Already migrated               (``pin-123456789``)

    The pin ID is recovered from ``metadata.json`` via the ``guid``,
    ``canonical_url``, or ``source_url`` fields.  Items that cannot produce a
    pin ID are migrated to a title-slug as before (backward-compatible fallback).
    """
    from pinterest_rss.normalizer import extract_pin_id

    console.print(f"\n[bold]🔄 Migrating feed:[/bold] {feed_cfg.id}")

    manifest = load_manifest(output_dir, feed_cfg.url, feed_cfg.id)
    if not manifest.items:
        console.print("   No items in manifest – nothing to migrate.")
        return

    # Build a registry of already-assigned target directories for collision safety.
    target_registry: dict[str, str] = {}
    for entry in manifest.items.values():
        if entry.directory:
            target_registry[entry.directory] = entry.stable_id
        elif entry.slug and entry.slug.startswith("pin-"):
            target_registry[entry.slug] = entry.stable_id

    migrated = 0
    skipped = 0

    for stable_id, entry in list(manifest.items.items()):
        # Skip already-migrated items (directory is set and uses pin-<id> format).
        if entry.directory and entry.directory.startswith("pin-"):
            log.debug("migrate.already_done", stable_id=stable_id, directory=entry.directory)
            skipped += 1
            continue

        # Determine the current on-disk directory name.
        current_dir_name = entry.directory or entry.slug or stable_id
        old_dir = output_dir / "items" / current_dir_name

        # Recover pin ID from metadata.json.
        target_directory = _recover_pin_directory(
            stable_id, current_dir_name, output_dir, extract_pin_id
        )

        if target_directory is None:
            # No pin ID available – fall back to slug migration (pre-existing behavior).
            target_directory = _provisional_directory(stable_id, output_dir)

        # Handle collisions.
        base_target = target_directory
        counter = 2
        while (
            target_directory in target_registry
            and target_registry[target_directory] != stable_id
        ):
            target_directory = f"{base_target}-{counter}"
            counter += 1
        target_registry[target_directory] = stable_id

        new_dir = output_dir / "items" / target_directory

        if dry_run:
            console.print(f"  [dim](dry-run)[/dim] {current_dir_name} → {target_directory}")
        else:
            if old_dir.exists() and not new_dir.exists():
                old_dir.rename(new_dir)
                log.debug("migrate.renamed", old=str(old_dir), new=str(new_dir))
            elif not old_dir.exists() and new_dir.exists():
                log.debug("migrate.already_renamed", target=target_directory)
            elif not old_dir.exists() and not new_dir.exists():
                log.debug("migrate.no_dir", stable_id=stable_id, target=target_directory)
            # else: both exist – keep as-is to avoid data loss

            # Update local_paths to reflect the new directory name.
            old_infix = f"items/{current_dir_name}/"
            new_infix = f"items/{target_directory}/"
            updated_paths = {
                k: v.replace(old_infix, new_infix, 1)
                for k, v in entry.local_paths.items()
            }
            entry.local_paths = updated_paths
            entry.directory = target_directory
            # Keep slug for backward compat unless we're upgrading a pin.
            if not entry.slug or entry.slug == stable_id:
                entry.slug = target_directory
            manifest.items[stable_id] = entry
            console.print(f"  [green]→[/green] {current_dir_name} → {target_directory}")

        migrated += 1

    if not dry_run and migrated > 0:
        save_manifest(manifest, output_dir)

    mode = " [dim](dry-run)[/dim]" if dry_run else ""
    console.print(
        f"\n  Migrated: [green]{migrated}[/green]{mode}  "
        f"Already done: {skipped}"
    )


def _recover_pin_directory(
    stable_id: str,
    current_dir_name: str,
    output_dir: Path,
    extract_pin_id: Any,
) -> str | None:
    """Attempt to recover a ``pin-<id>`` directory name from stored metadata.

    Tries, in order:
    1. Parse the pin ID directly from *stable_id* (for legacy URL-slug stable IDs).
    2. Read ``metadata.json`` and extract from ``guid``, ``canonical_url``, ``source_url``.

    Returns ``None`` when no pin ID can be recovered.
    """
    # Try extracting pin ID from the stable_id itself (e.g. "www-pinterest-com-pin-123-")
    pin_id = extract_pin_id(stable_id.replace("-", "/"))
    if not pin_id:
        # Also try treating hyphens as separators and look for trailing digit sequences
        import re as _re
        m = _re.search(r'pin[-/](\d{10,})', stable_id)
        if m:
            pin_id = m.group(1)

    if pin_id:
        return pin_directory_name(pin_id)

    # Read metadata.json
    meta_path = output_dir / "items" / current_dir_name / "metadata.json"
    if not meta_path.exists():
        # Also try the stable_id directory in case the current dir name differs
        meta_path = output_dir / "items" / stable_id / "metadata.json"

    if meta_path.exists():
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            for field in ("guid", "canonical_url", "source_url"):
                pid = extract_pin_id(data.get(field, "") or "")
                if pid:
                    return pin_directory_name(pid)
        except Exception:
            pass

    return None


def _write_item_files(item: Any, item_dir: Path) -> None:
    """Write metadata.json and description.md for an item."""
    meta_path = item_dir / "metadata.json"
    meta_path.write_text(
        json.dumps(item.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    desc_path = item_dir / "description.md"
    desc_path.write_text(
        f"# {item.title}\n\n{item.description}\n",
        encoding="utf-8",
    )


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
    url_override = os.environ.get("PINTEREST_RSS_URL")
    if url_override:
        feed_cfg.url = url_override
    output_override = os.environ.get("PINTEREST_OUTPUT_DIRECTORY")
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
    console.print(f"  Feeds processed : {totals['feeds']}")
    console.print(f"  New items       : [green]{totals['new']}[/green]")
    console.print(f"  Updated items   : [yellow]{totals['updated']}[/yellow]")
    console.print(f"  Unchanged items : {totals['unchanged']}")
    console.print(f"  Failed          : [red]{totals['failed']}[/red]")


def _resolve_config_path(config_path: Path) -> Path:
    """Resolve a config path from the current directory or the workspace root."""
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
    """Resolve a feed output path against the workspace root when needed."""
    if output_path.is_absolute():
        return output_path
    return (workspace_root / output_path).resolve()


def _display_path(path: Path, workspace_root: Path) -> str:
    """Render a path relative to the workspace root when possible."""
    resolved_path = path.resolve()
    try:
        return str(resolved_path.relative_to(workspace_root))
    except ValueError:
        return str(resolved_path)


def _find_workspace_root(start: Path) -> Path:
    """Search upward for the repository root and fall back to the current directory."""
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
