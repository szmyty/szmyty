# Asset Generation Briefs — Alan Szmyt Profile

**Document type:** Implementation record and regeneration brief
**Status:** Profile Done v1 banners implemented
**Last updated:** 2026-08-21

> **Note:** Legacy branding concepts are historical references only. Do not
> promote old drafts directly. The briefs below define the final target.

---

## Brief 1 — Hero Banner (Light Theme)

**Output file:** `assets/profile/banner-light.svg`
**Dimensions:** 1280 × 400 px (16 : 5 aspect ratio)
**Format:** SVG (preferred) or PNG at ≥ 2× resolution, then traced to SVG
**Max file size:** 120 KB

### Composition

Horizontal panoramic systems map. Three signal rails enter from each side and
converge through a continuous central orbit. Evidence nodes, constellation
fragments, a quiet grid, and restrained cosmic glows connect engineering,
research, local-first tools, and creative technology without embedded text.

### Subject-Safe Zone

Critical focal content must stay within the safe zone:
`x: 240–1040 px, y: 60–340 px`

GitHub crops the banner to approximately 16 : 5 on desktop and may crop
further on mobile. Keep the subject and any key visual accents within the safe
zone.

### Palette (Light Theme)

- Background sky: `#f0f4ff` fading to `#dde7f8`
- Star points: white or pale `#aac8ff` on soft background
- Signal accents: pink, violet, and cyan
- Grid and evidence nodes: slate/violet at low opacity

### Contrast

All meaningful visual elements must maintain ≥ 3 : 1 contrast against the
background. Text (if any) must meet ≥ 4.5 : 1. **No critical information
should appear as text inside the image.**

### Text-Free Variant

The banner must read as intentional and complete with **no embedded text**.
Identity text (name, role) is supplied by the Markdown heading immediately
below the `<picture>` block in `README.md`.

### Negative Constraints

- No photorealistic faces, portraits, or human figures.
- No stock clipart or recognizable third-party brand marks.
- No dark overlay that obscures more than 10 % of the canvas.
- No JavaScript, external URL references, or `<script>` elements in SVG.
- No text elements inside the banner SVG.
- Motion must be optional and wrapped in
  `@media (prefers-reduced-motion: no-preference)`.

### Required Outputs

1. `banner-light.svg` — implemented light-theme variant.
2. A brief description of the scene for the alt-text record.

---

## Brief 2 — Hero Banner (Dark Theme)

**Output file:** `assets/profile/banner-dark.svg`
**Dimensions:** 1280 × 400 px (16 : 5 aspect ratio)
**Format:** SVG (preferred)
**Max file size:** 120 KB

### Composition

The same systems-map geometry as the light theme, adapted to a deep neutral
canvas. Violet/cyan glows, a sparse star field, evidence nodes, and animated
signal traces preserve the exact visual concept across theme changes.

### Subject-Safe Zone

Same as Brief 1: `x: 240–1040 px, y: 60–340 px`

### Palette (Dark Theme)

- Background: `#0d1117` → `#161b22` radial
- Stars: `#e6edf3` at varying opacity (0.3–0.8)
- Constellation lines: `#388bfd` at 0.4 opacity
- Accent glyph: amber `#e3b341` or violet `#a371f7`
- Architecture silhouette: `#a371f7` at 0.3–0.5 opacity

### Contrast

Star points, constellation lines, and accent elements must maintain ≥ 3 : 1
against the background. No text in image.

### Text-Free Variant

Same rule as Brief 1. No embedded text.

### Negative Constraints

Same as Brief 1.

### Required Outputs

1. `banner-dark.svg` — implemented dark-theme variant.
2. A brief description of the scene for the alt-text record.

---

## Brief 3 — Profile Mark / Avatar

**Output file:** `assets/profile/mark.svg`
**Dimensions:** 400 × 400 px (1 : 1 square)
**Format:** SVG
**Max file size:** 40 KB

### Composition

A minimal circular or square mark that works as both a README logo and a
GitHub avatar crop. Central motif: a stylized monogram "AS" or an abstract
geometric symbol (orbiting dots, minimal constellation, or a single angular
letterform) that is legible at 32 px.

### Dual-Theme Requirement

The mark must be legible against both `#FFFFFF` (light) and `#0d1117` (dark)
backgrounds. Preferred approach: transparent background with `stroke` and/or
`fill` in a high-contrast color (`#6639BA` violet or `#e3b341` amber) that
achieves ≥ 4.5 : 1 on both surfaces.

### Negative Constraints

- No photorealistic elements.
- No external URL references.
- No text elements (the monogram, if used, must be rendered as paths, not
  `<text>`).
- Must include a `<title>` element: "Alan Szmyt — profile mark".

### Required Outputs

1. `mark.svg` — single file, dual-theme compatible.

---

## Brief 4 — Section Divider (Optional)

**Output file:** `assets/profile/divider.svg`
**Dimensions:** 1280 × 8 px
**Format:** SVG
**Max file size:** 8 KB

### Composition

A single horizontal line with a gradient fade from transparent at both ends
to the accent colors in the center. The line must be purely decorative
(no information content). `alt=""` in markup.

### Palette

Gradient: `#6639BA` → `#3fb950` (left to right), fading to transparent at
both edges.

### Required Outputs

1. `divider.svg`.

---

## Legacy Branding Reference Notes

Earlier branding drafts do not satisfy the asset contract defined in this
document (dimensions, format, validation, provenance) and should be
regenerated from scratch using the briefs above.
