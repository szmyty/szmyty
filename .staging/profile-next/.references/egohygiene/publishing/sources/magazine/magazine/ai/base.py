"""Abstract base class for AI generation stages (Strategy Pattern)."""

from abc import ABC, abstractmethod
from pathlib import Path


class AIStage(ABC):
    """Abstract AI generation stage.

    Concrete implementations follow the Strategy Pattern so new AI stages can
    be added without touching core orchestration code.
    """

    @abstractmethod
    def ensure_model(self) -> None:
        """Ensure the AI model is available, bootstrapping it if necessary."""

    @abstractmethod
    def should_regenerate(self, page_dir: Path) -> bool:
        """Return True if the stage output needs to be (re-)generated."""

    @abstractmethod
    def generate(self, page_dir: Path) -> None:
        """Run the generation step for the given page directory."""

    def generate_or_skip(self, page_dir: Path) -> None:
        """Run generation only when the stage output needs to be (re-)generated.

        Template method: delegates to :meth:`should_regenerate` and
        :meth:`generate`.  Concrete stages should not override this method.
        """
        if self.should_regenerate(page_dir):
            self.generate(page_dir)
