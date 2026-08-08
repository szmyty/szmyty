# Testing Foundation

Ego Hygiene uses a layered testing strategy so tests stay fast, deterministic, and easy to extend.

## Test layers

- **Unit tests** (`apps/egohygiene/test/**`): domain logic, repositories, providers, utilities.
- **Widget tests** (`apps/egohygiene/test/**`): UI rendering and interactions with provider overrides.
- **Golden tests** (`apps/egohygiene/test/golden/`): visual regression tests for high-value UI components.
- **Integration tests** (`apps/egohygiene/integration_test/`): end-to-end user flows in a real app runtime.
- **Smoke tests** (`apps/egohygiene/test/widget_test.dart`): fast app-launch and core-shell confidence checks.

## Repository conventions

- Mirror `apps/egohygiene/lib/` structure under `apps/egohygiene/test/` when possible.
- Share fakes/helpers from `apps/egohygiene/test/helpers/` instead of redefining them in each test file.
- Use `ProviderContainer` and provider overrides for deterministic state.
- Avoid network/filesystem access in unit and widget tests.
- Inject clocks/time where needed to avoid flaky tests.
- Wrap `MaterialApp` with `TranslationProvider` in widget tests that render screens using `context.t`.

## Shared helpers

- `apps/egohygiene/test/helpers/fake_storage_service.dart` — in-memory `StorageService` fake for provider and repository tests.
- `apps/egohygiene/integration_test/helpers/integration_test_helpers.dart` — fakes and `pumpApp` helper for integration tests.

## Commands

Run the same sequence used by CI:

```bash
cd apps/egohygiene
fvm flutter pub get
fvm dart run build_runner build --delete-conflicting-outputs
fvm dart run slang
fvm dart format --output=none --set-exit-if-changed lib test integration_test
fvm flutter analyze
fvm flutter test --coverage
```

Using the Taskfile (recommended):

```bash
task ci:local
```

This runs pub-get, code generation, formatting check, static analysis, and tests with coverage in one command — identical to what CI validates.

## Golden tests

Golden tests provide visual regression protection for high-value UI components and themes.

### Covered components

| Component | Themes covered |
|---|---|
| `AppCard` | light, dark, AMOLED, high-contrast, tappable variant |
| `AppLoadingIndicator` | light, dark, AMOLED, high-contrast, inline variant |
| `AppErrorState` | light, dark, AMOLED, high-contrast, with-action variant |
| `AppEmptyState` | light, dark, AMOLED, high-contrast, with-action variant |

### Golden image location

Reference images live in `apps/egohygiene/test/goldens/` and are tracked in version control.

### Running golden tests

```bash
task test:golden
```

Or directly:

```bash
cd apps/egohygiene
fvm flutter test test/golden/
```

### Updating golden images

Run this command **only after an intentional visual change** has been reviewed and approved:

```bash
task test:golden:update
```

Or directly:

```bash
cd apps/egohygiene
fvm flutter test test/golden/ --update-goldens
```

After updating, commit the changed PNG files together with the code change that caused them.

### When to regenerate goldens

Regenerate goldens when:
- A shared widget's appearance has intentionally changed (e.g., spacing, color, typography).
- A new theme token is introduced and applied to covered components.
- The design system is intentionally updated.

Do **not** regenerate goldens to silence a failing test without reviewing whether the visual change is intentional.

### CI expectations

Golden tests run as part of the standard `flutter test` suite (included in `task ci:local` and the CI `test` job). A failing golden means the rendered output no longer matches the reference image — review the diff before regenerating.

### Reviewing golden diffs

When a golden test fails in CI:
1. Download the `coverage-lcov` or test artifact from the GitHub Actions run.
2. Compare the failing `*_failure.png` against the reference in `test/goldens/`.
3. If the visual change is intentional, run `task test:golden:update` locally and commit the updated images.
4. If the change is a regression, fix the root cause instead of regenerating.

## Formatting

### Checking formatting (CI and `task ci:local`)

