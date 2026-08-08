# 🗺️ Repository Map

> *A complete structural map of the Ego Hygiene repository.*

---

## Purpose

This document describes every significant file and directory in the repository, what it contains, and why it exists.

Use this map to orient yourself before exploring a specific area.

---

## Root Directory

### Foundational Documents

| File | Purpose |
|---|---|
| [START_HERE.md](../START_HERE.md) | Guided entry point for contributors and AI agents |
| [README.md](../README.md) | Project overview, quick start, and development commands |
| [.engineering/architecture/FOUNDATIONS.md](../.engineering/architecture/FOUNDATIONS.md) | Product philosophy — what Ego Hygiene is and why it exists |
| [VISION.md](../VISION.md) | Long-term vision for the project |
| [PURPOSE.md](../PURPOSE.md) | Core purpose and mission statement |
| [.engineering/architecture/MANIFESTO.md](../.engineering/architecture/MANIFESTO.md) | Beliefs and commitments behind the project |
| [.engineering/architecture/PRINCIPLES.md](../.engineering/architecture/PRINCIPLES.md) | Core engineering and product principles |
| [.engineering/architecture/PILLARS.md](../.engineering/architecture/PILLARS.md) | Foundational pillars the system is built upon |

### Architecture and Engineering

| File | Purpose |
|---|---|
| [ARCHITECTURE.md](../ARCHITECTURE.md) | Architecture reference and 80/20 foundation boundary |
| [SYSTEM.md](../SYSTEM.md) | AI-native engineering system — how the project is designed and built |
| [.engineering/architecture/DESIGN.md](../.engineering/architecture/DESIGN.md) | Design system principles and visual language |
| [.engineering/architecture/DESIGN_SYSTEM.md](../.engineering/architecture/DESIGN_SYSTEM.md) | Design system specification details |
| [.engineering/architecture/ECOSYSTEM.md](../.engineering/architecture/ECOSYSTEM.md) | How Ego Hygiene fits into the broader application ecosystem |
| [.engineering/architecture/DECISIONS.md](../.engineering/architecture/DECISIONS.md) | Architectural decisions and their rationale |
| [.engineering/architecture/IMPLEMENTATION_SUMMARY.md](../.engineering/architecture/IMPLEMENTATION_SUMMARY.md) | Summary of what has been implemented |

### Knowledge Framework

| File | Purpose |
|---|---|
| [.engineering/architecture/AI_CONSTITUTION.md](../.engineering/architecture/AI_CONSTITUTION.md) | Principles governing AI system behavior in this repository |
| [.engineering/architecture/EPISTEMOLOGY.md](../.engineering/architecture/EPISTEMOLOGY.md) | How knowledge is structured and validated |
| [.engineering/architecture/ONTOLOGY.md](../.engineering/architecture/ONTOLOGY.md) | Core domain concepts and their relationships |
| [.engineering/architecture/METHODOLOGY.md](../.engineering/architecture/METHODOLOGY.md) | Engineering methodology documentation |
| [.engineering/architecture/META.md](../.engineering/architecture/META.md) | Repository metadata and self-description |

### Planning and Evolution

| File | Purpose |
|---|---|
| [ROADMAP.md](../ROADMAP.md) | Near-term and long-term direction |
| [ONBOARDING.md](../ONBOARDING.md) | AI agent onboarding and synchronization protocol |

### Configuration

| File | Purpose |
|---|---|
| [Taskfile.yml](../Taskfile.yml) | One-command developer workflows (setup, generate, test, build, run) |
| [.fvmrc](../.fvmrc) | Pinned Flutter SDK version (via FVM) |
| [package.json](../package.json) | Node dependencies (commitlint hooks) |
| [commitlint.config.js](../commitlint.config.js) | Commit message linting rules |
| [SECURITY.md](../SECURITY.md) | Security policy and vulnerability disclosure process |
| [LICENSE](../LICENSE) | Project license |

---

## docs/

Developer documentation covering setup, architecture, testing, and domain knowledge.

