# Reference Inventory

Discovery audit of all three reference repositories, conducted as Phase 1 of
the `profile-next` reconstruction.

Reference repositories are read-only and located in `.references/`.

---

## Sources

| ID | Path | Purpose |
|----|------|---------|
| A | `.references/szmyty` | Current live GitHub profile (`szmyty/szmyty`) |
| B | `.references/profile` | Previous experimental profile implementation |
| C | `.references/egohygiene` | Mature engineering infrastructure repository |

---

## Decision Table

| Source | Feature | Current State | Decision | Target Module | Notes |
|--------|---------|---------------|----------|---------------|-------|
| A | Hero section with branded SVG header | Working, hardcoded to szmyty/szmyty | Adapt | `assets/branding/` | Port SVG, use portable paths |
| A | GitHub followers / stars / views badges | Working | Keep | README | Use shields.io + komarev; portable by construction |
| A | Metrics dashboard (overview, stats, languages, contributions SVGs) | Working via `lowlighter/metrics` | Adapt | `github-stats` module | Adapt workflow; use context vars not hardcoded repo |
| A | `github-metrics.svg` legacy combined SVG | Working | Defer | `github-stats` module | Replace with individual SVGs; legacy SVG is redundant |
| A | Profile summary cards (`profile-summary-card-output/`) | Working but requires private PAT | Defer | — | Depends on private action; low value for migration milestone |
| A | Recent activity section via `jamesgeorge007/github-activity-readme` | Working | Adapt | `activity` module | Adapt workflow to use `${{ github.repository_owner }}` |
| A | Developer Experience section (DX Philosophy, Engineering Pillars, What I Build) | Working static content | Keep | README | Clean, relevant content |
| A | Tech stack icon grid (devicons CDN) | Working | Keep | README | Portable CDN links |
| A | Featured Projects table (3 projects) | Working, outdated project list | Adapt | README | Update project list; expand to 6-8 entries |
| A | Automation & Workflows table | Working but hardcoded to szmyty/szmyty | Adapt | README | Rewrite using portable relative paths |
| A | `branding/header.svg` | Working | Keep | `assets/branding/` | Copy and update paths |
| A | `branding/footer.svg` | Working | Keep | `assets/branding/` | Copy and update paths |
| A | `branding/logo.svg` | Working | Keep | `assets/branding/` | Copy and update paths |
| A | `metrics.yml` workflow | Working | Adapt | `.github/workflows/` | Remove hardcoded repo; use `METRICS_TOKEN` secret |
| A | `update-readme.yml` workflow | Working | Adapt | `.github/workflows/` | Use context vars; pin action version |
| A | `profile-summary-cards.yml` workflow | Working | Defer | — | Requires private action; defer post-migration |
| A | `docs/architecture.md` | Good structure | Adapt | `docs/ARCHITECTURE.md` | Rewrite for profile-next conventions |
| A | `docs/secrets.md` | Good reference doc | Adapt | `docs/MIGRATION.md` | Fold secrets documentation into migration guide |
| A | `docs/workflows.md` | Good reference | Adapt | `docs/ARCHITECTURE.md` | Fold into architecture doc |
| A | `resume.pdf` | Committed binary | Defer | `assets/` | Evaluate PDF-vs-link; do not commit on every change |
| A | `audits/` | Audit artifacts | Archive only | — | Not needed in new repo |
| B | Hero section with branded SVG | Working | Discard | — | Superseded by szmyty version; szmyty's is cleaner |
| B | About Me section | Working | Adapt | README | Same content as szmyty; use consolidated version |
| B | Developer Experience section | Working | Discard | — | Duplicates szmyty version |
| B | Dashboard app (Node.js/TypeScript) | Incomplete | Discard | — | Overengineered; not appropriate for profile repo |
| B | SVG card generators (Python) | Partially working | Defer | `github-stats` module | Good concept; evaluate post-foundation |
| B | Oura biometric integration | Working but private data | Discard | — | Privacy concern; biometric data not for public profile |
| B | Location card | Partially working | Discard | — | Privacy concern; precise location not appropriate |
| B | GitHub stats engine (Python) | Partially working | Defer | `github-stats` module | Evaluate as alternative to lowlighter/metrics |
| B | Music platform integration | Stub | Defer | `music` module | Interesting concept; defer until after foundation |
| B | Poetry / pyproject.toml | Working | Adapt | `pyproject.toml` | Adapt for profile-next Python tooling |
| B | `data/metrics/` and mock data | Working | Defer | `.github/artifacts/` | Useful for testing; defer to module phase |
| B | `branding/` assets (header, logo, badges) | Working | Discard | — | Superseded by szmyty branding |
| B | `CHANGELOG.md` / `VERSION` | Working | Discard | — | Versioned changelog unnecessary for a profile repo |
| B | `CONTRIBUTING.md` | Decent | Discard | — | Profile repos rarely need contribution guides |
| B | `mypy.ini` | Working | Adapt | `pyproject.toml` | Fold mypy config into pyproject.toml |
| B | `package.json` / `package-lock.json` | Working (dashboard) | Discard | — | Dashboard is discarded; no Node.js needed |
| B | `docs/ENGINE_ARCHITECTURE.md` | Working | Archive only | — | Profile engine is deferred/discarded |
| B | `docs/SVG_SANITIZATION.md` | Working | Defer | docs | Useful reference when implementing SVG modules |
| B | `docs/WORKFLOWS.md` | Working | Archive only | — | Superseded by new workflow architecture |
| B | Tests (`tests/`) | Partial Python tests | Defer | `tests/` | Adapt test scaffold when Python modules are added |
| C | `LICENSE` (MIT) | Working | Keep | `LICENSE` | Adapt for Alan Szmyt authorship |
| C | `ARCHITECTURE.md` / architecture pattern | Mature | Adapt | `docs/ARCHITECTURE.md` | Adopt structure, simplify to profile scale |
| C | `ONBOARDING.md` AI reading instructions | Mature | Adapt | `AGENTS.md` | Condense into AGENTS.md for profile scope |
| C | `.github/agents/` agent definitions | Mature | Adapt | `.github/instructions/` | Adapt auditor pattern; simplify for profile |
| C | `.github/skills/` skill definitions | Mature | Defer | — | Useful in future; not needed for foundation |
| C | `.github/specs/` specification files | Mature | Defer | `.github/specs/` | Adopt pattern; write specs as modules are defined |
| C | `.github/workflows/build.yml` | Working (Flutter) | Discard | — | Flutter-specific; not needed in profile repo |
| C | `commitlint.config.js` | Working | Discard | — | Too heavy for a profile repo |
| C | `Taskfile.yml` | Working | Defer | — | Evaluate when Python tooling is in place |
| C | `.editorconfig` pattern | Working | Adapt | `.editorconfig` | Create minimal version for profile repo |
| C | `CODE_OF_CONDUCT.md` | Working | Discard | — | Not standard for a personal profile repo |
| C | `SECURITY.md` | Working | Discard | — | Not needed at profile repo scale |
| C | `ROADMAP.md` structure | Working | Adapt | `docs/ROADMAP.md` | Adopt structure; write profile-specific content |
| C | Conventional commits discipline | Working | Keep | `AGENTS.md` | Document as convention for this repo |
| C | `docs/READING_ORDER.md` pattern | Working | Adapt | `AGENTS.md` | Fold reading order into AGENTS.md |
| C | `humans.txt` | Interesting | Discard | — | Low value for a profile repo |

