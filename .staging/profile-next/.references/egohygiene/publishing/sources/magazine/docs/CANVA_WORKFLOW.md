# Canva Workflow

**Canonical reference:** `references/edition_1/cover/outside.png`

This document translates the finalized front cover of Edition 1 into a reproducible Canva layer system. It defines the standard layer structure, naming conventions, and assembly workflow so that any contributor can recreate or extend cover and page designs consistently.

---

## Document Setup

Before building any layer, configure the Canva document to match the canonical page dimensions:

| Setting | Value |
|---|---|
| Width | 800 px (`layout.page.width`) |
| Height | 1120 px (`layout.page.height`) |
| Orientation | Portrait |
| Color profile | sRGB |

> **Cover-specific dimensions:** the reference cover image (`outside.png`) is 1024 × 1536 px (2:3 aspect ratio). When recreating the cover in Canva, set the document to 1024 × 1536 px. The 800 × 1120 px canvas is used for interior practice pages.

---

## Brand Kit Setup

Before using any layer that contains color or text, configure the Canva Brand Kit to match the design tokens in `design-system/tokens/`.

### Color palette

Add each swatch to the Brand Kit using its token name as the label:

| Token | Hex | Cover role |
|---|---|---|
| `warm_yellow` | `#F5C842` | Title band and subtitle glow |
| `burnt_orange` | `#C4622D` | Dominant warm accent, headers, decorative elements |
| `soft_amber` | `#FFBF00` | Candlelight warmth, highlight areas, bottom price band |
| `crimson` | `#880B02` | Title band depth, edge-burn regions |
| `deep_teal` | `#3D6B67` | Shadow behind crystal cluster and silhouette |
| `deep_blue` | `#1B3A6B` | Night-sky depth, archival ink, outer background |
| `near_black` | `#161117` | Deep vignette shadow, outermost border regions |
| `rose_quartz` | `#CE6B70` | Prismatic iridescent accent from crystal cluster |
| `soft_gold` | `#D4AF37` | Metallic decorative accent, rules, ornate border |
| `warm_parchment` | `#F5ECD7` | Aged paper base surface tone |
| `charcoal` | `#3A3A3A` | Standard content frame lines |
| `deep_brown` | `#4A2C2A` | Worn-ink distress marks |

### Typography styles

Map each role to a Canva text style. **All cover text carries ink-distress texture — do not apply anti-aliasing that would eliminate worn-ink edge quality.**

| Role | Canva style name | Family | Weight | Size | Tracking | Case |
|---|---|---|---|---|---|---|
| `role.display` | `Display / Cover Headline` | Bold distressed retro display (TBD) | Black / 900 | 56 px | Tight (−0.02 em) | Uppercase |
| `role.heading` | `Heading / Edition Label` | Serif | Bold / 700 | 28 px | Normal | Title case |
| `role.tagline` | `Tagline / Atmospheric` | Retro emphasis sans-serif | Medium / 500 | 12 px | Wider (0.12 em) | Title case |
| `role.label` | `Label / UI Badge` | Bold sans-serif | Bold / 700 | 10 px | Wider (0.12 em) | All caps |
| `role.body` | `Body / Editorial` | Serif | Regular / 400 | 16 px | Normal | Sentence case |
| `role.caption` | `Caption / Footnote` | Sans-serif | Regular / 400 | 10 px | Wide (0.06 em) | Sentence case |

---

## Layer Naming Conventions

All layers follow this pattern:

```
[section]__[element]--[variant]
```

| Part | Description | Examples |
|---|---|---|
| `section` | Functional zone of the page | `bg`, `texture`, `hero`, `fx`, `text`, `ui`, `frame` |
| `element` | Specific named element | `base`, `grain`, `vignette`, `crystal`, `silhouette`, `title`, `price_badge` |
| `variant` | Optional modifier | `dark`, `warm`, `left`, `top`, `v2` |

**Examples:**

```
bg__base
bg__teal_shadow
texture__grain
texture__vignette--edge
texture__ink_distress
hero__crystal
hero__silhouette
fx__glow--amber
text__title
text__edition_label
text__tagline
ui__skull_emblem
ui__price_badge
ui__issue_badge
ui__tone_badge
frame__ornate_border
```

All layer names must be lowercase with underscores for spaces. No layer should be named by Canva's default (e.g. "Image 3" or "Text 7").

---

## Layer Stack — Cover Front (Outside)

Layers are listed bottom to top. The topmost layer in the list is rendered above all others.

