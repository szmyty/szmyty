# Repository Auditor Specification

## Metadata

- **Spec ID:** `auditor`
- **File Name:** `auditor.spec.md`
- **Status:** Approved
- **Owner:** Sanctuary
- **Related Issues:** #315
- **Related ADRs:** N/A
- **Last Updated:** 2026-07-12

---

# 1. Purpose

Define the canonical contract for repository auditing across any codebase.

This specification establishes what an audit is, how audits are requested and scoped, what evidence standards apply, how findings are classified, what output format is required, and how the auditor agent must behave.

The specification is repository-agnostic and portable. It respects local architecture and governance without being coupled to any specific technology stack.

---

# 2. Goals

- Define a universal auditing contract reusable across repositories.
- Support holistic and scoped audit strategies.
- Establish evidence, classification, severity, confidence, and uncertainty rules.
- Define the canonical output file format, location, and naming convention.
- Define agent behavior, reading order, and completion criteria.
- Enforce read-only default behavior.
- Require positive observations alongside defect findings.
- Support partial and blocked audit reporting.

---

# 3. Non-Goals

- This spec does not perform a repository audit.
- This spec does not define application architecture.
- This spec does not create GitHub issues from findings.
- This spec does not couple the auditor to Flutter, Dart, or any specific technology.
- This spec does not replace existing governance, architecture, or specification documents.

---

# 4. Context

Repositories accumulate technical debt, architectural drift, documentation gaps, and security risks over time. Without a consistent auditing framework, assessments become ad hoc, unrepeatable, and difficult to act on.

This specification provides a structured, evidence-based, machine-readable and human-readable framework for producing audit reports that are:

- reproducible across time and agents
- grounded in repository-observable evidence
- transparent about confidence and uncertainty
- actionable without being prescriptive
- additive rather than destructive

Existing specifications, agents, and governance files serve as primary context sources. The auditor adapts when those sources are absent.

---

# 5. Core Principles

Every audit must be:

- **Evidence-based** — Findings must cite concrete, observable evidence.
- **Repository-aware** — The auditor adapts to local architecture and conventions.
- **Non-destructive** — Audits produce reports only. Source files are never modified.
- **Reproducible** — Two agents given the same repository state should reach similar conclusions.
- **Transparent** — Assumptions, exclusions, and uncertainties must be documented.
- **Prioritized** — Findings must carry severity, confidence, and impact.
- **Actionable** — Every finding must include a recommendation or clarification path.
- **Explicit about uncertainty** — Unverifiable claims must be labeled accordingly.
- **Scoped** — Output must reflect the requested scope and document exclusions.
- **Balanced** — Strengths must be captured alongside risks.

The auditor must distinguish between observation types:

| Observation Type | Description |
|---|---|
| Confirmed defect | Evidence clearly demonstrates a problem. |
| Probable issue | Evidence suggests a likely problem but requires validation. |
| Architectural concern | A structural pattern that may limit evolution or correctness. |
| Maintainability risk | A pattern that increases long-term maintenance cost. |
| Optimization opportunity | A non-blocking improvement with measurable benefit. |
| Documentation gap | Missing or misleading documentation. |
| Future enhancement | Useful feature not yet present. |
| Intentional trade-off | A known compromise that has been deliberately accepted. |
| Needs human clarification | Insufficient evidence to classify without additional context. |

---

# 6. Repository Context Discovery

Before auditing, the auditor must inspect repository context in the following order. Absent files must be noted rather than assumed.

1. `README.md`, `START_HERE.md`
2. Architecture and system documents (`ARCHITECTURE.md`, `SYSTEM.md`, `DESIGN.md`)
3. Governance and contribution files (`AI_CONSTITUTION.md`, `CONTRIBUTOR_GUIDE.md`, `DECISIONS.md`)
4. Existing specifications under `.github/specs/`
5. Agent and skill files under `.github/agents/` and `.github/skills/`
6. Build and task automation (`Taskfile.yml`, `Makefile`, `package.json`, etc.)
7. Dependency manifests (`pubspec.yaml`, `package.json`, `pyproject.toml`, etc.)
8. CI/CD workflows under `.github/workflows/`
9. Source code under `lib/`, `src/`, `apps/`, etc.
10. Tests
11. Documentation under `docs/`
12. Existing audits under `audits/`

