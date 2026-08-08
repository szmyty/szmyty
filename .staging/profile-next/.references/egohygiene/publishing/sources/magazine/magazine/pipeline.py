"""Stage registry and pipeline orchestration for the page build pipeline.

This module provides:
- ``BuildContext``: immutable context object passed to every stage.
- ``PipelineStage``: abstract base class that all stages must implement.
- ``STAGE_REGISTRY``: ordered list of registered stage *classes*.
- ``register_stage()``: decorator / callable that appends a stage to the registry.

Built-in stages are registered at module import time in pipeline order:

    MetadataStage → ImageStage → FountainStage → ScreenplayStage
    → LatexStage → SizesStage

New stages can be appended via :func:`register_stage` without touching
``page.py`` or any existing stage.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from magazine.assets.images import generate_image_assets
from magazine.assets.latex import generate_latex_page
from magazine.assets.screenplay import generate_screenplay_assets
from magazine.assets.sizes import generate_size_variants
from magazine.config import Config
from magazine.metadata import gen_page_meta
from magazine.utils import log_warn


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------


@dataclass
class BuildContext:
    """All inputs required by the pipeline stages for a single page build."""

    page_dir: Path
    artifacts: Path
    config: Config
    ai_stage: Any = field(default=None)
    force: bool = False
    skip_existing: bool = False
    edition_name: str = ""
    reproducible: bool = False
    exif_disable: bool = False
    latex_disable: bool = False
    latex_force: bool = False
    latex_safe_mode: bool = False
    latex_engine: str | None = None
    sizes_disable: bool = False
    sizes_force: bool = False
    sizes: list[str] | None = None
    sizes_config: Path | None = None
    sizes_safe_mode: bool = False
    ai_fountain_disable: bool = False


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------


class PipelineStage(ABC):
    """Abstract base class for all pipeline stages.

    Each concrete stage must declare a human-readable ``name`` and implement
    :meth:`should_run` (guard) and :meth:`run` (execution).
    """

    name: str = ""

    @abstractmethod
    def should_run(self, ctx: BuildContext) -> bool:
        """Return ``True`` if this stage should execute given *ctx*."""

    @abstractmethod
    def run(self, ctx: BuildContext) -> None:
        """Execute the stage using the provided *ctx*."""


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

STAGE_REGISTRY: list[type[PipelineStage]] = []


def register_stage(stage_cls: type[PipelineStage]) -> type[PipelineStage]:
    """Register *stage_cls* in :data:`STAGE_REGISTRY`.

    Can be used as a plain call or as a class decorator::

        @register_stage
        class MyStage(PipelineStage):
            ...
    """
    STAGE_REGISTRY.append(stage_cls)
    return stage_cls


# ---------------------------------------------------------------------------
# Built-in stage implementations
# ---------------------------------------------------------------------------


@register_stage
class MetadataStage(PipelineStage):
    """Generate page metadata (stage 1)."""

    name = "metadata"

    def should_run(self, ctx: BuildContext) -> bool:
        return True

    def run(self, ctx: BuildContext) -> None:
        gen_page_meta(
            ctx.page_dir,
            reproducible=ctx.reproducible,
            exif_disable=ctx.exif_disable,
            config=ctx.config,
        )


@register_stage
class ImageStage(PipelineStage):
    """Generate image assets (stage 2)."""

    name = "images"

    def should_run(self, ctx: BuildContext) -> bool:
        return True

    def run(self, ctx: BuildContext) -> None:
        generate_image_assets(ctx.page_dir, ctx.artifacts, config=ctx.config)


@register_stage
class FountainStage(PipelineStage):
    """Run the AI fountain-screenplay generation stage (stage 3)."""

    name = "fountain"

    def should_run(self, ctx: BuildContext) -> bool:
        if ctx.ai_fountain_disable:
            log_warn("⚠️ AI Fountain generation disabled by flag")
            return False
        return True

    def run(self, ctx: BuildContext) -> None:
        ctx.ai_stage.generate_or_skip(ctx.page_dir)


@register_stage
class ScreenplayStage(PipelineStage):
    """Generate screenplay assets from the fountain file (stage 4)."""

    name = "screenplay"

    def should_run(self, ctx: BuildContext) -> bool:
        return True

    def run(self, ctx: BuildContext) -> None:
        generate_screenplay_assets(ctx.page_dir, ctx.artifacts)


@register_stage
class LatexStage(PipelineStage):
    """Compile the LaTeX page document (stage 5)."""

    name = "latex"

    def should_run(self, ctx: BuildContext) -> bool:
        return not ctx.latex_disable

    def run(self, ctx: BuildContext) -> None:
        generate_latex_page(
            ctx.page_dir,
            ctx.artifacts,
            safe_mode=ctx.latex_safe_mode,
            engine=ctx.latex_engine,
            force=ctx.latex_force,
            config=ctx.config,
        )


@register_stage
class SizesStage(PipelineStage):
    """Generate comic trim-size variants (stage 6)."""

    name = "sizes"

    def should_run(self, ctx: BuildContext) -> bool:
        return not ctx.sizes_disable

    def run(self, ctx: BuildContext) -> None:
        generate_size_variants(
            ctx.page_dir,
            ctx.artifacts,
            sizes=ctx.sizes,
            config_path=ctx.sizes_config,
            force=ctx.sizes_force,
            safe_mode=ctx.sizes_safe_mode,
            config=ctx.config,
        )
