"""Validate and persist manual music highlight metadata for the profile README."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click
import yaml

from tools.profile_builder.models import MusicHighlight

MODULE_NAME = 'music-highlight'
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / 'profile' / 'content' / 'music-highlight.yml'
DEFAULT_FIXTURE = REPO_ROOT / 'profile' / 'fixtures' / 'music-highlight.yml'
DEFAULT_OUTPUT = REPO_ROOT / 'profile' / 'artifacts' / MODULE_NAME / 'music.yml'


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding='utf-8',
    )


def load_music(path: Path) -> MusicHighlight:
    """Load and validate a manual or fixture music highlight file."""
    raw = yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(raw, dict):
        raise ValueError('Music highlight file must contain a mapping.')
    return MusicHighlight.model_validate(raw)


def load_cached_music(path: Path) -> MusicHighlight | None:
    """Load the previous artifact as a fallback cache."""
    if not path.exists():
        return None
    music = load_music(path)
    return music.model_copy(update={'data_source': 'cache'})


def build_music_highlight(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    fixture_path: Path = DEFAULT_FIXTURE,
) -> MusicHighlight:
    """Build the music highlight artifact from manual data with fallback."""
    try:
        music = load_music(input_path)
    except Exception as exc:  # noqa: BLE001
        cached = load_cached_music(output_path)
        if cached is not None:
            music = cached
        else:
            try:
                music = load_music(fixture_path).model_copy(update={'data_source': 'fixture'})
            except Exception as fixture_exc:  # noqa: BLE001
                raise ValueError(f'No usable music highlight data: {exc}; fixture failed: {fixture_exc}') from fixture_exc
    _write_yaml(output_path, music.model_dump(mode='json'))
    return music


@click.command()
@click.option('--input', 'input_path', type=click.Path(exists=True, path_type=Path), default=str(DEFAULT_INPUT), show_default=True)
@click.option('--output', 'output_path', type=click.Path(path_type=Path), default=str(DEFAULT_OUTPUT), show_default=True)
@click.option('--fixture', 'fixture_path', type=click.Path(exists=True, path_type=Path), default=str(DEFAULT_FIXTURE), show_default=True)
def main(input_path: Path, output_path: Path, fixture_path: Path) -> None:
    """Write validated music highlight metadata to *output_path*."""
    music = build_music_highlight(input_path=input_path, output_path=output_path, fixture_path=fixture_path)
    click.echo(f'music-highlight: wrote {output_path} ({music.data_source})')


if __name__ == '__main__':
    main()
