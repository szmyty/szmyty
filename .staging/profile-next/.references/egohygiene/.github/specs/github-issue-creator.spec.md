# GitHub Issue Creator Specification

## Metadata

- **Spec ID:** `github-issue-creator`
- **File Name:** `github-issue-creator.spec.md`
- **Status:** Draft
- **Owner:** Ego Hygiene
- **Related Specifications:** `specfile.spec.md`
- **Last Updated:** `<YYYY-MM-DD>`

---

# 1. Purpose

This specification defines the canonical process, structure, and quality bar for creating GitHub issues from ideas, conversations, audits, specifications, bug reports, architectural decisions, and implementation plans.

The issue-creation system exists to transform unstructured or partially structured input into clear, scoped, implementation-ready work.

It should support the flow:

```text
Brain dump
→ clarify intent
→ identify outcome
→ determine scope
→ select issue strategy
→ structure implementation guidance
→ define validation
→ create queueable GitHub issue
```

The resulting issue should be understandable by:

- the original author
- future maintainers
- GitHub Copilot
- other AI implementation agents
- reviewers unfamiliar with the original conversation

---

# 2. Goals

- Standardize GitHub issue generation.
- Convert informal ideas into actionable implementation contracts.
- Preserve the original intent and motivation behind a request.
- Produce issues that GitHub Copilot can execute with minimal additional context.
- Support both small tasks and multi-issue feature roadmaps.
- Define consistent scope, constraints, validation, and acceptance criteria.
- Remain compatible with blank GitHub issues.
- Remain aware of repository issue templates without depending on them.
- Reduce ambiguity, architectural drift, and oversized pull requests.
- Make issue dependencies and execution order explicit.
- Support portable use in ChatGPT, Copilot, and other agent environments.

---

# 3. Non-Goals

- This specification does not implement the requested feature.
- It does not replace architecture or feature specifications.
- It does not require every idea to become an issue.
- It does not require every issue to use a GitHub Issue Form.
- It does not automatically create or submit issues unless explicitly authorized.
- It does not invent requirements that are unsupported by the provided context.
- It does not force all repositories to use the same issue templates.
- It does not require excessive ceremony for small, well-defined tasks.

---

# 4. Core Principles

GitHub issues generated under this specification must be:

- outcome-oriented
- scoped
- implementation-ready
- repository-aware
- architecture-aware
- testable
- explicit
- traceable
- readable
- appropriately sized
- honest about uncertainty

The issue creator should optimize for:

```text
Low cognitive load
+
Clear implementation direction
+
Small reviewable changes
+
Reliable validation
```

An issue is not merely a description of activity.

It is a contract describing the change in repository state that should exist when the work is complete.

---

# 5. Input Sources

The issue creator may receive input from:

- conversational brain dumps
- feature ideas
- bug reports
- architecture discussions
- audit findings
- specifications
- roadmap items
- screenshots
- error messages
- repository trees
- code snippets
- documentation
- research notes
- migration plans
- external references
- existing GitHub issues
- pull-request feedback

Input may be incomplete, emotional, repetitive, exploratory, or unordered.

The issue creator must extract the stable engineering intent without stripping away useful motivation or context.

---

# 6. Repository Context Discovery

Before generating a repository-specific issue, inspect available context in the following order when practical:

1. `START_HERE.md`
2. `README.md`
3. `SYSTEM.md`
4. `ARCHITECTURE.md`
5. `ONBOARDING.md`
6. relevant specifications under `.github/specs/`
7. relevant agents and skills
8. repository structure
9. current implementation files
10. tests
11. build and task automation
12. existing related issues
13. issue templates under `.github/ISSUE_TEMPLATE/`

When a file does not exist, continue without assuming its contents.

The issue creator must not fabricate repository conventions.

---

# 7. Issue Template Awareness

The issue creator should inspect the current contents of:

```text
.github/ISSUE_TEMPLATE/
```

