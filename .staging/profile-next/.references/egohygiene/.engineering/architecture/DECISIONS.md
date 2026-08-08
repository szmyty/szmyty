# Decisions

> *A living record of significant architectural, philosophical, and engineering decisions made throughout the evolution of the Ego Hygiene ecosystem.*

---

# Overview

Every complex system is the result of thousands of decisions.

Over time, the reasoning behind those decisions is often forgotten.

This document exists to preserve that reasoning.

Rather than documenting every implementation detail, it captures the important choices that shape the long-term direction of the ecosystem.

Future contributors should understand not only *what* was built, but *why* it was built that way.

---

# Purpose

The purpose of this document is to preserve architectural intent.

Each decision should answer questions such as:

- Why was this chosen?
- What alternatives were considered?
- What tradeoffs were accepted?
- What assumptions were made?
- Under what circumstances should this decision be revisited?

---

# Principles

## Decisions are Temporary

Every decision is made using the best information available at the time.

As new evidence emerges, decisions may evolve.

Changing direction is viewed as learning rather than failure.

---

## Preserve Reasoning

Implementation details naturally change.

Reasoning should remain discoverable.

Future contributors should understand the context surrounding major decisions.

---

## Favor Simplicity

Prefer solutions that reduce long-term complexity.

Avoid cleverness when clarity achieves the same outcome.

---

## Architecture Before Implementation

Whenever practical, major architectural decisions should be documented before implementation begins.

Doing so creates alignment between humans and AI while reducing unnecessary rework.

---

## Record Tradeoffs

No design is perfect.

Every meaningful decision involves tradeoffs.

Documenting those tradeoffs creates better future decisions.

---

# Recorded Decisions

> **Note:** All entries below are reconstructed from the current architecture and implementation evidence. Where the original decision rationale is not directly documented, it is marked as `Status: Reconstructed`.

---

## ADR-001 — Flutter as the Primary Application Framework

**Status:** Active  
**Date:** ~2024 (reconstructed from implementation)

### Context

Ego Hygiene requires a cross-platform mobile and desktop application. The project philosophy prioritizes human-centered UX, local-first data, and a development model where AI agents can reliably implement features from specifications.

### Alternatives Considered

- **React Native** — strong ecosystem but JavaScript tooling adds complexity; less strong compile-time safety.
- **Kotlin Multiplatform** — strong for Android/iOS but limited web and Linux support.
- **Native (Android/iOS)** — best platform performance but doubles development effort and prevents future desktop/web delivery.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Single codebase for Android, Web, Linux | Platform-specific polish requires extra effort |
| Strong Dart type safety | Smaller ecosystem than React Native |
| Hot reload accelerates iteration | Dart is less universally known |
| Rich widget primitives | Performance edge-cases at scale |

### Rationale

Flutter provides the best combination of cross-platform reach (Android, Web, Linux), a strongly typed language, a mature UI framework, and a development model that is deterministic enough for AI-assisted implementation. The local-first, offline-first architecture aligns with Flutter's performance model.

### Consequences

- All UI work is in Dart/Flutter.
- Platform-specific functionality is isolated behind service abstractions (`lib/shared/services/`).
- The codebase serves as a reference implementation for a reusable Flutter Foundation.

### Future Reconsideration

If Flutter's cross-platform parity degrades significantly, or if a competing framework closes the gap on type safety and tooling, this decision should be re-evaluated.

---

## ADR-002 — Riverpod for State Management and Dependency Injection

**Status:** Active  
**Date:** ~2024 (reconstructed from implementation)

### Context

A Flutter application of this complexity requires a state management solution that supports reactivity, testability, code generation, and composable dependency injection. Provider registration needs to be safe, compile-time verifiable, and AI-implementable from specifications.

### Alternatives Considered

- **Provider** — simpler but lacks generated providers and compile-time safety.
- **BLoC/Cubit** — more ceremonious; event/state separation adds boilerplate.
- **GetX** — less compositional; anti-patterns for testability.
- **MobX** — observable-based; code generation style differs from Dart idioms.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Code generation removes boilerplate | `build_runner` adds build step complexity |
| Compile-time provider graph safety | Migration from older patterns requires effort |
| Excellent testability via `ProviderContainer` | Learning curve for contributors unfamiliar with Riverpod |
| Composable and scoped providers | Potential over-abstraction for simple state |

