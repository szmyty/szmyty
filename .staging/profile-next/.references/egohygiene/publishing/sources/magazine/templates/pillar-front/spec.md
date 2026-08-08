# PillarFrontTemplate — Layout Specification

**Reference source:** `references/edition_1/pillar/movement.png`  
**Template ID:** `pillar-front`  
**Page type:** `practice_front` (pillar variant)  
**Aspect ratio:** 2:3 (portrait)  
**Canonical dimensions:** 2063 × 3150 px (300 dpi print-safe)

---

## Purpose

`PillarFrontTemplate` is the primary reusable layout for all pillar front pages in
Ego Hygiene Magazine.  A *pillar* page introduces a core regulation practice
(e.g. Movement, Rest, Presence) through a consistent visual grammar: a symbolic
header, a dominant central illustration, four flanking action cards, a full-width
effect summary, and an affirming closing statement.

This spec defines the structural template only.  It does not implement components
or modify any existing edition assets.

---

## Full Layout Description

The page is divided into six horizontal bands stacked top-to-bottom.  The central
band is the tallest and houses both the illustration and the four action cards in a
single composite zone.

```
┌─────────────────────────────────────┐
│           [1] TOP SYMBOL            │  ~4 % of page height
├─────────────────────────────────────┤
│             [2] TITLE               │  ~12 %
├─────────────────────────────────────┤
│           [3] SUBTITLE              │  ~5 %
├──────────────┬──────────────────────┤
│  [4a] CARD   │                      │
│  top-left    │  [5] CENTRAL         │  ~38 %
├──────────────┤  ILLUSTRATION        │
│  [4b] CARD   │                      │
│  bot-left    ├──────────────────────┤
│              │  [4c] CARD top-right │
│              ├──────────────────────┤
│              │  [4d] CARD bot-right │
├──────────────┴──────────────────────┤
│           [6] EFFECT PANEL          │  ~16 %
├─────────────────────────────────────┤
│        [7] CLOSING STATEMENT        │  ~10 %
├─────────────────────────────────────┤
│         [8] DECORATIVE BASE         │  ~15 %
└─────────────────────────────────────┘
```

Cards [4a–4d] form a 2 × 2 grid that wraps the left and right edges of the
central illustration.  The illustration occupies the vertical centre of the
composite zone; the cards are inset so their outer edges align with the page
margin.

---

## Template Slots

| Slot ID              | Label               | Zone in layout       | Required |
|----------------------|---------------------|----------------------|----------|
| `top_symbol`         | Top Symbol          | Band 1               | ✅        |
| `title`              | Title               | Band 2               | ✅        |
| `subtitle`           | Subtitle            | Band 3               | ✅        |
| `card_top_left`      | Action Card 1       | Band 4 — top-left    | ✅        |
| `card_bottom_left`   | Action Card 2       | Band 4 — bottom-left | ✅        |
| `card_top_right`     | Action Card 3       | Band 4 — top-right   | ✅        |
| `card_bottom_right`  | Action Card 4       | Band 4 — bottom-right| ✅        |
| `central_illustration` | Central Illustration | Band 5            | ✅        |
| `effect_panel`       | Effect Panel        | Band 6               | ✅        |
| `closing_statement`  | Closing Statement   | Band 7               | ✅        |
| `decorative_base`    | Decorative Base     | Band 8               | ❌        |

---

## Slot Descriptions

### `top_symbol`

A single decorative icon centred at the very top of the page, above the title.
It functions as a symbolic anchor that frames the pillar's thematic identity.

- **Visual treatment:** small, centred, high-contrast against the background
- **Typography:** none (icon only)
- **Reference instance:** infinity symbol (∞) — representing cyclical
  self-regulation without terminus
- **Constraints:** must not contain text; must remain unambiguous at small size

---

### `title`

The pillar name rendered as the dominant typographic element of the page.

- **Visual treatment:** bold distressed retro display face, uppercase, amber-to-red
  gradient or single warm accent colour, large tracking
- **Typography:** hierarchy rank 1 — largest text on the page
- **Content type:** single word or short phrase (e.g. `MOVEMENT`)
- **Constraints:** uppercase only; no more than ~12 characters to preserve scale

---

### `subtitle`

A secondary line of text positioned immediately below the title that names the
practice domain.

- **Visual treatment:** retro serif or small-caps sans, lighter weight than title,
  centred, moderate tracking
- **Typography:** hierarchy rank 2
- **Content type:** short descriptive phrase (e.g. `PRACTICES FOR NERVOUS SYSTEM
  REGULATION`)
- **Constraints:** sentence case or all-caps; kept to one line where possible

---

### `card_top_left`

The first of four action cards; positioned to the upper-left of the central
illustration.

- **Visual treatment:** rounded rectangle panel with a warm amber border; bold
  card label (uppercase) followed by a short instructional sentence in a lighter
  serif weight; slight aged-paper fill
