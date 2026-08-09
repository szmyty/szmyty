#!/usr/bin/env python3
"""Tests for the lint-markdown-images script."""

import sys
from pathlib import Path

# Add scripts directory to Python path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

# Import after path is set
import importlib.util
spec = importlib.util.spec_from_file_location(
    "lint_markdown_images",
    scripts_dir / "lint-markdown-images.py"
)
lint_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint_module)
find_markdown_images_in_html = lint_module.find_markdown_images_in_html


def test_no_html_blocks():
    """Test markdown with no HTML blocks."""
    content = """# Header

![Image](image.svg)

Some text.
"""
    issues = find_markdown_images_in_html(content, "test.md")
    assert len(issues) == 0


def test_markdown_image_in_div():
    """Test markdown image inside div block (should be detected)."""
    content = """<div align="center">

![Card Image](./card.svg)

</div>"""
    issues = find_markdown_images_in_html(content, "test.md")
    assert len(issues) == 1
    assert "Card Image" in issues[0][1]


def test_markdown_image_in_p_tag():
    """Test markdown image inside p tag (should be detected)."""
    content = """<p align="center">
![Location Card](./location.svg)
</p>"""
    issues = find_markdown_images_in_html(content, "test.md")
    assert len(issues) == 1
    assert "Location Card" in issues[0][1]


def test_badge_excluded():
    """Test that shields.io badges are excluded."""
    content = """<div align="center">

![Build](https://img.shields.io/badge/build-passing-green)

</div>"""
    issues = find_markdown_images_in_html(content, "test.md")
    assert len(issues) == 0


def test_komarev_badge_excluded():
    """Test that komarev badges are excluded."""
    content = """<div align="center">

![Views](https://komarev.com/ghpvc/?username=test)

</div>"""
    issues = find_markdown_images_in_html(content, "test.md")
    assert len(issues) == 0


def test_workflow_badge_excluded():
    """Test that workflow badge.svg images are excluded."""
    content = """<div align="center">

![Workflow](https://github.com/user/repo/badge.svg)

</div>"""
    issues = find_markdown_images_in_html(content, "test.md")
    assert len(issues) == 0


def test_html_img_tag_not_detected():
    """Test that HTML img tags are not detected as issues."""
    content = """<div align="center">

<img src="./card.svg" alt="Card" width="100%"/>

</div>"""
    issues = find_markdown_images_in_html(content, "test.md")
    assert len(issues) == 0


def test_multiple_images_in_same_block():
    """Test multiple markdown images in the same HTML block."""
    content = """<div align="center">

![Image 1](./image1.svg)
![Image 2](./image2.svg)

</div>"""
    issues = find_markdown_images_in_html(content, "test.md")
    assert len(issues) == 2


def test_nested_html_blocks():
    """Test nested HTML blocks with markdown images."""
    content = """<div align="center">
<section>

![Card](./card.svg)

</section>
</div>"""
    issues = find_markdown_images_in_html(content, "test.md")
    # Should detect the image inside the section
    assert len(issues) >= 1


def test_markdown_image_outside_html():
    """Test markdown image outside HTML blocks (should not be detected)."""
    content = """# Header

![Image outside](./image.svg)

<div align="center">

Some text without images.

</div>

![Another image outside](./another.svg)
"""
    issues = find_markdown_images_in_html(content, "test.md")
    assert len(issues) == 0
