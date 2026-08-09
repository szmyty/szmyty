# Design System — Alan Szmyt Profile

**Status:** Active — production source of truth
**Last updated:** 2026-08-09

---

## 1. Visual Thesis and Narrative

The profile communicates **craft, depth, and precision**. The aesthetic is
cosmic: dark-mode-first, deep-space blues and violets with deliberate warm
amber and teal accents, conveying both technical rigour and creative breadth.
Every visual element must reinforce the written narrative rather than
substitute for it. When images are unavailable, the profile must remain fully
legible and credible through text alone.

---

## 2. Color Roles and Contrast Targets

All color decisions must meet WCAG 2.1 AA contrast (≥ 4.5 : 1 for body text,
≥ 3 : 1 for large text and UI components).

| Role | Light token | Dark token | Notes |
|------|-------------|------------|-------|
| Background | `#FFFFFF` | `#0d1117` | GitHub default surface |
| Surface elevated | `#F6F8FA` | `#161b22` | Cards, code blocks |
| Border | `#D0D7DE` | `#30363d` | Dividers |
| Text primary | `#1F2328` | `#e6edf3` | Body copy |
| Text secondary | `#59636E` | `#7d8590` | Captions, metadata |
| Accent cosmic-blue | `#0969DA` | `#388bfd` | Links, active states |
| Accent violet | `#6639BA` | `#a371f7` | Hero highlight |
| Accent amber | `#9A6700` | `#e3b341` | Warnings, emphasis |
| Accent teal | `#1A7F64` | `#3fb950` | Success, secondary CTA |

**Validation rule:** Every foreground/background combination used in SVG assets
must be listed here and must pass the AA contrast ratio at its declared size.

---

## 3. Typography Constraints under GitHub Markdown

GitHub Markdown does not allow custom fonts, font-size overrides, or CSS
variables in `README.md`. All body typography is controlled by GitHub's
rendering pipeline.

- **Body:** GitHub's default proportional sans-serif (Segoe UI, Helvetica, etc.)
- **Code:** GitHub's default monospace (SFMono, Cascadia Code, etc.)
- **Bold / italic** may be used for emphasis; avoid excessive decoration.
- **Heading hierarchy:** use `##` for sections, `###` for subsections.
  Never skip heading levels.
- **Table width** is fluid; keep column counts ≤ 4 to avoid horizontal scroll
  on mobile viewports (320 px minimum).
- **SVG text elements** used for labels within assets must embed their own
  fallback font stack (no web-font imports).

---

## 4. Spacing, Section Rhythm, and Responsive Behavior

- Separate top-level sections with a single `---` horizontal rule.
- Never nest more than two `<div>` elements; GitHub strips unknown HTML.
- All `<div align="center">` wrappers must contain only inline or block
  elements that GitHub allows (headings, paragraphs, images, badges).
- Mobile target: 320 px viewport — no element should require horizontal scroll.
- `<picture>` blocks must define both `light` and `dark` sources; see §8.
- Badge rows: group up to 6 badges per line; use `<br>` sparingly.

---

## 5. Light / Dark Theme Strategy

GitHub profiles render in the viewer's chosen theme. Assets must account for
both modes.

- **Banner:** supply `banner-light.svg` and `banner-dark.svg`.
  Use a `<picture>` block with `prefers-color-scheme` media queries.
- **Mark / avatar:** supply a single `mark.svg` with an embedded palette that
  works against both `#FFFFFF` and `#0d1117` backgrounds (use a transparent
  background or a high-contrast border).
- **Dividers / frames:** use `stroke` rather than `fill` where possible so the
  element is visible against both backgrounds; or supply paired variants.
- **Text in SVG:** embed both colors and switch via `<style>`
  `prefers-color-scheme` where SVG renderers support it; otherwise supply
  paired files.

---

## 6. Reduced-Motion Behavior

- All SVG animations must be wrapped in
  `@media (prefers-reduced-motion: no-preference) { … }`.
- The static (no-animation) state must be visually meaningful on its own;
  animation is an enhancement, not a carrier of information.
- Do not use `<animate>` or JavaScript inside SVGs served from GitHub
  (GitHub strips script tags; animated SVGs via `<img>` tags retain CSS but
  not JS).

