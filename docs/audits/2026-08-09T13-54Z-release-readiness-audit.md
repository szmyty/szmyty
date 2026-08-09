# Holistic Release-Readiness Audit Report

Date: 2026-08-09T13:54Z (UTC)
Issue: szmyty/szmyty#81
Queue key: `szmyty-profile-rebuild-16`
Scope: Post-cutover production tree + accessible GitHub repository surfaces (read-only)

## Recommendation

**NOT READY**

Rationale: the production CI workflow is currently failing on `master` (run `31316994554`), so release-readiness is blocked until the validation gate is green again.

---

## Evidence collection summary

### Repository and local command evidence

- `README.md` content and structure reviewed (`/home/runner/work/szmyty/szmyty/README.md:1-378`).
- Workflows reviewed:
  - `/home/runner/work/szmyty/szmyty/.github/workflows/ci.yml:1-70`
  - `/home/runner/work/szmyty/szmyty/.github/workflows/update-profile.yml:1-226`
  - `/home/runner/work/szmyty/szmyty/.github/workflows/pages.yml:1-92`
- Module/config/source-of-truth files reviewed:
  - `/home/runner/work/szmyty/szmyty/profile/content/modules.yml:1-34`
  - `/home/runner/work/szmyty/szmyty/profile/content/evidence.yml:1-422`
  - `/home/runner/work/szmyty/szmyty/tools/modules/*.py`
  - `/home/runner/work/szmyty/szmyty/tests/test_modules.py:1-295`
- Template portability files reviewed:
  - `/home/runner/work/szmyty/szmyty/templates/manifest.yml:1-86`
  - `/home/runner/work/szmyty/szmyty/templates/validate_template.py:1-347`
  - `/home/runner/work/szmyty/szmyty/tests/test_validate_template.py:1-317`

Commands run:

```bash
bash .tasks/check-identity.sh
python profile/validate_assets.py assets/profile
python templates/validate_template.py \
  templates/repository/example/README.md \
  templates/profile/example/README.md
python - <<'PY'  # README relative-link existence check
...
PY
```

Results:

- Identity check: `Identity check PASSED: no stale repository references found.`
- Asset validation: `Asset validation passed — assets/profile`
- Template validation:
  - `Template validation passed — templates/repository/example/README.md`
  - `Template validation passed — templates/profile/example/README.md`
- README relative links: `relative_links 9`, `missing 0`

### GitHub MCP evidence

- Repository metadata (`github-mcp-server-search_repositories`, query `repo:szmyty/szmyty`):
  - public repo, MIT license, Discussions enabled, Pages enabled, issues enabled.
- Discussions categories (`github-mcp-server-list_discussion_categories`):
  - categories available: `Announcements`, `General`, `Ideas`, `Polls`, `Q&A`, `Show and tell`.
- CI/workflow runs (`github-mcp-server-actions_list` + `github-mcp-server-get_job_logs`):
  - failing run on `master`: `CI` run `31316994554`.
  - failed job logs show Ruff failures (import order, unused imports, line length) in tests.

---

## Findings by severity

## CRITICAL

None.

## HIGH

### H1 — CI gate is failing on production branch (`master`) (**new issue warranted**)

- **Severity:** HIGH
- **Evidence:**
  - `github-mcp-server-actions_list` shows `CI` push runs on `master` with `failure` conclusion.
  - `github-mcp-server-get_job_logs` for run `31316994554` shows `validate` job failed in Ruff step (`Found 28 errors`, exit code 1).
- **Affected surface:** GitHub Actions CI status, branch release safety.
- **Impact:** repository does not currently satisfy its own validation pipeline; release readiness is blocked.
- **Recommended resolution:** fix Ruff violations reported in failing run and restore green CI on `master`.
- **Validation method:** re-run `CI` workflow and confirm successful conclusion on latest `master` commit.
- **Issue draft needed:** yes.

## MEDIUM

### M1 — Discussions contact link points to a non-existent category path (**new issue warranted**)

- **Severity:** MEDIUM
- **Evidence:**
  - `.github/ISSUE_TEMPLATE/config.yml:25-27` routes “Documentation Feedback” to `.../discussions/categories/documentation`.
  - `github-mcp-server-list_discussion_categories` returns categories without `documentation`.
- **Affected paths/surface:** issue contact UX in GitHub issue-creation flow.
- **Impact:** users clicking the documentation feedback link can land on a missing/invalid category route.
- **Recommended resolution:** either create a matching Discussions category or update the link to an existing category (for example `ideas` or `q-a`).
- **Validation method:** verify category exists in Discussions UI and that contact link resolves correctly.
- **Issue draft needed:** yes.

