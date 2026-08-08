Spec File Specification

Metadata

- Spec ID: "specfile"
- File Name: "specfile.spec.md"
- Status: Draft
- Owner: Sanctuary
- Purpose: Define the canonical structure, expectations, and quality bar for creating specification files.

---

1. Purpose

This specification defines how spec files should be written, organized, validated, and used across projects.

A spec file exists to turn an idea, architecture, feature, workflow, or system requirement into a clear implementation contract.

Specs should help humans and AI agents move from:

«idea
→ architecture
→ specification
→ implementation plan
→ GitHub issues
→ code
→ validation»

---

2. Goals

- Standardize spec file structure.
- Make specs readable by humans and AI agents.
- Support GitHub issue generation.
- Support implementation by Copilot or other coding agents.
- Reduce ambiguity before code is written.
- Separate intent, design, implementation, and validation.
- Make acceptance criteria explicit.

---

3. Non-Goals

- A spec is not a full implementation.
- A spec is not a vague brainstorm.
- A spec is not a changelog.
- A spec is not a replacement for tests.
- A spec should not contain unnecessary code unless examples clarify behavior.

---

4. File Naming Convention

Spec files should use kebab-case and end with ".spec.md".

Examples:

«authentication-flow.spec.md
flutter-app-shell.spec.md
repository-intelligence.spec.md
health-tracking-garden.spec.md
specfile.spec.md»

---

5. Required Sections

Every spec file should include these sections unless there is a documented reason to omit one.

5.1 Metadata

Defines identity and ownership.

Recommended fields:

- Spec ID
- File Name
- Status
- Owner
- Related Issues
- Related ADRs
- Last Updated

5.2 Purpose

Explain why this spec exists.

5.3 Goals

Define what success looks like.

5.4 Non-Goals

Define what this spec intentionally does not cover.

5.5 Context

Describe background, current state, constraints, and relevant history.

5.6 Requirements

List functional and non-functional requirements.

5.7 Architecture

Describe components, boundaries, data flow, interfaces, and dependencies.

5.8 Implementation Plan

Break the work into clear implementation phases or tasks.

5.9 Validation Plan

Define how the implementation will be tested, verified, or reviewed.

5.10 Acceptance Criteria

Use checklist format.

5.11 Open Questions

List unresolved decisions.

---

6. Recommended Spec Template

Use this template when creating a new spec.

«# <Spec Title>

## Metadata

- **Spec ID:** `<kebab-case-id>`
- **File Name:** `<kebab-case-id>.spec.md`
- **Status:** Draft
- **Owner:** `<owner-or-team>`
- **Related Issues:** `#...`
- **Related ADRs:** `ADR-...`
- **Last Updated:** `<YYYY-MM-DD>`

---

# 1. Purpose

Describe why this spec exists.

---

# 2. Goals

- Goal one.
- Goal two.
- Goal three.

---

# 3. Non-Goals

- Out-of-scope item one.
- Out-of-scope item two.

---

# 4. Context

Describe the current state, background, constraints, and relevant decisions.

---

# 5. Requirements

## 5.1 Functional Requirements

- The system must...
- The user must be able to...

## 5.2 Non-Functional Requirements

- The system should be maintainable.
- The system should be testable.
- The system should be documented.

---

# 6. Architecture

## 6.1 Components

- Component A
- Component B

## 6.2 Data Flow

Describe how information moves through the system.

## 6.3 Interfaces

Describe APIs, files, commands, events, or integration points.

## 6.4 Dependencies

List required tools, libraries, services, or repositories.

---

# 7. Implementation Plan

## Phase 1 — Foundation

- [ ] Task one.
- [ ] Task two.

## Phase 2 — Implementation

- [ ] Task one.
- [ ] Task two.

## Phase 3 — Validation

- [ ] Task one.
- [ ] Task two.

---

# 8. Validation Plan

- Unit tests
- Integration tests
- Manual testing
- CI validation
- Documentation review

---

# 9. Acceptance Criteria

- [ ] The implementation satisfies all functional requirements.
- [ ] The implementation satisfies all non-functional requirements.
- [ ] Tests have been added or updated.
- [ ] Documentation has been added or updated.
- [ ] CI passes.
- [ ] Follow-up issues have been created where needed.

---

# 10. Open Questions

- Question one?
- Question two?»

---

7. Spec Quality Bar

A good spec should be:

- clear
- scoped
- testable
- implementation-ready
- readable by humans
- usable by AI agents
- explicit about tradeoffs
- explicit about validation

A bad spec is:

- vague
- too large
- missing acceptance criteria
- missing context
- unclear about scope
- impossible to validate

---

8. Agent Instructions

When an AI agent creates a spec file, it must:

1. Identify the problem being solved.
2. Separate goals from non-goals.
3. Define clear requirements.
4. Describe architecture before implementation.
5. Break implementation into phases.
6. Include validation steps.
7. Include acceptance criteria.
8. List open questions instead of guessing.
9. Avoid over-engineering.
10. Prefer simple, explicit language.

---

9. GitHub Issue Generation Rules

A spec should be able to produce GitHub issues.

Each implementation phase may become an issue.

Each issue should include:

- context
- scope
- expected files or modules
- implementation notes
- validation steps
- acceptance criteria

Large specs should generate multiple small issues instead of one massive issue.

---

10. Status Values

Allowed status values:

- Draft
- Review
- Approved
- In Progress
- Implemented
- Superseded

---

11. Completion Criteria

This spec is complete when:

- [ ] The spec template is usable for new projects.
- [ ] Agents can follow the format consistently.
- [ ] Specs can be converted into GitHub issues.
- [ ] Specs can guide implementation without additional context.
- [ ] The format works for architecture, features, automation, gardens, and agent workflows.