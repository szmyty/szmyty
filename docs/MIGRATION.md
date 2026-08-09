# Staging Migration Ledger

**Stable queue key:** `szmyty-profile-rebuild-03`
**Epic:** szmyty/szmyty#65
**Closes:** szmyty/szmyty#68

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
| 1 | `.staging/README.md` | `MERGE` | `README.md` | Primary candidate README variant; hero, badges, DX sections are reusable. Must be merged with content from README2.md and README3.md after evidence verification. | `INTERNAL` | |
| 2 | `.staging/README2.md` | `MERGE` | `README.md` | Alternative variant with additional project table and principles sections; merge selected content into production README. | `INTERNAL` | |
| 3 | `.staging/README3.md` | `MERGE` | `README.md` | Cleaner metrics-dashboard variant; metrics layout is a strong candidate for adoption. | `INTERNAL` | |
| 4 | `.staging/AGENTS.md` | `REWRITE` | `AGENTS.md` | Contains project-level agent guidance; superseded by the production `AGENTS.md` but source content is useful as a reference. Rewrite production file from both versions. | `INTERNAL` | |
| 5 | `.staging/CHANGELOG.md` | `DISCARD` | — | Changelog tracks changes to the experimental profile repository, not to production. Not appropriate to promote. | `INTERNAL` | |
| 6 | `.staging/CONTRIBUTING.md` | `ADOPT` | `CONTRIBUTING.md` | Standard contributing guide; content is generic and safe to adopt with minor updates. | `PUBLIC` | |
| 7 | `.staging/CONTRIBUTING copy.md` | `DISCARD` | — | Accidental duplicate file; redundant copy of `CONTRIBUTING.md`. | `INTERNAL` | |
| 8 | `.staging/PLAN.md` | `ARCHIVE` | `docs/audits/` | Detailed engineering plan for the staging build; valuable as a historical audit artifact but not for production promotion. | `INTERNAL` | |
| 9 | `.staging/PULL_REQUEST_SUMMARY.md` | `DISCARD` | — | Internal PR summary created during staging development; not relevant to production. | `INTERNAL` | |
| 10 | `.staging/VERSION` | `DISCARD` | — | Version pinned to the staging repository lifecycle; production versioning is managed via `pyproject.toml`. | `INTERNAL` | |
| 11 | `.staging/.pre-commit-config.yaml` | `ADOPT` | `.pre-commit-config.yaml` | Pre-commit hooks configuration; evaluate hooks for compatibility, then adopt or merge with existing configuration. | `PUBLIC` | |
| 12 | `.staging/.secrets.example` | `ADOPT` | `.secrets.example` | Safe template showing required secret names without values; useful onboarding reference. | `TEMPLATE` | |
| 13 | `.staging/package.json` | `DEFER` | issue to be filed | Node.js package configuration for the dashboard app; defer until dashboard decision is made. | `INTERNAL` | |
| 14 | `.staging/pyproject.toml` | `MERGE` | `pyproject.toml` | Alternative Python project configuration; compare dependency groups and tool settings with production `pyproject.toml`; merge selected additions. | `INTERNAL` | |
| 15 | `.staging/pyproject2.toml` | `DISCARD` | — | Duplicate / scratch variant of `pyproject.toml`; no unique content. | `INTERNAL` | |
| 16 | `.staging/requirements.txt` | `DISCARD` | — | Flat requirements file superseded by Poetry-managed `pyproject.toml`. | `INTERNAL` | |
| 17 | `.staging/requirements-dev.txt` | `DISCARD` | — | Dev requirements file superseded by Poetry dependency groups. | `INTERNAL` | |
| 18 | `.staging/profile.code-workspace` | `DISCARD` | — | VS Code workspace file scoped to the staging repository; not relevant to production. | `INTERNAL` | |
| 19 | `.staging/dashboard.svg` | `PURGE` | — | Generated SVG dashboard containing live metrics; may embed location or biometric data. Do not publish. | `SENSITIVE` | |
| 20 | `.staging/dashboard-dark.svg` | `PURGE` | — | Dark-mode variant of the generated dashboard SVG; same privacy risk as `dashboard.svg`. | `SENSITIVE` | |
| 21 | `.staging/dashboard-light.svg` | `PURGE` | — | Light-mode variant; same privacy risk. | `SENSITIVE` | |
| 22 | `.staging/dashboard-interactive.svg` | `PURGE` | — | Interactive SVG dashboard; may embed live or historical biometric/location data. | `SENSITIVE` | |
| 23 | `.staging/github-metrics.svg` | `DEFER` | szmyty/szmyty#65 | Legacy combined GitHub metrics SVG; regenerate via `lowlighter/metrics` workflow instead of committing a stale copy. | `PUBLIC` | |
| 24 | `.staging/metrics.plugin.16personalities.svg` | `PURGE` | — | Personality-type plugin output; personal psychometric data; must not be published. | `SENSITIVE` | |
| 25 | `.staging/summary-monthly.svg` | `DEFER` | szmyty/szmyty#65 | Monthly summary card; regenerate rather than promote stale artifact. | `PUBLIC` | |
| 26 | `.staging/summary-weekly.svg` | `DEFER` | szmyty/szmyty#65 | Weekly summary card; same as monthly. | `PUBLIC` | |

