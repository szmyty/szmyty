# Staging Migration Ledger

**Stable queue key:** `szmyty-profile-rebuild-15`
**Epic:** szmyty/szmyty#65
**Closes:** szmyty/szmyty#80

This document is the single source of truth for every `.staging` artifact
decision.  It is seeded from the reconstruction epic audit matrix and the
public-data security audit in `docs/audits/public-data-security-audit.md`.
Do **not** replace it with `.staging/docs/reference-inventory.md` without a
fresh review, as that file reflects an older, pre-privacy-policy analysis.

---

## Decision key

| Code | Meaning |
|------|---------|
| `ADOPT` | Use substantially as-is with minor path or reference adjustments. |
| `MERGE` | Combine selected content with another source into a unified artifact. |
| `REWRITE` | Retain the idea but replace implementation / content entirely. |
| `REGENERATE` | Create new production assets from the design intent only. |
| `DEFER` | Preserve an explicit future decision; no production use now. |
| `ARCHIVE` | Retain only as historical evidence outside the production tree. |
| `DISCARD` | Intentionally remove; no production value. |
| `PURGE` | Remove because it is sensitive or unsafe for public publication. |

---

## Privacy status key

| Code | Meaning |
|------|---------|
| `PUBLIC` | Safe to include in the production repository and profile. |
| `SENSITIVE` | Contains personal, biometric, or location data; must not be published. |
| `TEMPLATE` | Structural template only; values must be reviewed before promotion. |
| `INTERNAL` | Developer notes / draft material; not ready for public consumption. |

---

## Completion evidence key

Leave blank until the row is actioned.  Use `issue#N`, `commit:<sha>`,
or `promoted:<target-path>` once complete.

---

