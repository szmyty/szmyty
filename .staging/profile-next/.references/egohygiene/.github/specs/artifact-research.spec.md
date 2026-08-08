# Artifact Research

## Metadata

- **Spec ID:** `artifact-research`
- **File Name:** `artifact-research.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #21
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-28

---

# 1. Purpose

Define what a research artifact is, what responsibilities it carries, how it relates to specifications and other artifact types, and how it moves through its lifecycle from observation to validated knowledge.

Research artifacts preserve the exploratory layer of the engineering process. They capture observations, hypotheses, and experiments before ideas are mature enough to become specifications. This specification establishes the canonical definition, boundaries, and expectations for research artifacts at the artifact system layer.

---

# 2. Goals

- Define the canonical purpose and responsibilities of a research artifact.
- Establish lifecycle stages for a research artifact.
- Define the relationship between research and specification artifacts.
- Specify structural expectations for research artifacts without prescribing content.
- Establish the boundary between research and specification.

---

# 3. Non-Goals

- This spec does not define the content of any specific research area.
- This spec does not prescribe implementation technology.
- This spec does not replace or duplicate `docs/research/README.md`.
- This spec does not define how specifications are created (see `artifact-specification.spec.md`).

---

# 4. Context

Research is a permanent activity in Ego Hygiene. Architecture should emerge from validated understanding, not from speculation. Research artifacts exist to preserve context during the period between observation and decision.

The engineering flow for research is:

```
Observation
  ↓
Hypothesis
  ↓
Experiment
  ↓
Evidence
  ↓
Specification (if evidence is sufficient)
```

Without research artifacts, context is lost between cycles. Ideas either get implemented prematurely or disappear entirely. Research artifacts solve this by providing a durable, structured home for exploratory thinking.

The existing `docs/research/` directory and its README establish the file system convention. This spec establishes the artifact-level definition that complements that convention.

---

# 5. Requirements

## 5.1 Functional Requirements

- A research artifact must represent one discrete area of investigation.
- A research artifact must capture observations, hypotheses, and experimental outcomes.
- A research artifact must record the evidence that supports or refutes each hypothesis.
- A research artifact must carry a lifecycle status indicating its maturity.
- A research artifact must be promotable to a specification when evidence is sufficient.
- A research artifact must be archivable when the investigation is closed or superseded.

## 5.2 Non-Functional Requirements

- Research artifacts must be legible to both human readers and AI agents.
- Research artifacts must not contain implementation decisions — only evidence and hypotheses.
- Research artifacts must preserve context across multiple development cycles.
- Research artifacts must not be promoted to specifications without documented evidence.

---

# 6. Architecture

## 6.1 Responsibilities

A research artifact is responsible for:

- Capturing observations about the system, domain, or technology under investigation.
- Recording hypotheses derived from those observations.
- Documenting experiments designed to test hypotheses.
- Preserving experimental outcomes and evidence.
- Signaling when evidence is sufficient to promote a finding into a specification.
- Remaining in an honest, inconclusive state when evidence is insufficient.

## 6.2 Relationships

```
Research
  ← observes →     Domain Artifacts (research may investigate domain behavior)
  ← informs →      Specification Artifacts (mature research promotes into specifications)
  ← references →   Schema Artifacts (research may explore schema options)
  ← consumed by →  Agent Artifacts (agents may use research as exploratory context)
  ← documented in → Documentation Artifacts (research summaries surface in documentation)
```

## 6.3 Lifecycle

```
Observation
  ↓ (initial observation captured)
Hypothesis
  ↓ (testable hypothesis formed from observation)
Experiment
  ↓ (experiment designed and executed)
Evidence
  ↓ (outcomes recorded)
Promoted
  ↓ (evidence sufficient; promoted to specification)
  — or —
Archived
  (investigation closed; insufficient evidence or superseded)
```

## 6.4 Structural Expectations

A research artifact should carry:

- A stable identifier
- An investigation title
- A list of observations
- One or more hypotheses derived from observations
- Experiment descriptions and outcomes
- Evidence statements
- A promotion decision with rationale (if promoted)
- Lifecycle status
- Created and updated timestamps

## 6.5 Implementation Expectations

Research artifacts live primarily in documentation form within `docs/research/`. They are not directly persisted in application storage. However, implementations are expected to:

- Respect the research-to-specification boundary.
- Not implement features derived from research artifacts that have not been promoted to specifications.
- Reference research artifacts in specification context sections when traceability is needed.

---

# 7. Implementation Plan

## Phase 1 — Artifact Definition

- [ ] Confirm research artifact identity and purpose.
- [ ] Document canonical lifecycle stages.
- [ ] Document relationships to specification, schema, agent, and documentation artifacts.

## Phase 2 — Structural Alignment

- [ ] Align research artifact structure with existing `docs/research/README.md`.
- [ ] Confirm structural expectations are sufficient without being prescriptive.

## Phase 3 — Validation

- [ ] Verify this spec is consistent with `docs/research/README.md`.
- [ ] Verify the boundary between research and specification is clearly described.
- [ ] Verify lifecycle is complete and unambiguous.

---

# 8. Validation Plan

- Review this spec against `docs/research/README.md` for consistency.
- Verify that no implementation-specific technology is referenced in this spec.
- Verify that all relationships to other artifact types are explicitly stated.
- Confirm the research-to-specification promotion path is unambiguous.

---

# 9. Acceptance Criteria

- [ ] Research artifact purpose is clearly defined.
- [ ] Research lifecycle stages are documented.
- [ ] Relationships to specification, schema, agent, and documentation artifacts are explicit.
- [ ] The promotion boundary between research and specification is clearly stated.
- [ ] The spec is consistent with `specfile.spec.md`.
- [ ] The spec remains implementation-independent.

---

# 10. Open Questions

- Should research artifacts carry a confidence score or evidence strength rating?
- How should conflicting hypotheses within a single research artifact be resolved?
- Should research artifacts be linked to specific GitHub issues for traceability?
- At what point does accumulated evidence become sufficient for promotion — who decides?