- **Typography:** card label at hierarchy rank 3; body text at rank 4
- **Content fields:**
  - `label` — short action word (e.g. `MOVE`)
  - `text` — one to two instructional sentences
- **Constraints:** label must be a single imperative word; text must fit within
  the panel without overflow at the canonical canvas size

---

### `card_bottom_left`

The second action card; positioned to the lower-left of the central illustration.
Identical structural treatment to `card_top_left`.

- **Content fields:** `label`, `text`
- **Reference instance:** label `STRETCH`, text about easing tension without
  forcing range

---

### `card_top_right`

The third action card; positioned to the upper-right of the central illustration.
Mirrors `card_top_left` in structure and visual treatment.

- **Content fields:** `label`, `text`
- **Reference instance:** label `MOBILIZE`, text about inviting gentle range and
  circulation

---

### `card_bottom_right`

The fourth action card; positioned to the lower-right of the central illustration.
Mirrors `card_bottom_left` in structure and visual treatment.

- **Content fields:** `label`, `text`
- **Reference instance:** label `RELEASE`, text about allowing excess activation
  to discharge

---

### `central_illustration`

The dominant visual element of the page: a full-body figurative illustration
centred in the composite action zone.  It is flanked on both sides by the four
action cards.

- **Visual treatment:** luminous silhouette of a standing human figure with
  motion-echo trails (ghosted repeated figures); warm amber/orange inner glow
  emanating from the figure; cosmic or starfield dark background
- **Composition:** figure centred on the vertical axis; glow diffuses outward to
  bleed into card zones; motion echoes extend laterally to suggest kinaesthetic
  breadth
- **Constraints:** must be figurative (human or humanoid); no text embedded in
  the illustration; must remain legible as a silhouette if colour is removed

---

### `effect_panel`

A full-width panel below the action grid that summarises the physiological or
psychological outcome of the practice.

- **Visual treatment:** wide rounded rectangle, matching card aesthetic but wider;
  prominent `EFFECT` label centred at the top of the panel; body text beneath in
  lighter serif; optional small icon (e.g. brain glyph) inset to the right
- **Typography:** `EFFECT` label at hierarchy rank 3; body text at rank 4
- **Content fields:**
  - `label` — always `EFFECT`
  - `text` — one to three sentences describing the expected outcome
  - `icon` (optional) — a small symbolic illustration inside the panel
- **Constraints:** `label` is fixed as `EFFECT`; text must avoid clinical or
  prescriptive language per editorial guardrails

---

### `closing_statement`

A full-width affirming declaration printed below the effect panel, functioning as
the emotional resolution of the page.

- **Visual treatment:** bold retro caps, warm accent colour, centred, large
  tracking; may wrap across two lines if needed
- **Typography:** hierarchy rank 5 — prominent but subordinate to the title
- **Content type:** short declarative sentence or two-part phrase
  (e.g. `MOVE YOUR BODY.  CALM YOUR MIND.  FEEL AT HOME IN YOURSELF.`)
- **Constraints:** uppercase; affirming tone; no prescriptive or conditional
  language; no more than ~60 characters per line

---

### `decorative_base`

Ornamental elements anchoring the very bottom of the page.  Optional but strongly
recommended for the retro-print aesthetic.

- **Visual treatment:** crystal or mineral formations at the lower-left and
  lower-right corners; aged-paper burn and grain applied to the bottom edge;
  elements should not obscure the closing statement
- **Content type:** purely decorative — no text, no semantic content
- **Constraints:** must not introduce any IP-protected iconography; forms should
  feel geological or botanical rather than technological

---

## Slot Composition Summary

```
top_symbol
    ↓
title
    ↓
subtitle
    ↓
[ card_top_left  |  central_illustration  |  card_top_right  ]
[ card_bottom_left                        |  card_bottom_right ]
    ↓
effect_panel
    ↓
closing_statement
    ↓
decorative_base  (optional)
```

---

## Visual Grammar Notes

- All card slots share identical structural markup (label + body text + rounded
  panel); only their content and horizontal position differ.
- The `central_illustration` bleeds visually into the card zones through its glow
  and motion-echo treatment — the illustration is not strictly bounded.
- The overall page reads top-to-bottom as: *identity → practice → outcome →
  affirmation*.
- Texture, grain, and aged-paper effects are applied at the page level, not per
  slot — individual slots do not own their own texture treatment.
- The colour temperature of the page shifts slightly from cooler amber at the top
  to warmer burnt-red at the base, creating a grounding visual flow.

---

## Relationship to Other Files

| File | Relationship |
|------|-------------|
| `references/edition_1/pillar/movement.png` | Primary visual reference from which this spec was extracted |
| `editions/edition_1/pages/04_movement/page.json` | Content instance that populates this template's slots |
| `schemas/page.schema.json` | JSON Schema whose fields map to individual slot content fields |
| `docs/PAGE_SCHEMA.md` | Documentation of the page schema; `practice_panels` maps to the four action card slots |
| `context/constraints.json` | Editorial constraints that apply to all slot content |
