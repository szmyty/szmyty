# Testing

Ego Hygiene uses a layered testing strategy so tests stay fast, deterministic, and easy to extend. See also `docs/testing.md` for commands and integration test conventions.

## Test layers

| Layer | Location | Purpose |
|---|---|---|
| **Unit** | `apps/egohygiene/test/**` | Domain logic, repositories, providers, utilities |
| **Widget** | `apps/egohygiene/test/**` | UI rendering and interactions with provider overrides |
| **Golden** | `apps/egohygiene/test/golden/` | Visual regression coverage for design-system components across all theme variants |
| **Integration** | `apps/egohygiene/integration_test/` | End-to-end user flows in a real app runtime |
| **Smoke** | `apps/egohygiene/test/widget_test.dart` | Fast app-launch and core-shell confidence checks |

## Conventions

- Mirror `apps/egohygiene/lib/` structure under `apps/egohygiene/test/` when possible.
- Share fakes and helpers from `apps/egohygiene/test/helpers/` instead of redefining them per file.
- Use `ProviderContainer` and provider overrides for deterministic state in unit tests.
- Avoid network and filesystem access in unit and widget tests.
- Inject clocks and time where needed to avoid flaky tests.
- Mock dependencies using [Mocktail](https://pub.dev/packages/mocktail).
- Golden reference images live in `apps/egohygiene/test/goldens/` and are updated with `flutter test --update-goldens`.
- Wrap `MaterialApp` with `TranslationProvider` in widget tests that render screens using `context.t`.

## Shared test helpers

| Helper | Purpose |
|---|---|
| `apps/egohygiene/test/helpers/fake_storage_service.dart` | In-memory `StorageService` fake for provider and repository tests |
| `apps/egohygiene/integration_test/helpers/integration_test_helpers.dart` | Shared fakes and `pumpApp` helper for integration tests |

## Running tests

```bash
cd apps/egohygiene

# Install dependencies and generate code
fvm flutter pub get
fvm dart run build_runner build --delete-conflicting-outputs
fvm dart run slang

# Analyse and test (mirrors CI)
fvm flutter analyze
fvm flutter test --coverage
```

Or use the Taskfile shortcut:

```bash
task test
```

Coverage output is written to `apps/egohygiene/coverage/lcov.info` and uploaded as the `coverage-lcov` artifact in CI.

## Golden tests

Golden tests provide visual regression protection for high-value UI components across all theme variants (light, dark, AMOLED, high-contrast).

Reference images are committed to `apps/egohygiene/test/goldens/`. To regenerate after an intentional visual change:

```bash
task test:golden:update
```

See `docs/testing.md` for full golden workflow documentation.

## Integration tests

Integration tests require a connected device or running emulator:

```bash
cd apps/egohygiene

# Run a specific flow test
fvm flutter test integration_test/app_smoke_test.dart -d <device-id>
fvm flutter test integration_test/first_launch_test.dart -d <device-id>
fvm flutter test integration_test/onboarding_test.dart -d <device-id>
fvm flutter test integration_test/navigation_test.dart -d <device-id>
fvm flutter test integration_test/reflection_flow_test.dart -d <device-id>
fvm flutter test integration_test/conversation_test.dart -d <device-id>
fvm flutter test integration_test/settings_test.dart -d <device-id>
fvm flutter test integration_test/restart_persistence_test.dart -d <device-id>

# Run all integration tests
fvm flutter test integration_test/ -d <device-id>
```

See `docs/testing.md` for the full list of integration test files and helper utilities.

## CI integration

The GitHub Actions workflow in `.github/workflows/build.yml` runs the full test suite after code generation and static analysis. An optional `COVERAGE_THRESHOLD` variable can enforce a minimum coverage percentage.
