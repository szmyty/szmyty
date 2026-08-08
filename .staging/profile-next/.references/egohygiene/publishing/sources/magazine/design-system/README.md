# Design System

This directory is the **single source of truth** for all visual design tokens and styling decisions used across the *magazine* project.

---

## Purpose

The `design-system/` directory establishes a centralized, version-controlled foundation for:

- **Design tokens** — the atomic values (colors, typography, spacing, borders) that define the visual language
- **Consistency** — every component, template, and published edition references the same source values
- **Collaboration** — tokens are format-agnostic JSON structures that can be consumed by React, Storybook, Canva, and custom renderers equally
- **Traceability** — every visual decision can be traced back to a named token with a documented purpose, making audits and reviews straightforward

The design system sits at the base of the entire production stack. Nothing in the publication should carry hard-coded color, spacing, or typographic values that are not defined here first.

---

## Cover Design DNA

**Canonical reference:** `references/edition_1/cover/outside.png`

All design decisions in this system are anchored to the finalized front cover of Edition 1. The values below were extracted directly from the reference artifact. Do **not** generalize beyond what is observed in that image.

---

### 🎨 Color System

The cover palette is built on a **warm-over-dark** contrast strategy: bright amber-gold and burnt-orange forms are layered over near-black and deep-teal backgrounds, creating the high-contrast aged-print quality central to the publication's identity.

Token hex values are the canonical design system values. Where pixel-average measurements from the reference image are noted, they confirm the token is correctly anchored to the observed color and explain any minor rounding differences between the idealized token swatch and the blended average across thousands of rendered pixels.

#### Primary warm colors

| Token | Hex | Cover role |
|---|---|---|
| `color.warm_yellow` | `#F5C842` | Title band and subtitle glow; measured pixel average `#F7BB26` across ~13.5% of cover pixels — token value is the canonical idealized swatch |
| `color.burnt_orange` | `#C4622D` | Dominant warm accent across headers and decorative elements; measured pixel average `#C46C16` across ~9.6% of cover pixels |
| `color.soft_amber` | `#FFBF00` | Mid-tone candlelight warmth used in highlight areas and bottom price band |
| `color.crimson` | `#880B02` | Deep rust-red visible in the cover title band and edge-burn regions (≈ 2.2% of cover pixels) |

#### Secondary cool colors

| Token | Hex | Cover role |
|---|---|---|
| `color.deep_teal` | `#3D6B67` | Muted blue-green shadow behind the crystal cluster and human silhouette (≈ 3.4% of cover pixels) |
| `color.deep_blue` | `#1B3A6B` | Night-sky and archival ink depth; found in the outer background beyond the teal zone |
| `color.near_black` | `#161117` | Deep vignette shadow dominating the outer edges and border regions (≈ 7.2% of cover pixels) |

#### Crystal / accent

| Token | Hex | Cover role |
|---|---|---|
| `color.rose_quartz` | `#CE6B70` | Prismatic iridescent tone from the central crystal cluster (≈ 2.5% of cover pixels) |
| `color.soft_gold` | `#D4AF37` | Metallic decorative accent for rules and ornate frame borders |

#### Contrast relationships

- **Warm vs cool balance:** warm tones (gold, orange, amber) account for approximately 25% of cover pixels; cool tones (teal, blue, near-black) account for approximately 14%. The remaining ~61% comprises mid-range browns, warm-darks, and transitional tones — confirming a warm-dominant, cool-accented palette. (All percentages are approximate and reflect color-range sampling rather than hard boundaries.)
- **Dominant contrast axis:** the cover's primary visual tension is `warm_yellow` / `soft_amber` over `near_black` — bright warm golds punching out of a near-black field.
- **Secondary contrast axis:** `deep_teal` receding behind `rose_quartz` crystal highlights — cool shadow grounding prismatic warm accents.

---

### 🧪 Texture Stack

The cover presents five texture layers, applied in the order listed. Every layer must be present in any component or template that claims to reproduce the cover aesthetic.