## Top-level `.staging` families

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 1 | `.staging/README.md` | `MERGE` | `README.md` | Primary candidate README variant; hero, badges, DX sections are reusable. Must be merged with content from README2.md and README3.md after evidence verification. | `INTERNAL` | issue#80 |
| 2 | `.staging/README2.md` | `MERGE` | `README.md` | Alternative variant with additional project table and principles sections; merge selected content into production README. | `INTERNAL` | issue#80 |
| 3 | `.staging/README3.md` | `MERGE` | `README.md` | Cleaner metrics-dashboard variant; metrics layout is a strong candidate for adoption. | `INTERNAL` | issue#80 |
| 4 | `.staging/AGENTS.md` | `REWRITE` | `AGENTS.md` | Contains project-level agent guidance; superseded by the production `AGENTS.md` but source content is useful as a reference. Rewrite production file from both versions. | `INTERNAL` | issue#80 |
| 5 | `.staging/CHANGELOG.md` | `DISCARD` | — | Changelog tracks changes to the experimental profile repository, not to production. Not appropriate to promote. | `INTERNAL` | issue#80 |
| 6 | `.staging/CONTRIBUTING.md` | `ADOPT` | `CONTRIBUTING.md` | Standard contributing guide; content is generic and safe to adopt with minor updates. | `PUBLIC` | issue#80 |
| 7 | `.staging/CONTRIBUTING copy.md` | `DISCARD` | — | Accidental duplicate file; redundant copy of `CONTRIBUTING.md`. | `INTERNAL` | issue#80 |
| 8 | `.staging/PLAN.md` | `ARCHIVE` | `docs/audits/` | Detailed engineering plan for the staging build; valuable as a historical audit artifact but not for production promotion. | `INTERNAL` | issue#80 |
| 9 | `.staging/PULL_REQUEST_SUMMARY.md` | `DISCARD` | — | Internal PR summary created during staging development; not relevant to production. | `INTERNAL` | issue#80 |
| 10 | `.staging/VERSION` | `DISCARD` | — | Version pinned to the staging repository lifecycle; production versioning is managed via `pyproject.toml`. | `INTERNAL` | issue#80 |
| 11 | `.staging/.pre-commit-config.yaml` | `ADOPT` | `.pre-commit-config.yaml` | Pre-commit hooks configuration; evaluate hooks for compatibility, then adopt or merge with existing configuration. | `PUBLIC` | issue#80 |
| 12 | `.staging/.secrets.example` | `ADOPT` | `.secrets.example` | Safe template showing required secret names without values; useful onboarding reference. | `TEMPLATE` | issue#80 |
| 13 | `.staging/package.json` | `DEFER` | szmyty/szmyty#65 | Node.js package configuration for the dashboard app; defer until dashboard decision is made. | `INTERNAL` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |
| 14 | `.staging/pyproject.toml` | `MERGE` | `pyproject.toml` | Alternative Python project configuration; compare dependency groups and tool settings with production `pyproject.toml`; merge selected additions. | `INTERNAL` | issue#80 |
| 15 | `.staging/pyproject2.toml` | `DISCARD` | — | Duplicate / scratch variant of `pyproject.toml`; no unique content. | `INTERNAL` | issue#80 |
| 16 | `.staging/requirements.txt` | `DISCARD` | — | Flat requirements file superseded by Poetry-managed `pyproject.toml`. | `INTERNAL` | issue#80 |
| 17 | `.staging/requirements-dev.txt` | `DISCARD` | — | Dev requirements file superseded by Poetry dependency groups. | `INTERNAL` | issue#80 |
| 18 | `.staging/profile.code-workspace` | `DISCARD` | — | VS Code workspace file scoped to the staging repository; not relevant to production. | `INTERNAL` | issue#80 |
| 19 | `.staging/dashboard.svg` | `PURGE` | — | Generated SVG dashboard containing live metrics; may embed location or biometric data. Do not publish. | `SENSITIVE` | issue#80 |
| 20 | `.staging/dashboard-dark.svg` | `PURGE` | — | Dark-mode variant of the generated dashboard SVG; same privacy risk as `dashboard.svg`. | `SENSITIVE` | issue#80 |
| 21 | `.staging/dashboard-light.svg` | `PURGE` | — | Light-mode variant; same privacy risk. | `SENSITIVE` | issue#80 |
| 22 | `.staging/dashboard-interactive.svg` | `PURGE` | — | Interactive SVG dashboard; may embed live or historical biometric/location data. | `SENSITIVE` | issue#80 |
| 23 | `.staging/github-metrics.svg` | `DEFER` | szmyty/szmyty#65 | Legacy combined GitHub metrics SVG; regenerate via `lowlighter/metrics` workflow instead of committing a stale copy. | `PUBLIC` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |
| 24 | `.staging/metrics.plugin.16personalities.svg` | `PURGE` | — | Personality-type plugin output; personal psychometric data; must not be published. | `SENSITIVE` | issue#80 |
| 25 | `.staging/summary-monthly.svg` | `DEFER` | szmyty/szmyty#65 | Monthly summary card; regenerate rather than promote stale artifact. | `PUBLIC` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |
| 26 | `.staging/summary-weekly.svg` | `DEFER` | szmyty/szmyty#65 | Weekly summary card; same as monthly. | `PUBLIC` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |

---

## `.staging/.github` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 27 | `.staging/.github/GOVERNANCE.md` | `ADOPT` | `.github/GOVERNANCE.md` | Generic governance document; safe to adopt. | `PUBLIC` | issue#80 |
| 28 | `.staging/.github/dependabot.yml` | `ADOPT` | `.github/dependabot.yml` | Dependabot configuration; evaluate intervals and adopt. | `PUBLIC` | promoted:.github/dependabot.yml |
| 29 | `.staging/.github/workflows/` | `REWRITE` | `.github/workflows/` | Workflow files are tightly coupled to staging repository layout and hardcoded secrets; rewrite for production with portable context variables. | `INTERNAL` | promoted:.github/workflows/{ci.yml,update-profile.yml,pages.yml} |
| 30 | `.staging/.github/actions/` | `DEFER` | szmyty/szmyty#65 | Custom composite actions; evaluate individual actions and defer until workflows are rebuilt. | `INTERNAL` | issue#77 |
| 31 | `.staging/.github/instructions/` | `ARCHIVE` | `docs/audits/` | Copilot instruction files specific to the staging development process; not needed in production. | `INTERNAL` | issue#80 |