### Top-Level Docs

| File | Purpose |
|---|---|
| [docs/developer-setup.md](developer-setup.md) | Environment prerequisites, setup commands, and common troubleshooting |
| [docs/testing.md](testing.md) | Testing strategy, test types, coverage configuration |
| [docs/commits.md](commits.md) | Commit message conventions |
| [docs/AUDIT.md](AUDIT.md) | Architecture audit report (legacy, 2026-07-06 — see `audits/` for current system) |
| [docs/READING_ORDER.md](READING_ORDER.md) | Recommended reading paths by audience |
| [docs/CONTRIBUTOR_GUIDE.md](CONTRIBUTOR_GUIDE.md) | Contribution workflow and standards |
| [docs/REPOSITORY_MAP.md](REPOSITORY_MAP.md) | This file |

### docs/architecture/

Detailed architecture documentation for each major system area.

| File | Purpose |
|---|---|
| [overview.md](architecture/overview.md) | Core principles, 80/20 boundary, feature-first organization |
| [flutter-foundation.md](architecture/flutter-foundation.md) | Tech stack, state management, localization, build system, CI/CD |
| [design-system.md](architecture/design-system.md) | Design tokens, colors, spacing, typography, accessibility |
| [storage.md](architecture/storage.md) | Encryption, storage architecture, privacy, data portability |
| [ai.md](architecture/ai.md) | AI providers, context assembly, memory engine, knowledge graph |
| [routing.md](architecture/routing.md) | Navigation and GoRouter configuration |
| [testing.md](architecture/testing.md) | Testing strategy and shared test helpers |
| [startup.md](architecture/startup.md) | Environment management and feature flag engine |
| [publishing-automation.md](architecture/publishing-automation.md) | Medium and Pinterest sync workflows, direct-to-main rationale |
| [extraction-plan.md](architecture/extraction-plan.md) | Flutter Foundation extraction phases and package structure |

### docs/domains/

Domain model documentation for application-specific concepts.

| File | Purpose |
|---|---|
| [domains/README.md](domains/README.md) | Domain documentation index |
| [domains/TEMPLATE.md](domains/TEMPLATE.md) | Template for new domain documentation |
| [domains/mental-emotional-health/README.md](domains/mental-emotional-health/README.md) | Mental and emotional health domain model |

### docs/practices/

Documentation for structured practices within the application.

| File | Purpose |
|---|---|
| [practices/README.md](practices/README.md) | Practice documentation index |
| [practices/reflection/README.md](practices/reflection/README.md) | Reflection practice framework |
| [practices/gratitude.md](practices/gratitude.md) | Gratitude practice |
| [practices/abundance.md](practices/abundance.md) | Abundance mindset practice |

### docs/research/

Research foundations informing the product and architecture.

| File | Purpose |
|---|---|
| [research/README.md](research/README.md) | Research documentation index |
| [research/personal-health-knowledge-engine.md](research/personal-health-knowledge-engine.md) | Personal health knowledge engine research |

### docs/storage/

Storage-specific implementation documentation.

| File | Purpose |
|---|---|
| [storage/migrations.md](storage/migrations.md) | Database migration history and strategy |

---

## .github/

GitHub-specific configuration, CI/CD workflows, AI agent definitions, and engineering specifications.

### .github/agents/

AI agent configuration files defining how AI systems should behave.

| File | Purpose |
|---|---|
| `auditor.agent.md` | Repository auditor agent — evidence-based auditing and standardized report generation |
| `flutter-engineer.agent.md` | Flutter engineer agent — capabilities and operating constraints |
| `specfile-creator.agent.md` | Specification file creator agent |

### .github/skills/flutter/

Skill documents teaching AI systems how to perform specific Flutter engineering tasks.