| Layer | Name | Description |
|---|---|---|
| 1 | **aged paper base** | The primary surface tone (`warm_parchment` / `#F5ECD7`); slight yellowing and uneven density evoke paper age. Applied as the base fill before any other layer. |
| 2 | **grain / noise** | Fine photographic grain distributed uniformly across the entire surface, most visible in mid-tone areas. Reduces digital smoothness and reinforces the analog-print origin. |
| 3 | **edge burn / vignette** | A radial darkening from edge to center, fading from `near_black` (`#161117`) at the outermost boundary toward the warm mid-tones of the center zone. Frames the central element and strengthens the artifact reading. |
| 4 | **ink distress** | Irregular worn-ink breaks and oxidation marks, most concentrated in the title and lower price-band areas. Expressed through `crimson` (`#880B02`) and `deep_brown` (`#4A2C2A`) tonal variations. |
| 5 | **lighting / glow effects** | A warm central light source emanating from the crystal cluster, creating a `soft_amber` to `warm_yellow` radial glow. The inner canvas is significantly warmer and brighter than the edges. Allowed animation effects include `subtle_light_pass`, `crystal_edge_glow`, and `ambient_particle_drift`. |

---

### 🔤 Typography Roles

Typography on the cover follows a strict three-tier hierarchy with an additional badge layer for UI identifiers. All roles are documented as tokens in `tokens/typography.json`.

| Role token | Cover element | Style | Example |
|---|---|---|---|
| `role.display` | Main title | Bold distressed retro display, uppercase, ink-wear texture, maximum weight | `EGO HYGIENE` |
| `role.heading` | Edition label / subtitle | Clean serif, title case, normal weight | `Edition 1: Orientation` |
| `role.tagline` | Atmospheric tagline | Retro emphasis sans-serif, medium weight, wide tracking | `A Mystic Guide for Self-Maintenance` |
| `role.label` | UI badge identifiers | Bold sans-serif, compact, extra-wide tracking, all-caps | `Issue No. 1` · `25¢` · `Scary! Fun!` |
| `role.body` | Interior editorial text | Serif, regular weight, optimized for sustained reading | *(not on cover)* |
| `role.caption` | Captions and footnotes | Sans-serif, reduced scale, wide tracking | *(not on cover)* |

**Notes:**
- The `display` font family is still marked `TBD` in `font.family.display` pending finalization. The cover reference confirms it must be a **bold, distressed, high-contrast uppercase display face** consistent with mid-20th-century pulp print typography.
- All cover text is rendered with ink-distress texture — do not apply on-screen anti-aliasing that would eliminate the worn-ink edge quality.

---

### 🎯 Visual Tone

The cover establishes three tonal registers that all edition components must honor:

| Register | Description |
|---|---|
| **Pulp / vintage comic** | Mid-20th-century aesthetic reference. Bold framing, high contrast, price-badge and issue-number identifiers, retro color separation, and a slightly coarse printed feel. |
| **Mystical / symbolic** | Iridescent crystal cluster as the central motif. Human silhouette in spiritual contemplation. Visual language borrows from esoteric / metaphysical print artifacts. The `rose_quartz` crystal accent and `deep_teal` shadow support this register. |
| **Distressed / tactile** | Every element carries some evidence of physical age — grain, worn ink, vignette burn, oxidized reds. The cover should read as a found artifact, not a newly produced digital file. |

These three registers are not independent — they reinforce each other. A component that is *mystical but clean* or *distressed but bright* is diverging from the reference. All three must be simultaneously present.

---

## Directory Structure

```
design-system/
├── tokens/
│   ├── colors.json       ← Color palette extracted from visual_dna.json
│   ├── typography.json   ← Font families, sizes, weights, line-heights
│   ├── spacing.json      ← Layout proportions, grid, and gap scale
│   └── borders.json      ← Frame styles, border widths, and radii
└── README.md             ← This file
```

---

## Token Files

### `tokens/colors.json`

Contains the canonical twelve-color palette cross-referenced between
`editions/edition_1/visual_dna.json` and the reference front cover artifact
(`references/edition_1/cover/outside.png`). Each token includes:

- a semantic name (e.g. `burnt_orange`, `warm_parchment`)
- a hex `$value`
- a `$description` explaining the color's role in the aesthetic