---

### Detailed workflow inventory for issue `#77`

| Source path | Decision | Production mapping | Notes |
|-------------|----------|--------------------|-------|
| `.staging/.github/workflows/build-profile.yml` | `REWRITE` | `ci.yml`, `update-profile.yml`, `pages.yml` | Split validation, scheduled refresh, and Pages deployment into separate least-privilege workflows. |
| `.staging/.github/workflows/tests.yml` | `MERGE` | `ci.yml` | Fold Python test coverage into the read-only validation workflow. |
| `.staging/.github/workflows/lint.yml` | `MERGE` | `ci.yml` | Fold YAML/Python linting into the read-only validation workflow. |
| `.staging/.github/workflows/update-readme.yml` | `MERGE` | `update-profile.yml` | Replace README mutation with the current Python module pipeline. |
| `.staging/.github/workflows/activity.yml` | `MERGE` | `update-profile.yml` | Retain public-activity refresh through `tools.modules.recent_activity`. |
| `.staging/.github/workflows/github-stats.yml` | `MERGE` | `update-profile.yml` | Retain public GitHub metrics refresh through `tools.modules.github_metrics`. |
| `.staging/.github/workflows/metrics.yml` | `DISCARD` | — | No active production asset consumes the staged lowlighter metrics workflow. |
| `.staging/.github/workflows/profile-summary-cards.yml` | `DISCARD` | — | No active production asset consumes the staged summary-card workflow. |
| `.staging/.github/workflows/monitoring.yml` | `DISCARD` | — | Routine incident and issue automation is intentionally omitted from the production set. |
| `.staging/.github/workflows/health.yml` | `DISCARD` | — | Health monitoring for staged services is out of scope for the public profile repository. |
| `.staging/.github/workflows/release.yml` | `DISCARD` | — | Release automation is unrelated to profile validation, refresh, or Pages deployment. |
| `.staging/.github/workflows/greetings.yml` | `DISCARD` | — | Contributor greeting automation is unrelated to the target workflow set. |
| `.staging/.github/workflows/test-engine.yml` | `DISCARD` | — | Staged engine test harness was superseded by production `pytest` coverage. |
| `.staging/.github/workflows/test-individual-actions.yml` | `DISCARD` | — | Local composite-action tests are unnecessary after consolidating on first-party workflows. |
| `.staging/.github/workflows/act-demo.yml` | `DISCARD` | — | Best-effort `act` guidance is documented, but no separate demo workflow is retained. |
| `.staging/.github/workflows/all-contributors.yml` | `DISCARD` | — | Contributor management is unrelated to the target workflow set. |

### Detailed composite-action inventory for issue `#77`

