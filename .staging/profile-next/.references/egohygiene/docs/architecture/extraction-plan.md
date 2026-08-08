# Flutter Foundation Extraction Plan

This document defines the formal plan for extracting Ego Hygiene's reusable infrastructure into a standalone Flutter Foundation starter.

**This plan does not move any code.**

It defines boundaries, proposed package structure, extraction phases, dependency direction, naming conventions, migration risks, and extraction readiness criteria.

---

## Context

Ego Hygiene is intentionally designed as a **foundation-first application**.

- ~80% of the repository is intended to be reusable Flutter infrastructure.
- ~20% is intended to be Ego Hygiene-specific application logic.

The long-term goal is for Ego Hygiene to serve as the **reference implementation** that validates a reusable Flutter Foundation — one that future Flutter applications can adopt as a starting point rather than rebuilding from scratch.

See [overview.md](./overview.md) for the architectural principles that inform this plan.

---

## Foundation Boundary

### Reusable Foundation Infrastructure

The following systems are general-purpose infrastructure with no dependency on Ego Hygiene's domain concepts. They belong in the extracted foundation.

| System | Current Location | Description |
|---|---|---|
| **Startup lifecycle** | `lib/app/`, `lib/shared/environment/`, `lib/shared/flags/` | App initialization, environment configuration, feature flag engine |
| **Authentication lifecycle** | `lib/app/authentication/` | Abstract `AuthenticationProvider`, `AuthenticationSession`, `UserRole`, `DemoAuthenticationProvider` |
| **Permission lifecycle** | `lib/shared/` | Platform permission request orchestration |
| **Notification lifecycle** | `lib/shared/services/notification_service.dart` | Abstract `NotificationService` with local and remote push support |
| **Routing** | `lib/shared/routing/` | GoRouter-based navigation with authentication and onboarding redirect guards |
| **Theme and design system** | `lib/shared/theme/` | Design tokens: `AppColors`, `AppSpacing`, `AppRadius`, `AppElevation`, `AppShadows`, `AppDurations`, `AppCurves`, `AppOpacity` |
| **Localization** | `lib/shared/localization/` | Type-safe i18n using Slang with locale switching |
| **Storage abstractions** | `lib/shared/storage/`, `lib/shared/services/` | `StorageService`, `SecureStorageService`, `Repository<T,ID>` abstraction |
| **Settings engine** | `lib/shared/settings/` | User preferences with typed access and persistence |
| **Analytics engine** | `lib/shared/analytics/` | `AnalyticsProvider`, `AnalyticsManager`, `NoopAnalyticsProvider`, consent state |
| **Sync engine** | `lib/shared/sync/` | `SyncManager`, `SyncQueue`, `SyncOperation`, `SyncStatus`, `SyncCheckpoint`, `InMemorySyncQueue` |
| **Memory engine** | `lib/shared/memory/` | `Memory`, `MemoryType`, `MemoryStore`, `MemoryManager`, `InMemoryMemoryStore` |
| **Context assembly engine** | `lib/shared/context/` | `ContextManager`, `ContextSource`, composable context pipeline for AI |
| **AI abstractions** | `lib/shared/services/ai_provider.dart` | `AIProvider`, `AIMessage`, `AIConversation`, `DemoAIProvider`, `AIProviderRegistry` |
| **Privacy engine** | `lib/shared/privacy/` | Data minimization, consent tracking, portability controls |
| **Data portability** | `lib/shared/portability/` | Export and import abstractions |
| **Connectivity** | `lib/shared/connectivity/` | Network state detection and reactive streams |
| **Performance** | `lib/shared/performance/` | Performance monitoring abstractions |
| **Conflict resolution** | `lib/shared/conflict/` | `ConflictResolver`, `ConflictStrategy`, `InMemoryConflictStore` |
| **Plugin registry** | `lib/shared/` | Provider-injectable plugin registration patterns |
| **Shared widgets** | `lib/shared/widgets/` | `AppCard`, `AppScaffold`, `AppLoadingIndicator`, and other general-purpose UI primitives |
| **Testing infrastructure** | `test/helpers/` | `FakeStorageService`, shared test fakes and helpers |
| **CI/CD pipeline** | `.github/workflows/` | Build, test, coverage, and release workflows |
| **Release pipeline** | `publishing/`, `Taskfile.yml` | Semantic release, version management, build signing |
| **Developer experience** | `Taskfile.yml`, `.fvmrc`, `lint/` | FVM, Taskfile tasks, lint rules |

