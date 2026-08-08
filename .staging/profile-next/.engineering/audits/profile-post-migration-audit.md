# Profile Post-Migration Audit

**Audit date:** 2026-07-17
**Repository audited:** `szmyty/profile-next` (staging repository; content migrates to `szmyty/szmyty`)
**Note:** This audit was performed on the staging repository. The audit document is committed here and will be carried into the production repository (`szmyty/szmyty`) as part of the migration, per `PLAN.md` Section 17.
**Branch:** `copilot/audit-github-profile-post-migration`
**Commits reviewed:**
- `80a8888a` — "Initial plan" (HEAD at time of audit)
- `e57958c6` — "Merge pull request #4 from szmyty/copilot/profile-next-evolution-bootstrap"
**Scope:** Full repository — README, workflows, assets, artifacts, scripts, tests, documentation, configuration, security.
**Method:** Static analysis of all committed files; validation scripts run locally; workflow YAML reviewed manually; SVG files parsed; links inventoried; portability and security scanned.

---

## Executive Summary

The `profile-next` staging repository represents a well-structured, architecturally sound GitHub profile reconstruction. The documentation and infrastructure are proportional and disciplined. The static sections of the README (About, Current Focus, Engineering Principles, Technology Stack, etc.) are well-written and recruiter-friendly.

However, the profile is **not yet in a production-ready state**. The three most significant gaps are:

1. **Generated artifacts are absent.** The GitHub Statistics section references three SVG files (`overview.svg`, `languages.svg`, `contributions.svg`) that do not yet exist. First-time visitors to the live profile will see broken image placeholders in the most visually prominent metric section.

2. **The activity section is empty.** The `Latest Activity` section contains only an HTML comment placeholder. The `jamesgeorge007/github-activity-readme` workflow has not been run, so no activity is visible.

3. **Third-party GitHub Actions are unpinned.** Both `lowlighter/metrics@latest` and `jamesgeorge007/github-activity-readme@master` are pinned to floating refs, creating supply-chain risk.

**Phases 5 (Visual Polish), 6 (Migration Readiness), and 7 (Production Cutover) remain incomplete** per `docs/ROADMAP.md`. The repository should complete these phases before the production cutover is declared done.

**Overall readiness rating: 5 / 10** — Strong foundation; content is solid; critical dynamic sections are incomplete; unpinned actions represent a security risk.

---

## Findings by Domain

---

### 1. Public Profile Impact

**F-01** | Profile first impression is strong once artifacts are present
- The hero SVG header is visually polished and sets a professional tone.
- The badge row (followers, views, stars, LinkedIn, Portfolio) is clean and appropriate.
- The About section communicates identity clearly in three short paragraphs.
- **Gap:** Until generated SVGs exist, the GitHub Statistics section breaks the visual flow with missing images.

**F-02** | Identity and role are clearly communicated
- "Software engineer with a focus on cloud-native systems, developer experience, AI-assisted tooling, and creative automation" is a strong, accurate opening sentence.
- The "Personal OS" metaphor in the Project Ecosystem section is distinctive and memorable.

**F-03** | Featured Projects section has two placeholder entries
- "Homelab" and "Resume Generator" are marked *In progress* and link to `https://github.com/szmyty` (the profile root) rather than to specific repositories.
- This looks incomplete to any visitor who clicks those links.
- These should either link to real repositories or be replaced with projects that have repositories.

**F-04** | No résumé or CV link is present
- `docs/MIGRATION.md` mentions a `resume.pdf` decision. The current README and contact section do not include a résumé link.
- Recruiters expect this, particularly for engineering roles.