CI and `task ci:local` use a **non-mutating** format check. The command reports any files that would change and exits with a non-zero code if formatting is required, without modifying source files:

```bash
# Using the Taskfile (mirrors CI exactly)
task dart:format:check

# Or directly with fvm
fvm dart format --output=none --set-exit-if-changed lib test integration_test
```

### Applying formatting

To apply formatting locally (rewrites files in-place), run:

```bash
task dart:format
```

This is intentionally separate from `task ci:local` to avoid accidentally reformatting files in CI or in contexts where only a check is needed.

## Coverage

### Collecting coverage

Running `flutter test --coverage` (or `task test:coverage`) produces `coverage/lcov.info`.
Both the pull-request CI workflow (`build.yml`) and the development-build workflow (`development-build.yml`) collect coverage and upload it as the `coverage-lcov` artifact, retained for 7 days.

A line-coverage summary is published directly in the GitHub Actions workflow run UI after each CI execution.

### Coverage threshold enforcement

Coverage enforcement is controlled by the `COVERAGE_THRESHOLD` Actions variable on this repository.

When set (e.g., `COVERAGE_THRESHOLD=60`), CI fails if line coverage drops below that value on both pull-request and development builds.

When the variable is not set, the CI coverage summary reports:

> ⚠️ Coverage threshold is not configured. Set the `COVERAGE_THRESHOLD` Actions variable on this repository to enforce a minimum coverage floor.

**To configure enforcement:**
1. Run `task test:coverage` locally and check the printed line coverage percentage.
2. Choose a threshold at or slightly below the measured baseline.
3. Set `COVERAGE_THRESHOLD` in the repository's **Settings → Secrets and variables → Actions → Variables** tab.

Run integration tests (requires a connected device or running emulator):

```bash
cd apps/egohygiene

# Individual test files
fvm flutter test integration_test/app_smoke_test.dart -d <device-id>
fvm flutter test integration_test/first_launch_test.dart -d <device-id>
fvm flutter test integration_test/onboarding_test.dart -d <device-id>
fvm flutter test integration_test/navigation_test.dart -d <device-id>
fvm flutter test integration_test/reflection_flow_test.dart -d <device-id>
fvm flutter test integration_test/conversation_test.dart -d <device-id>
fvm flutter test integration_test/settings_test.dart -d <device-id>
fvm flutter test integration_test/restart_persistence_test.dart -d <device-id>

# All integration tests at once
fvm flutter test integration_test/ -d <device-id>
```

## Integration tests

Integration tests live in `apps/egohygiene/integration_test/` and exercise the full application
runtime end-to-end.

### Structure

```
apps/egohygiene/integration_test/
  helpers/
    integration_test_helpers.dart       # shared fakes, overrides, pumpApp
  app_smoke_test.dart                   # startup + home screen smoke test
  first_launch_test.dart                # first-launch: onboarding shown to new users
  onboarding_test.dart                  # full onboarding flow (skip / complete)
  navigation_test.dart                  # bottom-nav tab switching (all 5 tabs)
  reflection_flow_test.dart             # reflection creation end-to-end
  conversation_test.dart                # conversation screen + message flow
  settings_test.dart                    # settings navigation + AI settings sub-route
  restart_persistence_test.dart         # onboarding completion persists across restart
```

### Constraints

- Tests must be deterministic — avoid real clocks, network, or file-system access.
- Use `FakeStorageService` from `apps/egohygiene/integration_test/helpers/` to avoid
  platform-specific storage.
- Use the `appDatabaseProvider` override in `pumpApp` (backed by `NativeDatabase.memory()`)
  to keep database operations in-memory and isolated per test.
- Prefer the default `DemoAIProvider` (no `--dart-define` required) so tests
  pass without an external AI backend.
- Each test file calls `IntegrationTestWidgetsFlutterBinding.ensureInitialized()`
  as its very first statement.

### Helper utilities