### Rationale

Riverpod v3 with `riverpod_annotation` and `riverpod_generator` provides compile-time-safe dependency injection, generated providers, and a testable architecture pattern well-suited to specification-driven development. The code generation model aligns with how AI agents implement features from specs.

### Consequences

- All state uses generated Riverpod providers.
- `build_runner build` must be run after modifying providers.
- Providers are tested via `ProviderContainer` without widget trees.

### Future Reconsideration

If Riverpod's code generation or the `build_runner` infrastructure becomes unmaintained or significantly more complex, this decision should be revisited.

---

## ADR-003 — Drift and SQLite for Local-First Persistence

**Status:** Active  
**Date:** ~2024 (reconstructed from implementation)

### Context

Ego Hygiene stores personal reflection data: check-ins, memories, reflections, and knowledge. The application philosophy requires data to live on the user's device, operate without network connectivity, and never require cloud access for core functionality.

### Alternatives Considered

- **Hive** — fast key-value store but limited relational query support.
- **Isar** — good performance but less mature; schema migration tooling less robust.
- **Firebase / Firestore** — cloud-first, violates privacy-first and offline-first principles.
- **Realm** — good mobile performance but additional licensing considerations.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Full relational SQL with typed queries | Schema migration management complexity |
| Strong Dart type-safety via generated code | Code generation step required |
| Works entirely offline | Sync across devices requires additional implementation |
| Mature Flutter ecosystem | SQLite constraints (e.g., no native JSON columns) |

### Rationale

Drift provides type-safe SQL with Dart code generation, supports complex relational queries needed for timeline and memory systems, and operates entirely locally. This aligns with the privacy-first and offline-first architectural principles. SQLite is a proven, stable engine present on all target platforms.

### Consequences

- All persistent data lives in a local SQLite database managed by Drift.
- Database migrations must be managed explicitly.
- At-rest encryption strategy is a known open item (see `docs/AUDIT.md` C1).

### Future Reconsideration

If at-rest encryption requirements necessitate a different engine (e.g., SQLCipher), this decision may evolve. The `StorageService` abstraction exists to isolate this migration risk.

---

## ADR-004 — GoRouter for Navigation

**Status:** Active  
**Date:** ~2024 (reconstructed from implementation)

### Context

Navigation in a Flutter app with authentication, onboarding guards, and deep-link support requires a declarative, testable router. Routes need to be redirectable based on auth and onboarding state.

### Alternatives Considered

- **Navigator 2.0 directly** — maximum control but high boilerplate.
- **AutoRoute** — code-generated but more opinionated structure.
- **Beamer** — less community adoption than GoRouter.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Declarative route tree | Slightly verbose for simple navigation |
| Built-in redirect guards | Deep-link handling requires careful configuration |
| Official Flutter team recommendation | API changes between major versions |
| Deep-link and web URL support | |

### Rationale

GoRouter is the officially recommended Flutter routing solution, widely adopted, and supports the redirect guard pattern required for authentication and onboarding flows without custom navigation stack management.

### Consequences

- All navigation is declarative via GoRouter.
- Authentication and onboarding redirects are implemented as GoRouter redirect callbacks.
- Routes are defined in `lib/shared/routing/`.

### Future Reconsideration

If GoRouter introduces breaking API changes that complicate the routing model, this decision should be revisited.

---

## ADR-005 — Slang for Localization

**Status:** Active  
**Date:** ~2024 (reconstructed from implementation)

### Context

Localization in Flutter can be handled via the official `flutter_localizations` / ARB approach or via third-party type-safe alternatives. The project requires localization that is type-safe, AI-implementable, and consistent with the code generation model.

### Alternatives Considered

- **Official ARB + `flutter_gen`** — official but less ergonomic; strings accessed via context lookup.
- **Easy Localization** — runtime-loaded JSON; less compile-time safety.
- **Intl (standalone)** — verbose and less Dart-idiomatic.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Compile-time type-safe string access | Code generation step required |
| Dart-idiomatic API | Less widely known than ARB approach |
| Plural, gender, and parameter support | Migration from ARB if switching |
| Integrates naturally with Riverpod |  |

