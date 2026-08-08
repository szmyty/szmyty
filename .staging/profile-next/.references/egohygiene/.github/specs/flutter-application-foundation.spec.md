# Flutter Application Foundation

## Metadata

- **Spec ID:** `flutter-application-foundation`
- **File Name:** `flutter-application-foundation.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #9
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-21

---

# 1. Purpose

Define the canonical Flutter application architecture for Ego Hygiene.

This specification establishes the structural foundation that all feature development builds upon. It covers the application shell, initialization, dependency wiring, shared infrastructure, and the layered architecture model that governs how all features are organized.

---

# 2. Goals

- Define the canonical feature-first directory structure.
- Define the application initialization sequence.
- Define the shared infrastructure layer and its responsibilities.
- Establish service abstraction boundaries.
- Define provider scoping and lifetime conventions.
- Ensure the foundation supports offline-first, cross-platform, and AI-capable development from day one.

---

# 3. Non-Goals

- This spec does not define individual feature implementations.
- This spec does not define routing in detail (see `routing-navigation.spec.md`).
- This spec does not define the design system in detail (see `design-system.spec.md`).
- This spec does not define storage schema in detail (see `offline-first-storage.spec.md`).
- This spec does not define the testing strategy in detail (see `testing-strategy.spec.md`).

---

# 4. Context

The repository already contains a Flutter application foundation in `lib/` with:

- Feature-first directory structure (`lib/features/`)
- Shared infrastructure (`lib/shared/`)
- Riverpod state management with code generation
- GoRouter navigation
- Drift for local storage
- Design tokens in `lib/shared/theme/`
- Service abstractions in `lib/shared/services/`
- Localization via slang

This spec formalizes that foundation, identifies gaps, and defines the authoritative conventions for ongoing development. It references `flutter-engineer.spec.md` as the technology standard and builds the application-specific architecture on top of it.

---

# 5. Requirements

## 5.1 Functional Requirements

- The application must initialize all required services before rendering the UI.
- The application must support light mode and dark mode from launch.
- The application must support localization from launch.
- The application must support offline usage from launch.
- The application must provide a consistent error boundary.
- The application must expose all shared services through provider abstractions.
- All features must follow the canonical feature directory structure.
- All external dependencies must be accessed through service abstractions.

## 5.2 Non-Functional Requirements

- The application shell must remain clean and minimal.
- Provider scoping must prevent unnecessary rebuilds.
- Service abstractions must be mockable for testing.
- Initialization errors must be handled gracefully and visibly.
- The build system must remain deterministic.
- The architecture must support adding new features without modifying the shell.

---

# 6. Architecture

## 6.1 Canonical Directory Structure

```
lib/
  main.dart                    — entry point
  app.dart                     — root widget (MaterialApp.router)
  features/
    home/                      — example feature
      presentation/
        home_screen.dart
        widgets/
      providers/
        home_provider.dart
        home_provider.g.dart
      domain/
        home_state.dart
        home_state.freezed.dart
      data/
        home_repository.dart
    domains/                   — domain feature
    practices/                 — practices feature
    insights/                  — insights feature
    reflection/                — reflection feature (future)
    settings/                  — settings feature
  shared/
    theme/
      colors.dart
      spacing.dart
      typography.dart
      app_theme.dart
    routing/
      app_router.dart
      app_router.g.dart
      routes.dart
    localization/
      app_en.i18n.json
      strings.g.dart
    services/
      storage_service.dart
      secure_storage_service.dart
      notification_service.dart
      ai_provider.dart
      impl/
        shared_preferences_storage_service.dart
        flutter_secure_storage_service.dart
        local_notification_service.dart
    providers/
      app_providers.dart
      app_providers.g.dart
    models/
      (shared domain models)
    widgets/
      (shared reusable UI components)
```

## 6.2 Application Initialization Sequence

```
main()
  ↓
WidgetsFlutterBinding.ensureInitialized()
  ↓
Initialize shared services
  (StorageService, SecureStorageService, NotificationService)
  ↓
ProviderScope (root Riverpod container)
  ↓
App widget
  ↓
MaterialApp.router (GoRouter)
  ↓
