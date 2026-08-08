# Testing Strategy

## Metadata

- **Spec ID:** `testing-strategy`
- **File Name:** `testing-strategy.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #9
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-21

---

# 1. Purpose

Define the testing philosophy and implementation requirements for Ego Hygiene.

This specification establishes how the application is tested, what must be tested at each layer, which tools are used, and how testing integrates with the CI pipeline. It ensures that code changes can be made with confidence and that regressions are caught before they reach users.

---

# 2. Goals

- Define the canonical testing layers and what each covers.
- Establish tooling and package selection for each layer.
- Define test organization and file naming conventions.
- Define mocking and dependency injection conventions.
- Establish minimum coverage expectations.
- Integrate testing into the CI pipeline.

---

# 3. Non-Goals

- This spec does not define QA processes or manual testing procedures.
- This spec does not define performance benchmarking.
- This spec does not define accessibility auditing tooling (covered separately).
- This spec does not define end-to-end testing with external services.

---

# 4. Context

The repository already has a `test/` directory and uses:
- `flutter_test` — widget and unit testing
- `mocktail` — mocking
- `golden_toolkit` — golden tests

From `ARCHITECTURE.md`:

> "Unit Tests — Test business logic in isolation, mock dependencies using Mocktail."
> "Widget Tests — Test UI components and interactions."
> "Integration Tests — Test complete user flows."

The `flutter-engineer.spec.md` adds:
- `integration_test` — integration test package
- `patrol` — future end-to-end testing

This spec builds on those foundations with explicit conventions and expectations.

---

# 5. Requirements

## 5.1 Functional Requirements

- All domain models must have unit tests for serialization and deserialization.
- All repository implementations must have unit tests for CRUD operations.
- All Riverpod providers must have unit tests using `ProviderContainer`.
- All shared widgets must have widget tests.
- All screens must have widget tests for their primary rendering states.
- Critical user flows must have integration tests.
- Key UI components must have golden tests for light and dark mode.
- Test utilities must be shared via `test/helpers/` to avoid duplication.

## 5.2 Non-Functional Requirements

- Tests must be fast. Unit tests must not access the network or filesystem.
- Mocks must use `mocktail` and never use `mockito`.
- Tests must be deterministic and not depend on system time without explicit time injection.
- Golden image files must be committed to the repository.
- Tests must be runnable locally with a single command.
- CI must run the full test suite on every pull request.

---

# 6. Architecture

## 6.1 Testing Layers

### Layer 1 — Unit Tests

**Scope:** Pure Dart logic with no Flutter dependency.

**Covers:**
- Domain models (serialization, equality, value objects)
- Repository implementations (logic, not DB itself)
- Provider state transitions
- Utility functions
- Mappers (domain ↔ DAO)

**Tools:**
- `flutter_test` (test runner)
- `mocktail` (mocking)

**Location:** `test/` mirroring `lib/` structure.

---

### Layer 2 — Widget Tests

**Scope:** Flutter UI in isolation (no network, no database).

**Covers:**
- Shared widgets (`lib/shared/widgets/`)
- Feature screens (loading, data, empty, error states)
- Provider-wired widget behavior

**Tools:**
- `flutter_test`
- `mocktail` (mock providers and services)
- `golden_toolkit` (visual regression)

**Location:** `test/` mirroring `lib/` structure.

---

### Layer 3 — Golden Tests

**Scope:** Visual regression testing.

**Covers:**
- Design system components in light and dark mode
- Key screens in standard states

**Tools:**
- `golden_toolkit`

**Location:** `test/golden/` with reference images in `test/goldens/`.

---

### Layer 4 — Integration Tests

**Scope:** Complete user flows in a real application environment.

**Covers:**
- Core navigation flows
- Practice completion lifecycle
- Insight creation lifecycle

**Tools:**
- `integration_test`

**Location:** `integration_test/`

---

## 6.2 Test Directory Structure

```
test/
  helpers/
    mock_providers.dart       — shared mock provider overrides
    test_utils.dart           — common test utilities
    fake_storage_service.dart — in-memory StorageService fake
    fake_database.dart        — in-memory Drift database
  features/
    domains/
      domain_test.dart
      domain_repository_test.dart
      domains_provider_test.dart
      domain_list_screen_test.dart
    practices/
      practice_test.dart
      practice_repository_test.dart
      practices_provider_test.dart
    insights/
      insight_test.dart
      insight_repository_test.dart
      insights_provider_test.dart
  shared/
    widgets/
      app_button_test.dart
      app_card_test.dart
      app_text_field_test.dart
    services/
      storage_service_test.dart
      secure_storage_service_test.dart
  golden/
    app_button_golden_test.dart
    app_card_golden_test.dart
  goldens/
    app_button_light.png
    app_button_dark.png

