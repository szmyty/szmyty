"""Tests for SVG sanitization module."""

import tempfile
from pathlib import Path

import pytest

from profile_engine.utils.sanitize_svg import (
    SVGSanitizationError,
    SVGSanitizer,
    sanitize_all_svgs,
    sanitize_svg,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_remove_python_comments(temp_dir):
    """Test removal of Python-style comments like # noqa."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <text font-size="12" fill="#000"  # noqa: E501>Test</text>
    <rect width="50" height="50"  # type: ignore />
</svg>'''
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    success, warnings = sanitize_svg(svg_path)
    
    assert success
    result_content = svg_path.read_text()
    assert "# noqa" not in result_content
    assert "# type:" not in result_content
    assert "<text" in result_content
    assert "<rect" in result_content


def test_remove_xml_comments(temp_dir):
    """Test removal of XML/HTML comments."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <!-- This is a comment -->
    <rect width="50" height="50" />
    <!-- Another comment -->
</svg>'''
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    success, warnings = sanitize_svg(svg_path)
    
    assert success
    result_content = svg_path.read_text()
    assert "<!--" not in result_content
    assert "-->" not in result_content
    assert "<rect" in result_content


def test_remove_script_tags(temp_dir):
    """Test removal of script tags."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <script>alert('XSS')</script>
    <rect width="50" height="50" />
</svg>'''
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    success, warnings = sanitize_svg(svg_path)
    
    assert success
    assert any("script" in w.lower() for w in warnings)
    result_content = svg_path.read_text()
    assert "<script" not in result_content
    assert "alert" not in result_content


def test_remove_foreign_object(temp_dir):
    """Test removal of foreignObject tags."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <foreignObject width="100" height="100">
        <div>HTML content</div>
    </foreignObject>
    <rect width="50" height="50" />
</svg>'''
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    success, warnings = sanitize_svg(svg_path)
    
    assert success
    assert any("foreignobject" in w.lower() for w in warnings)
    result_content = svg_path.read_text()
    assert "foreignObject" not in result_content
    assert "<rect" in result_content


def test_remove_event_handlers(temp_dir):
    """Test removal of event handler attributes."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <rect width="50" height="50" onclick="alert('XSS')" onload="doEvil()" />
</svg>'''
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    success, warnings = sanitize_svg(svg_path)
    
    assert success
    assert any("onclick" in w.lower() for w in warnings)
    assert any("onload" in w.lower() for w in warnings)
    result_content = svg_path.read_text()
    assert "onclick" not in result_content
    assert "onload" not in result_content
    assert "alert" not in result_content


def test_preserve_valid_styling(temp_dir):
    """Test that valid styling is preserved."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <defs>
        <linearGradient id="grad1">
            <stop offset="0%" style="stop-color:rgb(255,255,0);stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="50" height="50" fill="url(#grad1)" stroke="#000" stroke-width="2" />
    <text font-family="Arial" font-size="12" fill="#000">Test</text>
</svg>'''
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    success, warnings = sanitize_svg(svg_path)
    
    assert success
    result_content = svg_path.read_text()
    assert "linearGradient" in result_content
    assert "stop-color" in result_content
    assert 'fill="url(#grad1)"' in result_content
    assert "stroke" in result_content
    assert "font-family" in result_content


def test_add_missing_xmlns(temp_dir):
    """Test that missing xmlns attribute is added."""
    svg_content = '<svg width="100" height="100" viewBox="0 0 100 100"><rect width="50" height="50" /></svg>'
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    success, warnings = sanitize_svg(svg_path)
    
    assert success
    assert any("xmlns" in w.lower() for w in warnings)
    result_content = svg_path.read_text()
    assert 'xmlns="http://www.w3.org/2000/svg"' in result_content


def test_add_viewbox_from_dimensions(temp_dir):
    """Test that viewBox is created from width/height if missing."""
    svg_content = '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150"><rect width="50" height="50" /></svg>'
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    success, warnings = sanitize_svg(svg_path)
    
    assert success
    result_content = svg_path.read_text()
    assert 'viewBox="0 0 200 150"' in result_content or 'viewBox="0 0 200.0 150.0"' in result_content


def test_handle_malformed_xml(temp_dir):
    """Test handling of malformed XML."""
    svg_content = '<svg><rect width="50" height="50"</svg>'  # Missing closing >
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    # In non-strict mode, it should return False but not raise
    success, warnings = sanitize_svg(svg_path, strict=False)
    assert not success
    assert len(warnings) > 0
    
    # In strict mode, it should raise
    with pytest.raises(SVGSanitizationError):
        sanitize_svg(svg_path, strict=True)


def test_sanitize_with_output_path(temp_dir):
    """Test sanitizing to a different output file."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <text fill="#000"  # noqa>Test</text>
</svg>'''
    
    input_path = temp_dir / "input.svg"
    output_path = temp_dir / "output.svg"
    
    input_path.write_text(svg_content)
    
    success, warnings = sanitize_svg(input_path, output_path)
    
    assert success
    assert output_path.exists()
    
    # Input should be unchanged
    assert "# noqa" in input_path.read_text()
    
    # Output should be sanitized
    assert "# noqa" not in output_path.read_text()


def test_sanitize_all_svgs(temp_dir):
    """Test sanitizing multiple SVG files."""
    # Create test SVG files
    for i in range(3):
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <text fill="#000"  # noqa>Test {i}</text>
</svg>'''
        (temp_dir / f"test{i}.svg").write_text(svg_content)
    
    # Create a non-SVG file
    (temp_dir / "test.txt").write_text("Not an SVG")
    
    results = sanitize_all_svgs(temp_dir)
    
    # Should have processed 3 SVG files
    assert len(results) == 3
    
    # All should succeed
    for success, warnings in results.values():
        assert success


def test_sanitize_all_with_subdirectories(temp_dir):
    """Test sanitizing SVG files in subdirectories."""
    # Create subdirectory
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    
    # Create SVG files
    svg_content = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="50" height="50" /></svg>'
    
    (temp_dir / "root.svg").write_text(svg_content)
    (subdir / "sub.svg").write_text(svg_content)
    
    results = sanitize_all_svgs(temp_dir)
    
    # Should find both files
    assert len(results) == 2


def test_skip_excluded_directories(temp_dir):
    """Test that certain directories are skipped."""
    # Create directories that should be skipped
    for dirname in ["node_modules", ".git", "dist", "logs"]:
        excluded_dir = temp_dir / dirname
        excluded_dir.mkdir()
        (excluded_dir / "test.svg").write_text('<svg></svg>')
    
    # Create a regular SVG
    svg_content = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="50" height="50" /></svg>'
    (temp_dir / "regular.svg").write_text(svg_content)
    
    results = sanitize_all_svgs(temp_dir)
    
    # Should only process the regular SVG
    assert len(results) == 1
    assert any("regular.svg" in path for path in results.keys())


def test_sanitizer_class_direct(temp_dir):
    """Test using SVGSanitizer class directly."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <text fill="#000"  # noqa>Test</text>
</svg>'''
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    sanitizer = SVGSanitizer(strict=False)
    success = sanitizer.sanitize_file(svg_path)
    
    assert success
    assert len(sanitizer.warnings) >= 0
    
    result_content = svg_path.read_text()
    assert "# noqa" not in result_content


def test_complex_svg_with_multiple_issues(temp_dir):
    """Test SVG with multiple issues that need fixing."""
    svg_content = '''<svg width="800" height="400">
    <!-- Comment -->
    <script>alert('xss')</script>
    <text fill="#000"  # noqa: E501>Title</text>
    <rect onclick="doEvil()" width="100" height="100" />
    <foreignObject><div>HTML</div></foreignObject>
</svg>'''
    
    svg_path = temp_dir / "test.svg"
    svg_path.write_text(svg_content)
    
    success, warnings = sanitize_svg(svg_path)
    
    assert success
    assert len(warnings) > 0
    
    result_content = svg_path.read_text()
    # Should have xmlns
    assert 'xmlns="http://www.w3.org/2000/svg"' in result_content
    # Should have viewBox
    assert 'viewBox="0 0 800 400"' in result_content or 'viewBox="0 0 800.0 400.0"' in result_content
    # Should not have dangerous content
    assert "<!--" not in result_content
    assert "<script" not in result_content
    assert "# noqa" not in result_content
    assert "onclick" not in result_content
    assert "foreignObject" not in result_content
    # Should preserve safe content
    assert "<text" in result_content
    assert "<rect" in result_content
