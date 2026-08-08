# Publishing Automation

This document covers the automated publishing synchronization workflows currently operating in the Ego Hygiene repository — how they work, why they are designed the way they are, and what operators should know.

---

## Overview

Ego Hygiene maintains archive mirrors of two external publishing channels:

| Channel | Workflow | Schedule |
|---------|----------|----------|
| Medium | `medium-rss-sync.yml` | Daily at 08:30 UTC |
| Pinterest | `pinterest-rss-sync.yml` | Daily at 08:00 UTC |

Both workflows ingest RSS feeds from the external platform and commit the synchronized archive to the repository.

---

## Source vs. Mirror Ownership

**Canonical content** lives in `publishing/sources/`:

```text
publishing/sources/
    articles/       — long-form essays authored in Markdown
    synapses/       — living stream of insights and knowledge notes
    magazine/       — AI-powered magazine editions
```

**Synchronized mirrors** live in `publishing/channels/`:

```text
publishing/channels/
    medium/         — Medium article archive (synchronized, not authored)
    pinterest/      — Pinterest board archive (synchronized, not authored)
```

Content in `publishing/channels/` is **synchronized output**, not the source of truth.

Do not manually edit files in `publishing/channels/`. They are overwritten on the next sync run.

The source of truth for published content is always `publishing/sources/` or the external platform itself, depending on which direction the content was authored.

---

## Medium RSS Sync

### Purpose

Ingests the Medium RSS feed for the Ego Hygiene publication and archives article metadata and content to `publishing/channels/medium/`.

### Workflow file

`.github/workflows/medium-rss-sync.yml`

### Triggers

| Trigger | Condition |
|---------|-----------|
| Schedule | Daily at 08:30 UTC |
| `workflow_dispatch` | Manual trigger via GitHub Actions UI |
| `push` to `main` | Only when workflow, tool, or config files change |

The `push` trigger is path-scoped. A commit touching unrelated files does not trigger a sync.

### Configuration

```text
publishing/channels/medium/config.yaml
```

Defines:

- Feed ID (`ego-hygiene-medium`)
- RSS URL (`https://articles.egohygiene.io/feed`)
- Output directory (`publishing/channels/medium/`)

### Output

Synchronized content is written to:

```text
publishing/channels/medium/
    articles/           — archived article files
    manifest.json       — feed manifest with stable article IDs
    config.yaml         — feed configuration (checked in)
```

### Commit behavior

The workflow commits directly to `main` using `github-actions[bot]` when new content is detected.

Commit message format:

```
docs(medium): 📝 sync Medium article archive [skip ci]
```

`[skip ci]` prevents the build workflow from triggering on automated sync commits.

If no new content is found, no commit is made.

### GitHub token permissions

The workflow requires `contents: write` permission to commit to `main`. This is granted via the workflow's `permissions` block and uses the `GITHUB_TOKEN` provided by GitHub Actions.

No additional secrets are required for read-only RSS ingestion.

---

## Pinterest RSS Sync

### Purpose

Ingests the Pinterest RSS feed for the Ego Hygiene board and archives pin metadata and images to `publishing/channels/pinterest/`.

### Workflow file

`.github/workflows/pinterest-rss-sync.yml`

### Triggers

| Trigger | Condition |
|---------|-----------|
| Schedule | Daily at 08:00 UTC |
| `workflow_dispatch` | Manual trigger via GitHub Actions UI |
| `push` to `main` | Only when workflow, tool, or config files change |

### Configuration

```text
publishing/channels/pinterest/config.yaml
```

Defines:

- Feed ID (`ego-hygiene`)
- RSS URL (`https://www.pinterest.com/egohygiene/ego-hygiene.rss`)
- Output directory (`publishing/channels/pinterest/boards/ego-hygiene`)

Environment variable overrides (optional):

| Variable | Description |
|----------|-------------|
| `PINTEREST_RSS_URL` | Override the feed URL |
| `PINTEREST_OUTPUT_DIRECTORY` | Override the output path |
| `PINTEREST_DOWNLOAD_IMAGES` | Set to `"false"` to skip image downloads |

### Output

Synchronized content is written to:

```text
publishing/channels/pinterest/
    boards/
        ego-hygiene/    — archived pin data and images
    config.yaml         — feed configuration (checked in)
```

### Commit behavior

The workflow commits directly to `main` using `github-actions[bot]` when new content is detected.

Commit message format:

```
assets(pinterest): 🍱 sync Pinterest feed [skip ci]
```

