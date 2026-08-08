# Artifact Documentation

## Metadata

- **Spec ID:** `artifact-documentation`
- **File Name:** `artifact-documentation.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #21
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-28

---

# 1. Purpose

Define what a documentation artifact is, what responsibilities it carries, how it organizes knowledge within the repository, and how it supports long-term maintenance.

Documentation artifacts preserve understanding at the human layer. Where specifications define behavior and schemas define structure, documentation communicates purpose, context, and guidance to humans navigating the repository. This specification establishes the canonical definition, boundaries, and expectations for documentation artifacts at the artifact system layer.

---

# 2. Goals

- Define the canonical purpose and responsibilities of a documentation artifact.
- Establish a knowledge hierarchy that organizes documentation across the repository.
- Define the relationship between documentation and other artifact types.
- Establish repository organization expectations for documentation.
- Define long-term maintenance responsibilities.

---

# 3. Non-Goals

- This spec does not define the content of any specific documentation file.
- This spec does not prescribe documentation tooling or output formats.
- This spec does not replace existing top-level documents (PURPOSE.md, MANIFESTO.md, etc.).
- This spec does not define how specifications are written (see `specfile.spec.md`).

---

# 4. Context

The Ego Hygiene repository treats itself as a knowledge system. Code is a downstream artifact. The primary artifacts that carry meaning are philosophical documents, specifications, schemas, and documentation.

Documentation artifacts serve a distinct role from specifications. Specifications define what should be built. Documentation explains what exists, why it exists, and how to use it. Both are necessary. Neither replaces the other.

The repository already contains multiple layers of documentation:

- Philosophy layer: PURPOSE.md, MANIFESTO.md, PRINCIPLES.md, VISION.md
- Architecture layer: ARCHITECTURE.md, SYSTEM.md, DESIGN.md, FOUNDATIONS.md
- Operational layer: ROADMAP.md, ONBOARDING.md
- Domain layer: docs/domains/, docs/practices/, docs/research/

This spec provides the artifact-level definition that unifies and clarifies these layers.

---

# 5. Requirements

## 5.1 Functional Requirements

- A documentation artifact must serve a clearly identifiable audience (e.g., new contributors, AI agents, domain experts).
- A documentation artifact must carry a purpose statement explaining why it exists.
- A documentation artifact must remain accurate as the repository evolves.
- A documentation artifact must reference related specifications, schemas, and other documents.
- A documentation artifact must be organized within the established repository knowledge hierarchy.
- Documentation artifacts must not duplicate information already captured in specifications.

## 5.2 Non-Functional Requirements

- Documentation artifacts must be legible to both human readers and AI agents.
- Documentation artifacts must use consistent formatting within their layer.
- Documentation artifacts must be maintainable with minimal effort.
- Documentation artifacts must degrade gracefully — partial documentation is better than no documentation.

---

# 6. Architecture

## 6.1 Responsibilities

A documentation artifact is responsible for:

- Communicating purpose, context, and guidance to a specific audience.
- Preserving decisions and rationale across development cycles.
- Providing navigation context within the repository knowledge hierarchy.
- Staying synchronized with the specifications and implementations it describes.
- Reducing onboarding time for new contributors and AI agents.

## 6.2 Relationships

```
Documentation
  ← describes →     Specification Artifacts (documentation explains specification intent)
  ← references →    Schema Artifacts (documentation describes data structures)
  ← surfaces →      Research Artifacts (documentation may summarize research findings)
  ← guides →        Agent Artifacts (agents consume documentation as context)
  ← supports →      Domain Artifacts (documentation provides domain-level knowledge)
  ← supports →      Practice Artifacts (documentation provides practice instructions)
  ← anchored by →   Philosophy Layer (PURPOSE.md, MANIFESTO.md, PRINCIPLES.md, VISION.md)
```

## 6.3 Knowledge Hierarchy

Documentation in this repository is organized into layers:

```
Layer 1 — Philosophy
  PURPOSE.md, MANIFESTO.md, PRINCIPLES.md, VISION.md
  (Why this repository exists)

Layer 2 — Architecture
  ARCHITECTURE.md, SYSTEM.md, DESIGN.md, FOUNDATIONS.md
  (How the system is structured)

Layer 3 — Operations
  ROADMAP.md, ONBOARDING.md
  (How work is organized and executed)

Layer 4 — Domains
  docs/domains/
  (What life areas are defined)

Layer 5 — Practices
  docs/practices/
  (What behaviors are defined within domains)

Layer 6 — Research
  docs/research/
  (What is being investigated)

Layer 7 — Specifications
  .github/specs/
  (What should be built and how)
```

Each layer supports the layers below it without replacing them. The philosophy layer is the most stable. The specification layer is the most frequently updated.

## 6.4 Lifecycle

```
Draft
  ↓ (initial content captured)
Active
  ↓ (in use; referenced by contributors and AI agents)
Stale
  ↓ (content is outdated but not yet updated)
Updated
  ↓ (synchronized with current repository state)
Archived
  (content preserved for historical reference; no longer authoritative)
```

## 6.5 Repository Organization

Documentation artifacts live in their layer-appropriate location:

- Philosophy documents: repository root
- Architecture documents: repository root
- Operational documents: repository root
- Domain documentation: `docs/domains/`
- Practice documentation: `docs/practices/`
- Research documentation: `docs/research/`
- Specification files: `.github/specs/`
- Agent files: `.github/agents/`

Documentation artifacts must not be placed outside their designated layer location without a documented reason.

## 6.6 Long-Term Maintenance

Documentation maintenance follows these principles:

- Documentation is a living artifact — it must evolve with the repository.
- Stale documentation is worse than no documentation because it misleads.
- AI agents are responsible for flagging stale documentation during execution.
- Humans are responsible for approving documentation updates.
- Documentation updates that accompany implementation changes are required, not optional.

---

# 7. Implementation Plan

## Phase 1 — Artifact Definition

- [ ] Confirm documentation artifact identity and purpose.
- [ ] Document canonical lifecycle stages.
- [ ] Document the knowledge hierarchy and layer organization.
- [ ] Document relationships to specification, schema, research, and agent artifacts.

## Phase 2 — Hierarchy Validation

- [ ] Verify existing repository documentation maps correctly to the knowledge hierarchy.
- [ ] Identify any gaps or misplaced documentation.

## Phase 3 — Maintenance Protocol

- [ ] Define the staleness detection process.
- [ ] Define the update responsibility model (AI flags, human approves).

---

# 8. Validation Plan

- Verify that existing repository documentation is consistent with the knowledge hierarchy.
- Verify that all relationships to other artifact types are explicitly stated.
- Verify the lifecycle stages are complete and unambiguous.
- Verify the spec is consistent with `specfile.spec.md`.

---

# 9. Acceptance Criteria

- [ ] Documentation artifact purpose is clearly defined.
- [ ] Knowledge hierarchy with layers is documented.
- [ ] Repository organization expectations are explicit.
- [ ] Long-term maintenance responsibilities are defined.
- [ ] Relationships to specification, schema, research, agent, domain, and practice artifacts are explicit.
- [ ] The spec is consistent with `specfile.spec.md`.
- [ ] The spec remains implementation-independent.

---

# 10. Open Questions

- Should documentation artifacts carry an explicit staleness date beyond which they must be reviewed?
- How should documentation conflicts between layers be resolved?
- Should AI agents be required to update documentation as part of every implementation cycle?
- How should the repository surface documentation coverage gaps?