---

### Ego Hygiene-Specific Code

The following systems are tightly coupled to Ego Hygiene's domain model and human development philosophy. They belong in the application layer and should not be extracted.

| System | Current Location | Description |
|---|---|---|
| **Ontology** | `ONTOLOGY.md`, `lib/` | The 12-domain model of human life and its philosophical structure |
| **Domains** | `docs/domains/`, `lib/shared/health/` | Domain definitions (health, relationships, finance, purpose, etc.) and domain health engine |
| **Practices** | `docs/practices/`, `lib/shared/practice/` | Reflection, gratitude, abundance, mindfulness, and other behavioral practices |
| **Rituals** | `ROADMAP.md`, `docs/` | Intentional sequences of practices composed for specific life contexts |
| **Reflections feature** | `lib/features/reflection/` | Reflection entry, journaling, and templates |
| **Check-in feature** | `lib/features/check_in/` | Daily check-in flow and domain signal collection |
| **Insights** | `lib/shared/insight/` | Pattern detection, reflection summaries, personal trend analysis |
| **Journey** | `ROADMAP.md` | Longitudinal personal growth history layer |
| **Goal engine** | `lib/shared/goal/`, `lib/features/progress/` | `GoalProgressSnapshot`, `GoalStore`, domain-specific progress tracking |
| **Timeline engine** | `lib/shared/timeline/` | Reflection, practice, and insight timeline sources — domain-specific by nature |
| **Knowledge graph** | `lib/shared/graph/`, `lib/features/graph/` | Personal knowledge graph with `GraphNode`, `GraphEdge`, `GraphStore`, knowledge graph visualization |
| **Domain health engine** | `lib/shared/health/` | `DomainHealthEngine`, `DomainSignalSource`, per-domain health scoring |
| **Conversation feature** | `lib/features/conversation/` | AI conversation UI wired to Ego Hygiene ontology and check-in context |
| **Human development philosophy** | `MANIFESTO.md`, `PILLARS.md`, `PRINCIPLES.md`, `PURPOSE.md` | Philosophical foundation unique to Ego Hygiene |

---

## Proposed Package Structure

The extracted foundation should live in a separate repository: `flutter-foundation`.

Packages should follow a flat, single-responsibility organization.

```
flutter-foundation/
├── packages/
│   ├── foundation_core/           # Lifecycle, environment, feature flags, startup orchestration
│   ├── foundation_auth/           # Authentication abstractions and demo provider
│   ├── foundation_storage/        # StorageService, SecureStorageService, Repository<T,ID>
│   ├── foundation_settings/       # Settings engine with typed preferences
│   ├── foundation_routing/        # GoRouter-based navigation utilities and guards
│   ├── foundation_theme/          # Design token system (colors, spacing, typography, motion)
│   ├── foundation_localization/   # Slang-based i18n infrastructure
│   ├── foundation_notifications/  # Notification abstractions and lifecycle
│   ├── foundation_analytics/      # Analytics abstractions, consent, noop provider
│   ├── foundation_ai/             # AI provider abstractions, registry, demo provider
│   ├── foundation_context/        # Context assembly engine for AI pipelines
│   ├── foundation_memory/         # Memory engine abstractions and in-memory default
│   ├── foundation_sync/           # Sync engine, queue, status tracking
│   ├── foundation_conflict/       # Conflict resolution abstractions and strategies
│   ├── foundation_privacy/        # Privacy engine, consent tracking, data minimization
│   ├── foundation_portability/    # Data export and import abstractions
│   ├── foundation_connectivity/   # Network state detection
│   ├── foundation_performance/    # Performance monitoring abstractions
│   └── foundation_widgets/        # General-purpose reusable UI primitives
├── apps/
│   └── foundation_demo/           # Reference app demonstrating all packages
└── docs/                          # Foundation-specific documentation
```

Ego Hygiene would then declare these as dependencies:

```yaml
# apps/egohygiene/pubspec.yaml
dependencies:
  foundation_core:
    git:
      url: https://github.com/egohygiene/flutter-foundation
      path: packages/foundation_core
  foundation_auth:
    git: ...
  # etc.
```

---

## Dependency Direction

Dependencies must flow in one direction only.

