# Reflection

## Metadata

- **Spec ID:** `reflection`
- **File Name:** `reflection.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #27
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-29

---

# 1. Purpose

Define Reflection as the first complete vertical slice that carries one ontology concept through documentation, schema, application code, storage, state, UI, and validation.

Reflection is the reference implementation for future practices. It must therefore be coherent across artifact layers while remaining small, local-first, and implementation-ready.

---

# 2. Goals

- Define the canonical behavior of a reflection record and reflection workflow.
- Specify the reflection lifecycle from noticed experience to captured record and later review.
- Make relationships to ontology, domains, insights, storage, and AI abstraction points explicit.
- Establish a schema-backed contract that the Flutter domain model satisfies.
- Create a reusable implementation pattern for future practice slices.

---

# 3. Non-Goals

- This spec does not introduce cloud synchronization.
- This spec does not define therapist dashboards or multi-user workflows.
- This spec does not require production AI providers.
- This spec does not define a generalized practice engine for every future practice.

---

# 4. Context

`ONTOLOGY.md` defines Reflection as the capture of conscious awareness of experience and notes that reflections often produce insights.

The repository already contains:

- reflection practice documentation in `docs/practices/reflection/README.md`
- a Flutter feature module in `lib/features/reflection/`
- local-first storage abstractions in `lib/shared/services/`
- placeholder AI service interfaces in `lib/shared/services/insight_*.dart`

This specification makes that implementation intentional and reusable by declaring the Reflection slice contract explicitly.

---

# 5. Requirements

## 5.1 Functional Requirements

- The system must allow a user to create a reflection record locally without network access.
- The system must allow a user to browse saved reflections in reverse-chronological order.
- The system must allow a user to open a reflection detail view.
- Reflection records must serialize to and from a canonical schema-compatible JSON shape.
- Reflection storage must be abstracted behind a repository interface.
- Riverpod providers must expose reflection list and reflection lookup state.
- Reflection must expose AI-ready abstraction points for summarization, theme extraction, coaching, and feedback without binding to production providers.

## 5.2 Non-Functional Requirements

- Reflection must remain local-first and usable offline.
- Reflection models must remain implementation-independent at the schema layer.
- Reflection code must follow feature-first architecture and repository boundaries.
- Reflection behavior must be testable at model, repository, provider, and UI layers.
- Reflection data must remain portable across future storage implementations.

---

# 6. Architecture

## 6.1 Behavior

Reflection behavior is intentionally small in the first slice:

1. A user notices an experience worth examining.
2. The user captures it as a reflection record with body, optional title, and optional tags.
3. The record is stored locally and becomes visible in the reflection list.
4. The record can be reopened in a detail view for review.
5. Optional AI-oriented services may derive summaries, themes, coaching prompts, or feedback later.

## 6.2 Lifecycle

```text
noticed experience
    ↓
captured reflection
    ↓
stored local record
    ↓
reviewed reflection
    ↓
future insight/coaching augmentation
```

The first vertical slice fully implements capture, storage, and review. Augmentation is represented only through abstraction points.

## 6.3 Relationships

```text
Mental & Emotional Health domain
    ↓ anchors
Reflection practice
    ↓ produces
Reflection records
    ↓ may inform
Insights
    ↓ may shape
Future behavior
```

Reflection also relates to:

- `docs/practices/reflection/README.md` as the human-readable artifact
- `schemas/practices/reflection.schema.json` as the structural contract
- `lib/features/reflection/domain/reflection_model.dart` as the Flutter domain expression
- `lib/features/reflection/domain/reflection_repository.dart` as the storage boundary
- `lib/shared/services/insight_summarization_service.dart` and `lib/shared/services/insight_feedback_service.dart` as AI abstraction points

## 6.4 Validation

Validation for Reflection must cover:

- model serialization and value behavior
- repository persistence and ordering behavior
- provider state loading and creation flows
- screen rendering for primary reflection states

Full repository validation should additionally run:

- `fvm flutter analyze`
- `fvm flutter test`
- Android build
- Web build

## 6.5 Future Evolution

Future reflection iterations may add:

- editing and deletion workflows
- structured prompts or templates
- explicit insight entities linked to reflections
- richer filtering, search, and timelines
- production AI providers behind the existing service abstractions
- migration from key-value persistence to a structured local database

These additions must preserve schema compatibility or version the schema explicitly when compatibility changes.

---

# 7. Implementation Plan

## Phase 1 — Artifact Synchronization

- [ ] Align reflection documentation with ontology language.
- [ ] Create the canonical reflection schema artifact.
- [ ] Create the reflection specification artifact.

## Phase 2 — Application Slice

- [ ] Keep the Flutter reflection model aligned with the schema contract.
- [ ] Keep local-first repository and Riverpod providers as the implementation boundary.
- [ ] Keep reflection UI focused on list, detail, and creation workflows.
- [ ] Preserve AI integration as abstraction points only.

## Phase 3 — Validation

- [ ] Maintain model, repository, provider, and screen tests.
- [ ] Run repository validation commands and required platform builds.

---

# 8. Validation Plan

- Review `docs/practices/reflection/README.md` against `ONTOLOGY.md`.
- Verify the schema and Flutter domain model describe the same fields.
- Verify repository and provider tests cover local-first behavior.
- Verify screen tests cover empty and populated reflection states.
- Run analyze, tests, Android build, and Web build when the Flutter toolchain is available.

---

# 9. Acceptance Criteria

- [ ] Reflection is consistent across ontology, documentation, schema, specification, and implementation.
- [ ] Reflection follows repository architecture and storage abstractions.
- [ ] Reflection supports local-first persistence and Riverpod state integration.
- [ ] Reflection UI supports list, detail, and creation flows.
- [ ] Reflection exposes AI abstraction points without real providers.
- [ ] Reflection tests cover model, storage, provider, and primary UI states.

---

# 10. Open Questions

- Should the canonical reflection schema eventually include explicit insight identifiers?
- Should reflection editing be part of the reference slice or a follow-up iteration?
- When Reflection migrates to Drift, should the JSON schema remain the portability contract?
