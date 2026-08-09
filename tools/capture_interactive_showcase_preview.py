"""Deterministic headless capture for the interactive observatory preview."""

from __future__ import annotations

import contextlib
import shutil
import subprocess
import tempfile
from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    REPO_ROOT / "profile" / "artifacts" / "interactive-showcase" / "preview.png"
)
DEFAULT_PORT = 4173
DEFAULT_VIEWPORT = "1280,720"


def _find_browser() -> str | None:
    for command in (
        "chromium-browser",
        "chromium",
        "google-chrome",
        "google-chrome-stable",
    ):
        if shutil.which(command):
            return command
    return None


def _serve_repo(port: int) -> ThreadingHTTPServer:
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(  # noqa: E731
        *args, directory=str(REPO_ROOT), **kwargs
    )
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _capture(output: Path, *, browser: str, port: int, viewport: str) -> int:
    url = (
        f"http://127.0.0.1:{port}/site/ai-agent-showcase.html"
        "?preview=1&motion=off&orbit=paused"
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        temp_path = Path(tmp.name)

    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={viewport}",
        "--virtual-time-budget=6000",
        f"--screenshot={temp_path}",
        url,
    ]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)  # noqa: S603
    if result.returncode == 0 and temp_path.exists():
        output.parent.mkdir(parents=True, exist_ok=True)
        temp_path.replace(output)
        return 0
    with contextlib.suppress(FileNotFoundError):
        temp_path.unlink()
    return result.returncode or 1


def main() -> int:
    parser = ArgumentParser(
        description="Capture deterministic preview of the interactive observatory."
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output PNG path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Local preview server port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--viewport",
        default=DEFAULT_VIEWPORT,
        help=f"Viewport width,height (default: {DEFAULT_VIEWPORT})",
    )
    args = parser.parse_args()

    output = Path(args.output)
    browser = _find_browser()
    if browser is None:
        print(
            "capture skipped: no supported headless browser found; "
            "keeping last-known-good preview"
        )
        return 0 if output.exists() else 1

    server = _serve_repo(args.port)
    try:
        code = _capture(output, browser=browser, port=args.port, viewport=args.viewport)
    finally:
        server.shutdown()
        server.server_close()

    if code == 0:
        print(f"captured interactive preview: {output}")
        return 0
    print("capture failed; keeping last-known-good preview")
    return 0 if output.exists() else 1


if __name__ == "__main__":
    raise SystemExit(main())