---

## `.staging/.github` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 27 | `.staging/.github/GOVERNANCE.md` | `ADOPT` | `.github/GOVERNANCE.md` | Generic governance document; safe to adopt. | `PUBLIC` | |
| 28 | `.staging/.github/dependabot.yml` | `ADOPT` | `.github/dependabot.yml` | Dependabot configuration; evaluate intervals and adopt. | `PUBLIC` | |
| 29 | `.staging/.github/workflows/` | `REWRITE` | `.github/workflows/` | Workflow files are tightly coupled to staging repository layout and hardcoded secrets; rewrite for production with portable context variables. | `INTERNAL` | |
| 30 | `.staging/.github/actions/` | `DEFER` | szmyty/szmyty#65 | Custom composite actions; evaluate individual actions and defer until workflows are rebuilt. | `INTERNAL` | |
| 31 | `.staging/.github/instructions/` | `ARCHIVE` | `docs/audits/` | Copilot instruction files specific to the staging development process; not needed in production. | `INTERNAL` | |

---

## `.staging/assets` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 32 | `.staging/assets/branding/` | `ADOPT` | `assets/branding/` | SVG branding assets (header, footer, logo); adopt as-is with path corrections. | `PUBLIC` | |
| 33 | `.staging/assets/icons/` | `ADOPT` | `assets/icons/` | Icon assets; adopt if referenced by production README or site. | `PUBLIC` | |
| 34 | `.staging/assets/images/` | `DEFER` | szmyty/szmyty#65 | Image assets; review individually before promotion. | `PUBLIC` | |

---

## `.staging/branding` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 35 | `.staging/branding/` | `ADOPT` | `assets/branding/` | Root-level branding directory mirrors `assets/branding/`; consolidate into `assets/branding/` at production. | `PUBLIC` | |
| 36 | `.staging/branding/badges/` | `ADOPT` | `assets/branding/badges/` | Custom badge SVGs; safe to adopt. | `PUBLIC` | |

---

## `.staging/dashboard-app` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 37 | `.staging/dashboard-app/` | `DEFER` | issue to be filed | React/TypeScript dashboard app; overengineered for a profile README; defer until a dedicated dashboard decision is made. | `INTERNAL` | |

---

