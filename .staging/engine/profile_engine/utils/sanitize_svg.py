"""
SVG Sanitization Module

This module provides utilities to sanitize SVG files for GitHub compatibility.
It removes invalid attributes, comments, unsafe content, and ensures proper structure.
"""

import re
import sys
from pathlib import Path
from typing import Optional, Tuple
from xml.etree import ElementTree as ET


class SVGSanitizationError(Exception):
    """Raised when SVG sanitization fails."""
    pass


class SVGSanitizer:
    """Sanitize SVG files for GitHub compatibility."""
    
    # Elements that should be removed for security
    FORBIDDEN_ELEMENTS = {
        'script',
        'foreignObject',
    }
    
    # Attributes that should be removed
    FORBIDDEN_ATTRIBUTES = {
        'onload',
        'onclick',
        'onerror',
        'onmouseover',
        'onmouseout',
        'onfocus',
        'onblur',
    }
    
    # Required SVG root attributes
    REQUIRED_ATTRIBUTES = {'xmlns', 'viewBox', 'width', 'height'}
    
    def __init__(self, strict: bool = False):
        """
        Initialize sanitizer.
        
        Args:
            strict: If True, fail on any issues. If False, try to fix issues.
        """
        self.strict = strict
        self.warnings = []
    
    def sanitize_file(self, svg_path: Path, output_path: Optional[Path] = None) -> bool:
        """
        Sanitize an SVG file.
        
        Args:
            svg_path: Path to input SVG file
            output_path: Path to output SVG file (defaults to overwriting input)
            
        Returns:
            True if sanitization was successful
            
        Raises:
            SVGSanitizationError: If sanitization fails in strict mode
        """
        self.warnings = []
        output_path = output_path or svg_path
        
        try:
            # Read and preprocess the SVG content
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if xmlns exists in the original content
            self._has_xmlns_in_original = 'xmlns=' in content
            
            # Remove Python-style comments (e.g., # noqa)
            content = self._remove_python_comments(content)
            
            # Remove XML comments
            content = self._remove_xml_comments(content)
            
            # Parse the SVG
            tree = self._parse_svg(content)
            root = tree.getroot()
            
            # Ensure root is svg element
            if not root.tag.endswith('svg'):
                # Try to find svg element
                svg_elem = root.find('.//{http://www.w3.org/2000/svg}svg')
                if svg_elem is None:
                    svg_elem = root.find('.//svg')
                if svg_elem is not None:
                    root = svg_elem
                else:
                    raise SVGSanitizationError("No SVG root element found")
            
            # Sanitize the SVG
            self._sanitize_element(root)
            
            # Ensure required attributes
            self._ensure_required_attributes(root)
            
            # Write sanitized SVG
            self._write_svg(tree, output_path)
            
            return True
            
        except SVGSanitizationError:
            raise
        except Exception as e:
            error_msg = f"Failed to sanitize {svg_path}: {e}"
            if self.strict:
                raise SVGSanitizationError(error_msg)
            else:
                self.warnings.append(error_msg)
                return False
    
    def _remove_python_comments(self, content: str) -> str:
        """
        Remove Python-style comments from SVG content.
        
        These comments (e.g., # noqa: E501) can appear in SVG attributes
        and cause GitHub to reject the SVG.
        """
        # Remove comments at end of lines within attributes
        # Pattern: anything like # noqa or # type: ignore before closing > or />
        # This handles cases like: <text attr="value"  # noqa>
        pattern = r'\s+#\s*(?:noqa|type:|pylint:|pyright:)[^\n/>]*(?=/?>)'
        content = re.sub(pattern, '', content)
        
        # Also remove standalone Python comments (lines starting with #)
        pattern = r'^\s*#[^\n]*\n'
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        return content
    
    def _remove_xml_comments(self, content: str) -> str:
        """Remove XML/HTML comments from SVG content."""
        # Remove <!-- ... --> comments
        pattern = r'<!--.*?-->'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        return content
    
    def _parse_svg(self, content: str) -> ET.ElementTree:
        """
        Parse SVG content into ElementTree.
        
        Args:
            content: SVG content as string
            
        Returns:
            ElementTree object
            
        Raises:
            SVGSanitizationError: If parsing fails
        """
        try:
            # Register SVG namespace
            ET.register_namespace('', 'http://www.w3.org/2000/svg')
            ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
            
            # Parse the content
            root = ET.fromstring(content)
            return ET.ElementTree(root)
        except ET.ParseError as e:
            raise SVGSanitizationError(f"Invalid XML: {e}")
    
    def _sanitize_element(self, element: ET.Element) -> None:
        """
        Recursively sanitize an SVG element and its children.
        
        Args:
            element: XML element to sanitize
        """
        # Get tag name without namespace
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        
        # Remove forbidden elements
        if tag in self.FORBIDDEN_ELEMENTS:
            self.warnings.append(f"Removed forbidden element: {tag}")
            element.clear()
            return
        
        # Remove forbidden attributes
        attrs_to_remove = []
        for attr in element.attrib:
            attr_name = attr.split('}')[-1] if '}' in attr else attr
            if attr_name in self.FORBIDDEN_ATTRIBUTES:
                attrs_to_remove.append(attr)
                self.warnings.append(f"Removed forbidden attribute: {attr_name}")
        
        for attr in attrs_to_remove:
            del element.attrib[attr]
        
        # Clean element text content (remove Python comments from text)
        if element.text:
            original_text = element.text
            # Remove leading/trailing Python comments from text content
            element.text = re.sub(r'\s*#\s*(?:noqa|type:|pylint:|pyright:)[^\n]*', '', element.text)
            if element.text != original_text and element.text.strip() == '':
                # If text becomes empty after removing comment, set to None
                element.text = None
        
        # Clean tail text (text after element)
        if element.tail:
            element.tail = re.sub(r'\s*#\s*(?:noqa|type:|pylint:|pyright:)[^\n]*', '', element.tail)
        
        # Recursively sanitize children
        for child in list(element):
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag in self.FORBIDDEN_ELEMENTS:
                element.remove(child)
                self.warnings.append(f"Removed forbidden element: {tag}")
            else:
                self._sanitize_element(child)
    
    def _ensure_required_attributes(self, root: ET.Element) -> None:
        """
        Ensure SVG root has required attributes.
        
        Args:
            root: SVG root element
        """
        # Ensure xmlns - only add if it wasn't in the original content
        # ElementTree parsing might not preserve xmlns in attributes,
        # but if it was in the original, it will be written back
        if not self._has_xmlns_in_original:
            has_xmlns = False
            for attr in root.attrib:
                if attr == 'xmlns' or attr.endswith('}xmlns'):
                    has_xmlns = True
                    break
            
            if not has_xmlns:
                root.set('xmlns', 'http://www.w3.org/2000/svg')
                self.warnings.append("Added missing xmlns attribute")
        
        # Check for width, height, viewBox
        has_width = 'width' in root.attrib
        has_height = 'height' in root.attrib
        has_viewbox = 'viewBox' in root.attrib
        
        if not has_viewbox and (has_width and has_height):
            # Create viewBox from width/height
            try:
                width = self._parse_dimension(root.get('width', ''))
                height = self._parse_dimension(root.get('height', ''))
                root.set('viewBox', f'0 0 {width} {height}')
                self.warnings.append(f"Added viewBox from width/height: 0 0 {width} {height}")
            except ValueError:
                pass
        
        if not (has_width or has_height or has_viewbox):
            # No dimensions at all - warn but don't fail
            msg = "SVG is missing width, height, and viewBox attributes"
            self.warnings.append(msg)
            if self.strict:
                raise SVGSanitizationError(msg)
    
    def _parse_dimension(self, value: str) -> float:
        """
        Parse dimension value, stripping units.
        
        Args:
            value: Dimension value (e.g., "800", "800px")
            
        Returns:
            Numeric value
        """
        # Remove units
        value = re.sub(r'(px|pt|em|rem|%)', '', value.strip())
        return float(value)
    
    def _write_svg(self, tree: ET.ElementTree, output_path: Path) -> None:
        """
        Write sanitized SVG to file.
        
        Args:
            tree: ElementTree to write
            output_path: Output file path
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with proper encoding and XML declaration
        tree.write(
            output_path,
            encoding='utf-8',
            xml_declaration=False,  # SVG doesn't need XML declaration
            method='xml'
        )
        
        # Post-process to clean up formatting
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ensure it starts with <svg
        if not content.strip().startswith('<svg'):
            # Add newline before svg if needed
            content = content.strip()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


def sanitize_svg(
    svg_path: Path,
    output_path: Optional[Path] = None,
    strict: bool = False
) -> Tuple[bool, list[str]]:
    """
    Sanitize an SVG file.
    
    Args:
        svg_path: Path to input SVG file
        output_path: Path to output SVG file (defaults to overwriting input)
        strict: If True, fail on any issues. If False, try to fix issues.
        
    Returns:
        Tuple of (success, warnings)
    """
    sanitizer = SVGSanitizer(strict=strict)
    try:
        success = sanitizer.sanitize_file(svg_path, output_path)
        return success, sanitizer.warnings
    except SVGSanitizationError as e:
        if strict:
            raise
        return False, [str(e)]


def sanitize_all_svgs(
    directory: Path,
    pattern: str = "*.svg",
    strict: bool = False
) -> dict[str, Tuple[bool, list[str]]]:
    """
    Sanitize all SVG files in a directory.
    
    Args:
        directory: Directory containing SVG files
        pattern: Glob pattern for SVG files
        strict: If True, fail on any issues. If False, try to fix issues.
        
    Returns:
        Dictionary mapping file paths to (success, warnings) tuples
    """
    results = {}
    svg_files = list(directory.rglob(pattern))
    
    for svg_path in svg_files:
        # Skip files in certain directories
        if any(part in svg_path.parts for part in ['.git', 'node_modules', 'dist', 'logs']):
            continue
        
        success, warnings = sanitize_svg(svg_path, strict=strict)
        results[str(svg_path)] = (success, warnings)
    
    return results


if __name__ == "__main__":
    # Simple CLI for testing
    if len(sys.argv) < 2:
        print("Usage: python sanitize_svg.py <svg_file>")
        sys.exit(1)
    
    svg_path = Path(sys.argv[1])
    if not svg_path.exists():
        print(f"Error: File not found: {svg_path}")
        sys.exit(1)
    
    success, warnings = sanitize_svg(svg_path)
    
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if success:
        print(f"✅ Successfully sanitized {svg_path}")
        sys.exit(0)
    else:
        print(f"❌ Failed to sanitize {svg_path}")
        sys.exit(1)