The auditor must never assume a convention exists without evidence.

---

# 7. Audit Strategies

## 7.1 Holistic Repository Audit

Reviews the repository as an integrated system.

Evaluates:

- architecture and structure
- code quality and consistency
- testing completeness
- automation and CI/CD
- documentation accuracy
- security posture
- maintainability and scalability
- accessibility
- performance
- developer experience
- release readiness

---

## 7.2 Architecture Audit

Evaluates:

- module boundaries and dependency direction
- layering, coupling, cohesion
- source-of-truth ownership
- abstraction quality
- duplicated responsibilities
- extension points
- architectural drift
- spec-to-implementation alignment

---

## 7.3 Code Quality Audit

Evaluates:

- clarity and complexity
- duplication and naming
- type safety and error handling
- dead code and implicit behavior
- maintainability
- consistency with language idioms

---

## 7.4 Testing Audit

Evaluates:

- test coverage by behavior (not raw line coverage alone)
- missing critical cases
- brittle or duplicated tests
- integration boundaries
- fixture quality
- deterministic execution
- CI parity
- test naming and structure

---

## 7.5 Security and Privacy Audit

Evaluates:

- secrets handling
- unsafe defaults and sensitive logging
- dependency risk
- data exposure and permissions
- input validation
- authentication boundaries
- encryption usage
- privacy controls and retention behavior

The auditor must not claim a vulnerability without evidence.

---

## 7.6 Performance Audit

Evaluates:

- unnecessary work and repeated I/O
- avoidable rebuilds and inefficient queries
- caching and concurrency
- startup behavior and memory pressure
- large artifact handling
- build pipeline performance

Distinguishes measured problems from suspected risks.

---

## 7.7 Accessibility and UX Audit

Evaluates:

- semantic labels and keyboard navigation
- contrast and motion reduction
- screen-reader support and focus behavior
- cognitive load and error clarity
- responsive behavior and interaction consistency

---

## 7.8 Dependency Audit

Evaluates:

- outdated, duplicate, or abandoned packages
- unnecessary dependencies and version drift
- lockfile consistency
- licensing concerns
- platform compatibility

Does not automatically recommend upgrades without considering migration risk.

---

## 7.9 CI/CD and Automation Audit

Evaluates:

- duplicated workflow logic and missing gates
- caching and artifact flow
- release ordering
- branch protection assumptions
- reusable actions
- deterministic builds
- failure propagation and concurrency
- unnecessary job execution
- local/CI parity

---

## 7.10 Documentation Audit

Evaluates:

- onboarding quality
- architecture accuracy
- broken paths and stale references
- missing usage examples
- unclear ownership
- contradictory guidance
- documentation discoverability
- source-of-truth ambiguity

---

## 7.11 Developer Experience Audit

Evaluates:

- setup friction and task automation
- command consistency
- editor support and local environment parity
- debugging ergonomics
- cognitive overhead and discoverability
- contribution workflow and reproducibility

---

## 7.12 Scoped Audit

Supports targeted audits by:

- directory or file set
- feature or subsystem
- package or module
- workflow
- specification
- platform

The output must clearly state included and excluded areas.

Example invocation:

```text
Audit only the Flutter context-capture subsystem.
```

---

# 8. Audit Request Contract

An audit invocation may provide the following fields. All fields are optional unless otherwise stated.

```yaml
audit_name: repository-health         # Required. Slug used in filename and report ID.
strategy: holistic                    # Audit mode from section 7. Default: holistic.
scope:
  include:
    - "."
  exclude:
    - "generated/**"
focus:                                # Optional subset of evaluation areas.
  - architecture
  - testing
  - developer-experience
depth: comprehensive                  # comprehensive | standard | surface. Default: standard.
constraints:
  - "Do not modify files"
```

When fields are omitted, the auditor infers reasonable defaults and documents those assumptions in the report.

---

# 9. Output Location and Filename

Every audit must produce a Markdown file under:

```text
audits/
```

**Filename format:**

```text
audits/{audit-name}-{utc-timestamp}.md
```

- `{audit-name}` — lowercase kebab-case slug normalized from the audit request name
- `{utc-timestamp}` — filesystem-safe UTC timestamp in `YYYYMMDDTHHMMSSZ` format

**Example:**