## `.staging/data` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 38 | `.staging/data/metrics/` | `PURGE` | — | Generated metrics JSON; may contain location, health, or usage data. Do not publish. | `SENSITIVE` | |
| 39 | `.staging/data/mock/` | `ADOPT` | `profile/fixtures/` | Mock data for testing; safe to adopt as test fixtures after review. | `PUBLIC` | |
| 40 | `.staging/data/quotes/` | `ADOPT` | `profile/content/quotes/` | Quote data files; safe to adopt. | `PUBLIC` | |
| 41 | `.staging/data/snapshots/` | `PURGE` | — | Snapshot JSON files may contain biometric or location data; purge entirely. | `SENSITIVE` | |
| 42 | `.staging/data/status/` | `DEFER` | szmyty/szmyty#65 | Status data files; review individually before promotion. | `INTERNAL` | |

---

## `.staging/developer` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 43 | `.staging/developer/` | `DEFER` | szmyty/szmyty#65 | Developer-specific configuration or scripts; review before promotion. | `INTERNAL` | |

---

## `.staging/docs` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 44 | `.staging/docs/ARCHITECTURE.md` | `MERGE` | `docs/ARCHITECTURE.md` | Architecture documentation; merge selected content into the production architecture doc. | `PUBLIC` | |
| 45 | `.staging/docs/DESIGN.md` | `ARCHIVE` | `docs/audits/` | Design notes from the staging build; retain as an audit artifact. | `INTERNAL` | |
| 46 | `.staging/docs/MIGRATION.md` | `DISCARD` | — | Staging migration procedure for promoting staging into production; superseded by this production-side ledger. | `INTERNAL` | |
| 47 | `.staging/docs/ROADMAP.md` | `MERGE` | `docs/ROADMAP.md` | Staging roadmap; merge near-term items with the production roadmap. | `INTERNAL` | |
| 48 | `.staging/docs/MODULES.md` | `DEFER` | szmyty/szmyty#65 | Module documentation; defer until production modules are established. | `INTERNAL` | |
| 49 | `.staging/docs/WORKFLOWS.md` | `MERGE` | `docs/ARCHITECTURE.md` | Workflow documentation; fold relevant content into the architecture doc. | `INTERNAL` | |
| 50 | `.staging/docs/MONITORING.md` | `DEFER` | szmyty/szmyty#65 | Monitoring documentation; defer until production observability is established. | `INTERNAL` | |
| 51 | `.staging/docs/TROUBLESHOOTING.md` | `DEFER` | szmyty/szmyty#65 | Troubleshooting guide; defer until production services are running. | `INTERNAL` | |
| 52 | `.staging/docs/reference-inventory.md` | `ARCHIVE` | `docs/audits/` | Older reference inventory; superseded by this ledger; retain as an audit artifact. | `INTERNAL` | |
| 53 | `.staging/docs/style-guide.md` | `ADOPT` | `docs/style-guide.md` | Markdown/content style guide; safe to adopt. | `PUBLIC` | |
| 54 | `.staging/docs/suggestions.md` | `ARCHIVE` | `docs/audits/` | Internal brainstorming notes; not suitable for production. | `INTERNAL` | |
| 55 | `.staging/docs/cards.md` | `DEFER` | szmyty/szmyty#65 | Card design notes; defer until production card system is established. | `INTERNAL` | |
| 56 | `.staging/docs/markdown_valid_elements.md` | `ADOPT` | `docs/markdown_valid_elements.md` | Reference for valid GitHub-rendered Markdown elements; safe to adopt. | `PUBLIC` | |
| 57 | `.staging/docs/ENGINE_ARCHITECTURE.md` | `ARCHIVE` | `docs/audits/` | Engine architecture notes specific to the staging profile engine. | `INTERNAL` | |
| 58 | `.staging/docs/MODULAR_ARCHITECTURE.md` | `ARCHIVE` | `docs/audits/` | Modular architecture notes; staging-specific. | `INTERNAL` | |
| 59 | `.staging/docs/LOCAL_DEVELOPMENT.md` | `DEFER` | szmyty/szmyty#65 | Local development guide; defer until production tooling is settled. | `INTERNAL` | |
| 60 | `.staging/docs/RELEASES.md` | `DISCARD` | — | Staging release notes; not relevant to production. | `INTERNAL` | |
| 61 | `.staging/docs/OPTIMIZATION_GUIDE.md` | `ARCHIVE` | `docs/audits/` | Staging-specific optimisation notes. | `INTERNAL` | |
| 62 | `.staging/docs/CACHING_BENCHMARKS.md` | `ARCHIVE` | `docs/audits/` | Caching benchmark results from staging engine; not portable to production without re-measurement. | `INTERNAL` | |
| 63 | `.staging/docs/CACHING_QUICK_REFERENCE.md` | `ARCHIVE` | `docs/audits/` | Quick reference for staging caching system. | `INTERNAL` | |
| 64 | `.staging/docs/WORKFLOW_CACHING.md` | `ARCHIVE` | `docs/audits/` | Workflow caching notes; staging-specific. | `INTERNAL` | |
| 65 | `.staging/docs/API_RESILIENCE.md` | `ARCHIVE` | `docs/audits/` | API resilience notes for the staging engine. | `INTERNAL` | |
| 66 | `.staging/docs/API_TIMEOUT_RETRY_GUIDE.md` | `ARCHIVE` | `docs/audits/` | Retry and timeout guide for the staging engine. | `INTERNAL` | |
| 67 | `.staging/docs/INTEGRATION_EXAMPLE.md` | `ARCHIVE` | `docs/audits/` | Integration example for the staging engine. | `INTERNAL` | |
| 68 | `.staging/docs/SVG_SANITIZATION.md` | `ADOPT` | `docs/SVG_SANITIZATION.md` | SVG sanitisation guidelines; relevant to production card generation. | `PUBLIC` | |
| 69 | `.staging/docs/ROBUSTNESS_IMPROVEMENTS.md` | `ARCHIVE` | `docs/audits/` | Robustness notes specific to the staging engine implementation. | `INTERNAL` | |
| 70 | `.staging/docs/README_LAYOUT_BEFORE_AFTER.md` | `ARCHIVE` | `docs/audits/` | Before/after layout diff; historical reference only. | `INTERNAL` | |
| 71 | `.staging/docs/README_LAYOUT_CHANGELOG.md` | `ARCHIVE` | `docs/audits/` | Layout changelog; staging history only. | `INTERNAL` | |
| 72 | `.staging/docs/README_SECTION_CHANGES.md` | `ARCHIVE` | `docs/audits/` | Section change notes; staging history only. | `INTERNAL` | |
| 73 | `.staging/docs/LOCATION_CARD_CHANGES.md` | `PURGE` | — | Location card change log may contain location data references; purge. | `SENSITIVE` | |
| 74 | `.staging/docs/UNIFIED_WORKFLOW_MIGRATION.md` | `ARCHIVE` | `docs/audits/` | Unified workflow migration notes; staging-specific. | `INTERNAL` | |

