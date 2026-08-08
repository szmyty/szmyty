# Page Schema (v1.1.0)

Canonical schema definition for `page.json` files used across all Ego Hygiene Magazine pages.

---

## Overview

Every page directory inside an edition contains a `page.json` file that drives the
production pipeline.  Starting with **schema version 1.1.0** all new pages should
conform to `schemas/page.schema.json`.

The schema is a [JSON Schema draft-07](https://json-schema.org/draft-07/schema) document.

---

## Schema File

```
schemas/page.schema.json
```

An annotated example conforming to this schema is provided at:

```
schemas/page.schema.example.json
```

---

## Required Fields

| Field            | Type     | Description                                                 |
|------------------|----------|-------------------------------------------------------------|
| `schema_version` | `string` | Must be `"1.1.0"`.                                          |
| `page_id`        | `string` | Unique dot-namespaced identifier (e.g. `"movement.front"`). |
| `page_type`      | `string` | Page type enum — see [Page Types](#page-types) below.       |
| `title`          | `string` | Display title for the page.                                 |
| `edition`        | `object` | Edition metadata block — see [Edition Block](#edition-block) below. |

---

## Page Types

The `page_type` field accepts one of the following canonical values:

| Value               | Description                            |
|---------------------|----------------------------------------|
| `cover_front`       | Front cover (outside)                  |
| `cover_back`        | Back cover (outside)                   |
| `inside_front_cover`| Inside front cover                     |
| `inside_back_cover` | Inside back cover                      |
| `practice_front`    | Front face of a practice page          |
| `practice_back`     | Back face of a practice page           |
| `section_divider`   | Decorative divider between sections    |

> **Migration note:** older pages used values such as `"practice_page"`, `"practice"`,
> and `"front_cover"`.  These are normalised to the canonical values above when pages
> are migrated to v1.1.0.

---

## Edition Block

```json
"edition": {
  "number": 1,
  "name": "Orientation",
  "series": "Ego Hygiene Magazine"
}
```

| Field    | Required | Type      | Description                          |
|----------|----------|-----------|--------------------------------------|
| `number` | ✅        | `integer` | Edition number (1-indexed).          |
| `name`   | ✅        | `string`  | Edition name (e.g. `"Orientation"`). |
| `series` | ❌        | `string`  | Series name.                         |
| `theme`  | ❌        | `string`  | Edition theme (alias for `series`).  |

---

## Optional Blocks

### `intent`

Describes the purpose and tone of the page.

```json
"intent": {
  "role": "somatic_activation_pillar",
  "primary_function": "discharge_accumulated_tension_through_movement",
  "secondary_function": "restore_body_mind_integration",
  "tone": ["activating", "grounded", "embodied"]
}
```

### `visual_style`

Visual design specification including palette, texture, iconography, and typography.

```json
"visual_style": {
  "world": "retro_mystic_field_manual",
  "texture": ["aged_paper", "worn_ink"],
  "color_palette": {
    "primary": ["deep_amber", "burnt_red"],
    "secondary": ["muted_teal"],
    "accent": ["soft_gold_glow"]
  },
  "iconography": ["running_silhouette"],
  "typography": {
    "title": { "style": "bold_distressed_retro_display", "case": "uppercase" }
  }
}
```

### `layout`

Layout and visual composition specification.

```json
"layout": {
  "composition": "central_figure_with_surrounding_instruction_panels",
  "central_element": "running_silhouette",
  "depth_layers": 2,
  "flow": "clockwise_loop",
  "panel_style": {
    "shape": "rounded_rectangle",
    "has_speech_tail": false,
    "appearance": "printed_instructional_panel"
  }
}
```

### `practice_panels` *(canonical practice content)*

Structured instruction panels.  This is the **canonical** format for practice pages
in v1.1.0+.  Each panel represents a discrete step or prompt.

```json
"practice_panels": [
  {
    "id": "breathe",
    "label": "BREATHE",
    "text": "Coordinate breath with movement to synchronize body and mind.",
    "domain": "somatic",
    "modality": "breathwork"
  }
]
```

| Field            | Required | Description                                                |
|------------------|----------|------------------------------------------------------------|
| `id`             | ✅        | Machine-readable identifier.                               |
| `label`          | ✅        | Displayed label (uppercase, e.g. `"BREATHE"`).             |
| `text`           | ✅        | Instructional text shown in the panel.                     |
| `domain`         | ❌        | Psychological or behavioural domain.                       |
| `modality`       | ❌        | Practice modality (`"written"`, `"spoken"`, `"physical"`). |
| `visual_reference` | ❌      | Visual element accompanying the panel.                     |

### `text_elements` *(legacy)*

Freeform keyed text used by older pages.  Accepted for backwards compatibility but
new pages should use `practice_panels` instead.

### `effect_section`

Describes the expected outcome of practising the page.

```json
"effect_section": {
  "label": "EFFECT",
  "text": "Reduces cortisol, activates endorphins, and restores regulatory baseline.",
  "scientific_status": "conceptual_placeholder"
}
```

### `footer_banner`

Affirming or instructional footer message.

```json
"footer_banner": {
  "text": "ANY MOVEMENT COUNTS. YOUR SYSTEM RESPONDS.",
  "tone": "reassuring",
  "intent": "lower_barrier_to_entry"
}
```

### `asset_files`

References to generated asset files.

```json
"asset_files": {
  "master_image": "movement.front.page.png",
  "print_variant": "variants/movement.front.print.png",
  "animation": "movement.front.animation.mp4",
  "prompt": "movement.front.prompt"
}
```

### `image_metadata`

Technical metadata for the master image.

```json
"image_metadata": {
  "format": "PNG",
  "color_mode": "RGB",
  "dimensions_px": { "width": 1024, "height": 1536 },
  "aspect_ratio": "2:3",
  "orientation": "portrait",
  "intended_print_dpi": 300,
  "file_size_bytes": 0,
  "color_profile": "sRGB (assumed)",
  "compression": "lossless_png"
}
```

### `animation_profile`

Animation specification for the digital version.

```json
"animation_profile": {
  "type": "practice_animation",
  "allowed_effects": ["ambient_particle_drift", "grain_breathing"],
  "forbidden_effects": ["camera_movement", "zoom", "parallax"]
}
```

### `print_considerations`

Print-specific metadata.

```json
"print_considerations": {
  "requires_upscale_for_large_format": true,
  "recommended_upscale_factor": "2x"
}
```

### `constraints`

Boolean flags expressing production and content constraints.

```json
"constraints": {
  "no_fitness_culture_aesthetic": true,
  "no_medical_claims": true,
  "preserve_pulp_texture": true
}
```

### `notes`

Freeform contextual notes (any structure).

```json
"notes": {
  "movement_as_regulation_not_exercise": true,
  "pairs_with_rest_practice": true
}
```

---

## Validation

Use any JSON Schema draft-07 validator to check a `page.json` against the schema.

### Python (jsonschema)

```python
import json
from jsonschema import validate

with open("schemas/page.schema.json") as f:
    schema = json.load(f)

with open("editions/edition_1/pages/04_movement/page.json") as f:
    page = json.load(f)

validate(instance=page, schema=schema)
```

### Node.js (ajv)

```js
const Ajv = require("ajv");
const ajv = new Ajv();
const schema = require("./schemas/page.schema.json");
const page   = require("./editions/edition_1/pages/04_movement/page.json");

const valid = ajv.validate(schema, page);
if (!valid) console.error(ajv.errors);
```

---

## Migration Guide (existing pages → v1.1.0)

> ❌ Do **not** migrate existing pages in `editions/` yet.  
> This section is provided for future reference only.

When migrating an existing `page.json` to v1.1.0:

1. Add `"schema_version": "1.1.0"`.
2. Add or rename `page_id` (replacing `practice_id` where used).
3. Normalise `page_type` to one of the canonical enum values.
4. Ensure `edition` contains at least `number` and `name`.
5. Convert `text_elements` panels to `practice_panels` array format.
6. Replace edition-level `theme` with `series` (or keep `theme` as the alias).

---

## Changelog

| Version | Notes                                                                 |
|---------|-----------------------------------------------------------------------|
| 1.1.0   | Canonical schema established. Normalised `page_type` enum, canonical `practice_panels` array, unified `edition` block. |
| 1.0.0   | Implicit schema used in early edition pages (cover, inside cover, practice v1). |