These colors reflect the **retro-print / weathered-artifact** identity of the publication.

The file is organised into three layers:

| Layer | Key | Purpose |
|---|---|---|
| `color.*` | e.g. `color.burnt_orange` | Raw named palette values; one token per hex swatch |
| `palette.*` | e.g. `palette.primary.base` | Groupings by visual role (primary, secondary, accent) that reference `color.*` tokens |
| `semantic.*` | e.g. `semantic.background` | UI-function aliases (background, text, primary, accent, border, shadow) that reference `color.*` tokens |

The four colors added from the cover reference artifact (`deep_teal`, `near_black`, `crimson`, `rose_quartz`) are present in the reference image and in `editions/edition_1/pages/00_cover_front_outside/page.json` (as `deep_teal`, `shadow_black`, `rust_red`, and `prismatic_crystal` respectively) but were absent from `editions/edition_1/visual_dna.json`. The `visual_dna.json` file captures patterns aggregated across all edition pages and uses short label names rather than hex values; the cover page's unique accent tones were under-represented in that aggregation. The token file is the maintained source of truth; `visual_dna.json` remains the historical extraction artifact and is not modified.

Always reference **semantic tokens** in components and templates. Reference raw `color.*` tokens only when creating new palette groupings inside `colors.json` itself.

### `tokens/typography.json`

Defines font primitives (families, sizes, weights, line-heights, letter-spacing) and
six **semantic text roles** that compose those primitives into reusable styles:

| Role | Font family | Weight | Size | Line height | Letter spacing |
|---|---|---|---|---|---|
| `display` | `font.family.display` (TBD) | black / 900 | 56 px (`3xl`) | tight / 1.2 | tight / −0.02 em |
| `heading` | `font.family.serif` | bold / 700 | 28 px (`xl`) | snug / 1.4 | normal / 0 em |
| `body` | `font.family.serif` | regular / 400 | 16 px (`md`) | normal / 1.6 | normal / 0 em |
| `caption` | `font.family.sans` | regular / 400 | 10 px (`xs`) | snug / 1.4 | wide / 0.06 em |
| `tagline` | `font.family.sans` | medium / 500 | 12 px (`sm`) | snug / 1.4 | wider / 0.12 em |
| `label` | `font.family.sans` | bold / 700 | 10 px (`xs`) | tight / 1.2 | wider / 0.12 em |

**Role definitions:**

- **display** — Page titles and cover headlines. Uses the yet-to-be-finalized display
  font at maximum weight for full visual impact.
- **heading** — Section headers and article titles. Editorial serif at bold weight
  provides a clear hierarchy marker.
- **body** — Main editorial text and practice prompts. Same serif family as headings
  for visual coherence; optimized for sustained reading comfort.
- **caption** — Captions, metadata labels, and footnotes. Switched to sans-serif for
  contrast; wide letter-spacing compensates for small size to maintain legibility.
- **tagline** — Cover atmospheric tagline, as observed on the reference cover
  ("A Mystic Guide for Self-Maintenance"). Retro emphasis sans-serif at medium weight
  with extra-wide tracking for vintage-print feel.
- **label** — UI badge and price-tag identifiers, as observed on the reference cover
  ("Issue No. 1", "25¢", "Scary! Fun!"). Bold sans-serif, compact, extra-wide tracking
  for all-caps legibility at small sizes.

All role values are expressed as token references (e.g. `{font.size.md}`) so that
updating a primitive automatically propagates to every role that references it.

The `display` font family is still marked `TBD` in `font.family.display` and will be
finalized during the component-design phase.

Use `role.*` tokens in all components and templates. Use `font.*` primitive tokens only
when defining or composing new roles inside `typography.json`.

### `tokens/spacing.json`

A 4-based spacing scale (0 → 128 px) plus named layout constants
(page width/height, margins, column counts) inferred from edition page templates.