---

## 7. Asset Roles, Dimensions, Aspect Ratios, and File-Size Budgets

| Asset | File(s) | Dimensions | Aspect ratio | Max size |
|-------|---------|-----------|--------------|----------|
| Hero banner | `banner-light.svg`, `banner-dark.svg` | 1280 × 400 px | 16 : 5 | 120 KB each |
| Profile mark / avatar | `mark.svg` | 400 × 400 px | 1 : 1 | 40 KB |
| Section divider | `divider.svg` | 1280 × 8 px | — | 8 KB |
| Project card frame | `card-frame.svg` | 480 × 240 px | 2 : 1 | 24 KB |

All raster fallbacks (if any) must be ≤ 2× the SVG budget and must not exceed
the dimension limits. No raster image may carry text that is unavailable
elsewhere as Markdown.

---

## 8. Alt-Text Strategy

- Every `<img>` and `<picture>` in `README.md` must carry a non-empty `alt`
  attribute.
- The `alt` attribute must describe what the image conveys, not just its
  filename. Example: `alt="Alan Szmyt — Software Engineer, Systems Architect"`.
- Decorative-only elements (pure dividers with no informational content) use
  `alt=""`.
- Every SVG file must contain a direct `<title>` element as the first child of
  the root `<svg>` element.

---

## 9. Fallbacks When Images Do Not Load

All critical identity text (name, role, tagline, links) must exist as real
Markdown text in `README.md`, not only inside image files. If every image on
the page fails to load, the visitor must still be able to identify the person,
understand their work, and navigate to public artifacts.

- The hero `<picture>` block must be immediately followed by (or replaced by)
  a Markdown heading and brief tagline.
- Section headings and navigation must be Markdown headings, never image-only.

---

## 10. Rules for Generated versus Hand-Authored Assets

| Rule | Generated assets | Hand-authored assets |
|------|-----------------|---------------------|
| Source preserved | Generation brief in `ASSET-BRIEF.md`; ChatGPT session reference | Editable vector in `source/` |
| Optimization required | Yes — strip metadata, minify | Yes — SVGO pass |
| Re-generation protocol | Replace file, run validator, commit | Edit source, export, run validator, commit |
| Active content (JS, external URLs) | Prohibited | Prohibited |
| Embedded credentials | Prohibited | Prohibited |

---

## 11. Examples of Approved and Rejected Visual Patterns

### Approved

- Deep-space radial gradient: `#0d1117` center to `#1e1b4b` edge with
  scattered white star points.
- Outlined constellation paths (`stroke` only, transparent `fill`).
- Amber `#e3b341` glyph or symbol as a focal mark.
- Plain `---` dividers in Markdown.
- `<picture>` banner with light and dark sources.

### Rejected

- Photorealistic portraits or avatars that could be confused with a real person.
- Stock art copied from another profile or AI-generation service output that
  was not created for this profile.
- Solid dark overlays that reduce text contrast below 4.5 : 1.
- Animations that carry information unavailable in the static state.
- SVGs that reference external URLs, embed scripts, or use
  `<foreignObject>` to inject HTML.
- Text that exists only inside a raster image (PNG, JPEG).
- Any placeholder labeled "FINAL" before it is confirmed by Alan.

---

## 12. Asset Validation Checklist (automated)

Run `python profile/validate_assets.py assets/profile/` to verify:

1. Required files are present and have allowed extensions.
2. File sizes are within budget.
3. SVGs parse without error.
4. SVGs have a `viewBox` attribute on the root element.
5. SVGs have a `<title>` as first child of root `<svg>`.
6. SVGs contain no `<script>` tags or `javascript:` URL references.
7. Light/dark banner pair is complete.
8. `assets/profile/README.md` references only files that exist.

---

## 13. Provenance and Licensing

All final assets must be documented in `assets/profile/README.md`:

- Tool used (ChatGPT image generation, Inkscape, etc.)
- Date generated or last modified.
- License (MIT for hand-authored; generation output is released under MIT by
  the repository owner's declaration in this file).
- Optimization tool and version.
- SHA-256 checksum for generated raster assets (informational).