---

## `.staging/engine` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 75 | `.staging/engine/profile_engine/` | `DEFER` | szmyty/szmyty#65 | Full Python profile engine (CLI, FastAPI, clients, generators, models, services, theme, utils); sophisticated but overscoped for an initial profile migration. Defer until production Python package needs are defined. | `PUBLIC` | |
| 76 | `.staging/engine/tests/` | `DEFER` | szmyty/szmyty#65 | Engine test suite; defer alongside the engine. | `PUBLIC` | |

---

## `.staging/footer` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 77 | `.staging/footer/footer.html` | `ADOPT` | `assets/footer/footer.html` | HTML footer template; safe to adopt. | `PUBLIC` | |
| 78 | `.staging/footer/README.md` | `ADOPT` | `assets/footer/README.md` | Footer documentation; safe to adopt. | `PUBLIC` | |

---

## `.staging/location` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 79 | `.staging/location/` | `PURGE` | — | Precise geographic location data; confirmed by public-data security audit. Must not be published. | `SENSITIVE` | |

---

## `.staging/metrics` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 80 | `.staging/metrics/` | `REGENERATE` | `metrics/` | Metrics SVGs should be regenerated by the production `lowlighter/metrics` workflow rather than promoted as stale artifacts. Directory structure can inform workflow output paths. | `PUBLIC` | |

