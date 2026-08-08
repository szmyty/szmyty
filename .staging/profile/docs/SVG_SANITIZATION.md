# SVG Sanitization

## Overview

The Profile Engine includes a comprehensive SVG sanitization system that ensures all generated SVG files are compatible with GitHub's SVG renderer. This prevents broken or invisible cards in your GitHub profile README.

## Why Sanitization is Needed

GitHub's SVG sanitizer silently refuses to display SVG images that contain:

- **Python-style comments** (e.g., `# noqa: E501`, `# type: ignore`)
- **JavaScript code** (e.g., `<script>` tags, event handlers)
- **Embedded HTML** (e.g., `<foreignObject>` elements)
- **Missing required attributes** (e.g., `xmlns`, `viewBox`)
- **XML comments** that may contain sensitive information

Without sanitization, these issues can cause:
- ❌ Cards not displaying in your README
- ❌ Broken visualizations on GitHub Pages
- ❌ Security vulnerabilities from XSS attacks
- ❌ Confusing debugging when cards work locally but not on GitHub

## Features

The SVG sanitizer automatically:

✅ **Removes Python comments** from attributes and text content  
✅ **Strips XML/HTML comments** for cleaner output  
✅ **Removes dangerous elements** (`<script>`, `<foreignObject>`)  
✅ **Removes event handlers** (`onclick`, `onload`, etc.)  
✅ **Adds missing attributes** (`xmlns`, `viewBox`)  
✅ **Preserves valid styling** (gradients, filters, transforms)  
✅ **Handles malformed XML** gracefully  

## Rules Enforced

### Forbidden Elements

The following elements are removed entirely:

- `<script>` - JavaScript code execution
- `<foreignObject>` - Embedded HTML/XHTML content

### Forbidden Attributes

The following attributes are removed from all elements:

- `onload` - JavaScript event handler
- `onclick` - JavaScript event handler
- `onerror` - JavaScript event handler
- `onmouseover` - JavaScript event handler
- `onmouseout` - JavaScript event handler
- `onfocus` - JavaScript event handler
- `onblur` - JavaScript event handler

### Required Attributes

The root `<svg>` element must have:

- `xmlns="http://www.w3.org/2000/svg"` - SVG namespace declaration
- `viewBox` or (`width` and `height`) - Viewport dimensions

If `viewBox` is missing but `width` and `height` are present, the sanitizer will automatically create a `viewBox` from those dimensions.

### Comments

All comments are removed:

- XML comments: `<!-- comment -->`
- Python-style comments: `# noqa: E501`, `# type: ignore`, etc.

Python comments are particularly problematic because they can appear:
- In attribute values: `<text fill="#fff"  # noqa>Text</text>`
- In text content: `<text># noqa\nActual text</text>`
- On standalone lines

## Usage

### Command-Line Interface

#### Sanitize a Single SVG File

```bash
profile-engine sanitize svg path/to/file.svg
```

With output to a different file:

```bash
profile-engine sanitize svg input.svg --output output.svg
```

In strict mode (fail on any issues instead of trying to fix):

```bash
profile-engine sanitize svg file.svg --strict
```

#### Sanitize All SVG Files

Sanitize all SVG files in the current directory and subdirectories:

```bash
profile-engine sanitize all
```

Sanitize SVG files in a specific directory:

```bash
profile-engine sanitize all --directory /path/to/svgs
```

With a custom pattern:

```bash
profile-engine sanitize all --pattern "dashboard*.svg"
```

### Python API

```python
from pathlib import Path
from profile_engine.utils.sanitize_svg import sanitize_svg, sanitize_all_svgs

# Sanitize a single file
success, warnings = sanitize_svg(Path("card.svg"))
if success:
    print("✅ Sanitized successfully")
for warning in warnings:
    print(f"⚠️  {warning}")

# Sanitize all SVGs in a directory
results = sanitize_all_svgs(Path("."), pattern="*.svg")
for svg_path, (success, warnings) in results.items():
    if success:
        print(f"✅ {svg_path}")
    else:
        print(f"❌ {svg_path}")
        for warning in warnings:
            print(f"   ⚠️  {warning}")
```

### In GitHub Actions Workflows

Add this step after generating SVG cards and before committing:

```yaml
- name: 🧹 Sanitize all generated SVG files
  run: |
    profile-engine sanitize all
  continue-on-error: false
```