```
Ego Hygiene Application
        │
        ▼
 Flutter Foundation packages
        │
        ▼
  Flutter SDK / pub.dev packages
```

**Rules:**

1. Foundation packages must never import from Ego Hygiene application code.
2. Foundation packages may depend on other foundation packages only when the dependency is genuinely necessary — prefer standalone packages.
3. Application features may depend on multiple foundation packages.
4. Foundation packages must not contain domain knowledge (no references to reflections, check-ins, practices, etc.).
5. Abstract interfaces in foundation packages must not be coupled to any specific backend (no Firebase, Supabase, or Drift imports in abstractions).

**Recommended dependency graph between foundation packages:**

```
foundation_core  ◄── foundation_auth
                 ◄── foundation_routing
                 ◄── foundation_settings ◄── foundation_storage
                 ◄── foundation_notifications
                 ◄── foundation_analytics
foundation_ai    ◄── foundation_context ◄── foundation_memory
foundation_theme ◄── foundation_widgets
```

---

## Naming Conventions

| Category | Convention | Examples |
|---|---|---|
| Repository | `flutter-foundation` | `github.com/egohygiene/flutter-foundation` |
| Package name | `foundation_<domain>` | `foundation_core`, `foundation_auth`, `foundation_storage` |
| Dart class prefix | None required | `AuthenticationProvider`, `StorageService`, `SyncManager` |
| Abstract interfaces | Interface name matches concept | `AIProvider`, `NotificationService`, `AnalyticsProvider` |
| Default/noop implementations | `Noop` or `Demo` prefix | `NoopAnalyticsProvider`, `DemoAIProvider`, `DemoAuthenticationProvider` |
| In-memory implementations | `InMemory` prefix | `InMemoryMemoryStore`, `InMemorySyncQueue` |
| Barrel exports | `<package_name>.dart` | `foundation_auth.dart`, `foundation_storage.dart` |

---

## Extraction Phases

### Phase 0 — Stabilize Before Extracting

**Goal:** Ensure the application is stable and well-tested before extraction begins.

**Prerequisite conditions:**
- Persistent storage layer is implemented (Drift-backed repositories replace in-memory defaults).
- Authentication lifecycle supports real providers (not hardcoded demo mode).
- Context assembly engine is wired into the AI pipeline.
- No critical audit findings remain unresolved (see [AUDIT.md](../AUDIT.md)).
- Core features (reflection, check-in, practices) are functional end-to-end.
- Test coverage meets the established threshold.

**No extraction should begin while Phase 0 conditions are unmet.**

---

### Phase 1 — Extract Stateless Utilities

**Goal:** Extract packages that have no internal state and no cross-package dependencies.

**Packages:**
- `foundation_theme`
- `foundation_localization`
- `foundation_widgets`
- `foundation_connectivity`
- `foundation_performance`

**Acceptance criteria:**
- Packages compile and pass their tests independently.
- Ego Hygiene references packages as git/path dependencies without behavioral change.
- No Ego Hygiene-specific code leaks into extracted packages.

---

### Phase 2 — Extract Infrastructure Abstractions

**Goal:** Extract packages that define abstract interfaces without implementations.

**Packages:**
- `foundation_storage` (abstractions only: `StorageService`, `Repository<T,ID>`)
- `foundation_auth` (abstractions only: `AuthenticationProvider`, `AuthenticationSession`)
- `foundation_notifications` (abstractions only: `NotificationService`)
- `foundation_analytics` (abstractions only: `AnalyticsProvider`, `AnalyticsManager`)

**Acceptance criteria:**
- All abstractions are implementation-free.
- Demo and noop implementations move alongside their abstractions.
- Ego Hygiene continues using injected providers without behavioral change.

---

### Phase 3 — Extract Application Engines

**Goal:** Extract stateful engines that use abstract stores.

**Packages:**
- `foundation_memory` (`MemoryEngine`, `MemoryManager`, `InMemoryMemoryStore`)
- `foundation_sync` (`SyncEngine`, `SyncManager`, `SyncQueue`, `InMemorySyncQueue`)
- `foundation_conflict` (`ConflictResolver`, `InMemoryConflictStore`)
- `foundation_settings` (`SettingsEngine`, preference store)
- `foundation_privacy` (`PrivacyEngine`, consent tracking)
- `foundation_portability` (export and import abstractions)

