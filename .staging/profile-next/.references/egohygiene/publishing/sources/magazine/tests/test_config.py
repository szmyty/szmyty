"""Tests for configuration (magazine.config)."""

import pytest

from magazine.config import Config


class TestConfigDefaults:
    def test_print_dpi(self) -> None:
        assert Config().PRINT_DPI == 300

    def test_web_width(self) -> None:
        assert Config().WEB_WIDTH == 1080

    def test_instagram_dimensions(self) -> None:
        cfg = Config()
        assert cfg.INSTAGRAM_WIDTH == 1080
        assert cfg.INSTAGRAM_HEIGHT == 1350

    def test_fountain_runtime(self) -> None:
        assert Config().FOUNTAIN_AI_RUNTIME == "ollama"

    def test_fountain_model(self) -> None:
        assert Config().FOUNTAIN_AI_MODEL == "qwen3-vl-fountain:latest"

    def test_latex_engine(self) -> None:
        assert Config().LATEX_ENGINE == "xelatex"

    def test_latex_safe_margin(self) -> None:
        assert Config().LATEX_SAFE_MARGIN == "0.25in"

    def test_latex_paper_dimensions(self) -> None:
        cfg = Config()
        assert cfg.LATEX_PAPER_WIDTH == "8.5in"
        assert cfg.LATEX_PAPER_HEIGHT == "11in"

    def test_sizes_config_path_empty(self) -> None:
        assert Config().SIZES_CONFIG_PATH == ""

    def test_sizes_default_all(self) -> None:
        assert Config().SIZES_DEFAULT == "all"

    def test_author(self) -> None:
        assert Config().AUTHOR == "Alan R Szmyt"

    def test_alias(self) -> None:
        assert Config().ALIAS == "Play Function"

    def test_location(self) -> None:
        assert Config().LOCATION == "Wilmington, MA"

    def test_publisher(self) -> None:
        assert Config().PUBLISHER == "Play Function"

    def test_format_version(self) -> None:
        assert Config().FORMAT_VERSION == "1.0"


class TestConfigEnvOverrides:
    """Verify environment variables override every default (12-factor)."""

    def test_print_dpi_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_PRINT_DPI", "600")
        assert Config().PRINT_DPI == 600

    def test_web_width_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_WEB_WIDTH", "1920")
        assert Config().WEB_WIDTH == 1920

    def test_instagram_width_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_INSTAGRAM_WIDTH", "1440")
        assert Config().INSTAGRAM_WIDTH == 1440

    def test_instagram_height_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_INSTAGRAM_HEIGHT", "1800")
        assert Config().INSTAGRAM_HEIGHT == 1800

    def test_fountain_runtime_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_FOUNTAIN_AI_RUNTIME", "llamacpp")
        assert Config().FOUNTAIN_AI_RUNTIME == "llamacpp"

    def test_fountain_model_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_FOUNTAIN_AI_MODEL", "llama3:latest")
        assert Config().FOUNTAIN_AI_MODEL == "llama3:latest"

    def test_latex_engine_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_LATEX_ENGINE", "pdflatex")
        assert Config().LATEX_ENGINE == "pdflatex"

    def test_latex_safe_margin_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_LATEX_SAFE_MARGIN", "0.5in")
        assert Config().LATEX_SAFE_MARGIN == "0.5in"

    def test_latex_paper_width_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_LATEX_PAPER_WIDTH", "210mm")
        assert Config().LATEX_PAPER_WIDTH == "210mm"

    def test_latex_paper_height_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_LATEX_PAPER_HEIGHT", "297mm")
        assert Config().LATEX_PAPER_HEIGHT == "297mm"

    def test_sizes_config_path_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_SIZES_CONFIG", "/tmp/custom_sizes.json")
        assert Config().SIZES_CONFIG_PATH == "/tmp/custom_sizes.json"

    def test_sizes_default_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_DEFAULT_SIZES", "modern,manga")
        assert Config().SIZES_DEFAULT == "modern,manga"

    def test_author_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_AUTHOR", "Jane Doe")
        assert Config().AUTHOR == "Jane Doe"

    def test_alias_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_ALIAS", "JD")
        assert Config().ALIAS == "JD"

    def test_location_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_LOCATION", "Boston, MA")
        assert Config().LOCATION == "Boston, MA"

    def test_publisher_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_PUBLISHER", "ACME Publishing")
        assert Config().PUBLISHER == "ACME Publishing"

    def test_format_version_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_FORMAT_VERSION", "2.0")
        assert Config().FORMAT_VERSION == "2.0"

    def test_multiple_overrides_isolated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_PRINT_DPI", "150")
        monkeypatch.setenv("MAGAZINE_WEB_WIDTH", "800")
        cfg = Config()
        assert cfg.PRINT_DPI == 150
        assert cfg.WEB_WIDTH == 800

    def test_env_not_set_uses_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MAGAZINE_PRINT_DPI", raising=False)
        assert Config().PRINT_DPI == 300


class TestConfigPrecedence:
    """Verify that env vars take precedence over built-in defaults."""

    def test_env_beats_default_for_dpi(self, monkeypatch: pytest.MonkeyPatch) -> None:
        default = Config().PRINT_DPI
        monkeypatch.setenv("MAGAZINE_PRINT_DPI", str(default + 100))
        assert Config().PRINT_DPI == default + 100

    def test_each_instantiation_reads_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_AUTHOR", "First Author")
        cfg1 = Config()
        monkeypatch.setenv("MAGAZINE_AUTHOR", "Second Author")
        cfg2 = Config()
        assert cfg1.AUTHOR == "First Author"
        assert cfg2.AUTHOR == "Second Author"
