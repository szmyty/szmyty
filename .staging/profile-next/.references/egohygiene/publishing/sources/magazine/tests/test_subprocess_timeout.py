"""Tests for subprocess timeout behaviour (magazine.utils.run)."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from magazine.exceptions import SubprocessTimeoutError
from magazine.utils import run


class TestSubprocessTimeoutError:
    def test_is_magazine_error_subclass(self) -> None:
        from magazine.exceptions import MagazineError

        assert issubclass(SubprocessTimeoutError, MagazineError)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(SubprocessTimeoutError):
            raise SubprocessTimeoutError("timed out")


class TestRunTimeout:
    def test_raises_subprocess_timeout_error_on_timeout(self) -> None:
        """run() must raise SubprocessTimeoutError when the process times out."""
        with patch("magazine.utils.subprocess.run") as mock_sub:
            mock_sub.side_effect = subprocess.TimeoutExpired(cmd=["fake"], timeout=300)
            with pytest.raises(SubprocessTimeoutError, match="fake"):
                run(["fake", "arg"])

    def test_error_message_contains_tool_name(self) -> None:
        with patch("magazine.utils.subprocess.run") as mock_sub:
            mock_sub.side_effect = subprocess.TimeoutExpired(cmd=["xelatex"], timeout=300)
            with pytest.raises(SubprocessTimeoutError, match="xelatex"):
                run(["xelatex", "-interaction=nonstopmode"])

    def test_error_message_contains_timeout_value(self) -> None:
        with patch("magazine.utils.subprocess.run") as mock_sub:
            mock_sub.side_effect = subprocess.TimeoutExpired(cmd=["magick"], timeout=60)
            with pytest.raises(SubprocessTimeoutError, match="60"):
                run(["magick", "input.png"], timeout=60)

    def test_timeout_passed_to_subprocess(self) -> None:
        """run() must forward the timeout value to subprocess.run."""
        with patch("magazine.utils.subprocess.run") as mock_sub:
            mock_sub.return_value.returncode = 0
            run(["echo", "hello"], timeout=42)
        _, kwargs = mock_sub.call_args
        assert kwargs["timeout"] == 42

    def test_default_timeout_from_config(self) -> None:
        """run() uses config.SUBPROCESS_TIMEOUT when no timeout kwarg is given."""
        with patch("magazine.utils.subprocess.run") as mock_sub:
            mock_sub.return_value.returncode = 0
            run(["echo"])
        _, kwargs = mock_sub.call_args
        # Default value from Config is 300
        assert kwargs["timeout"] == 300

    def test_caller_can_override_timeout(self) -> None:
        """Explicit timeout kwarg takes precedence over the config default."""
        with patch("magazine.utils.subprocess.run") as mock_sub:
            mock_sub.return_value.returncode = 0
            run(["echo"], timeout=10)
        _, kwargs = mock_sub.call_args
        assert kwargs["timeout"] == 10

    def test_no_artifact_written_on_timeout(self, tmp_path: Path) -> None:
        """No output file should be created when a timeout occurs."""
        out_file = tmp_path / "output.pdf"
        with patch("magazine.utils.subprocess.run") as mock_sub:
            mock_sub.side_effect = subprocess.TimeoutExpired(cmd=["img2pdf"], timeout=300)
            with pytest.raises(SubprocessTimeoutError):
                run(["img2pdf", "page.png", "-o", str(out_file)])
        assert not out_file.exists()

    def test_successful_run_not_affected(self) -> None:
        """A successful run must not raise SubprocessTimeoutError."""
        with patch("magazine.utils.subprocess.run") as mock_sub:
            mock_sub.return_value.returncode = 0
            result = run(["echo", "ok"])
        assert result is mock_sub.return_value


class TestConfigSubprocessTimeout:
    def test_default_is_300(self) -> None:
        from magazine.config import Config

        assert Config().SUBPROCESS_TIMEOUT == 300

    def test_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAGAZINE_SUBPROCESS_TIMEOUT", "120")
        from magazine.config import Config

        assert Config().SUBPROCESS_TIMEOUT == 120

    def test_env_override_applied_in_run(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """MAGAZINE_SUBPROCESS_TIMEOUT env var flows through to subprocess.run."""
        monkeypatch.setenv("MAGAZINE_SUBPROCESS_TIMEOUT", "45")
        with patch("magazine.utils.subprocess.run") as mock_sub:
            mock_sub.return_value.returncode = 0
            run(["echo"])
        _, kwargs = mock_sub.call_args
        assert kwargs["timeout"] == 45
