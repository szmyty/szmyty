"""Tests for metadata generation (magazine.metadata)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from magazine.metadata import gen_page_meta
from magazine.utils import REPRODUCIBLE_TIMESTAMP


class TestGenPageMeta:
    def test_writes_meta_json(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_intro"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        assert (page_dir / "meta.json").exists()

    def test_correct_page_id(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "05_test_page"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["page_id"] == "05_test_page"

    def test_correct_sequence_index(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "03_cover"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["sequence_index"] == 3

    def test_generated_at_present(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert "generated_at" in meta
        assert meta["generated_at"].endswith("Z")
        assert "T" in meta["generated_at"]

    def test_project_context_keys(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        ctx = meta["project_context"]
        assert "author" in ctx
        assert "alias" in ctx
        assert "location" in ctx

    def test_default_author_in_context(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["project_context"]["author"] == "Alan R Szmyt"

    def test_required_keys_present(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "07_spread"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        for key in ("page_id", "sequence_index", "generated_at", "project_context", "raw_exif"):
            assert key in meta, f"Missing required key: {key}"

    def test_raw_exif_empty_without_image(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_no_image"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["raw_exif"] == {}

    def test_valid_json_output(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "02_body"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        content = (page_dir / "meta.json").read_text()
        parsed = json.loads(content)
        assert isinstance(parsed, dict)

    def test_overwrites_existing_meta(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        (page_dir / "meta.json").write_text('{"old_key": "old_value"}')
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert "page_id" in meta
        assert "old_key" not in meta

    def test_author_from_env(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_AUTHOR", "Test Author")
        from magazine.config import Config
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir, config=Config())
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["project_context"]["author"] == "Test Author"

    def test_exif_called_when_image_exists(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        (page_dir / "page.png").write_bytes(b"fake png")
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = '[{"File": {"FileName": "page.png"}}]'
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        # exiftool was called; raw_exif should be populated
        assert isinstance(meta["raw_exif"], dict)

    def test_exif_failure_does_not_crash(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        (page_dir / "page.png").write_bytes(b"fake png")
        with patch("magazine.utils.subprocess.run", side_effect=Exception("exiftool missing")):
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["raw_exif"] == {}

    def test_exif_failure_logs_warning(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        (page_dir / "page.png").write_bytes(b"fake png")
        with patch("magazine.utils.subprocess.run", side_effect=Exception("exiftool missing")):
            gen_page_meta(page_dir)
        captured = capsys.readouterr()
        assert "WARN" in captured.err
        assert "EXIF extraction failed" in captured.err
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["raw_exif"] == {}

    def test_exif_json_parse_failure_logs_warning(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        (page_dir / "page.png").write_bytes(b"fake png")
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "not valid json"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        captured = capsys.readouterr()
        assert "WARN" in captured.err
        assert "EXIF extraction failed" in captured.err
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["raw_exif"] == {}

    def test_exif_disable_skips_extraction(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        (page_dir / "page.png").write_bytes(b"fake png")
        with patch("magazine.utils.subprocess.run") as mock_run:
            gen_page_meta(page_dir, exif_disable=True)
        mock_run.assert_not_called()
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["raw_exif"] == {}

    def test_exif_disable_empty_raw_exif_without_image(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            gen_page_meta(page_dir, exif_disable=True)
        mock_run.assert_not_called()
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["raw_exif"] == {}

    def test_exif_disable_false_extracts_exif_when_image_exists(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        (page_dir / "page.png").write_bytes(b"fake png")
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = '[{"File": {"FileName": "page.png"}}]'
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir, exif_disable=False)
        mock_run.assert_called_once()
        meta = json.loads((page_dir / "meta.json").read_text())
        assert isinstance(meta["raw_exif"], dict)

    def test_meta_json_excludes_build_cache_fields(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        build_cache_fields = (
            "image_hash",
            "fountain_generated_by",
            "fountain_generated_at",
            "latex_page_png_hash",
            "latex_config_hash",
            "size_config_hash",
            "size_generated_at",
        )
        for field in build_cache_fields:
            assert field not in meta, (
                f"Build cache field '{field}' found in meta.json "
                f"but should only exist in .build_state.json"
            )


class TestGenPageMetaReproducible:
    def test_reproducible_uses_epoch_timestamp(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir, reproducible=True)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["generated_at"] == REPRODUCIBLE_TIMESTAMP

    def test_non_reproducible_uses_current_timestamp(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir, reproducible=False)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["generated_at"] != REPRODUCIBLE_TIMESTAMP

    def test_reproducible_builds_are_identical(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir, reproducible=True)
        first = (page_dir / "meta.json").read_text()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir, reproducible=True)
        second = (page_dir / "meta.json").read_text()
        assert first == second

    def test_reproducible_default_is_false(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_a"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["generated_at"] != REPRODUCIBLE_TIMESTAMP


class TestSlugValidation:
    """Tests for page directory name (slug) validation in gen_page_meta."""

    @pytest.mark.parametrize("slug", ["01_intro", "10_finale", "99_end", "00_cover"])
    def test_valid_slug_accepted(self, tmp_path: Path, slug: str) -> None:
        page_dir = tmp_path / slug
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)  # should not raise
        assert (page_dir / "meta.json").exists()

    def test_valid_slug_sequence_index_is_int(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "07_spread"
        page_dir.mkdir()
        with patch("magazine.utils.subprocess.run") as mock_run:
            mock_run.return_value.stdout = "[]"
            mock_run.return_value.returncode = 0
            gen_page_meta(page_dir)
        meta = json.loads((page_dir / "meta.json").read_text())
        assert meta["sequence_index"] == 7
        assert isinstance(meta["sequence_index"], int)

    @pytest.mark.parametrize("slug", ["cover", "intro", "page01", "_intro", "intro_01"])
    def test_invalid_slug_raises_value_error(self, tmp_path: Path, slug: str) -> None:
        page_dir = tmp_path / slug
        page_dir.mkdir()
        with pytest.raises(ValueError, match="Invalid page directory name"):
            gen_page_meta(page_dir)

    def test_invalid_slug_error_message_mentions_format(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "cover"
        page_dir.mkdir()
        with pytest.raises(ValueError, match="NN_slug"):
            gen_page_meta(page_dir)