The repository may currently contain templates such as:

```text
architecture.yml
bootstrap-repository.yml
bug-report.yml
ci.yml
documentation.yml
dx.yml
feature.yml
research.yml
task.yml
tech-debt.yml
```

This list is not exhaustive or permanent.

New templates may be added, renamed, or removed over time.

The issue creator must discover available templates dynamically rather than hardcoding the current list as a closed registry.

---

## 7.1 Template Selection

Select an issue template only when one clearly matches the requested work.

Example mappings:

```text
System boundaries or structural design
→ architecture

New user-facing or platform capability
→ feature

Known incorrect behavior
→ bug-report

Workflow, release, build, or automation work
→ ci

Documentation-only changes
→ documentation

Developer tooling or contributor experience
→ dx

Investigation without immediate implementation
→ research

Bounded implementation work
→ task

Refactoring, cleanup, or architectural remediation
→ tech-debt

Initial repository foundation
→ bootstrap-repository
```

---

## 7.2 Blank Issue Default

A blank Markdown issue is valid and should often be preferred when:

- the work spans multiple template categories
- the issue is architectural and experimental
- the repository form does not capture the needed detail
- the issue will be pasted manually
- the user explicitly prefers a blank issue
- a custom structure communicates the work more clearly

The issue body generated by this specification must remain useful independently of any GitHub Issue Form.

---

## 7.3 Template Compatibility

When a template is selected:

- preserve the canonical issue content
- map relevant sections into template fields
- do not omit critical scope or constraints merely to fit the form
- place additional information in the template’s free-form description field when needed
- do not invent unsupported labels, assignees, projects, or milestones

---

# 8. Issue Types

The issue creator should classify the requested work into one primary issue type.

Supported issue types include:

- Architecture
- Bootstrap
- Bug
- CI/CD
- Documentation
- Developer Experience
- Feature
- Migration
- Refactor
- Research
- Task
- Technical Debt
- Testing
- Security
- Performance
- Accessibility
- Release
- Audit Remediation
- Content or Publishing
- Tooling
- Data or Schema

Additional repository-specific types may be used when clearly defined.

An issue may mention secondary concerns, but it should have one primary outcome.

---

# 9. Issue Sizing

Issues should be small enough to:

- understand independently
- implement in one focused pull request
- validate deterministically
- review without excessive context switching
- revert safely if needed

A proposed issue should be split when it contains multiple independently valuable outcomes.

Indicators that an issue is too large include:

- unrelated subsystems
- multiple major migrations
- several new architectural layers
- many external integrations
- acceptance criteria that describe separate products
- implementation that would require multiple unrelated pull requests
- ambiguous sequencing between major phases

---

## 9.1 When to Create a Roadmap

Create a mini issue roadmap before writing individual issues when:

- the feature requires foundational architecture
- several issues have dependencies
- the user wants to approve the sequence first
- implementation should occur in batches
- a broad idea needs progressive delivery

A roadmap should include:

```text
Issue number or sequence
Title
Primary outcome
Dependencies
Reason for ordering
```

After approval, generate issues one at a time unless explicitly asked for a batch.

---

## 9.2 Vertical Slices

Prefer issues that deliver a complete, testable slice of behavior.

Example:

```text
Bad:
Create all models for the entire health platform.

Better:
Create the health-item domain model, repository contract, local store, and focused tests.
```

Foundational issues may be horizontal when necessary, but their consumers and boundaries must be explicit.

---

# 10. Clarification Policy

Do not ask unnecessary questions.

Ask for clarification only when ambiguity materially changes:

- architecture
- data ownership
- security or privacy
- user-visible behavior
- migration safety
- repository destination
- dependency selection
- irreversible actions
- acceptance criteria

When a reasonable default exists:

- choose the simplest compatible default
- state the assumption in the issue
- keep the implementation reversible

Do not replace useful forward progress with excessive discovery.