| Source path | Decision | Production mapping | Notes |
|-------------|----------|--------------------|-------|
| `.staging/.github/actions/setup/action.yml` | `DISCARD` | — | Replaced by pinned `actions/setup-python` plus Poetry installs. |
| `.staging/.github/actions/setup-engine/action.yml` | `DISCARD` | — | Staged engine setup is superseded by the production Python toolchain. |
| `.staging/.github/actions/setup-environment/action.yml` | `DISCARD` | — | Replaced by pinned `actions/setup-python` plus Poetry installs. |
| `.staging/.github/actions/pip-install/action.yml` | `DISCARD` | — | Replaced by Poetry with lockfile-based caching. |
| `.staging/.github/actions/update-readme/action.yml` | `REWRITE` | `update-profile.yml` | Replaced by `python -m tools.modules.update_readme`. |
| `.staging/.github/actions/deploy-pages/action.yml` | `REWRITE` | `pages.yml` | Replaced by official Pages actions in a dedicated deployment workflow. |
| `.staging/.github/actions/fetch-developer/action.yml` | `DISCARD` | — | Developer dashboard data is not part of the active public profile pipeline. |
| `.staging/.github/actions/engine-fetch-developer/action.yml` | `DISCARD` | — | Staged engine fetch path is superseded by production tooling. |
| `.staging/.github/actions/generate-developer-dashboard/action.yml` | `DISCARD` | — | Developer dashboard SVG generation is not retained in production. |
| `.staging/.github/actions/engine-generate-developer-dashboard/action.yml` | `DISCARD` | — | Staged engine dashboard generation is superseded by production tooling. |
| `.staging/.github/actions/fetch-location/action.yml` | `DISCARD` | — | Location automation remains excluded for privacy reasons. |
| `.staging/.github/actions/generate-location-card/action.yml` | `DISCARD` | — | Location card generation remains excluded for privacy reasons. |
| `.staging/.github/actions/fetch-weather/action.yml` | `DISCARD` | — | Weather automation remains excluded from the production profile scope. |
| `.staging/.github/actions/generate-weather-card/action.yml` | `DISCARD` | — | Weather card generation remains excluded from the production profile scope. |
| `.staging/.github/actions/fetch-oura/action.yml` | `DISCARD` | — | Oura and health automation remains excluded for privacy reasons. |
| `.staging/.github/actions/generate-oura-dashboard/action.yml` | `DISCARD` | — | Oura and health automation remains excluded for privacy reasons. |
| `.staging/.github/actions/generate-oura-mood/action.yml` | `DISCARD` | — | Oura and health automation remains excluded for privacy reasons. |
| `.staging/.github/actions/fetch-soundcloud/action.yml` | `DISCARD` | — | Replaced by the hand-authored `music-highlight` input file. |
| `.staging/.github/actions/generate-soundcloud-card/action.yml` | `DISCARD` | — | SoundCloud card generation is replaced by the current README module template. |
| `.staging/.github/actions/fetch-quote/action.yml` | `DISCARD` | — | Quote automation is not part of the active public profile pipeline. |
| `.staging/.github/actions/generate-quote-card/action.yml` | `DISCARD` | — | Quote card generation is not part of the active public profile pipeline. |
| `.staging/.github/actions/optimize-svgs/action.yml` | `DISCARD` | — | No active generated SVG workflow requires a retained optimizer action. |

---

## `.staging/assets` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 32 | `.staging/assets/branding/` | `ADOPT` | `assets/branding/` | SVG branding assets (header, footer, logo); adopt as-is with path corrections. | `PUBLIC` | issue#80 |
| 33 | `.staging/assets/icons/` | `ADOPT` | `assets/icons/` | Icon assets; adopt if referenced by production README or site. | `PUBLIC` | issue#80 |
| 34 | `.staging/assets/images/` | `DEFER` | szmyty/szmyty#65 | Image assets; review individually before promotion. | `PUBLIC` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |

---

## `.staging/branding` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 35 | `.staging/branding/` | `ADOPT` | `assets/branding/` | Root-level branding directory mirrors `assets/branding/`; consolidate into `assets/branding/` at production. | `PUBLIC` | issue#80 |
| 36 | `.staging/branding/badges/` | `ADOPT` | `assets/branding/badges/` | Custom badge SVGs; safe to adopt. | `PUBLIC` | issue#80 |

---

## `.staging/dashboard-app` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 37 | `.staging/dashboard-app/` | `ARCHIVE` | szmyty/szmyty#76, ADR 0002 | React/TypeScript Vite dashboard; rejected in favour of plain HTML/CSS `site/` companion (see ADR 0002). Retained as historical evidence only. | `INTERNAL` | issue#76, promoted:site/ |

---

## `.staging/data` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 38 | `.staging/data/metrics/` | `PURGE` | — | Generated metrics JSON; may contain location, health, or usage data. Do not publish. | `SENSITIVE` | issue#80 |
| 39 | `.staging/data/mock/` | `ADOPT` | `profile/fixtures/` | Mock data for testing; safe to adopt as test fixtures after review. | `PUBLIC` | issue#80 |
| 40 | `.staging/data/quotes/` | `ADOPT` | `profile/content/quotes/` | Quote data files; safe to adopt. | `PUBLIC` | issue#80 |
| 41 | `.staging/data/snapshots/` | `PURGE` | — | Snapshot JSON files may contain biometric or location data; purge entirely. | `SENSITIVE` | issue#80 |
| 42 | `.staging/data/status/` | `DEFER` | szmyty/szmyty#65 | Status data files; review individually before promotion. | `INTERNAL` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |

---

## `.staging/developer` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 43 | `.staging/developer/` | `DEFER` | szmyty/szmyty#65 | Developer-specific configuration or scripts; review before promotion. | `INTERNAL` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |

---

## `.staging/docs` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 44 | `.staging/docs/ARCHITECTURE.md` | `MERGE` | `docs/ARCHITECTURE.md` | Architecture documentation; merge selected content into the production architecture doc. | `PUBLIC` | issue#80 |
| 45 | `.staging/docs/DESIGN.md` | `ARCHIVE` | `docs/audits/` | Design notes from the staging build; retain as an audit artifact. | `INTERNAL` | issue#80 |
| 46 | `.staging/docs/MIGRATION.md` | `DISCARD` | — | Staging migration procedure for promoting staging into production; superseded by this production-side ledger. | `INTERNAL` | issue#80 |
| 47 | `.staging/docs/ROADMAP.md` | `MERGE` | `docs/ROADMAP.md` | Staging roadmap; merge near-term items with the production roadmap. | `INTERNAL` | issue#80 |
| 48 | `.staging/docs/MODULES.md` | `DEFER` | szmyty/szmyty#65 | Module documentation; defer until production modules are established. | `INTERNAL` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |
| 49 | `.staging/docs/WORKFLOWS.md` | `MERGE` | `docs/ARCHITECTURE.md` | Workflow documentation; fold relevant content into the architecture doc. | `INTERNAL` | issue#80 |
| 50 | `.staging/docs/MONITORING.md` | `DEFER` | szmyty/szmyty#65 | Monitoring documentation; defer until production observability is established. | `INTERNAL` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |
| 51 | `.staging/docs/TROUBLESHOOTING.md` | `DEFER` | szmyty/szmyty#65 | Troubleshooting guide; defer until production services are running. | `INTERNAL` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |
| 52 | `.staging/docs/reference-inventory.md` | `ARCHIVE` | `docs/audits/` | Older reference inventory; superseded by this ledger; retain as an audit artifact. | `INTERNAL` | issue#80 |
| 53 | `.staging/docs/style-guide.md` | `ADOPT` | `docs/style-guide.md` | Markdown/content style guide; safe to adopt. | `PUBLIC` | issue#80 |
| 54 | `.staging/docs/suggestions.md` | `ARCHIVE` | `docs/audits/` | Internal brainstorming notes; not suitable for production. | `INTERNAL` | issue#80 |
| 55 | `.staging/docs/cards.md` | `DEFER` | szmyty/szmyty#65 | Card design notes; defer until production card system is established. | `INTERNAL` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |
| 56 | `.staging/docs/markdown_valid_elements.md` | `ADOPT` | `docs/markdown_valid_elements.md` | Reference for valid GitHub-rendered Markdown elements; safe to adopt. | `PUBLIC` | issue#80 |
| 57 | `.staging/docs/ENGINE_ARCHITECTURE.md` | `ARCHIVE` | `docs/audits/` | Engine architecture notes specific to the staging profile engine. | `INTERNAL` | issue#80 |
| 58 | `.staging/docs/MODULAR_ARCHITECTURE.md` | `ARCHIVE` | `docs/audits/` | Modular architecture notes; staging-specific. | `INTERNAL` | issue#80 |
| 59 | `.staging/docs/LOCAL_DEVELOPMENT.md` | `DEFER` | szmyty/szmyty#65 | Local development guide; defer until production tooling is settled. | `INTERNAL` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |
| 60 | `.staging/docs/RELEASES.md` | `DISCARD` | — | Staging release notes; not relevant to production. | `INTERNAL` | issue#80 |
| 61 | `.staging/docs/OPTIMIZATION_GUIDE.md` | `ARCHIVE` | `docs/audits/` | Staging-specific optimisation notes. | `INTERNAL` | issue#80 |
| 62 | `.staging/docs/CACHING_BENCHMARKS.md` | `ARCHIVE` | `docs/audits/` | Caching benchmark results from staging engine; not portable to production without re-measurement. | `INTERNAL` | issue#80 |
| 63 | `.staging/docs/CACHING_QUICK_REFERENCE.md` | `ARCHIVE` | `docs/audits/` | Quick reference for staging caching system. | `INTERNAL` | issue#80 |
| 64 | `.staging/docs/WORKFLOW_CACHING.md` | `ARCHIVE` | `docs/audits/` | Workflow caching notes; staging-specific. | `INTERNAL` | issue#80 |
| 65 | `.staging/docs/API_RESILIENCE.md` | `ARCHIVE` | `docs/audits/` | API resilience notes for the staging engine. | `INTERNAL` | issue#80 |
| 66 | `.staging/docs/API_TIMEOUT_RETRY_GUIDE.md` | `ARCHIVE` | `docs/audits/` | Retry and timeout guide for the staging engine. | `INTERNAL` | issue#80 |
| 67 | `.staging/docs/INTEGRATION_EXAMPLE.md` | `ARCHIVE` | `docs/audits/` | Integration example for the staging engine. | `INTERNAL` | issue#80 |
| 68 | `.staging/docs/SVG_SANITIZATION.md` | `ADOPT` | `docs/SVG_SANITIZATION.md` | SVG sanitisation guidelines; relevant to production card generation. | `PUBLIC` | issue#80 |
| 69 | `.staging/docs/ROBUSTNESS_IMPROVEMENTS.md` | `ARCHIVE` | `docs/audits/` | Robustness notes specific to the staging engine implementation. | `INTERNAL` | issue#80 |
| 70 | `.staging/docs/README_LAYOUT_BEFORE_AFTER.md` | `ARCHIVE` | `docs/audits/` | Before/after layout diff; historical reference only. | `INTERNAL` | issue#80 |
| 71 | `.staging/docs/README_LAYOUT_CHANGELOG.md` | `ARCHIVE` | `docs/audits/` | Layout changelog; staging history only. | `INTERNAL` | issue#80 |
| 72 | `.staging/docs/README_SECTION_CHANGES.md` | `ARCHIVE` | `docs/audits/` | Section change notes; staging history only. | `INTERNAL` | issue#80 |
| 73 | `.staging/docs/LOCATION_CARD_CHANGES.md` | `PURGE` | — | Location card change log may contain location data references; purge. | `SENSITIVE` | issue#80 |
| 74 | `.staging/docs/UNIFIED_WORKFLOW_MIGRATION.md` | `ARCHIVE` | `docs/audits/` | Unified workflow migration notes; staging-specific. | `INTERNAL` | issue#80 |