### Rationale

Slang provides type-safe, generated localization that aligns with the project's code-generation model and Riverpod integration pattern. It allows AI agents to implement localization accurately from specifications without runtime string lookup errors.

### Consequences

- All user-facing strings live in Slang translation files.
- `fvm flutter pub run slang` must be run after adding translations.
- Hardcoded strings in UI code violate architecture conventions.

### Future Reconsideration

If Slang becomes unmaintained or the official ARB tooling significantly closes the ergonomic gap, this decision should be revisited.

---

## ADR-006 — FVM for Flutter SDK Version Management

**Status:** Active  
**Date:** ~2024 (reconstructed from implementation)

### Context

Flutter SDK versions change frequently. CI, local development, and AI-assisted development must all use the same SDK version to produce consistent builds, avoid analyzer drift, and prevent version skew.

### Alternatives Considered

- **System-installed Flutter** — no version pinning; contributors may have different versions.
- **Mise / asdf** — general-purpose version managers; less Flutter-specific support.
- **Manual script** — fragile and hard to maintain.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Pinned Flutter version across all environments | Requires FVM installation step |
| `.fvmrc` provides single source of truth | Extra tool to learn |
| CI uses FVM via `flutter-version` resolver | FVM itself requires maintenance |

### Rationale

FVM provides a single, declarative Flutter version pin (`.fvmrc`) that applies consistently to local development, CI, and AI-assisted tasks. This eliminates version skew bugs and ensures generated code is reproducible across environments.

### Consequences

- All `flutter` commands are run as `fvm flutter`.
- `.fvmrc` pins the Flutter SDK version.
- CI resolves the Flutter version from FVM configuration.

### Future Reconsideration

If FVM loses active maintenance, or if Flutter introduces first-party SDK version pinning, this decision should be revisited.

---

## ADR-007 — Feature-First Application Organization

**Status:** Active  
**Date:** ~2024 (reconstructed from implementation)

### Context

Flutter applications can be organized either by technical layer (all presenters together, all repositories together) or by feature (all layers of a feature together). The project requires an organization model that scales, enables AI-assisted feature development, and isolates bounded contexts.

### Alternatives Considered

- **Layer-first (MVC/MVP)** — groups files by type; creates cross-feature coupling as the app grows.
- **Flat module structure** — too little organization for a complex app.
- **Package-per-feature** — maximum isolation but premature for a single-team project.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Each feature is self-contained | Requires discipline to avoid cross-feature imports |
| AI agents implement features from specifications cleanly | Shared logic must live in `lib/shared/` explicitly |
| Easy to reason about feature scope | Slightly more directory nesting |
| Natural boundary for future extraction | |

### Rationale

Feature-first organization aligns with the specification-driven development model: each feature maps to a spec, each spec maps to a directory. AI agents implementing a feature from a spec have a clear, predictable location for every file they create.

### Consequences

- Features live under `lib/features/<feature>/` with `presentation/`, `providers/`, `domain/`, and `data/` subdirectories.
- Shared infrastructure lives under `lib/shared/`.
- Cross-feature dependencies are prohibited except through `lib/shared/`.

### Future Reconsideration

If the feature count grows substantially, package-per-feature extraction may be appropriate.

---

## ADR-008 — Privacy-First and Offline-First Architecture

**Status:** Active  
**Date:** ~2024 (reconstructed from implementation)

### Context

Ego Hygiene stores deeply personal data: reflections, mental states, goals, and cognition patterns. Users must be able to trust that their data is not transmitted to external services without explicit consent.

### Alternatives Considered

- **Cloud-first with privacy controls** — easier to build sync but requires trusting a cloud provider with sensitive data.
- **Optional sync as a paid feature** — retains local-first but adds backend complexity prematurely.
- **End-to-end encrypted sync** — valid long-term direction but out of scope for v1.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Data never leaves the device by default | No built-in multi-device sync |
| Works fully offline | Cross-device features require future investment |
| Aligns with product philosophy | Requires careful at-rest encryption strategy (open item) |
| Builds user trust |  |

### Rationale

The project mission centers on human cognition and self-understanding. Personal reflection data is highly sensitive. An offline-first, privacy-first architecture makes the privacy guarantee the default, not an opt-in. This also eliminates backend infrastructure costs and dependencies for v1.

