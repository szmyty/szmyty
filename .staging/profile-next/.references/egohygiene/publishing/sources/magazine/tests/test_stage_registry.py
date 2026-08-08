"""Tests for the stage registry and pipeline orchestration (magazine.pipeline)."""

from contextlib import ExitStack
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magazine.pipeline import (
    STAGE_REGISTRY,
    BuildContext,
    FountainStage,
    ImageStage,
    LatexStage,
    MetadataStage,
    PipelineStage,
    ScreenplayStage,
    SizesStage,
    register_stage,
)
from magazine.config import Config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_context(page_dir: Path, **overrides) -> BuildContext:
    """Return a minimal BuildContext for tests."""
    artifacts = page_dir / "artifacts"
    artifacts.mkdir(exist_ok=True)
    defaults = dict(
        page_dir=page_dir,
        artifacts=artifacts,
        config=Config(),
        ai_stage=MagicMock(),
    )
    defaults.update(overrides)
    return BuildContext(**defaults)


# ---------------------------------------------------------------------------
# Registry structure
# ---------------------------------------------------------------------------


class TestStageRegistry:
    """Tests for STAGE_REGISTRY contents and ordering."""

    def test_registry_contains_six_stages(self) -> None:
        assert len(STAGE_REGISTRY) == 6

    def test_registry_order_is_deterministic(self) -> None:
        names = [cls.name for cls in STAGE_REGISTRY]
        assert names == ["metadata", "images", "fountain", "screenplay", "latex", "sizes"]

    def test_registry_contains_expected_classes(self) -> None:
        assert STAGE_REGISTRY[0] is MetadataStage
        assert STAGE_REGISTRY[1] is ImageStage
        assert STAGE_REGISTRY[2] is FountainStage
        assert STAGE_REGISTRY[3] is ScreenplayStage
        assert STAGE_REGISTRY[4] is LatexStage
        assert STAGE_REGISTRY[5] is SizesStage

    def test_all_stages_are_pipeline_stage_subclasses(self) -> None:
        for stage_cls in STAGE_REGISTRY:
            assert issubclass(stage_cls, PipelineStage)

    def test_register_stage_appends_and_returns_class(self) -> None:
        """register_stage() appends to registry and returns the class (decorator support)."""
        original_len = len(STAGE_REGISTRY)

        class _TempStage(PipelineStage):
            name = "_temp"

            def should_run(self, ctx):
                return True

            def run(self, ctx):
                pass

        result = register_stage(_TempStage)
        try:
            assert result is _TempStage
            assert STAGE_REGISTRY[-1] is _TempStage
            assert len(STAGE_REGISTRY) == original_len + 1
        finally:
            # Clean up so we don't pollute other tests
            STAGE_REGISTRY.remove(_TempStage)


# ---------------------------------------------------------------------------
# Stage should_run() guards
# ---------------------------------------------------------------------------


class TestShouldRun:
    """Tests for stage guard conditions."""

    def test_metadata_always_runs(self, page_dir: Path) -> None:
        ctx = _make_context(page_dir)
        assert MetadataStage().should_run(ctx) is True

    def test_image_always_runs(self, page_dir: Path) -> None:
        ctx = _make_context(page_dir)
        assert ImageStage().should_run(ctx) is True

    def test_fountain_always_runs(self, page_dir: Path) -> None:
        ctx = _make_context(page_dir)
        assert FountainStage().should_run(ctx) is True

    def test_screenplay_always_runs(self, page_dir: Path) -> None:
        ctx = _make_context(page_dir)
        assert ScreenplayStage().should_run(ctx) is True

    def test_latex_runs_by_default(self, page_dir: Path) -> None:
        ctx = _make_context(page_dir, latex_disable=False)
        assert LatexStage().should_run(ctx) is True

    def test_latex_skipped_when_disabled(self, page_dir: Path) -> None:
        ctx = _make_context(page_dir, latex_disable=True)
        assert LatexStage().should_run(ctx) is False

    def test_sizes_runs_by_default(self, page_dir: Path) -> None:
        ctx = _make_context(page_dir, sizes_disable=False)
        assert SizesStage().should_run(ctx) is True

    def test_sizes_skipped_when_disabled(self, page_dir: Path) -> None:
        ctx = _make_context(page_dir, sizes_disable=True)
        assert SizesStage().should_run(ctx) is False


# ---------------------------------------------------------------------------
# Execution order and mock injection
# ---------------------------------------------------------------------------


class TestRegistryExecution:
    """Tests for execution order and mock stage injection via build_page()."""

    _PIPELINE_TARGETS = [
        ("magazine.pipeline.gen_page_meta", "metadata"),
        ("magazine.pipeline.generate_image_assets", "images"),
        ("magazine.pipeline.generate_screenplay_assets", "screenplay"),
        ("magazine.pipeline.generate_latex_page", "latex"),
        ("magazine.pipeline.generate_size_variants", "sizes"),
    ]

    def _run_with_mocks(self, page_dir: Path, **build_kwargs) -> list[str]:
        """Run build_page() with stage functions mocked; return execution order."""
        executed: list[str] = []
        with ExitStack() as stack:
            for target, label in self._PIPELINE_TARGETS:
                stack.enter_context(
                    patch(target, side_effect=lambda *a, lbl=label, **kw: executed.append(lbl))
                )
            mock_ai = MagicMock()
            mock_ai.generate_or_skip.side_effect = lambda *a, **kw: executed.append("fountain")
            build_kwargs.setdefault("ai_stage", mock_ai)
            from magazine.page import build_page
            build_page(page_dir, **build_kwargs)
        return executed

    def test_stages_execute_in_registry_order(self, page_dir: Path) -> None:
        executed = self._run_with_mocks(page_dir)
        assert executed == ["metadata", "images", "fountain", "screenplay", "latex", "sizes"]

    def test_latex_stage_skipped_when_disabled(self, page_dir: Path) -> None:
        executed = self._run_with_mocks(page_dir, latex_disable=True)
        assert "latex" not in executed
        assert executed == ["metadata", "images", "fountain", "screenplay", "sizes"]

    def test_sizes_stage_skipped_when_disabled(self, page_dir: Path) -> None:
        executed = self._run_with_mocks(page_dir, sizes_disable=True)
        assert "sizes" not in executed
        assert executed == ["metadata", "images", "fountain", "screenplay", "latex"]

    def test_both_stages_skipped_when_both_disabled(self, page_dir: Path) -> None:
        executed = self._run_with_mocks(page_dir, latex_disable=True, sizes_disable=True)
        assert executed == ["metadata", "images", "fountain", "screenplay"]

    def test_mock_stage_injection_works(self, page_dir: Path) -> None:
        """A custom mock stage can be injected via build_page(ai_stage=...)."""
        mock_ai = MagicMock()
        self._run_with_mocks(page_dir, ai_stage=mock_ai)
        mock_ai.generate_or_skip.assert_called_once_with(page_dir.resolve())
