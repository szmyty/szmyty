# Build Pipeline

## Metadata

- **Spec ID:** `build-pipeline`
- **File Name:** `build-pipeline.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #9
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-21

---

# 1. Purpose

Define the CI/CD expectations and validation workflows for Ego Hygiene.

This specification establishes what happens when code is pushed, what is validated before merging, how builds are produced, and how artifacts are versioned and distributed. It ensures that the build pipeline is a reliable, deterministic, and observable system.

---

# 2. Goals

- Define the CI pipeline steps and their order.
- Define pull request validation requirements.
- Define artifact generation (APK, web, Linux).
- Define semantic versioning and changelog generation.
- Define build reproducibility requirements.
- Define secrets and environment variable management.

---

# 3. Non-Goals

- This spec does not define app store submission processes.
- This spec does not define infrastructure provisioning.
- This spec does not define monitoring or alerting for production builds.
- This spec does not define release scheduling or release management.

---

# 4. Context

The repository currently has a `.github/workflows/build.yml` that performs:
1. Install Flutter
2. Install dependencies
3. Run code generation
4. Run static analysis
5. Run tests
6. Build Android APK
7. Build Web
8. Upload artifacts

From `flutter-engineer.spec.md`:

> "Applications should support: automated testing, APK generation, web builds, semantic versioning, changelog generation."

From `ARCHITECTURE.md`:

> "Release automation should begin early."

This spec formalizes the build pipeline architecture and identifies gaps to fill as the project matures.

---

# 5. Requirements

## 5.1 Functional Requirements

- Every pull request must trigger the CI pipeline.
- The CI pipeline must run code generation before analysis or testing.
- The CI pipeline must run static analysis (`flutter analyze`) with zero errors.
- The CI pipeline must run the full test suite (`flutter test`).
- The CI pipeline must build an Android APK.
- The CI pipeline must build a web release.
- Build artifacts must be uploaded and accessible after the pipeline completes.
- The pipeline must fail and block merging if any step fails.
- The pipeline must use a pinned Flutter version to ensure reproducibility.

## 5.2 Non-Functional Requirements

- Pipeline execution time must remain under 15 minutes for the full suite.
- Secrets must never be logged or exposed in pipeline output.
- The pipeline must be idempotent — re-running it must produce the same result.
- Flutter and Dart versions must be pinned via FVM (`.fvmrc`).
- Build cache must be used to accelerate repeated runs.
- The pipeline must produce informative error output on failure.

---

# 6. Architecture

## 6.1 Pipeline Stages

```
Stage 1 — Checkout
  actions/checkout

Stage 2 — Setup
  Install FVM
  Install Flutter (via FVM / pinned version)
  flutter pub get
  Cache .pub-cache and build/

Stage 3 — Code Generation
  flutter pub run build_runner build --delete-conflicting-outputs
  flutter pub run slang

Stage 4 — Analysis
  flutter analyze

Stage 5 — Test
  flutter test --coverage
  Upload coverage report (optional: codecov)

Stage 6 — Build
  flutter build apk --release
  flutter build web --release

Stage 7 — Artifacts
  Upload APK artifact
  Upload web artifact
  Upload coverage artifact
```

## 6.2 Trigger Strategy

```
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

All pushes to `main` and all pull requests targeting `main` trigger the pipeline.

## 6.3 Flutter Version Pinning

Flutter version is pinned via `.fvmrc`:

```json
{
  "flutter": "3.x.x"
}
```

The CI pipeline uses the FVM-pinned version. This ensures developer environments and CI use identical Flutter versions.

## 6.4 Workflow File Structure

```
.github/
  workflows/
    build.yml          — primary CI pipeline (test + build)
    release.yml        — release automation (future)
    analysis.yml       — scheduled code quality checks (future)
```

## 6.5 Build Artifacts

| Artifact | Path | Retention |
|---|---|---|
| Android APK | `build/app/outputs/apk/release/app-release.apk` | 30 days |
| Web build | `build/web/` | 30 days |
| Test coverage | `coverage/lcov.info` | 7 days |

## 6.6 Secrets Management