---

# 11. Canonical Issue Structure

Use the following structure for substantial issues.

Sections may be shortened for genuinely small tasks, but the core contract must remain clear.

```markdown
# Title

<emoji> <Imperative outcome-oriented title>

## Overview

Describe the requested change and the intended outcome.

## Motivation

Explain why the work matters and what problem it solves.

## Current State

Describe the relevant existing behavior or repository structure.

## Desired State

Describe the repository or user-visible state after completion.

## Scope

Define what this issue includes.

## Requirements

Define functional and non-functional requirements.

## Architecture and Implementation Guidance

Describe boundaries, expected modules, data flow, patterns, and repository conventions.

## Expected File Changes

List known files or directories likely to be created or modified.

## Migration and Compatibility

Describe migration, backward compatibility, and preservation requirements when applicable.

## Testing and Validation

Define tests, commands, manual checks, and CI expectations.

## Constraints

Define what must not be changed or implemented.

## Deliverables

List concrete outputs.

## Acceptance Criteria

- [ ] Verifiable completion condition.
```

Optional sections include:

- Background
- User Experience
- Data Model
- Security and Privacy
- Accessibility
- Performance
- Observability
- Failure Behavior
- Rollout Strategy
- Dependencies
- Risks
- Open Questions
- References
- Follow-Up Work

---

# 12. Title Rules

Issue titles should be:

- imperative
- concise
- outcome-oriented
- distinguishable in an issue backlog
- understandable without opening the issue

Preferred format:

```text
<emoji> <Verb> <specific outcome>
```

Examples:

```text
🌍 Build the Context Signal Framework
🔍 Create the Universal Repository Auditor
♻️ Consolidate Duplicate Context Abstractions
📌 Normalize Pinterest Archive Identifiers
🧪 Add Integration Coverage for Context Capture
📚 Research Historical Pinterest Backfill Strategies
```

Avoid:

```text
Context stuff
Update files
Fix things
Implement feature
Misc cleanup
```

Do not require an emoji when the repository does not use them.

---

# 13. Overview Rules

The overview should answer:

- What is changing?
- Where is it changing?
- What should exist when complete?
- Is this implementation, research, migration, or remediation?

Keep the overview concise enough to scan while preserving the main intent.

---

# 14. Motivation Rules

Motivation should preserve useful human and product context.

It may describe:

- user pain
- cognitive load
- architectural inconsistency
- operational risk
- missing capability
- duplicated effort
- workflow friction
- future dependency
- scientific or product rationale

Avoid exaggerated claims.

The issue should remain valid even when emotional context is later forgotten.

---

# 15. Scope Rules

Scope must define what is included.

Examples:

```text
This issue includes:
- domain model
- repository contract
- local persistence
- providers
- focused tests
- documentation
```

Scope should identify the primary subsystem or directory whenever known.

---

# 16. Requirements

Requirements should be explicit and testable.

Use language intentionally:

- **must** for mandatory behavior
- **should** for expected behavior with reasonable exceptions
- **may** for optional behavior

Separate functional and non-functional requirements when useful.

Avoid requirements such as:

```text
Make it good.
Make it scalable.
Use best practices.
Improve everything.
```

Translate them into observable expectations.

---

# 17. Architecture and Implementation Guidance

Implementation guidance should constrain behavior without micromanaging every line of code.

Include:

- system boundaries
- ownership
- expected abstractions
- data flow
- interfaces
- source-of-truth rules
- state transitions
- relevant design patterns
- repository conventions
- integration points
- failure behavior

When architecture is already defined, reference the authoritative specification.

When architecture is unresolved, the issue may authorize a focused design investigation rather than pretending the answer is known.

Do not invent unnecessary abstractions.

---

# 18. Expected File Changes

List expected paths when they are known.

Example:

```text
.github/specs/auditor.spec.md
.github/agents/auditor.agent.md
audits/.gitkeep
docs/auditing.md
```