| File | Purpose |
|---|---|
| `ai-providers.md` | How to implement AI provider abstractions |
| `architecture.md` | Flutter architecture patterns and conventions |
| `design-system.md` | Design token usage and theming |
| `localization.md` | Slang-based type-safe localization |
| `notifications.md` | Notification system implementation |
| `offline-first.md` | Drift-based offline-first storage patterns |
| `routing.md` | GoRouter navigation patterns |
| `state-management.md` | Riverpod with code generation |
| `testing.md` | Test infrastructure and conventions |

### .github/specs/

Comprehensive specifications for all system components. Specifications define intent and outlive implementation.

| File | Purpose |
|---|---|
| `auditor.spec.md` | Repository auditor specification — universal audit contract, strategies, and output format |
| `flutter-application.spec.md` | Full Flutter application specification |
| `flutter-engineer.spec.md` | Flutter engineering standards and conventions |
| `build-pipeline.spec.md` | CI/CD build pipeline specification |
| `design-system.spec.md` | Design system specification |
| `domain-framework.spec.md` | Domain model framework |
| `insight-framework.spec.md` | Insight generation framework |
| `offline-first-storage.spec.md` | Offline-first storage specification |
| `practice-framework.spec.md` | Structured practice framework |
| `reflection.spec.md` | Reflection feature specification |
| `reflector.spec.md` | Reflector AI synchronization protocol |
| `routing-navigation.spec.md` | Navigation specification |
| `testing-strategy.spec.md` | Testing strategy specification |
| `specfile.spec.md` | How to write specification files |
| `artifact-*.spec.md` | Artifact type specifications (documentation, domain, research, schema, etc.) |

### .github/workflows/

CI/CD automation workflows.

| File | Purpose |
|---|---|
| `build.yml` | Primary CI pipeline: pub get, code generation, analyze, test, coverage |

---

## audits/

Canonical location for all repository audit reports. See [`audits/README.md`](../audits/README.md) for the full audit system documentation.

| Convention | Description |
|---|---|
| Filename format | `repository-health-<YYYY-MM-DD>.md` or `<scope>-<YYYY-MM-DD>.md` |
| Requested via | `.github/agents/auditor.agent.md` |
| Governed by | `.github/specs/auditor.spec.md` |
| Behavior | Read-only by default; each file is an immutable historical record |
| Finding tracking | Converted to GitHub Issues for backlog management |

**Note:** The first comprehensive audit (`docs/AUDIT.md`, 2026-07-06) predates this system and is preserved in its original location.

---

## apps/egohygiene/

The Flutter application workspace. All application source code lives here.

### apps/egohygiene/lib/

Source code organized using feature-first architecture.

```
lib/
├── app/                         # Application-level configuration
│   ├── app.dart                 # Root MaterialApp widget, theme resolution
│   ├── authentication/          # Authentication lifecycle
│   └── startup/                 # App startup sequence
├── features/                    # Feature modules (application-specific)
│   ├── check_in/                # Daily check-in feature
│   ├── conversation/            # AI conversation feature
│   ├── graph/                   # Knowledge graph visualization
│   ├── health/                  # Health tracking feature
│   ├── home/                    # Home screen and navigation hub
│   ├── memory/                  # Memory and timeline feature
│   ├── onboarding/              # First-launch onboarding flow
│   ├── progress/                # Progress tracking feature
│   ├── reflection/              # Reflection entry and review
│   └── settings/                # Application settings
└── shared/                      # Reusable infrastructure (80% boundary)
    ├── README.md                # Canonical shared taxonomy and ownership boundary
    ├── ai/                      # AI provider abstractions
    ├── analytics/               # Analytics engine
    ├── assets/                  # Asset management helpers
    ├── conflict/                # Conflict resolution engine
    ├── connectivity/            # Network connectivity monitoring
    ├── context/                 # Context assembly engine
    ├── debug/                   # Debug and developer tools
    ├── environment/             # Environment variable management
    ├── flags/                   # Feature flag engine
    ├── goal/                    # Goal management domain
    ├── graph/                   # Knowledge graph engine
    ├── health/                  # Health domain engine
    ├── insight/                 # Insight generation engine
    ├── localization/            # Slang i18n setup
    ├── memory/                  # Memory engine
    ├── performance/             # Performance monitoring
    ├── personal_health/         # Personal health knowledge engine
    ├── portability/             # Data export and portability
    ├── practice/                # Practice framework
    ├── privacy/                 # Privacy engine
    ├── providers/               # Shared Riverpod providers
    ├── routing/                 # GoRouter configuration
    ├── services/                # Service abstractions (StorageService, AIProvider, etc.)
    ├── settings/                # Settings management
    ├── storage/                 # Storage abstraction (Drift)
    ├── sync/                    # Sync engine
    ├── theme/                   # Design tokens and theming
    ├── timeline/                # Timeline engine
    ├── version/                 # Version management
    └── widgets/                 # Shared UI components
```

