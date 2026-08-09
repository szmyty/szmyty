"""Command-line interface for profile_builder.

Exposes four subcommands:

    profile-builder validate            Validate public content and normalized data
    profile-builder render MODULE       Render one named module (or --all to render every enabled module)
    profile-builder check               Report whether rendering would change output
    profile-builder status              Explain module status and stale/fallback behavior
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from tools.profile_builder.models import EvidenceCatalog, EvidenceEntry, ProfileConfig
from tools.profile_builder.regions import RegionNotFoundError, update_readme_region, would_change
from tools.profile_builder.rendering import render_template

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent.parent
_DEFAULT_README = _REPO_ROOT / "README.md"
_DEFAULT_EVIDENCE = _REPO_ROOT / "profile" / "content" / "evidence.yml"
_DEFAULT_CONFIG = _REPO_ROOT / "profile" / "content" / "modules.yml"


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------


@click.group()
@click.version_option(version="0.1.0", prog_name="profile-builder")
def main() -> None:
    """profile-builder — minimal data-and-render pipeline for szmyty/szmyty."""


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


@main.command("validate")
@click.option(
    "--evidence",
    "evidence_path",
    type=click.Path(exists=True, path_type=Path),
    default=str(_DEFAULT_EVIDENCE),
    show_default=True,
    help="Path to the evidence YAML catalog.",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path),
    default=str(_DEFAULT_CONFIG),
    show_default=True,
    help="Path to the modules configuration YAML.",
)
def validate(evidence_path: Path, config_path: Path) -> None:
    """Validate public content and normalized module data.

    Exits with a non-zero status code when validation fails so the command
    can be used as a CI gate.
    """
    errors: list[str] = []

    # Evidence catalog
    try:
        raw = yaml.safe_load(evidence_path.read_text(encoding="utf-8")) or {}
        entries_raw = raw.get("entries", raw.get("evidence", []))
        catalog = EvidenceCatalog(
            entries=[EvidenceEntry.model_validate(e) for e in entries_raw]
        )
        click.echo(
            f"evidence: {len(catalog.entries)} entries — "
            f"{len(catalog.verified)} verified, {len(catalog.pending)} pending"
        )
    except Exception as exc:  # noqa: BLE001
        errors.append(f"evidence validation failed: {exc}")

    # Module config (optional file)
    if config_path.exists():
        try:
            raw_cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            cfg = ProfileConfig.model_validate(raw_cfg)
            click.echo(
                f"modules: {len(cfg.modules)} declared — "
                f"{len(cfg.enabled_modules)} enabled"
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"module config validation failed: {exc}")
    else:
        click.echo(f"modules: config not found at {config_path} (skipped)", err=True)

    if errors:
        for msg in errors:
            click.echo(f"ERROR: {msg}", err=True)
        sys.exit(1)
    click.echo("validate: OK")


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------


@main.command("render")
@click.argument("module", required=False, default=None)
@click.option("--all", "render_all", is_flag=True, default=False, help="Render all enabled modules.")
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=str(_DEFAULT_CONFIG),
    show_default=True,
    help="Path to the modules configuration YAML.",
)
@click.option(
    "--readme",
    "readme_path",
    type=click.Path(path_type=Path),
    default=str(_DEFAULT_README),
    show_default=True,
    help="Path to the README to update.",
)
@click.option(
    "--templates",
    "templates_dir",
    type=click.Path(path_type=Path),
    default=str(_REPO_ROOT / "profile" / "templates"),
    show_default=True,
    help="Directory containing Jinja2 templates.",
)
def render(
    module: Optional[str],
    render_all: bool,
    config_path: Path,
    readme_path: Path,
    templates_dir: Path,
) -> None:
    """Render one module or all enabled modules into README regions.

    MODULE is the name of the module to render.  Use --all to render every
    enabled module declared in the config.
    """
    if not module and not render_all:
        raise click.UsageError("Provide a MODULE name or pass --all.")
    if module and render_all:
        raise click.UsageError("Pass either a MODULE name or --all, not both.")

    if not config_path.exists():
        click.echo(f"ERROR: config not found: {config_path}", err=True)
        sys.exit(1)

    raw_cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    cfg = ProfileConfig.model_validate(raw_cfg)

    targets = cfg.enabled_modules if render_all else [
        m for m in cfg.enabled_modules if m.name == module
    ]

    if not targets:
        if render_all:
            click.echo("No enabled modules declared; nothing to render.")
            return
        names = [m.name for m in cfg.enabled_modules]
        click.echo(
            f"ERROR: module {module!r} not found or not enabled. "
            f"Available: {names}",
            err=True,
        )
        sys.exit(1)

    for mod in targets:
        try:
            content = render_template(
                mod.template,
                {"module": mod},
                templates_dir=templates_dir,
            )
            changed = update_readme_region(
                readme_path, mod.region_start_marker, mod.region_end_marker, content
            )
            status = "updated" if changed else "unchanged"
            click.echo(f"render: {mod.name} — {status}")
        except RegionNotFoundError as exc:
            click.echo(f"ERROR [{mod.name}]: {exc}", err=True)
            sys.exit(1)
        except Exception as exc:  # noqa: BLE001
            click.echo(f"ERROR [{mod.name}]: {exc}", err=True)
            sys.exit(1)


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------


@main.command("check")
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=str(_DEFAULT_CONFIG),
    show_default=True,
    help="Path to the modules configuration YAML.",
)
@click.option(
    "--readme",
    "readme_path",
    type=click.Path(path_type=Path),
    default=str(_DEFAULT_README),
    show_default=True,
    help="Path to the README to check.",
)
@click.option(
    "--templates",
    "templates_dir",
    type=click.Path(path_type=Path),
    default=str(_REPO_ROOT / "profile" / "templates"),
    show_default=True,
    help="Directory containing Jinja2 templates.",
)
def check(config_path: Path, readme_path: Path, templates_dir: Path) -> None:
    """Report whether rendering would change tracked output.

    Exits with status 1 when one or more modules would produce new output,
    making this usable as a CI staleness gate.
    """
    if not config_path.exists():
        click.echo(f"ERROR: config not found: {config_path}", err=True)
        sys.exit(1)

    raw_cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    cfg = ProfileConfig.model_validate(raw_cfg)

    stale: list[str] = []
    for mod in cfg.enabled_modules:
        try:
            content = render_template(
                mod.template,
                {"module": mod},
                templates_dir=templates_dir,
            )
            if would_change(readme_path, mod.region_start_marker, mod.region_end_marker, content):
                stale.append(mod.name)
                click.echo(f"stale: {mod.name}")
            else:
                click.echo(f"current: {mod.name}")
        except RegionNotFoundError as exc:
            click.echo(f"ERROR [{mod.name}]: {exc}", err=True)
            sys.exit(1)
        except Exception as exc:  # noqa: BLE001
            click.echo(f"ERROR [{mod.name}]: {exc}", err=True)
            sys.exit(1)

    if stale:
        click.echo(
            f"\ncheck: {len(stale)} module(s) would change — run `render --all` to update.",
            err=True,
        )
        sys.exit(1)
    click.echo("check: all modules current")


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


@main.command("status")
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path),
    default=str(_DEFAULT_CONFIG),
    show_default=True,
    help="Path to the modules configuration YAML.",
)
def status(config_path: Path) -> None:
    """Explain module status and stale/fallback behavior.

    Prints a human-readable table of all declared modules with their enabled
    state, region markers, template, and artifact path.
    """
    if not config_path.exists():
        click.echo(f"No module config found at {config_path}.")
        click.echo("Create profile/content/modules.yml to declare modules.")
        return

    raw_cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    cfg = ProfileConfig.model_validate(raw_cfg)

    if not cfg.modules:
        click.echo("No modules declared.")
        return

    click.echo(f"{'NAME':<20} {'ENABLED':<8} {'TEMPLATE':<30} {'ARTIFACT'}")
    click.echo("-" * 80)
    for mod in cfg.modules:
        artifact = str(mod.artifact_path) if mod.artifact_path else "—"
        state = "yes" if mod.enabled else "no"
        click.echo(f"{mod.name:<20} {state:<8} {mod.template:<30} {artifact}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
