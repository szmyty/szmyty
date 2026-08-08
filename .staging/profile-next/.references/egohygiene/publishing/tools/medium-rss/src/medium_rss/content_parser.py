"""HTML content parsing, cleanup, and asset extraction for Medium articles."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import structlog
from bs4 import BeautifulSoup, Tag

log = structlog.get_logger(__name__)

# Medium tracking pixel pattern – 1×1 images served from medium.com/_/stat
_TRACKING_URL_RE = re.compile(
    r"https?://medium\.com/_/stat", re.IGNORECASE
)

# Image dimensions that indicate a tracking pixel (width=1 height=1)
_TRACKING_DIMENSION = "1"


@dataclass
class ArticleImage:
    """An image found inside article HTML."""

    src: str
    alt: str
    caption: str
    # Relative path to the locally downloaded file (set after download)
    local_path: str = ""


@dataclass
class ParsedArticle:
    """Result of parsing and cleaning article HTML."""

    clean_html: str
    images: list[ArticleImage] = field(default_factory=list)


def parse_article(html: str) -> ParsedArticle:
    """Clean Medium article HTML and extract image assets.

    - Removes Medium tracking pixels and analytics images
    - Removes empty elements that add no content
    - Preserves figures, captions, alt text, and legitimate images
    - Returns the cleaned HTML and a list of discovered images
    """
    if not html:
        return ParsedArticle(clean_html="", images=[])

    soup = BeautifulSoup(html, "lxml")

    # Remove tracking pixels first
    _remove_tracking_pixels(soup)

    # Extract article images (after tracking pixel removal)
    images = _extract_images(soup)

    # Remove empty elements (wrappers with no text or images)
    _remove_empty_elements(soup)

    clean_html = str(soup)

    log.debug("content_parser.parsed", image_count=len(images))
    return ParsedArticle(clean_html=clean_html, images=images)


def rewrite_image_references(
    html: str, images: list[ArticleImage]
) -> str:
    """Rewrite image src attributes in HTML to use local asset paths."""
    soup = BeautifulSoup(html, "lxml")
    url_to_local = {img.src: img.local_path for img in images if img.local_path}

    for tag in soup.find_all("img"):
        if not isinstance(tag, Tag):
            continue
        src = tag.get("src", "")
        if src and src in url_to_local:
            tag["src"] = url_to_local[src]

    return str(soup)


def _is_tracking_pixel(tag: Tag) -> bool:
    """Return True when the img tag is a Medium tracking pixel."""
    src = tag.get("src", "")
    if isinstance(src, str) and _TRACKING_URL_RE.search(src):
        return True

    # Also check by dimensions: 1×1 invisible images
    width = tag.get("width", "")
    height = tag.get("height", "")
    alt = tag.get("alt", "")
    if (
        str(width) == _TRACKING_DIMENSION
        and str(height) == _TRACKING_DIMENSION
        and alt == ""
    ):
        return True

    return False


def _remove_tracking_pixels(soup: BeautifulSoup) -> None:
    """Remove Medium tracking pixel images from the soup in place."""
    for tag in soup.find_all("img"):
        if isinstance(tag, Tag) and _is_tracking_pixel(tag):
            log.debug("content_parser.tracking_pixel_removed", src=tag.get("src", ""))
            # Remove the parent <figure> if this is the only child, else just the img
            parent = tag.parent
            tag.decompose()
            if parent and parent.name in ("figure", "p") and not parent.get_text(strip=True):
                parent.decompose()


def _extract_images(soup: BeautifulSoup) -> list[ArticleImage]:
    """Collect all non-tracking images from the article HTML."""
    images: list[ArticleImage] = []
    seen_srcs: set[str] = set()

    for tag in soup.find_all("img"):
        if not isinstance(tag, Tag):
            continue
        src = tag.get("src", "")
        if not src or not isinstance(src, str):
            continue
        if src in seen_srcs:
            continue
        seen_srcs.add(src)

        alt = tag.get("alt", "") or ""
        caption = _extract_caption(tag)

        images.append(ArticleImage(src=src, alt=str(alt), caption=caption))

    return images


def _extract_caption(img_tag: Tag) -> str:
    """Return figure caption text associated with an img tag, if any."""
    parent = img_tag.parent
    if parent and parent.name == "figure":
        figcaption = parent.find("figcaption")
        if figcaption:
            return figcaption.get_text(strip=True)
    return ""


def _remove_empty_elements(soup: BeautifulSoup) -> None:
    """Remove block elements that contain no visible text or images."""
    for tag in soup.find_all(["p", "div", "section"]):
        if not isinstance(tag, Tag):
            continue
        if not tag.get_text(strip=True) and not tag.find("img"):
            tag.decompose()