### Feature Structure

Each feature follows the same internal structure:

```
feature_name/
├── feature.dart          # Public barrel — exports domain types, providers, primary screens
├── presentation/         # UI screens and widgets (internal, not exported)
├── providers/            # Riverpod state providers
├── domain/               # Business logic and models
└── data/                 # Repositories and storage access
```

### apps/egohygiene/test/

Unit and widget tests. Mirrors the `lib/` structure.

```
test/
├── helpers/              # Shared test helpers (FakeStorageService, etc.)
├── app/                  # Tests for app-level code
├── features/             # Feature-level tests
└── shared/               # Tests for shared infrastructure
```

### apps/egohygiene/integration_test/

End-to-end integration tests using Flutter integration test framework.

```
integration_test/
├── helpers/              # Integration test helpers (pumpApp, RequiredOnboardingManager)
└── app_test.dart         # Smoke test entry point
```

---

## publishing/

The publishing workspace, organized around the content lifecycle — from knowledge extraction to distribution.

```
publishing/
    sources/        – Canonical authored source material
    channels/       – Publication mirrors and external platform output
    tools/          – Reusable publishing tooling
    specs/          – Publishing specifications
    schemas/        – Content schemas
    docs/           – Publishing documentation
```

**Sources** (`publishing/sources/`) contain the canonical authored content:
- `articles/` — long-form essays and articles
- `synapses/` — living stream of insights and knowledge notes
- `magazine/` — AI-powered magazine publishing engine
- `books/` — placeholder for future book content
- `papers/` — placeholder for future research papers

**Channels** (`publishing/channels/`) contain publication mirrors:
- `medium/` — synchronized Medium article archive
- `pinterest/` — synchronized Pinterest board archive
- `website/`, `newsletter/`, `linkedin/` — placeholders for future channels

**Tools** (`publishing/tools/`) contain reusable publishing tooling:
- `mindlint/` — spec-driven article linter
- `medium-rss/` — Medium RSS ingestion tool
- `pinterest-rss/` — Pinterest RSS ingestion tool

---

## schemas/

Repository-level canonical schema definitions and ownership boundaries.

- [schemas/README.md](../schemas/README.md) — ownership, scope, and evolution strategy
- `schemas/practices/reflection.schema.json` — canonical reflection record schema

---

## website/

Placeholder for future repository-owned website implementation.

- [website/README.md](../website/README.md) — purpose, ownership, and current status

---

## tasks/

Task definitions referenced by `Taskfile.yml`.

---

## lint/

Custom linting configurations and rules.

---

## Key File Relationships

```
START_HERE.md
    → README.md (quick start)
    → ONBOARDING.md (AI protocol)
    → docs/READING_ORDER.md (reading path)
    → docs/CONTRIBUTOR_GUIDE.md (contribution)
    → docs/REPOSITORY_MAP.md (this file)

ARCHITECTURE.md
    → docs/architecture/overview.md
    → docs/architecture/flutter-foundation.md
    → docs/architecture/ai.md
    → docs/architecture/storage.md
    → ...

SYSTEM.md
    → .github/specs/
    → .github/agents/
    → .github/skills/

ONBOARDING.md
    → SYSTEM.md
    → ARCHITECTURE.md
    → .github/specs/reflector.spec.md
```
