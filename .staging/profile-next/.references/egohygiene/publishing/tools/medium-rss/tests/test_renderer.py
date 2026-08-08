"""Tests for renderer.py."""

from __future__ import annotations

import pytest

from medium_rss.renderer import render_markdown


def test_render_markdown_produces_output() -> None:
    html = "<h2>Hello World</h2><p>A paragraph.</p>"
    md = render_markdown(html)
    assert md
    assert "Hello World" in md
    assert "A paragraph" in md


def test_render_markdown_converts_headings() -> None:
    html = "<h2>Section Title</h2>"
    md = render_markdown(html)
    assert "## Section Title" in md


def test_render_markdown_converts_emphasis() -> None:
    html = "<p>This is <em>important</em>.</p>"
    md = render_markdown(html)
    assert "*important*" in md or "_important_" in md


def test_render_markdown_converts_blockquote() -> None:
    html = "<blockquote>A deep thought.</blockquote>"
    md = render_markdown(html)
    assert ">" in md
    assert "A deep thought" in md


def test_render_markdown_converts_link() -> None:
    html = '<p>See <a href="https://example.com">this</a>.</p>'
    md = render_markdown(html)
    assert "[this](https://example.com)" in md


def test_render_markdown_converts_image() -> None:
    html = '<img src="assets/photo.jpg" alt="A photo"/>'
    md = render_markdown(html)
    assert "A photo" in md
    assert "assets/photo.jpg" in md


def test_render_markdown_empty_html() -> None:
    md = render_markdown("")
    assert md == ""


def test_render_markdown_ends_with_newline() -> None:
    html = "<p>Text.</p>"
    md = render_markdown(html)
    assert md.endswith("\n")


def test_render_markdown_collapses_blank_lines() -> None:
    html = "<p>One</p><p>Two</p>"
    md = render_markdown(html)
    # Should not have more than two consecutive blank lines
    assert "\n\n\n" not in md


def test_render_markdown_unordered_list() -> None:
    html = "<ul><li>Item one</li><li>Item two</li></ul>"
    md = render_markdown(html)
    assert "Item one" in md
    assert "Item two" in md


def test_render_markdown_preserves_strong() -> None:
    html = "<p>This is <strong>very</strong> important.</p>"
    md = render_markdown(html)
    assert "very" in md