Or sanitize specific files:

```yaml
- name: 🧹 Sanitize dashboard SVG
  run: |
    profile-engine sanitize svg dashboard.svg
    profile-engine sanitize svg summary-weekly.svg
    profile-engine sanitize svg summary-monthly.svg
```

## Common Issues and Solutions

### Issue: SVG displays locally but not on GitHub

**Cause**: The SVG likely contains Python comments or other content that GitHub's sanitizer rejects.

**Solution**: Run `profile-engine sanitize svg your-file.svg` to clean it.

### Issue: "Invalid XML: duplicate attribute"

**Cause**: The SVG has duplicate attributes (often happens with `xmlns`).

**Solution**: The sanitizer will detect and report this. Check the original SVG generation code and ensure attributes are not duplicated.

### Issue: SVG text displays ` # noqa` in the rendered card

**Cause**: Python linter comments were included in the text content of SVG elements.

**Solution**: The sanitizer removes these from both attributes and text content. Run `profile-engine sanitize all`.

### Issue: Sanitization fails with "mismatched tag" error

**Cause**: The SVG has malformed XML (e.g., unclosed tags, incorrect nesting).

**Solution**: 
1. Fix the SVG generation code to produce valid XML
2. Use an XML validator to identify the specific issue
3. In non-strict mode, the sanitizer will report the error without failing

### Issue: Gradients or filters are removed

**Cause**: This should NOT happen - the sanitizer preserves all valid SVG styling.

**Solution**: If this occurs, please report it as a bug. The sanitizer only removes dangerous content, not valid SVG features.

## Excluded Directories

The `sanitize all` command automatically skips SVG files in:

- `.git/` - Version control
- `node_modules/` - Dependencies
- `dist/` - Build output
- `logs/` - Log files

## Best Practices

1. **Run sanitization in CI/CD**: Add the sanitization step to your GitHub Actions workflow to ensure all SVGs are cleaned before committing.

2. **Fix generation code**: If you see repeated warnings about the same issues, fix the source generation code rather than relying on sanitization.

3. **Use strict mode in development**: When testing locally, use `--strict` mode to catch issues early:
   ```bash
   profile-engine sanitize all --strict
   ```

4. **Review warnings**: The sanitizer reports all changes it makes. Review these warnings to understand what was cleaned.

5. **Test on GitHub**: After sanitizing, commit and verify that your SVGs display correctly on GitHub.

## Technical Details

### Implementation

The sanitizer uses Python's built-in `xml.etree.ElementTree` parser with:

- Namespace-aware parsing for SVG and XLink namespaces
- Regex-based pre-processing to remove comments before parsing
- Recursive tree traversal to clean all elements
- Post-processing to ensure proper XML formatting

### Limitations

- **Namespace handling**: ElementTree may not preserve all namespace prefixes exactly as written
- **Formatting**: The sanitizer may reformat whitespace and tag closures
- **CDATA sections**: Not specifically handled (rarely needed in SVG)
- **Entity references**: Standard XML entities are preserved, custom entities may cause issues

### Performance

Sanitization is fast:
- Single SVG: ~10-50ms
- 20-30 SVGs: ~200-500ms

Safe to run in CI/CD without significant overhead.

## Troubleshooting

### Enable verbose output

```bash
profile-engine sanitize svg file.svg --strict
```

This will show all warnings and fail immediately on errors.

### Validate XML separately

```bash
xmllint --noout file.svg
```

### Check for Python comments

```bash
grep -n "# noqa\|# type:" file.svg
```

### Test GitHub rendering

After sanitizing, commit the SVG and view it on GitHub:
```
https://github.com/username/repo/blob/main/path/to/file.svg
```

## Future Enhancements

Planned improvements:

- [ ] Schema validation against SVG specification
- [ ] Configurable rules via config file
- [ ] Automatic fallback card generation on failure
- [ ] Support for SVG 2.0 features
- [ ] CSS sanitization within `<style>` blocks

## Related Documentation

- [GitHub's SVG Sanitizer](https://github.com/github/markup#sanitization)
- [SVG Specification](https://www.w3.org/TR/SVG2/)
- [Profile Engine CLI](../engine/README.md)

## Support

If you encounter issues with SVG sanitization:

1. Check this documentation
2. Review the warnings from the sanitizer
3. Validate your SVG with an XML validator
4. Open an issue on GitHub with the SVG file and error message