### Consequences

- No data is transmitted to external servers without explicit user action.
- The AI provider abstraction defaults to a demo/local provider.
- At-rest encryption is a known open item (see `docs/AUDIT.md` C1).

### Future Reconsideration

If users strongly demand cross-device sync, an end-to-end encrypted sync layer (separate from core persistence) should be evaluated.

---

## ADR-009 — Specification-Driven Development

**Status:** Active  
**Date:** ~2024 (reconstructed from implementation)

### Context

This project uses AI agents for implementation work. For AI-assisted development to produce consistent, correct, and reviewable output, agents need machine-readable contracts that define intent, constraints, and acceptance criteria.

### Alternatives Considered

- **Verbal instructions only** — inconsistent; each implementation requires renegotiation.
- **Test-driven only** — tests verify behavior but don't capture intent or constraints upfront.
- **Wiki documentation** — human-readable but not well-structured for AI consumption.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Specifications act as contracts for AI agents | Spec files require maintenance |
| Consistent output across sessions | Upfront spec authorship time |
| Specifications document intent for future contributors | Spec drift if implementation diverges |
| Reduces implementation ambiguity |  |

### Rationale

Specification files in `.github/specs/` serve as executable intent. They define what should exist, how it should behave, and what constraints apply. AI agents load relevant specs before implementing. This creates a reviewable, referenceable contract between human intent and AI output.

### Consequences

- Every significant system has a spec in `.github/specs/`.
- AI agents are instructed to load relevant specs before implementing.
- Specs are updated when implementations evolve.

### Future Reconsideration

If the spec system creates more overhead than clarity, the model should be simplified.

---

## ADR-010 — Reusable Workflow and Composite Action Strategy

**Status:** Active  
**Date:** ~2025 (reconstructed from CI implementation)

### Context

CI pipelines with multiple jobs, platforms, and workflows tend to accumulate duplicated YAML. The project needed a CI architecture that is maintainable, DRY, and reusable across the build, test, and release pipelines.

### Alternatives Considered

- **Flat workflow files** — simple but duplicates setup and configuration logic.
- **External CI service (CircleCI, etc.)** — additional vendor dependency.
- **Monorepo-specific CI tools (Turborepo, Nx)** — designed for JS monorepos; mismatch for Flutter + Python.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Reusable workflows reduce YAML duplication | Composite action versioning complexity |
| CI logic is testable and reviewable in one place | Additional indirection |
| Changes propagate automatically to all callers | Debugging composite actions is harder |

### Rationale

GitHub Actions reusable workflows (`.github/workflows/reusable/`) and composite actions (`.github/actions/`) allow the build, test, and release pipelines to share setup, Flutter configuration, and code generation logic without duplication.

### Consequences

- Common steps (Flutter setup, code generation, caching) live in reusable actions.
- Workflow files call reusable workflows rather than repeating steps.
- CI changes affect all workflows consistently.

### Future Reconsideration

If the action/workflow graph becomes too complex, or if CI execution time increases significantly, the reusable structure should be simplified.

---

## ADR-011 — Deferred Flutter Foundation Extraction

**Status:** Deferred  
**Date:** ~2025 (reconstructed from extraction plan)

### Context

Ego Hygiene is designed so that ~80% of its codebase is reusable Flutter infrastructure. Extracting that infrastructure into standalone packages is a long-term goal. However, extraction before the infrastructure is stable creates churn and complexity.

### Alternatives Considered

- **Extract early** — publish packages from the start; expensive to maintain.
- **Extract after v1** — wait for stability; chosen approach.
- **Never extract** — forgo the foundation reuse goal.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Foundation is validated in production before extraction | Users of the foundation must wait for v1 |
| Reduces extraction churn | Foundation and app code remain coupled during development |
| Allows interfaces to stabilize before public API commitment |  |

### Rationale

Extracting unstable infrastructure into public packages creates a maintenance burden and premature API commitments. The correct sequence is to use the infrastructure in a real application first, stabilize it, then extract it. Ego Hygiene v1 is the reference implementation that proves the foundation is ready to extract.

### Consequences

