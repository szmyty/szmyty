"""Render enabled profile modules into their owned README regions."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import click
import yaml

from tools.profile_builder.models import ModuleRegistry
from tools.profile_builder.regions import update_readme_region
from tools.profile_builder.rendering import render_template

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "profile" / "content" / "modules-registry.yml"
DEFAULT_README = REPO_ROOT / "README.md"
DEFAULT_TEMPLATES = REPO_ROOT / "profile" / "templates"


def _load_data(path: Path) -> Any:
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix in {".yml", ".yaml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise ValueError(f"Unsupported artifact format: {path.suffix}")


def _context_for_module(provider_module: str, artifact_path: Path) -> dict[str, Any]:
    module = importlib.import_module(provider_module)
    loader = getattr(module, "load_template_context", None)
    if loader is None:
        raise ValueError(
            f"Provider module {provider_module!r} does not expose "
            "load_template_context()."
        )
    context = loader(artifact_path)
    if not isinstance(context, dict):
        raise ValueError(
            f"Provider module {provider_module!r} returned a non-mapping "
            "template context."
        )
    return context


def render_modules(
    config_path: Path = DEFAULT_CONFIG,
    readme_path: Path = DEFAULT_README,
    templates_dir: Path = DEFAULT_TEMPLATES,
) -> list[tuple[str, str]]:
    """Render all enabled modules and return ``(name, status)`` tuples."""
    raw_cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    config = ModuleRegistry.model_validate(raw_cfg)
    results: list[tuple[str, str]] = []
    for module in config.enabled_modules:
        artifact_path = REPO_ROOT / module.artifact_dir / module.artifact_file
        context = _context_for_module(module.provider_module, artifact_path)
        content = render_template(
            module.template,
            context,
            templates_dir=templates_dir,
        ).rstrip()
        changed = update_readme_region(
            readme_path,
            module.region_start_marker,
            module.region_end_marker,
            content,
        )
        results.append((module.name, "updated" if changed else "unchanged"))
    return results


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=str(DEFAULT_CONFIG),
    show_default=True,
)
@click.option(
    "--readme",
    "readme_path",
    type=click.Path(exists=True, path_type=Path),
    default=str(DEFAULT_README),
    show_default=True,
)
@click.option(
    "--templates",
    "templates_dir",
    type=click.Path(exists=True, path_type=Path),
    default=str(DEFAULT_TEMPLATES),
    show_default=True,
)
def main(config_path: Path, readme_path: Path, templates_dir: Path) -> None:
    """Update README module regions from declared artifacts."""
    for name, status in render_modules(
        config_path=config_path,
        readme_path=readme_path,
        templates_dir=templates_dir,
    ):
        click.echo(f"update-readme: {name} {status}")


if __name__ == "__main__":
    main()
