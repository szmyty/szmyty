# Personal Health Knowledge Engine

Exploratory architecture research for modeling how medications, supplements, nutrition, personal care products, devices, and future lab data fit into a person's health journey.

---

## Overview

The Personal Health Knowledge Engine should help a person understand:

- what they use
- why they use it
- what it contains
- how it relates to other items
- what evidence exists
- what they have personally observed over time

The objective is not diagnosis.

The objective is educational clarity, organization, transparency, and evidence-informed understanding.

This document proposes architecture and ontology direction.

It does not commit the application to a final implementation.

---

## Design Goals

- Model health support as an interconnected system rather than isolated trackers.
- Preserve a clear distinction between evidence, interpretation, and personal observation.
- Support a person's evolving Journey over time rather than only their current inventory.
- Allow AI to assist with summarization and pattern detection without making medical decisions.
- Remain extensible enough to add wearables and laboratory values later.

---

## Proposed Architecture

### Core Flow

```text
Health Item
  ↓
Ingredients / Nutrients / Device Signals
  ↓
Usage + Schedule + Dosage
  ↓
Timeline Events + Personal Observations
  ↓
Interactions + Evidence + Interpretations
  ↓
Health Knowledge Graph
  ↓
Context Assembly + Research Engine + Artifact Generation
```

### Primary Components

#### 1. Health Item

A Health Item is the umbrella concept for anything a person intentionally uses to support health.

Examples:

- prescription medication
- over-the-counter medication
- supplement
- vitamin
- food or meal pattern
- skincare product
- haircare product
- hygiene product
- wearable device
- future laboratory panel

#### 2. Composition Layer

Health Items should decompose into their meaningful components:

- active ingredients
- inactive ingredients when relevant
- nutrients
- device signal types
- laboratory analytes

This allows overlap detection across categories that normally appear unrelated.

Example:

Two products may look different at the product level but share zinc, biotin, salicylic acid, caffeine, or magnesium.

#### 3. Usage Layer

The engine should model:

- dose or amount
- unit
- route
- cadence
- start / stop dates
- adherence confidence
- reason for use

Usage belongs to a person and changes over time.

#### 4. Evidence Layer

External evidence should be stored separately from AI explanations and personal notes.

The system should track:

- claim or question
- source type
- citation metadata
- evidence quality
- evidence direction
- summary
- limitations

#### 5. Observation Layer

Personal observations should capture what a person notices without overstating certainty.

Examples:

- perceived benefit
- side effect
- symptom change
- adherence issue
- timing correlation
- uncertainty

#### 6. Knowledge Graph Layer

A Health Knowledge Graph should connect:

- person ↔ health item
- health item ↔ ingredient
- health item ↔ schedule
- ingredient ↔ ingredient interaction
- health item ↔ observation
- observation ↔ timeline event
- evidence ↔ claim
- claim ↔ ingredient / nutrient / item / outcome

This graph becomes the substrate for search, explanation, AI context assembly, and future visualizations.

---

## Ontology Proposal

The following concepts appear sufficient for an initial ontology extension:

| Concept | Purpose |
|---|---|
| `HealthItem` | Anything intentionally used in support of health |
| `HealthItemCategory` | Prescription, supplement, nutrition, skincare, wearable, lab, etc. |
| `Substance` | Ingredient, nutrient, compound, analyte, or active material |
| `Usage` | Person-specific use of a Health Item across time |
| `Dose` | Amount, unit, route, concentration, or serving size |
| `Schedule` | Frequency, timing, duration, and conditions for use |
| `Observation` | Personal report, effect, symptom, or note tied to usage |
| `Interaction` | Potential relationship between substances, items, or outcomes |
| `Evidence` | External research or reference material supporting or challenging a claim |
| `Interpretation` | AI or human explanation derived from evidence and context |
| `HealthEvent` | Timeline event such as start, stop, skipped dose, symptom change, lab result, or device reading |
| `Outcome` | A state or goal relevant to the person's health journey |

### Ontology Rules

- `Evidence` is not the same as `Interpretation`.
- `Interpretation` is not the same as `Observation`.
- `Observation` may suggest a pattern but should not be treated as proof.
- `Interaction` may be known, suspected, theoretical, or user-observed.
- `HealthItem` is the human-facing entry point, but `Substance` is the cross-category connector.
- `Usage` and `HealthEvent` are time-bound; the ontology should preserve history.

---

## Data Model Proposal

### Suggested Core Records

#### `health_items`

| Field | Notes |
|---|---|
| `id` | Stable identifier |
| `name` | Display name |
| `category` | Item category |
| `brand` | Optional manufacturer / brand |
| `form` | Capsule, cream, meal, shampoo, device, panel |
| `source_type` | user-entered, imported, inferred |
| `notes` | User-facing notes |
| `created_at` / `updated_at` | Audit timestamps |

#### `substances`

| Field | Notes |
|---|---|
| `id` | Stable identifier |
| `canonical_name` | Standard name |
| `substance_type` | active ingredient, nutrient, analyte, compound |
| `aliases` | Alternate names |
| `reference_unit` | mg, mcg, IU, %, etc. |

#### `health_item_substances`

| Field | Notes |
|---|---|
| `health_item_id` | Parent item |
| `substance_id` | Linked substance |
| `role` | active, inactive, nutrient, signal, analyte |
| `amount` | Optional normalized amount |
| `unit` | Optional unit |

#### `usages`

