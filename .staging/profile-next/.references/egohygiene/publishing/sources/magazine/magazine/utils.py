"""Utility helpers: logging, timestamps, dependency checking."""

import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from magazine.exceptions import DependencyError, SubprocessTimeoutError


# --------------------------------------------------------------------------- #
# NO_COLOR support (https://no-color.org/)
# --------------------------------------------------------------------------- #
_NO_COLOR = bool(os.environ.get("NO_COLOR", ""))

_BLUE = "" if _NO_COLOR else "\033[34m"
_YELLOW = "" if _NO_COLOR else "\033[33m"
_GREEN = "" if _NO_COLOR else "\033[32m"
_RED = "" if _NO_COLOR else "\033[31m"
_RESET = "" if _NO_COLOR else "\033[0m"


def page_dirs(edition_path: Path) -> list[Path]:
    """Return sorted list of page subdirectories under *edition_path*/pages."""
    pages_root = edition_path / "pages"
    return sorted(p for p in pages_root.iterdir() if p.is_dir())


REPRODUCIBLE_TIMESTAMP = "1970-01-01T00:00:00Z"
"""Fixed epoch timestamp used when reproducible build mode is active."""


def timestamp() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_info(message: str) -> None:
    ts = timestamp()
    print(f"{_BLUE}[{ts}] \u2139 INFO  {message}{_RESET}", flush=True)


def log_warn(message: str) -> None:
    ts = timestamp()
    print(f"{_YELLOW}[{ts}] \u26a0 WARN  {message}{_RESET}", file=sys.stderr, flush=True)


def log_success(message: str) -> None:
    ts = timestamp()
    print(f"{_GREEN}[{ts}] \u2714 SUCCESS  {message}{_RESET}", flush=True)


def log_error(message: str) -> None:
    ts = timestamp()
    print(f"{_RED}[{ts}] \u2716 ERROR  {message}{_RESET}", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- #
# Dependency checking
# --------------------------------------------------------------------------- #

#: Maps each pipeline stage name to the external tools it requires.
_STAGE_TOOLS: dict[str, list[str]] = {
    "metadata": [],
    "exif": ["exiftool"],
    "images": ["magick", "img2pdf"],
    "screenplay": ["afterwriting", "scripttool", "wrap", "jq"],
    "latex": ["xelatex", "pdflatex"],  # at least one is sufficient
    "ai": ["ollama"],
    "sizes": ["magick", "img2pdf"],
    "bundle": ["zip"],
}


def validate_dependencies(active_stages: list[str] | None = None) -> None:
    """Raise DependencyError if any required tool for the active stages is missing.

    Args:
        active_stages: Stage names to validate (e.g. ``["images", "latex"]``).
                       When ``None``, all stages in ``_STAGE_TOOLS`` are validated.

    Raises:
        DependencyError: If a required tool is not found on PATH.
    """
    stages = active_stages if active_stages is not None else list(_STAGE_TOOLS)
    # Map tool → stage for clear error messages
    missing_by_stage: dict[str, list[str]] = {}
    for stage in stages:
        tools = _STAGE_TOOLS.get(stage, [])
        if stage == "latex":
            # Either xelatex or pdflatex is sufficient; report as an alternative pair.
            if not any(shutil.which(t) for t in tools):
                missing_by_stage.setdefault(stage, []).append("xelatex or pdflatex")
        else:
            stage_missing = [t for t in tools if shutil.which(t) is None]
            if stage_missing:
                missing_by_stage.setdefault(stage, []).extend(stage_missing)
    if missing_by_stage:
        lines = ["Missing required tools:"]
        for stage in sorted(missing_by_stage):
            tools_str = ", ".join(missing_by_stage[stage])
            lines.append(f"  [{stage}] {tools_str}")
        lines.append("Install the missing tools before running the pipeline.")
        raise DependencyError("\n".join(lines))

    if "images" in stages:
        try:
            import pillow_avif  # noqa: F401
        except ImportError:
            log_warn("⚠️ AVIF plugin not installed — skipping AVIF generation")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a subprocess command, raising on non-zero exit.

    Applies a timeout (default: ``config.SUBPROCESS_TIMEOUT``) to prevent
    indefinite blocking.  Pass ``timeout=<seconds>`` in *kwargs* to override
    the default for a single call.

    Raises:
        SubprocessTimeoutError: When the process does not finish within the
            allowed time.
        subprocess.CalledProcessError: When the process exits with a non-zero
            return code (propagated from ``check=True``).
    """
    timeout = kwargs.pop("timeout", int(os.environ.get("MAGAZINE_SUBPROCESS_TIMEOUT", "300")))
    try:
        return subprocess.run(cmd, check=True, timeout=timeout, **kwargs)  # noqa: S603
    except subprocess.TimeoutExpired as exc:
        tool = cmd[0] if cmd else "<unknown>"
        raise SubprocessTimeoutError(
            f"Subprocess '{tool}' timed out after {timeout}s."
        ) from exc