**Acceptance criteria:**
- Engines work with injected stores.
- In-memory defaults are provided for testing and demo use.
- No domain-specific types (domains, practices, reflections) are imported.

---

### Phase 4 — Extract AI and Context Infrastructure

**Goal:** Extract the AI pipeline infrastructure without Ego Hygiene content.

**Packages:**
- `foundation_ai` (`AIProvider`, `AIConversation`, `AIMessage`, `DemoAIProvider`, `AIProviderRegistry`)
- `foundation_context` (`ContextManager`, `ContextSource`)

**Acceptance criteria:**
- `ContextSource` is a generic interface accepting any string-keyed data.
- No check-in, reflection, or practice types are referenced in extracted packages.
- Ego Hygiene registers its own `ContextSource` implementations that are NOT extracted.

---

### Phase 5 — Extract Core Lifecycle

**Goal:** Extract the startup, routing, and environment infrastructure.

**Packages:**
- `foundation_core` (startup orchestration, environment, feature flags, `AppEnvironment`)
- `foundation_routing` (GoRouter utilities, authentication guards, redirect logic)

**Acceptance criteria:**
- Route guards are configurable via callbacks (not hardcoded to Ego Hygiene routes).
- Feature flag engine is generic (no Ego Hygiene-specific flags baked in).
- Startup lifecycle is extensible via registered initializers.

---

### Phase 6 — Publish Foundation Demo App

**Goal:** Validate the extracted foundation by building a reference demo application.

**Deliverables:**
- `apps/foundation_demo/` demonstrating all extracted packages working together.
- Documentation covering how to start a new project using the foundation.
- README and setup guide for the `flutter-foundation` repository.

---

## Migration Risks

| Risk | Severity | Mitigation |
|---|---|---|
| **Extracting before stabilization** | High | Complete Phase 0 before any code moves. No extraction until persistence, auth, and context assembly are production-ready. |
| **Circular dependencies** | High | Enforce one-way dependency direction from the start. Use `dependency_validator` or similar tooling. |
| **Domain leakage into foundation** | High | All foundation packages must pass a "zero domain knowledge" review before extraction is considered complete. |
| **Breaking changes during extraction** | Medium | Use path-based local dependencies during extraction so the application continues building throughout. Switch to git/pub dependencies only after stabilization. |
| **In-memory defaults shipping to production** | Medium | Add runtime assertion in production environment that rejects in-memory stores. |
| **Version drift between packages** | Medium | Keep all foundation packages at the same version during initial development. Consider a monorepo with unified versioning (Melos). |
| **Missing test coverage on extracted code** | Medium | Each extracted package must include its own unit tests. Minimum coverage thresholds apply before extraction is considered complete. |
| **Loss of design context** | Low | Document package-level README files alongside each extraction. |

---

## Extraction Readiness Criteria

A system is ready to extract when all of the following are true:

1. **No domain knowledge** — The system contains no references to Ego Hygiene-specific concepts (domains, practices, reflections, rituals, journaling, etc.).
2. **Abstraction-backed** — The system depends on abstract interfaces, not concrete implementations. Implementations are injected.
3. **Self-contained** — The system can be compiled and tested independently of the Ego Hygiene application.
4. **Test coverage** — The system has meaningful unit test coverage that travels with it.
5. **Documented** — The system has a package-level README explaining its purpose, API, and extension points.
6. **No hardcoded configuration** — No Ego Hygiene environment variables, route names, or feature flags are embedded in the system.
7. **Demo or noop implementation exists** — A default implementation ships alongside the abstraction so new consumers can get started without implementing their own immediately.

---

## Relationship to Existing Documentation

| Document | Relationship |
|---|---|
| [overview.md](./overview.md) | Defines the 80/20 principle this plan operationalizes |
| [flutter-foundation.md](./flutter-foundation.md) | Describes the technology stack of the foundation being extracted |
| [storage.md](./storage.md) | Details the storage architecture targeted in Phase 2–3 |
| [ai.md](./ai.md) | Details the AI pipeline targeted in Phase 4 |
| [startup.md](./startup.md) | Details the lifecycle infrastructure targeted in Phase 5 |
| [testing.md](./testing.md) | Defines testing standards that extracted packages must meet |
| [AUDIT.md](../AUDIT.md) | Identifies Phase 0 blockers that must be resolved first |
| [ROADMAP.md](../../ROADMAP.md) | Places extraction in the post-Version-1 milestone sequence |
