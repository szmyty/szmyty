# Roadmap

## Repository: szmyty/szmyty

**Status:** Active — clean foundation phase

## Current Phase: Foundation (Q3 2026)

The immediate goal is a clean, truthful, minimal foundation.

### In Progress

- [x] Reconcile repository identity (owner, name, license, URLs)
- [x] Establish active `README.md` and `LICENSE`
- [x] Fix stale source-repository references (`egohygiene`, `sanctuary`)
- [x] Add `.editorconfig`, `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
- [x] Simplify `pyproject.toml` to active scope
- [x] Fix issue template and funding configuration
- [x] Remove tasks pointing to non-existent paths

### Near Term

- [ ] Add CI workflow for identity and broken-reference checks
- [ ] Verify and simplify `.github/FUNDING.yml` platform list
- [ ] Review `.staging/` content for promotion or removal
- [ ] Add `CONTRIBUTORS.md`

### Pinned-repository recommendations (for manual review)

The following six repositories are recommended as GitHub profile pins because
they collectively demonstrate the strongest breadth across the dimensions
described in [szmyty/szmyty#72](https://github.com/szmyty/szmyty/issues/72):

| Slot | Repository | Rationale |
|------|------------|-----------|
| 1 | [`szmyty/soliloquy`](https://github.com/szmyty/soliloquy) | Offline-first LLM tooling; concrete artifact; Docker Compose + Python |
| 2 | [`szmyty/universal`](https://github.com/szmyty/universal) | DX tooling and CI/CD; composable design; broad applicability |
| 3 | [`szmyty/OpenAI-Retro-SuperMarioWorld-SNES`](https://github.com/szmyty/OpenAI-Retro-SuperMarioWorld-SNES) | AI/ML experiment; documented and reproducible |
| 4 | [`egohygiene/egohygiene`](https://github.com/egohygiene/egohygiene) | Platform architecture; cross-platform app; ecosystem centrepiece |
| 5 | [`egohygiene/egolint`](https://github.com/egohygiene/egolint) | Shipped open-source contribution; merged PR; shared quality tooling |
| 6 | [`szmyty/szmyty`](https://github.com/szmyty/szmyty) | Evidence-first profile; schema-validated catalog; meta-engineering |

> These pins must be set manually in GitHub profile settings
> (Profile → Customize your pins). Review accuracy of each repository before
> pinning.

### Future

- [ ] Automated README regeneration from structured profile data
- [ ] Reusable issue form and workflow templates published as a template repository
- [ ] Documentation site (if warranted; see [ADR 0002](adr/0002-site-companion-static-html.md) — static HTML/CSS companion under `site/`)

## Non-Goals

- This is a personal profile repository. It will not grow into a general-purpose
  platform or accumulate speculative tooling.
- No content is promoted from `.staging/` without explicit review.
