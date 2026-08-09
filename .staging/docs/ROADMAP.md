# Roadmap

Current status and planned work for the profile reconstruction.

---

## Status

**Phase:** Foundation + Static Profile  
**Milestone:** Migration readiness

---

## Phase 1 — Repository Foundation ✅

- [x] Merge master branch content into working branch.
- [x] Create `docs/reference-inventory.md` with decision table.
- [x] Create `AGENTS.md` with AI coding instructions.
- [x] Create `LICENSE` (MIT).
- [x] Create `.editorconfig`.
- [x] Create `docs/ARCHITECTURE.md`.
- [x] Create `docs/DESIGN.md`.
- [x] Create `docs/MODULES.md`.
- [x] Create `docs/MIGRATION.md`.
- [x] Create `docs/ROADMAP.md` (this file).

---

## Phase 2 — Reference Discovery ✅

- [x] Inspect `.references/szmyty` (current live profile).
- [x] Inspect `.references/profile` (experimental implementation).
- [x] Inspect `.references/egohygiene` (engineering infrastructure).
- [x] Document all features with keep/adapt/rewrite/defer/discard decisions.
- [x] Identify and document hardcoded paths to remediate.
- [x] Identify and document privacy boundary violations to avoid.

---

## Phase 3 — Static Profile Composition ✅

- [x] Update `README.md` hero section with portable badges.
- [x] Write "About" section — who Alan is and what he builds.
- [x] Write "Current Focus" section — active projects and interests.
- [x] Write "Project Ecosystem" — overview of Alan's project landscape.
- [x] Write "Engineering Principles" section.
- [x] Write "Technology Stack" section with devicons.
- [x] Write "Research & Learning" section.
- [x] Write "Featured Projects" table.
- [x] Write "Organizations" section.
- [x] Write "Creative Technology" section.
- [x] Write "Contact" section.
- [x] Add footer with branding.
- [x] Verify no hardcoded `profile-next` references in README.

---

## Phase 4 — Dynamic Modules 🔄

### `github-stats` module

- [x] Adapt `lowlighter/metrics` workflow from `.references/szmyty`.
- [x] Replace hardcoded `szmyty/szmyty` with `${{ github.repository_owner }}`.
- [x] Workflow generates `overview.svg`, `languages.svg`, `contributions.svg`.
- [x] Workflow commits artifacts to `.github/artifacts/github-stats/`.
- [x] Integrate SVG artifact paths into README.
- [ ] Write `.github/specs/github-stats.spec.md`.
- [ ] Test workflow via `workflow_dispatch`.

### `activity` module

- [x] Adapt `jamesgeorge007/github-activity-readme` workflow.
- [x] Replace hardcoded username with `${{ github.repository_owner }}`.
- [x] Integrate `START_SECTION:activity` / `END_SECTION:activity` markers into README.
- [ ] Write `.github/specs/activity.spec.md`.
- [ ] Test workflow via `workflow_dispatch`.

### `branding` module (static) ✅

- [x] Source and adapt `header.svg` for `assets/branding/`.
- [x] Create `footer.svg` for `assets/branding/`.
- [x] Source and adapt `logo.svg` for `assets/branding/`.
- [x] Integrate header and footer into README.

---

## Phase 5 — Visual Polish 🔲

- [ ] Review README in GitHub light mode.
- [ ] Review README in GitHub dark mode.
- [ ] Review README at desktop width.
- [ ] Review README at narrow/mobile width.
- [ ] Verify SVG clipping behavior.
- [ ] Verify text readability throughout.
- [ ] Verify link behavior (all links resolve).
- [ ] Verify image loading (no broken images).
- [ ] Verify visual consistency across sections.
- [ ] Verify alt text on all meaningful images.
- [ ] Verify accessibility (no color-only information).

---

## Phase 6 — Migration Readiness 🔲

- [ ] Confirm no path references `profile-next`.
- [ ] Confirm no URL incorrectly targets the staging repository.
- [ ] Confirm workflows use portable GitHub context variables.
- [ ] Confirm secrets required in production are documented in
  `docs/MIGRATION.md`.
- [ ] Confirm all embedded assets use valid relative paths.
- [ ] Confirm all generation commands work from a clean clone.
- [ ] Confirm scheduled workflows can run in `szmyty/szmyty`.
- [ ] Confirm the README renders correctly in GitHub's profile context.
- [ ] All items in the `docs/MIGRATION.md` validation checklist pass.

---

## Phase 7 — Production Cutover 🔲

- [ ] Archive the pre-migration state of `szmyty/szmyty`.
- [ ] Follow the cutover procedure in `docs/MIGRATION.md`.
- [ ] Run all manual workflows in production.
- [ ] Verify the public GitHub profile.
- [ ] Observe at least one scheduled automation cycle.
- [ ] Archive `szmyty/profile-next` after verification.
- [ ] Perform post-migration audit.

---

## Deferred Work

The following items are intentionally deferred until after the first
migration milestone:

| Item | Reason |
|------|--------|
| `music` module | API strategy not defined |
| Profile summary cards | Requires private action PAT |
| `pyproject.toml` / Python tooling | No Python scripts yet |
| Tests | No Python scripts to test yet |
| GitHub specs | Write as modules are defined |
| `.github/instructions/` | Write as Copilot workspace is configured |

---

## Backlog

Ideas worth exploring after the migration milestone:

- Automated resume/CV generation from structured data.
- Project ecosystem visualization (ASCII or SVG diagram).
- Organization card generation.
- Technology radar / skills matrix.
- Research notes integration (lightweight PKM export).
- Music streaming activity card (Spotify or Last.fm).
- Ko-fi / sponsorship integration.
- Blog/writing feed integration.

These are exploratory and must each be evaluated against the privacy boundary
and proportionality principles in `PLAN.md`.