The list may be described as expected rather than exhaustive.

Do not fabricate exact paths when the repository structure has not been inspected.

---

# 19. Validation Rules

Every implementation issue must define how success will be validated.

Validation may include:

- unit tests
- widget tests
- integration tests
- golden tests
- schema validation
- static analysis
- formatting
- build generation
- CLI execution
- workflow validation
- manual user-flow checks
- documentation review
- migration dry runs
- idempotency checks

Use repository-native commands whenever available.

Example:

```text
task pub-get
task generate
task dart:format
task analyze
task test
```

Do not claim commands passed when they were not executed.

---

# 20. Acceptance Criteria

Acceptance criteria must describe observable completion.

Each item should be independently checkable.

Good:

```markdown
- [ ] Existing Pinterest item directories are migrated to `pin-<id>`.
- [ ] New synchronization runs generate the same identifier format.
- [ ] Manifest references are updated without redownloading unchanged assets.
- [ ] Repeated migration runs produce no additional changes.
```

Bad:

```markdown
- [ ] Code is clean.
- [ ] Works correctly.
- [ ] Best practices followed.
```

Acceptance criteria should cover:

- primary behavior
- error behavior
- tests
- documentation
- compatibility
- CI or validation

Only include criteria relevant to the issue.

---

# 21. Constraints

Constraints should prevent predictable scope drift.

Examples:

```text
Do not:
- redesign unrelated features
- add speculative dependencies
- migrate data without preserving backups
- modify generated files manually
- create GitHub issues automatically
- replace canonical source content with channel mirrors
```

Constraints should be specific to the task.

Avoid large generic prohibition lists that add no value.

---

# 22. Research Issues

A research issue must not pretend implementation is already decided.

It should include:

- research question
- motivation
- current assumptions
- options to evaluate
- evaluation criteria
- expected evidence
- output location
- decision or recommendation format
- explicit non-goals

Expected output may be:

```text
docs/research/<topic>.md
audits/<topic>-<timestamp>.md
.github/specs/<topic>.spec.md
```

Acceptance criteria should verify the investigation and recommendation, not production implementation.

---

# 23. Bug Issues

A bug issue should include:

- observed behavior
- expected behavior
- reproduction steps
- environment
- evidence or logs
- suspected area
- regression risk
- validation
- acceptance criteria

Do not claim a root cause unless evidence supports it.

When reproduction details are unavailable, mark them as unknown rather than inventing them.

---

# 24. Migration and Refactor Issues

Migration and refactor issues should define:

- current ownership
- target ownership
- files or systems affected
- history preservation
- compatibility requirements
- references that must be updated
- cleanup expectations
- rollback or recovery approach
- validation commands

A migration is incomplete while duplicate canonical copies remain without a documented reason.

---

# 25. CI/CD Issues

CI/CD issues should consider:

- trigger conditions
- job dependencies
- required gates
- failure propagation
- concurrency
- caching
- artifact ownership
- release ordering
- local/CI parity
- reusable actions
- permissions
- generated commits
- recursion prevention

The desired pipeline must be described as an ordered flow.

---

# 26. Architecture Issues

Architecture issues should define:

- problem
- current boundaries
- desired boundaries
- ownership
- data flow
- interfaces
- dependencies
- migration strategy
- validation strategy
- documentation updates

When the issue is primarily architectural discovery, the output should be a specification or decision record before production implementation.

---

# 27. Issue Dependencies

When an issue depends on another issue, state it explicitly.

Example:

```markdown
## Dependencies

- Blocked by: #123
- Enables: Context Snapshot Engine
- Related: #118, #121
```

Do not invent issue numbers.

When issue numbers are not yet known, use titles or roadmap sequence names.

---

# 28. Suggested Labels

The issue creator may suggest labels based on available repository labels.

It must not assume labels exist.

Suggested labels should be listed separately from the issue body when useful.

