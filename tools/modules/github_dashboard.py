"""Thin CLI entrypoint for the GitHub engineering dashboard module."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import click

from tools.profile_builder.github_dashboard.models import GitHubDashboardSnapshot
from tools.profile_builder.github_dashboard.service import (
    DEFAULT_FIXTURE,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_USERNAME,
    MODULE_NAME,
    build_dashboard,
    load_snapshot,
)


def load_template_context(artifact_path: Path) -> dict[str, Any]:
    """Load the README template context for a rendered dashboard artifact."""
    return {"dashboard": load_snapshot(artifact_path)}


@click.command()
@click.option(
    "--output-dir",
    "output_dir",
    type=click.Path(path_type=Path),
    default=str(DEFAULT_OUTPUT_DIR),
    show_default=True,
)
@click.option(
    "--fixture",
    "fixture_path",
    type=click.Path(exists=True, path_type=Path),
    default=str(DEFAULT_FIXTURE),
    show_default=True,
)
@click.option(
    "--username",
    type=str,
    default=DEFAULT_USERNAME,
    show_default=True,
)
def main(output_dir: Path, fixture_path: Path, username: str) -> None:
    """Build the dashboard snapshot and SVG variants in *output_dir*."""
    snapshot: GitHubDashboardSnapshot = build_dashboard(
        output_dir=output_dir,
        fixture_path=fixture_path,
        username=username,
        token=os.getenv("GITHUB_TOKEN"),
    )
    click.echo(
        f"{MODULE_NAME}: wrote {output_dir} "
        f"({snapshot.status.data_source}/{snapshot.status.source_state})"
    )


if __name__ == "__main__":
    main()
