# Migration Guide

This document defines the exact procedure for migrating
`szmyty/profile-next` (staging) into `szmyty/szmyty` (production).

---

## Prerequisites

Before beginning the cutover:

- [ ] All items in the Phase 6 migration readiness checklist pass.
- [ ] The static profile is visually complete and reviewed.
- [ ] All workflows run successfully via `workflow_dispatch`.
- [ ] `docs/ROADMAP.md` reflects the current implementation state.
- [ ] No open blockers exist in the GitHub issue tracker.

---

## Pre-Cutover Archive

Before making destructive changes to the production repository, archive the
existing state:

1. Tag the current state of `szmyty/szmyty`:
   ```sh
   git tag archive/pre-profile-next-migration
   git push origin archive/pre-profile-next-migration
   ```

2. Note the commit SHA for rollback reference.

3. Optionally export the existing README as a Markdown snapshot in
   `audits/pre-migration-snapshot.md` for historical reference.

---

## Cutover Procedure

### Step 1: Prepare the staging repository

Verify the staging repository is migration-ready:

```sh
# Confirm no reference to profile-next in production files
grep -r "profile-next" README.md AGENTS.md docs/ .github/workflows/ --include="*.md" --include="*.yml"

# Confirm no reference to .references/ in production files
grep -r "\.references" README.md AGENTS.md docs/ .github/workflows/ --include="*.md" --include="*.yml"

# Confirm all relative asset paths resolve from repo root
# (manual check — open README.md and verify all src= paths)
```

### Step 2: Copy contents to production

From a local clone of `szmyty/szmyty`:

```sh
# In szmyty/szmyty working directory
# Remove replaceable content
git rm -r --cached .

# Copy content from profile-next (excluding staging-specific files)
rsync -av --exclude='.git/' \
  --exclude='.references/' \
  --exclude='profile-next.code-workspace' \
  --exclude='*.code-workspace' \
  /path/to/profile-next/ ./

# Stage all changes
git add .
```

### Step 3: Review the diff

```sh
git diff --staged --stat
git diff --staged | head -200
```

Confirm:
- Only expected files are added/changed/removed.
- No `.references/` paths are included.
- No `.code-workspace` files are included.
- No nested `.git/` directories are included.

### Step 4: Commit and push

```sh
git commit -m "chore: migrate profile from profile-next to szmyty"
git push origin master
```

### Step 5: Configure secrets

In `szmyty/szmyty` → Settings → Secrets and variables → Actions, confirm:

| Secret | Required | Purpose |
|--------|----------|---------|
| `GITHUB_TOKEN` | Auto | Provided by GitHub; no configuration needed |
| `METRICS_TOKEN` | Yes | PAT with `read:user` and `repo` scopes for `lowlighter/metrics` |

Optional:
| Secret | Required | Purpose |
|--------|----------|---------|
| `STEAM_TOKEN` | No | Steam Web API key for gaming stats (metrics plugin) |

### Step 6: Enable workflows

In `szmyty/szmyty` → Actions, confirm all workflows are enabled:

- `github-stats.yml` — enable if scheduled triggers were disabled.
- `activity.yml` — enable if scheduled triggers were disabled.

### Step 7: Trigger manual runs

Run each workflow manually via `workflow_dispatch` to generate initial
artifacts:

```sh
gh workflow run github-stats.yml
gh workflow run activity.yml
```

### Step 8: Verify the public profile

1. Open `https://github.com/szmyty`.
2. Confirm the README renders correctly.
3. Confirm all images load (header, footer, metrics SVGs).
4. Confirm all links resolve.
5. Switch between light and dark mode; confirm readability in both.
6. Resize to narrow viewport; confirm layout remains usable.

### Step 9: Observe one scheduled automation cycle

Wait for the next scheduled run (or advance the schedule temporarily).
Confirm:
- Workflow runs succeed.
- Generated artifacts are committed.
- README displays updated artifacts.
- No recursive workflow loop occurs.

---

## Migration Exclusions

The following files must **not** be migrated:

```
.references/
profile-next.code-workspace
*.code-workspace
nested .git/ directories
local environment files (.env, .envrc)
caches and temporary files
generated debug output
local log files
```

These are already excluded from the `rsync` command in Step 2.

---

## Migration Validation Checklist

### Repository portability

- [ ] No production code references `.references/`.
- [ ] No production code references `profile-next`.
- [ ] No required link points to the staging repository.
- [ ] Relative asset paths work from the repository root.
- [ ] Workflows derive repository identity from GitHub context.
- [ ] Installation and generation commands work from a clean clone.

### README rendering

- [ ] README renders on GitHub without broken HTML.
- [ ] All images load.
- [ ] All SVGs load.
- [ ] All links resolve.
- [ ] Light mode is readable.
- [ ] Dark mode is readable.
- [ ] Narrow layouts remain usable.
- [ ] Alt text exists for meaningful images.
- [ ] Decorative animation does not impair readability.

### Automation

- [ ] Manual workflows succeed.
- [ ] Scheduled workflows are enabled.
- [ ] Permissions use least privilege.
- [ ] Secrets are configured.
- [ ] Generated artifacts are committed correctly.
- [ ] No recursive workflow loop occurs.
- [ ] API failure does not erase valid existing artifacts.

### Repository quality

- [ ] Documentation matches implementation.
- [ ] No secrets are committed.
- [ ] No unnecessary reference files remain.
- [ ] The repository remains reasonably small and understandable.

---

## Rollback

If the migration must be reverted:

```sh
# In szmyty/szmyty working directory
git revert HEAD
git push origin master
```

Or restore from the pre-migration archive tag:

```sh
git checkout archive/pre-profile-next-migration
git checkout -b restore/pre-migration
git push origin restore/pre-migration
# Open a PR from restore/pre-migration to master
```

---

## Post-Migration Archive

After confirming the public profile is working:

1. Verify `szmyty/profile-next` is no longer needed.
2. Archive `szmyty/profile-next` (Settings → Archive repository).
3. Do not delete `szmyty/profile-next` until at least one full scheduled
   automation cycle has succeeded in production.

---

## Post-Migration Audit

After the migration is stable (at minimum 48 hours of successful scheduled
runs), perform a comprehensive audit and write the results to:

```
.engineering/audits/profile-post-migration-audit.md
```

The audit must evaluate public profile impact, technical reliability,
accessibility, and identify future improvement opportunities. See
`PLAN.md` Section 17 for the full audit scope.