Example:

```text
Suggested labels:
- feature
- architecture
- flutter
- context
```

Do not add labels automatically unless explicitly authorized.

---

# 29. Issue Output Modes

The issue creator must support multiple output modes.

## 29.1 Full Markdown Issue

Default for substantial implementation work.

Output as a single fenced Markdown block suitable for copying into GitHub.

## 29.2 Concise Task

For a small, bounded change.

Recommended sections:

```text
Overview
Scope
Validation
Acceptance Criteria
```

## 29.3 Research Issue

Uses the research structure defined by this specification.

## 29.4 Bug Report

Uses the bug structure defined by this specification.

## 29.5 Roadmap

Returns an ordered sequence of proposed issues without generating every full body.

## 29.6 Issue Batch

Generates several issues only when explicitly requested.

Each issue must remain independently copyable.

## 29.7 Issue Comment

Produces a scoped update or correction for an existing issue or pull request.

## 29.8 Template Field Mapping

Maps canonical issue content into an existing GitHub Issue Form when requested.

---

# 30. Formatting Rules

- Use Markdown.
- Use fenced code blocks for code, file trees, commands, schemas, and structured examples.
- Close every code fence correctly.
- Use checkbox syntax for acceptance criteria.
- Prefer headings over deeply nested bullet lists.
- Keep paragraphs readable.
- Avoid decorative horizontal separators between every small section.
- Preserve exact paths, identifiers, and commands.
- Use relative repository paths where practical.
- Do not embed internal reasoning or hidden analysis.
- Do not add unsupported citations.
- Do not wrap the issue in conversational commentary when the user asks for a copy-ready issue.

---

# 31. Tone

Issue language should be:

- direct
- professional
- clear
- calm
- specific
- collaborative
- implementation-oriented

Preserve personality where it adds motivation, but translate highly informal brainstorming into durable engineering language.

Avoid:

- unnecessary hype
- condescension
- vague corporate language
- excessive jargon
- false certainty

---

# 32. Agent Behavior

An AI issue creator must:

1. Understand the requested outcome.
2. Inspect relevant repository context when available.
3. Determine whether the request is one issue or a roadmap.
4. Select the most appropriate issue type.
5. Preserve the motivating problem.
6. Define current and desired state.
7. Establish scope and constraints.
8. Reference authoritative specifications.
9. Define implementation guidance.
10. Define validation.
11. Produce testable acceptance criteria.
12. Surface unresolved questions.
13. Avoid implementation unless requested.
14. Avoid automatically creating issues unless authorized.
15. Return a copy-ready result.

---

# 33. Quality Review Checklist

Before returning an issue, verify:

- [ ] The title describes an outcome.
- [ ] The issue has one primary objective.
- [ ] Motivation is understandable.
- [ ] Scope is explicit.
- [ ] Non-goals or constraints prevent obvious drift.
- [ ] Architecture is referenced or explained.
- [ ] Expected repository areas are identified where known.
- [ ] Validation is concrete.
- [ ] Acceptance criteria are observable.
- [ ] Dependencies are identified.
- [ ] Unknowns are stated honestly.
- [ ] The issue is reasonably sized.
- [ ] The Markdown renders correctly.
- [ ] Every code fence is closed.
- [ ] The issue can be understood without the originating chat.

---

# 34. Completion Criteria

This specification is complete when:

- [ ] It can transform conversational brain dumps into implementation-ready issues.
- [ ] It supports blank Markdown issues.
- [ ] It discovers and uses repository templates dynamically.
- [ ] It supports multiple issue types.
- [ ] It supports issue roadmaps and decomposition.
- [ ] It defines a canonical issue structure.
- [ ] It defines validation and acceptance-criteria rules.
- [ ] It supports ChatGPT and Copilot workflows.
- [ ] It remains portable across repositories.
- [ ] It avoids unnecessary ceremony for small tasks.