| Token | Value | Use |
|---|---|---|
| `spacing.1` | 4 px | Micro gaps, icon padding |
| `spacing.2` | 8 px | Inline element separation |
| `spacing.3` | 12 px | Caption-to-image gap |
| `spacing.4` | 16 px | Base unit; paragraph spacing, panel padding |
| `spacing.5` | 24 px | Section inset, card padding |
| `spacing.6` | 32 px | Column gutter, block separation |
| `spacing.7` | 48 px | Section break, large vertical rhythm |
| `spacing.8` | 64 px | Page margin, hero padding |
| `spacing.9` | 96 px | Full-bleed offsets, editorial white space |
| `spacing.10` | 128 px | Cover anchor, oversized decorative gap |

The file also defines a `layout.zones` group that formalises the proportional
layout bands observed consistently across all ten practice pages in edition 1.
Zone heights are expressed as **decimal fractions of the total page height**
(e.g. `0.09` = 9%) so they remain valid regardless of the final output resolution
or print format. Multiply a fraction by the page height in pixels to obtain the
absolute pixel height.

| Zone token | Value | Pixel equivalent (1120 px canvas) | Role |
|---|---|---|---|
| `layout.zones.header.height` | 0.09 | ≈ 100 px | Display title + subtitle band |
| `layout.zones.content.height` | 0.45 | ≈ 504 px | Central focal image / silhouette region |
| `layout.zones.prompt.height` | 0.30 ¹ | ≈ 336 px | Four labelled practice-instruction panels |
| `layout.zones.effect.height` | 0.10 | ≈ 112 px | Highlighted neurological-benefit strip |
| `layout.zones.footer.height` | 0.07 | ≈ 78 px | Bold affirming closing-statement banner |
| `layout.zones.inner_margin` | 24 px | 24 px | Gap between content blocks within a zone |

¹ The prompt zone is nested within the content zone. Do not add prompt and content heights together when computing total layout height — non-overlapping zones (header + content + effect + footer = 0.71) plus outer margins and inter-zone gaps account for the full page height.

### `tokens/borders.json`

Border widths, radii, line styles, and five named **frame presets**
(`standard`, `ornate`, `aged`, `accent`, `subtle`) that map to the visual aesthetics
defined in `visual_dna.json`.

| Frame preset | Width | Style | Color token | Use |
|---|---|---|---|---|
| `frame.standard` | 1 px | solid | `color.charcoal` | Default content frame |
| `frame.ornate` | 4 px | double | `color.soft_gold` | Feature spreads and covers |
| `frame.aged` | 2 px | solid | `color.deep_brown` | Vintage-print worn-ink look |
| `frame.accent` | 2 px | dashed | `color.burnt_orange` | Pull-quotes and callout boxes |
| `frame.subtle` | 0.5 px | solid | `color.warm_parchment` | Near-invisible image bleed separation |

Border and padding primitives (`border.width.*`, `border.radius.*`, `border.style.*`,
`padding.*`) should be composed into named presets rather than referenced individually
in page templates. Use `frame.*` presets wherever a border is required.

---

## How Tokens Are Used