| # | Layer name | Type | Token / value | Purpose |
|---|---|---|---|---|
| 1 | `bg__base` | Rectangle (full bleed) | `near_black` `#161117` | Deepest background field; establishes the dark artifact register on which all warm tones are revealed |
| 2 | `bg__teal_shadow` | Shape / gradient fill | `deep_teal` `#3D6B67` → transparent | Muted blue-green mid-ground shadow zone behind the crystal cluster and human silhouette; creates cool depth contrast |
| 3 | `texture__aged_paper` | Image (texture tile, set to Multiply or Overlay) | `warm_parchment` `#F5ECD7` | Primary surface tone; slight yellowing and uneven density evoke paper age; first in the texture stack, placed directly above the background layers |
| 4 | `texture__grain` | Image (noise/grain overlay, set to Overlay or Soft Light) | Opacity ≈ 30–40% | Fine photographic grain distributed uniformly across the entire surface; eliminates digital smoothness and reinforces analog-print origin |
| 5 | `texture__vignette--edge` | Radial gradient (full bleed) | `near_black` `#161117` → transparent | Radial darkening from edge to center; frames the central element and strengthens the found-artifact reading |
| 6 | `texture__ink_distress` | Image (distress overlay, set to Multiply) | `crimson` `#880B02` / `deep_brown` `#4A2C2A` | Irregular worn-ink breaks and oxidation marks; most concentrated in the title and lower price-band areas |
| 7 | `hero__crystal` | Image | — | Large iridescent crystal cluster; the central foreground motif; carries `rose_quartz` prismatic highlights and `deep_teal` shadow underside |
| 8 | `hero__silhouette` | Image | `near_black` `#161117` silhouette | Shadowed human figure in contemplative posture; positioned behind or beside the crystal to imply scale and spiritual context |
| 9 | `fx__glow--amber` | Radial gradient or blurred shape | `soft_amber` `#FFBF00` → `warm_yellow` `#F5C842` → transparent | Warm central light source emanating from the crystal cluster; inner canvas significantly warmer and brighter than edges |
| 10 | `ui__skull_emblem` | Image / SVG | — | Decorative skull motif; reinforces the retro-mystical-pulp register |
| 11 | `text__title` | Text (`role.display`) | `warm_yellow` `#F5C842` | Main cover headline: `EGO HYGIENE`; maximum weight, uppercase, ink-wear texture applied; anchors the entire title band |
| 12 | `text__edition_label` | Text (`role.heading`) | `soft_amber` `#FFBF00` | Edition identifier: `Edition 1: Orientation`; clean serif below the title; establishes hierarchy tier 2 |
| 13 | `text__tagline` | Text (`role.tagline`) | `warm_parchment` `#F5ECD7` | Atmospheric tagline: `A Mystic Guide for Self-Maintenance`; retro emphasis sans-serif, wide tracking; hierarchy tier 3 |
| 14 | `ui__price_badge` | Text + shape (`role.label`) | `soft_amber` `#FFBF00` on `crimson` `#880B02` | Price identifier: `25¢`; retro price-tag shape; all-caps bold sans-serif |
| 15 | `ui__issue_badge` | Text + shape (`role.label`) | `warm_yellow` `#F5C842` on `near_black` `#161117` | Issue identifier: `Issue No. 1`; compact, extra-wide tracking |
| 16 | `ui__tone_badge` | Text + shape (`role.label`) | `warm_parchment` `#F5ECD7` on `deep_teal` `#3D6B67` | Tonal flavor badge: `Scary! Fun!`; secondary badge adjacent to price or issue identifier |
| 17 | `frame__ornate_border` | Rectangle stroke | `soft_gold` `#D4AF37`, 4 px double | Outermost ornate frame; `frame.ornate` preset from `design-system/tokens/borders.json`; visually contains the composition and signals the collectible-artifact register |

---

## Layer Groups

Organize layers into named groups in the Canva layer panel to reduce visual noise:

| Group name | Layers inside |
|---|---|
| `GRP_background` | `bg__base`, `bg__teal_shadow` |
| `GRP_texture` | `texture__aged_paper`, `texture__grain`, `texture__vignette--edge`, `texture__ink_distress` |
| `GRP_hero` | `hero__crystal`, `hero__silhouette` |
| `GRP_effects` | `fx__glow--amber` |
| `GRP_text` | `text__title`, `text__edition_label`, `text__tagline` |
| `GRP_ui` | `ui__skull_emblem`, `ui__price_badge`, `ui__issue_badge`, `ui__tone_badge` |
| `GRP_frame` | `frame__ornate_border` |

Collapse all groups when not editing them to keep the panel legible.

---

## Layout Zones

The cover composition follows the same proportional zone system documented in `design-system/tokens/spacing.json`:

| Zone | Fractional height | Approximate pixel height (1120 px canvas) | Content |
|---|---|---|---|
| Header | 0.09 | ≈ 100 px | Title (`text__title`) + edition label (`text__edition_label`) |
| Content | 0.45 | ≈ 504 px | Crystal cluster (`hero__crystal`) + silhouette (`hero__silhouette`) + glow (`fx__glow--amber`) |
| Tagline | 0.10 | ≈ 112 px | Tagline text (`text__tagline`) |
| UI strip | 0.09 | ≈ 100 px | Badge identifiers (`ui__price_badge`, `ui__issue_badge`, `ui__tone_badge`) |
| Footer | 0.07 | ≈ 78 px | *(empty on front cover — used by practice pages)* |

Use Canva's **ruler guides** to mark the boundaries of each zone before placing elements.

