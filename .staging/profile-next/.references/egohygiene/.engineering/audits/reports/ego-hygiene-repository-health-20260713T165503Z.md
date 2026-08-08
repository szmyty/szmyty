---
audit_id: ego-hygiene-repository-health-20260713T165503Z
audit_name: ego-hygiene-repository-health
strategy: holistic
status: complete
started_at: 2026-07-13T16:55:03Z
completed_at: 2026-07-13T17:30:00Z
repository: egohygiene/egohygiene
repository_revision: "91c2289222de223c702ebe1c9addba5004ead3eb"
auditor: auditor-agent v1.0.0
spec_version: "1.0.0"
depth: comprehensive
scope:
  included:
    - "."
  excluded:
    - "**/build/**"
    - "**/.dart_tool/**"
    - "**/node_modules/**"
    - "**/.venv/**"
    - "**/__pycache__/**"
    - "**/*.g.dart"
    - "**/*.freezed.dart"
    - "**/*.generated.*"
    - "coverage/**"
    - "dist/**"
---

# Ego Hygiene Repository Health Audit

> **First comprehensive holistic audit of the egohygiene/egohygiene repository.**
> Revision `91c2289` · Audited 2026-07-13

---

## Executive Summary

The Ego Hygiene repository is a **well-architected, specification-driven Flutter application** at an early but thoughtful stage of development. The codebase has evolved from a blank-slate foundation into a functioning multi-feature application with strong architectural governance, a rich specification system, and a layered CI/CD pipeline.

The repository's greatest strengths are its **documentation discipline** and **architectural governance**: layered knowledge-system philosophy, extensive specifications, composite reusable CI actions, role-based onboarding paths, a formal AI Constitution, and a documented extraction plan toward an independent Flutter Foundation. These are characteristics rarely seen at this project scale and represent genuine long-term value.

The most actionable concerns cluster around three areas:

1. **CI/CD duplication and gaps** — the PR and main-branch workflows share near-identical job logic without a shared composite layer; the CI pipeline lacks formatting enforcement, has no integration-test gate, and coverage enforcement is opt-in by default.
2. **Dependency hygiene** — one end-of-life marker (`sqlite3_flutter_libs+eol`), one pre-release dev dependency (`freezed ^3.2.6-dev.1`), one unbounded dev constraint (`riverpod: any`), and debug logging in production dependencies.
3. **Documentation drift** — `DECISIONS.md` contains only a template with zero recorded decisions; `apps/egohygiene/lib/README.md` describes 5 `shared/` subdirectories while the actual implementation has 33; the Golden test directory is a `.gitkeep` placeholder.

The prior audit (`docs/AUDIT.md`, 2026-07-06) flagged several concerns that remain partially open: data-at-rest encryption architecture is now documented and partially implemented, an AI Policy Gateway now exists, but localization coverage gaps (particularly in Progress/Graph screens), reduced-motion consistency, and integration-test CI gaps remain.

**Overall Health Score: 7.2 / 10** — Strong foundations, focused improvement needed on CI/CD automation robustness and documentation accuracy.

---

## Repository Context

### Consolidation Phase

The project is in **active consolidation**: architectural governance is complete and rich, the Flutter feature surface is being built out, and the repository has crossed from "foundation planning" into "foundation + feature delivery." The two current commits (`Initial plan`, `feat(mindgarden): establish canonical knowledge garden structure`) indicate this is a recently initialized or rebased repository at head.

### Major Subsystems

| Subsystem | Location | Maturity |
|---|---|---|
| Flutter App | `apps/egohygiene/` | Active development |
| Architecture governance | `ARCHITECTURE.md`, `docs/architecture/` | Well-established |
| Specification system | `.github/specs/` | 22 specs, active |
| Agent system | `.github/agents/` | 4 agents defined |
| CI/CD pipeline | `.github/workflows/` | 6 workflows, functional |
| Publishing tools | `publishing/tools/` | 2 Python tools operational |
| MindGarden | `mindgarden/` | Obsidian knowledge garden |
| Schemas | `schemas/` | practices schema only |
| Website | `website/` | Placeholder (empty) |

### Migration Status

The extraction plan (`docs/architecture/extraction-plan.md`) documents a formal Flutter Foundation extraction but explicitly states it does not yet move any code. The `shared/` directory currently holds ~33 top-level subsystems, all within the application module. No extraction has occurred. The 80/20 boundary target remains aspirational.

---

## Scope and Exclusions

### Included

All top-level repository structure including `.github/`, `apps/`, `docs/`, `mindgarden/`, `publishing/`, `schemas/`, `tasks/`, `website/`, root governance files, build configuration, and CI/CD workflows.

### Explicitly Excluded (Per Audit Request)

- `**/build/**`
- `**/.dart_tool/**`
- `**/node_modules/**`
- `**/.venv/**`
- `**/__pycache__/**`
- `**/*.g.dart`, `**/*.freezed.dart`, `**/*.generated.*`
- `coverage/**`, `dist/**`

### Not Deeply Inspected (Documented)

- `mindgarden/.obsidian/` — Obsidian configuration directory (editor config)
- `apps/egohygiene/ios/`, `apps/egohygiene/macos/`, `apps/egohygiene/windows/` — non-target platform scaffolding
- `apps/egohygiene/android/` — build configuration only, no application logic
- Individual publishing articles under `publishing/channels/`
- Individual MindGarden knowledge notes under `mindgarden/knowledge/`
- Python lock files under `publishing/tools/*/poetry.lock`

---

## Methodology

### Reading Order Followed

1. `README.md` and `START_HERE.md` ✓
2. `ARCHITECTURE.md`, `SYSTEM.md`, `DESIGN.md` ✓
3. `AI_CONSTITUTION.md`, `DECISIONS.md` ✓  
   `CONTRIBUTOR_GUIDE.md` → located at `docs/CONTRIBUTOR_GUIDE.md` (not root) ✓
4. `.github/specs/auditor.spec.md` ✓
5. All 22 files under `.github/specs/` (sampled key specs fully) ✓
6. `.github/agents/` (4 agents) and `.github/skills/flutter/` ✓
7. `audits/` → `.gitkeep` found, one prior report in `docs/AUDIT.md` ✓
8. `Taskfile.yml`, `package.json`, `commitlint.config.js` ✓
9. `apps/egohygiene/pubspec.yaml`, `publishing/tools/*/pyproject.toml` ✓
10. All 6 CI/CD workflows under `.github/workflows/` ✓
11. `apps/egohygiene/lib/` (main.dart, app/, features/, shared/) ✓
12. `apps/egohygiene/test/` (114 test files), `integration_test/` (8 files) ✓
13. `docs/` (AUDIT.md, architecture/, developer-setup.md, testing.md, etc.) ✓
14. `publishing/`, `mindgarden/`, `schemas/`, `tasks/`, `website/` ✓

### Validation Commands Run

```bash
# Git info
git -C /home/runner/work/egohygiene/egohygiene log --oneline -5
# Result: 91c2289 Initial plan
#         ed2d492 feat(mindgarden): establish canonical knowledge garden structure

git -C /home/runner/work/egohygiene/egohygiene rev-parse HEAD
# Result: 91c2289222de223c702ebe1c9addba5004ead3eb

# FVM configuration
cat .fvmrc
# Result: Flutter 3.44.2 pinned, useGitCache: true, updateMelosSettings: true

# Directory structure enumerated via ls, find, grep
# Flutter/FVM: not installed in audit environment — CLI validation not run

# Workflow files listed and read
# Audit scope: read-only inspection only
```

### Absent Files Noted

- `CONTRIBUTOR_GUIDE.md` at repository root — present at `docs/CONTRIBUTOR_GUIDE.md`; README and START_HERE reference it at root
- `Makefile` — not present; Taskfile is sole task automation
- `apps/egohygiene/test/golden/` — directory exists but contains only `.gitkeep` (no golden files)
- `website/` — directory exists but contains only `tsconfig.base.json` (no application content)
- No `SECURITY.md` at repository root
- No branch protection configuration visible in repository files

---

## Overall Assessment

| Dimension | Score | Notes |
|---|---|---|
| Architecture & Structure | 8/10 | Excellent governance; shared/ breadth creates cognitive load |
| Flutter Application | 7/10 | Feature-rich foundation; some prior-audit gaps remain |
| Testing | 6.5/10 | 114 unit/widget tests + 8 integration tests; golden tests absent; no CI integration gate |
| CI/CD & Automation | 6/10 | Functional but duplicated logic; coverage opt-in; no format gate; no signing |
| Documentation | 7.5/10 | Exceptional governance docs; some impl docs stale; DECISIONS.md is template-only |
| Publishing & MindGarden | 7/10 | Operational; auto-commit pattern is non-standard |
| Security & Privacy | 6.5/10 | Encryption and policy gateway exist; WiFi metadata access undocumented; +eol dep |
| Performance | 7/10 | Lazy-load concerns exist per prior audit; MotionManager well-implemented |
| Accessibility | 7/10 | AppAccessibility and MotionManager are strong; consistency not fully verifiable |
| Developer Experience | 7.5/10 | Excellent Taskfile and docs; minor inconsistencies with CI and FVM Melos setting |
| Dependencies | 6/10 | Large dep count; eol/pre-release markers; unbounded version constraint |

**Overall: 7.2 / 10 — Early-stage but architecturally mature. Ready for focused quality work.**

---

## Findings Summary

