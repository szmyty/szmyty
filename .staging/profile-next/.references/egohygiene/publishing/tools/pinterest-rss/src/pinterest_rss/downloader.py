"""Image downloader with retry, content-type detection, and atomic write."""

from __future__ import annotations

import mimetypes
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import httpx
import structlog
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

log = structlog.get_logger(__name__)

_DEFAULT_TIMEOUT = 30.0
_DEFAULT_RETRIES = 3
_USER_AGENT = "EgoHygiene-PinterestRSS/0.1 (+https://github.com/egohygiene/egohygiene)"

_MIME_TO_EXT: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/avif": ".avif",
    "image/tiff": ".tiff",
}


def download_image(
    url: str,
    dest_dir: Path,
    timeout: float = _DEFAULT_TIMEOUT,
    max_retries: int = _DEFAULT_RETRIES,
) -> Path | None:
    """Download an image from *url* into *dest_dir*.

    Returns the local ``Path`` on success, or ``None`` on failure.
    The filename is derived from the URL path and content-type header.
    """
    if not url:
        return None

    dest_dir.mkdir(parents=True, exist_ok=True)

    try:
        return _download_with_retry(url, dest_dir, timeout, max_retries)
    except RetryError as exc:
        log.warning("downloader.failed_after_retries", url=url, exc=str(exc))
        return None
    except Exception as exc:
        log.warning("downloader.failed", url=url, exc=str(exc))
        return None


@retry(
    retry=retry_if_exception_type(httpx.TransportError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=False,
)
def _download_with_retry(
    url: str, dest_dir: Path, timeout: float, max_retries: int
) -> Path:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": _USER_AGENT})
        response.raise_for_status()

    content_type = response.headers.get("content-type", "").split(";")[0].strip()
    ext = _resolve_extension(content_type, url)
    filename = f"image{ext}"
    dest = dest_dir / filename

    _atomic_write(dest, response.content)
    log.debug(
        "downloader.ok",
        url=url,
        dest=str(dest),
        content_type=content_type,
        size=len(response.content),
    )
    return dest


_KNOWN_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif", ".tiff"}


def _resolve_extension(content_type: str, url: str) -> str:
    """Determine file extension from content-type header, falling back to URL path."""
    if content_type in _MIME_TO_EXT:
        return _MIME_TO_EXT[content_type]

    # Try guessing from content-type via mimetypes – only accept image extensions
    ext = mimetypes.guess_extension(content_type)
    if ext and ext in _KNOWN_IMAGE_EXTS:
        return ext if ext != ".jpeg" else ".jpg"

    # Fallback: derive from URL path
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix in _KNOWN_IMAGE_EXTS:
        return suffix if suffix != ".jpeg" else ".jpg"

    return ".jpg"


def _atomic_write(path: Path, data: bytes) -> None:
    dir_ = path.parent
    dir_.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_, prefix=".img-download-")
    try:
        os.write(fd, data)
        os.close(fd)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
