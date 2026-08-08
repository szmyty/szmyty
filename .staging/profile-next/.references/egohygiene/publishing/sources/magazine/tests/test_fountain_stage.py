"""Tests for FountainAIStage (magazine.ai.fountain)."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from magazine.ai.fountain import FountainAIStage, _build_prompt
from magazine.config import Config
from magazine.exceptions import AIRuntimeError, ModelfileError
from magazine.hashing import hash_file

_VALID_FOUNTAIN = "Title: Test\n\nINT. TEST – DAY\n\nAn example scene.\n"


class TestFountainShouldRegenerate:
    def test_no_image_returns_false(self, tmp_path: Path) -> None:
        stage = FountainAIStage()
        assert stage.should_regenerate(tmp_path) is False

    def test_no_fountain_file_returns_true(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"fake image")
        stage = FountainAIStage()
        assert stage.should_regenerate(tmp_path) is True

    def test_matching_hash_returns_false(self, tmp_path: Path) -> None:
        img = tmp_path / "page.png"
        img.write_bytes(b"stable image")
        (tmp_path / "page.fountain").write_text("fountain content")
        (tmp_path / ".build_state.json").write_text(
            json.dumps({"image_hash": hash_file(img)})
        )
        assert FountainAIStage().should_regenerate(tmp_path) is False

    def test_changed_hash_returns_true(self, tmp_path: Path) -> None:
        img = tmp_path / "page.png"
        img.write_bytes(b"new image data")
        (tmp_path / "page.fountain").write_text("old fountain")
        (tmp_path / ".build_state.json").write_text(json.dumps({"image_hash": "old_hash_000"}))
        assert FountainAIStage().should_regenerate(tmp_path) is True

    def test_fountain_exists_no_build_state_returns_true(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"data")
        (tmp_path / "page.fountain").write_text("content")
        # no .build_state.json → cannot verify hash → must regenerate
        assert FountainAIStage().should_regenerate(tmp_path) is True

    def test_corrupted_build_state_returns_true(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"data")
        (tmp_path / "page.fountain").write_text("content")
        (tmp_path / ".build_state.json").write_text("NOT JSON {{{")
        assert FountainAIStage().should_regenerate(tmp_path) is True

    def test_build_state_missing_image_hash_key_returns_true(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"data")
        (tmp_path / "page.fountain").write_text("content")
        (tmp_path / ".build_state.json").write_text(json.dumps({"other_key": "value"}))
        assert FountainAIStage().should_regenerate(tmp_path) is True


class TestFountainEnsureModel:
    def test_default_modelfile_path_resolves_within_package(self) -> None:
        cfg = Config()
        modelfile = Path(cfg.FOUNTAIN_MODELFILE_PATH)
        assert modelfile.is_absolute(), "Default FOUNTAIN_MODELFILE_PATH must be absolute"
        assert modelfile.exists(), (
            f"Default Modelfile must exist at {modelfile}; "
            "ensure magazine/ai/fountain.modelfile is included in package data"
        )

    def test_raises_ai_runtime_error_when_runtime_missing(self, tmp_path: Path) -> None:
        stage = FountainAIStage()
        with patch("magazine.ai.fountain.shutil.which", return_value=None):
            with pytest.raises(AIRuntimeError, match="not found"):
                stage.ensure_model()

    def test_passes_when_model_show_succeeds(self) -> None:
        stage = FountainAIStage()
        with patch("magazine.ai.fountain.shutil.which", return_value="/usr/local/bin/ollama"):
            with patch("magazine.ai.fountain.run") as mock_run:
                stage.ensure_model()
        # run("ollama", "show", ...) was called once
        assert mock_run.call_count == 1

    def test_creates_model_when_show_fails(self, tmp_path: Path) -> None:
        modelfile = tmp_path / "Modelfile"
        modelfile.write_text("FROM llama3")
        from magazine.config import Config
        cfg = Config()
        cfg.FOUNTAIN_AI_RUNTIME = "ollama"
        cfg.FOUNTAIN_AI_MODEL = "test-model:latest"
        cfg.FOUNTAIN_MODELFILE_PATH = str(modelfile)
        stage = FountainAIStage(config=cfg)
        with patch("magazine.ai.fountain.shutil.which", return_value="/usr/local/bin/ollama"):
            with patch("magazine.ai.fountain.run") as mock_run:
                mock_run.side_effect = [Exception("model not found"), None]
                stage.ensure_model()
        # run called twice: once for "show" (fails), once for "create"
        assert mock_run.call_count == 2

    def test_raises_modelfile_error_when_modelfile_missing(self, tmp_path: Path) -> None:
        from magazine.config import Config
        cfg = Config()
        cfg.FOUNTAIN_AI_RUNTIME = "ollama"
        cfg.FOUNTAIN_AI_MODEL = "test-model:latest"
        cfg.FOUNTAIN_MODELFILE_PATH = str(tmp_path / "nonexistent_Modelfile")
        stage = FountainAIStage(config=cfg)
        with patch("magazine.ai.fountain.shutil.which", return_value="/usr/local/bin/ollama"):
            with patch("magazine.ai.fountain.run", side_effect=Exception("model not found")):
                with pytest.raises(ModelfileError):
                    stage.ensure_model()


class TestFountainGenerate:
    def test_skips_when_no_image(self, tmp_path: Path) -> None:
        stage = FountainAIStage()
        stage.generate(tmp_path)  # should not raise
        assert not (tmp_path / "page.fountain").exists()

    def test_skips_when_up_to_date(self, tmp_path: Path) -> None:
        img = tmp_path / "page.png"
        img.write_bytes(b"stable image")
        (tmp_path / "page.fountain").write_text("existing fountain")
        (tmp_path / ".build_state.json").write_text(
            json.dumps({"image_hash": hash_file(img)})
        )
        stage = FountainAIStage()
        with patch("magazine.ai.fountain.run") as mock_run:
            stage.generate_or_skip(tmp_path)
        mock_run.assert_not_called()

    def test_calls_runtime_when_regeneration_needed(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"new image data")
        # No fountain file → should_regenerate returns True
        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = "Title: Test\n\nINT. TEST – DAY\n"
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result) as mock_run:
                stage.generate(tmp_path)
        assert mock_run.call_count == 1

    def test_writes_fountain_file(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"new image data")
        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = "Title: Test\n\nINT. TEST – DAY\n"
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                stage.generate(tmp_path)
        assert (tmp_path / "page.fountain").exists()
        assert (tmp_path / "page.fountain").read_text() == mock_result.stdout

    def test_updates_build_state_with_hash(self, tmp_path: Path) -> None:
        img = tmp_path / "page.png"
        img.write_bytes(b"new image data")
        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = _VALID_FOUNTAIN
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                stage.generate(tmp_path)
        build_state = json.loads((tmp_path / ".build_state.json").read_text())
        assert "image_hash" in build_state
        assert build_state["image_hash"] == hash_file(img)

    def test_updates_build_state_with_ai_provenance(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image data")
        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = _VALID_FOUNTAIN
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                stage.generate(tmp_path)
        build_state = json.loads((tmp_path / ".build_state.json").read_text())
        assert "fountain_generated_by" in build_state
        assert "fountain_generated_at" not in build_state, (
            "fountain_generated_at is a timestamp and must not appear in .build_state.json"
        )

    def test_does_not_modify_meta_json(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image data")
        (tmp_path / "meta.json").write_text(
            json.dumps({"page_id": "01_test", "sequence_index": "01"})
        )
        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = _VALID_FOUNTAIN
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                stage.generate(tmp_path)
        meta = json.loads((tmp_path / "meta.json").read_text())
        assert meta["page_id"] == "01_test"
        assert meta["sequence_index"] == "01"
        assert "image_hash" not in meta, "image_hash must not appear in meta.json"
        assert "fountain_generated_by" not in meta, "fountain_generated_by must not appear in meta.json"
        assert "fountain_generated_at" not in meta, "fountain_generated_at must not appear in meta.json"

    def test_second_run_skipped_after_generation(self, tmp_path: Path) -> None:
        """After generate_or_skip() succeeds, a second call should not re-invoke AI."""
        (tmp_path / "page.png").write_bytes(b"stable image")
        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = _VALID_FOUNTAIN
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result) as mock_run:
                stage.generate_or_skip(tmp_path)
                stage.generate_or_skip(tmp_path)
        assert mock_run.call_count == 1

    def test_build_state_excludes_all_timestamps(self, tmp_path: Path) -> None:
        """No timestamp fields must appear in .build_state.json after generation."""
        (tmp_path / "page.png").write_bytes(b"image data")
        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = _VALID_FOUNTAIN
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                stage.generate(tmp_path)
        build_state = json.loads((tmp_path / ".build_state.json").read_text())
        timestamp_fields = {"fountain_generated_at", "generated_at", "created_at", "updated_at"}
        for field in timestamp_fields:
            assert field not in build_state, (
                f"Timestamp field '{field}' must not appear in .build_state.json"
            )

    def test_hash_invalidation_unaffected_by_timestamps(self, tmp_path: Path) -> None:
        """Injecting arbitrary timestamp fields into .build_state.json must not
        trigger regeneration when the image hash is unchanged."""
        img = tmp_path / "page.png"
        img.write_bytes(b"stable image content")
        (tmp_path / "page.fountain").write_text("existing fountain")
        (tmp_path / ".build_state.json").write_text(
            json.dumps({
                "image_hash": hash_file(img),
                "fountain_generated_by": "some-model",
                # Inject a timestamp as if written by an older code version
                "fountain_generated_at": "2024-01-01T00:00:00Z",
            })
        )
        stage = FountainAIStage()
        # should_regenerate must return False regardless of the extra timestamp field
        assert stage.should_regenerate(tmp_path) is False


class TestFountainValidateOutput:
    def _make_stage_result(self, stdout: str) -> tuple:
        """Return a (FountainAIStage, MagicMock) pair with stdout pre-set."""
        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = stdout
        return stage, mock_result

    def test_empty_output_raises(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image")
        stage, mock_result = self._make_stage_result("")
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                with pytest.raises(AIRuntimeError, match="empty output"):
                    stage.generate(tmp_path)
        assert not (tmp_path / "page.fountain").exists()

    def test_whitespace_only_output_raises(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image")
        stage, mock_result = self._make_stage_result("   \n\n  ")
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                with pytest.raises(AIRuntimeError, match="empty output"):
                    stage.generate(tmp_path)
        assert not (tmp_path / "page.fountain").exists()

    def test_missing_title_raises(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image")
        stage, mock_result = self._make_stage_result("INT. OFFICE – DAY\n\nSome text here.\n")
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                with pytest.raises(AIRuntimeError, match="Title line"):
                    stage.generate(tmp_path)
        assert not (tmp_path / "page.fountain").exists()

    def test_missing_scene_heading_raises(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image")
        stage, mock_result = self._make_stage_result("Title: Test\n\nSome narrative.\n")
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                with pytest.raises(AIRuntimeError, match="scene heading"):
                    stage.generate(tmp_path)
        assert not (tmp_path / "page.fountain").exists()

    def test_error_phrase_raises(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image")
        stage, mock_result = self._make_stage_result(
            "Error: Cannot process image.\nTitle: X\nINT. Y\n"
        )
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                with pytest.raises(AIRuntimeError, match="error phrase"):
                    stage.generate(tmp_path)
        assert not (tmp_path / "page.fountain").exists()

    def test_cannot_see_image_phrase_raises(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image")
        stage, mock_result = self._make_stage_result(
            "Cannot see image. Title: X\n\nINT. Y – DAY\n\nSome text.\n"
        )
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                with pytest.raises(AIRuntimeError, match="error phrase"):
                    stage.generate(tmp_path)
        assert not (tmp_path / "page.fountain").exists()

    def test_insufficient_structure_raises(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image")
        # Only one block (no double-newline separator)
        stage, mock_result = self._make_stage_result("Title: Test\nINT. OFFICE – DAY\n")
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                with pytest.raises(AIRuntimeError, match="insufficient structure"):
                    stage.generate(tmp_path)
        assert not (tmp_path / "page.fountain").exists()

    def test_valid_output_writes_file(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image")
        stage, mock_result = self._make_stage_result(_VALID_FOUNTAIN)
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                stage.generate(tmp_path)
        assert (tmp_path / "page.fountain").exists()
        assert (tmp_path / "page.fountain").read_text() == _VALID_FOUNTAIN

    def test_ext_scene_heading_is_valid(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image")
        ext_fountain = "Title: Exterior\n\nEXT. GARDEN – DAY\n\nA quiet moment.\n"
        stage, mock_result = self._make_stage_result(ext_fountain)
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result):
                stage.generate(tmp_path)
        assert (tmp_path / "page.fountain").read_text() == ext_fountain


class TestBuildPrompt:
    def test_author_injected_into_prompt(self) -> None:
        prompt = _build_prompt("Jane Doe", "My Magazine")
        assert "Written & Designed by Jane Doe" in prompt

    def test_edition_name_injected_into_prompt(self) -> None:
        prompt = _build_prompt("Jane Doe", "Issue 7 – Summer")
        assert "Source: Issue 7 – Summer" in prompt

    def test_no_hardcoded_author_in_prompt(self) -> None:
        prompt = _build_prompt("New Author", "New Edition")
        assert "Alan Szmyt" not in prompt
        assert "Ego Hygiene" not in prompt
        assert "Edition 1" not in prompt

    def test_prompt_is_deterministic(self) -> None:
        prompt1 = _build_prompt("Author A", "Edition X")
        prompt2 = _build_prompt("Author A", "Edition X")
        assert prompt1 == prompt2

    def test_empty_edition_name_produces_empty_source(self) -> None:
        prompt = _build_prompt("Some Author", "")
        assert "Source: \n" in prompt

    def test_prompt_contains_required_structure(self) -> None:
        prompt = _build_prompt("Test Author", "Test Edition")
        assert "Title:" in prompt
        assert "Credit:" in prompt
        assert "Draft date:" in prompt
        assert "Source:" in prompt
        assert "INT. PRINTED MAGAZINE" in prompt


class TestFountainGenerateWithEditionName:
    def test_edition_name_passed_to_prompt(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image data")
        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = _VALID_FOUNTAIN
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result) as mock_run:
                stage.generate(tmp_path, edition_name="Custom Edition")
        call_args = mock_run.call_args[0][0]
        prompt_arg = call_args[-1]
        assert "Custom Edition" in prompt_arg

    def test_author_env_override_used_in_prompt(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image data")
        mock_result = MagicMock()
        mock_result.stdout = _VALID_FOUNTAIN
        with patch.dict(os.environ, {"MAGAZINE_AUTHOR": "Override Author"}):
            from magazine.config import Config
            stage = FountainAIStage(config=Config())
            with patch.object(stage, "ensure_model"):
                with patch("magazine.ai.fountain.run", return_value=mock_result) as mock_run:
                    stage.generate(tmp_path, edition_name="Test Edition")
        call_args = mock_run.call_args[0][0]
        prompt_arg = call_args[-1]
        assert "Override Author" in prompt_arg
        assert "Alan Szmyt" not in prompt_arg

    def test_default_edition_name_is_empty_string(self, tmp_path: Path) -> None:
        (tmp_path / "page.png").write_bytes(b"image data")
        stage = FountainAIStage()
        mock_result = MagicMock()
        mock_result.stdout = _VALID_FOUNTAIN
        with patch.object(stage, "ensure_model"):
            with patch("magazine.ai.fountain.run", return_value=mock_result) as mock_run:
                stage.generate(tmp_path)
        call_args = mock_run.call_args[0][0]
        prompt_arg = call_args[-1]
        assert "Ego Hygiene" not in prompt_arg
        assert "Edition 1" not in prompt_arg