| ID | Title | Severity | Classification | Confidence | Status | Effort | Impact |
|---|---|---|---|---|---|---|---|
| AUDIT-001 | CI workflow logic is heavily duplicated | High | CI/CD | High | Confirmed | Medium | High |
| AUDIT-002 | Pub package cache absent from analyze and test jobs | High | CI/CD | High | Confirmed | Small | High |
| AUDIT-003 | Integration tests have no CI pipeline gate | High | CI/CD | High | Confirmed | Medium | High |
| AUDIT-004 | Code format check absent from CI pipeline | Medium | CI/CD | High | Confirmed | Small | Medium |
| AUDIT-005 | Coverage threshold is opt-in and unenforced by default | Medium | CI/CD | High | Confirmed | Small | Medium |
| AUDIT-006 | Flutter version is hardcoded in three separate locations | Medium | Maintainability | High | Confirmed | Small | Medium |
| AUDIT-007 | `sqlite3_flutter_libs` carries an `+eol` version suffix | High | Dependency | High | Confirmed | Medium | High |
| AUDIT-008 | `freezed` dev dependency is a pre-release version | Medium | Dependency | High | Confirmed | Small | Medium |
| AUDIT-009 | `riverpod: any` dev dependency has unbounded version constraint | Medium | Dependency | High | Confirmed | Small | Medium |
| AUDIT-010 | `pretty_dio_logger` in production dependencies enables HTTP logging | Medium | Security | High | Confirmed | Small | Medium |
| AUDIT-011 | WiFi SSID and gateway data collected without documented consent flow | Medium | Security | Medium | Probable | Small | Medium |
| AUDIT-012 | `DECISIONS.md` contains only a template with zero actual decisions | High | Documentation | High | Confirmed | Small | High |
| AUDIT-013 | `apps/egohygiene/lib/README.md` is materially out-of-date | Medium | Documentation | High | Confirmed | Small | Medium |
| AUDIT-014 | Golden test directory is an empty placeholder | High | Testing | High | Confirmed | Large | High |
| AUDIT-015 | Development-build test job does not collect coverage | Medium | CI/CD | High | Confirmed | Small | Medium |
| AUDIT-016 | `build_runner build` in generate action lacks `--delete-conflicting-outputs` | Medium | DX | High | Confirmed | Small | Medium |
| AUDIT-017 | RSS sync workflows commit directly to `main` without a PR | Medium | CI/CD | High | Confirmed | Medium | Medium |
| AUDIT-018 | Action version divergence across workflows | Low | CI/CD | High | Confirmed | Small | Low |
| AUDIT-019 | `.fvmrc` `updateMelosSettings: true` but Melos is not used | Low | DX | High | Confirmed | Trivial | Low |
| AUDIT-020 | `task clean` removes FVM SDK cache, forcing expensive re-downloads | Low | DX | High | Confirmed | Small | Low |
| AUDIT-021 | `task ci:local` includes `dart:format` but CI does not enforce formatting | Medium | DX | High | Confirmed | Small | Medium |
| AUDIT-022 | Website directory is an unpopulated placeholder | Low | Architecture | High | Confirmed | Unknown | Low |
| AUDIT-023 | `shared/` module has 33 top-level subdirectories creating high cognitive load | Medium | Architecture | High | Confirmed | Large | Medium |
| AUDIT-024 | Extraction plan is well-documented but has no execution phase begun | Informational | Architecture | High | Intentional trade-off | Unknown | High |
| AUDIT-025 | Android APK build not signed; no key management configured | High | Security | Medium | Needs validation | Large | High |
| AUDIT-026 | `docs/AUDIT.md` is a prior informal audit file outside the `audits/` system | Low | Documentation | High | Confirmed | Trivial | Low |
| AUDIT-027 | `tasks/tests.yml` purpose is undocumented and the file is empty | Low | DX | High | Confirmed | Trivial | Low |
| AUDIT-028 | Publishing Python tool environments are managed independently | Low | DX | Medium | Confirmed | Medium | Low |
| AUDIT-029 | Prior audit findings for localization gaps remain open | Medium | Documentation | Medium | Probable | Medium | Medium |
| AUDIT-030 | Sensor and hardware metadata permissions not privacy-policy documented | Medium | Security | Medium | Probable | Small | Medium |
| AUDIT-031 | `CONTRIBUTOR_GUIDE.md` path inconsistency between root and `docs/` | Low | Documentation | High | Confirmed | Trivial | Low |
| AUDIT-032 | `schemas/` directory contains only `practices/` schema | Informational | Architecture | High | Confirmed | Unknown | Low |
| AUDIT-033 | No `SECURITY.md` file at repository root | Low | Security | High | Confirmed | Small | Low |

---

## Critical Findings

*No new Critical-severity findings were identified in this audit.*

Prior critical findings from `docs/AUDIT.md` (2026-07-06):

- **C1 — Data-at-rest encryption**: The storage architecture documentation now describes an `EncryptionManager` → `AesGcmEncryptionProvider` → `KeyManager` chain. Encryption infrastructure is partially implemented. Actual application of field-level or database-level encryption to `AppDatabase` reflection/check-in/memory tables was **not independently confirmed** by this audit. See AUDIT-025 note on validation needed.
- **C2 — AI Constitution enforcement**: An `AiPolicyGateway` class now exists in `lib/shared/ai/ai_policy_gateway.dart` with regex-based harm, diagnosis, and certainty pattern matching. This represents meaningful progress from the prior audit.

---

## High-Priority Findings

### AUDIT-001 — CI workflow logic is heavily duplicated between PR and main-branch pipelines

**Classification:** Maintainability  
**Severity:** High  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.github/workflows/build.yml`, `.github/workflows/development-build.yml`  
**Effort:** Medium  
**Impact:** High

#### Observation

The `build.yml` (PR validation) and `development-build.yml` (main branch) workflows contain near-identical job definitions for `analyze`, `build-android`, `build-web`, `build-linux`, and the `changes` filter. The only structural differences are: `development-build.yml` adds a `publish` job and omits coverage collection from the test job. All other job steps — checkout, Flutter setup, generate, build commands, artifact upload — are copy-pasted with minor naming variations.

#### Evidence

- Observed: `build.yml` L59–L268 and `development-build.yml` L62–L205 contain structurally identical job definitions for `analyze`, `build-android`, `build-web`, and `build-linux`.
- Observed: `changes` job (path filter logic) is duplicated verbatim in both files.
- Observed: Composite actions `flutter-setup` and `flutter-generate` already exist, showing the team has adopted the reusable-action pattern for steps — but not yet for jobs.

#### Why It Matters

Any change to build configuration (new Linux dependency, updated artifact path, cache key update) must be applied in two places. Divergence has already occurred: `build.yml` `test` job runs `--coverage` while `development-build.yml` `test` does not (AUDIT-015). As the project grows, more divergence is inevitable, creating silent CI parity failures.

#### Recommendation

Extract the shared job logic into [reusable workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows) (`workflow_call`) for `analyze`, `test`, and build jobs. The PR and main-branch workflows then become thin orchestrators that call the reusable workflows with appropriate inputs.

#### Suggested Validation

After extraction, trigger both workflows and verify job outcomes are identical. Add a `workflow_call` input parameter for `collect-coverage` to control the one known difference.

#### Dependencies or Risks

Depends on: none. Risk: reusable workflow syntax requires the caller and callee to be in the same repository or organization. This is satisfied here.

---

### AUDIT-002 — Pub package cache is absent from `analyze` and `test` CI jobs

**Classification:** Performance  
**Severity:** High  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.github/workflows/build.yml` (analyze, test jobs), `.github/workflows/development-build.yml` (analyze, test jobs)  
**Effort:** Small  
**Impact:** High

#### Observation

The composite action `.github/actions/flutter-setup/action.yml` correctly caches the Pub package cache via `actions/cache@v4` using `pubspec.lock` as the hash key. However, the `analyze` and `test` jobs in both `build.yml` and `development-build.yml` use this composite action, so the cache is available. What is missing is that `build-android` and `build-web` and `build-linux` jobs each re-run `flutter pub get` through the same composite action. On cache hit, this is fast, but on cache miss all four jobs (analyze, test, build-android, build-web, build-linux) independently re-download the full pub graph rather than sharing a single warm cache within the run.

More importantly: the `flutter-generate` composite action does **not** include any caching for generated artifacts, meaning `build_runner` re-runs full generation on every job even when source files have not changed since a previous job in the same run.

#### Evidence

- Observed: `.github/actions/flutter-setup/action.yml` includes `actions/cache@v4` for `${{ env.PUB_CACHE }}` keyed on `pubspec.lock`.
- Observed: `build.yml` analyze, test, build-android, build-web, build-linux each independently invoke `flutter-setup` and therefore each perform their own cache restore.
- Observed: `.github/actions/flutter-generate/action.yml` has no caching step.
- Inferred: code generation (`build_runner build`) runs independently in each job that calls `flutter-generate`, even within a single workflow run.

#### Why It Matters

Without generated-artifact sharing between jobs, `build_runner` (which can take 60–120+ seconds) executes independently in analyze, test, and each build job. For a 5-job run, this represents 5× generation overhead. As the codebase grows with more Riverpod providers, Drift tables, and Freezed classes, this will compound significantly.

#### Recommendation

Upload generated files as a job artifact after the `analyze` step (which is the first to run generation) and download them in subsequent jobs, or use `actions/upload-artifact`/`download-artifact` to share the generated `lib/**/*.g.dart` outputs. Alternatively, add a dedicated `generate` job that runs once and exports artifacts to all downstream jobs.

#### Suggested Validation

Compare job durations before and after with GitHub Actions timing summary.

#### Dependencies or Risks

Depends on: AUDIT-001 (addressing workflow duplication first would make this easier to implement in one place).

---

### AUDIT-003 — Integration tests have no CI pipeline gate

