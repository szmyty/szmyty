# GitHub Metrics Diagnostics

## Summary

This document details the investigation and repair of GitHub stats, metrics, and language cards in the profile README.

## Issues Found

### 1. Update Stats Workflow (`update-stats.yml`) - **CRITICAL**

**Problem**: The workflow was using `anuraghazra/github-readme-stats@v2.0.9` as a GitHub Action, but this is not a GitHub Action - it's a web service that provides dynamic SVG cards via HTTP URLs.

**Error**: `Unable to resolve action 'anuraghazra/github-readme-stats@v2.0.9'`

**Impact**: Workflow failed on every run since the action version doesn't exist.

**Root Cause**: Incorrect usage of the github-readme-stats service as a GitHub Action. The service is designed to be used via Vercel API URLs in markdown, not as a workflow action.

### 2. Profile Summary Cards Workflow (`profile-summary-cards.yml`) - **MEDIUM**

**Problem**: The workflow relies on:
- A private repository `szmyty/github-profile-summary-cards`
- A secret `PERSONAL_ACCESS_KEY` that may not be properly configured
- Triggered on `create` event unnecessarily

**Error**: Workflow fails when trying to checkout the private repository or when secrets are missing.

**Impact**: Daily workflow failures in logs.

### 3. README Image Paths - **LOW**

**Problem**: The GitHub metrics SVG was using a relative path (`/github-metrics.svg`) which may not render correctly in all contexts (e.g., external embeds, mobile apps).

**Impact**: Potential image loading issues in certain viewing contexts.

### 4. Working Components

The following components were verified to be working correctly:

- ✅ **Metrics Workflow** (`metrics.yml`): Successfully generates `github-metrics.svg`
- ✅ **Update README Workflow** (`update-readme.yml`): Successfully updates activity section
- ✅ **GitHub Stats Cards** (Vercel API): Dynamic URLs work correctly
- ✅ **Top Languages Card** (Vercel API): Dynamic URLs work correctly
- ✅ **GitHub Streak Stats** (herokuapp): Dynamic URLs work correctly

## Fixes Applied

### 1. Removed `update-stats.yml` Workflow

**Action**: Deleted the workflow file entirely.

**Reason**: 
- The workflow was fundamentally broken (using a web service as an action)
- The functionality is already provided by dynamic Vercel API URLs in the README
- No local SVG generation was actually needed

### 2. Updated `profile-summary-cards.yml` Workflow

**Changes**:
- Removed `create` event trigger (unnecessary and could cause issues)
- Added secret availability check to gracefully skip when `PERSONAL_ACCESS_KEY` is not configured
- Added `continue-on-error: true` to prevent workflow failures from blocking
- Improved error messaging with warnings

### 3. Updated README Image Path

**Change**: Updated github-metrics.svg reference from relative path to absolute raw GitHub URL:
```markdown
<!-- Before -->
<img src="/github-metrics.svg" alt="GitHub Metrics" width="100%"/>

<!-- After -->
<img src="https://raw.githubusercontent.com/szmyty/szmyty/master/github-metrics.svg" alt="GitHub Metrics" width="100%"/>
```

**Reason**: Ensures consistent image loading across all platforms and contexts.

## Token/Secret Configuration

### Currently Required Secrets

| Secret Name | Used By | Scope Required | Status |
|-------------|---------|----------------|--------|
| `METRICS_TOKEN` | metrics.yml | `read:user`, `repo` (if private stats needed) | ✅ Configured |
| `STEAM_TOKEN` | metrics.yml | Steam Web API Key | ✅ Configured |
| `PERSONAL_ACCESS_KEY` | profile-summary-cards.yml | `repo` (for private repo access) | ⚠️ Optional |
| `GITHUB_TOKEN` | All workflows | Automatic | ✅ Auto-provided |

### Secret Recommendations

1. **METRICS_TOKEN**: Ensure this PAT has the following scopes:
   - `read:user` - Required for user profile data
   - `repo` - Required if showing private repository stats
   - `read:org` - Required if showing organization metrics

2. **PERSONAL_ACCESS_KEY**: Only needed if using the profile-summary-cards workflow with the private repository.

## Remaining Suggestions

### Optional Improvements

1. **Disable or remove profile-summary-cards.yml**: If not actively using the private github-profile-summary-cards repository, consider disabling the workflow to prevent unnecessary runs.

2. **Add workflow status badges**: The README already includes workflow status badges, ensuring users can see the current state of automation.

3. **Consider caching strategies**: The metrics workflow includes caching, which helps with rate limiting. Monitor if additional caching is needed.

### Monitoring

- Watch the Actions tab for any future failures
- The Metrics workflow should run successfully on schedule and push events
- The Update README workflow should run successfully every minute

## Verification Checklist

- [x] Metrics workflow runs successfully
- [x] GitHub-metrics.svg file exists and contains valid content
- [x] Update README workflow runs successfully
- [x] GitHub Stats Card loads via Vercel API
- [x] Top Languages Card loads via Vercel API
- [x] GitHub Streak Stats loads via herokuapp
- [x] Removed broken update-stats.yml workflow
- [x] Fixed profile-summary-cards.yml with graceful error handling
- [x] Updated README image paths to use absolute URLs

## Date of Diagnosis

2025-11-29