---

## Blend Modes for Texture Layers

| Layer | Recommended blend mode | Notes |
|---|---|---|
| `texture__aged_paper` | Multiply or Overlay | Test both; Multiply darkens less aggressively on light surfaces |
| `texture__grain` | Overlay or Soft Light | Soft Light preserves more midtone warmth |
| `texture__vignette--edge` | Normal (gradient) | Adjust opacity (40–65%) until edges feel burned without crushing the hero zone |
| `texture__ink_distress` | Multiply | Allows underlying warm tones to show through the distress marks |
| `fx__glow--amber` | Screen or Add | Creates additive warm luminance; reduce opacity until the glow reads as internal light, not flare |

---

## Three Visual Registers

All layers must collectively embody three simultaneous visual registers. A cover that satisfies only one or two of these is incomplete:

| Register | Description | Key layers |
|---|---|---|
| **Pulp / vintage comic** | Mid-20th-century aesthetic. Bold framing, high contrast, price-badge and issue-number identifiers, retro color separation, coarse printed feel. | `bg__base`, `text__title`, `ui__price_badge`, `ui__issue_badge`, `ui__tone_badge`, `frame__ornate_border` |
| **Mystical / symbolic** | Iridescent crystal cluster as the central motif. Human silhouette in spiritual contemplation. Visual language from esoteric / metaphysical print artifacts. | `hero__crystal`, `hero__silhouette`, `bg__teal_shadow`, `fx__glow--amber` |
| **Distressed / tactile** | Every element carries evidence of physical age — grain, worn ink, vignette burn, oxidized reds. Reads as a found artifact, not a freshly produced digital file. | `texture__aged_paper`, `texture__grain`, `texture__vignette--edge`, `texture__ink_distress` |

---

## Standard Layer Structure for Future Pages

For **practice pages** (page type `practice_front` / `practice_back`), apply this reduced layer set derived from the cover structure:

| # | Layer name | Type | Purpose |
|---|---|---|---|
| 1 | `bg__base` | Rectangle (full bleed) | Dark background field |
| 2 | `texture__aged_paper` | Image (Multiply) | Aged paper surface tone |
| 3 | `texture__grain` | Image (Overlay) | Analog-print noise |
| 4 | `texture__vignette--edge` | Radial gradient | Edge burn / framing |
| 5 | `texture__ink_distress` | Image (Multiply) | Worn ink marks |
| 6 | `hero__illustration` | Image | Central practice illustration (silhouette, symbol, or figure) |
| 7 | `fx__glow--ambient` | Radial gradient | Soft warm light source from central element |
| 8 | `text__title` | Text (`role.display`) | Practice title |
| 9 | `text__subtitle` | Text (`role.heading`) | Practice subtitle or instruction header |
| 10 | `panel__[id]` × 4 | Text + shape (`role.label` + `role.body`) | Practice instruction panels (e.g. `panel__breathe`, `panel__move`) |
| 11 | `panel__effect` | Text + shape (`role.heading` + `role.body`) | EFFECT strip |
| 12 | `banner__footer` | Rectangle + text (`role.label`) | Bottom affirming statement banner |
| 13 | `frame__ornate_border` | Rectangle stroke | Outermost ornate gold frame |

Rename `hero__illustration` to reflect the specific page content (e.g. `hero__running_silhouette`, `hero__crystal_hands`).

---

## Workflow Checklist

Before exporting any page from Canva:

- [ ] All layers are named using the `[section]__[element]--[variant]` convention — no default Canva names remain
- [ ] All layers are organized into the correct named groups
- [ ] Brand Kit color swatches match the tokens in `design-system/tokens/colors.json`
- [ ] Typography styles match the roles in `design-system/tokens/typography.json`
- [ ] All three visual registers (pulp, mystical, distressed) are present simultaneously
- [ ] Ruler guides mark the layout zone boundaries
- [ ] Texture blend modes follow the table above
- [ ] Frame border uses the `frame.ornate` preset: `soft_gold` `#D4AF37`, 4 px double stroke
- [ ] Export format: PNG, sRGB, maximum quality

---

## Relationship to Other Documents

| Document | Relationship |
|---|---|
| `design-system/README.md` | Full design token documentation; canonical source for all hex values, typography roles, and texture descriptions used in this file |
| `design-system/tokens/colors.json` | Authoritative color token file; consult before selecting any hex value in Canva |
| `design-system/tokens/typography.json` | Authoritative typography token file; consult before creating any text style |
| `design-system/tokens/spacing.json` | Layout zone proportions and spacing scale |
| `design-system/tokens/borders.json` | Frame and border presets including `frame.ornate` |
| `editions/edition_1/pages/00_cover_front_outside/page.json` | Cover page schema; the data model that corresponds to this visual layer structure |
| `references/edition_1/cover/outside.png` | The finalized front cover image; ultimate visual reference for any ambiguity in this document |
| `context/constraints.json` | Editorial constraints (forbidden IP, tone markers, style invariants, conceptual guardrails) that apply to all Canva work |
