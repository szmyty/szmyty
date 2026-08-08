"""Tests for the CLI (magazine.cli) — flag parsing and pipeline routing."""

import json
from pathlib import Path
from unittest.mock import patch, call

import pytest
from click.testing import CliRunner

from magazine.cli import cli


class TestCLIHelp:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_root_help_exit_zero(self) -> None:
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_root_help_lists_commands(self) -> None:
        result = self.runner.invoke(cli, ["--help"])
        for cmd in ("manifest", "page", "edition", "finalize"):
            assert cmd in result.output

    def test_page_help(self) -> None:
        result = self.runner.invoke(cli, ["page", "--help"])
        assert result.exit_code == 0
        assert "PAGE_PATH" in result.output

    def test_edition_help(self) -> None:
        result = self.runner.invoke(cli, ["edition", "--help"])
        assert result.exit_code == 0
        assert "EDITION_PATH" in result.output

    def test_finalize_help(self) -> None:
        result = self.runner.invoke(cli, ["finalize", "--help"])
        assert result.exit_code == 0
        assert "EDITION_PATH" in result.output

    def test_manifest_help(self) -> None:
        result = self.runner.invoke(cli, ["manifest", "--help"])
        assert result.exit_code == 0
        assert "EDITION_PATH" in result.output


class TestPageFlags:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_page_latex_flags_in_help(self) -> None:
        result = self.runner.invoke(cli, ["page", "--help"])
        assert "--latex-disable" in result.output
        assert "--latex-force" in result.output
        assert "--latex-safe-mode" in result.output
        assert "--latex-engine" in result.output

    def test_page_sizes_flags_in_help(self) -> None:
        result = self.runner.invoke(cli, ["page", "--help"])
        assert "--sizes-disable" in result.output
        assert "--sizes-force" in result.output
        assert "--sizes" in result.output
        assert "--sizes-config" in result.output
        assert "--sizes-safe-mode" in result.output

    def test_page_routes_to_build_page(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            result = self.runner.invoke(cli, ["page", str(page_dir)])
        assert result.exit_code == 0
        mock_build.assert_called_once()

    def test_page_latex_disable_flag(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", "--latex-disable", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["latex_disable"] is True

    def test_page_latex_force_flag(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", "--latex-force", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["latex_force"] is True

    def test_page_sizes_disable_flag(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", "--sizes-disable", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["sizes_disable"] is True

    def test_page_sizes_force_flag(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", "--sizes-force", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["sizes_force"] is True

    def test_page_sizes_safe_mode_flag(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", "--sizes-safe-mode", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["sizes_safe_mode"] is True

    def test_page_sizes_list_parsed(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", "--sizes", "modern,manga", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["sizes"] == ["modern", "manga"]

    def test_page_latex_engine_passed(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", "--latex-engine", "pdflatex", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["latex_engine"] == "pdflatex"

    def test_page_force_flag_in_help(self) -> None:
        result = self.runner.invoke(cli, ["page", "--help"])
        assert "--force" in result.output

    def test_page_defaults_to_no_force(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["force"] is False

    def test_page_force_flag_passes_true(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", "--force", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["force"] is True


class TestEditionFlags:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_edition_has_latex_flags(self) -> None:
        result = self.runner.invoke(cli, ["edition", "--help"])
        assert "--latex-disable" in result.output
        assert "--latex-force" in result.output
        assert "--latex-safe-mode" in result.output
        assert "--latex-engine" in result.output

    def test_edition_has_sizes_flags(self) -> None:
        result = self.runner.invoke(cli, ["edition", "--help"])
        assert "--sizes-disable" in result.output
        assert "--sizes-force" in result.output
        assert "--sizes" in result.output

    def test_edition_has_skip_existing_flag(self) -> None:
        result = self.runner.invoke(cli, ["edition", "--help"])
        assert "--skip-existing" in result.output

    def test_edition_routes_to_build_edition(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_edition") as mock_build:
            result = self.runner.invoke(cli, ["edition", str(edition_dir)])
        assert result.exit_code == 0
        mock_build.assert_called_once()

    def test_edition_skip_existing_flag(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_edition") as mock_build:
            self.runner.invoke(cli, ["edition", "--skip-existing", str(edition_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["skip_existing"] is True

    def test_edition_latex_disable_flag(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_edition") as mock_build:
            self.runner.invoke(cli, ["edition", "--latex-disable", str(edition_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["latex_disable"] is True

    def test_edition_sizes_disable_flag(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_edition") as mock_build:
            self.runner.invoke(cli, ["edition", "--sizes-disable", str(edition_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["sizes_disable"] is True


class TestFinalizeFlags:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_finalize_has_force_flag(self) -> None:
        result = self.runner.invoke(cli, ["finalize", "--help"])
        assert "--force" in result.output

    def test_finalize_has_sizes_flags(self) -> None:
        result = self.runner.invoke(cli, ["finalize", "--help"])
        assert "--sizes-disable" in result.output
        assert "--sizes-force" in result.output
        assert "--sizes" in result.output
        assert "--sizes-config" in result.output
        assert "--sizes-safe-mode" in result.output

    def test_finalize_routes_to_finalize_edition(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.finalize_edition") as mock_fin:
            result = self.runner.invoke(cli, ["finalize", str(edition_dir)])
        assert result.exit_code == 0
        mock_fin.assert_called_once()

    def test_finalize_force_flag(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.finalize_edition") as mock_fin:
            self.runner.invoke(cli, ["finalize", "--force", str(edition_dir)])
        _, kwargs = mock_fin.call_args
        assert kwargs["force"] is True

    def test_finalize_sizes_disable_flag(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.finalize_edition") as mock_fin:
            self.runner.invoke(cli, ["finalize", "--sizes-disable", str(edition_dir)])
        _, kwargs = mock_fin.call_args
        assert kwargs["sizes_disable"] is True

    def test_finalize_sizes_force_flag(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.finalize_edition") as mock_fin:
            self.runner.invoke(cli, ["finalize", "--sizes-force", str(edition_dir)])
        _, kwargs = mock_fin.call_args
        assert kwargs["sizes_force"] is True


class TestManifestCommand:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_manifest_routes_to_gen_page_meta(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        (pages / "01_intro").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.gen_page_meta") as mock_meta:
            result = self.runner.invoke(cli, ["manifest", str(edition_dir)])
        assert result.exit_code == 0
        mock_meta.assert_called_once()

    def test_manifest_calls_meta_for_each_page(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        for slug in ("01_intro", "02_body", "03_end"):
            (pages / slug).mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.gen_page_meta") as mock_meta:
            self.runner.invoke(cli, ["manifest", str(edition_dir)])
        assert mock_meta.call_count == 3

    def test_manifest_pages_sorted(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        for slug in ("03_end", "01_intro", "02_body"):
            (pages / slug).mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.gen_page_meta") as mock_meta:
            self.runner.invoke(cli, ["manifest", str(edition_dir)])
        names = [c.args[0].name for c in mock_meta.call_args_list]
        assert names == sorted(names)


class TestCLIErrorHandling:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_page_exits_on_magazine_error(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        from magazine.exceptions import MagazineError
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page", side_effect=MagazineError("oops")):
            result = self.runner.invoke(cli, ["page", str(page_dir)])
        assert result.exit_code == 1

    def test_edition_exits_on_magazine_error(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "ed"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        from magazine.exceptions import MagazineError
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_edition", side_effect=MagazineError("oops")):
            result = self.runner.invoke(cli, ["edition", str(edition_dir)])
        assert result.exit_code == 1

    def test_finalize_exits_on_magazine_error(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "ed"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        from magazine.exceptions import MagazineError
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.finalize_edition", side_effect=MagazineError("oops")):
            result = self.runner.invoke(cli, ["finalize", str(edition_dir)])
        assert result.exit_code == 1


class TestVersion:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_version_attribute_exists(self) -> None:
        import magazine
        assert hasattr(magazine, "__version__")

    def test_version_is_string(self) -> None:
        import magazine
        assert isinstance(magazine.__version__, str)

    def test_version_is_not_empty(self) -> None:
        import magazine
        assert magazine.__version__

    def test_cli_version_flag(self) -> None:
        import magazine
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert magazine.__version__ in result.output

    def test_version_matches_pyproject_toml(self) -> None:
        import tomllib
        import magazine
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
        assert magazine.__version__ == data["tool"]["poetry"]["version"]


class TestReproducibleFlag:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_reproducible_flag_in_help(self) -> None:
        result = self.runner.invoke(cli, ["--help"])
        assert "--reproducible" in result.output

    def test_reproducible_passed_to_manifest(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        (pages / "01_intro").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.gen_page_meta") as mock_meta:
            self.runner.invoke(cli, ["--reproducible", "manifest", str(edition_dir)])
        _, kwargs = mock_meta.call_args
        assert kwargs.get("reproducible") is True

    def test_non_reproducible_default_manifest(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        (pages / "01_intro").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.gen_page_meta") as mock_meta:
            self.runner.invoke(cli, ["manifest", str(edition_dir)])
        _, kwargs = mock_meta.call_args
        assert kwargs.get("reproducible") is False

    def test_reproducible_passed_to_page(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["--reproducible", "page", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs.get("reproducible") is True

    def test_reproducible_passed_to_edition(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_edition") as mock_build:
            self.runner.invoke(cli, ["--reproducible", "edition", str(edition_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs.get("reproducible") is True

    def test_reproducible_passed_to_finalize(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.finalize_edition") as mock_fin:
            self.runner.invoke(cli, ["--reproducible", "finalize", str(edition_dir)])
        _, kwargs = mock_fin.call_args
        assert kwargs.get("reproducible") is True

    def test_non_reproducible_default_finalize(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.finalize_edition") as mock_fin:
            self.runner.invoke(cli, ["finalize", str(edition_dir)])
        _, kwargs = mock_fin.call_args
        assert kwargs.get("reproducible") is False


class TestAIFlags:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_ai_fountain_model_in_help(self) -> None:
        result = self.runner.invoke(cli, ["--help"])
        assert "--ai-fountain-model" in result.output

    def test_ai_fountain_runtime_in_help(self) -> None:
        result = self.runner.invoke(cli, ["--help"])
        assert "--ai-fountain-runtime" in result.output

    def test_ai_fountain_model_overrides_config(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["--ai-fountain-model", "llama3:latest", "page", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["config"].FOUNTAIN_AI_MODEL == "llama3:latest"

    def test_ai_fountain_runtime_overrides_config(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["--ai-fountain-runtime", "llamacpp", "page", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["config"].FOUNTAIN_AI_RUNTIME == "llamacpp"

    def test_ai_fountain_model_default_unchanged(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["config"].FOUNTAIN_AI_MODEL == "qwen3-vl-fountain:latest"

    def test_ai_fountain_runtime_default_unchanged(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["config"].FOUNTAIN_AI_RUNTIME == "ollama"

    def test_ai_flags_propagate_to_edition(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_edition") as mock_build:
            self.runner.invoke(
                cli,
                ["--ai-fountain-model", "mistral:latest", "--ai-fountain-runtime", "ollama2", "edition", str(edition_dir)],
            )
        _, kwargs = mock_build.call_args
        assert kwargs["config"].FOUNTAIN_AI_MODEL == "mistral:latest"
        assert kwargs["config"].FOUNTAIN_AI_RUNTIME == "ollama2"

    def test_ai_fountain_disable_flag_in_page_help(self) -> None:
        result = self.runner.invoke(cli, ["page", "--help"])
        assert "--ai-fountain-disable" in result.output

    def test_ai_fountain_disable_flag_in_edition_help(self) -> None:
        result = self.runner.invoke(cli, ["edition", "--help"])
        assert "--ai-fountain-disable" in result.output


class TestStageAwareDependencyValidation:
    """Tests that CLI commands call validate_dependencies with correct active stages."""

    def setup_method(self) -> None:
        self.runner = CliRunner()

    # ------------------------------------------------------------------ #
    # page command
    # ------------------------------------------------------------------ #

    def test_page_default_includes_all_stages(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_page"):
            self.runner.invoke(cli, ["page", str(page_dir)])
        stages = mock_val.call_args[0][0]
        for stage in ("metadata", "images", "screenplay", "ai", "latex", "sizes"):
            assert stage in stages

    def test_page_ai_fountain_disable_excludes_ai_stage(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_page"):
            self.runner.invoke(cli, ["page", "--ai-fountain-disable", str(page_dir)])
        stages = mock_val.call_args[0][0]
        assert "ai" not in stages

    def test_page_latex_disable_excludes_latex_stage(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_page"):
            self.runner.invoke(cli, ["page", "--latex-disable", str(page_dir)])
        stages = mock_val.call_args[0][0]
        assert "latex" not in stages

    def test_page_sizes_disable_excludes_sizes_stage(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_page"):
            self.runner.invoke(cli, ["page", "--sizes-disable", str(page_dir)])
        stages = mock_val.call_args[0][0]
        assert "sizes" not in stages

    def test_page_all_disable_flags_strips_optional_stages(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_page"):
            self.runner.invoke(
                cli,
                ["page", "--ai-fountain-disable", "--latex-disable", "--sizes-disable", str(page_dir)],
            )
        stages = mock_val.call_args[0][0]
        assert "ai" not in stages
        assert "latex" not in stages
        assert "sizes" not in stages
        # Core stages are always present
        for stage in ("metadata", "images", "screenplay"):
            assert stage in stages

    # ------------------------------------------------------------------ #
    # edition command
    # ------------------------------------------------------------------ #

    def test_edition_default_includes_all_stages(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_edition"):
            self.runner.invoke(cli, ["edition", str(edition_dir)])
        stages = mock_val.call_args[0][0]
        for stage in ("metadata", "images", "screenplay", "ai", "latex", "sizes"):
            assert stage in stages

    def test_edition_ai_fountain_disable_excludes_ai_stage(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_edition"):
            self.runner.invoke(cli, ["edition", "--ai-fountain-disable", str(edition_dir)])
        stages = mock_val.call_args[0][0]
        assert "ai" not in stages

    def test_edition_latex_disable_excludes_latex_stage(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_edition"):
            self.runner.invoke(cli, ["edition", "--latex-disable", str(edition_dir)])
        stages = mock_val.call_args[0][0]
        assert "latex" not in stages

    def test_edition_sizes_disable_excludes_sizes_stage(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_edition"):
            self.runner.invoke(cli, ["edition", "--sizes-disable", str(edition_dir)])
        stages = mock_val.call_args[0][0]
        assert "sizes" not in stages

    # ------------------------------------------------------------------ #
    # finalize command
    # ------------------------------------------------------------------ #

    def test_finalize_default_includes_bundle_and_images(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.finalize_edition"):
            self.runner.invoke(cli, ["finalize", str(edition_dir)])
        stages = mock_val.call_args[0][0]
        assert "bundle" in stages
        assert "images" in stages
        assert "sizes" in stages

    def test_finalize_sizes_disable_excludes_sizes_stage(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.finalize_edition"):
            self.runner.invoke(cli, ["finalize", "--sizes-disable", str(edition_dir)])
        stages = mock_val.call_args[0][0]
        assert "sizes" not in stages
        assert "bundle" in stages

    # ------------------------------------------------------------------ #
    # manifest command
    # ------------------------------------------------------------------ #

    def test_manifest_validates_metadata_and_exif_stages(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        (pages / "01_intro").mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.gen_page_meta"):
            self.runner.invoke(cli, ["manifest", str(edition_dir)])
        stages = mock_val.call_args[0][0]
        assert "metadata" in stages
        assert "exif" in stages


class TestMetadataExifDisableFlag:
    """Tests for --metadata-exif-disable flag across commands."""

    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_page_metadata_exif_disable_in_help(self) -> None:
        result = self.runner.invoke(cli, ["page", "--help"])
        assert "--metadata-exif-disable" in result.output

    def test_edition_metadata_exif_disable_in_help(self) -> None:
        result = self.runner.invoke(cli, ["edition", "--help"])
        assert "--metadata-exif-disable" in result.output

    def test_manifest_metadata_exif_disable_in_help(self) -> None:
        result = self.runner.invoke(cli, ["manifest", "--help"])
        assert "--metadata-exif-disable" in result.output

    def test_page_metadata_exif_disable_excludes_exif_stage(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_page"):
            self.runner.invoke(cli, ["page", "--metadata-exif-disable", str(page_dir)])
        stages = mock_val.call_args[0][0]
        assert "exif" not in stages

    def test_page_default_includes_exif_stage(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_page"):
            self.runner.invoke(cli, ["page", str(page_dir)])
        stages = mock_val.call_args[0][0]
        assert "exif" in stages

    def test_page_metadata_exif_disable_passes_flag(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", "--metadata-exif-disable", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["exif_disable"] is True

    def test_page_default_exif_disable_is_false(self, tmp_path: Path) -> None:
        page_dir = tmp_path / "01_test"
        page_dir.mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_page") as mock_build:
            self.runner.invoke(cli, ["page", str(page_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["exif_disable"] is False

    def test_edition_metadata_exif_disable_excludes_exif_stage(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_edition"):
            self.runner.invoke(cli, ["edition", "--metadata-exif-disable", str(edition_dir)])
        stages = mock_val.call_args[0][0]
        assert "exif" not in stages

    def test_edition_default_includes_exif_stage(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.build_edition"):
            self.runner.invoke(cli, ["edition", str(edition_dir)])
        stages = mock_val.call_args[0][0]
        assert "exif" in stages

    def test_edition_metadata_exif_disable_passes_flag(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        (edition_dir / "pages").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.build_edition") as mock_build:
            self.runner.invoke(cli, ["edition", "--metadata-exif-disable", str(edition_dir)])
        _, kwargs = mock_build.call_args
        assert kwargs["exif_disable"] is True

    def test_manifest_metadata_exif_disable_excludes_exif_stage(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        (pages / "01_intro").mkdir()
        with patch("magazine.cli.validate_dependencies") as mock_val, \
             patch("magazine.cli.gen_page_meta"):
            self.runner.invoke(cli, ["manifest", "--metadata-exif-disable", str(edition_dir)])
        stages = mock_val.call_args[0][0]
        assert "exif" not in stages
        assert "metadata" in stages

    def test_manifest_metadata_exif_disable_passes_flag(self, tmp_path: Path) -> None:
        edition_dir = tmp_path / "edition_01"
        edition_dir.mkdir()
        pages = edition_dir / "pages"
        pages.mkdir()
        (pages / "01_intro").mkdir()
        with patch("magazine.cli.validate_dependencies"), \
             patch("magazine.cli.gen_page_meta") as mock_meta:
            self.runner.invoke(cli, ["manifest", "--metadata-exif-disable", str(edition_dir)])
        _, kwargs = mock_meta.call_args
        assert kwargs.get("exif_disable") is True