Secrets are stored in GitHub repository settings (`Settings → Secrets and variables → Actions`).

Required secrets (future):
- `GOOGLE_SERVICES_JSON` — Android Firebase config
- `KEYSTORE_FILE` — Android release keystore (base64)
- `KEYSTORE_PASSWORD`
- `KEY_ALIAS`
- `KEY_PASSWORD`

Current builds are debug/development builds; release signing is deferred.

## 6.7 Caching Strategy

```yaml
- name: Cache pub dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.pub-cache
    key: ${{ runner.os }}-pub-${{ hashFiles('pubspec.lock') }}
    restore-keys: |
      ${{ runner.os }}-pub-
```

## 6.8 Task Runner Integration

The pipeline uses `Taskfile.yml` commands where available:

```
task generate   → flutter pub run build_runner build + slang
task analyze    → flutter analyze
task test       → flutter test
task build:web  → flutter build web --release
```

## 6.9 Commit Conventions and Pipeline Gates

The repository uses Conventional Commits enforced via commitlint and a Husky `commit-msg` hook locally.

Future pipeline additions:
- `commitlint` validation step on PRs
- Automated changelog generation via `conventional-changelog`
- Semantic version bumping via `semantic-release`

## 6.10 Dependencies

- GitHub Actions (CI runner)
- `actions/checkout`
- `subosito/flutter-action` or FVM action
- `actions/cache` — dependency caching
- `actions/upload-artifact` — artifact storage
- FVM (`.fvmrc`) — Flutter version management

---

# 7. Implementation Plan

## Phase 1 — Audit and Stabilize Current Pipeline

- [ ] Audit `.github/workflows/build.yml` against the stage definitions in this spec.
- [ ] Verify Flutter version is pinned via FVM and used in CI.
- [ ] Verify dependency caching is configured.
- [ ] Verify code generation runs before analysis and testing.
- [ ] Verify artifacts are uploaded after build.

## Phase 2 — Coverage and Quality Gates

- [ ] Add `--coverage` flag to `flutter test`.
- [ ] Upload coverage report as artifact.
- [ ] Consider integrating Codecov or equivalent.

## Phase 3 — Pipeline Reliability

- [ ] Add explicit `flutter analyze --fatal-infos` gate.
- [ ] Confirm all pipeline steps fail the build on error.
- [ ] Add pipeline timeout to prevent runaway jobs.

## Phase 4 — Release Pipeline (Future)

- [ ] Create `.github/workflows/release.yml`.
- [ ] Define semantic versioning strategy.
- [ ] Implement automated changelog generation.
- [ ] Configure signed Android release builds.

## Phase 5 — Validation

- [ ] Manually trigger the pipeline and verify all stages pass.
- [ ] Verify artifacts are downloadable from GitHub Actions.
- [ ] Verify a failing test correctly blocks the pipeline.
- [ ] Verify a failing `flutter analyze` correctly blocks the pipeline.

---

# 8. Validation Plan

- Manually trigger the pipeline on a test branch.
- Introduce a deliberate test failure and confirm pipeline blocks.
- Introduce a deliberate analysis error and confirm pipeline blocks.
- Download and verify APK artifact.
- Download and verify web artifact.

---

# 9. Acceptance Criteria

- [ ] Pipeline runs on every push to `main` and every pull request.
- [ ] Code generation runs before analysis and tests.
- [ ] `flutter analyze` with zero errors is enforced.
- [ ] `flutter test` is enforced.
- [ ] APK and web artifacts are uploaded after a successful build.
- [ ] Flutter version is pinned and consistent between local and CI.
- [ ] Dependency caching is active.
- [ ] Pipeline fails correctly when any stage fails.
- [ ] No secrets are logged in pipeline output.

---

# 10. Open Questions

- Should CI run builds for all platforms (Android, Web, Linux) or only Android and Web initially?
- Should test coverage be enforced at a minimum threshold (e.g., 80%)?
- Should the pipeline include a scheduled nightly run for extended analysis?
- When should signed release builds be added to the pipeline?
- Should automated deployment to a staging environment be added before production release?