---

## Summary by Decision

| Decision | Count |
|----------|-------|
| Keep | 5 |
| Adapt | 18 |
| Rewrite | 0 |
| Defer | 14 |
| Discard | 20 |
| Archive only | 3 |

---

## Priority Modules for Phase 4

Based on the inventory, these modules are most valuable for the first
migration milestone:

1. **`github-stats`** — Generate overview, languages, and contributions SVGs
   using `lowlighter/metrics`. Replace the hardcoded `metrics.yml` from
   szmyty.
2. **`activity`** — Recent public activity section updated on schedule.
3. **`branding`** — Port `header.svg`, `footer.svg`, and `logo.svg` with
   portable asset paths.

Modules to defer until after first migration:

- `music` — Platform integration needs an API strategy.
- `dashboard` — Dashboard app is overengineered for a profile repo.
- `oura` / biometric — Privacy concern; do not expose.
- `location` — Privacy concern; do not expose.

---

## Privacy Boundary Summary

The following discovered features must **never** appear in the public profile:

| Feature | Reason |
|---------|--------|
| Oura biometric / health data | Sensitive personal health information |
| Precise location card | Exposes geolocation without clear benefit |
| Private repository names | May expose unreleased work |
| Private contribution activity | May expose unreleased work |
| Internal employment details | Not appropriate for public profile |
| Personal access tokens | Security risk |

---

## Hardcoded Path Inventory

The following hardcoded repository references were found in reference files
and must **not** be carried forward:

| Source File | Hardcoded Reference | Resolution |
|-------------|---------------------|-----------|
| `.references/szmyty/README.md` | `szmyty/szmyty` in badge URLs | Use `${{ github.repository }}` in workflows; README uses relative paths |
| `.references/szmyty/.github/workflows/metrics.yml` | `szmyty/szmyty` in config | Replace with `${{ github.repository_owner }}` |
| `.references/szmyty/.github/workflows/update-readme.yml` | `szmyty` in config | Replace with `${{ github.repository_owner }}` |
| `.references/szmyty/README.md` | Badge status URLs with `szmyty/szmyty` | Rewrite to use relative workflow paths |
| `.references/profile/pyproject.toml` | `szmyty/profile` in homepage/repository | Not carried forward; rewritten |

---

*Generated: 2026-07-17. Update this inventory as modules are implemented.*
