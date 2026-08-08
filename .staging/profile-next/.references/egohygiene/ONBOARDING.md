# 🧠 Ego Hygiene — AI Onboarding

---

## Purpose

This document serves as the primary entry point for AI assistants working within this repository.

Before performing any implementation work, AI systems must synchronize with the repository's architectural intent, specifications, standards, and active task context.

The goal is:

    alignment before execution

not:

    execution before understanding

---

# Required Reading Order

Before beginning any task, read:

1. SYSTEM.md
2. Relevant specifications in `.github/specs/`
3. Relevant agents in `.github/agents/`
4. Relevant skills in `.github/skills/`
5. FOUNDATIONS.md
6. DESIGN.md
7. ARCHITECTURE.md
8. ROADMAP.md
9. TASK.md

Only after repository context is loaded should implementation begin.

For the complete audience-aware reading order, see [docs/READING_ORDER.md](docs/READING_ORDER.md).

For a structural map of every file, see [docs/REPOSITORY_MAP.md](docs/REPOSITORY_MAP.md).

---

# Repository Architecture Context

## Engineering System

This repository treats itself as a layered knowledge system, not a code container.

```
Identity        VISION.md · PURPOSE.md · FOUNDATIONS.md · MANIFESTO.md
    ↓
Design          DESIGN.md · DESIGN_SYSTEM.md
    ↓
Architecture    ARCHITECTURE.md · docs/architecture/
    ↓
Engineering     .github/specs/ · .github/skills/ · .github/agents/
    ↓
Execution       ROADMAP.md · GitHub Issues
    ↓
Implementation  apps/egohygiene/
```

Code is the final artifact.

The layers above it are authoritative.

---

## Application Architecture

The Flutter application follows a **feature-first** architecture with a clear 80/20 boundary:

- ~80% is reusable Flutter infrastructure (`lib/shared/`)
- ~20% is Ego Hygiene-specific feature logic (`lib/features/`)

### Feature Module Structure

Each feature in `lib/features/` is self-contained:

```
feature_name/
├── feature.dart      # Public barrel (domain types, providers, primary screens)
├── presentation/     # UI screens and widgets
├── providers/        # Riverpod state providers
├── domain/           # Business logic and models
└── data/             # Repositories and storage access
```

### Shared Infrastructure

`lib/shared/` contains reusable engines and abstractions:

| Engine | Location | Purpose |
|---|---|---|
| Memory Engine | `lib/shared/memory/` | MemoryManager, MemoryStore, MemoryType |
| Sync Engine | `lib/shared/sync/` | SyncManager, SyncQueue, SyncOperation |
| Analytics Engine | `lib/shared/analytics/` | AnalyticsManager, AnalyticsProvider |
| Timeline Engine | `lib/shared/timeline/` | TimelineManager, TimelineSource |
| Personal Health Engine | `lib/shared/personal_health/` | HealthManager, HealthItemStore |
| Version Engine | `lib/shared/version/` | VersionManager, VersionService |
| Location Engine | `lib/shared/location/` | LocationManager, LocationProvider, GeocodingProvider, TimezoneResolver |
| Theme Personalization | `lib/shared/theme/personalization/` | ThemeGenerator, ImageThemeService |
| Service Abstractions | `lib/shared/services/` | StorageService, AIProvider, NotificationService |

---

## Key Conventions for AI Implementation

### Service Abstractions

Never depend on concrete implementations.

Use service abstractions from `lib/shared/services/`.

### State Management

Use Riverpod with `@riverpod` code generation.

Run `flutter pub run build_runner build --delete-conflicting-outputs` after adding or modifying providers.

### Design Tokens

Use tokens from `lib/shared/theme/theme_tokens.dart` (AppColors, AppSpacing, AppRadius, etc.).

Never hardcode values.

### Barrel Exports

Each feature exposes a `feature.dart` barrel.

Export only: domain types, public providers, primary screens.

Do **not** export: data implementations, internal widgets.

### Generated Files

`*.g.dart` and `strings.g.dart` are excluded from version control.

Never commit generated files.

---

# Core Principles

## Repository First

The repository is a knowledge system.

Code is a downstream artifact.

Specifications, architecture, and repository context take precedence over implementation details.

---

## Reflector Alignment

This repository adopts Reflector-style synchronization.

AI systems should:

- respect synchronization boundaries
- avoid recursive drift
- surface uncertainty early
- terminate work in auditable states

Reference:

    .github/specs/reflector.spec.md

---

## Scope Discipline

Implement only the requested task.

Do not:

- expand scope
- redesign architecture
- introduce unrelated dependencies
- modify unrelated files

unless explicitly instructed.

---

## Architecture Respect

Architecture is authoritative.

When architecture is unclear:

    pause
    surface ambiguity
    request clarification

Do not invent architecture.

---

## Simplicity First

Prefer:

- clear code
- maintainable code
- composable code

Avoid:

- cleverness
- premature optimization
- unnecessary abstractions

---

# Ego Hygiene Philosophy

Ego Hygiene is a personal cognition system.

The project emphasizes:

- reflection
- navigation
- synchronization
- memory
- progress
- insight

Technology exists to support those goals.

Technology is not the goal.

---

# Execution Pattern

For each task:

1. Read TASK.md
2. Identify scope
3. Load relevant specifications
4. Load relevant skills
5. Implement bounded changes
6. Validate implementation
7. Leave repository in a synchronized state

---

# Preferred Output Characteristics

Generated work should be:

- deterministic
- modular
- composable
- documented
- testable
- portable

---

# AI Role

You are operating as:

    Implementer

You are not:

    Product Owner
    Architect
    Governance Authority

Architecture and continuation decisions belong to humans.

---

# Escalation Rules

Escalate when:

- architecture is ambiguous
- specifications conflict
- requirements are incomplete
- implementation requires expanding scope

When uncertain:

    ask
    do not assume

---

# Final Rule

Understand first.

Implement second.

Synchronize before continuing.