**F-05** | Activity section is empty
- The `Latest Activity` section is invisible to profile visitors (only an HTML comment is rendered, not visible in GitHub's Markdown preview).
- An empty section with no visible content is worse than no section — it implies the profile is abandoned or broken.

**F-06** | Profile feels active and maintained at the content level
- The Current Focus section references active work on AI Tooling, Flutter Foundation, and Homelab.
- Engineering Principles and Research & Learning are thoughtful and current.
- Creative Technology is a positive differentiator.

---

### 2. Content Quality

**F-07** | Content is well-written, specific, and appropriately technical
- No grammar or spelling issues observed.
- Tone is confident and professional without being arrogant.
- Buzzword density is low; language is specific.

**F-08** | "Current Focus" is detailed but could be slightly more selective
- Six active items is the upper end of what a recruiter will read.
- Consider cutting to four high-signal items and moving lower-priority items to the Research section.

**F-09** | egohygiene org listed in Organizations section but with no link check
- The `egohygiene` organization card links to `https://github.com/egohygiene` — this should be verified to be a live, publicly accessible org.
- The szmyty org card describes "Personal open-source engineering work" but the second organization block appears blank or truncated (the szmyty cell has no following organization).

**F-10** | "soliloquy" project description is accurate and strong
- Local LLM + PDF chat with "no data leaves your machine" is a compelling differentiator.

**F-11** | "OpenAI-Retro-SuperMarioWorld-SNES" title is long and repository-name-specific
- Consider a display title like "NEAT AI Agent — Super Mario World" and a secondary note for the repository name.

---

### 3. Information Architecture

**F-12** | Section order is correct per the design document
- Hero → Navigation → About → Current Focus → Stats → Ecosystem → Orgs → Projects → Principles → Stack → Research → Creative → Activity → Contact → Footer.
- This matches `docs/DESIGN.md`'s recommended layout.

**F-13** | Navigation ToC uses emoji+text anchors
- GitHub Markdown anchors with emoji prefix (e.g., `#-about`, `#️-project-ecosystem`) are generated by GitHub from headings. The `#️-project-ecosystem` anchor includes a variation selector (`️`) which may not render identically on all GitHub UI contexts.
- **Verify** all navigation links resolve in the live profile.

**F-14** | The "Project Ecosystem" section is a unique visual differentiator
- The ASCII tree diagram of "Personal OS" components is distinctive and communicates systems thinking.
- No other change needed here.

**F-15** | No explicit "What I'm looking for" or "Open to" signal
- Profiles targeting recruiters benefit from an explicit availability or role-type signal ("Open to senior IC and tech lead roles in..." or similar).
- This could be a one-liner in the Contact or About sections.

---

### 4. Visual Design

**F-16** | Branding SVG assets are present and valid
- `assets/branding/header.svg`, `footer.svg`, and `logo.svg` all parse as valid SVG/XML.
- Logo is present but not embedded in the README.

**F-17** | Generated artifact SVGs are absent — critical gap
- `.github/artifacts/github-stats/` contains only a `README.md` placeholder.
- `overview.svg`, `languages.svg`, and `contributions.svg` have not been generated.
- The README embeds these paths, so the GitHub Statistics section currently shows three broken image placeholders on the live profile.
- **This is the highest-priority visual issue.**

**F-18** | Technology stack devicons use CDN with no fallback
- `cdn.jsdelivr.net/gh/devicons/devicon/...` is a reliable CDN but a CDN outage would render the entire tech stack section as missing icons.
- This is an accepted trade-off for profile READMEs; no change is required, but it should be noted.

**F-19** | Dark and light mode not yet tested (Phase 5 incomplete)
- `docs/ROADMAP.md` shows Phase 5 (Visual Polish) as incomplete.
- Branding SVGs should be tested in both GitHub themes before migration is declared complete.

**F-20** | Badge row in the hero section is appropriately sized
- Five badges is within the recommended maximum of six.
- Badge style (`for-the-badge`, `labelColor=1a1a2e`, `color=4a4e69`) is consistent throughout.

---

### 5. Accessibility

**F-21** | Hero and footer SVGs have descriptive alt text
- `header.svg`: `alt="Alan Szmyt — Software Engineer · AI Builder · Systems Thinker · Creative Technologist"` — good.
- `footer.svg`: same alt text — acceptable.

**F-22** | Technology stack icon alt text is minimal but present
- Icons use single-word alt text (`alt="Python"`, `alt="Docker"` etc.).
- This is correct for technology logos; no screen-reader confusion expected.

**F-23** | Generated SVG artifacts lack alt text (when they exist)
- `overview.svg`: `alt="GitHub Overview"` — minimal but acceptable.
- `languages.svg`: `alt="Top Languages"` — acceptable.
- `contributions.svg`: `alt="Contribution Calendar"` — acceptable.
- These can be improved with more descriptive text (e.g., "GitHub contribution statistics for @szmyty") but current text meets baseline accessibility.

**F-24** | Navigation ToC uses collapsible `<details>` element
- Keyboard and screen-reader users can access the navigation.
- No issues identified.

---

### 6. Links and Assets

**F-25** | Internal relative asset paths are correct
- `./assets/branding/header.svg` — file exists at this path.
- `./assets/branding/footer.svg` — file exists at this path.
- `.github/artifacts/github-stats/overview.svg` — file does **not** exist (pending workflow run).
- `.github/artifacts/github-stats/languages.svg` — file does **not** exist.
- `.github/artifacts/github-stats/contributions.svg` — file does **not** exist.

**F-26** | External service links are structurally correct
- LinkedIn: `https://www.linkedin.com/in/alanszmyt` — cannot verify live connectivity from CI, but URL is well-formed.
- Portfolio: `https://szmyty.vercel.app` — requires manual verification that the Vercel deployment is live.
- Email: `mailto:szmyty@gmail.com` — well-formed; no concern.

**F-27** | Featured Projects — two entries link to profile root, not repos
- "Homelab" badge: `https://github.com/szmyty` — links to profile, not a repo.
- "Resume Generator" badge: `https://github.com/szmyty` — links to profile, not a repo.
- This is a broken navigation experience for visitors.

**F-28** | No hardcoded `profile-next` in workflows or scripts
- Both `.github/workflows/github-stats.yml` and `.github/workflows/activity.yml` use `${{ github.repository_owner }}` correctly.
- No hardcoded `szmyty/profile-next` found in workflow files.

**F-29** | No hardcoded `profile-next` in README or assets
- `grep` scan confirms no production file contains `profile-next` as a hardcoded dependency.
- Occurrences in documentation files (`AGENTS.md`, `docs/*.md`) are contextual references, not production dependencies. ✅

**F-30** | `.references/` is not referenced from any production workflow or README
- All `.references/` mentions in documentation are explanatory/historical. ✅

---

### 7. Generated Modules

#### Module: `github-stats`

| Attribute | Status |
|-----------|--------|
| Purpose | Generate GitHub contribution metrics SVGs |
| Inputs | GitHub API via `lowlighter/metrics` |
| Outputs | `overview.svg`, `languages.svg`, `contributions.svg` |
| Refresh schedule | Daily at 06:00 UTC |
| Failure behavior | `continue-on-error` not set; workflow fails silently on API error without explicit artifact preservation |
| Artifact ownership | `.github/artifacts/github-stats/` |
| README integration | Embedded at correct relative paths |
| Test coverage | None |
| Portability | ✅ Uses `${{ github.repository_owner }}` |
| Current correctness | ❌ No artifacts generated yet |
| Maintenance risk | Medium — `lowlighter/metrics@latest` is unpinned |

**F-31** | `lowlighter/metrics@latest` is an unpinned, floating action reference
- Using `@latest` exposes the workflow to supply-chain attacks and unexpected breaking changes.
- **Recommendation:** Pin to a specific release tag (e.g., `@v3.34` or a SHA) and use Dependabot to keep it updated.

**F-32** | `output_action: none` pattern requires explicit push step
- The workflow uses `output_action: none` for all three metrics steps and then runs a single `git commit && git push` step. This is correct and efficient.
- The commit step uses `git diff --staged --quiet || git commit ...` which correctly skips commits when nothing changed. ✅

**F-33** | No `.github/specs/github-stats.spec.md` exists
- Per ROADMAP, this is a known incomplete item.
- Should be created as part of completing Phase 4.

**F-34** | No failure-protection on artifact delete
- If `lowlighter/metrics` fails during generation, the workflow fails at that step and never reaches the commit step. The existing committed artifacts are safe.
- However, no `continue-on-error: true` is set, so a failure in step 2 prevents step 3 from running. If `output_action: none` is used and the action crashes mid-way, partial writes to the local file system could be committed. This is low risk with the current implementation.

#### Module: `activity`

| Attribute | Status |
|-----------|--------|
| Purpose | Update README with recent GitHub activity |
| Inputs | GitHub API via `jamesgeorge007/github-activity-readme` |
| Outputs | Updates `README.md` between `START_SECTION:activity` / `END_SECTION:activity` markers |
| Refresh schedule | Daily at 06:00 UTC |
| Failure behavior | Not explicitly hardened |
| Artifact ownership | In-place README mutation |
| README integration | Markers present in README |
| Test coverage | None |
| Portability | ✅ Uses `${{ github.repository_owner }}` |
| Current correctness | ❌ No activity rendered yet |
| Maintenance risk | High — `jamesgeorge007/github-activity-readme@master` is pinned to `master` |

**F-35** | `jamesgeorge007/github-activity-readme@master` is a floating branch reference
- This is the highest-severity action pinning issue. The `@master` ref means any push to that repository's master branch can change the action's behavior without a version bump.
- **Recommendation:** Pin to a specific tag or commit SHA.

**F-36** | Activity workflow modifies README directly
- This pattern (in-place README mutation) is more fragile than the commit-artifact pattern used by `github-stats`.
- If the activity section markers are accidentally removed from README.md, the workflow will fail or append content outside the section.
- **Recommendation:** Consider adding a validation step that confirms the markers exist before running the action.

**F-37** | No `.github/specs/activity.spec.md` exists
- Known incomplete item per ROADMAP.

#### Module: `branding` (static)

| Attribute | Status |
|-----------|--------|
| Purpose | Visual header, footer, and logo assets |
| Outputs | `assets/branding/header.svg`, `footer.svg`, `logo.svg` |
| Current correctness | ✅ All three SVG files are present and valid XML |
| Maintenance risk | Low |

**F-38** | `logo.svg` is not embedded in the README
- The logo exists as a hand-authored asset but is not used anywhere in the README.
- This may be intentional (reserved for future use), but it should be documented or removed if it has no purpose.

---

### 8. GitHub Actions

**F-39** | Both workflows correctly support `workflow_dispatch` ✅

**F-40** | Both workflows use `concurrency` groups to prevent overlapping runs ✅

**F-41** | Both workflows use `[skip ci]` in commit messages to prevent recursive loops ✅

**F-42** | `github-stats.yml` uses `permissions: contents: write` — this is appropriate for committing artifacts, but it is broader than `read` ✅ (least privilege for this purpose)

**F-43** | `activity.yml` uses `permissions: contents: write` — same note as above ✅

**F-44** | Workflow schedules are both `0 6 * * *` (daily at 06:00 UTC)
- Both workflows running at the same time on the same branch could create a race condition if both commit to the same branch simultaneously.
- The `concurrency` group names are different (`github-stats` vs. `activity`), so they will not cancel each other.
- However, if both succeed in the same minute, there may be a `git push` conflict.
- **Recommendation:** Stagger the schedules (e.g., `github-stats` at 06:00, `activity` at 06:30).

**F-45** | `github-stats.yml` fetches with `fetch-depth: 0` — this is required for the commit step to work correctly ✅

**F-46** | `activity.yml` does not specify `fetch-depth`
- The activity workflow does not set `fetch-depth`. The default is `1` (shallow clone).
- For a workflow that commits to the branch, a shallow clone is sufficient since it only needs the latest state.
- No issue here, but it should be noted for consistency.

**F-47** | No timeout is set on either workflow
- Long-running API calls (e.g., metrics generation) could run for the full GitHub Actions default timeout (6 hours).
- **Recommendation:** Add `timeout-minutes: 10` at the job level.

**F-48** | No Dependabot configuration for GitHub Actions
- No `.github/dependabot.yml` exists.
- This means unpinned action versions will not be automatically updated.
- **Recommendation:** Add a `dependabot.yml` with `package-ecosystem: "github-actions"`.

---

### 9. Security and Privacy

**F-49** | No committed secrets found
- Full scan of all tracked files reveals no API keys, tokens, or credentials. ✅

**F-50** | `METRICS_TOKEN` secret is correctly used and documented
- The `github-stats.yml` workflow uses `${{ secrets.METRICS_TOKEN }}` for the external PAT.
- The secret is documented in `docs/MIGRATION.md`.
- The token's required scopes (`read:user`, `repo`) are documented. ✅

**F-51** | No biometric, health, or location data present ✅

**F-52** | No private repository names or contribution data exposed ✅

**F-53** | `lowlighter/metrics@latest` supply-chain risk
- As noted in F-31. An unpinned `@latest` action from an external repository is a supply-chain risk.
- **Severity: High.**

**F-54** | `jamesgeorge007/github-activity-readme@master` supply-chain risk
- As noted in F-35. An unpinned `@master` branch ref is a higher-severity supply-chain risk.
- **Severity: High.**

**F-55** | `.references/` directory is committed to the repository
- The `.references/` directory contains three cloned reference repositories (`szmyty`, `profile`, `egohygiene`).
- These repositories are present as git submodule-style directories under `.references/`.
- `PLAN.md` explicitly states: "Remove `.references/` before final migration."
- This is not yet a privacy risk (the references are public), but it is a cleanliness requirement before production migration.
- `.gitignore` notes that `.references/` should be excluded from production, but it is currently tracked.

---

### 10. Repository Architecture

**F-56** | Directory structure is clean and matches documented architecture ✅
- The layout matches `docs/ARCHITECTURE.md` exactly.
- No unexpected files at the root level (other than `.references/` and `profile-next.code-workspace`, which are staging-only).

**F-57** | `profile-next.code-workspace` is present in the repository
- This file is a VS Code workspace configuration.
- `.gitignore` includes `profile-next.code-workspace` and `*.code-workspace`, but the file is tracked (committed before the gitignore rule was added or was explicitly added).
- **Verify:** Run `git ls-files profile-next.code-workspace` to confirm whether the file is tracked.
- If tracked: run `git rm --cached profile-next.code-workspace` and re-commit.

**F-58** | `.github/scripts/` is empty (contains only `.gitkeep`)
- No Python scripts exist yet. This is expected for the current phase.

**F-59** | `tests/` directory is empty (no test files)
- No Python scripts to test yet, which is expected.
- However, no test infrastructure means there is no validation gate before commits.

**F-60** | `.engineering/` directory does not yet exist
- This audit creates the first file in this directory.
- The directory naming convention (`.engineering/`) is not documented in `docs/ARCHITECTURE.md`.
- **Recommendation:** Add `.engineering/` to the architecture documentation after this audit is committed.

---

### 11. Code Quality

**F-61** | Workflow YAML is clean, well-commented, and readable ✅
- Both workflow files are concise and follow the documented patterns.
- Commit messages use the conventional commit format (`chore(artifacts): ...`). ✅

**F-62** | No Python scripts to review yet
- The `pyproject.toml` is well-configured with `ruff`, `mypy`, and `pytest`.
- Once scripts are added, they should be validated with `ruff check .` and `mypy`.

**F-63** | `pyproject.toml` references `setuptools` as a build system
- For a repository with no distributable package, this is heavier than necessary.
- This is a minor cleanup opportunity once Python scripts are in place.

---

### 12. Testing and Validation

**F-64** | No tests exist
- The `tests/` directory is empty.
- `pytest` is configured but no test files exist.
- Running `python -m pytest tests/` produces no output (no tests, no failures).
- This is acceptable during the foundation phase but must be addressed as Python modules are implemented.

**F-65** | SVG files validate as well-formed XML ✅
- `assets/branding/header.svg`, `footer.svg`, and `logo.svg` all parse as valid XML.

**F-66** | Workflow YAML files are syntactically valid ✅
- Both workflow files can be parsed as valid YAML.

**F-67** | Secret scan result: clean ✅
- No secrets, tokens, or credentials found in any tracked file.

**F-68** | Portability scan: no hardcoded `profile-next` in production paths ✅
- All references to `profile-next` are in documentation that describes the staging process, not in production code.

**F-69** | Portability scan: no runtime dependency on `.references/` ✅
- No workflow or script imports from or references `.references/`.

---

### 13. Documentation Accuracy

**F-70** | `docs/ROADMAP.md` accurately reflects current implementation state ✅
- Phase 1, 2, 3 marked complete. Phase 4 partial. Phases 5-7 not started.
- Two items in Phase 4 are marked incomplete (specs for github-stats and activity).
- This is an accurate representation of the repository state.

**F-71** | `docs/ARCHITECTURE.md` is accurate ✅
- Describes the actual directory structure, data flow, and automation model correctly.

**F-72** | `docs/MODULES.md` describes a more detailed lifecycle than is currently implemented
- The module lifecycle (Provider → Normalizer → Renderer) is documented but no modules use this pattern yet.
- `lowlighter/metrics` is a third-party action, not a custom provider/normalizer/renderer pipeline.
- This is acceptable for the current phase, but the documentation implies more structure than currently exists.

**F-73** | `AGENTS.md` `.engineering/` directory is not documented
- The `AGENTS.md` file does not mention `.engineering/audits/` as a valid path.
- After this audit, `AGENTS.md` should be updated to document the `.engineering/` structure.

**F-74** | `docs/DESIGN.md` anti-patterns section is thorough and matches implementation ✅

---

### 14. Repository Cleanup

**F-75** | `.references/` directory should be removed before production migration
- Contains three reference repositories: `szmyty`, `profile`, `egohygiene`.
- These are development context only.
- `PLAN.md` explicitly requires their removal before migration.
- **Action required before production cutover.**

**F-76** | `profile-next.code-workspace` may be tracked in git
- Needs verification. If tracked, should be removed via `git rm --cached`.

**F-77** | No stale or obsolete files found beyond the above ✅

---

### 15. Performance and Efficiency

**F-78** | Both workflows run daily on the same schedule — minor race condition risk
- As noted in F-44. Staggering by 30 minutes is recommended.

**F-79** | No dependency caching in either workflow
- `github-stats.yml` uses `lowlighter/metrics` which installs its own dependencies.
- `activity.yml` is similarly self-contained.
- Caching is not applicable for these workflows.

**F-80** | Repository size is appropriately small
- Only committed source files, branding SVGs, and the artifacts README placeholder.
- No binary files (beyond SVGs), no lock files, no large generated outputs.

---

### 16. Future Opportunities

**F-81** | Resume/CV integration is a high-value addition for recruiter audiences
- A link to a hosted, maintained résumé (Vercel-hosted PDF or web page) would improve recruiter discoverability.

**F-82** | Organization card generation could replace the static HTML table
- Currently the Organizations section is hand-authored HTML.
- Automated organization cards (auto-updated with repo counts, member counts) would reduce maintenance.
- **Deferred** — appropriate for a post-migration enhancement issue.

**F-83** | Contribution heatmap alternative
- The `contributions.svg` will be generated by `lowlighter/metrics`, but a custom Python-rendered contribution heatmap could offer more design control.
- **Deferred** — appropriate for a post-foundation enhancement.

**F-84** | Module consolidation opportunity
- Both `github-stats` and `activity` run on the same schedule.
- A single "profile update" workflow could run both in sequence, reducing the chance of simultaneous commits.
- **Low priority** — current architecture is not problematic.

---

## Prioritized Recommendation Table

| Priority | ID | Title | Domain | Severity |
|----------|-----|-------|--------|----------|
| **Critical** | F-17 | Generate GitHub Statistics SVG artifacts | Generated Modules | Critical |
| **Critical** | F-05 | Render or remove empty activity section | Public Profile | Critical |
| **Critical** | F-53/F-54 | Pin `lowlighter/metrics` and `github-activity-readme` actions to version tags | Security | High |
| **High** | F-27 | Fix placeholder project links (Homelab, Resume Generator) | Links & Assets | High |
| **High** | F-75 | Remove `.references/` before production cutover | Repository Cleanup | High |
| **High** | F-44 | Stagger workflow schedules to avoid commit race condition | GitHub Actions | Medium |
| **High** | F-47 | Add `timeout-minutes` to both workflows | GitHub Actions | Medium |
| **High** | F-48 | Add Dependabot configuration for GitHub Actions | Security | Medium |
| **Medium** | F-04 | Add résumé or CV link to Contact section | Content | Medium |
| **Medium** | F-15 | Add "Open to" or availability signal in About/Contact | Content | Medium |
| **Medium** | F-19 | Complete Phase 5: test in GitHub light and dark mode | Visual Design | Medium |
| **Medium** | F-36 | Add marker-existence check to activity workflow | GitHub Actions | Medium |
| **Medium** | F-57 | Untrack `profile-next.code-workspace` if currently tracked | Repository Cleanup | Low |
| **Medium** | F-76 | Verify and remove `.code-workspace` from git tracking | Repository Cleanup | Low |
| **Low** | F-11 | Improve "OpenAI-Retro-SuperMarioWorld-SNES" display title | Content | Low |
| **Low** | F-08 | Reduce "Current Focus" from 6 to 4 items | Content | Low |
| **Low** | F-33/F-37 | Create missing module specs | Documentation | Low |
| **Low** | F-60 | Document `.engineering/` directory in ARCHITECTURE.md | Documentation | Low |
| **Low** | F-73 | Update AGENTS.md to document `.engineering/` convention | Documentation | Low |
| **Low** | F-38 | Document or remove unused `logo.svg` | Repository Cleanup | Informational |

---

## Suggested GitHub Issue Roadmap

The following issues are recommended as focused, independently reviewable work items. They are ordered by priority.

---

### Issue 1: Generate GitHub Statistics Artifacts

**Title:** 🔧 Run `github-stats` workflow and commit initial artifacts
**Objective:** Trigger the `github-stats` workflow via `workflow_dispatch`, verify all three SVGs are generated and committed, and confirm the GitHub Statistics section renders correctly on the live profile.
**Scope:**
- Trigger `.github/workflows/github-stats.yml` manually.
- Verify `overview.svg`, `languages.svg`, `contributions.svg` are generated.
- Verify README renders correctly in both GitHub themes.
**Dependencies:** Requires `METRICS_TOKEN` secret to be configured in the production repository.
**Priority:** P0 — blocks profile visibility.
**Expected validation:** Three SVG files exist in `.github/artifacts/github-stats/`; README GitHub Statistics section shows rendered visualizations.
**Copilot-suitable:** No — requires secret configuration and manual workflow run in the production repository.

---

### Issue 2: Pin GitHub Actions to Specific Release Tags

**Title:** 🔒 Pin `lowlighter/metrics` and `github-activity-readme` actions to version tags
**Objective:** Replace `@latest` and `@master` action refs with pinned version tags or commit SHAs. Add a Dependabot configuration for automated action updates.
**Scope:**
- Pin `lowlighter/metrics@latest` to a specific tag (e.g., `lowlighter/metrics@v3.34`).
- Pin `jamesgeorge007/github-activity-readme@master` to a specific tag.
- Create `.github/dependabot.yml` with `package-ecosystem: "github-actions"`.
**Dependencies:** None.
**Priority:** P1 — security requirement.
**Expected validation:** Workflow files reference pinned versions; Dependabot config is valid.
**Copilot-suitable:** Yes.

---

### Issue 3: Fix Placeholder Project Links

**Title:** ✏️ Fix placeholder project links in Featured Projects section
**Objective:** Replace the two "link to profile root" badges with either real repository links or alternative projects.
**Scope:**
- "Homelab" — link to a real repository or mark as a future section.
- "Resume Generator" — link to a real repository or mark as a future section.
- Optionally add a third complete project to fill the table.
**Dependencies:** Requires knowledge of which public repositories exist.
**Priority:** P1 — broken navigation for profile visitors.
**Expected validation:** All "View Repo" badges link to specific GitHub repositories.
**Copilot-suitable:** Partially — requires human confirmation of correct repository URLs.

---

### Issue 4: Trigger Activity Workflow and Verify Activity Section

**Title:** ⚡ Trigger `activity` workflow and verify activity section renders
**Objective:** Run the activity workflow, confirm the `START_SECTION:activity` / `END_SECTION:activity` block is populated, and verify the section renders on the live profile.
**Scope:**
- Trigger `.github/workflows/activity.yml` manually.
- Verify README is updated with recent activity.
- Stagger the `activity` workflow schedule to `30 6 * * *` to avoid race condition with `github-stats`.
**Dependencies:** None (uses `GITHUB_TOKEN`).
**Priority:** P1 — empty section looks broken.
**Expected validation:** Activity section shows ≥1 recent activity item; workflows do not conflict.
**Copilot-suitable:** Yes (for schedule change); No (for manual run).

---

### Issue 5: Complete Phase 5 Visual Polish

**Title:** 🎨 Review and polish profile rendering in GitHub light/dark mode
**Objective:** Open `github.com/szmyty` in GitHub light mode and dark mode, identify any visual issues (SVG clipping, contrast, wrapping), and fix any found.
**Scope:**
- Test in GitHub light mode (desktop).
- Test in GitHub dark mode (desktop).
- Test at narrow viewport (mobile).
- Verify SVG alt text, link resolution, and image loading.
- Fix any identified issues.
**Dependencies:** Issue 1 must be completed first (artifacts must be present).
**Priority:** P2.
**Expected validation:** No visual issues in either theme; all Phase 5 ROADMAP items checked.
**Copilot-suitable:** Partially — requires human visual inspection.

---

### Issue 6: Add Résumé Link and Role Signal

**Title:** 📄 Add résumé link and availability/role signal to profile
**Objective:** Add a résumé link to the Contact section. Add a brief "open to" statement to the About or Contact section.
**Scope:**
- Add a résumé badge in the Contact section (e.g., hosted PDF on Vercel or Google Drive).
- Add a one-line availability/role statement ("Open to senior engineering roles in cloud-native and AI tooling").
**Dependencies:** Alan provides résumé URL.
**Priority:** P2.
**Expected validation:** Contact section includes résumé link; About or Contact includes role signal.
**Copilot-suitable:** Partially — Alan must provide résumé URL and review tone.

---

### Issue 7: Add `timeout-minutes` and Stagger Schedules in Workflows

**Title:** ⚙️ Harden workflows with timeouts and staggered schedules
**Objective:** Add `timeout-minutes: 10` to both workflow jobs. Stagger the `activity` schedule to `30 6 * * *`.
**Scope:**
- `github-stats.yml` — add `timeout-minutes: 10`.
- `activity.yml` — add `timeout-minutes: 10` and change schedule to `30 6 * * *`.
**Dependencies:** None.
**Priority:** P3.
**Expected validation:** Workflow YAML is valid; schedules differ by 30 minutes.
**Copilot-suitable:** Yes.

---

### Issue 8: Remove `.references/` and Finalize Migration Readiness

**Title:** 🧹 Remove `.references/` and complete migration readiness checklist
**Objective:** Remove the `.references/` development context directory. Complete all Phase 6 ROADMAP checklist items. Declare the repository migration-ready.
**Scope:**
- Remove `.references/` from the repository (or confirm it's untracked and gitignored).
- Untrack `profile-next.code-workspace` if tracked.
- Complete Phase 6 validation checklist in `docs/ROADMAP.md`.
**Dependencies:** All P0-P2 issues complete.
**Priority:** P3.
**Expected validation:** No `.references/` in tracked files; Phase 6 checklist complete.
**Copilot-suitable:** Yes.

---

### Issue 9: Write Module Specifications

**Title:** 📋 Create `.github/specs/` for `github-stats` and `activity` modules
**Objective:** Write specification files for the two implemented modules, documenting purpose, inputs, outputs, schema, failure behavior, and acceptance criteria.
**Scope:**
- `.github/specs/github-stats.spec.md`.
- `.github/specs/activity.spec.md`.
**Dependencies:** None.
**Priority:** P4.
**Expected validation:** Both spec files exist and match the workflow implementation.
**Copilot-suitable:** Yes.

---

### Issue 10: Update ARCHITECTURE.md to Document `.engineering/` Convention

**Title:** 📖 Document `.engineering/` directory in ARCHITECTURE.md and AGENTS.md
**Objective:** Update architecture and agent documentation to reflect the `.engineering/audits/` convention introduced by this audit.
**Scope:**
- Add `.engineering/` to the directory tree in `docs/ARCHITECTURE.md`.
- Add a note to `AGENTS.md` documenting the `.engineering/` convention.
**Dependencies:** This audit must be committed first.
**Priority:** P4.
**Expected validation:** Both documentation files reference `.engineering/`.
**Copilot-suitable:** Yes.

---

## Validation Evidence

The following checks were run locally during this audit:

| Check | Command | Result |
|-------|---------|--------|
| Secret scan | Manual review of all tracked files | ✅ No secrets found |
| SVG validity | `python3 -c "import xml.etree.ElementTree as ET; ET.parse('assets/branding/header.svg')"` | ✅ Valid |
| SVG validity | `python3 -c "import xml.etree.ElementTree as ET; ET.parse('assets/branding/footer.svg')"` | ✅ Valid |
| SVG validity | `python3 -c "import xml.etree.ElementTree as ET; ET.parse('assets/branding/logo.svg')"` | ✅ Valid |
| `profile-next` portability scan | `grep -r "profile-next" .github/workflows/ README.md assets/` | ✅ None found in production files |
| `.references` portability scan | `grep -r ".references" .github/workflows/ README.md` | ✅ None found in workflows or README |
| Tests | `python -m pytest tests/ -v` | ⚠️ No tests found (expected — no scripts yet) |
| Generated artifacts | `ls .github/artifacts/github-stats/` | ❌ Only `README.md` placeholder; no SVGs |
| Working tree | `git status` | ✅ Clean |
| Workflow YAML | Manual parse of both workflow files | ✅ Valid syntax |
| Image path verification | Extract all `src=` paths from README, verify local files exist | ⚠️ Three paths reference not-yet-generated SVGs |
| Anchor verification | Extract all `#anchor` links from navigation ToC | ⚠️ Emoji anchors require live GitHub verification |

**Checks requiring live GitHub access (cannot be verified locally):**

- Portfolio link (`https://szmyty.vercel.app`) — verify the site is live.
- LinkedIn link (`https://www.linkedin.com/in/alanszmyt`) — verify the profile exists and is public.
- GitHub anchor resolution — verify emoji-prefixed ToC links resolve correctly in the GitHub Markdown renderer.
- Light mode rendering — requires opening `github.com/szmyty` in a browser with light theme.
- Dark mode rendering — requires opening `github.com/szmyty` in a browser with dark theme.
- Narrow/mobile rendering — requires browser developer tools or a mobile device.

---

## Explicitly Deferred Ideas

The following ideas are credible future enhancements but are intentionally out of scope for the next iteration:

| Idea | Reason for deferral |
|------|---------------------|
| Custom Python-rendered GitHub stats SVGs | `lowlighter/metrics` is sufficient; custom renderer adds maintenance cost without clear gain at this stage |
| Music streaming activity card | API strategy not defined; privacy implications require review |
| Organization card automation | Static HTML is sufficient until there is clear maintenance burden |
| Profile summary cards (`profile-summary-card-output`) | Requires private PAT for the action; dependency on an external action with limited controls |
| Personal knowledge management export | Architecture not defined; significant complexity |
| Contribution graph redesign | High visual complexity; acceptable to use `lowlighter/metrics` output |
| Oura / biometric data | Privacy violation — explicitly prohibited |
| Location card | Privacy violation — explicitly prohibited |
| Full dashboard application (Node.js) | Overengineered for a profile repository; discarded in reference inventory |
| Ko-fi / sponsorship widget | Low signal; adds visual noise without career-relevant content |

---

## Explicit Non-Recommendations

The following ideas were considered and deliberately rejected:

| Idea | Reason for rejection |
|------|---------------------|
| Rebuild as a generic Personal OS framework | Adds abstraction overhead without concrete benefit; the profile is the product |
| Add a `CONTRIBUTING.md` | Personal profile repositories do not require contribution guides |
| Add a `SECURITY.md` | Disproportionate formality for a profile repository |
| Add `CHANGELOG.md` / semantic versioning | Versioned changelogs are unnecessary for a personal profile |
| Migrate to Node.js tooling | Contradicts the documented Python-first architecture |
| Replace `lowlighter/metrics` with a fully custom Python pipeline | Premature optimization; `lowlighter/metrics` is battle-tested and well-maintained |
| Add test coverage for branding SVGs | SVG asset validation is better done by XML parse; formal test suite overhead is disproportionate |
| Use GitHub Pages or a separate repository for the portfolio | Out of scope; the portfolio is already hosted at `szmyty.vercel.app` |
| Add a `CODE_OF_CONDUCT.md` | Unnecessary formality for a personal profile |

---

*Audit prepared by GitHub Copilot coding agent. All findings are based on static analysis of tracked repository contents as of the audit date. Live GitHub rendering and external service availability require manual verification.*
