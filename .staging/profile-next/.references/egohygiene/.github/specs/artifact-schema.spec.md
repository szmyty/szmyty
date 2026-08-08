# Artifact Schema

## Metadata

- **Spec ID:** `artifact-schema`
- **File Name:** `artifact-schema.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #21
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-28

---

# 1. Purpose

Define what a schema artifact is, what responsibilities it carries, how it relates to specifications and other artifact types, and how it behaves across its lifecycle.

A schema artifact formalizes the structure of data. Where specifications define behavior and intent, schemas define shape and contract. This specification establishes the canonical definition, boundaries, and expectations for schema artifacts at the artifact system layer — independent of implementation technology.

---

# 2. Goals

- Define the canonical purpose and responsibilities of a schema artifact.
- Establish the schema lifecycle including versioning and deprecation.
- Define the relationship between schemas and specifications, domains, and implementations.
- Establish validation expectations for schema artifacts.
- Clarify the distinction between schemas and specifications.

---

# 3. Non-Goals

- This spec does not define any individual schema (e.g., the domain schema or practice schema).
- This spec does not prescribe a specific schema format (e.g., JSON Schema, Protobuf, Avro).
- This spec does not define storage infrastructure.
- This spec does not define application-level validation logic.

---

# 4. Context

Schemas and specifications are often confused. In Ego Hygiene, they serve distinct roles:

- A **specification** defines intent, behavior, and responsibilities.
- A **schema** defines structure, field types, and constraints.

Specifications inform schemas. Schemas constrain implementations. Neither replaces the other.

The artifact system requires a formal definition of schemas as artifacts so that schema evolution can be tracked, validated, and coordinated independently of the specifications that produced them.

---

# 5. Requirements

## 5.1 Functional Requirements

- A schema artifact must formally define the structure of one artifact type.
- A schema artifact must carry a version identifier.
- A schema artifact must define required and optional fields.
- A schema artifact must define field types and constraints.
- A schema artifact must support forward compatibility expectations.
- A schema artifact must document breaking versus non-breaking changes.
- A schema artifact must be validatable against artifact instances.

## 5.2 Non-Functional Requirements

- Schema artifacts must be independent of any specific implementation technology.
- Schema artifacts must be legible to both human readers and AI agents.
- Schema version identifiers must follow a stable versioning convention.
- Schema artifacts must not embed business logic or behavioral rules.

---

# 6. Architecture

## 6.1 Responsibilities

A schema artifact is responsible for:

- Defining the canonical structure of one artifact type.
- Carrying version information to support schema evolution.
- Distinguishing required from optional fields.
- Defining field types and acceptable value ranges or patterns.
- Documenting compatibility expectations across versions.
- Providing a validation contract for implementations.

## 6.2 Relationships

```
Schema
  ← derived from →   Specification Artifacts (specifications produce schema definitions)
  ← formalizes →     Domain Artifacts (schema formalizes domain data structure)
  ← formalizes →     Practice Artifacts (schema formalizes practice data structure)
  ← formalizes →     Research Artifacts (schema may formalize research record structure)
  ← consumed by →    Agent Artifacts (agents validate artifact instances against schemas)
  ← referenced by →  Documentation Artifacts (documentation describes schema expectations)
  ← implemented by → Application Code (implementations must satisfy schema contracts)
```

## 6.3 Lifecycle

```
Draft
  ↓ (initial field definitions proposed)
Review
  ↓ (reviewed for completeness and consistency)
Active
  ↓ (in use by implementations)
Versioned
  ↓ (new version introduced; old version marked deprecated)
Deprecated
  ↓ (scheduled for removal; implementations should migrate)
Retired
  (no longer in use; replaced by newer version)
```

## 6.4 Versioning

Schema versions must follow a consistent pattern:

- Major version: breaking changes (field removals, type changes)
- Minor version: non-breaking additions (new optional fields)
- Patch version: documentation corrections only

Implementations must declare the schema version they satisfy. Schema artifacts must document migration paths for major version changes.

## 6.5 Structural Expectations

A schema artifact should carry:

- A stable identifier
- A schema version
- A list of field definitions (name, type, required/optional, constraints)
- Compatibility notes
- Change history
- Lifecycle status
- Created and updated timestamps

## 6.6 Implementation Independence

Schema artifacts define contracts. They do not specify how those contracts are implemented. A schema may be satisfied by:

- A Dart class with `freezed` and `json_serializable`
- A JSON Schema document
- A Protobuf definition
- A database table definition

The schema artifact is the authoritative contract. The implementation is one expression of that contract.

---

# 7. Implementation Plan

## Phase 1 — Artifact Definition

- [ ] Confirm schema artifact identity and purpose.
- [ ] Document canonical lifecycle stages and versioning conventions.
- [ ] Document relationships to specification, domain, practice, agent, and documentation artifacts.

## Phase 2 — Structural Alignment

- [ ] Confirm structural expectations are sufficient to validate artifact instances.
- [ ] Define the distinction between schemas and specifications clearly.

## Phase 3 — Validation

- [ ] Verify the schema-specification distinction is unambiguous.
- [ ] Verify versioning conventions are consistent with common schema evolution patterns.
- [ ] Verify lifecycle is complete and unambiguous.

---

# 8. Validation Plan

- Verify that no specific schema format is prescribed.
- Verify that all relationships to other artifact types are explicitly stated.
- Confirm versioning conventions are complete and unambiguous.
- Verify the spec is consistent with `specfile.spec.md`.

---

# 9. Acceptance Criteria

- [ ] Schema artifact purpose is clearly defined.
- [ ] Schema lifecycle stages and versioning are documented.
- [ ] The distinction between schemas and specifications is explicit.
- [ ] Relationships to specification, domain, practice, agent, and documentation artifacts are explicit.
- [ ] The spec is consistent with `specfile.spec.md`.
- [ ] The spec remains implementation-independent.

---

# 10. Open Questions

- Should schema artifacts live in a dedicated directory (e.g., `.github/schemas/`) or alongside specs?
- Should schemas be machine-readable (e.g., JSON Schema files) or human-readable markdown?
- How should schema migration be coordinated across multiple implementations?
- Who is responsible for approving breaking schema changes?
