"""Tests for VideoAIStage stub (magazine.ai.video)."""

from pathlib import Path

from magazine.ai.video import VideoAIStage


class TestVideoAIStage:
    def test_should_regenerate_always_false(self, tmp_path: Path) -> None:
        assert VideoAIStage().should_regenerate(tmp_path) is False

    def test_should_regenerate_with_image(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"fake image")
        assert VideoAIStage().should_regenerate(tmp_path) is False

    def test_generate_does_not_raise(self, tmp_path: Path) -> None:
        VideoAIStage().generate(tmp_path)  # should not raise

    def test_generate_does_not_write_files(self, tmp_path: Path) -> None:
        VideoAIStage().generate(tmp_path)
        assert list(tmp_path.iterdir()) == []

    def test_ensure_model_does_not_raise(self) -> None:
        VideoAIStage().ensure_model()  # should not raise

    def test_is_ai_stage_subclass(self) -> None:
        from magazine.ai.base import AIStage
        assert isinstance(VideoAIStage(), AIStage)

    def test_generate_with_existing_files_unaffected(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image data")
        (tmp_path / "page.fountain").write_text("existing fountain")
        VideoAIStage().generate(tmp_path)
        # Ensure no files were added or modified
        assert (tmp_path / "page.fountain").read_text() == "existing fountain"