```text
audits/repository-health-20260712T184530Z.md
```

Previous audits must never be overwritten or modified.

---

# 10. Standard Report Format

Every audit report must use the following Markdown structure.

```markdown
---
audit_id: repository-health-20260712T184530Z
audit_name: repository-health
strategy: holistic
status: complete
started_at: 2026-07-12T18:30:00Z
completed_at: 2026-07-12T18:45:30Z
repository_revision: "<git-sha-or-unknown>"
scope:
  included:
    - "."
  excluded:
    - "generated/**"
auditor_version: "1.0.0"
---

# {Audit Title}

## Executive Summary

## Scope

## Repository Context

## Methodology

## Overall Assessment

## Findings Summary

## Critical Findings

## High-Priority Findings

## Medium-Priority Findings

## Low-Priority Findings

## Positive Observations

## Architectural Opportunities

## Refactoring Opportunities

## Testing Opportunities

## Documentation Opportunities

## Developer Experience Opportunities

## Suggested Issue Backlog

## Deferred or Out-of-Scope Observations

## Uncertainties and Required Clarifications

## Evidence Index

## Validation Notes
```

Sections may be omitted only when explicitly documented as not applicable.

**Status field values:**

| Value | Meaning |
|---|---|
| `complete` | All requested scope was inspected. |
| `partial` | Some scope was inspected; gaps are documented. |
| `blocked` | Audit could not proceed; reason is documented. |
| `failed` | Audit encountered an unrecoverable error. |

---

# 11. Finding Format

Every finding must follow this structure:

```markdown
### AUDIT-NNN — {Short descriptive title}

**Classification:** {Observation type from section 5}
**Severity:** {Critical | High | Medium | Low | Informational}
**Confidence:** {High | Medium | Low}
**Status:** {Confirmed | Probable | Needs validation | Intentional trade-off | Needs clarification | Not applicable}
**Area:** `{path/to/relevant/area}`
**Effort:** {Small | Medium | Large | Unknown}
**Impact:** {Low | Medium | High | Critical}

#### Observation

Describe what was observed without exaggeration.

#### Evidence

- `path/to/file`
- `path/to/other_file`
- Relevant symbols, workflows, or configuration

#### Why It Matters

Explain the technical, operational, or cognitive consequence.

#### Recommendation

Describe the preferred corrective direction.

#### Suggested Validation

Explain how the change should be tested or verified.

#### Dependencies or Risks

List migration risks, prerequisites, or related findings.
```

Finding IDs (`AUDIT-NNN`) must be unique within a single report and stable once assigned.

---

# 12. Severity Model

## Critical

Immediate risk to security, data integrity, releases, core functionality, user safety, or repository operability.

## High

Material architectural, reliability, maintainability, or workflow risk.

## Medium

Important improvement with meaningful long-term value but no immediate failure.

## Low

Minor cleanup, consistency, polish, or optional optimization.

## Informational

Observation, positive pattern, intentional trade-off, or future idea.

---

# 13. Confidence Model

Every nontrivial finding must include a confidence level.

| Level | Meaning |
|---|---|
| High | Clear, direct evidence supports the finding. |
| Medium | Evidence exists but requires some inference. |
| Low | Minimal evidence; finding is a hypothesis. |

Low-confidence findings must clearly state what evidence is missing and what would be needed to raise confidence.

---

# 14. Status Model

| Status | Meaning |
|---|---|
| Confirmed | Evidence clearly supports the finding. |
| Probable | Evidence suggests likelihood but is not conclusive. |
| Needs validation | Finding requires a tool run, human review, or runtime check. |
| Intentional trade-off | The pattern is deliberate and documented. |
| Needs clarification | Insufficient context exists to classify. |
| Not applicable | Finding does not apply to this repository or scope. |

---

# 15. Effort and Impact

Use normalized estimates. Avoid false precision.

**Effort:**

| Value | Description |
|---|---|
| Small | A few hours or less. |
| Medium | One to several days. |
| Large | A week or more. |
| Unknown | Cannot be estimated without further investigation. |

**Impact:**

| Value | Description |
|---|---|
| Low | Minimal observable effect. |
| Medium | Noticeable improvement to quality, reliability, or experience. |
| High | Significant structural or operational benefit. |
| Critical | Prevents a defect, breach, or systemic failure. |

