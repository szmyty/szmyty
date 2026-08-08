# Artifact Practice

## Metadata

- **Spec ID:** `artifact-practice`
- **File Name:** `artifact-practice.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #21
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-28

---

# 1. Purpose

Define what a practice artifact is, what responsibilities it carries, how it relates to domain artifacts and other artifact types, and how it behaves across its lifecycle.

A practice is the active layer of Ego Hygiene. Where domains describe areas of life, practices describe what a person actually does. This specification establishes the canonical definition, boundaries, and expectations for practice artifacts at the artifact system layer — independent of implementation.

---

# 2. Goals

- Define the canonical purpose and responsibilities of a practice artifact.
- Establish lifecycle stages for a practice artifact.
- Define the relationship between practices and domains.
- Specify schema expectations for practice data without prescribing implementation.
- Establish validation expectations for practice artifacts.

---

# 3. Non-Goals

- This spec does not define individual practice content (e.g., specific journaling workflows).
- This spec does not prescribe implementation technology.
- This spec does not define scheduling, notification, or reminder infrastructure.
- This spec does not replace `practice-framework.spec.md`, which addresses implementation-level concerns.

---

# 4. Context

Practices are the bridge between philosophy and behavior in Ego Hygiene. A domain defines the area of life; a practice defines the recurring action taken within that area.

The relationship between practices and domains is foundational:

```
Domain
  ↓
Practices
  ↓
Behavior
  ↓
Insight
```

Without practices, domains remain abstract. Without domains, practices lack context. This artifact spec defines the practice layer of that relationship independent of technology.

---

# 5. Requirements

## 5.1 Functional Requirements

- A practice artifact must represent one recurring behavior performed within a domain.
- A practice artifact must have a stable, human-readable identifier.
- A practice artifact must carry a clear purpose statement and instructions.
- A practice artifact must be associated with one or more domain artifacts.
- A practice artifact must support a configurable frequency (e.g., daily, weekly).
- A practice artifact must support completion tracking as a first-class concern.
- A practice artifact must carry enough context to be performed without additional documentation.

## 5.2 Non-Functional Requirements

- Practice identifiers must remain stable across artifact versions.
- Practice artifacts must be independent of any specific storage technology.
- Practice artifacts must be legible to both human readers and AI agents.
- Practice artifacts must not embed implementation-specific details.

---

# 6. Architecture

## 6.1 Responsibilities

A practice artifact is responsible for:

- Representing a single recurring action at the behavioral level.
- Anchoring to one or more domain artifacts for organizational context.
- Carrying instructional content sufficient to perform the practice.
- Recording completion state as part of its lifecycle.
- Providing the foundation for insight generation through completion history.

## 6.2 Relationships

```
Practice
  ← belongs to →  Domain (one or more domains own this practice)
  ← produces →    Insights (completion patterns produce insight artifacts)
  ← expressed via → Schema (practice structure is formalized in a schema artifact)
  ← guided by →   Specification (practice behavior is described in a specification artifact)
  ← documented in → Documentation (practice knowledge is captured in documentation artifacts)
  ← tracked by →  Completion Records (each execution is a separate record)
```

## 6.3 Lifecycle

```
Concept
  ↓ (identified as a meaningful recurring behavior)
Draft
  ↓ (purpose, instructions, and domain associations defined)
Active
  ↓ (in use within the application and completion system)
Refined
  ↓ (instructions, frequency, and domain links stabilized)
Archived
  (no longer practiced or superseded by another practice)
```

## 6.4 Schema Expectations

A practice artifact should carry:

- A stable identifier (kebab-case string)
- A display name
- A purpose statement
- Step-by-step instructions
- A list of associated domain identifiers
- A frequency descriptor (daily, weekly, monthly, as-needed)
- An estimated duration
- Lifecycle status
- Created and updated timestamps

The schema artifact for practices provides the formal structure. The practice artifact instance satisfies that schema.

## 6.5 Implementation Expectations

Practice artifacts are implementation-independent at this layer. However, implementations are expected to:

- Serialize practice artifacts to and from a standard data format.
- Enforce schema validation at read and write boundaries.
- Support lookup by identifier and filtering by domain.
- Record completions with timestamps for history and insight generation.

---

# 7. Implementation Plan

## Phase 1 — Artifact Definition

- [ ] Confirm practice artifact identity and purpose.
- [ ] Document canonical lifecycle stages.
- [ ] Document relationships to domain, insight, schema, and specification artifacts.

## Phase 2 — Schema Alignment

- [ ] Align practice artifact structure with the artifact-schema spec.
- [ ] Confirm schema fields are implementation-independent.

## Phase 3 — Validation

- [ ] Verify this spec is consistent with `practice-framework.spec.md`.
- [ ] Verify all relationships are explicitly documented.
- [ ] Verify lifecycle is complete and unambiguous.

---

# 8. Validation Plan

- Review this spec against `practice-framework.spec.md` for consistency.
- Verify that no implementation-specific technology is referenced in this spec.
- Verify that all relationships to other artifact types are explicitly stated.
- Confirm lifecycle stages are complete, ordered, and unambiguous.

---

# 9. Acceptance Criteria

- [ ] Practice artifact purpose is clearly defined.
- [ ] Practice lifecycle stages are documented.
- [ ] Relationships to domain, insight, schema, specification, and documentation artifacts are explicit.
- [ ] Schema expectations are described without prescribing implementation.
- [ ] The spec is consistent with `specfile.spec.md`.
- [ ] The spec remains implementation-independent.

---

# 10. Open Questions

- Should practice artifacts carry versioned instructions to support behavioral evolution over time?
- How are practice completion records scoped — per user, per device, or globally?
- Should practices support branching (e.g., multiple variants of the same practice)?
- How should practices relate to each other when they share a domain?
