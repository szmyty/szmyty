# Final Profile Readiness Report

Date: 2026-08-09 (UTC)
Issue: szmyty/szmyty#119
Queue key: `szmyty-profile-finalize-13`

## Recommendation

**READY WITH MANUAL SETUP**

Rationale: the public profile surface is polished, privacy-bounded, and locally
green (`303 passed`), the latest `CI` run on `master` succeeded (`31340834598`),
and the latest `Pages` run succeeded (`31337341343`). The remaining work is
manual owner verification of GitHub UI settings plus one bounded
medium-severity follow-up for an `Update Profile` issue-event push race
(`31340834869`) that did not corrupt public output because the latest
push-triggered refresh on `master` already succeeded (`31340834587`).

---

## Scope and evidence sources

- Repository contracts reviewed before changes:
  - `/home/runner/work/szmyty/szmyty/AGENTS.md:12-22`
  - `/home/runner/work/szmyty/szmyty/docs/ARCHITECTURE.md:98-131`
  - `/home/runner/work/szmyty/szmyty/docs/PRIVACY.md:7-37`
  - `/home/runner/work/szmyty/szmyty/docs/CONTENT.md:13-55`
  - `/home/runner/work/szmyty/szmyty/docs/DEVELOPMENT.md:54-147`
- Local validation evidence came from a clean working tree plus the commands in
  [Repository and local validation](#repository-and-local-validation).
- GitHub workflow and metadata evidence came from workflow runs
  `31340834598` (`CI`), `31340834587` and `31340834869` (`Update Profile`),
  `31337341343` (`Pages`), repository search metadata, and discussion-category
  APIs.
- Rendered-experience evidence came from committed README/site sources and their
  corresponding tests because live Pages HTTP probes from this audit environment
  failed DNS resolution for `https://szmyty.github.io/szmyty/`.

---

## Repository and local validation

### Clean checkout and locked dependency install

Command:

```bash
python -m pip install poetry==2.1.4
poetry install --with lint,test --no-interaction --no-root
```

Result: install completed successfully in a clean checkout; `git status --short`
was empty before the audit commands ran.

### Validation, lint, format, schema, tests, and site checks

Commands and exact outcomes:

```bash
poetry run python -m tools.profile_builder.cli validate
# evidence: 44 entries — 12 verified, 28 needs-user-verification, 4 excluded
# modules: 13 declared — 4 enabled
# validate: OK

poetry run python profile/validate_assets.py assets/profile
# Asset validation passed — assets/profile

bash .tasks/check-identity.sh
# Identity check PASSED: no stale repository references found.

poetry run ruff check .
# All checks passed!

poetry run ruff format --check .
# 40 files already formatted

poetry run yamllint .github/workflows .github/dependabot.yml Taskfile.yml
# exited 0 with no findings

poetry run python -m pytest tests/test_workflows.py -k "workflow or site"
# 16 passed in 0.13s

poetry run python -m pytest
# 303 passed in 1.07s
```

Additional module-state evidence:

```bash
poetry run python -m tools.profile_builder.cli registry
poetry run python -m tools.profile_builder.cli snapshot
```

- Registry output confirms `13` declared modules and `4` enabled modules.
- Snapshot output confirms the disabled modules stay disabled and that the live
  AI-agent showcase currently presents `FAILED-WITH-FALLBACK` state rather than
  inventing replacement content.

### Renderer idempotency and semantic no-op behavior

Command:

```bash
poetry run python -m tools.modules.update_readme
poetry run python -m tools.modules.update_readme
```

Observed results during the audit:

- First pass: `github-metrics unchanged`, `recent-activity updated`,
  `ai-agent-showcase unchanged`, `music-highlight unchanged`.
- Second pass: all four enabled modules reported `unchanged`.

Interpretation: renderer no-op behavior is verified after README/artifact
synchronization, matching the existing region tests at
`/home/runner/work/szmyty/szmyty/tests/test_modules.py:470-564` and
`/home/runner/work/szmyty/szmyty/tests/test_profile_builder_regions.py:131-157`.
The audit reverted the temporary working-tree mutations immediately after
capturing this evidence.

### Repository footprint and budgets

Tracked-footprint command result (excluding `.git`, `.venv`, caches):

```text
tracked_bytes 1288518
tracked_mb 1.23
```

Key budget results:

```text
README.md 9162 bytes
site/index.html 12993 bytes
site/ai-agent-showcase.html 12530 bytes
core_js_bytes 3014
observatory_bundle_bytes 347719
observatory_js_bytes 8883
three_vendor_bytes 338836
site_plus_preview_images_bytes 61081
```

Assessment:

- README is comfortably below typical GitHub rendering budgets at `9162` bytes.
- Site HTML pages are below the site budget of `≤ 50 KB` per page
  (`/home/runner/work/szmyty/szmyty/site/README.md:43-53`).
- Core JS (`3014` bytes) is below the `≤ 10 KB` budget and the lazy
  observatory bundle (`347719` bytes) is below the documented `≤ 380 KB`
  budget (`/home/runner/work/szmyty/szmyty/site/README.md:47-51`,
  `/home/runner/work/szmyty/szmyty/tests/test_interactive_observatory.py:46-59`).
- Profile asset validation passed and the tracked SVG sizes remain within the
  budgets declared in
  `/home/runner/work/szmyty/szmyty/assets/profile/README.md:10-16`.

### Tracked-secret and raw-provider-data scan

Regex scan across `README.md`, `profile/artifacts/`, and `site/` found only
secret *names* in disabled-module metadata, not secret values:

- `/home/runner/work/szmyty/szmyty/profile/artifacts/soundcloud/metadata.json:12-13`
- `/home/runner/work/szmyty/szmyty/profile/artifacts/steam/metadata.json:12-13`
- `/home/runner/work/szmyty/szmyty/profile/artifacts/oura-trends/metadata.json:12-13`

No committed output in those public surfaces matched token prefixes,
private-key headers, `authorization:` headers, or provider credential values.

---

## GitHub surfaces

### Latest workflow conclusions

#### CI

- Latest `master` push run: `31340834598` — **success**
- Prior failed `master` run: `31339094937` — failure reproduced in logs and now
  superseded by the green run above. The failed logs showed a pytest failure in
  `tests/test_ai_agent_showcase.py` before later fixes landed.

#### Update Profile

- Latest `master` push run: `31340834587` — **success**
- Latest run overall: `31340834869` (`issues` event) — **failure**
- Failed-job logs for `31340834869` show the `commit` job created commit
  `58bb484` and then failed on `git push` with
  `! [rejected] master -> master (fetch first)`, which is a classic
  non-fast-forward race after a concurrent push-triggered refresh.

#### Pages

- Latest `Pages` run: `31337341343` — **success**
- Workflow evidence:
  `/home/runner/work/szmyty/szmyty/.github/workflows/pages.yml:59-92`

### Deployed Pages URL and static fallback

- Canonical site URL is hard-coded to `https://szmyty.github.io/szmyty/` in
  `/home/runner/work/szmyty/szmyty/site/index.html:6-15`.
- The AI-agent showcase artifact publishes
  `https://szmyty.github.io/szmyty/ai-agent-showcase.html` from committed
  artifact data:
  `/home/runner/work/szmyty/szmyty/profile/artifacts/ai-agent-showcase/cache.json:118-125`.
- Static fallback is explicit in the README preview bridge:
  `/home/runner/work/szmyty/szmyty/README.md:99-104`, and in the capture flow:
  `/home/runner/work/szmyty/szmyty/site/README.md:54-66`.
- Audit limitation: `web_fetch` from this environment failed DNS resolution for
  both Pages URLs, so live `HTTP 200` remains an owner-verification item in the
  handoff checklist.

### Issue, discussion, and security routing

- Issue-contact routing is correctly bounded:
  `/home/runner/work/szmyty/szmyty/.github/ISSUE_TEMPLATE/config.yml:16-31`.
- Discussion categories currently exposed by GitHub API:
  `Announcements`, `General`, `Ideas`, `Polls`, `Q&A`, `Show and tell`.
- Security reports route to
  `https://github.com/szmyty/szmyty/security/advisories/new`
  (`config.yml:29-31`).
- Local validation covers the routing contract:
  `/home/runner/work/szmyty/szmyty/tests/test_workflows.py:193-228`.

### Repository metadata observable through APIs

Repository API evidence confirms:

- public repository
- default branch `master`
- MIT license
- issues enabled
- discussions enabled
- Pages enabled

This was observed from repository search metadata for `repo:szmyty/szmyty`.

### Owner-only manual settings

Branch protections/rulesets, About text, topics, social preview, pinned
repositories, Pages environment, and Discussions UI state remain partly outside
repository-file observability. Those items are consolidated in
`/home/runner/work/szmyty/szmyty/docs/FINAL-OWNER-HANDOFF-CHECKLIST.md`.

---

## Rendered experience

### First viewport and hiring-manager time-to-trust

- README first view immediately exposes the banner, name, title, navigation
  links, and hiring snapshot:
  `/home/runner/work/szmyty/szmyty/README.md:1-35`.
- Pages first view immediately exposes the hero name, subtitle, summary, and
  GitHub CTA:
  `/home/runner/work/szmyty/szmyty/site/index.html:81-92`.

Assessment: pass. The profile explains who Alan is and what to inspect first
without requiring scroll, JavaScript, or external assets.

### Light, dark, narrow, desktop, and image-disabled behavior

- README theme switching uses a `<picture>` element with light/dark banner
  sources:
  `/home/runner/work/szmyty/szmyty/README.md:3-11`.
- Pages dark mode and contrast mode are encoded in CSS:
  `/home/runner/work/szmyty/szmyty/site/css/theme.css:1-70`.
- Narrow-view behavior is encoded in responsive layout rules, with wrap-aware
  grids and a simplified mobile nav:
  `/home/runner/work/szmyty/szmyty/site/css/layout.css:20-27`,
  `:36-41`, `:88-108`.
- Images are non-blocking because the README keeps the identity heading and
  summary as text outside the banner image:
  `/home/runner/work/szmyty/szmyty/README.md:13-35`.

Assessment: pass for documented light/dark and narrow-layout behavior, with the
remaining live-browser spot check delegated to the owner handoff.

### JavaScript-disabled, WebGL-unavailable, reduced-motion, keyboard, and touch

- The AI-agent showcase declares a semantic fallback list before the script and
  includes a `<noscript>` message:
  `/home/runner/work/szmyty/szmyty/site/ai-agent-showcase.html:48-123`.
- Tests assert the fallback precedes JS, and that reduced motion, WebGL checks,
  keyboard controls, and local Three.js loading are present:
  `/home/runner/work/szmyty/szmyty/tests/test_interactive_observatory.py:16-65`.
- Global skip-link and focus styles support keyboard navigation:
  `/home/runner/work/szmyty/szmyty/site/css/base.css:42-87`.
- Touch-sized controls are explicit in the showcase control buttons:
  `/home/runner/work/szmyty/szmyty/site/ai-agent-showcase.html:55-71`.

Assessment: pass.

### Link/anchor integrity and accessible names

Audit script result:

```text
index.html anchors 19 links 18 missing []
index.html aria_labels 4 buttons 1 img_alts 0
ai-agent-showcase.html anchors 14 links 22 missing []
ai-agent-showcase.html aria_labels 2 buttons 2 img_alts 0
README local_paths 2 missing_paths []
README fragments ['contact'] missing_fragments []
```

Assessment: pass. Internal anchors, local paths, and accessible labels are
present for the reviewed pages.

### Provider failure, disabled-module presentation, and freshness signals

- README explicitly states that dynamic sections render from committed artifacts
  and keep the last-known-good public cache when providers fail:
  `/home/runner/work/szmyty/szmyty/README.md:265-271`.
- The AI-agent showcase exposes its current fallback state without hiding it:
  `/home/runner/work/szmyty/szmyty/profile/artifacts/ai-agent-showcase/metadata.json:1-13`
  and `/home/runner/work/szmyty/szmyty/site/ai-agent-showcase.html:253-258`.
- Disabled modules remain empty between owned markers while adjacent prose
  explains why they are hidden:
  `/home/runner/work/szmyty/szmyty/README.md:78-90`,
  `:178-187`, `:213-249`.
- The refresh workflow publishes per-module outcome/data-source summaries at run
  time:
  `/home/runner/work/szmyty/szmyty/.github/workflows/update-profile.yml:148-179`.

Assessment: pass.

---

## Feature completion matrix

| Item | Final state | Evidence | Remaining owner action |
|---|---|---|---|
| GitHub statistics dashboard | `live` | README metrics + activity sections at `/home/runner/work/szmyty/szmyty/README.md:117-162`; enabled modules in `modules.yml:13-40`; public-only GitHub cache fields in `profile/artifacts/github-metrics/cache.json:1-60` and `profile/artifacts/recent-activity/cache.json:1-25` | None required |
| ORCID/publications | `deferred with durable slot` | Hidden README markers at `/home/runner/work/szmyty/szmyty/README.md:178-187`; disabled registry entries at `modules-registry.yml:99-139`; config gate at `profile/content/orcid-config.yml:1-13`; evidence gate at `profile/content/evidence.yml:390-409` | Supply verified ORCID iD and public profile |
| Medium articles | `deferred with durable slot` | Hidden README markers at `/home/runner/work/szmyty/szmyty/README.md:178-187`; disabled registry entry at `modules-registry.yml:120-139`; config gate at `profile/content/medium-config.yml:1-11`; evidence gate at `profile/content/evidence.yml:413-430` | Supply verified Medium username/profile URL |
| SoundCloud | `static` | Public music highlight at `/home/runner/work/szmyty/szmyty/README.md:191-209` and `profile/artifacts/music-highlight/music.yml:1-7`; dynamic snapshot slot remains disabled in `modules-registry.yml:201-222`; metadata fallback state at `profile/artifacts/soundcloud/metadata.json:1-13` | If live profile snapshot is desired, provide verified public profile plus credentials and enable the module |
| Steam achievements/gamer information | `deferred with durable slot` | Hidden README slot at `/home/runner/work/szmyty/szmyty/README.md:213-219`; disabled registry entry at `modules-registry.yml:224-244`; metadata state at `profile/artifacts/steam/metadata.json:1-13` | Provide `STEAM_ID64`, API key, and enable the module if desired |
| Oura privacy aggregate dashboard | `privacy-gated` | Hidden README slot at `/home/runner/work/szmyty/szmyty/README.md:243-249`; blocked registry entry at `modules-registry.yml:266-290`; static synthetic metadata at `profile/artifacts/oura-trends/metadata.json:1-13`; allowlist tests at `tests/test_oura_trends.py:76-165` | Complete the owner approval checklist in `docs/RUNBOOK.md:299-323` before any enablement |
| Resume | `deferred with durable slot` | Hidden README markers at `/home/runner/work/szmyty/szmyty/README.md:83-90`; disabled registry entry at `modules-registry.yml:161-179`; config gate at `profile/content/resume-config.yml:1-15`; evidence gate at `profile/content/evidence.yml:377-386` | Supply a sanitized public resume artifact that passes `docs/RESUME-CHECKLIST.md` |
| UMass Lowell education card | `deferred with durable slot` | Disabled degree at `/home/runner/work/szmyty/szmyty/profile/content/education-config.yml:9-16`; evidence gate at `profile/content/evidence.yml:351-361`; hidden education region at `README.md:83-87` | Confirm degree title/program URL and optional year, then enable the degree |
| Boston University education card | `deferred with durable slot` | Disabled degree at `/home/runner/work/szmyty/szmyty/profile/content/education-config.yml:18-24`; evidence gate at `profile/content/evidence.yml:363-373`; hidden education region at `README.md:83-87` | Confirm degree title/program URL and optional year, then enable the degree |
| 16Personalities working-style content | `deferred with durable slot` | Hidden README slot at `/home/runner/work/szmyty/szmyty/README.md:221-222`; disabled registry entry at `modules-registry.yml:181-199`; config gate at `profile/content/working-style-config.yml:1-14`; evidence gate at `profile/content/evidence.yml:435-445` | Supply approved type, image path, public URL, and summary |
| STARS source slot | `privacy-gated` | Hidden README slot at `/home/runner/work/szmyty/szmyty/README.md:245-246`; internal registry entry at `modules-registry.yml:246-264`; disabled config at `profile/content/stars-config.yml:1-12`; excluded evidence at `profile/content/evidence.yml:449-459` | Keep disabled unless Alan explicitly selects public-safe items |
| AI-agent showcase | `live` | README showcase section at `/home/runner/work/szmyty/szmyty/README.md:94-113`; committed cache at `profile/artifacts/ai-agent-showcase/cache.json:1-125`; Pages detail at `site/ai-agent-showcase.html:40-258` | None required |
| Three.js Pages experience and README preview | `live` | README preview bridge at `/home/runner/work/szmyty/szmyty/README.md:99-104`; showcase page fallback + script at `site/ai-agent-showcase.html:48-123` and `:260`; observatory tests at `tests/test_interactive_observatory.py:16-65` | None required |
| Ego Hygiene compact architecture | `live` | README architecture narrative at `/home/runner/work/szmyty/szmyty/README.md:166-174`; Pages architecture section and accessible inline SVG at `site/index.html:168-225` | None required |
| Ego Hygiene full-poster slot | `deferred with durable slot` | The current Pages architecture section preserves a future richer asset seam via the inline replacement note at `/home/runner/work/szmyty/szmyty/site/index.html:177-182`; no separate poster artifact is committed today | Only add a separate poster/export if Alan wants a dedicated artifact later |
| Final/interim cosmic visual assets | `static` | Production-interim asset registry at `/home/runner/work/szmyty/szmyty/assets/profile/README.md:3-4` and `:27-51`; asset validator passed locally | Optionally replace interim cosmic SVGs with final approved artwork later |

---

## Security and privacy review

### Secrets are not committed or logged in public artifacts

- Public outputs contain only secret names in disabled-module metadata, not
  values (`soundcloud`, `steam`, `oura-trends` metadata files cited above).
- SoundCloud explicitly never stores tokens in caches or logs:
  `/home/runner/work/szmyty/szmyty/tools/modules/soundcloud.py:16-19`.

### Public caches stay inside the allowlist

- Privacy allowlist/deny-list:
  `/home/runner/work/szmyty/szmyty/docs/PRIVACY.md:7-30`.
- GitHub metrics fetch path excludes private and fork repositories:
  `/home/runner/work/szmyty/szmyty/tools/modules/github_metrics.py:94-114`
  and `/home/runner/work/szmyty/szmyty/tests/test_modules.py:429-442`.
- SoundCloud fetches public tracks only and stores artwork URLs as plain text:
  `/home/runner/work/szmyty/szmyty/tools/modules/soundcloud.py:26-30`.
- Steam never exposes exact online status, timestamps, or privacy-hidden data:
  `/home/runner/work/szmyty/szmyty/tools/modules/steam.py:20-27`.
- The committed Oura fixture exposes only coarse monthly aggregate fields:
  `/home/runner/work/szmyty/szmyty/profile/fixtures/oura-trends.json:1-13`.

### Oura leakage review

Observed output and tests show no routine, timestamp, location, illness,
workout, tag, or raw-sample leakage:

- committed public Oura metadata contains only module state and an
  `OURA_ACCESS_TOKEN not set` message:
  `/home/runner/work/szmyty/szmyty/profile/artifacts/oura-trends/metadata.json:1-13`
- allowlist tests reject unknown provider fields, daily arrays, tags, timezone,
  workout records, and auth fields:
  `/home/runner/work/szmyty/szmyty/tests/test_oura_trends.py:76-165`

### Private GitHub activity and private provider records

- Public GitHub data is restricted to public repositories/activity by policy:
  `/home/runner/work/szmyty/szmyty/docs/PRIVACY.md:9-14` and `:58-67`.
- GitHub metrics code and tests enforce that private repos and forks are
  excluded:
  `/home/runner/work/szmyty/szmyty/tools/modules/github_metrics.py:98-114`,
  `/home/runner/work/szmyty/szmyty/tests/test_modules.py:429-442`.

### Remote images and active content

- README profile assets are local SVG files under `assets/profile/`.
- The SoundCloud module stores artwork URLs as text only and does not embed
  active remote content (`soundcloud.py:28-30`).
- The interactive showcase vendors Three.js locally:
  `/home/runner/work/szmyty/szmyty/tests/test_interactive_observatory.py:36-49`.

### Action permissions and untrusted-event behavior

- `CI` uses `pull_request`, not `pull_request_target`, and stays read-only:
  `/home/runner/work/szmyty/szmyty/.github/workflows/ci.yml:3-13`,
  `/home/runner/work/szmyty/szmyty/tests/test_workflows.py:60-67`.
- Read-only checkout is enforced outside writer jobs:
  `/home/runner/work/szmyty/szmyty/tests/test_workflows.py:69-79`.
- External actions are SHA pinned:
  `/home/runner/work/szmyty/szmyty/tests/test_workflows.py:81-89`.
- Pages write permissions are scoped to the deploy job only:
  `/home/runner/work/szmyty/szmyty/.github/workflows/pages.yml:59-92`,
  `/home/runner/work/szmyty/szmyty/tests/test_workflows.py:123-131`.

---

## Findings by severity

### CRITICAL

None.

### HIGH

None.

### MEDIUM

#### M1 — `Update Profile` issue-event runs can fail on a non-fast-forward push race

- **Evidence:** latest issue-triggered run `31340834869` failed; failed `commit`
  job logs show `! [rejected] master -> master (fetch first)` after creating
  commit `58bb484`.
- **Impact:** issue edits/labels/reopens/closes can fail to publish refreshed
  artifacts when a push-triggered refresh advances `master` first.
- **Affected surface:** `.github/workflows/update-profile.yml` commit phase and
  workflow reliability.
- **Current mitigation:** public output was not corrupted because the latest
  push-triggered refresh on `master` succeeded (`31340834587`) and cache
  fallback behavior remains intact.
- **Resolution:** harden the commit phase against a remote-advanced branch
  (for example by fetching/rebasing before push, or exiting successfully when
  the remote already contains the intended semantic refresh).
- **Validation method:** reproduce with an issue event immediately after a
  push-triggered refresh and confirm the commit job exits successfully.

### LOW

None.

### NOTE

#### N1 — Live Pages HTTP verification remained environment-limited

- **Evidence:** `web_fetch` could not resolve `https://szmyty.github.io/szmyty/`
  or `.../ai-agent-showcase.html` from this audit environment.
- **Impact:** live HTTP 200 and final browser rendering still need owner
  confirmation even though the latest `Pages` workflow succeeded.
- **Resolution:** use the owner handoff checklist and verify the live Pages URL
  directly in a browser.

#### N2 — GitHub UI settings still require owner confirmation

- **Evidence:** branch protections, About text, topics, pinned repos, Pages UI,
  and Discussions UI are not fully exposed via repository files or the APIs used
  here.
- **Resolution:** complete
  `/home/runner/work/szmyty/szmyty/docs/FINAL-OWNER-HANDOFF-CHECKLIST.md`.

---

## Concise follow-up issue drafts

Only one bounded follow-up is warranted from this audit.

### Draft 1

- **Title:** `ci(update-profile): tolerate non-fast-forward pushes during issue-triggered refreshes`
- **Why:** latest issue-event refresh run `31340834869` failed in the `commit`
  job after the remote advanced first.
- **Scope:** keep the refresh workflow semantically identical while making the
  writer job safe when a push-triggered refresh or merge lands concurrently.
- **Acceptance:** rerunning the issue-event workflow on a concurrently updated
  branch either pushes successfully or exits `0` after detecting that the remote
  already contains the intended output.

---

## Future `egolint` migration note (do not start migration here)

Current authoritative lint gate remains Ruff:

- `/home/runner/work/szmyty/szmyty/docs/DEVELOPMENT.md:301-327`
- `/home/runner/work/szmyty/szmyty/.github/workflows/ci.yml:62-69`

Future migration prerequisites:

1. `egolint` must have a stable public release suitable for Poetry pinning
   (treat `>=1.0.0` as the minimum acceptable release class for planning).
2. The repository must be able to install that version reproducibly through the
   existing Poetry workflow.
3. A parity branch must prove that `egolint` can replace Ruff without reducing
   the current signal from `ruff check .` and `ruff format --check .`.

Future-only command plan:

```bash
# Future planning only — do not run in this issue
poetry add --group lint egolint@<stable-version>
poetry run egolint check .
```

Required parity checks before any adoption:

- compare `poetry run egolint check .` against current `poetry run ruff check .`
- confirm formatting coverage remains equivalent to
  `poetry run ruff format --check .`
- rerun `poetry run python -m pytest`
- rerun `poetry run python -m pytest tests/test_workflows.py -k "workflow or site"`
- rerun `poetry run yamllint .github/workflows .github/dependabot.yml Taskfile.yml`
- confirm `CI` stays green on a trial branch before touching `master`

Rollback plan if parity fails:

1. revert `.github/workflows/ci.yml` to Ruff commands,
2. remove the `egolint` dependency from `pyproject.toml` and `poetry.lock`,
3. rerun the full validation gate, and
4. keep the repository on Ruff until a later validated release.

---

## Owner handoff

Complete the manual GitHub UI review in
`/home/runner/work/szmyty/szmyty/docs/FINAL-OWNER-HANDOFF-CHECKLIST.md` before
declaring the public profile fully signed off for active job-search use.