---

# 16. Evidence Rules

Findings must cite concrete, observable evidence whenever possible.

Evidence may include:

- file paths
- symbols, classes, or functions
- dependency declarations
- workflow jobs
- commands
- test files
- documentation
- generated diagnostics
- repository structure

The auditor must never fabricate line numbers, command results, or runtime behavior.

Evidence must be clearly labeled as one of:

| Label | Meaning |
|---|---|
| Observed | Directly visible in repository files. |
| Inferred | Logically derived from observable patterns. |
| Recommended | Suggested direction without direct evidence. |
| Unverified | Suspected but not confirmed. |

---

# 17. Positive Observations

Every audit must capture strengths, not only defects.

Examples of positive observations:

- well-defined module boundaries
- strong test coverage with behavior-driven cases
- effective CI automation
- clear and accurate documentation
- thoughtful accessibility implementation
- consistent naming conventions
- good offline-first or resilience patterns
- reusable infrastructure or abstractions

A report consisting only of defect findings is incomplete.

---

# 18. Suggested Issue Backlog

The report should translate major findings into a concise candidate backlog.

```markdown
### Suggested Issue: {Short title}

**Priority:** {Critical | High | Medium | Low}
**Depends On:** {None | AUDIT-NNN, ...}
**Source Findings:** {AUDIT-NNN, ...}

**Outcome:**
Describe the intended result.

**Acceptance Criteria:**
- [ ] ...
- [ ] ...
```

The auditor must not automatically create GitHub issues during an audit unless explicitly authorized by the invocation.

---

# 19. Existing Audit Awareness

Before creating a new report, the auditor must inspect existing files under `audits/`.

The auditor must:

- avoid blindly repeating prior findings
- note recurring findings as recurring
- identify resolved findings when evidence supports resolution
- never modify historical audit files

Each audit file is an immutable historical record.

---

# 20. Non-Destructive Behavior

Audits are read-only by default.

The auditor must not:

- modify source files
- reformat the repository
- update dependencies
- delete files
- create or apply fixes
- commit changes
- open GitHub issues

unless the invocation contract explicitly authorizes those actions.

The only expected output of a normal audit is the audit report file under `audits/`.

---

# 21. Partial and Blocked Audit Behavior

If the auditor cannot complete the requested audit, it must still create a report with an appropriate status value (`partial`, `blocked`, or `failed`).

The report must state:

- what was inspected
- what could not be inspected
- why the audit was incomplete
- what is needed to continue or complete the audit

Partial reports are valid historical records and must follow the same format as complete reports.

---

# 22. Implementation Plan

## Phase 1 — Foundation

- [x] Create `.github/specs/auditor.spec.md`
- [x] Create `.github/agents/auditor.agent.md`
- [x] Create `audits/` directory with `.gitkeep`
- [x] Update repository documentation

---

# 23. Validation Plan

- Verify frontmatter and Markdown structure of spec and agent files.
- Verify the `audits/` directory exists with `.gitkeep`.
- Verify existing repository documentation references the auditor.
- Verify no application code was modified.
- Verify no full repository audit was performed.

---

# 24. Acceptance Criteria

- [ ] `.github/specs/auditor.spec.md` exists and follows repository spec conventions.
- [ ] `.github/agents/auditor.agent.md` exists and follows repository agent conventions.
- [ ] `audits/` directory exists with `.gitkeep`.
- [ ] Specification defines multiple audit strategies.
- [ ] Specification supports scoped and holistic audits.
- [ ] Repository discovery order is documented.
- [ ] Standard audit filename format is defined.
- [ ] Standard report frontmatter is defined.
- [ ] Standard report section structure is defined.
- [ ] Standard finding syntax is defined.
- [ ] Severity, confidence, status, effort, and impact models are defined.
- [ ] Evidence and uncertainty rules are defined.
- [ ] Positive observations are required.
- [ ] Suggested issue backlog format is defined.
- [ ] Read-only default behavior is enforced.
- [ ] Partial and blocked audit behavior is defined.
- [ ] Repository documentation is updated.
- [ ] No full repository audit was performed.

---

# 25. Open Questions

- Should audits eventually support machine-readable JSON output alongside Markdown?
- Should the auditor integrate with GitHub Issues for backlog creation in a future version?