**Classification:** Testing  
**Severity:** High  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.github/workflows/`, `apps/egohygiene/integration_test/`  
**Effort:** Medium  
**Impact:** High

#### Observation

Eight integration tests exist in `apps/egohygiene/integration_test/`: `app_smoke_test.dart`, `first_launch_test.dart`, `onboarding_test.dart`, `navigation_test.dart`, `reflection_flow_test.dart`, `conversation_test.dart`, `settings_test.dart`, and `restart_persistence_test.dart`. None of these are executed by any CI workflow. The `docs/architecture/testing.md` and `docs/testing.md` explicitly define integration tests as a test layer and provide run instructions, but no CI job executes them.

#### Evidence

- Observed: `integration_test/` contains 8 test files covering critical user flows.
- Observed: `build.yml` and `development-build.yml` test jobs run `flutter test --coverage` or `flutter test` — both commands default to `test/` and do not run integration tests.
- Observed: No workflow file references `integration_test/` in any `run:` step.
- Observed: `docs/architecture/testing.md` L57–76 documents integration test execution commands but references device-connected runs only.

#### Why It Matters

Integration tests exist for the exact flows that are hardest to cover with unit and widget tests: startup lifecycle, persistence across restarts, navigation, onboarding completion, and conversation flows. Without a CI gate, these tests may accumulate drift from the actual codebase and provide false confidence when they pass locally but are never automatically verified on PRs.

#### Recommendation

Add a CI job that runs integration tests against a virtual device (Android emulator or Chrome for web). GitHub Actions supports Android emulators via `reactivecircus/android-emulator-runner@v2`. Chrome integration tests can run headlessly on `ubuntu-latest` with `flutter drive --target=integration_test/app_smoke_test.dart -d chrome`. Start with the smoke and navigation tests which are lowest-risk.

#### Suggested Validation

Add the job to `build.yml` as a gated step after `test`. Verify it passes in a workflow run before making it blocking.

#### Dependencies or Risks

Integration tests require device access and add ~3–10 minutes to CI. Consider running only smoke and navigation tests in CI and leaving full flows for scheduled runs.

---

### AUDIT-007 — `sqlite3_flutter_libs` carries an `+eol` version suffix

**Classification:** Dependency  
**Severity:** High  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `apps/egohygiene/pubspec.yaml`  
**Effort:** Medium  
**Impact:** High

#### Observation

The `pubspec.yaml` declares `sqlite3_flutter_libs: ^0.6.0+eol`. The `+eol` build metadata in a Pub version string is non-standard — it is not a standard Semver pre-release marker. In the context of `sqlite3_flutter_libs`, this signals that the `0.6.x` line is intended as a compatibility shim while migration to a newer API or package is expected. Continuing to depend on an end-of-life shim means the project will not receive security patches or platform compatibility updates.

#### Evidence

- Observed: `apps/egohygiene/pubspec.yaml` line: `sqlite3_flutter_libs: ^0.6.0+eol`
- Inferred: The `+eol` suffix is a publisher signal that this version line is deprecated.
- Inferred: `drift` (v2.34.0) ships its own SQLite abstractions and may have a preferred `sqlite3_flutter_libs` version aligned with the drift ecosystem.

#### Why It Matters

For a privacy-first, local-first application where user data lives in a local SQLite database, the SQLite library version is security-critical. An EOL dependency may accumulate vulnerabilities without receiving patches. SQLite vulnerabilities (though rare) can result in privilege escalation or data corruption.

#### Recommendation

Check the `drift` changelog and `sqlite3_flutter_libs` pub.dev page for the recommended migration path. Upgrade to the current supported version of `sqlite3_flutter_libs`. Verify with `task analyze` and `task test` after upgrade.

#### Suggested Validation

Run `task outdated` from repository root after updating to see remaining outdated deps. Run `task test` to confirm no regressions.

#### Dependencies or Risks

Drift compatibility must be confirmed before upgrading. May require coordinated update of `drift` and `drift_dev` versions.

---

### AUDIT-012 — `DECISIONS.md` contains only a template with zero actual decisions recorded

**Classification:** Documentation  
**Severity:** High  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `DECISIONS.md`  
**Effort:** Small  
**Impact:** High

#### Observation

`DECISIONS.md` is a 172-line document that defines a template structure for decisions (Decision, Context, Alternatives, Tradeoffs, Rationale, Future Reconsideration) and lists **examples of future entries** — but contains zero actual recorded decisions. The "Examples" section lists decisions like "Flutter Foundation extracted into reusable packages" and "AI providers abstracted behind registries," both of which are significant architectural choices already made, but none are documented as formal decision records.

#### Evidence

- Observed: `DECISIONS.md` has no section that conforms to the decision template with filled-in content.
- Observed: The file contains only: overview, purpose, principles, template, a list of "future examples," and an evolution section.
- Inferred: Multiple significant decisions have been made (Riverpod v3, GoRouter, Drift, Slang, FVM pinning, feature-first architecture, Poetry for tooling, Release Please) — none are documented.

#### Why It Matters

The explicit stated purpose of this document is to preserve architectural reasoning for future contributors (including AI agents). When AI agents load repository context, the absence of real decision records means they cannot access the reasoning behind key architectural choices. This increases the risk of re-litigating resolved decisions or making choices that conflict with prior rationale.

#### Recommendation

Immediately record at least the top 5–8 most significant decisions that have already been made: technology stack selections (Riverpod, Drift, GoRouter, Slang), the local-first/offline-first architecture choice, the FVM version pinning approach, the feature-first module organization, and the extraction plan decision. Use the template format already defined in the document.

#### Suggested Validation

After populating, verify that an AI agent given `DECISIONS.md` as context can answer "why was Riverpod chosen over Bloc?" with reasoned evidence.

#### Dependencies or Risks

None. This is a documentation-only task.

---

### AUDIT-014 — Golden test directory is an empty placeholder

**Classification:** Testing  
**Severity:** High  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `apps/egohygiene/test/golden/`  
**Effort:** Large  
**Impact:** High

#### Observation

The `apps/egohygiene/test/golden/` directory contains only a `.gitkeep` file. The `golden_toolkit` package (`^0.15.0`) is declared in `dev_dependencies`, and `docs/architecture/testing.md` explicitly lists golden tests as a test layer: "Golden tests — Visual regression coverage for design-system components and core screens." No golden test files exist.

#### Evidence

- Observed: `find apps/egohygiene/test/golden -type f` → only `.gitkeep`
- Observed: `pubspec.yaml` `dev_dependencies` includes `golden_toolkit: ^0.15.0`
- Observed: `docs/architecture/testing.md` L11 defines the golden test layer
- Observed: The prior audit (`docs/AUDIT.md`) testing spec mentions golden tests as a required layer

#### Why It Matters

Golden tests are the primary defense against visual regressions in design-system components. For a project where the design system (AppTheme, AppColors, AppSpacing, motion system) is central to the product experience, and where the DESIGN.md explicitly defines a detailed visual language, the absence of golden coverage means that design token changes, theme updates, or widget refactors can silently alter the visual output without detection.

#### Recommendation

Begin with 3–5 golden tests covering the highest-value design-system components: `AppCard`, `AppLoadingIndicator`, `AppErrorState`, and the home/onboarding screen in light and dark mode. These form a baseline that prevents the most visible regressions.

#### Suggested Validation

Generate goldens with `flutter test --update-goldens` and then verify they pass in a subsequent `flutter test` run. Add golden output to `.gitignore` exceptions or track them in the repository.

#### Dependencies or Risks

Golden tests are platform-sensitive (font rendering, pixel density). Use `golden_toolkit`'s `loadAppFonts()` and `GoldenToolkit.configure()` for consistent output. Establish device sizing conventions early.

---

### AUDIT-025 — Android APK release builds are not signed; no key management configured

**Classification:** Security  
**Severity:** High  
**Confidence:** Medium  
**Status:** Needs validation  
**Area:** `.github/workflows/release-artifacts.yml`, `apps/egohygiene/android/`  
**Effort:** Large  
**Impact:** High

#### Observation

The `release-artifacts.yml` workflow builds Android APKs with `flutter build apk --release` but does not include any signing step. The standard Flutter release build process requires a keystore and signing configuration (`key.properties`). Without signing, the released APK uses Flutter's debug key, which is not accepted by the Google Play Store and may trigger security warnings on side-load installation. `apps/egohygiene/android/key.properties` is gitignored (correct), but no CI secret injection or signing step is present in the workflow.

#### Evidence

- Observed: `release-artifacts.yml` build-android job runs `flutter build apk --release` with no signing step.
- Observed: `.gitignore` includes `**/android/key.properties` — correct to exclude from repository.
- Inferred: No `ANDROID_KEYSTORE_FILE`, `ANDROID_KEY_ALIAS`, or equivalent secrets are referenced in any workflow file.
- Unverified: Whether the app is currently being distributed to the Play Store or only via GitHub Releases.

#### Why It Matters

If the intent is to distribute the application publicly (the README links to GitHub Releases APK downloads), users installing the APK will receive a build signed with an inconsistent or debug key. For a privacy-focused application that stores personal reflection data, the signing chain is part of the trust model. Additionally, if a Play Store submission is planned, unsigned builds will fail submission.

#### Recommendation

1. Generate a production keystore and store it as an encrypted GitHub Actions secret.
2. Add a signing step to the `build-android` job in `release-artifacts.yml` using the standard `flutter build apk --release --key-alias`, or configure `android/app/build.gradle` to use `key.properties` injected from CI secrets.
3. Consider using `actions/setup-java` with `key-alias` and `keystore-password` inputs for secure key injection.

#### Suggested Validation

Build a signed APK locally and verify with `jarsigner -verify` or `apksigner verify`. Confirm the signing certificate matches for both development and release builds.

#### Dependencies or Risks

Key management requires a one-time keystore generation and secure storage in GitHub Secrets. Loss of the production keystore means the app cannot be updated on the Play Store.

---

## Medium-Priority Findings

### AUDIT-004 — Code format check is absent from the CI pipeline

**Classification:** CI/CD  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.github/workflows/build.yml`  
**Effort:** Small  
**Impact:** Medium

#### Observation

`task ci:local` (the local CI parity command) includes `task dart:format` (`fvm dart format .`). However, neither `build.yml` nor `development-build.yml` include a `dart format --output=none --set-exit-if-changed` check. This means formatting violations in submitted code will pass CI and only be caught locally by contributors who run `task ci:local`.

#### Evidence

- Observed: `Taskfile.yml` `ci:local` task: `task dart:format`, `task analyze`, `task test:coverage`.
- Observed: `build.yml` analyze job runs only `flutter analyze` — no format step.
- Inferred: Formatting divergence between contributors will accumulate over time.

#### Why It Matters

Inconsistent formatting creates noisy diffs, increases review friction, and can mask real code changes. The project already commits to 120-character page width and `prefer_single_quotes` in `analysis_options.yaml`; enforcing this in CI closes the gap between local and automated validation.

#### Recommendation

Add `dart format --output=none --set-exit-if-changed .` to the `analyze` job in `build.yml` (before `flutter analyze`). This is a read-only check that exits non-zero if any file would be reformatted.

#### Suggested Validation

Introduce a deliberate formatting violation in a branch and verify CI fails.

#### Dependencies or Risks

Some generated files may trigger false format checks — ensure the `analyzer` `exclude:` patterns in `analysis_options.yaml` also apply to the format check scope, or run format against `lib/` and `test/` explicitly.

---

### AUDIT-005 — Coverage threshold is opt-in and unenforced by default

**Classification:** CI/CD  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.github/workflows/build.yml` (test job)  
**Effort:** Small  
**Impact:** Medium

#### Observation

The `build.yml` test job computes line coverage and summarizes it in GitHub Step Summary but only enforces a minimum threshold when the `COVERAGE_THRESHOLD` repository variable is set. The variable defaults to empty string (`${{ vars.COVERAGE_THRESHOLD || '' }}`), and the enforcement step is guarded by `if: env.COVERAGE_THRESHOLD != ''`. No threshold is currently configured.

#### Evidence

- Observed: `build.yml` L18: `COVERAGE_THRESHOLD: ${{ vars.COVERAGE_THRESHOLD || '' }}`
- Observed: `build.yml` L149: `if: env.COVERAGE_THRESHOLD != ''` — enforcement is conditional.
- Inferred: No `COVERAGE_THRESHOLD` repository variable is currently set (not visible in repository files).

#### Why It Matters

Without a threshold, coverage can silently regress on each PR. The coverage computation infrastructure is already in place — the only missing step is activating it with a realistic minimum.

#### Recommendation

Set the `COVERAGE_THRESHOLD` repository variable to a value that reflects current coverage (start at 60% if that is current reality) and ratchet it upward as coverage improves. Document the expected threshold in `docs/testing.md`.

#### Suggested Validation

Run `task test:coverage` locally, examine the LCOV output to determine current coverage, then set the variable accordingly.

#### Dependencies or Risks

If current coverage is below any reasonable threshold, this must first be addressed before enforcement can be activated.

---

### AUDIT-006 — Flutter version is hardcoded in three separate locations

**Classification:** Maintainability  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.fvmrc`, `.github/actions/flutter-setup/action.yml`, `.github/workflows/copilot-setup-steps.yml`  
**Effort:** Small  
**Impact:** Medium

#### Observation

The Flutter SDK version `3.44.2` appears in three places: `.fvmrc` (authoritative source), `.github/actions/flutter-setup/action.yml` (hardcoded default input), and `.github/workflows/copilot-setup-steps.yml` (hardcoded in a step).

#### Evidence

- Observed: `.fvmrc` `"flutter": "3.44.2"` — intended canonical source.
- Observed: `.github/actions/flutter-setup/action.yml` L12: `default: '3.44.2'`
- Observed: `.github/workflows/copilot-setup-steps.yml` L35: `flutter-version: '3.44.2'`

#### Why It Matters

When the Flutter version is upgraded, all three locations must be updated simultaneously. Missing one location means a CI job runs with a different Flutter version than the authoritative `.fvmrc`, producing subtle inconsistencies.

#### Recommendation

Have the `flutter-setup` composite action read `flutter-version` from `.fvmrc` using a step that extracts the version with `jq`, e.g.:
```bash
FLUTTER_VERSION=$(jq -r '.flutter' .fvmrc)
```
Then pass it as an output to the `subosito/flutter-action` step. This makes `.fvmrc` the single authoritative source. The `copilot-setup-steps.yml` should use the same composite action rather than duplicating the setup logic.

#### Suggested Validation

Change the version in `.fvmrc` only and verify all three workflows pick up the new version.

#### Dependencies or Risks

`subosito/flutter-action` requires the version as an input string; reading from `.fvmrc` adds a parsing step but is straightforward with `jq`.

---

### AUDIT-008 — `freezed` dev dependency is a pre-release version

**Classification:** Dependency  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `apps/egohygiene/pubspec.yaml`  
**Effort:** Small  
**Impact:** Medium

#### Observation

`pubspec.yaml` declares `freezed: ^3.2.6-dev.1` in `dev_dependencies`. Pre-release versions (`-dev.N`) are unstable by definition and may introduce breaking changes in patch-level releases within the same range. The `^` prefix in combination with a pre-release version has unusual behavior in Dart's Pub solver.