| Class / Function | Purpose |
|---|---|
| `FakeStorageService` | In-memory `StorageService` — avoids platform storage |
| `CompletedOnboardingManager` | Reports onboarding as completed — default for most tests |
| `RequiredOnboardingManager` | Reports onboarding as required — use for first-launch tests |
| `pumpApp(tester, {overrides})` | Pumps the full app with standard overrides (completed onboarding, in-memory database, zero-delay splash) |
| `pumpAppWithRealOnboarding(tester, {sharedStorage})` | Pumps with the real `OnboardingManager` reading from a shared `FakeStorageService` — use for persistence tests |

### Future expansion

- Authentication flow tests
- Health feature flow tests
- Cross-platform and emulator CI jobs

## Integration test CI pipeline

### CI test subset

The pull-request CI gate runs the following two integration tests on every relevant
Flutter app change:

| File | Coverage |
|---|---|
| `app_smoke_test.dart` | Full startup lifecycle and home screen |
| `navigation_test.dart` | All five bottom-nav tabs |

These files cover the highest-value user flows with the fewest external
dependencies.  Additional tests will be promoted to the blocking gate once their
CI reliability is verified.

### Execution platform

Integration tests run on **Chrome (headless)** inside an `ubuntu-latest`
GitHub Actions runner.

**Rationale:**

- Chrome is pre-installed on `ubuntu-latest` — no emulator provisioning needed.
- Flutter's `integration_test` package supports Chrome directly.
- Headless mode works without a virtual display (`Xvfb`), keeping setup minimal.
- The project already ships `web/sqlite3.wasm` and `web/drift_worker.js`, so the
  `NativeDatabase.memory()` executor used by the test helpers works on the web
  platform without any additional configuration.
- The `startupTransitionProvider` override in `pumpApp()` sets the splash to
  zero duration, bypassing Rive and Lottie animations and keeping each test fast
  and deterministic.

### CI job structure

The `integration-test` job in `.github/workflows/reusable/flutter-ci.yml`:

- Runs after the `analyze` job passes (in parallel with `test`).
- Is gated on `flutter-app` path changes — documentation-only or publishing-only
  changes do not trigger an integration test run.
- Is controlled by the `run-integration-tests` workflow input (default: `true`).
- Uploads `integration-test-logs` as a 7-day artifact when the job fails.

### Local command

Run the same CI subset locally using:

```bash
task test:integration:ci
```

**Prerequisites:**

- Google Chrome must be installed and on `PATH`.
- Run `task setup` first to install Flutter and fetch dependencies.
- Run `task generate` if generated code is not already present.

**Exact tests included:**

```
integration_test/app_smoke_test.dart
integration_test/navigation_test.dart
```

**Full integration suite:**

```bash
task test:integration       # all eight integration-test files on Chrome
```

Or directly:

```bash
cd apps/egohygiene
fvm flutter test integration_test/ --device-id chrome --reporter expanded
```

### Diagnosing common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `Chrome not found` | Chrome not installed | Install `google-chrome-stable` |
| `Unable to connect to Chrome` | Port conflict | Retry or kill stale Chrome processes |
| `pumpAndSettle timed out` | Infinite animation | Verify `startupTransitionProvider` override is applied |
| `Finder found zero widgets` | Route or label changed | Update the assertion to match new UI text/widget |
| Database error on web | Missing `sqlite3.wasm` | Ensure `web/sqlite3.wasm` is present in the project |

### Full-suite strategy

| Trigger | Test set |
|---|---|
| Pull request (flutter-app changes) | `app_smoke_test` + `navigation_test` |
| Push to `main` | Same CI subset (via `development-build.yml`) |
| Scheduled workflow (future) | Complete integration suite |
| Tagged release (future) | Complete integration suite |

The remaining six integration tests (`first_launch_test`, `onboarding_test`,
`reflection_flow_test`, `conversation_test`, `settings_test`,
`restart_persistence_test`) can be added to the blocking gate by appending
their file paths to the `Run Integration Tests` step in
`.github/workflows/reusable/flutter-ci.yml` once their CI reliability is
confirmed.  No new workflow is needed — the `run-integration-tests` input and
the existing `integration_test/` path filter already accommodate expansion.