integration_test/
  app_test.dart
  navigation_test.dart
  practice_completion_test.dart
```

## 6.3 Mock and Fake Strategy

| Dependency | Testing approach |
|---|---|
| `StorageService` | Fake in-memory implementation |
| `SecureStorageService` | Fake in-memory implementation |
| `NotificationService` | Mock via `mocktail` |
| `AIProvider` | Mock via `mocktail` |
| Drift database | In-memory SQLite (`NativeDatabase.memory()`) |
| Riverpod providers | `ProviderContainer` with overrides |

## 6.4 Provider Testing Pattern

```dart
test('domainsProvider returns seeded domains', () async {
  final container = ProviderContainer(
    overrides: [
      domainRepositoryProvider.overrideWith(
        (_) => FakeDomainRepository(),
      ),
    ],
  );
  addTearDown(container.dispose);

  final domains = await container.read(domainsProvider.future);
  expect(domains, isNotEmpty);
});
```

## 6.5 Golden Test Pattern

```dart
testGoldens('AppButton renders correctly in light mode', (tester) async {
  await loadAppFonts();
  await tester.pumpWidgetBuilder(
    const AppButton(label: 'Confirm', onPressed: null),
    wrapper: materialAppWrapper(theme: AppTheme.light()),
  );
  await screenMatchesGolden(tester, 'app_button_light');
});
```

## 6.6 Dependencies

Required:
- `flutter_test` (Flutter SDK)
- `mocktail`
- `golden_toolkit`

Recommended:
- `integration_test` (Flutter SDK)

Future:
- `patrol` — advanced integration/E2E testing

---

# 7. Implementation Plan

## Phase 1 — Test Infrastructure

- [ ] Create `test/helpers/mock_providers.dart` with shared provider overrides.
- [ ] Create `test/helpers/test_utils.dart` with common test utilities.
- [ ] Create `test/helpers/fake_storage_service.dart`.
- [ ] Create `test/helpers/fake_database.dart` using `NativeDatabase.memory()`.
- [ ] Configure `golden_toolkit` in `flutter_test_config.dart`.

## Phase 2 — Domain and Model Tests

- [ ] Write unit tests for `Domain` model.
- [ ] Write unit tests for `Practice` model.
- [ ] Write unit tests for `PracticeCompletion` model.
- [ ] Write unit tests for `Insight` model.
- [ ] Write unit tests for domain-to-DAO mappers.

## Phase 3 — Repository Tests

- [ ] Write unit tests for `DomainRepositoryImpl`.
- [ ] Write unit tests for `PracticeRepositoryImpl`.
- [ ] Write unit tests for `PracticeCompletionRepositoryImpl`.
- [ ] Write unit tests for `InsightRepositoryImpl`.

## Phase 4 — Provider Tests

- [ ] Write unit tests for `domainsProvider`.
- [ ] Write unit tests for `practicesProvider`.
- [ ] Write unit tests for `insightsProvider`.

## Phase 5 — Widget Tests

- [ ] Write widget tests for `AppButton`, `AppCard`, `AppTextField`.
- [ ] Write widget tests for `DomainListScreen`.
- [ ] Write widget tests for `PracticeListScreen`.
- [ ] Write widget tests for `InsightListScreen`.

## Phase 6 — Golden Tests

- [ ] Write golden tests for `AppButton` (light + dark).
- [ ] Write golden tests for `AppCard` (light + dark).
- [ ] Commit golden reference images.

## Phase 7 — Integration Tests

- [ ] Write `app_test.dart` — smoke test confirming app launches.
- [ ] Write `navigation_test.dart` — verify tab switching.
- [ ] Write `practice_completion_test.dart` — complete a practice and verify storage.

---

# 8. Validation Plan

- All unit tests must pass locally and in CI.
- Widget tests must pass without network access.
- Golden tests must be regenerated and committed when design changes.
- Integration tests must pass on Android and/or iOS in CI.
- Test failures block pull request merges.

---

# 9. Acceptance Criteria

- [ ] Test infrastructure helpers are in place.
- [ ] Unit tests exist for all domain models.
- [ ] Unit tests exist for all repository implementations.
- [ ] Unit tests exist for all Riverpod providers.
- [ ] Widget tests exist for all shared widgets.
- [ ] Widget tests exist for all feature screens (primary states).
- [ ] Golden tests exist for key design system components.
- [ ] Integration tests exist for core user flows.
- [ ] `flutter test` passes locally and in CI with no failures.

---

# 10. Open Questions

- What is the minimum acceptable test coverage percentage?
- Should golden tests be committed per platform (Android, iOS, Web) or single-platform?
- Should `patrol` be adopted for integration tests from the beginning or deferred?
- How should flaky integration tests be handled in CI?
- Should test helpers be extracted into a separate Dart package for reuse?
