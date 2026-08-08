# Fountain to HTML Export - Lint Fix Guide

## Overview

This document explains how to fix HTML validation errors in Fountain-generated HTML files to ensure they pass `htmlhint` validation.

## Common Issues

The Fountain to HTML export process (likely BetterFountain) can generate HTML with the following validation issues:

1. **Missing `<title>` tag** - HTML spec requires a title in the head section
2. **Single-quoted attributes** - htmlhint enforces double quotes for attribute values
3. **Duplicate IDs** - The same ID appears on both container and child elements
4. **Unpaired tags** - Extra closing tags (e.g., `</p></p>`)

## Manual Fix Process

### 1. Add Title Tag

Insert a title tag before the closing `</head>`:

```html
</style>
<title>Ego Hygiene - Cover</title>
</head>
```

### 2. Convert Single Quotes to Double Quotes

Change all attribute quotes from single to double:

**Before:**

```html
<body id='fountain-js'>
<section id='workspace' style='display:block;'>
```

**After:**

```html
<body id="fountain-js">
<section id="workspace" style="display:block;">
```

### 3. Remove Duplicate IDs

When an ID appears on both a parent and child element, remove it from the child:

**Before:**

```html
<h3 id="sourceline_5"><span id="sourceline_5">Text</span></h3>
```

**After:**

```html
<h3 id="sourceline_5"><span>Text</span></h3>
```

### 4. Fix Unpaired Tags

Remove extra closing tags:

**Before:**

```html
<span>text</span></p></p>
```

**After:**

```html
<span>text</span></p>
```

## Automated Fix

Use the provided script to automatically fix these issues:

```bash
./scripts/fix_fountain_html.sh editions/edition_1/front_matter/cover/screenplay/cover.front.html
```

The script will:

- Create a backup (.bak file)
- Apply all fixes
- Run htmlhint validation (if installed)

## Validation

After applying fixes, validate with htmlhint:

```bash
npm install -g htmlhint  # Install if needed
htmlhint path/to/file.html
```

**Expected output:**

```bash
Scanned 1 files, no errors found
```

## Prevention

To prevent these issues in future exports:

1. **Configure BetterFountain** (if possible) to:
   - Use double quotes for attributes
   - Add title tags automatically
   - Avoid duplicate IDs

2. **Add to build pipeline:**

   ```bash
   # After Fountain → HTML conversion
   ./scripts/fix_fountain_html.sh generated.html
   ```

3. **CI Integration:**
   Add htmlhint validation to your CI workflow to catch issues early.

## Files Fixed

- `editions/edition_1/front_matter/cover/screenplay/cover.front.html`
  - Added title tag
  - Fixed all attribute quoting
  - Removed duplicate `sourceline_5` ID
  - Fixed unpaired `</p>` tag

## Related Files

- Script: `scripts/fix_fountain_html.sh`
- Valid HTML example: `editions/edition_1/front_matter/cover/exports/cover.front.final.html`