Feature screens
```

## 6.3 Feature Layer Architecture

Each feature follows a four-layer structure:

```
presentation/   — widgets, screens, UI logic
providers/      — Riverpod providers, state management
domain/         — business logic, entities, use cases
data/           — repositories, data sources
```

**Rules:**

- `presentation` depends on `providers`.
- `providers` depends on `domain`.
- `domain` has no Flutter dependencies.
- `data` implements interfaces defined in `domain`.
- Features must not import from other features directly.
- Cross-feature communication occurs through `shared/` providers or events.

## 6.4 Service Abstraction Layer

All external dependencies are wrapped behind interfaces in `lib/shared/services/`:

```
StorageService          — key-value storage (SharedPreferences impl)
SecureStorageService    — secrets (FlutterSecureStorage impl)
NotificationService     — local notifications (flutter_local_notifications impl)
AIProvider              — AI capabilities (abstracted, provider-agnostic)
  ChatProvider
  InsightProvider
  SummarizationProvider
  EmbeddingProvider
```

Implementations live in `lib/shared/services/impl/` and are injected via Riverpod providers.

## 6.5 Provider Conventions

- Use `@riverpod` annotation with code generation for all providers.
- Use `Ref` for dependency injection between providers.
- Prefer `AsyncNotifierProvider` for async state.
- Prefer `NotifierProvider` for synchronous mutable state.
- Use `Provider` for derived/computed values.
- Providers that wrap services must accept the service as a dependency.

## 6.6 Error Handling

- Wrap the root widget in an `ErrorBoundary` that catches and displays unhandled errors.
- Service initialization failures must display a user-visible error screen.
- Provider errors must be handled using `AsyncValue` error states.
- Never swallow exceptions silently.

## 6.7 Dependencies

- `flutter_riverpod` + `riverpod_annotation` + `riverpod_generator`
- `go_router`
- `drift` + `sqlite3_flutter_libs`
- `shared_preferences`
- `flutter_secure_storage`
- `flutter_local_notifications`
- `flex_color_scheme` + `google_fonts`
- `slang` + `intl` + `flutter_localizations`
- `freezed` + `json_serializable`
- `build_runner`

---

# 7. Implementation Plan

## Phase 1 — Verify and Formalize Foundation

- [ ] Confirm `lib/` directory structure matches the canonical structure defined above.
- [ ] Confirm all service abstractions exist and are wired into providers.
- [ ] Confirm `main.dart` initialization sequence is correct.
- [ ] Document any gaps between current state and canonical structure.

## Phase 2 — Strengthen Shared Infrastructure

- [ ] Ensure `StorageService`, `SecureStorageService`, and `NotificationService` interfaces are complete.
- [ ] Ensure all service implementations are injected via Riverpod.
- [ ] Validate `AIProvider` abstraction is in place even if not yet connected to a backend.
- [ ] Add a root error boundary widget.

## Phase 3 — Feature Scaffolding

- [ ] Scaffold `domains` feature directory.
- [ ] Scaffold `practices` feature directory.
- [ ] Scaffold `insights` feature directory.
- [ ] Scaffold `settings` feature directory.
- [ ] Confirm `home` feature follows canonical structure.

## Phase 4 — Validation

- [ ] Run `flutter analyze` with zero errors.
- [ ] Run `flutter pub run build_runner build` with no conflicts.
- [ ] Run `flutter test` with all tests passing.
- [ ] Manually verify hot reload works correctly.
- [ ] Manually verify light and dark mode on at least one platform.

---

# 8. Validation Plan

- Static analysis (`flutter analyze`) must pass with zero errors.
- Code generation (`build_runner`) must complete without conflicts.
- Unit tests for service implementations.
- Widget tests for `App` root widget rendering.
- Integration smoke test confirming the app launches and navigates.
- CI pipeline must execute all validation steps.

---

# 9. Acceptance Criteria

- [ ] Application initializes all services before rendering UI.
- [ ] All features follow the canonical four-layer structure.
- [ ] No feature imports directly from another feature.
- [ ] All external dependencies are accessed through service abstractions.
- [ ] Light and dark mode work from launch.
- [ ] Localization is active from launch.
- [ ] Application functions offline.
- [ ] `flutter analyze` passes with zero errors.
- [ ] All tests pass.
- [ ] CI pipeline is green.

---

# 10. Open Questions

- Should the application support a splash screen or loading state during initialization?
- How should initialization failures be communicated to the user — full-screen error or partial degradation?
- Should features communicate through a shared event bus, or only through shared providers?
- When should the `AIProvider` be eagerly initialized versus lazily instantiated?
