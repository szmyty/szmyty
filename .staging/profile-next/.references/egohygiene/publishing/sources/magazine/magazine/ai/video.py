"""Video AI generation stage (stub — reserved for future implementation)."""

from pathlib import Path

from magazine.ai.base import AIStage
from magazine.utils import log_warn


class VideoAIStage(AIStage):
    """Stub video generation stage — placeholder for future implementation.

    .. note::
        This class is **intentionally not registered** in ``STAGE_REGISTRY``
        and is therefore unreachable from the standard page-build pipeline.
        It exists solely as a typed placeholder so that a concrete video
        generation stage can be wired in later without touching core
        orchestration code.  All methods are no-ops until an implementation
        is provided.
    """

    def ensure_model(self) -> None:
        log_warn("VideoAIStage.ensure_model: not yet implemented (stub).")

    def should_regenerate(self, page_dir: Path) -> bool:  # noqa: ARG002
        return False

    def generate(self, page_dir: Path) -> None:  # noqa: ARG002
        log_warn("VideoAIStage.generate: not yet implemented (stub).")
