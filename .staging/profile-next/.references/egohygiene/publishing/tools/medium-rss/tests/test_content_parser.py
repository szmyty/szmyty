"""Tests for content_parser.py."""

from __future__ import annotations

import pytest

from medium_rss.content_parser import (
    ArticleImage,
    ParsedArticle,
    parse_article,
    rewrite_image_references,
    _is_tracking_pixel,
)
from bs4 import BeautifulSoup, Tag


# ---------------------------------------------------------------------------
# Tracking pixel detection
# ---------------------------------------------------------------------------


def _make_img_tag(src: str = "", width: str = "", height: str = "", alt: str = "") -> Tag:
    html = f'<img src="{src}" width="{width}" height="{height}" alt="{alt}">'
    soup = BeautifulSoup(html, "lxml")
    tag = soup.find("img")
    assert isinstance(tag, Tag)
    return tag


def test_tracking_pixel_detected_by_url() -> None:
    tag = _make_img_tag(
        src="https://medium.com/_/stat?event=post.clientViewed&postId=abc",
        width="1",
        height="1",
        alt="",
    )
    assert _is_tracking_pixel(tag)


def test_tracking_pixel_detected_by_dimensions() -> None:
    tag = _make_img_tag(src="https://example.com/image.gif", width="1", height="1", alt="")
    assert _is_tracking_pixel(tag)


def test_legitimate_image_not_tracking_pixel() -> None:
    tag = _make_img_tag(
        src="https://cdn-images-1.medium.com/max/1024/1*hero.png",
        width="800",
        height="600",
        alt="Hero image",
    )
    assert not _is_tracking_pixel(tag)


def test_image_without_dimensions_not_tracking_pixel() -> None:
    tag = _make_img_tag(src="https://cdn-images-1.medium.com/max/800/1*photo.jpg", alt="Photo")
    assert not _is_tracking_pixel(tag)


# ---------------------------------------------------------------------------
# parse_article
# ---------------------------------------------------------------------------

_SAMPLE_HTML = """
<h2>Mood Colors Your Reality</h2>
<p>Your mood is a <em>rendering condition</em>.</p>
<figure>
  <img src="https://cdn-images-1.medium.com/max/1024/1*hero.png" alt="Hero image"/>
  <figcaption>The mood as a rendering lens</figcaption>
</figure>
<blockquote>Perception is filtered through emotional state.</blockquote>
<img src="https://medium.com/_/stat?event=post.clientViewed&amp;postId=f284b362c931" width="1" height="1" alt="">
"""


def test_parse_article_returns_clean_html() -> None:
    result = parse_article(_SAMPLE_HTML)
    assert isinstance(result, ParsedArticle)
    assert result.clean_html


def test_parse_article_removes_tracking_pixels() -> None:
    result = parse_article(_SAMPLE_HTML)
    assert "medium.com/_/stat" not in result.clean_html


def test_parse_article_preserves_legitimate_images() -> None:
    result = parse_article(_SAMPLE_HTML)
    assert "cdn-images-1.medium.com/max/1024/1*hero.png" in result.clean_html


def test_parse_article_extracts_images() -> None:
    result = parse_article(_SAMPLE_HTML)
    assert len(result.images) == 1
    assert result.images[0].src == "https://cdn-images-1.medium.com/max/1024/1*hero.png"


def test_parse_article_preserves_alt_text() -> None:
    result = parse_article(_SAMPLE_HTML)
    assert result.images[0].alt == "Hero image"


def test_parse_article_preserves_figure_caption() -> None:
    result = parse_article(_SAMPLE_HTML)
    assert result.images[0].caption == "The mood as a rendering lens"


def test_parse_article_empty_html() -> None:
    result = parse_article("")
    assert result.clean_html == ""
    assert result.images == []


def test_parse_article_no_tracking_pixels_when_none_present() -> None:
    html = "<p>Just text.</p>"
    result = parse_article(html)
    assert result.images == []


def test_parse_article_deduplicates_images() -> None:
    html = """
    <img src="https://cdn-images-1.medium.com/max/800/1*photo.jpg" alt="A"/>
    <img src="https://cdn-images-1.medium.com/max/800/1*photo.jpg" alt="A"/>
    """
    result = parse_article(html)
    assert len(result.images) == 1


# ---------------------------------------------------------------------------
# rewrite_image_references
# ---------------------------------------------------------------------------


def test_rewrite_image_references() -> None:
    html = '<img src="https://cdn-images-1.medium.com/max/800/1*photo.jpg" alt="Photo"/>'
    images = [
        ArticleImage(
            src="https://cdn-images-1.medium.com/max/800/1*photo.jpg",
            alt="Photo",
            caption="",
            local_path="publishing/medium/articles/test/assets/photo-abc12345.jpg",
        )
    ]
    result = rewrite_image_references(html, images)
    assert "publishing/medium/articles/test/assets/photo-abc12345.jpg" in result
    assert "cdn-images-1.medium.com" not in result


def test_rewrite_image_references_skips_undownloaded() -> None:
    html = '<img src="https://cdn-images-1.medium.com/max/800/1*photo.jpg" alt="Photo"/>'
    images = [
        ArticleImage(
            src="https://cdn-images-1.medium.com/max/800/1*photo.jpg",
            alt="Photo",
            caption="",
            local_path="",  # not downloaded
        )
    ]
    result = rewrite_image_references(html, images)
    # URL should remain untouched when local_path is empty
    assert "cdn-images-1.medium.com/max/800/1*photo.jpg" in result