Tokens follow the [W3C Design Token Community Group](https://design-tokens.github.io/community-group/format/) draft format.
Each value is expressed as a `$value` / `$type` / `$description` triplet.

References between tokens use the `{category.name}` syntax (e.g. `{color.charcoal}`),
which is resolved by build-time tooling such as [Style Dictionary](https://amzn.github.io/style-dictionary/).

### Intended consumers

| Consumer | How tokens are loaded |
|---|---|
| React / Storybook | CSS custom properties generated by Style Dictionary |
| Canva templates | Hex values copied from `colors.json` by hand or script |
| Python renderer | Direct JSON import via `json.load()` |
| LaTeX templates | Values interpolated into `.sty` files at build time |

### React / Storybook

Style Dictionary transforms token JSON into platform-specific outputs (CSS custom
properties, JS constants, SCSS variables). The expected workflow is:

1. Run Style Dictionary against `tokens/` to emit a `tokens.css` file (or equivalent).
2. Import the generated file at the root of the React application or Storybook config.
3. Reference tokens in component styles using CSS custom properties:

   ```css
   .article-heading {
     color: var(--color-charcoal);
     font-family: var(--font-family-serif);
     font-size: var(--font-size-xl);
   }
   ```

4. Storybook stories should document which token each visual property uses, so that
   design decisions remain visible and reviewable.

Style Dictionary is not yet wired into the project build; this is a planned step in the
component-design phase. Until then, token values may be imported directly from the JSON
files in JavaScript via `import tokens from '../design-system/tokens/colors.json'`.

### Canva workflow

Canva does not natively consume JSON tokens. The recommended workflow is:

1. Open `tokens/colors.json` and locate the `color.*` group.
2. Copy the hex values into the Canva **Brand Kit** color palette, using the semantic
   name (e.g. `burnt_orange`) as the swatch label.
3. For typography, map the `role.*` entries to Canva text styles:
   - `role.display` → Cover / Headline style
   - `role.heading` → Subheading style
   - `role.body` → Body text style
   - `role.caption` → Caption / Label style
4. For spacing and layout, use `layout.page.width` (800 px) and `layout.page.height`
   (1120 px) as the Canva document dimensions, and apply `layout.page.margin` (64 px)
   as the page safe-area margin guide.
5. After any update to `colors.json` or `typography.json`, update the Canva Brand Kit
   manually to keep it in sync with the token source.

A future scripted sync (e.g. via the Canva Connect API) may automate this step.

### Python renderer

The Python rendering pipeline imports token files directly:

```python
import json
from pathlib import Path

TOKENS_DIR = Path("design-system/tokens")

colors     = json.loads((TOKENS_DIR / "colors.json").read_text())
typography = json.loads((TOKENS_DIR / "typography.json").read_text())
spacing    = json.loads((TOKENS_DIR / "spacing.json").read_text())
borders    = json.loads((TOKENS_DIR / "borders.json").read_text())

# Example: access the page background color
# $value is the raw token reference string — pass it through a resolver before use
bg_ref = colors["semantic"]["background"]["$value"]  # → "{color.warm_parchment}"
bg_hex = resolve(colors, bg_ref)                     # → "#F5ECD7"
```

Token references (e.g. `{color.warm_parchment}`) must be resolved by the consuming
code before they are applied. A lightweight resolver walks the token tree to substitute
referenced values with their final primitive values. Do not hard-code hex values inside
Python rendering scripts.

---

## Relationship to Components and Templates

```
design-system/tokens/   ←  atomic values (this directory)
        ↓
  (future) design-system/components/   ←  composed UI primitives
        ↓
  editions/<edition>/pages/            ←  page templates using components
        ↓
  editions/<edition>/publishing/       ←  final rendered artifacts
```

The token layer is intentionally decoupled from components: tokens change only
when the visual language evolves; components change when layout patterns evolve.

**Layer responsibilities:**

| Layer | Contains | Changes when |
|---|---|---|
| `tokens/` | Raw values and semantic aliases | The visual language or brand identity changes |
| `components/` *(future)* | Reusable UI primitives that consume tokens | Layout patterns, interaction models, or component APIs change |
| `pages/` | Page-level templates that compose components | Editorial content structure or page type changes |
| `publishing/` | Final rendered artifacts | Any upstream layer changes |

A component must never define its own color, spacing, or typographic value outside of a
token reference. If a needed value does not exist as a token, add the token first.

---

## How to Add New Tokens

Follow these steps when the visual language requires a new value.

### 1. Determine the correct token file

| Value type | File |
|---|---|
| Color swatch or semantic color role | `tokens/colors.json` |
| Font family, size, weight, line-height, letter-spacing, or text role | `tokens/typography.json` |
| Spacing step, page dimension, or layout zone | `tokens/spacing.json` |
| Border width, radius, style, frame preset, or padding constant | `tokens/borders.json` |

### 2. Add the token to the correct group

- Place primitive values in the raw group (e.g. `color.*`, `font.*`, `spacing.*`, `border.*`).
- Place semantic aliases or role-level tokens in the higher-level group (e.g. `semantic.*`, `role.*`, `frame.*`).
- Never skip the primitive layer to add a value directly to a semantic group.

### 3. Follow the token format

Every token must include all three required fields:

```json
"token_name": {
  "$value": "...",
  "$type": "...",
  "$description": "One sentence explaining the token's purpose and where it appears."
}
```

Use token references (`{category.name}`) for any value that is derived from an existing
token. Never duplicate a hex or pixel value that already exists as a named token.

### 4. Update the README

If a new token *category* is added (a new top-level key in any token file, or an entirely
new token file), update this README's Token Files section to document it.

### 5. Validate

Run the project test suite to confirm all token files remain valid JSON and that no
existing references are broken:

```bash
poetry run pytest
```

---

## Consistency Guidelines

- **Always use token references for cross-file dependencies.** If `borders.json` needs the
  charcoal color, write `{color.charcoal}`, not `"#333333"`. This ensures a single change
  in `colors.json` propagates everywhere automatically.

- **Prefer semantic tokens over raw tokens in consumers.** Components and templates should
  reference `semantic.background`, not `color.warm_parchment`. This keeps the layer of
  intent visible and allows the semantic mapping to be changed without touching consumers.

- **Keep the spacing scale step-based.** New spacing values should align to an existing
  step or, if none exists, be added as a new named step on the 4 px base grid. Avoid
  one-off pixel values outside the scale.

- **Frame presets over ad hoc borders.** Any border applied in a component or template
  must use one of the five named `frame.*` presets. If none fits, add a new preset to
  `borders.json` before applying it.

- **Text roles over raw font primitives.** All text-bearing elements must use a named
  `role.*` style (`display`, `heading`, `body`, `caption`). If none fits, add a new role
  to `typography.json` before applying it.

- **One source of truth per value.** If the same logical value is needed in multiple
  token files, define it as a named token in the most appropriate file and use a
  `{category.name}` reference in any other file that needs it. Do not paste the same
  literal value into multiple files.

- **Descriptions are required.** Every token must carry a `$description` that explains
  its purpose in one clear sentence. Descriptions are read by developers, designers,
  and AI tooling alike.

---

## What NOT to Do

The following practices undermine the design system and must be avoided.

### ❌ Ad hoc inline styling

Do not apply colors, spacing, or typography as raw values directly in component code,
templates, or scripts:

```python
# Wrong — bypasses the design system
element.style.color = "#C4622D"
element.style.fontSize = "28px"
element.style.margin = "24px"
```

```python
# Correct — reads from tokens
element.style.color = resolve(colors["semantic"]["primary"]["$value"])
element.style.fontSize = resolve(typography["role"]["heading"]["fontSize"]["$value"])
element.style.margin = spacing["spacing"]["5"]["$value"]
```

### ❌ Modifying edition files to embed token values

Token values are *extracted from* edition assets (`visual_dna.json`), not embedded back
into them. Do not edit files inside `editions/` to hard-code design system values. The
edition files are the historical source; the token files are the maintained truth.

### ❌ Duplicating token values across files

Do not copy a hex value, pixel value, or font name from one token file and paste it as a
literal in another. Use `{category.name}` references so that a single edit propagates
to all consumers.

### ❌ Adding tokens without descriptions

A token without a `$description` is a liability. Future contributors — and AI tooling —
rely on descriptions to understand intent. Every new token must have a description before
it is merged.

### ❌ Inventing new visual values outside the token system

Do not introduce a new color, font size, spacing value, or border style anywhere in the
project without first adding it as a named token. If a value is worth using, it is worth
naming and documenting.

### ❌ Implementing components or features in this directory

The `design-system/` directory contains tokens and documentation only. Component
implementation belongs in the future `design-system/components/` layer. Do not add
JavaScript, Python, or rendering logic here.

---

## Constraints

- ❌ Do **not** modify files inside `editions/` directly — token values are *extracted from* edition assets, not embedded in them.
- ❌ Components are **not** implemented here yet — this directory contains structure and initial token extraction only.
- ✅ All token files must remain valid JSON and pass `json.loads()` without error.

---

## Contributing

1. Identify the correct token file for the change (see [How to Add New Tokens](#how-to-add-new-tokens)).
2. Edit the relevant token file under `tokens/`.
3. Keep `$description` fields accurate and up to date.
4. Use token references (`{category.name}`) instead of duplicating literal values.
5. Run the project test suite (`poetry run pytest`) to confirm no regressions.
6. Update this README if new token categories are added.