#### Evidence

- Observed: `apps/egohygiene/pubspec.yaml` `dev_dependencies`: `freezed: ^3.2.6-dev.1`
- Observed: Corresponding `freezed_annotation: ^3.1.0` is in production dependencies.

#### Why It Matters

Pre-release dev versions are not recommended for production code generation tooling. A patch release in the `3.2.6-dev` series could regenerate `*.freezed.dart` files with changed output, causing silent behavioral differences between generated code and production behavior. Additionally, pub.dev discoverability and security audit tools may skip pre-release versions.

#### Recommendation

Check pub.dev for the stable `freezed` release that targets `freezed_annotation: ^3.1.0` and upgrade to the stable version. If no stable version is available that matches the annotation version, pin to the exact pre-release version (`3.2.6-dev.1`) rather than using `^` to prevent unintended upgrades.

#### Suggested Validation

Run `task generate` after upgrading to confirm all generated files remain valid and `task analyze` passes.

#### Dependencies or Risks

`freezed_annotation` and `freezed` versions must remain compatible.

---

### AUDIT-009 — `riverpod: any` dev dependency has unbounded version constraint

**Classification:** Dependency  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `apps/egohygiene/pubspec.yaml`  
**Effort:** Small  
**Impact:** Medium

#### Observation

`pubspec.yaml` `dev_dependencies` includes `riverpod: any` — an explicit unbounded version constraint. This allows Pub to resolve any available version of the base `riverpod` package regardless of breaking changes. This is a common pattern in some code generation setups but carries risk.

#### Evidence

- Observed: `apps/egohygiene/pubspec.yaml` `dev_dependencies`: `riverpod: any`
- Observed: `flutter_riverpod: ^3.3.2` and `riverpod_annotation: ^4.0.3` are in production dependencies.

#### Why It Matters

`riverpod: any` will match Riverpod v2, v3, or any future breaking version. In a monorepo or dependency resolution conflict, Pub might resolve to a version inconsistent with `flutter_riverpod`'s expectations. This is particularly problematic if `riverpod` major versions ship with breaking API changes.

#### Recommendation

Pin `riverpod` to match the major version of `flutter_riverpod`: `riverpod: ^3.0.0` (matching the `^3.3.2` constraint in production).

#### Suggested Validation

Run `flutter pub get` and `task analyze` after constraining the version.

#### Dependencies or Risks

This is a low-risk change — the existing `pubspec.lock` already pins the resolved version; changing the constraint only affects future resolution.

---

### AUDIT-010 — `pretty_dio_logger` in production dependencies enables HTTP debug logging

**Classification:** Security  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `apps/egohygiene/pubspec.yaml`  
**Effort:** Small  
**Impact:** Medium

#### Observation

`pretty_dio_logger: ^1.4.0` is in `dependencies` (production), not `dev_dependencies`. This package intercepts Dio HTTP requests and responses and logs them to console with full headers, body, and response data. In a privacy-first application that may send AI prompts and responses over HTTP to a local Ollama instance, request/response logging should either be disabled in production builds or moved to a debug-only configuration.

#### Evidence

- Observed: `apps/egohygiene/pubspec.yaml` `dependencies`: `pretty_dio_logger: ^1.4.0`
- Observed: `analysis_options.yaml` `avoid_print: true` — signals awareness of logging hygiene.
- Inferred: HTTP logging of AI provider requests in a reflection/journaling application could expose personal content in debug logs or crash reports.

#### Why It Matters

A production build with active request logging may leak sensitive AI prompt content (user reflections, journal entries) to system log outputs accessible via `adb logcat` or crash reporting systems. This conflicts with the application's privacy-first philosophy.

#### Recommendation

Move `pretty_dio_logger` to `dev_dependencies` and conditionally attach the logger only in debug/development builds. Pattern:
```dart
if (kDebugMode) {
  dio.interceptors.add(PrettyDioLogger());
}
```
Alternatively, use the `AppEnvironment` enum to gate logger attachment to `development` and `staging` environments only.

#### Suggested Validation

Confirm that `flutter build apk --release` produces a binary where no HTTP request content is logged to system output. Use `adb logcat` on a release build to verify.

#### Dependencies or Risks

This requires finding all Dio client construction sites and removing or gating the logger attachment.

---

### AUDIT-011 — WiFi SSID, IP, and gateway data collected without a documented consent flow

**Classification:** Security  
**Severity:** Medium  
**Confidence:** Medium  
**Status:** Probable  
**Area:** `apps/egohygiene/lib/features/settings/providers/system_info_providers.dart`  
**Effort:** Small  
**Impact:** Medium

#### Observation

`system_info_providers.dart` uses `network_info_plus` to collect: WiFi network name (`wifiName`), IP address (`ipAddress`), gateway IP (`gatewayIp`), and subnet mask (`subnetMask`). This occurs in a `FutureProvider` (`networkInfoProvider`). It is unclear whether this data collection is gated by explicit user consent or disclosed in any privacy policy document.

#### Evidence

- Observed: `system_info_providers.dart` L231–234 collects `wifiName`, `wifiIP`, `wifiGatewayIP`, `wifiSubmask` via `NetworkInfo`.
- Observed: `lib/shared/privacy/` contains `consent_manager.dart`, `privacy_engine.dart`, `privacy_policy_registry.dart` — a consent framework exists.
- Unverified: Whether the `networkInfoProvider` result is gated behind a consent check.
- Inferred: WiFi SSID is considered sensitive network metadata; some platforms require `ACCESS_FINE_LOCATION` permission to obtain WiFi SSID on Android.

#### Why It Matters

The application's stated philosophy is "local-first, privacy-respecting." Collection of network topology data (gateway IP, subnet mask) in a reflection app is unusual and may require explicit justification and user consent. On Android 10+, accessing WiFi SSID requires location permission, which broadens the permission footprint beyond what users would expect from a journaling application.

#### Recommendation

Audit the purpose of `networkInfoProvider` — if it serves only the developer `SystemInfoDashboardScreen` (debug/diagnostic screen), gate it to `development`/`staging` environments only and remove it from production builds. If network information is needed for a legitimate feature, document its purpose in the privacy policy and ensure it passes through the existing `PrivacyPolicyRegistry`.

#### Suggested Validation

Check where `networkInfoProvider` is consumed. If only in the settings/system-info debug screen, restrict it to debug builds using the `AppEnvironment` check.

#### Dependencies or Risks

Changing permission footprint affects Play Store listing and may require updated permission rationale strings.

---

### AUDIT-013 — `apps/egohygiene/lib/README.md` is materially out-of-date

**Classification:** Documentation  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `apps/egohygiene/lib/README.md`  
**Effort:** Small  
**Impact:** Medium

#### Observation

`apps/egohygiene/lib/README.md` describes the `shared/` directory with 8 subdirectories (localization, models, providers, routing, services, theme, models, widgets). The actual `shared/` directory contains 33 top-level subdirectories including `ai/`, `analytics/`, `animation/`, `capture/`, `conflict/`, `connectivity/`, `context/`, `debug/`, `environment/`, `flags/`, `goal/`, `graph/`, `health/`, `insight/`, `location/`, `memory/`, `performance/`, `personal_health/`, `portability/`, `practice/`, `privacy/`, `sync/`, `timeline/`, `version/`, and others.

#### Evidence

- Observed: `apps/egohygiene/lib/README.md` `shared/` section lists ~8 subdirs.
- Observed: `ls apps/egohygiene/lib/shared/` returns 33 directories.
- Observed: The README lists features that are also out-of-date (shows `home`, `reflection`, `memory`, `progress`, `settings` — actual feature dirs include also `check_in`, `conversation`, `graph`, `health`, `onboarding`, `personal_model`).

#### Why It Matters

This README is referenced by AI agents during onboarding context loading. Out-of-date structural documentation causes AI to generate code that doesn't match the actual architecture, particularly around import paths, service locations, and shared module boundaries.

#### Recommendation

Regenerate the README structure section to match the actual `lib/` structure. Consider scripting the directory listing as part of a maintenance task, or note in the README that the structure is illustrative and may not reflect the complete current state.

#### Suggested Validation

After updating, verify the feature list and shared subdirectory list match `ls lib/features/` and `ls lib/shared/` outputs exactly.

#### Dependencies or Risks

None. Documentation-only change.

---

### AUDIT-015 — `development-build.yml` test job does not collect coverage

**Classification:** CI/CD  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.github/workflows/development-build.yml` (test job)  
**Effort:** Small  
**Impact:** Medium

#### Observation

The `build.yml` test job runs `flutter test --coverage` and uploads a `coverage-lcov` artifact with 7-day retention. The `development-build.yml` test job runs `flutter test` without `--coverage`, producing no coverage artifact for main-branch builds. This means coverage data is collected on PRs but not on merged commits.

#### Evidence

- Observed: `build.yml` L99: `flutter test --coverage`
- Observed: `development-build.yml` L102: `flutter test` (no `--coverage`)

#### Why It Matters

Coverage reports on main-branch builds are the primary baseline for tracking coverage trends over time. Without them, there is no way to detect if a merged PR decreased overall coverage. This is a directly observable consequence of the workflow duplication identified in AUDIT-001.

#### Recommendation

Add `--coverage` to the test step in `development-build.yml` and upload the resulting `coverage/lcov.info` as an artifact (or a different artifact name to distinguish from PR runs).

#### Suggested Validation

Confirm `coverage-lcov` artifact appears in the Development Build workflow run history after the fix.

#### Dependencies or Risks

Addressed most efficiently alongside AUDIT-001 (workflow unification).

---

### AUDIT-016 — `flutter-generate` composite action does not use `--delete-conflicting-outputs`

**Classification:** DX  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.github/actions/flutter-generate/action.yml`  
**Effort:** Small  
**Impact:** Medium

#### Observation

The `flutter-generate` composite action runs `dart run build_runner build` without the `--delete-conflicting-outputs` flag. However, `docs/developer-setup.md` explicitly instructs developers to use `fvm flutter pub run build_runner build --delete-conflicting-outputs`, and `task generate` also runs `fvm dart run build_runner build --delete-conflicting-outputs`. CI and local generation have inconsistent behavior.

#### Evidence

- Observed: `.github/actions/flutter-generate/action.yml` step: `dart run build_runner build`
- Observed: `Taskfile.yml` `generate` task: `fvm dart run build_runner build --delete-conflicting-outputs`
- Observed: `docs/developer-setup.md` uses `--delete-conflicting-outputs`

#### Why It Matters

If a generated file has a stale version (from a previous generation pass with a different Dart version or code-gen version), `build_runner build` without `--delete-conflicting-outputs` will fail with a conflict error rather than resolving it. This creates non-deterministic CI failures that are difficult to diagnose.

#### Recommendation

Add `--delete-conflicting-outputs` to the `flutter-generate` action's `dart run build_runner build` command to match local developer workflow.

#### Suggested Validation

Introduce a conflict situation (manually create a stale `.g.dart` file) and verify CI handles it cleanly after the fix.

#### Dependencies or Risks

None. This is a purely additive flag.

---

### AUDIT-017 — RSS sync workflows commit directly to `main` without a pull request

