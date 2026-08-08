# Artifact Domain

## Metadata

- **Spec ID:** `artifact-domain`
- **File Name:** `artifact-domain.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #21
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-28

---

# 1. Purpose

Define what a domain artifact is, what responsibilities it carries, how it relates to other artifacts, and how it behaves across its lifecycle.

A domain is the highest-level organizational unit within Ego Hygiene. It represents a major area of life that a person actively maintains over time. This specification establishes the canonical definition, boundaries, and expectations for domain artifacts at the artifact system layer — not the implementation layer.

---

# 2. Goals

- Define the canonical purpose and responsibilities of a domain artifact.
- Establish lifecycle stages for a domain artifact.
- Define relationships between domains and other artifact types.
- Specify schema expectations for domain data without prescribing implementation.
- Establish validation expectations for domain artifacts.

---

# 3. Non-Goals

- This spec does not define individual domain content (e.g., Finance, Health).
- This spec does not prescribe implementation technology (e.g., Dart classes, database tables).
- This spec does not define practice logic, insight logic, or schema format.
- This spec does not replace `domain-framework.spec.md`, which addresses implementation-level concerns.

---

# 4. Context

Ego Hygiene is structured around the philosophy that human life is organized into broad, interconnected areas. Domains are the formalization of that philosophy into a navigable, maintainable artifact.

Domains sit above practices and insights in the knowledge hierarchy. They provide the organizing context that gives practices and insights meaning. Without domains, practices float without purpose and insights lack coherence.

The artifact system requires a definition of domain artifacts that is independent of the technology used to represent or persist them. This spec provides that definition.

---

# 5. Requirements

## 5.1 Functional Requirements

- A domain artifact must represent one major area of life maintained by a person over time.
- A domain artifact must have a stable, human-readable identifier.
- A domain artifact must carry a clear statement of purpose.
- A domain artifact must document its relationships to associated practices.
- A domain artifact must support lifecycle transitions from definition through active use to archival.
- A domain artifact must be representable in both documentation and application contexts.

## 5.2 Non-Functional Requirements

- Domain identifiers must remain stable across artifact versions.
- Domain artifacts must be independent of any specific storage technology.
- Domain artifacts must be legible to both human readers and AI agents.
- Domain artifacts must not embed implementation-specific details.

---

# 6. Architecture

## 6.1 Responsibilities

A domain artifact is responsible for:

- Representing a major life area at the philosophical and organizational level.
- Providing an anchor for associated practices and insights.
- Carrying enough context for a human or AI agent to understand its purpose without additional documentation.
- Remaining stable as a reference point across application evolution.

## 6.2 Relationships

```
Domain
  ← owns →    Practices (one domain has many practices)
  ← produces → Insights (practices within a domain produce domain-level insights)
  ← expressed via → Schema (domain structure is formalized in a schema artifact)
  ← guided by → Specification (domain behavior is described in a specification artifact)
  ← documented in → Documentation (domain knowledge is captured in documentation artifacts)
```

## 6.3 Lifecycle

```
Concept
  ↓ (identified as a distinct life area)
Draft
  ↓ (name, purpose, and initial practices defined)
Active
  ↓ (in use within application and practice system)
Refined
  ↓ (boundaries clarified, practices stabilized)
Archived
  (no longer actively maintained or superseded)
```

## 6.4 Schema Expectations

A domain artifact should carry:

- A stable identifier (kebab-case string)
- A display name
- A one-sentence purpose statement
- A list of associated practice identifiers
- Optional classification tags
- Lifecycle status
- Created and updated timestamps

The schema artifact for domains provides the formal structure. The domain artifact instance satisfies that schema.

## 6.5 Implementation Expectations

Domain artifacts are implementation-independent at this layer. However, implementations are expected to:

- Serialize domain artifacts to and from a standard data format.
- Enforce schema validation at read and write boundaries.
- Provide stable lookup by identifier.
- Support association with related practice and insight artifacts.

---

# 7. Implementation Plan

## Phase 1 — Artifact Definition

- [ ] Confirm domain artifact identity and purpose.
- [ ] Document canonical lifecycle stages.
- [ ] Document relationships to practice, insight, schema, and specification artifacts.

## Phase 2 — Schema Alignment

- [ ] Align domain artifact structure with the artifact-schema spec.
- [ ] Confirm schema fields are implementation-independent.

## Phase 3 — Validation

- [ ] Verify this spec is consistent with `domain-framework.spec.md`.
- [ ] Verify all relationships are explicitly documented.
- [ ] Verify lifecycle is complete and unambiguous.

---

# 8. Validation Plan

- Review this spec against `domain-framework.spec.md` for consistency.
- Verify that no implementation-specific technology is referenced in this spec.
- Verify that all relationships to other artifact types are explicitly stated.
- Confirm lifecycle stages are complete, ordered, and unambiguous.

---

# 9. Acceptance Criteria

- [ ] Domain artifact purpose is clearly defined.
- [ ] Domain lifecycle stages are documented.
- [ ] Relationships to practice, insight, schema, specification, and documentation artifacts are explicit.
- [ ] Schema expectations are described without prescribing implementation.
- [ ] The spec is consistent with `specfile.spec.md`.
- [ ] The spec remains implementation-independent.

---

# 10. Open Questions

- Should domains support hierarchical nesting (e.g., sub-domains)?
- Should domain artifacts carry priority or ordering metadata?
- How are deprecated domains distinguished from archived domains?