| Field | Notes |
|---|---|
| `id` | Stable identifier |
| `health_item_id` | Item being used |
| `reason_for_use` | Why the person uses it |
| `dose_amount` / `dose_unit` | Person-specific amount |
| `route` | oral, topical, dietary, device-worn, etc. |
| `schedule_type` | daily, as-needed, cycle-based, event-based |
| `started_at` / `ended_at` | Time bounds |
| `adherence_confidence` | Optional self-reported confidence |

#### `health_events`

| Field | Notes |
|---|---|
| `id` | Stable identifier |
| `usage_id` | Related usage |
| `event_type` | taken, skipped, started, stopped, symptom, lab, device |
| `occurred_at` | Time of event |
| `value` | Optional structured value |
| `unit` | Optional unit |
| `source` | user, device, import, system |

#### `observations`

| Field | Notes |
|---|---|
| `id` | Stable identifier |
| `health_event_id` | Related event |
| `observation_type` | benefit, side effect, question, concern, pattern |
| `description` | Free-text observation |
| `confidence` | Self-reported certainty |
| `severity` | Optional scale |

#### `evidence_records`

| Field | Notes |
|---|---|
| `id` | Stable identifier |
| `title` | Paper, review, guideline, database entry |
| `source_type` | RCT, meta-analysis, guideline, monograph, article |
| `citation` | DOI, PMID, URL, publisher info |
| `quality_rating` | low / moderate / high / unknown |
| `summary` | Neutral summary |
| `limitations` | Caveats |

#### `interactions`

| Field | Notes |
|---|---|
| `id` | Stable identifier |
| `left_entity_type` / `left_entity_id` | Item or substance |
| `right_entity_type` / `right_entity_id` | Item, substance, or outcome |
| `interaction_kind` | overlap, depletion, synergy, caution, contraindication |
| `evidence_status` | known, emerging, uncertain, user-observed |
| `notes` | Context |

#### `interpretations`

| Field | Notes |
|---|---|
| `id` | Stable identifier |
| `subject_type` / `subject_id` | Item, substance, interaction, or outcome |
| `evidence_record_id` | Optional backing evidence |
| `generated_by` | AI, clinician-imported, user-authored |
| `summary` | Explanation |
| `disclaimer` | Explicit uncertainty / boundary statement |

---

## Research Strategy

### Phase 1 — Taxonomy Research

Define the minimal category system for:

- medications
- supplements
- vitamins
- nutrition
- skincare
- haircare
- hygiene products
- wearables
- laboratory values

### Phase 2 — Substance Normalization

Research how to normalize:

- active ingredients
- nutrients
- units
- aliases
- formulations

This is required for overlap and interaction analysis.

### Phase 3 — Evidence Framework

Define how evidence quality is represented without overstating certainty.

The engine should be able to say:

- supported by stronger evidence
- mixed evidence
- limited evidence
- anecdotal only
- unknown

### Phase 4 — Personal Observation Framework

Determine how to capture:

- symptom trends
- perceived outcomes
- adherence patterns
- uncertainty
- timeline correlations

without implying diagnosis or causation.

### Phase 5 — AI Safety and Explanation Layer

Research prompts and guardrails for AI assistance:

- summarize evidence
- identify overlapping ingredients
- identify potential interactions
- identify possible nutrient gaps
- explain evidence quality
- surface relevant research papers

AI output should always separate:

1. source evidence
2. system interpretation
3. personal observation

### Phase 6 — Integration Planning

Map how this engine connects to:

- Personal Model
- Context Assembly
- Knowledge Graph
- Journey
- Timeline
- Artifact Generation
- Research Engine
- Learning Paths

---

## AI Integration Boundaries

AI may help:

- summarize research
- explain terminology
- cluster related items
- surface possible overlaps
- highlight uncertainty
- generate follow-up questions

AI must not:

- diagnose conditions
- prescribe treatment
- replace clinician guidance
- present correlation as proof
- hide evidence quality or uncertainty

---

## Recommended Follow-Up GitHub Issues

1. **[Research] Define Personal Health Item taxonomy**
   - Establish categories, boundaries, and examples for items tracked by the engine.
2. **[Research] Design substance normalization model**
   - Define canonical ingredients, aliases, units, and cross-category matching rules.
3. **[Architecture] Specify Health Knowledge Graph relationships**
   - Formalize nodes, edges, temporal links, and query patterns.
4. **[Research] Define evidence quality framework for health claims**
   - Separate evidence strength, claim direction, and uncertainty language.
5. **[Architecture] Design personal observation and timeline event model**
   - Model symptom notes, adherence, outcomes, and correlation-safe event capture.
6. **[AI] Design guarded explanation prompts for health research summaries**
   - Define safe prompt patterns and output sections for evidence, interpretation, and observation.
7. **[Integration] Plan wearable and lab value ingestion architecture**
   - Define future ingestion paths and normalization boundaries for device and lab data.

---

## Open Questions

- What should count as a first-class Health Item versus a subtype of another item?
- How much normalization should happen locally before any external enrichment is considered?
- Which interaction types are safe to surface without increasing user anxiety or false certainty?
- How should nutrition be modeled: individual foods, meals, dietary patterns, or all three?
- Should personal care items always decompose to ingredients, or only when users need that depth?
- What is the minimum evidence schema that still supports transparent AI explanations?

---

## Summary

The Personal Health Knowledge Engine should be modeled as a time-aware knowledge system centered on `HealthItem`, connected through substances, usage, evidence, observations, and interactions.

Its primary value is not tracking inventory.

Its primary value is helping a person understand how their intentional health supports relate to one another across their Journey.