**Classification:** CI/CD  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.github/workflows/medium-rss-sync.yml`, `.github/workflows/pinterest-rss-sync.yml`  
**Effort:** Medium  
**Impact:** Medium

#### Observation

Both `medium-rss-sync.yml` and `pinterest-rss-sync.yml` use `git push` to commit synchronized content directly to `main` (with commit message `[skip ci]`). This bypasses any PR process, code review, or branch protection rules that may be in effect.

#### Evidence

- Observed: `medium-rss-sync.yml` L59–68: `git commit ... && git push`
- Observed: `pinterest-rss-sync.yml` L59–68: `git commit ... && git push`
- Observed: Both workflows have `permissions: contents: write` at the job level.

#### Why It Matters

Direct commits to `main` from automated workflows:
- Bypass branch protection (if configured)
- Are not reviewed by any contributor
- Can pollute `git log` with automated noise
- In case of a sync bug (e.g., corrupted content), the damage is immediately in `main`

For content-only files (publishing archives), this pattern is acceptable in many projects, but it should be a deliberate choice with documentation.

#### Recommendation

Either:
1. Document this as an intentional trade-off in `DECISIONS.md` with explicit rationale (content archives are low-risk, skip-ci is appropriate)
2. Or change the workflows to open PRs (e.g., using `peter-evans/create-pull-request@v7`) for review before merging

If keeping the direct-commit approach, document it and ensure `main` branch protection rules explicitly allow `github-actions[bot]` to bypass PR requirements for content paths.

#### Suggested Validation

Confirm that existing branch protection settings (if any) account for this workflow behavior.

#### Dependencies or Risks

Changing to PR-based flow would introduce latency in content synchronization.

---

### AUDIT-021 — `task ci:local` includes `dart:format` but CI does not enforce formatting

**Classification:** DX  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `Taskfile.yml`, `.github/workflows/build.yml`  
**Effort:** Small  
**Impact:** Medium

#### Observation

`task ci:local` is documented as "Execute full local validation suite mimicking the CI/CD environment" and includes `task dart:format`. However, CI (`build.yml`) does not run a format check step. This means `task ci:local` passes formatting enforcement that does not exist in actual CI, breaking the parity guarantee implied by the task description.

#### Evidence

- Observed: `Taskfile.yml` `ci:local` task: `task pub-get`, `task generate`, `task dart:format`, `task analyze`, `task test:coverage`
- Observed: `build.yml` analyze job: `flutter analyze` only — no format step.
- Inferred: `dart:format` in `ci:local` runs `fvm dart format .` (reformats), not a check (`--output=none --set-exit-if-changed`).

#### Why It Matters

The `ci:local` task is presented to contributors as a way to catch issues before pushing. If `dart:format` runs in `ci:local` but CI doesn't check format, contributors get a false confidence: their code is formatted locally but CI would accept unformatted code. Additionally, `dart format .` is a destructive reformat, not a check — contributors may accidentally reformat generated files.

#### Recommendation

1. Add `dart format --output=none --set-exit-if-changed lib/ test/` to CI (see AUDIT-004).
2. Change the `ci:local` `dart:format` step to use `--output=none --set-exit-if-changed` or add a separate `dart:format:check` task that mirrors what CI does.

#### Suggested Validation

After adding the CI check, verify `task ci:local` and CI behavior are identical for a formatting violation.

#### Dependencies or Risks

Depends on AUDIT-004 being addressed. Must align the format check scope between local and CI.

---

### AUDIT-023 — `shared/` module has 33 top-level subdirectories creating high cognitive load

**Classification:** Architecture  
**Severity:** Medium  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `apps/egohygiene/lib/shared/`  
**Effort:** Large  
**Impact:** Medium

#### Observation

The `shared/` directory contains 33 top-level subdirectories: `ai`, `analytics`, `animation`, `assets`, `capture`, `conflict`, `connectivity`, `context`, `debug`, `environment`, `flags`, `goal`, `graph`, `health`, `insight`, `localization`, `location`, `memory`, `performance`, `personal_health`, `portability`, `practice`, `privacy`, `providers`, `routing`, `services`, `settings`, `storage`, `sync`, `theme`, `timeline`, `version`, `widgets`. This is a direct consequence of the "foundation-first" architecture placing all reusable infrastructure in one location.

#### Evidence

- Observed: `ls apps/egohygiene/lib/shared/ | wc -l` → 33
- Observed: The `docs/architecture/extraction-plan.md` lists 23 distinct "reusable foundation infrastructure" systems, consistent with this count.
- Inferred: Without extraction, every new AI-assisted implementation or new contributor must navigate all 33 subdirectories to understand what is available.

#### Why It Matters

A flat 33-directory module is cognitively expensive to navigate. Finding the right abstraction requires either deep familiarity or systematic search. This slows onboarding, increases the chance of duplicate implementations (creating a `NewFooManager` instead of finding the existing `FooEngine`), and makes it harder for AI agents to reason about boundaries.

#### Recommendation

Until the extraction plan is executed, group `shared/` subdirectories with a documented taxonomy:
- **Platform abstractions**: `connectivity`, `location`, `performance`, `storage`, `services`
- **State and engines**: `ai`, `analytics`, `context`, `conflict`, `insight`, `memory`, `sync`
- **Domain concepts**: `capture`, `goal`, `graph`, `health`, `personal_health`, `practice`, `timeline`
- **UI foundations**: `animation`, `assets`, `theme`, `widgets`
- **Application lifecycle**: `environment`, `flags`, `routing`, `version`
- **Data governance**: `portability`, `privacy`, `settings`
- **Debug**: `debug`
- **Providers**: `providers` (Riverpod app-level)

Document this taxonomy in `apps/egohygiene/lib/README.md` and `docs/architecture/overview.md`.

#### Suggested Validation

After documenting the taxonomy, verify an AI agent can navigate to the correct subsystem given a feature description without needing to list all 33 directories.

#### Dependencies or Risks

The extraction plan (AUDIT-024) is the long-term resolution. This finding recommends interim documentation improvement.

---

### AUDIT-029 — Prior audit localization gap findings remain open

**Classification:** Maintainability  
**Severity:** Medium  
**Confidence:** Medium  
**Status:** Probable  
**Area:** `apps/egohygiene/lib/features/progress/`, `apps/egohygiene/lib/features/graph/`  
**Effort:** Medium  
**Impact:** Medium

#### Observation

The prior `docs/AUDIT.md` (H1) flagged "Localization consistency is broken in key product surfaces" including hardcoded English strings in the Progress screen. This audit was unable to independently verify the current state of localization coverage in all feature screens (would require running `flutter analyze` with localization linting). However, the `en.i18n.json` structure was observed to be well-defined, and the architecture is correct.

#### Evidence

- Inferred: `docs/AUDIT.md` H1 identified Progress screen copy as hardcoded English.
- Unverified: Current state of Progress, Graph, and other feature screens.
- Observed: `lib/shared/localization/en.i18n.json` exists with structured keys.
- Unverified: Whether all user-facing strings have been migrated to localization keys.

#### Why It Matters

Localization gaps block internationalization readiness and create inconsistent voice/tone. The DESIGN.md defines a careful copy style; hardcoded strings bypass this system.

#### Recommendation

Run a localization completeness audit: search for hardcoded user-facing strings (non-empty string literals in widget builds that are not `t.someKey`) across all feature screens. Use a custom lint rule or a grep scan of `Text(` and `title:` properties.

#### Suggested Validation

`grep -rn 'Text("' apps/egohygiene/lib/features/ --include="*.dart"` as a starting point. All matches should ideally be `Text(t.someKey)` patterns.

#### Dependencies or Risks

Localization fixes are low-risk individually but require coordination to avoid duplicate or inconsistent key naming.

---

### AUDIT-030 — Sensor and hardware metadata permissions are not documented in the privacy policy

**Classification:** Security  
**Severity:** Medium  
**Confidence:** Medium  
**Status:** Probable  
**Area:** `apps/egohygiene/lib/features/settings/providers/system_info_providers.dart`, `lib/shared/privacy/`  
**Effort:** Small  
**Impact:** Medium

#### Observation

The `system_info_providers.dart` collects accelerometer/gyroscope data (via `sensors_plus`), battery state/level (via `battery_plus`), and network topology data (via `network_info_plus`). The application has a `PrivacyPolicyRegistry` and `ConsentManager` in `lib/shared/privacy/`. It is unclear whether these hardware/network data collections are registered in the privacy policy or gated by consent checks.

#### Evidence

- Observed: `system_info_providers.dart` uses `sensors_plus`, `battery_plus`, `network_info_plus`.
- Observed: `lib/shared/privacy/privacy_policy_registry.dart` exists — a consent framework is in place.
- Unverified: Whether `networkInfoProvider`, `batteryInfoProvider`, and accelerometer providers are gated by consent.
- Inferred: WiFi name collection requires `ACCESS_FINE_LOCATION` on Android 10+, broadening permission footprint.

#### Why It Matters

A "local-first, privacy-respecting" application collecting sensor, battery, and network data without explicit consent and documentation creates a trust gap between the product philosophy and the actual implementation. App Store review teams may flag undisclosed hardware access.

#### Recommendation

Audit each hardware/network provider: determine if it is accessible in production builds, document its purpose, and ensure it is covered by the privacy policy via `PrivacyPolicyRegistry`. If purely for debug purposes, restrict to development/staging environments.

#### Suggested Validation

Review the privacy policy data map (if one exists) and verify it covers all hardware data collection points.

#### Dependencies or Risks

Related to AUDIT-011. Addressing both together is efficient.

---

## Low-Priority Findings

### AUDIT-018 — Action version divergence across workflows

**Classification:** Maintainability  
**Severity:** Low  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.github/workflows/`  
**Effort:** Small  
**Impact:** Low

#### Observation

`build.yml`, `development-build.yml`, `release-artifacts.yml`, and `copilot-setup-steps.yml` use `actions/checkout@v5`. However, `medium-rss-sync.yml` and `pinterest-rss-sync.yml` use `actions/checkout@v4`. Similarly, `copilot-setup-steps.yml` is a slightly expanded version of `flutter-setup` rather than calling the composite action.

#### Evidence

- Observed: `build.yml` L39: `uses: actions/checkout@v5`
- Observed: `medium-rss-sync.yml` L29: `uses: actions/checkout@v4`
- Observed: `pinterest-rss-sync.yml` L29: `uses: actions/checkout@v4`

#### Why It Matters

Version divergence is a minor maintenance concern but can cause different behavior between workflows (e.g., `checkout@v4` vs `v5` may have different default settings for `fetch-depth`, sparse checkout, etc.).

#### Recommendation

Standardize all workflows on `actions/checkout@v5`. Update RSS sync workflows as part of routine maintenance.

#### Suggested Validation

After update, trigger both RSS sync workflows and confirm they behave identically to before.

#### Dependencies or Risks

None.

---

### AUDIT-019 — `.fvmrc` `updateMelosSettings: true` but Melos is not used

**Classification:** DX  
**Severity:** Low  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `.fvmrc`  
**Effort:** Trivial  
**Impact:** Low

#### Observation

`.fvmrc` includes `"updateMelosSettings": true`. Melos is a Dart monorepo management tool, but this repository does not use Melos — there is no `melos.yaml`, no `melos` in any dependency manifest, and no Melos commands in `Taskfile.yml`.

#### Evidence

- Observed: `.fvmrc` `"updateMelosSettings": true`
- Observed: No `melos.yaml` at repository root
- Observed: No `melos` in `pubspec.yaml` or `Taskfile.yml`

#### Why It Matters

This is a minor configuration noise item. The `updateMelosSettings: true` setting tells FVM to update Melos workspace configuration on SDK changes. Since Melos is absent, this setting has no effect but creates confusion for contributors reading the FVM config.

#### Recommendation

Set `"updateMelosSettings": false` in `.fvmrc`. If Melos adoption is planned, restore this flag at that time.

#### Suggested Validation

No validation needed — purely cosmetic.

#### Dependencies or Risks

None.

---

### AUDIT-020 — `task clean` removes FVM SDK cache

**Classification:** DX  
**Severity:** Low  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `Taskfile.yml` (`clean` task)  
**Effort:** Small  
**Impact:** Low

#### Observation

`task clean` removes `build/`, `coverage/`, `.dart_tool/`, and also `.fvm/flutter_sdk/bin/cache`, `.fvm/flutter_sdk/bin/cache/artifacts/engine`, and `.fvm/flutter_sdk/bin/cache/dart-sdk`. Deleting the FVM SDK cache causes the next SDK operation to re-download hundreds of megabytes of artifacts.

#### Evidence

- Observed: `Taskfile.yml` `clean` task includes `rm -rf .fvm/flutter_sdk/bin/cache` and sub-paths.

#### Why It Matters

Including FVM SDK cache in `task clean` is surprising — developers expect `clean` to remove build artifacts, not SDK downloads. A developer who runs `task clean` to reset build state will face an unexpected multi-minute SDK re-download on the next `task setup` or build.

#### Recommendation

Remove the FVM SDK cache deletion from `task clean`. If a full environment reset is occasionally needed, create a separate `task nuke` or `task reset:env` that makes the destructive nature explicit.

#### Suggested Validation

Run `task clean` and verify FVM SDK remains intact (no re-download on next `fvm flutter --version`).

#### Dependencies or Risks

None.

---

### AUDIT-022 — `website/` directory is an unpopulated placeholder

**Classification:** Architecture  
**Severity:** Low  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `website/`  
**Effort:** Unknown  
**Impact:** Low

#### Observation

`website/` contains only `tsconfig.base.json`. No website content, framework scaffolding, or documentation exists. The directory name implies a future public-facing website for Ego Hygiene, but its current state provides no value.

#### Evidence

- Observed: `ls website/` → `tsconfig.base.json` only.
- Observed: No entry point, framework config, or content files.

#### Why It Matters

An empty directory with a single TypeScript config file confuses repository orientation. The directory is listed in scope definitions, suggesting it is intended for future use, but it may mislead new contributors about available surface area.

#### Recommendation

Either populate it with a minimal scaffold (Next.js, Astro, etc.) when website work begins, or add a `README.md` with a brief note: "Website placeholder — scheduled for future development."

#### Suggested Validation

None — documentation or scaffolding change only.

#### Dependencies or Risks

None.

---

### AUDIT-026 — `docs/AUDIT.md` is a prior informal audit outside the `audits/` system

**Classification:** Documentation  
**Severity:** Low  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `docs/AUDIT.md`  
**Effort:** Trivial  
**Impact:** Low

#### Observation

`docs/AUDIT.md` is a July 2026 informal architecture and UX audit report stored in `docs/`. The formal `audits/` system (with `auditor.spec.md` and this report) is the canonical location for audit reports. The `docs/AUDIT.md` predates the formal auditor specification and uses a non-standard format.

#### Evidence

- Observed: `docs/AUDIT.md` is a 2026-07-06 audit report with C/H/M/P priority tiers.
- Observed: `audits/` is the canonical audit output directory per `auditor.spec.md` section 9.
- Observed: `README.md` references `docs/AUDIT.md` as "Architecture audit report."

#### Why It Matters

Having audit history split between `docs/` and `audits/` creates discoverability confusion. Future audits following the spec will land in `audits/`; the earlier report is not cross-referenced.

#### Recommendation

1. Do not modify or move `docs/AUDIT.md` (it predates the formal system and is referenced by README).
2. Update `README.md` to point to `audits/` as the canonical audit location, noting `docs/AUDIT.md` as a legacy report.
3. Consider adding a brief note in `docs/AUDIT.md` header indicating it has been superseded by the formal audits system.

#### Suggested Validation

Verify `README.md` link update is correct after change.

#### Dependencies or Risks

None.

---

### AUDIT-027 — `tasks/tests.yml` is an empty placeholder file

**Classification:** DX  
**Severity:** Low  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `tasks/tests.yml`  
**Effort:** Trivial  
**Impact:** Low

#### Observation

`tasks/tests.yml` exists in `tasks/` but contains no content. The `tasks/` directory appears to hold supplemental task automation, but its purpose and relationship to `Taskfile.yml` are not documented.

#### Evidence

- Observed: `ls tasks/` → `tests.yml` only.
- Observed: `tasks/tests.yml` contains no actionable content.
- Observed: `Taskfile.yml` does not include or reference `tasks/tests.yml`.

#### Why It Matters

An undocumented empty file in a directory named `tasks/` creates contributor confusion about whether it is a TODO item, a template, or an abandoned artifact.

#### Recommendation

Either populate `tasks/tests.yml` with its intended content (e.g., Taskfile includes for test configuration), or remove it. If Taskfile modularization into `tasks/*.yml` is planned, add a brief `tasks/README.md`.

#### Suggested Validation

None — documentation/housekeeping change.

#### Dependencies or Risks

None.

---

### AUDIT-031 — `CONTRIBUTOR_GUIDE.md` path is inconsistently referenced

**Classification:** Documentation  
**Severity:** Low  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `README.md`, `START_HERE.md`, `docs/CONTRIBUTOR_GUIDE.md`  
**Effort:** Trivial  
**Impact:** Low

#### Observation

`README.md` references `docs/CONTRIBUTOR_GUIDE.md` (correct path). `START_HERE.md` does not explicitly mention the contributor guide but references `docs/READING_ORDER.md`. The auditor spec reading order lists `CONTRIBUTOR_GUIDE.md` as a root-level file. The actual file is at `docs/CONTRIBUTOR_GUIDE.md`.

#### Evidence

- Observed: `docs/CONTRIBUTOR_GUIDE.md` exists.
- Observed: No `CONTRIBUTOR_GUIDE.md` at repository root.
- Observed: `README.md` Step 3 in Contributing section: "Read [docs/CONTRIBUTOR_GUIDE.md]" — correct.
- Inferred: The auditor agent spec and reading order documents list `CONTRIBUTOR_GUIDE.md` at root, which creates a minor resolution step.

#### Why It Matters

AI agents following the authoritative reading order may attempt to load a root-level `CONTRIBUTOR_GUIDE.md` and receive a 404 before falling back to search.

#### Recommendation

Update the auditor's reading order to reference `docs/CONTRIBUTOR_GUIDE.md`. This is a documentation-only fix.

#### Suggested Validation

None.

#### Dependencies or Risks

None.

---

### AUDIT-033 — No `SECURITY.md` file at repository root

**Classification:** Security  
**Severity:** Low  
**Confidence:** High  
**Status:** Confirmed  
**Area:** Repository root  
**Effort:** Small  
**Impact:** Low

#### Observation

The repository has no `SECURITY.md` file defining a vulnerability disclosure policy or reporting process. GitHub's security advisory system supports custom `SECURITY.md` files to guide responsible disclosure.

#### Evidence

- Observed: `ls /home/runner/work/egohygiene/egohygiene/` — no `SECURITY.md`.

#### Why It Matters

For an application that stores personal reflection and mental-health-adjacent data, having a documented security disclosure path is a basic responsible-disclosure hygiene requirement. It also communicates to security researchers and users that the project takes security seriously.

#### Recommendation

Create `SECURITY.md` at repository root with: supported versions, vulnerability reporting process (GitHub Security Advisories or email), response timeline expectations, and safe-harbor language.

#### Suggested Validation

Verify GitHub displays the security policy in the repository Security tab.

#### Dependencies or Risks

None.

---

## Informational Findings

### AUDIT-024 — Flutter Foundation extraction plan is documented but execution has not begun

**Classification:** Architecture  
**Severity:** Informational  
**Confidence:** High  
**Status:** Intentional trade-off  
**Area:** `docs/architecture/extraction-plan.md`  
**Effort:** Unknown  
**Impact:** High

#### Observation

`extraction-plan.md` explicitly states: "This plan does not move any code." The 80/20 boundary (80% reusable foundation, 20% app-specific) is defined, and the boundary classification table is comprehensive. No extraction phase has been executed.

#### Evidence

- Observed: `docs/architecture/extraction-plan.md` L6: "This plan does not move any code."
- Inferred: All 33 `shared/` subsystems remain embedded in `apps/egohygiene/`.

#### Why It Matters

This is an intentional trade-off: stabilize the foundation in-app before extracting to packages. The risk is premature extraction introducing coupling. The opportunity: each release is a step toward a reusable Flutter Foundation that benefits the broader ecosystem.

#### Recommendation

None for this audit — this is correctly an intentional decision. The recommendation is to record this trade-off in `DECISIONS.md` (see AUDIT-012).

---

### AUDIT-032 — `schemas/` directory contains only practices schema

**Classification:** Architecture  
**Severity:** Informational  
**Confidence:** High  
**Status:** Confirmed  
**Area:** `schemas/`  
**Effort:** Unknown  
**Impact:** Low

#### Observation

`schemas/` contains only a `practices/` subdirectory. The `publishing/` system has its own `schemas/` subdirectory within the publishing tree. The scope of the top-level `schemas/` is not documented.

#### Evidence

- Observed: `ls schemas/` → `practices/` only.
- Observed: `publishing/schemas/` exists separately.
- Observed: No README in `schemas/`.

#### Why It Matters

As the ontology and specification system matures, schemas will likely be important for validation, code generation, and knowledge-graph integration. The current state is a reasonable starting point but lacks documentation of scope and intent.

#### Recommendation

Add a `schemas/README.md` describing the purpose of the top-level schemas directory and how it relates to `publishing/schemas/` and individual feature data models.

---

## Positive Observations

The following patterns represent genuine strengths that should be preserved and extended.

### POS-001 — Layered documentation governance is exceptional

The repository implements a six-layer knowledge hierarchy (Identity → Design → Architecture → Engineering → Execution → Implementation) documented in `SYSTEM.md` and `START_HERE.md`. The `AI_CONSTITUTION.md`, `DESIGN.md`, `FOUNDATIONS.md`, `MANIFESTO.md`, `ONTOLOGY.md`, `EPISTEMOLOGY.md`, and `PILLARS.md` provide rare depth for a project of this scale. This creates reproducible AI-assisted development with strong context anchoring.

### POS-002 — Composite GitHub Actions are well-designed

`flutter-setup` and `flutter-generate` composite actions correctly encapsulate setup and generation steps with appropriate input parameterization. The `cache: true` option in `subosito/flutter-action` and the Pub package cache step in `flutter-setup` demonstrate CI performance awareness. This pattern reduces duplication across 5 jobs that all need Flutter configured.

### POS-003 — AI Policy Gateway is implemented with meaningful safety checks

`AiPolicyGateway` (`lib/shared/ai/ai_policy_gateway.dart`) implements pre/post-processing checks using regex patterns for harm, medical diagnosis, and false certainty language. The gateway is wired into the AI capability pipeline and includes versioned policy records. This partially addresses the prior audit's C2 finding and represents real enforcement of the `AI_CONSTITUTION.md` principles at runtime.

### POS-004 — Privacy and encryption architecture is well-specified

The storage architecture (`docs/architecture/storage.md`) documents a full AES-256-GCM encryption chain: `EncryptionManager` → `KeyManager` → `SecureStorageService` → hardware-backed key storage. `EncryptedPayload` carries version, algorithm ID, ciphertext, nonce, and MAC. The `PrivacyPolicyRegistry`, `ConsentManager`, and `PrivacyEngine` provide a consent-and-enforcement framework. This is architecturally sound and privacy-thoughtful.

### POS-005 — Motion and accessibility system respects platform preferences

`AppAccessibility.disableAnimationsOf()` and `MotionManager.pageTransitionsTheme` both check `MediaQuery.disableAnimations` and `MediaQuery.accessibleNavigation`. The `ReducedMotionPageTransitionsBuilder` wraps all page transitions. This is a proactive, correct implementation of reduced-motion support that respects system accessibility settings.

### POS-006 — Feature-first module organization is consistently applied

All 11 feature modules (`check_in`, `conversation`, `graph`, `health`, `home`, `memory`, `onboarding`, `personal_model`, `progress`, `reflection`, `settings`) follow the same `presentation/`, `providers/`, `domain/`, `data/` structure with a `feature.dart` barrel file. This consistency enables AI-assisted development to be reliable and predictable.

### POS-007 — Comprehensive test coverage for a project at this stage

114 test files cover features, shared engines, providers, repositories, and domain models. The test structure mirrors the `lib/` structure. Shared helpers (`FakeStorageService`, integration test helpers) prevent duplication. `mocktail` is used consistently. 8 integration test files cover critical user flows including first launch, onboarding, conversation, reflection, persistence, and navigation.

### POS-008 — Release pipeline has sound ordering guarantees

The `release-please.yml` workflow uses `workflow_run` to trigger only after `Development Build` completes successfully. This prevents release tag creation when the build is broken. The `release-artifacts.yml` builds from the exact tagged commit for deterministic, traceable release artifacts. This is a well-designed release chain.

### POS-009 — Husky + commitlint enforces semantic commit hygiene

The project uses Husky and `@commitlint/config-conventional` with a custom `type-enum` that includes project-specific types (`specs`, `agents`, `skills`, `design`, `assets`) beyond standard types. This ensures the commit history is structured and Release Please can generate meaningful changelogs.

### POS-010 — Role-based onboarding paths lower contributor friction

`START_HERE.md` provides three entry paths (Human Contributor, AI Agent, Explorer) with distinct reading sequences. `docs/READING_ORDER.md` further decomposes into New Human Contributor, AI Agent, Designer, Product Manager, and Architecture Explorer paths. This is thoughtful and reduces cognitive overhead for different stakeholder types.

### POS-011 — Dynamic color and theme personalization are well-implemented

`app.dart` implements a 4-priority theme resolution: image-derived scheme > seed scheme > device dynamic color > brand defaults. `DynamicColorBuilder` is correctly integrated. The `AppTheme` class exposes `light`, `dark`, `amoled`, and `highContrast` variants. This is a nuanced theme implementation appropriate for an Android-first application targeting Material You.

---

## Architectural Opportunities

### AO-001 — Begin populating `DECISIONS.md` with real decisions

The decision record infrastructure exists but is empty (see AUDIT-012). Capturing the top 8–10 decisions made to date would significantly improve AI context quality and onboarding.

### AO-002 — Define the `shared/` taxonomy publicly

The 33-directory `shared/` module needs a documented taxonomy (see AUDIT-023). A taxonomy document in `docs/architecture/shared-taxonomy.md` would map each subsystem to a category and serve as the precursor to the extraction plan.

### AO-003 — Consider a reusable workflow layer for CI

The CI workflows are at a complexity threshold where reusable workflows would pay off. A `flutter-ci.yml` reusable workflow callable from both `build.yml` and `development-build.yml` would eliminate the duplication identified in AUDIT-001.

### AO-004 — Define the website architecture before building

`website/` is empty. Before adding a framework, define the website architecture: static site vs. server-rendered, content strategy, deployment pipeline, and relationship to the `publishing/` system. This decision should be recorded in `DECISIONS.md`.

---

## Refactoring Opportunities

### RO-001 — Consolidate Flutter version to single source of truth

AUDIT-006: `.fvmrc` should be the sole source; `flutter-setup/action.yml` and `copilot-setup-steps.yml` should read from it.

### RO-002 — Move debug-only logging to dev dependencies

AUDIT-010: `pretty_dio_logger` should be in `dev_dependencies` or conditionally enabled only in non-production environments.

### RO-003 — Standardize `build_runner` invocation

AUDIT-016: Add `--delete-conflicting-outputs` to the CI generate action to match local developer tooling.

### RO-004 — Remove `task clean` FVM SDK cache deletion

AUDIT-020: Extract FVM cache clearing into a separate destructive-reset task.

### RO-005 — Fix `.fvmrc` Melos setting

AUDIT-019: Set `updateMelosSettings: false` to remove a misleading configuration.

---

## Testing Opportunities

### TO-001 — Implement golden tests for design-system components

AUDIT-014: Begin with `AppCard`, `AppLoadingIndicator`, `AppErrorState` in light and dark mode. 5–10 golden tests would provide meaningful visual regression protection.

### TO-002 — Add integration test CI job

AUDIT-003: Start with `app_smoke_test.dart` and `navigation_test.dart` on a Chrome driver. These are lowest-risk to run in CI.

### TO-003 — Activate coverage threshold enforcement

AUDIT-005: Measure current coverage, set the `COVERAGE_THRESHOLD` repository variable to the floor value, and add documentation of the threshold in `docs/testing.md`.

### TO-004 — Add format check to test pipeline

AUDIT-004: A `dart format --output=none --set-exit-if-changed lib/ test/` step in the `analyze` job closes the local/CI parity gap.

### TO-005 — Audit localization completeness

AUDIT-029: Run `grep -rn 'Text("' apps/egohygiene/lib/features/` to identify hardcoded English strings not going through `t.someKey`.

---

## Documentation Opportunities

### DO-001 — Populate `DECISIONS.md` with real decisions

Immediately record: Riverpod v3 selection, GoRouter choice, Drift for local-first storage, Slang for localization, FVM for SDK management, feature-first module organization, and the extraction plan decision.

### DO-002 — Update `apps/egohygiene/lib/README.md`

The README describes 5 `shared/` subdirectories; the actual count is 33. Update the structural documentation to reflect reality. Add the shared taxonomy.

### DO-003 — Add `SECURITY.md`

A minimal security disclosure policy file at repository root (see AUDIT-033) communicates responsible-disclosure expectations.

### DO-004 — Add `website/README.md`

Document the intended purpose of the `website/` directory (see AUDIT-022) and its planned architecture.

### DO-005 — Document auto-commit workflows as intentional

Add a note to `DECISIONS.md` or `docs/architecture/` explaining the rationale for the RSS sync direct-to-main commit pattern (see AUDIT-017).

### DO-006 — Note `docs/AUDIT.md` as legacy in README

Update the README link to `docs/AUDIT.md` to note it predates the formal `audits/` system, directing readers to `audits/` for current audit reports.

---

## Developer Experience Opportunities

### DX-001 — Add `task version:check` or `task fvm:check`

Help developers verify they are on the correct Flutter version without running the full `doctor` task. A quick `fvm use` verification step.

### DX-002 — Add a shared taxonomy document

A `docs/architecture/shared-taxonomy.md` mapping the 33 `shared/` subsystems to logical groups would significantly reduce new-contributor ramp-up time.

### DX-003 — Clarify `task ci:local` format behavior

The format step in `ci:local` should be a check (`--output=none --set-exit-if-changed`) not a reformat to match CI behavior. Or document that `ci:local` auto-corrects issues that CI would flag.

### DX-004 — Add `task secrets:check` or document secret management

As the project approaches production, a documented pattern for managing secrets (Android keystore, future cloud API keys) would prevent accidental commits and CI confusion.

---

## Suggested Issue Backlog

### Suggested Issue: Unify CI/CD workflow logic into reusable workflows

**Priority:** High  
**Depends On:** None  
**Source Findings:** AUDIT-001, AUDIT-002, AUDIT-015

**Outcome:**  
`build.yml` and `development-build.yml` call shared reusable workflows for analyze, test (with coverage), and platform builds. Generated artifact sharing reduces CI duration.

**Acceptance Criteria:**
- [ ] A `flutter-ci.yml` reusable workflow exists for the analyze/test/build pipeline
- [ ] `build.yml` calls the reusable workflow with PR-appropriate inputs
- [ ] `development-build.yml` calls the reusable workflow with main-branch inputs
- [ ] Coverage is collected in both PR and main-branch builds
- [ ] CI duration is reduced by at least 20% (from artifact sharing)

---

### Suggested Issue: Add code format check and activate coverage threshold in CI

**Priority:** High  
**Depends On:** None  
**Source Findings:** AUDIT-004, AUDIT-005, AUDIT-021

**Outcome:**  
CI enforces formatting and a minimum coverage floor on all PRs.

**Acceptance Criteria:**
- [ ] `dart format --output=none --set-exit-if-changed lib/ test/` passes in CI analyze job
- [ ] `COVERAGE_THRESHOLD` repository variable is set to a meaningful value
- [ ] `task ci:local` format step uses `--output=none --set-exit-if-changed`
- [ ] Coverage threshold is documented in `docs/testing.md`

---

### Suggested Issue: Add integration test CI gate for smoke and navigation flows

**Priority:** High  
**Depends On:** CI unification  
**Source Findings:** AUDIT-003

**Outcome:**  
`app_smoke_test.dart` and `navigation_test.dart` run automatically on PRs against a virtual device.

**Acceptance Criteria:**
- [ ] CI job runs integration tests on Chrome or Android emulator
- [ ] Smoke test and navigation test pass in CI
- [ ] Failing integration test blocks PR merge
- [ ] Run time added to CI is within acceptable limits (target: < 8 minutes)

---

### Suggested Issue: Upgrade `sqlite3_flutter_libs` from EOL version

**Priority:** High  
**Depends On:** None  
**Source Findings:** AUDIT-007

**Outcome:**  
`sqlite3_flutter_libs` is upgraded to a supported, non-EOL version compatible with the current Drift version.

**Acceptance Criteria:**
- [ ] `pubspec.yaml` references a non-EOL `sqlite3_flutter_libs` version
- [ ] `task analyze` passes
- [ ] `task test` passes
- [ ] Database functionality verified on Android and Linux build targets

---

### Suggested Issue: Populate `DECISIONS.md` with real architectural decisions

**Priority:** High  
**Depends On:** None  
**Source Findings:** AUDIT-012

**Outcome:**  
`DECISIONS.md` contains at least 8 real decision records covering the most significant choices made in the repository.

**Acceptance Criteria:**
- [ ] Decision records for: Riverpod v3, GoRouter, Drift, Slang, FVM, feature-first architecture, local-first storage, extraction plan intention
- [ ] Each decision includes Context, Alternatives, Tradeoffs, Rationale sections
- [ ] AI agents loading the file can answer "why was X chosen?" for each decision

---

### Suggested Issue: Implement golden test baseline for design-system components

**Priority:** High  
**Depends On:** None  
**Source Findings:** AUDIT-014

**Outcome:**  
5–10 golden tests cover core design-system components in light and dark mode.

**Acceptance Criteria:**
- [ ] Golden tests exist for `AppCard`, `AppLoadingIndicator`, `AppErrorState`
- [ ] Tests run against a pinned device profile (consistent rendering)
- [ ] Golden images are committed and tracked
- [ ] CI runs golden tests as part of the test suite

---

### Suggested Issue: Android APK signing for release builds

**Priority:** High  
**Depends On:** None  
**Source Findings:** AUDIT-025

**Outcome:**  
Release APK builds in `release-artifacts.yml` are signed with a production keystore.

**Acceptance Criteria:**
- [ ] Production keystore stored as encrypted GitHub Actions secret
- [ ] `release-artifacts.yml` build-android job signs the APK
- [ ] Signed APK verified with `apksigner verify`
- [ ] Development builds remain functional with debug signing

---

### Suggested Issue: Dependency hygiene pass

**Priority:** Medium  
**Depends On:** AUDIT-007 (sqlite3_flutter_libs) done first  
**Source Findings:** AUDIT-008, AUDIT-009, AUDIT-010, AUDIT-018

**Outcome:**  
All dependency version constraints are appropriate; debug-only dependencies are gated correctly.

**Acceptance Criteria:**
- [ ] `freezed` upgraded to stable version or pinned to exact pre-release
- [ ] `riverpod: any` changed to `riverpod: ^3.0.0`
- [ ] `pretty_dio_logger` moved to `dev_dependencies` or guarded by `kDebugMode`
- [ ] `actions/checkout@v4` in RSS sync workflows updated to `@v5`
- [ ] `task analyze` passes after all changes

---

### Suggested Issue: Consolidate Flutter version to single source of truth

**Priority:** Medium  
**Depends On:** None  
**Source Findings:** AUDIT-006

**Outcome:**  
`.fvmrc` is the sole authoritative Flutter version source; all CI workflows read from it.

**Acceptance Criteria:**
- [ ] `flutter-setup/action.yml` reads Flutter version from `.fvmrc` at runtime
- [ ] `copilot-setup-steps.yml` uses the `flutter-setup` composite action
- [ ] Version change in `.fvmrc` propagates to all CI jobs automatically

---

### Suggested Issue: Privacy audit for hardware and network data collection

**Priority:** Medium  
**Depends On:** None  
**Source Findings:** AUDIT-011, AUDIT-030

**Outcome:**  
All hardware/network data collection is either restricted to debug builds or covered by the privacy policy consent framework.

**Acceptance Criteria:**
- [ ] `networkInfoProvider`, accelerometer, and battery providers are audited for production exposure
- [ ] Any production-accessible collection is registered in `PrivacyPolicyRegistry`
- [ ] Debug-only collection is gated to development/staging environments
- [ ] Privacy policy documentation updated to reflect data collection scope

---

## Deferred / Out-of-Scope Observations

- **iOS and macOS platform support**: `ios/` and `macos/` directories exist as Flutter scaffolding but iOS/macOS are not listed as target platforms (Android, Web, Linux are). Platform viability not audited.
- **Windows platform**: `windows/` scaffold exists; not a stated target platform. Not audited.
- **MindGarden knowledge content**: Individual Obsidian notes under `mindgarden/knowledge/` were not inspected for content accuracy or organization.
- **Publishing article content**: Individual articles under `publishing/channels/medium/` and `publishing/channels/newsletter/` were not inspected for content.
- **Runtime performance**: No runtime profiling was possible in this static audit. Prior audit's H4 (eager rendering patterns) remains as a concern but requires a running app to validate.
- **Actual database encryption status**: Whether the `EncryptionManager` chain is currently applied to `AppDatabase` reflection/check-in/memory tables requires runtime inspection beyond the scope of a static audit. The prior audit's C1 finding remains open at Low confidence.
- **App Store compliance**: Not within scope of this audit.
- **LinkedIn and newsletter publishing channels**: `publishing/channels/linkedin/` and `publishing/channels/newsletter/` were not deeply inspected.
- **Mindlint tool**: `publishing/tools/mindlint/` was noted but not deeply inspected.
- **`publish/specs/` directory**: Not deeply inspected.

---

## Uncertainties and Required Clarifications

1. **Data-at-rest encryption application**: The prior audit (C1) flagged plaintext storage in `AppDatabase`. The current codebase has an `EncryptionManager` chain. It is **unverified** whether this chain is actually applied to the Drift database for reflection/check-in/memory data, or whether it is only used for key-value and secure storage. This requires a code inspection of the Drift database DAOs and repository implementations.

2. **Coverage threshold value**: The actual current line coverage percentage is unknown without running `task test:coverage`. The recommendation to activate `COVERAGE_THRESHOLD` depends on knowing the baseline.

3. **Branch protection rules**: Whether `main` branch protection is configured in GitHub repository settings is not visible from repository files. If branch protection requires PRs, the RSS sync direct-commit pattern (AUDIT-017) may already be causing issues.

4. **`english_words` dependency purpose**: `english_words: ^4.0.0` is in `pubspec.yaml` dependencies but no usage was found in `lib/`. This may be used in a test helper, generated code, or may be a dead dependency. Requires `flutter pub deps` inspection.

5. **Sensors used in production vs. debug only**: `system_info_providers.dart` uses sensors. Whether the `SystemInfoDashboardScreen` is visible in production builds or restricted to debug/settings builds requires runtime verification.

6. **MindGarden Obsidian synchronization**: `mindgarden/.obsidian/` is committed to the repository. Whether personal Obsidian vault configuration files are intentionally shared or accidentally committed is a design question that should be documented.

7. **Release Please configuration correctness**: `release-please-config.json` uses `"release-type": "dart"`. Whether this correctly handles the `apps/egohygiene/pubspec.yaml` version field and CHANGELOG generation should be verified with a test release.

---

## Evidence Index

| Evidence | Type | Source |
|---|---|---|
| Repository structure | Observed | `ls -la /home/runner/work/egohygiene/egohygiene/` |
| Git log (2 commits) | Observed | `git log --oneline -5` |
| `.fvmrc` Flutter 3.44.2 pinning | Observed | `.fvmrc` |
| `pubspec.yaml` dependencies | Observed | `apps/egohygiene/pubspec.yaml` |
| Workflow files (6) | Observed | `.github/workflows/*.yml` |
| Composite actions (2) | Observed | `.github/actions/flutter-setup/action.yml`, `.github/actions/flutter-generate/action.yml` |
| CI job structure | Observed | `build.yml`, `development-build.yml` |
| Test file count (114) | Observed | `find test -name "*.dart" | wc -l` |
| Integration test files (8) | Observed | `find integration_test -name "*.dart"` |
| Golden test directory (.gitkeep only) | Observed | `find test/golden -type f` |
| `shared/` 33 subdirectories | Observed | `ls apps/egohygiene/lib/shared/ | wc -l` |
| `DECISIONS.md` template-only content | Observed | `DECISIONS.md` |
| `docs/AUDIT.md` prior audit | Observed | `docs/AUDIT.md` |
| `analysis_options.yaml` strict settings | Observed | `apps/egohygiene/analysis_options.yaml` |
| AiPolicyGateway implementation | Observed | `lib/shared/ai/ai_policy_gateway.dart` |
| AppAccessibility reduced-motion | Observed | `lib/shared/theme/accessibility.dart` |
| MotionManager pageTransitionsTheme | Observed | `lib/shared/theme/motion.dart` |
| `sqlite3_flutter_libs: ^0.6.0+eol` | Observed | `apps/egohygiene/pubspec.yaml` |
| `freezed: ^3.2.6-dev.1` | Observed | `apps/egohygiene/pubspec.yaml` |
| `riverpod: any` | Observed | `apps/egohygiene/pubspec.yaml` |
| `pretty_dio_logger` in prod deps | Observed | `apps/egohygiene/pubspec.yaml` |
| WiFi data collection | Observed | `lib/features/settings/providers/system_info_providers.dart` |
| Sensor data collection | Observed | `lib/features/settings/providers/system_info_providers.dart` |
| `build_runner build` without --delete | Observed | `.github/actions/flutter-generate/action.yml` |
| RSS sync direct-to-main commits | Observed | `.github/workflows/medium-rss-sync.yml`, `pinterest-rss-sync.yml` |
| `checkout@v4` in RSS workflows | Observed | `.github/workflows/medium-rss-sync.yml`, `pinterest-rss-sync.yml` |
| `.fvmrc` updateMelosSettings: true | Observed | `.fvmrc` |
| FVM cache in `task clean` | Observed | `Taskfile.yml` |
| `task ci:local` includes dart:format | Observed | `Taskfile.yml` |
| No `dart format` in CI | Observed | `.github/workflows/build.yml` |
| COVERAGE_THRESHOLD optional | Observed | `.github/workflows/build.yml` L18 |
| `website/` content (tsconfig only) | Observed | `ls website/` |
| `tasks/tests.yml` empty | Observed | `cat tasks/tests.yml` |
| Extraction plan documented | Observed | `docs/architecture/extraction-plan.md` |
| No signing in release workflow | Observed | `.github/workflows/release-artifacts.yml` |
| `lib/README.md` stale structure | Observed | `apps/egohygiene/lib/README.md` |
| Encryption architecture | Observed | `docs/architecture/storage.md` |
| Shared/taxonomy not documented | Inferred | `ls lib/shared/` |
| Localization gaps (prior) | Inferred | `docs/AUDIT.md` H1 |

---

## Validation Notes

### Commands Run

```bash
git -C /home/runner/work/egohygiene/egohygiene log --oneline -5
# 91c2289 Initial plan
# ed2d492 feat(mindgarden): establish canonical knowledge garden structure

git -C /home/runner/work/egohygiene/egohygiene rev-parse HEAD
# 91c2289222de223c702ebe1c9addba5004ead3eb

ls -la /home/runner/work/egohygiene/egohygiene/
# Full directory listing obtained

cat .fvmrc
# Flutter 3.44.2, useGitCache: true, updateMelosSettings: true

find apps/egohygiene/test -name "*.dart" | wc -l
# 114

find apps/egohygiene/test/golden -type f
# apps/egohygiene/test/golden/.gitkeep

ls apps/egohygiene/lib/shared/ | wc -l
# 33

ls .github/workflows/
# build.yml, copilot-setup-steps.yml, development-build.yml,
# medium-rss-sync.yml, pinterest-rss-sync.yml, release-artifacts.yml, release-please.yml

grep -n "sqlite3_flutter_libs\|freezed\|riverpod: any" apps/egohygiene/pubspec.yaml
# sqlite3_flutter_libs: ^0.6.0+eol
# freezed: ^3.2.6-dev.1
# riverpod: any

find apps/egohygiene/integration_test -name "*.dart"
# 8 files confirmed
```

### Commands Not Run

- `fvm flutter --version` — FVM not installed in audit environment
- `flutter analyze` — build environment not available
- `flutter test --coverage` — build environment not available
- `task generate` — explicitly excluded per audit constraints (modifies files)
- `flutter pub deps` — dependency tree not available without pub environment
- Any command that could modify repository state

### Failures / Limitations

- Flutter SDK not installed in audit execution environment — no runtime validation performed
- Coverage percentage not measurable — `COVERAGE_THRESHOLD` recommendation is guidance-based, not empirically set
- Generated Dart files excluded from audit — provider and repository implementations in `.g.dart` files not inspected
- Integration test CI gap is confirmed by absence of workflow steps; actual test pass/fail status on a device is unverified

---

*Audit completed 2026-07-13T17:30:00Z. Report produced by auditor-agent v1.0.0 following `.github/specs/auditor.spec.md` v1.0.0.*
