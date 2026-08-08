# TODO

> The current focus is **convergence**, not expansion.
>
> The goal is to reduce cognitive load, strengthen engineering quality, and
> stabilize Ego Hygiene into a reusable platform before expanding feature work.

---

# Current Phase

**Privacy & Security**

Status:

```
Foundation
    ✓

Architecture
    ✓

Features
    ◐

Convergence
    ✓

Documentation
    ✓

Testing
    ✓

Stabilization
    ○

Release v1
    ○

Flutter Foundation Extraction
    ○

Organization Bootstrap
    ○
```

---

# Guiding Philosophy

Every task should answer **yes** to at least one of these questions:

- Does this reduce cognitive load?
- Does this simplify the architecture?
- Does this improve the developer experience?
- Does this increase confidence?
- Does this reduce duplication?
- Does this strengthen the source of truth?

If not...

...it probably shouldn't be done yet.

---

# Phase 1 — Repository Stabilization ✓

Phase 1 is complete.

CI/CD, dependency hygiene, and developer tooling were stabilized:

- Unified CI into a single reusable workflow with code-generation caching, integration test pipeline, formatting enforcement, and consistent coverage collection and enforcement.
- Upgraded all dependencies to current stable versions: replaced the obsolete `sqlite3_flutter_libs` EOL shim, upgraded `freezed` to the stable `3.2.5` release, pinned `riverpod` to `^3.0.0`, and moved `pretty_dio_logger` to dev-only.
- Standardized all GitHub Action versions to `@v5`.
- Removed obsolete `updateMelosSettings` from FVM configuration.
- Separated `task clean` (lightweight) from `task reset` (destructive, removes FVM SDK cache).

---

# Phase 2 — Repository Convergence ✓

Phase 2 is complete.

Architectural convergence work completed:

- Documented a canonical Shared module taxonomy and ownership boundary in `apps/egohygiene/lib/shared/README.md`.
- Reduced Shared discovery friction by linking taxonomy from `apps/egohygiene/lib/README.md`, `README.md`, `docs/architecture/overview.md`, and `docs/REPOSITORY_MAP.md`.
- Refreshed architecture entry points by adding root `ARCHITECTURE.md` and `SYSTEM.md` index documents that point to canonical sources.
- Clarified placeholder purpose and ownership for `website/` in `website/README.md`.
- Clarified `schemas/` ownership, scope boundaries, and evolution guidance in `schemas/README.md`.

---

# Phase 3 — Documentation ✓

Phase 3 is complete.

Documentation is now the authoritative source of truth for contributors, AI agents, and maintainers:

- Populated [`DECISIONS.md`](.engineering/architecture/DECISIONS.md) with 13 recorded architectural decisions covering all major technology and architecture choices (ADR-001 through ADR-013).
- Created [`SECURITY.md`](SECURITY.md) at the repository root with a private vulnerability disclosure policy, safe-harbor language, and scope definitions.
- Created [`audits/`](audits/) as the canonical location for future audit reports, with `audits/README.md` documenting the audit lifecycle and finding-to-issue workflow.
- Preserved [`docs/AUDIT.md`](docs/AUDIT.md) as a clearly labeled legacy artifact.
- Created [`docs/architecture/publishing-automation.md`](docs/architecture/publishing-automation.md) documenting the Medium and Pinterest sync workflows end-to-end.
- Updated [`README.md`](README.md), [`docs/READING_ORDER.md`](docs/READING_ORDER.md) with links to new canonical documentation.

---

# Phase 4 — Testing ✓

Testing maturity and quality assurance pass is complete.

Confidence was increased through:

- **Golden test baseline established** — Visual regression tests cover `AppCard`, `AppLoadingIndicator`, `AppErrorState`, and `AppEmptyState` across all four theme variants (light, dark, AMOLED, high-contrast). Reference images are committed to `apps/egohygiene/test/goldens/`. See `docs/testing.md` for the update-goldens workflow.
- **Integration testing reviewed** — Eight integration tests cover the full user lifecycle (smoke, first-launch, onboarding, navigation, reflection, conversation, settings, restart-persistence). CI runs the highest-value subset (`app_smoke_test` + `navigation_test`) on every PR.
- **Localization audit completed** — Hardcoded user-facing strings in `update_experience_screen.dart`, `system_info_dashboard_screen.dart`, `update_section_widgets.dart`, `update_shared_widgets.dart`, and `context_permission_card.dart` were migrated to the slang localization framework. New keys added under `updateExperienceScreen`, `updateSectionWidgets`, `debugCenterScreen.systemInfo`, and `common.openSettings`.
- **Localization validation test added** — `test/shared/localization/localization_completeness_test.dart` validates that all key localization strings resolve correctly and that interpolated keys produce non-empty results.
- **Testing documentation refreshed** — `docs/testing.md` and `docs/architecture/testing.md` document the golden test workflow, update-goldens procedure, CI expectations, and the `TranslationProvider` convention for widget tests.
- **Taskfile updated** — `task test:golden` and `task test:golden:update` provide one-command golden test execution and regeneration.

---

# Phase 5 — Privacy & Security (Active)

Goal:

Ensure implementation matches the project's privacy-first philosophy.

- [ ] Audit hardware permissions
- [ ] Audit network metadata collection
- [ ] Verify encryption implementation
- [ ] Configure Android signing
- [ ] Review privacy documentation

---

# Phase 6 — Flutter Foundation

Goal:

Prepare reusable infrastructure for extraction.

- [ ] Continue convergence
- [ ] Identify reusable packages
- [ ] Extract shared infrastructure
- [ ] Validate package boundaries

---

# Phase 7 — Ego Hygiene v1

Goal:

Ship a polished, stable first release.

- [ ] Complete stabilization
- [ ] Complete testing
- [ ] Complete documentation
- [ ] Final release audit
- [ ] Publish v1

---

# Future

After v1:

- Flutter Foundation
- Incompris LLC Platform
- Grant Proposal
- Research
- Additional applications

---

# Notes

This file intentionally prioritizes **quality over quantity**.

The objective is not to finish every task as quickly as possible.

The objective is to continuously make the repository simpler, clearer, and easier to evolve.