---

## `.staging/engine` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 75 | `.staging/engine/profile_engine/` | `ARCHIVE` | szmyty/szmyty#74 | Staged Python profile engine replaced by `tools/profile_builder/`. Proven invariants (atomic writes, change detection, SVG sanitization, Pydantic models) were recovered or deliberately deferred per ADR 0001. Retain as historical evidence only. | `PUBLIC` | szmyty/szmyty#74 |
| 76 | `.staging/engine/tests/` | `ARCHIVE` | szmyty/szmyty#74 | Engine test suite; superseded by `tests/test_profile_builder_*.py`. Retain as historical evidence only. | `PUBLIC` | szmyty/szmyty#74 |

---

## `.staging/footer` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 77 | `.staging/footer/footer.html` | `ADOPT` | `assets/footer/footer.html` | HTML footer template; safe to adopt. | `PUBLIC` | issue#80 |
| 78 | `.staging/footer/README.md` | `ADOPT` | `assets/footer/README.md` | Footer documentation; safe to adopt. | `PUBLIC` | issue#80 |

---

## `.staging/location` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 79 | `.staging/location/` | `PURGE` | — | Precise geographic location data; confirmed by public-data security audit. Must not be published. | `SENSITIVE` | issue#80 |

---

## `.staging/metrics` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 80 | `.staging/metrics/` | `REGENERATE` | `metrics/` | Metrics SVGs should be regenerated by the production `lowlighter/metrics` workflow rather than promoted as stale artifacts. Directory structure can inform workflow output paths. | `PUBLIC` | issue#80 |

