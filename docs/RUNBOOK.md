# Operations Runbook

**Repository:** `szmyty/szmyty`
**Status:** Active

This runbook covers response procedures for every known failure scenario in the
profile build and publish pipeline.

---

## 1. Scheduled Update Failure

**Symptom:** The `update-profile.yml` workflow run ends in failure or
partial-failure.

**Response:**

1. Open the failed run in Actions and check the `summarize` step output.
   Each module reports its outcome (`success`, `failure`, `skipped`) and its
   `data_source` value from the artifact cache.
2. If a single module failed but the others succeeded, the README is still
   updated with the passing modules.  The `report-partial-failure` job marks
   the overall run as failed to make the problem visible.
3. Identify which module failed (`github-metrics`, `recent-activity`, or
   `music-highlight`).
4. Check whether the failure is a transient API error or a structural problem.
5. For transient errors: re-run the workflow from the Actions UI.
6. For structural errors: see the module-specific sections below.
7. If the update has not run in more than 48 hours, open an issue and tag
   `@szmyty` for manual review.

---

## 2. Module Provider Failure

### 2a. GitHub API failure (github-metrics, recent-activity)

**Symptom:** Module step exits non-zero; log shows a non-2xx response or
connection error from the GitHub API.

**Response:**

1. Check [githubstatus.com](https://www.githubstatus.com) for an active
   incident.
2. If GitHub is degraded, wait and re-run the workflow after the incident
   resolves.
3. If the failure persists after GitHub recovers, inspect the module script
   for changes to the API endpoint or response schema.
4. The cached artifact from the previous successful run is preserved in the
   repository.  The README will retain the last-known-good content until the
   provider recovers.

### 2b. Music highlight module failure

**Symptom:** The `music-highlight` step fails.

**Response:**

1. Inspect `profile/content/music-highlight.yml` for malformed YAML or a
   missing required field.
2. Validate the file locally:
   ```sh
   poetry run python -m tools.modules.music_highlight \
     --input profile/content/music-highlight.yml \
     --output /tmp/music.yml
   ```
3. If the file is valid and the failure is script-related, check the module
   script at `tools/modules/music_highlight.py` for a broken import or logic
   error.

---

## 3. Stale Output

**Symptom:** The rendered README shows data that is significantly older than
expected (e.g., no activity updates for several days).

**Response:**

1. Confirm the scheduled workflow is not disabled.  Open Actions → Update
   Profile → check that the workflow is enabled.
2. Verify the workflow schedule is active (GitHub disables scheduled workflows
   on repositories with no activity for 60 days).
3. Re-enable or trigger the workflow manually from the Actions UI.
4. If artifacts are stale due to repeated module failures, manually update the
   fixture fallback:
   ```sh
   GITHUB_TOKEN=<your-pat> \
     poetry run python -m tools.modules.github_metrics \
       --output profile/artifacts/github-metrics/cache.json
   git add profile/artifacts/github-metrics/cache.json
   git commit -m "chore(profile): manually refresh stale github-metrics cache"
   git push
   ```

---

## 4. Broken Link

**Symptom:** A link in `README.md`, `site/index.html`, or a documentation file
returns a 404 or connection error.

**Response:**

1. Identify the broken URL and where it is referenced.
2. For profile README links: check `profile/content/evidence.yml` for the
   corresponding record.  If the URL is no longer valid, mark the record
   `status: needs-user-verification` and open an issue.
3. For site links: update `site/index.html` or the relevant CSS/JS reference.
4. For documentation links: update the markdown file directly.
5. Commit the fix and verify in CI.

---

## 5. Asset Replacement

**Symptom:** An SVG or image asset in `assets/profile/` is missing, corrupted,
or must be replaced.

**Response:**

1. Prepare the replacement asset offline and validate it meets the design
   constraints in `docs/DESIGN.md` (contrast ratios, font fallbacks, dimensions).
2. Replace the file at the same path:
   ```sh
   cp /path/to/new-banner-dark.svg assets/profile/banner-dark.svg
   ```
3. Run the asset validator:
   ```sh
   poetry run python profile/validate_assets.py assets/profile
   ```
4. Review the README to confirm the replaced asset renders as expected in the
   GitHub Markdown preview.
5. Commit the replacement:
   ```sh
   git add assets/profile/banner-dark.svg
   git commit -m "chore(assets): replace banner-dark.svg"
   git push
   ```

---

## 6. GitHub Pages Rollback

**Symptom:** The deployed Pages site (`szmyty.github.io`) is broken or showing
wrong content after a `pages.yml` deployment.

**Response:**

1. Identify the last known-good commit for `site/`:
   ```sh
   git log --oneline -- site/
   ```
2. Check out the known-good state of the site files:
   ```sh
   git checkout <good-commit-sha> -- site/
   ```
3. Run the local site validator:
   ```sh
   poetry run python -m pytest tests/test_workflows.py -k "workflow or site"
   ```
4. Commit and push the reverted site:
   ```sh
   git add site/
   git commit -m "revert(site): roll back to <good-commit-sha>"
   git push
   ```
5. The `pages.yml` workflow will re-deploy automatically on push to `master`.
6. Verify the deployment completed successfully in Actions and confirm the live
   site is restored.

---

## 7. Suspected Secret Exposure

**Symptom:** A secret value (token, credential) may have been committed,
logged, or leaked.

**Immediate response (within minutes):**

1. **Revoke immediately:** Go to the provider (GitHub, etc.) and invalidate
   the affected token before doing anything else.
2. **Remove from tracked tree:**
   ```sh
   git rm --cached <file-with-secret>
   git commit -m "security: remove accidentally committed secret"
   git push
   ```
3. **Remove from Actions logs:** If the secret appeared in a workflow log,
   open Settings → Actions → Logs and delete the affected run logs.
4. **Notify:** Tag `@szmyty` on the incident and, if the secret was used to
   access third-party services, follow those services' breach-notification
   procedures.
5. **Assess exposure:** Scan the current tracked tree and recent history for
   other occurrences of the same token pattern.
6. **Re-issue a new secret** only after confirming the old one is fully
   revoked and removed.
7. **Document** the incident in `docs/audits/` using a sanitized summary
   (type, path range, date — never the value).
8. **Schedule history rewrite** separately, coordinated with `@szmyty`, as
   rewriting shared history affects all forks and clones.

> Do not rewrite shared branch history automatically.  Rewriting history
> after a secret exposure requires explicit coordination with the repository
> owner.

---

## 8. CI Validation Failure

**Symptom:** The `ci.yml` workflow fails on a pull request or push.

**Response:**

1. Open the failed job in Actions.
2. Run the failing step locally to reproduce:
   - Profile validation: `poetry run python -m tools.profile_builder.cli validate`
   - Asset validation: `poetry run python profile/validate_assets.py assets/profile`
   - Python lint: `poetry run ruff check tests`
   - YAML lint: `poetry run yamllint .github/workflows .github/dependabot.yml Taskfile.yml`
   - Tests: `poetry run python -m pytest`
3. Fix the underlying issue, commit, and push to trigger a new CI run.
4. If the failure is a flaky test, investigate root cause — do not simply
   re-run without understanding why it failed.

---

## 9. Evidence Verification Request

**Symptom:** A claim in `README.md` or `profile/content/evidence.yml` is
marked `status: needs-user-verification` and is blocking a profile update.

**Response:**

1. Open or locate the corresponding GitHub issue requesting verification from
   `@szmyty`.
2. Do not change the record to `verified` without an explicit response or a
   publicly inspectable artifact.
3. If `@szmyty` provides confirmation:
   - Update the record's `status` to `verified`.
   - Add or update the `url` or `repo_path` field with the artifact reference.
   - Update `last_reviewed` to today's date.
   - Commit and push.
4. If verification is refused or not forthcoming, mark the record `excluded`
   and remove the corresponding claim from `README.md`.

---

## 10. GitHub Surface Owner Checklist

The following settings require direct access to the GitHub UI and cannot be
verified by repository files or CI.  `@szmyty` must review these manually
before each release.

> Use the consolidated release handoff at
> [`docs/FINAL-OWNER-HANDOFF-CHECKLIST.md`](FINAL-OWNER-HANDOFF-CHECKLIST.md)
> together with
> [`docs/audits/FINAL-PROFILE-READINESS-REPORT.md`](audits/FINAL-PROFILE-READINESS-REPORT.md)
> when performing the final owner sign-off.

> These items are outside the automated validation scope.  Repository files
> and CI workflows cannot assert their correctness.

### Branch rules and required checks

- [ ] `master` has a branch protection rule or ruleset enabled.
- [ ] Required status checks include the `validate`, `assets`, `lint-python`,
      `lint-yaml`, and `tests` jobs from `ci.yml`.
- [ ] Force-push to `master` is disabled.
- [ ] Deletion of `master` is disabled.

### Repository About text, homepage, and topics

- [ ] About description is current and accurate.
- [ ] Homepage URL points to `https://szmyty.github.io` (or is intentionally blank).
- [ ] Topics reflect the current project focus (e.g., `profile`, `github-profile`).
- [ ] Social preview image is set and renders correctly in link previews.

### Profile pinned repositories

- [ ] Pinned repositories reflect current flagship projects.
- [ ] No stale, archived, or placeholder repositories are pinned.

### Pages environment and deployment URL

- [ ] GitHub Pages source is set to the `gh-pages` branch or the Actions
      deployment workflow (`pages.yml`).
- [ ] Deployment URL is `https://szmyty.github.io` and returns HTTP 200.
- [ ] The Pages environment (`github-pages`) shows a successful last deployment.

### Discussions categories and issue-routing links

- [ ] Discussions are enabled on the repository.
- [ ] The following categories exist: `Announcements`, `General`, `Ideas`,
      `Polls`, `Q&A`, `Show and tell`.
- [ ] Contact links in `.github/ISSUE_TEMPLATE/config.yml` each resolve to a
      real Discussions category or page:
      - `https://github.com/szmyty/szmyty/discussions` — General Discussions
      - `https://github.com/szmyty/szmyty/discussions/categories/ideas` — Research & Exploration
      - `https://github.com/szmyty/szmyty/discussions/categories/q-a` — Documentation Feedback
      - `https://github.com/szmyty/szmyty/security/advisories/new` — Security Reports

---

## oura-trends module

### Default state

The module is `enabled: false` and `publication: blocked-pending-owner-approval`
in `profile/content/modules-registry.yml`.  No real-data artifact is written
until the owner completes the approval checklist below.

### Owner approval checklist (required before enabling)

- [ ] Review the threat model in `tools/modules/oura_trends.py` (sleep/wake
      schedule, travel, illness, availability inference risks).
- [ ] Confirm the metric allowlist in `OURA_PUBLIC_AGGREGATE_ALLOWLIST` (models.py)
      covers only coarse approved metrics.
- [ ] Create a Personal Access Token at
      <https://cloud.ouraring.com/personal-access-tokens> with only the
      minimum scopes needed: `daily_sleep`, `daily_readiness`, `daily_activity`.
- [ ] Add `OURA_ACCESS_TOKEN` as a repository secret under GitHub → Settings →
      Secrets and variables → Actions.
- [ ] Set `enabled: true` **and** `publication: allowed` in
      `profile/content/modules-registry.yml`.
- [ ] Run `poetry run python -m pytest tests/test_oura_trends.py -v` locally
      to confirm the full pipeline passes.
- [ ] Merge the registry change in a dedicated PR reviewed by `@szmyty`.

### Token rotation

1. Create a new token at <https://cloud.ouraring.com/personal-access-tokens>.
2. Update the `OURA_ACCESS_TOKEN` repository secret.
3. Verify the next scheduled pipeline run succeeds.
4. Revoke the old token.

### Revocation

1. Revoke the token at <https://cloud.ouraring.com/personal-access-tokens>.
2. Remove or invalidate the `OURA_ACCESS_TOKEN` repository secret immediately.
3. The module automatically falls back to the cached artifact or fixture —
   other profile modules are unaffected.

### Disable procedure

1. Set `enabled: false` in `profile/content/modules-registry.yml`.
2. Commit and merge.  The module stops fetching and the README region is
   cleared on the next pipeline run.

### Delete public artifact procedure

1. Delete `profile/artifacts/oura-trends/` from the tracked tree:
   ```sh
   git rm -r profile/artifacts/oura-trends/
   ```
2. Clear the README region between
   `<!-- START:oura-trends -->` and `<!-- END:oura-trends -->`.
3. Set `enabled: false` and `publication: blocked-pending-owner-approval` in
   the registry.
4. Commit and merge.

**Note:** History containing previously committed aggregate artifacts should be
reviewed separately.  Do not rewrite shared branch history automatically;
follow the incident response procedure in `docs/PRIVACY.md`.
