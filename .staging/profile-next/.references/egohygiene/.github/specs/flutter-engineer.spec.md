---
title: Flutter Engineer Specification
version: 1.1.0
status: approved
category:
  - specification
  - flutter
  - engineering
  - architecture
tags:
  - flutter
  - riverpod
  - drift
  - offline-first
  - cross-platform
  - ai-assisted-engineering
---

## Purpose

This specification defines the engineering contract for Flutter applications in the Ego Hygiene ecosystem.

Its purpose is to reduce architectural drift, analyzer failures, code generation errors, and rework during AI-assisted implementation.

Generated code must be correct-by-construction, aligned with the existing repository, and verified against the project tooling before work is considered complete.

---

## Workspace Rules

The Flutter application lives in:

```text
apps/egohygiene
```

All Flutter file paths, imports, package commands, and generated code must be relative to that application unless explicitly working on monorepo-level files.

Run project tasks from the monorepo root.

Required verification commands:

```bash
task pub-get
task generate
task analyze
```

Use additional checks when relevant:

```bash
task test
task test:coverage
task build:android
task build:web
```

Never claim completion unless `task generate` and `task analyze` pass.

---

## Repository Awareness

Before creating or modifying code, inspect the existing implementation.

Do not invent APIs, providers, models, routes, generated classes, localization keys, or theme tokens without checking the current repository first.

Prefer extending existing patterns over introducing new ones.

When modifying generated-code-backed files, ensure the corresponding source files and part files remain consistent.

---

## Core Philosophy

Flutter code must be:

- cross-platform
- offline-first
- privacy-first
- modular
- strongly typed
- accessible
- localized
- testable
- design-system aligned
- compatible with AI-assisted maintenance

The application should remain calm, cognitively lightweight, and human-centered.

---

## Static Analysis Rules

The project uses `very_good_analysis` with strict analyzer settings:

- strict casts
- strict inference
- strict raw types
- preserved trailing commas
- 120-character formatter width

Generated code must satisfy analyzer rules without relying on later cleanup.

Avoid:

- implicit dynamic
- raw `List` / `Map` / `Set`
- unchecked casts
- unnecessary nullable types
- unused imports
- unused providers
- dead code
- broad catch blocks unless intentionally documented

---

## Formatting

Use Dart formatting conventions configured by the project.

Dart source currently prefers single-quoted strings because `prefer_single_quotes` is enabled.

Use trailing commas for multiline declarations, constructors, widget trees, collection literals, and provider definitions.

---

## Riverpod Rules

The project uses Riverpod 3.

Prefer generated Riverpod providers using:

- `riverpod_annotation`
- `@riverpod`
- generated `*.g.dart` part files

Manual providers are allowed only when they are already part of the project pattern or when Riverpod generation is not appropriate.

Riverpod 3 guardrails:

- Do not type public app helpers with `Override`; this type is not safely available to app code.
- Do not use `valueOrNull`; use current Riverpod 3-compatible APIs such as `.value` or `.asData?.value`.
- If using `StateProvider`, import the Riverpod legacy API intentionally.
- Do not assume Riverpod 2 APIs are available.
- Always run `task generate` after provider changes.

---

## Drift Rules

The project uses Drift for local persistence.

When modifying persistence:

- preserve existing repository contracts
- keep migrations explicit
- avoid raw SQL unless consistent with current database architecture
- add or update tests for schema-sensitive changes
- do not store sensitive data casually
- prepare for encryption and migration compatibility

Generated Drift outputs must never be manually edited.

---

## Localization Rules

The project uses `slang`.

All user-facing strings should come from localization resources unless the string is:

- test-only
- debug-only
- log-only
- internal developer text

After changing localization files, run:

```bash
task generate
```

Do not create namespaced translation files unless `slang.yaml` enables namespaces.

---

## Routing Rules

The project uses `go_router`.

Navigation must be:

- declarative where possible
- testable
- deep-link compatible where relevant
- separated from pure presentation widgets

Do not hardcode navigation paths in many places when a route abstraction already exists.

---

## Design System Rules

Use existing design tokens and shared UI primitives.

Prefer existing theme, spacing, typography, color, motion, and accessibility utilities.

Avoid hardcoded colors, spacing, animation durations, and typography when project tokens exist.

UI should support:

- light mode
- dark mode
- future custom themes
- reduced motion
- screen readers
- large text
- keyboard/focus navigation where relevant

---

## AI Architecture Rules

AI code must remain provider-independent.

Do not couple features directly to OpenAI, Gemini, Anthropic, Ollama, or any single provider.

Use existing abstractions for:

- AI providers
- tool registry
- context assembly
- policy boundaries
- debug visibility

AI should distinguish:

- evidence
- interpretation
- user-provided context
- uncertainty
- personal observation

---

## Privacy Rules

Treat reflections, memories, health data, dreams, conversations, and location/context data as sensitive.

Do not log sensitive user content.

Do not export sensitive data by default.

Do not add telemetry, analytics, cloud sync, crash reporting, or remote logging without explicit architecture and consent handling.

---

## Testing Rules

Feature work should include appropriate tests.

Use:

- unit tests for models, engines, repositories, and pure logic
- widget tests for screens/components
- integration tests for critical flows
- golden tests only when visual stability is intentional

Update existing tests when changing behavior.

Run relevant tests before completion.

---

## Code Generation Rules

Generated files must never be edited manually.

Run code generation after changes involving:

- Riverpod
- Freezed
- JSON serialization
- Drift
- Slang localization

Required command:

```bash
task generate
```

If generated output changes unexpectedly, inspect the source cause rather than patching generated files.

---

## Completion Criteria

A task is complete only when:

- implementation follows existing architecture
- generated code is updated
- localization is updated where needed
- tests are added or updated where appropriate
- `task generate` passes
- `task analyze` passes
- relevant tests pass or failures are documented clearly

---

## Final Rule

Optimize every implementation for long-term maintainability, local-first privacy, accessibility, analyzer cleanliness, and low cognitive load.