- Foundation code lives in `apps/egohygiene/lib/shared/` during development.
- The extraction plan is documented in `docs/architecture/extraction-plan.md`.
- Extraction begins after Ego Hygiene v1 is shipped.

### Future Reconsideration

The extraction plan should be revisited after v1 ships. If another application needs the foundation before v1, a partial extraction may be justified.

---

## ADR-012 — Lifecycle-Oriented Repository Organization

**Status:** Active  
**Date:** ~2025 (reconstructed from repository structure)

### Context

The repository contains not only Flutter application code but also publishing pipelines, schemas, documentation, research, and AI agent infrastructure. A purely technology-oriented top-level structure (e.g., `src/`, `scripts/`, `infra/`) would obscure the lifecycle relationships between these layers.

### Alternatives Considered

- **Technology-oriented structure** — groups by technology type (e.g., `python/`, `flutter/`, `github/`).
- **Domain-oriented structure** — groups by product domain; risks mixing implementation layers.
- **Flat repository** — simple but hard to navigate at scale.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Each directory has a clear purpose in the lifecycle | More top-level directories |
| Lifecycle relationships are immediately discoverable | Contributors must learn the lifecycle model |
| Supports long-form content, schemas, and tooling alongside code |  |

### Rationale

The repository is not just a Flutter app. It is a publishing platform, a knowledge system, and a reference implementation. Organizing by lifecycle (app code, publishing, schemas, docs, tooling) reflects how information flows through the system rather than what technology it uses.

### Consequences

- `apps/` — Flutter application code
- `publishing/` — long-form content and publication tooling
- `schemas/` — cross-system JSON schemas
- `docs/` — operational documentation
- `.engineering/` — architectural and philosophical corpus
- `.github/` — AI agent infrastructure, CI, specs

### Future Reconsideration

If the repository splits into multiple repositories (e.g., a separate organization repo), the lifecycle-oriented structure should be preserved within each repository.

---

## ADR-013 — Direct-to-Main Commits for Automated Publishing Synchronization

**Status:** Active (intentional)  
**Date:** ~2025 (reconstructed from workflow implementation)

### Context

The Medium RSS sync and Pinterest RSS sync workflows run on a schedule and ingest external RSS feeds to produce archive files committed to the repository. These workflows need a commit strategy: either open a pull request for each sync run or commit directly to `main`.

### Alternatives Considered

- **Pull request per sync** — adds review overhead; delays archive; creates noise in PR history.
- **Direct commit to `main`** — simpler; no review required for automated archive data.
- **External storage (S3, artifact)** — stores data outside the repository; loses version history.

### Tradeoffs

| Benefit | Cost |
|---|---|
| Archive is immediately available in `main` | No human review gate for automated commits |
| Simpler workflow implementation | Bypasses branch protection if misconfigured |
| `[skip ci]` prevents recursive CI triggers | Requires `contents: write` permission |
| Archive history is visible in git log |  |

### Rationale

The synchronized content is structured archive data (Medium article metadata, Pinterest board data) with stable naming conventions and duplicate prevention. It does not affect application code, tests, or behavior. Direct commit with `[skip ci]` is the appropriate pattern for low-risk, high-frequency automated archive updates. See `docs/architecture/publishing-automation.md` for full documentation.

### Consequences

- Automated sync workflows commit directly to `main` using `github-actions[bot]`.
- `[skip ci]` is appended to all automated commit messages to prevent recursive CI.
- Operators can recover from bad syncs by reverting the offending commit.
- Branch protection rules must allow `github-actions[bot]` commits if enabled.

### Future Reconsideration

If branch protection is tightened or if the archive content requires human review before landing, this pattern should be replaced with pull-request-based synchronization.

---

# Types of Decisions

Decisions recorded in this document span:

- architecture
- ontology
- engineering methodology
- AI behavior
- UX philosophy
- repository organization
- design system
- publishing workflow
- ecosystem evolution

---

# Evolution

This document should evolve alongside the ecosystem.

New decisions should be added rather than replacing historical context.

The goal is not to preserve every implementation detail.

The goal is to preserve understanding.

---

# Summary

The quality of a system depends not only on the decisions it contains, but on the ability of future contributors to understand why those decisions were made.

This document exists to preserve that understanding.

It provides continuity across time, contributors, and evolving implementations.

