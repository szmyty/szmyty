# Editorial Constraints (`context/constraints.json`)

## Purpose

`context/constraints.json` is the canonical **editorial constraint manifest** for Ego Hygiene Magazine.

It defines the boundaries that every AI-generated asset, page schema, and creative prompt must respect.  The file acts as a single source of truth for the core creative and ethical rules of the publication, preventing drift across editions and tools.

It is **not executed by the pipeline** — it is a **reference document** consulted when:

- Writing or reviewing AI generation prompts (e.g. Canva, Midjourney, or Ollama prompts)
- Authoring or auditing `page.json` schemas
- Extending or updating the IP lint check (`scripts/lint_ip_references.py`)
- Onboarding contributors to the Ego Hygiene aesthetic and tone

---

## File Location

```
context/constraints.json
```

---

## Structure

The file contains four top-level arrays, each expressing a distinct category of constraint.

### `forbidden_ip_references`

Named external intellectual properties that must **never** appear in any generated asset, schema, prompt, or derivative work.

```json
"forbidden_ip_references": [
  "fallout",
  "blade runner",
  "dune",
  "mad max",
  "neuromancer"
]
```

These terms are a superset of the terms enforced by `scripts/lint_ip_references.py`.  When a new term is added here, it should also be added to the lint script so that CI enforcement stays in sync.

See [`docs/IP_LINT_CHECK.md`](IP_LINT_CHECK.md) for guidance on allowed replacement language.

---

### `mandatory_tone_markers`

Tonal qualities that every page must embody.  Use these as positive guidance when writing or evaluating AI prompts and copy.

```json
"mandatory_tone_markers": [
  "non-prescriptive",
  "grounding",
  "collectible",
  "calm",
  "nervous-system aware"
]
```

A page or prompt that contradicts these markers (e.g. is prescriptive, anxiety-inducing, or disposable in feel) should be revised before use.

---

### `style_invariants`

Visual and aesthetic rules that apply to every page, regardless of the specific practice or section.

```json
"style_invariants": [
  "retro_print_aesthetic",
  "aged_paper_texture",
  "field_manual_tone",
  "mid_20th_century_pulp_inspiration",
  "post_collapse_mystic_without_franchise_reference"
]
```

These invariants are aligned with `visual_dna.json` at the edition level.  Any page whose visual style deviates from these invariants should be flagged during review.

---

### `conceptual_guardrails`

Content and conceptual boundaries that protect readers and preserve the Ego Hygiene ethos.

```json
"conceptual_guardrails": [
  "no_medical_claims",
  "no_spiritual_superiority",
  "no_required_actions",
  "no_productivity_optimization",
  "balance_over_achievement"
]
```

These guardrails apply to both written copy and visual framing.  A page that implies clinical efficacy, moral hierarchy, or compulsory practice violates this boundary and must be revised.

---

## How to Use This File

### During AI Prompt Authoring

When writing a Canva, Midjourney, Ollama, or other AI generation prompt, check the prompt against all four sections:

1. Does the prompt contain or imply any `forbidden_ip_references`?
2. Does the output embody the `mandatory_tone_markers`?
3. Does the visual direction align with the `style_invariants`?
4. Does the copy and framing respect the `conceptual_guardrails`?

### During Schema Authoring (`page.json`)

When writing the `intent`, `visual_style`, and `practice_panels` blocks for a new page, use the constraints as a review checklist before committing the schema.

### During IP Lint Script Updates

When extending `scripts/lint_ip_references.py` with new forbidden terms, cross-reference `forbidden_ip_references` here to ensure the lint list is a complete superset of this manifest.

### During Edition Audits

Automated and manual audits should verify that each page in an edition conforms to all four constraint categories.

---

## Relationship to Other Files

| File | Relationship |
|------|-------------|
| `scripts/lint_ip_references.py` | Enforces a subset of `forbidden_ip_references` via CI |
| `editions/edition_1/visual_dna.json` | Edition-level visual identity; `style_invariants` here should be consistent with it |
| `schemas/page.schema.json` | Page-level schema; `conceptual_guardrails` apply to content fields within it |
| `docs/IP_LINT_CHECK.md` | Explains how the IP lint check works and the vocabulary of allowed alternatives |
| `docs/EXAMPLE_WORKFLOW.md` | Demonstrates constraint-aware page authoring in practice |

---

## Updating This File

Changes to `context/constraints.json` represent a **change to the editorial identity** of Ego Hygiene Magazine and should be treated with care:

- Adding a `forbidden_ip_reference` — also update `scripts/lint_ip_references.py` and `docs/IP_LINT_CHECK.md`
- Changing `mandatory_tone_markers` — review existing pages for compliance
- Changing `style_invariants` — review `visual_dna.json` and existing page schemas for consistency
- Changing `conceptual_guardrails` — review existing copy in `practice_panels` fields across all editions
