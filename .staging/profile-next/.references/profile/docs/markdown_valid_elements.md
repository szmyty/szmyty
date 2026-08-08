# GitHub-Flavored Markdown: Valid HTML Elements Reference

> **Last Updated**: 2025-12-03  
> **Purpose**: Reference guide for HTML elements and attributes supported in GitHub README files

---

## 📋 Overview

GitHub uses a sanitized subset of HTML in Markdown files. This document catalogs which elements, attributes, and patterns are safe to use in README.md files.

---

## ✅ Fully Supported HTML Elements

### Block-Level Elements

#### `<div>`
- **Supported Attributes**: `align`
- **Usage**: Container for grouping and centering content
- **Example**:
  ```html
  <div align="center">
    <h2>Centered Heading</h2>
    <p>Centered paragraph</p>
  </div>
  ```

#### `<p>`
- **Supported Attributes**: `align`
- **Usage**: Paragraph element with optional alignment
- **Example**:
  ```html
  <p align="center">
    This text is centered
  </p>
  ```

#### `<table>`, `<tr>`, `<td>`, `<th>`
- **Supported Attributes**: 
  - `align` (left, center, right)
  - `valign` (top, middle, bottom) - deprecated but functional
  - `width` (percentage or pixels) - deprecated but functional
- **Usage**: Tabular data and layout grids
- **Example**:
  ```html
  <table align="center">
    <tr>
      <td width="50%" align="center">Left</td>
      <td width="50%" align="center">Right</td>
    </tr>
  </table>
  ```

#### `<details>` and `<summary>`
- **Supported Attributes**: None required
- **Usage**: Collapsible sections
- **Example**:
  ```html
  <details>
    <summary>Click to expand</summary>
    Hidden content goes here
  </details>
  ```

### Inline Elements

#### `<img>`
- **Supported Attributes**: `src`, `alt`, `width`, `height`, `align`
- **Usage**: Display images
- **Notes**: 
  - Width can be specified in pixels or percentages
  - Percentage widths work correctly (e.g., `width="100%"`)
  - Supports both absolute and relative paths
- **Example**:
  ```html
  <img src="image.svg" alt="Description" width="100%"/>
  <img src="badge.png" alt="Badge" width="150" height="50"/>
  ```

#### `<a>`
- **Supported Attributes**: `href`, `title`
- **Usage**: Links
- **Example**:
  ```html
  <a href="https://example.com" title="Example Site">Link Text</a>
  ```

#### `<br/>` or `<br>`
- **Supported Attributes**: None
- **Usage**: Line breaks and vertical spacing
- **Example**:
  ```html
  Line one<br/>
  Line two<br/><br/>
  Line three with extra space
  ```

#### `<kbd>`
- **Supported Attributes**: None
- **Usage**: Keyboard input representation
- **Example**:
  ```html
  Press <kbd>Ctrl</kbd> + <kbd>C</kbd> to copy
  ```

#### `<sub>` and `<sup>`
- **Supported Attributes**: None
- **Usage**: Subscript and superscript text
- **Example**:
  ```html
  H<sub>2</sub>O
  x<sup>2</sup> + y<sup>2</sup>
  ```

### Semantic Elements

#### `<code>`
- **Supported Attributes**: None
- **Usage**: Inline code snippets
- **Example**:
  ```html
  Use the <code>git status</code> command
  ```

#### `<pre>`
- **Supported Attributes**: None
- **Usage**: Preformatted text
- **Example**:
  ```html
  <pre>
  Preformatted
  text
  </pre>
  ```

---

## ⚠️ Deprecated but Functional

These HTML5-deprecated elements/attributes still work on GitHub but should be used with caution:

### Attributes

- **`align`** on `<div>`, `<p>`, `<table>`, `<td>`, `<th>`, `<img>`
  - Status: Deprecated in HTML5
  - GitHub: Still fully functional
  - Alternative: None available in GitHub Markdown
  - Recommendation: **Safe to use** - no CSS alternative available

- **`valign`** on `<td>`, `<th>`
  - Status: Deprecated in HTML5
  - GitHub: Still renders correctly
  - Recommendation: Use sparingly, only when necessary

- **`width`** and `height`** on table elements
  - Status: Deprecated in HTML5 for layout
  - GitHub: Still functional
  - Recommendation: Use for images, avoid for layout tables

---

## ❌ Not Supported / Stripped

These elements and attributes are **not supported** by GitHub's HTML sanitizer:

### Elements
- `<style>` - Inline style blocks are completely stripped
- `<script>` - JavaScript is not allowed
- `<iframe>` - Embedded content not allowed
- `<form>`, `<input>`, `<button>` - Form elements not supported
- `<center>` - Deprecated tag, use `<div align="center">` instead
- `<font>` - Use Markdown formatting instead
- `<object>`, `<embed>` - Multimedia elements not supported

### Attributes
- **`style`** - Inline CSS is stripped
- **`class`** - CSS classes are ignored
- **`id`** - IDs may be stripped or modified
- **`onclick`**, **`onload`**, etc. - Event handlers not allowed
- **`data-*`** - Custom data attributes may be stripped

### CSS
- No CSS stylesheets can be included
- No inline styles via `style=""` attribute
- No `<style>` blocks
- Colors, fonts, margins, padding cannot be directly controlled

---

## 🎨 Recommended Layout Patterns

### Pattern 1: Centered Content Block

**Best for**: Major sections, hero content, cards

```html
<div align="center">
  <h2>Section Title</h2>
  <p>Description text</p>
  <img src="image.svg" alt="Image" width="600"/>
</div>
```

### Pattern 2: Centered Image with Caption

**Best for**: Dashboard cards, visualizations

```html
<p align="center">
  <img src="dashboard.svg" alt="Dashboard" width="100%"/>
</p>
```

### Pattern 3: Horizontal Card Layout

**Best for**: Multiple cards side-by-side

```html
<p align="center">
  <img src="card1.svg" alt="Card 1" width="300"/>
  <img src="card2.svg" alt="Card 2" width="300"/>
  <img src="card3.svg" alt="Card 3" width="300"/>
</p>
```

### Pattern 4: Stacked Card Layout

**Best for**: Vertical arrangement of cards

```html
<p align="center">
  <img src="card1.svg" alt="Card 1" width="600"/>
</p>

<br/>

<p align="center">
  <img src="card2.svg" alt="Card 2" width="600"/>
</p>
```

### Pattern 5: Collapsible Section

**Best for**: Hide/show detailed content

```html
<details>
  <summary><b>Click to expand details</b></summary>
  
  ### Detailed Information
  
  More content here...
</details>
```

### Pattern 6: Badge Row

**Best for**: Status indicators, links

```html
<div align="center">

[![Badge 1](badge1.svg)](link1)
[![Badge 2](badge2.svg)](link2)
[![Badge 3](badge3.svg)](link3)

</div>
```

---

## 📏 Spacing Best Practices

### Vertical Spacing

```html
<!-- Small gap -->
<br/>

<!-- Medium gap -->
<br/><br/>

<!-- Large gap (use sparingly) -->
<br/><br/><br/>
```

### Section Dividers

```markdown
<!-- Standard horizontal rule -->
---

<!-- With spacing -->
<br/>

---

<br/>
```

---

## 🌓 Dark Mode Considerations

GitHub automatically handles dark mode for most content:

- ✅ SVG images can include theme-aware styling
- ✅ Markdown text automatically adjusts colors
- ✅ Badges from shields.io have dark mode variants
- ❌ Cannot use CSS to detect dark mode preference
- ❌ Cannot use separate images for light/dark themes directly

**Recommendation**: Design SVGs with colors that work in both themes, or use GitHub's automatic color inversion.

---

## 📱 Mobile Responsiveness

GitHub's mobile view automatically handles:

- ✅ Images scale to fit screen width
- ✅ Tables become scrollable horizontally
- ✅ Text reflows appropriately
- ⚠️ Side-by-side images may stack vertically
- ⚠️ Very wide tables may require horizontal scrolling

**Recommendation**: 
- Use `width="100%"` for full-width images
- Avoid fixed pixel widths where possible
- Test layouts on mobile GitHub app

---

## 🔍 Testing Checklist

Before finalizing README changes, verify:

- [ ] Preview renders correctly on GitHub (push to branch)
- [ ] Desktop view looks clean and professional
- [ ] Mobile view (GitHub mobile app or responsive preview)
- [ ] Dark mode appearance
- [ ] Light mode appearance
- [ ] All images load correctly
- [ ] All links work
- [ ] Collapsible sections expand/collapse
- [ ] Tables render without horizontal scroll (if possible)
- [ ] Spacing is consistent throughout

---

## 📚 Additional Resources

- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
- [GitHub HTML Sanitization](https://github.com/gjtorikian/html-pipeline)
- [CommonMark Spec](https://spec.commonmark.org/)
- [Shields.io Badge Generator](https://shields.io/)

---

## 🔄 Version History

| Date       | Changes                                    |
|------------|-------------------------------------------|
| 2025-12-03 | Initial version - comprehensive HTML audit |

---

*This document serves as the canonical reference for HTML usage in this repository's README.md file.*
