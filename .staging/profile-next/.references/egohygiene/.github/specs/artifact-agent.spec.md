# Artifact Agent

## Metadata

- **Spec ID:** `artifact-agent`
- **File Name:** `artifact-agent.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #21
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-28

---

# 1. Purpose

Define what an agent artifact is, what responsibilities it carries, how it relates to specifications, schemas, and other artifact types, and how it behaves across its lifecycle.

An agent artifact defines how AI executes within the repository. Where specifications define intent and schemas define structure, agents define execution boundaries and reasoning guidelines for AI systems. This specification establishes the canonical definition of agent artifacts at the artifact system layer.

---

# 2. Goals

- Define the canonical purpose and responsibilities of an agent artifact.
- Establish execution boundaries for agent artifacts.
- Define the relationship between agents and specifications, schemas, and other artifacts.
- Clarify the distinction between agents and specifications.
- Establish validation expectations for agent behavior.

---

# 3. Non-Goals

- This spec does not define the behavior of any specific agent.
- This spec does not prescribe AI technology or model selection.
- This spec does not define how specifications are written (see `artifact-specification.spec.md`).
- This spec does not define schema content or structure.

---

# 4. Context

The Ego Hygiene engineering system is designed for human-AI collaboration. Agents are the mechanism through which AI participates in that system.

The relationship between agents and the rest of the artifact system is:

```
Philosophy
  ↓
Specifications
  ↓
Agents
  ↓
Implementation
```

Agents consume specifications. They execute within defined boundaries. They do not define architecture, invent scope, or override human governance decisions.

The existing `.github/agents/` directory contains agent definitions. This spec defines the artifact-level role and lifecycle of agents as first-class artifacts in the repository system.

---

# 5. Requirements

## 5.1 Functional Requirements

- An agent artifact must define the scope of work the agent is authorized to perform.
- An agent artifact must reference the specifications it is designed to execute.
- An agent artifact must carry explicit execution boundaries — what the agent must not do.
- An agent artifact must define escalation conditions under which the agent should pause and surface uncertainty.
- An agent artifact must describe the validation steps the agent should perform after execution.
- An agent artifact must define how the agent leaves the repository in a synchronized state.

## 5.2 Non-Functional Requirements

- Agent artifacts must be legible to AI systems consuming them as context.
- Agent artifacts must not contain implementation-specific code unless it clarifies execution expectations.
- Agent artifacts must remain stable in their scope boundaries once approved.
- Agent artifacts must not grant themselves authority to expand scope.

---

# 6. Architecture

## 6.1 Responsibilities

An agent artifact is responsible for:

- Defining the reasoning guidelines for AI execution within a specific scope.
- Referencing the specifications that govern the agent's work.
- Establishing what the agent is and is not authorized to do.
- Defining how the agent validates its own output.
- Defining escalation conditions to preserve human governance.
- Providing traceability between AI-generated artifacts and human intent.

## 6.2 Relationships

```
Agent
  ← consumes →      Specification Artifacts (agents execute specifications)
  ← validates against → Schema Artifacts (agents verify artifact instances satisfy schemas)
  ← produces →      Implementation Artifacts (agents generate code, docs, and configs)
  ← references →    Research Artifacts (agents may use research as exploratory context)
  ← governed by →   Human Governance (humans retain architectural and continuation authority)
  ← documented in → Documentation Artifacts (agent capabilities surface in documentation)
```

## 6.3 Lifecycle

```
Draft
  ↓ (initial scope and specification references defined)
Review
  ↓ (reviewed for correctness, boundaries, and escalation conditions)
Active
  ↓ (in use within the repository; AI systems may load this agent)
Refined
  ↓ (scope clarified, escalation conditions updated)
Retired
  (superseded by a more capable or differently scoped agent)
```

## 6.4 Execution Boundaries

Agent artifacts must explicitly define:

- **In scope**: what tasks the agent is authorized to perform
- **Out of scope**: what tasks the agent must not attempt
- **Escalation triggers**: conditions under which the agent must pause and ask for clarification

Execution boundaries are not optional. An agent without explicit boundaries is not a valid agent artifact.

## 6.5 Relationship to Specifications

Agents and specifications are complementary, not interchangeable:

- A **specification** defines what should be built and why.
- An **agent** defines how AI reasons and executes within the scope of a specification.

Agents do not define architecture. Agents execute architecture. A specification can exist and be implemented by a human without an agent. An agent cannot exist without a specification to reference.

## 6.6 Relationship to Schemas

Agents use schemas as validation tools. An agent may:

- Validate that generated artifacts satisfy schema contracts.
- Reference schema field definitions to produce correctly structured output.
- Surface schema violations as validation findings.

Agents do not define schemas. Schema authority belongs to the specification layer.

## 6.7 Validation Expectations

Agent artifacts must define how the agent validates its output:

- Does the generated artifact satisfy the referenced specification's acceptance criteria?
- Does the generated artifact satisfy the relevant schema contract?
- Has the agent left the repository in a synchronized, auditable state?
- Are there open questions or unresolved decisions that require human review?

## 6.8 Structural Expectations

An agent artifact should carry:

- A stable identifier
- A title and purpose statement
- Referenced specifications
- Execution scope (in scope, out of scope)
- Escalation conditions
- Validation steps
- Lifecycle status

---

# 7. Implementation Plan

## Phase 1 — Artifact Definition

- [ ] Confirm agent artifact identity and purpose.
- [ ] Document canonical lifecycle stages.
- [ ] Document relationships to specification, schema, research, and documentation artifacts.

## Phase 2 — Boundary Clarification

- [ ] Define execution boundary requirements (in scope, out of scope, escalation).
- [ ] Clarify specification and schema distinctions.

## Phase 3 — Validation

- [ ] Verify this spec is consistent with existing agent files in `.github/agents/`.
- [ ] Verify all relationships are explicitly documented.
- [ ] Verify lifecycle is complete and unambiguous.

---

# 8. Validation Plan

- Verify this spec is consistent with existing `.github/agents/` content.
- Verify the agent-specification distinction is unambiguous.
- Verify execution boundaries are required and not optional.
- Verify all relationships to other artifact types are explicitly stated.

---

# 9. Acceptance Criteria

- [ ] Agent artifact purpose is clearly defined.
- [ ] Agent lifecycle stages are documented.
- [ ] Execution boundaries are required for all agent artifacts.
- [ ] The distinction between agents and specifications is explicit.
- [ ] The relationship to schema validation is explicit.
- [ ] Escalation conditions are required for all agent artifacts.
- [ ] Relationships to specification, schema, research, and documentation artifacts are explicit.
- [ ] The spec is consistent with `specfile.spec.md`.
- [ ] The spec remains implementation-independent.

---

# 10. Open Questions

- Should agent artifacts carry explicit capability declarations (e.g., can read files, can write code)?
- How should multiple agents with overlapping scope coordinate execution?
- Should agents carry a trust level or authorization scope that gates what they can do?
- How are agent artifacts versioned when AI model capabilities change significantly?
