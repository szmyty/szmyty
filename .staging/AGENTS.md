# AGENTS.md

AI coding agents working in this repository must read this file before
performing any implementation work.

---

## Repository Identity

**Name:** `szmyty/szmyty` (production) / `szmyty/profile-next` (staging)
**Purpose:** Alan Szmyt's public GitHub profile repository.
**Audience:** GitHub visitors, recruiters, and engineering teams.
**Primary deliverable:** `README.md` — rendered on Alan's public GitHub page.

---

## Required Reading Order

Before implementing anything, load context in this order:

1. `PLAN.md` — Reconstruction plan, phases, and decisions.
2. `README.md` — The primary product.
3. `docs/ARCHITECTURE.md` — Repository boundaries and data flow.
4. `docs/MODULES.md` — Module lifecycle and conventions.
5. `docs/ROADMAP.md` — Current status and priorities.
6. `docs/reference-inventory.md` — Discovery decisions from reference repos.

---

## Core Constraints

### Portability is mandatory

This repository is staged at `szmyty/profile-next` but its final home is
`szmyty/szmyty`.

**Never:**
- Hardcode `szmyty/profile-next` in production code.
- Hardcode the repository name in workflow logic.
- Reference `.references/` from production workflows or README.
- Create runtime dependencies on `.references/`.
- Build links that break after migration.

**Always:**
- Use `${{ github.repository_owner }}` in workflows where the owner is needed.
- Use `${{ github.repository }}` where the full repo slug is needed.
- Use repository-relative asset paths in README (`./assets/branding/header.svg`).
- Design workflow behavior to remain valid after migration.

### The profile is the product

`README.md` is the primary deliverable. All infrastructure exists only to
improve the README's presentation, reliability, and maintainability.

Do not build infrastructure that exists for its own sake.

### Static before dynamic

Build a compelling static profile section before introducing automation.
Automation adds complexity; it should only be added when it reduces
maintenance burden and improves the public story.

### Privacy boundaries

Never include in the public profile:
- Oura or biometric data.
- Precise location.
- Private repository names.
- Private contribution activity.
- Personal access tokens.
- Internal employment details.

---

## Architecture Conventions

### Generated artifacts

Generated outputs (SVGs, JSON, Markdown) belong under:

```
.github/artifacts/<module>/
```

Example:

```
.github/artifacts/github-stats/overview.svg
.github/artifacts/github-stats/languages.svg
.github/artifacts/activity/recent.md
```

### Hand-authored assets

Creative and branding assets belong under:

```
assets/branding/
assets/icons/
assets/images/
```

### Module scripts

Data providers, renderers, and generators belong under:

```
.github/scripts/<module>/
```

### Workflows

GitHub Actions workflows belong under:

```
.github/workflows/
```

Workflows must:
- Support `workflow_dispatch`.
- Use least-privilege permissions.
- Not hardcode repository names.
- Commit only when content changes.
- Preserve last valid artifacts on API failure.
- Not trigger recursive workflow loops.

### Engineering audits

Post-migration and periodic audit reports belong under:

```
.engineering/audits/
```

Audit files are committed source material. An audit is considered published
once it is merged to the main branch. After publication, do not modify an
audit in place — create a follow-up amendment file (e.g.,
`profile-post-migration-audit-amendment-001.md`) or open a new audit for the
next review cycle.

---

## Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

Examples:

```
feat(readme): add technology stack section
fix(workflow): remove hardcoded repository name
docs(architecture): document module lifecycle
chore(assets): add branding SVGs
ci(github-stats): add metrics generation workflow
```

---

## Module Development Checklist

When implementing a new dynamic module:

- [ ] Write a specification in `.github/specs/<module>.spec.md`.
- [ ] Create a static prototype in the README.
- [ ] Implement provider and renderer under `.github/scripts/<module>/`.
- [ ] Generate artifacts to `.github/artifacts/<module>/`.
- [ ] Write at least one test under `tests/`.
- [ ] Add a workflow under `.github/workflows/`.
- [ ] Integrate into README.
- [ ] Verify portable paths (no hardcoded `profile-next`).
- [ ] Verify no privacy violations.

---

## File Ownership

| Path | Owner | Notes |
|------|-------|-------|
| `README.md` | Profile content | Primary product; high care |
| `docs/` | Documentation | Keep proportional to repo scale |
| `.github/workflows/` | Automation | Must be portable |
| `.github/artifacts/` | Generated outputs | Do not hand-edit |
| `assets/` | Branding and creative | Hand-authored source material |
| `tests/` | Validation | Run before committing module changes |
| `.engineering/audits/` | Audit reports | Post-migration and periodic audits |
| `PLAN.md` | Reconstruction plan | Update phase status as work completes |
| `AGENTS.md` | This file | Update as conventions evolve |

---

## What Not to Build

Avoid building any of the following unless explicitly approved:

- Full web applications or dashboards inside the profile repo.
- Custom GitHub Actions ecosystems.
- Biometric or private telemetry integrations.
- Duplicate rendering systems.
- Node.js tooling (this is a Python-first repo).
- Framework abstractions with fewer than two concrete consumers.

---

## Testing

Run tests with:

```sh
python -m pytest tests/
```

If no tests exist yet for a module, add at minimum a smoke test that
validates the renderer produces well-formed output.

---

## Migration Readiness

Before any commit is considered migration-ready:

- [ ] No reference to `profile-next` in production paths or workflow logic.
- [ ] No reference to `.references/` in README or workflows.
- [ ] All embedded assets use relative paths from repo root.
- [ ] All workflows use portable GitHub context variables.
- [ ] `docs/MIGRATION.md` is complete and accurate.
