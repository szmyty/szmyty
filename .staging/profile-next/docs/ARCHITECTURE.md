# Architecture

This document defines the structure, boundaries, data flow, and automation
model for Alan Szmyt's GitHub profile repository.

---

## Repository Purpose

This repository is Alan Szmyt's public GitHub profile, rendered at
`github.com/szmyty` when the repository owner matches the account name.

**The primary product is `README.md`.**

Everything else — documentation, scripts, workflows, generated artifacts —
exists only to make `README.md` more reliable, maintainable, or visually
compelling.

---

## Repository Boundaries

```
.
├── .github/
│   ├── artifacts/       # Generated outputs (committed, not hand-edited)
│   │   └── <module>/
│   ├── instructions/    # Copilot workspace instructions
│   ├── scripts/         # Data providers, normalizers, renderers
│   │   └── <module>/
│   ├── specs/           # Module specifications
│   │   └── <module>.spec.md
│   ├── workflows/       # GitHub Actions
│   └── agents/          # (future) Specialized agent definitions
├── assets/
│   ├── branding/        # Hand-authored: headers, footers, logos
│   ├── icons/           # Hand-authored: icon assets
│   └── images/          # Hand-authored: photography, illustrations
├── docs/
│   ├── ARCHITECTURE.md  # This file
│   ├── DESIGN.md        # Visual direction and layout principles
│   ├── MIGRATION.md     # Staging-to-production cutover procedure
│   ├── MODULES.md       # Module lifecycle and conventions
│   ├── ROADMAP.md       # Current status and planned work
│   └── reference-inventory.md  # Phase 1 discovery inventory
├── .engineering/
│   └── audits/          # Post-migration and periodic audit reports
├── tests/               # Validation tests for Python modules
├── .editorconfig        # Editor configuration
├── .gitignore           # Git ignore rules
├── AGENTS.md            # AI agent instructions
├── LICENSE              # MIT License
├── PLAN.md              # Reconstruction and migration plan
├── README.md            # Public GitHub profile (primary product)
└── pyproject.toml       # Python tooling configuration
```

---

## Data Flow

Dynamic profile sections follow a consistent lifecycle:

```
External data source (GitHub API, RSS, etc.)
        ↓
Provider (.github/scripts/<module>/provider.py)
        ↓
Normalizer (.github/scripts/<module>/normalizer.py)
        ↓
Renderer (.github/scripts/<module>/renderer.py)
        ↓
Committed artifact (.github/artifacts/<module>/*.svg|json|md)
        ↓
README.md (embeds artifact via relative path)
```

This pipeline ensures:
- The README is always backed by a committed, stable artifact.
- External API failures do not corrupt the displayed profile.
- Artifacts can be regenerated deterministically from a clean clone.

---

## Module Organization

A **module** is a self-contained unit that generates one or more profile
sections. Each module owns:

| File | Purpose |
|------|---------|
| `.github/specs/<module>.spec.md` | Specification and acceptance criteria |
| `.github/scripts/<module>/` | Provider, normalizer, renderer scripts |
| `.github/artifacts/<module>/` | Generated output committed to the repo |
| `.github/workflows/<module>.yml` | Scheduled or manual update workflow |
| `tests/test_<module>.py` | Validation tests |

Modules must be failure-isolated: one module failing must not corrupt other
sections of the README.

---

## Asset Ownership

| Directory | Contains | Managed by |
|-----------|----------|-----------|
| `assets/branding/` | `header.svg`, `footer.svg`, `logo.svg` | Hand-authored |
| `assets/icons/` | Technology and UI icons | Hand-authored |
| `assets/images/` | Photography, illustrations | Hand-authored |
| `.github/artifacts/` | Generated SVGs, JSON, Markdown | Automation workflows |

**Never hand-edit files under `.github/artifacts/`.**
**Never commit automation outputs to `assets/`.**

---

## Automation Model

All scheduled automation runs inside GitHub Actions.

**Workflow requirements:**

- Support `workflow_dispatch` for manual triggering.
- Use `${{ github.repository_owner }}` instead of hardcoded usernames.
- Use `${{ github.repository }}` instead of hardcoded repo slugs.
- Apply least-privilege `permissions` blocks.
- Commit artifacts only when content changes (use diff-check).
- Preserve last successful artifact on API failure (do not delete on error).
- Use `concurrency` groups to prevent overlapping runs.
- Avoid workflow-trigger loops (use `[skip ci]` or path filters).

**Workflow schedule guidelines:**

| Update frequency | Use case |
|-----------------|---------|
| Daily (`0 6 * * *`) | GitHub stats, activity feed |
| Weekly | Lower-priority telemetry |
| Manual only | One-time setup, debugging |

---

## Portability Requirements

This repository is staged at `szmyty/profile-next` and will be migrated to
`szmyty/szmyty`. All production code must be portable by construction.

Portability checklist:
- [ ] No hardcoded `profile-next` in workflows or scripts.
- [ ] No `${{ github.event.repository.name }}` comparisons against `szmyty`.
- [ ] All README asset URLs use repository-relative paths.
- [ ] All workflow `git remote` or `git push` targets use GITHUB_TOKEN.
- [ ] No runtime dependency on `.references/`.
- [ ] `.references/` is excluded from workflow runs.

---

## Generated Artifact Conventions

Artifacts committed to `.github/artifacts/` must:

- Use consistent file names within a module.
- Include a UTC timestamp comment in SVG files where practical.
- Be deterministic given the same input data.
- Be regenerable from a clean clone using a documented command.

---

## Privacy Boundaries

The profile is public. The following data must never appear:

- Biometric or health data (Oura, fitness trackers).
- Precise geolocation.
- Private repository names or contents.
- Personal access tokens (in any form).
- Private contribution activity.
- Internal or employer-confidential information.

---

## Dependency Strategy

**Python** is the primary scripting language.
**GitHub Actions** is the automation platform.
**No Node.js** in this repository (dashboard concept was discarded).

Python tooling is configured in `pyproject.toml`.
Dependencies are managed with `pip` and locked in `requirements.txt` per
module when needed.

---

## Security Model

- All secrets are stored in GitHub repository secrets.
- Workflows use `GITHUB_TOKEN` (auto-provided) wherever possible.
- External PATs (`METRICS_TOKEN`) are used only where `GITHUB_TOKEN` lacks
  required scope.
- No secrets are committed to the repository.
- Workflow permissions are declared explicitly and use least privilege.

See `docs/MIGRATION.md` for a complete secrets reference.