---

## `.staging/models` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 81 | `.staging/models/` | `DEFER` | szmyty/szmyty#65 | Placeholder directory (`.gitkeep` only); defer until model definitions are needed. | `INTERNAL` | |

---

## `.staging/oura` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 82 | `.staging/oura/` | `PURGE` | — | Biometric health data from Oura ring; confirmed by public-data security audit. Must not be published under any circumstances. | `SENSITIVE` | |

---

## `.staging/profile-summary-card-output` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 83 | `.staging/profile-summary-card-output/` | `REGENERATE` | `profile-summary-card-output/` | Theme-variant profile summary card SVGs; regenerate via the production `profile-summary-cards.yml` workflow rather than promoting stale copies. | `PUBLIC` | |

---

## `.staging/quotes` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 84 | `.staging/quotes/` | `ADOPT` | `profile/content/quotes/` | Quote data files at root level; consolidate with `data/quotes/` and adopt. | `PUBLIC` | |

---

## `.staging/schemas` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 85 | `.staging/schemas/weather.schema.json` | `DEFER` | szmyty/szmyty#65 | Weather data schema; defer until weather integration is considered for production. | `PUBLIC` | |
| 86 | `.staging/schemas/developer-stats.schema.json` | `ADOPT` | `schemas/developer-stats.schema.json` | Developer statistics schema; safe to adopt and use for metrics validation. | `PUBLIC` | |
| 87 | `.staging/schemas/health-snapshot.schema.json` | `PURGE` | — | Health/biometric snapshot schema; even the schema reveals the data shape of private health data. Purge to avoid inference. | `SENSITIVE` | |
| 88 | `.staging/schemas/soundcloud-track.schema.json` | `DEFER` | szmyty/szmyty#65 | SoundCloud track schema; defer until music integration decision. | `PUBLIC` | |
| 89 | `.staging/schemas/oura-metrics.schema.json` | `PURGE` | — | Oura biometric metrics schema; purge alongside Oura data. | `SENSITIVE` | |
| 90 | `.staging/schemas/README.md` | `ADOPT` | `schemas/README.md` | Schema directory documentation; safe to adopt with path updates. | `PUBLIC` | |
| 91 | `.staging/schemas/theme.schema.json` | `ADOPT` | `schemas/theme.schema.json` | Theme configuration schema; safe to adopt. | `PUBLIC` | |

---

## `.staging/scripts` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 92 | `.staging/scripts/` | `DEFER` | szmyty/szmyty#65 | Shell and Python scripts for the staging engine; review individually and defer until production tooling is established. | `INTERNAL` | |
| 93 | `.staging/scripts/lib/` | `DEFER` | szmyty/szmyty#65 | Script library modules; defer alongside scripts. | `INTERNAL` | |

---

## `.staging/soundcloud` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 94 | `.staging/soundcloud/latest.json` | `DEFER` | szmyty/szmyty#65 | Cached SoundCloud track data; defer until music integration decision. Not sensitive but also not needed now. | `PUBLIC` | |

---

## `.staging/tests` family

| # | Source path | Decision | Target path / issue | Rationale | Privacy status | Completion evidence |
|---|-------------|----------|---------------------|-----------|----------------|---------------------|
| 95 | `.staging/tests/` | `DEFER` | szmyty/szmyty#65 | Full test suite for the staging engine; defer alongside the engine. Evaluate individual tests when production modules are established. | `PUBLIC` | |

---

## Acceptance checklist

- [ ] Every top-level `.staging` family has a decision row (rows 1–95 above).
- [ ] All `SENSITIVE` items are classified `PURGE` and have no target public path.
- [ ] Every `ADOPT` / `MERGE` / `REWRITE` item has a target path or open issue.
- [ ] This document is reviewed and approved before any `.staging` content is promoted.
- [ ] Completion evidence is filled in as each row is actioned.