---

## `.staging/models` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 81 | `.staging/models/` | `DEFER` | szmyty/szmyty#65 | Placeholder directory (`.gitkeep` only); defer until model definitions are needed. | `INTERNAL` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |

---

## `.staging/oura` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 82 | `.staging/oura/` | `PURGE` | — | Biometric health data from Oura ring; confirmed by public-data security audit. Must not be published under any circumstances. | `SENSITIVE` | issue#80 |

---

## `.staging/profile-summary-card-output` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 83 | `.staging/profile-summary-card-output/` | `REGENERATE` | `profile-summary-card-output/` | Theme-variant profile summary card SVGs; regenerate via the production `profile-summary-cards.yml` workflow rather than promoting stale copies. | `PUBLIC` | issue#80 |

---

## `.staging/quotes` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 84 | `.staging/quotes/` | `ADOPT` | `profile/content/quotes/` | Quote data files at root level; consolidate with `data/quotes/` and adopt. | `PUBLIC` | issue#80 |

---

## `.staging/schemas` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 85 | `.staging/schemas/weather.schema.json` | `DEFER` | szmyty/szmyty#65 | Weather data schema; defer until weather integration is considered for production. | `PUBLIC` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |
| 86 | `.staging/schemas/developer-stats.schema.json` | `ADOPT` | `schemas/developer-stats.schema.json` | Developer statistics schema; safe to adopt and use for metrics validation. | `PUBLIC` | issue#80 |
| 87 | `.staging/schemas/health-snapshot.schema.json` | `PURGE` | — | Health/biometric snapshot schema; even the schema reveals the data shape of private health data. Purge to avoid inference. | `SENSITIVE` | issue#80 |
| 88 | `.staging/schemas/soundcloud-track.schema.json` | `DEFER` | szmyty/szmyty#65 | SoundCloud track schema; defer until music integration decision. | `PUBLIC` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |
| 89 | `.staging/schemas/oura-metrics.schema.json` | `PURGE` | — | Oura biometric metrics schema; purge alongside Oura data. | `SENSITIVE` | issue#80 |
| 90 | `.staging/schemas/README.md` | `ADOPT` | `schemas/README.md` | Schema directory documentation; safe to adopt with path updates. | `PUBLIC` | issue#80 |
| 91 | `.staging/schemas/theme.schema.json` | `ADOPT` | `schemas/theme.schema.json` | Theme configuration schema; safe to adopt. | `PUBLIC` | issue#80 |

---

## `.staging/scripts` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 92 | `.staging/scripts/` | `ARCHIVE` | szmyty/szmyty#74 | Shell and Python scripts for the staging engine; replaced by `tools/profile_builder/cli.py`. No individual scripts were promoted; retain as historical evidence only. | `INTERNAL` | szmyty/szmyty#74 |
| 93 | `.staging/scripts/lib/` | `ARCHIVE` | szmyty/szmyty#74 | Script library modules; superseded by `tools/profile_builder/`. Retain as historical evidence only. | `INTERNAL` | szmyty/szmyty#74 |

---

## `.staging/soundcloud` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 94 | `.staging/soundcloud/latest.json` | `DEFER` | szmyty/szmyty#65 | Cached SoundCloud track data; defer until music integration decision. Not sensitive but also not needed now. | `PUBLIC` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |

---

## `.staging/tests` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 95 | `.staging/tests/` | `DEFER` | szmyty/szmyty#65 | Full test suite for the staging engine; defer alongside the engine. Evaluate individual tests when production modules are established. | `PUBLIC` | roadmap:docs/ROADMAP.md#deferred-post-cutover-decisions |

---

## Acceptance checklist

- [x] Every top-level `.staging` family has a decision row (rows 1–95 above).
- [x] All `SENSITIVE` items are classified `PURGE` and have no target public path.
- [x] Every `ADOPT` / `MERGE` / `REWRITE` item has a target path or open issue.
- [x] This document is reviewed and approved before any `.staging` content is promoted.
- [x] Completion evidence is filled in as each row is actioned.