`[skip ci]` prevents the build workflow from triggering on automated sync commits.

If no new content is found, no commit is made.

### GitHub token permissions

The workflow requires `contents: write` permission to commit to `main`. No external secrets are required for RSS ingestion.

---

## Direct-to-Main Pattern

Both workflows commit directly to `main` rather than opening pull requests. This is intentional.

**Rationale:**

The synchronized content is structured archive data. It does not affect application code, tests, or CI behavior. Requiring pull request review for every automated archive update would create unnecessary noise in the review history and delay archive availability.

This decision is recorded in [`DECISIONS.md`](../../../.engineering/architecture/DECISIONS.md) as ADR-013.

**Safeguards that make this safe:**

- `[skip ci]` prevents recursive CI triggers.
- Concurrency groups (`concurrency: group: medium-rss-sync`) prevent duplicate runs.
- Each sync run checks for changes before committing.
- Stable file naming and a manifest prevent duplicate archiving.
- The `github-actions[bot]` identity is auditable in the git log.

**If branch protection is enabled:**

Ensure that `github-actions[bot]` is permitted to push to `main`. If the rule requires pull requests for all commits, the workflows must be updated to use pull-request-based synchronization instead.

---

## Duplicate Prevention

Both tools use a manifest file and stable content IDs to avoid re-archiving content that has already been synchronized.

The manifest (`manifest.json`) tracks previously ingested content by ID. On each run, only new content since the last sync is archived.

---

## Artifact and Manifest Behavior

| Artifact | Location | Behavior |
|----------|----------|----------|
| Medium article archive | `publishing/channels/medium/articles/` | Appended on each sync; never deleted |
| Medium manifest | `publishing/channels/medium/manifest.json` | Updated on each sync |
| Pinterest board archive | `publishing/channels/pinterest/boards/` | Appended on each sync; never deleted |

Archive files are additive. Removing a post from Medium or Pinterest does not remove it from the archive.

---

## Failure Handling

If a sync workflow fails:

- GitHub Actions will mark the run as failed.
- No partial commit is made (the commit step runs only if there are staged changes).
- The concurrency group prevents a parallel run from overlapping.
- The next scheduled run will attempt the sync again.

Check workflow run logs in the GitHub Actions UI for failure details.

---

## Privacy and Secret Handling

The Medium and Pinterest RSS feeds are public. No authentication tokens are required for read-only ingestion.

No user data, credentials, or private content is processed by these workflows.

If the feed configuration is updated to use an authenticated feed, the credentials must be stored in GitHub Actions Secrets and referenced via `${{ secrets.YOUR_SECRET }}` — never hardcoded in workflow or config files.

---

## Operator Workflow

**Normal operation:**

No action required. Syncs run automatically on schedule.

**Manual trigger:**

1. Navigate to the GitHub Actions tab.
2. Select `Medium RSS Sync` or `Pinterest RSS Sync`.
3. Click `Run workflow`.

**Update configuration:**

1. Edit the relevant `config.yaml` in `publishing/channels/<channel>/`.
2. Commit to `main`. The `push` trigger will run the sync with the new configuration.

**Update sync tooling:**

1. Edit files in `publishing/tools/medium-rss/` or `publishing/tools/pinterest-rss/`.
2. Commit to `main`. The `push` trigger will run the sync with the updated tool.

**Validate the tools locally:**

```bash
# Medium RSS tool
cd publishing/tools/medium-rss
poetry install --no-interaction
poetry run pytest tests/ -v

# Pinterest RSS tool
cd publishing/tools/pinterest-rss
poetry install --no-interaction
poetry run pytest tests/ -v
```

---

## Recovery from a Bad Synchronization

If a sync run produces incorrect or unwanted archive content:

1. Identify the offending commit in the git log (look for commits from `github-actions[bot]`).
2. Revert the commit:
   ```bash
   git revert <commit-sha>
   git push
   ```
3. If the root cause is in the sync tool or configuration, fix that first and then re-run the workflow manually.

Because the archive is additive, a bad sync can also be corrected by manually deleting the incorrect files and committing the deletion directly to `main`.

---

## Related Documentation

- `publishing/README.md` — publishing workspace overview and content lifecycle
- `publishing/docs/publishing-lifecycle.md` — detailed publishing pipeline
- `.engineering/architecture/DECISIONS.md` (ADR-013) — rationale for direct-to-main commits
- `.github/workflows/medium-rss-sync.yml` — Medium sync workflow
- `.github/workflows/pinterest-rss-sync.yml` — Pinterest sync workflow