### M2 — README contains two generated-region conventions, increasing maintenance ambiguity (**new issue warranted**)

- **Severity:** MEDIUM
- **Evidence:**
  - Reserved markers: `README.md:351-358` (`<!-- GENERATED:* -->`).
  - Active module markers: `README.md:370-377` (`<!-- START:<module> -->` / `<!-- END:<module> -->`).
  - Module ownership contract expects `START/END` markers (`profile/content/modules.yml:4-5`, `AGENTS.md:154-158`).
- **Affected paths/surface:** README maintenance clarity; contributor/operator understanding.
- **Impact:** unclear ownership can cause accidental edits in non-authoritative marker regions.
- **Recommended resolution:** standardize on one generated-marker scheme in production README and document migration/removal of obsolete markers.
- **Validation method:** run module rendering (`python -m tools.modules.update_readme`) and ensure all generated content uses only documented marker format.
- **Issue draft needed:** yes.

## LOW

### L1 — Visual assets are explicitly marked as placeholders, not final artwork (**new issue warranted**) 

- **Severity:** LOW
- **Evidence:** `assets/profile/README.md:3` (`Status: Placeholder assets — awaiting final ChatGPT-generated artwork`), plus asset table statuses `Placeholder` (`assets/profile/README.md:12-15`).
- **Affected paths/surface:** visual polish and brand distinctiveness.
- **Impact:** does not break functionality, but communicates interim brand state.
- **Recommended resolution:** replace placeholders with final approved assets and update provenance/status fields.
- **Validation method:** rerun `python profile/validate_assets.py assets/profile` and perform manual light/dark/narrow viewport render checks.
- **Issue draft needed:** yes.

## NOTE

### N1 — Several GitHub settings are outside repository-file observability

- **Severity:** NOTE
- **Evidence:** repository-level APIs in this audit surface workflow runs/metadata but not full settings state for branch protections/rulesets, pinned repos, and About links.
- **Affected surface:** governance/completeness of this audit.
- **Impact:** some checklist items remain manual-verification items.
- **Recommended resolution:** include a short owner-run manual checklist in follow-up operations.
- **Validation method:** owner review in GitHub Settings/UI.
- **Issue draft needed:** no (track inside runbook/checklist updates as needed).

---

## Passing evidence (quality and resilience signals)

- **First-viewport clarity/time-to-trust:** hero + explicit identity text appears immediately (`README.md:18-23`), with brief summary in first section (`README.md:32-40`).
- **Narrative hierarchy and scanability:** strong sectioning and evidence-linked tables (`README.md:48-77`, `85-189`, `221-255`, `338-344`).
- **Evidence traceability:** explicit Evidence IDs in README and canonical records in `profile/content/evidence.yml`.
- **Accessibility fundamentals:** non-empty banner alt text (`README.md:13-15`), markdown fallback identity text (`README.md:18-23`), SVG safety checks enforced in validator (`profile/validate_assets.py:91-153`).
- **Asset contract compliance:** local validator passes; required files present and within budget (`profile/validate_assets.py`, command result above).
- **Automation hardening:** external actions are SHA-pinned in workflows; CI avoids `pull_request_target`; write permission constrained to update-profile commit job.
- **Module determinism/fallbacks:** explicit fixture/cache fallback behavior implemented (`tools/modules/*.py`) and tested (`tests/test_modules.py`).
- **Template extraction safety:** include/exclude manifest and token validation are present (`templates/manifest.yml`, `templates/validate_template.py`), with passing example validation.
- **Repository hygiene:** identity constraint check passes, README relative links resolve, and profile deny-list/privacy docs are explicit (`docs/PRIVACY.md`).

---

## Required report areas coverage

### 1) Profile product quality

- **Clarity/time-to-trust:** pass (see passing evidence above).
- **Narrative hierarchy/scanability:** pass.
- **Evidence quality/traceability:** pass with strong linkage to evidence catalog.
- **Flagship projects/case-study depth:** pass; dedicated case studies under `docs/projects/*.md`.
- **Ego Hygiene comprehensibility:** mostly pass; architecture map + layer table are clear (`README.md:205-238`).
- **Professional/creative balance:** pass; both engineering and creative sections represented.
- **Contact/availability/freshness:** contact channels present (`README.md:338-344`); evidence catalog has fresh review dates (`2026-08-09`) but no explicit "last generated" stamp in README body.

### 2) Visual and accessibility quality

