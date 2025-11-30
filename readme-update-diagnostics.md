# README Auto-Update Diagnostics

## Investigation Summary

This document provides diagnostics and fixes for the GitHub Profile Summary Cards workflow and README auto-update process.

## Issues Identified

### 1. Profile Summary Cards Workflow - **CRITICAL FIX APPLIED**

**Problem**: The workflow was checking out the private action repository (`szmyty/github-profile-summary-cards`) to the repository root (`path: ./`), which **replaced** the profile repository content entirely.

**Root Cause Analysis**:
- Step 1: Workflow checked out `szmyty/github-profile-summary-cards` to `./`
- Step 2: This completely replaced the `szmyty/szmyty` profile repository
- Step 3: Action generated cards but tried to commit to wrong git remote
- Step 4: Commit failed with exit code 1

**Error from logs** (verbatim quote with formatting as shown in GitHub Actions):
```
##[error]Error: git add,./profile-summary-card-output/ 
  Invalid status code: 1
```
*Note: The comma in the error message above is from the original action's error output, not a typo.*

### 2. README Missing Profile Summary Card Embeds

**Problem**: The README.md did not include image references for the profile summary cards.

**Impact**: Even if cards were generated, they would not be visible on the profile.

## Fixes Applied

### Fix 1: Corrected Workflow Checkout Strategy

**Changes to `profile-summary-cards.yml`**:

1. ✅ Added checkout of profile repository FIRST with `fetch-depth: 0`
2. ✅ Changed action checkout to nested path: `.github/actions/profile-summary-cards`
3. ✅ Added git configuration step for committing
4. ✅ Added verification step to confirm output generation
5. ✅ Added explicit commit and push step with proper error handling
6. ✅ Cleanup of nested action directory before commit

**Before**:
```yaml
# BROKEN: Checked out action repo to root, replacing profile repo
- uses: actions/checkout@v4
  with:
    repository: szmyty/github-profile-summary-cards
    path: ./
```

**After**:
```yaml
# FIXED: Checkout profile repo first
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
    token: ${{ secrets.PERSONAL_ACCESS_KEY }}

# Then checkout action to nested path
- uses: actions/checkout@v4
  with:
    repository: szmyty/github-profile-summary-cards
    path: .github/actions/profile-summary-cards
```

### Fix 2: Added Profile Summary Card Embeds to README

Added a new "Profile Summary Cards" section with images pointing to:
- `profile-summary-card-output/default/0-profile-details.svg`
- `profile-summary-card-output/default/1-repos-per-language.svg`
- `profile-summary-card-output/default/2-most-commit-language.svg`
- `profile-summary-card-output/default/3-stats.svg`
- `profile-summary-card-output/default/4-productive-time.svg`

## Expected Output Structure

After a successful workflow run, the following files should exist:

```
profile-summary-card-output/
├── default/
│   ├── 0-profile-details.svg
│   ├── 1-repos-per-language.svg
│   ├── 2-most-commit-language.svg
│   ├── 3-stats.svg
│   └── 4-productive-time.svg
└── (additional theme folders if configured)
```

## Verification Checklist

After the next workflow run, verify:

- [ ] Workflow completes without errors
- [ ] `profile-summary-card-output/` directory is created
- [ ] All 5 SVG files are generated in the `default/` subfolder
- [ ] Commit is pushed to the repository
- [ ] README displays the profile summary cards correctly

## Workflow Runs Reference

| Run # | Date | Status | Notes |
|-------|------|--------|-------|
| 320 | 2025-11-30 | ❌ Failed | Action ran but commit failed due to wrong checkout |
| 319 | 2025-11-29 | ❌ Failed | Previous workflow version |
| 318 | 2025-11-28 | ❌ Failed | Previous workflow version |

## Token/Secret Configuration

| Secret | Required For | Status |
|--------|-------------|--------|
| `PERSONAL_ACCESS_KEY` | Profile cards workflow | ✅ Configured |
| `GITHUB_TOKEN` | Auto-provided by Actions | ✅ Auto-provided |

## Recommendations

1. **Monitor Next Run**: After merging the fix, monitor the next scheduled or manual workflow run
2. **Check Action Logs**: Verify the "Generate profile summary cards" step succeeds
3. **Verify Commit**: Confirm a commit is pushed with the generated cards
4. **Test Manual Trigger**: Use `workflow_dispatch` to test immediately after merge

## Related Files

- `.github/workflows/profile-summary-cards.yml` - Fixed workflow
- `README.md` - Updated with card embeds
- `metrics-diagnostics.md` - Previous diagnostics for other workflows

## Date of Diagnosis

2025-11-30
