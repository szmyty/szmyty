"""Page build pipeline orchestration."""

import shutil
from pathlib import Path

from magazine.ai.base import AIStage
from magazine.ai.fountain import FountainAIStage
from magazine.config import Config
from magazine.pipeline import STAGE_REGISTRY, BuildContext
from magazine.utils import log_info, log_success


def build_page(
    page_dir: Path,
    *,
    ai_stage: AIStage | None = None,
    force: bool = False,
    skip_existing: bool = False,
    edition_name: str = "",
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
    """Run the full build pipeline for a single page directory.

    Pipeline order is determined by :data:`magazine.pipeline.STAGE_REGISTRY`.
    Default order:
        1. MetadataStage
        2. ImageStage
        3. FountainStage (AI generation)
        4. ScreenplayStage
        5. LatexStage    (unless latex_disable=True)
        6. SizesStage    (unless sizes_disable=True)
    """
    if config is None:
        config = Config()
    page_dir = page_dir.resolve()
    artifacts = page_dir / "artifacts"

    if force:
        shutil.rmtree(artifacts, ignore_errors=True)

    artifacts.mkdir(parents=True, exist_ok=True)

    if ai_stage is None:
        ai_stage = FountainAIStage(config=config)

    log_info(f"Building page: {page_dir.name}")

    ctx = BuildContext(
        page_dir=page_dir,
        artifacts=artifacts,
        config=config,
        ai_stage=ai_stage,
        force=force,
        skip_existing=skip_existing,
        edition_name=edition_name,
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
    )

    for stage_cls in STAGE_REGISTRY:
        stage = stage_cls()
        if stage.should_run(ctx):
            stage.run(ctx)

    log_success(f"Page build complete: {page_dir.name}")