- **Brand consistency/distinctiveness:** functional but placeholder-status assets remain (L1).
- **Light/dark behavior:** `<picture>` with dark/light sources present (`README.md:10-16`); asset validator passes.
- **Alt text/headings/tables:** alt text present; heading hierarchy is consistent; tables are used with readable labels.
- **Reduced motion/keyboard behavior:** no interactive JS in README; keyboard concerns are minimal for static markdown.
- **Image-disabled/external failure behavior:** critical identity and summary text exist outside images (`README.md:18-40`); this passes fallback requirement.
- **Asset provenance/dimensions/budgets/SVG safety:** documented and validated (`assets/profile/README.md`, `docs/DESIGN.md`, `profile/validate_assets.py`).

### 3) Architecture and maintainability

- **Hand-authored/generated boundaries:** documented and generally respected (AGENTS + modules.yml).
- **Source-of-truth integrity:** mostly strong; marker-convention duplication raises maintainability risk (M2).
- **Module isolation/determinism/fallbacks:** pass, with explicit cache/fixture fallback paths and tests.
- **Dependency/tooling proportionality:** pass; focused Python dependency set in `pyproject.toml`.
- **Staging-era duplication/architecture theater:** `.staging` absent; cutover docs and audit trail are present.
- **Documentation/agent-instruction accuracy:** generally strong; one outdated Discussions category link identified (M1).

### 4) Automation and security

- **Workflow permissions/pinning/fork safety:** pass overall; SHA pinning and no `pull_request_target`.
- **Secret/public-data boundary:** pass by policy and implementation docs (`docs/PRIVACY.md`, `docs/audits/public-data-security-audit.md`).
- **Provider failure/cache/no-op behavior:** pass (update-profile summary + module fallbacks).
- **Reproducibility from clean checkout:** currently blocked by failing CI (H1).
- **Release/Pages rollback readiness:** documented in runbook (`docs/RUNBOOK.md:143-170`).

### 5) Template product quality

- **Repository/profile layer separation:** pass (`templates/manifest.yml` include/exclude lists).
- **Extraction safety/portability:** pass with validator checks and adaptation guides.
- **Placeholder/token validation:** pass (`templates/validate_template.py`, tests).
- **Absence of personal data:** pass in examples (validated by template validator rules and tests).
- **Onboarding quality:** pass (`templates/README.md` quick-start and structure sections).

### 6) Repository and GitHub surface

- **Metadata/license/discussions/pages/actions:** repository metadata indicates public + MIT + discussions/pages/actions enabled.
- **Security routing:** issue config has private advisory link (`.github/ISSUE_TEMPLATE/config.yml:29-31`).
- **Broken links/stale identifiers:** one stale Discussions category route found (M1).
- **Unnecessary tracked generated/editor files:** no release-blocking evidence found in this audit scope.
- **README size/repo footprint:** README ~23.9 KB (`wc -c README.md`), repository footprint ~1.5 MB (`du -sh .`).

---

## Prioritized, deduplicated follow-up backlog (issue drafts)

Dependency order is top-to-bottom.

### Draft 1 (blocks all others)

- **Title:** `ci: restore green validation pipeline on master`
- **Severity target:** HIGH
- **Why now:** release blocker; required to move from `NOT READY`.
- **Scope:** fix current Ruff failures reported in run `31316994554`; no unrelated refactors.
- **Acceptance:** latest `CI` run on `master` passes all jobs.
- **Dependencies:** none.

### Draft 2

- **Title:** `docs(github): align issue contact links with existing discussion categories`
- **Severity target:** MEDIUM
- **Scope:** update `.github/ISSUE_TEMPLATE/config.yml` documentation feedback link to a valid Discussions category (or create the category and keep link).
- **Acceptance:** link resolves to an existing category and contributor routing is clear.
- **Dependencies:** none (can run parallel), but should follow Draft 1 if batching release-readiness closure work.

### Draft 3

- **Title:** `docs(profile): standardize README generated-region marker convention`
- **Severity target:** MEDIUM
- **Scope:** remove or migrate obsolete `GENERATED:*` marker block and align docs/tests/contracts to one convention.
- **Acceptance:** `README.md` uses a single documented marker style; module renderer behavior unchanged and validated.
- **Dependencies:** preferably after Draft 1.

### Draft 4

- **Title:** `assets(profile): replace placeholder visual assets with final approved artwork`
- **Severity target:** LOW
- **Scope:** replace placeholder SVGs in `assets/profile/`, update provenance/status in `assets/profile/README.md`, keep budgets/safety checks passing.
- **Acceptance:** asset validator passes; manual light/dark/mobile checks complete.
- **Dependencies:** none.

---

## Final readiness statement

Current state is **NOT READY** due to one high-severity blocker (failing CI on `master`).

If Draft 1 is completed and CI returns to green, the repository can be promoted to **READY WITH FOLLOW-UPS**, with Drafts 2–4 handled as bounded quality/maintainability improvements.
