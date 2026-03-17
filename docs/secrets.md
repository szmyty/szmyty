# 🔐 GitHub Actions Secrets

This document lists all secrets required or optionally used by the GitHub
Actions workflows in this repository. Configure these secrets under
**Settings → Secrets and variables → Actions** in the repository.

---

## Secrets Reference

### `GITHUB_TOKEN`

- **Required:** Automatically provided by GitHub Actions
- **Used in:** `update-readme.yml`
- **Purpose:** Built-in GitHub token that authenticates API requests made by
  the workflow. Used by `jamesgeorge007/github-activity-readme` to read
  recent public activity and write the updated `README.md` back to the
  repository.
- **Example:** _(no configuration needed — GitHub injects this automatically)_

---

### `METRICS_TOKEN`

- **Required:** Yes
- **Used in:** `metrics.yml`
- **Purpose:** GitHub personal access token used by `lowlighter/metrics` to
  query the GitHub API and generate SVG visualizations of repository
  statistics, contributions, top languages, and activity. Without this token
  the entire metrics workflow will fail.
- **Example:** A classic PAT with `read:user` and `repo` scopes, or a
  fine-grained token with read access to the target account's metadata and
  repositories.

---

### `STEAM_TOKEN`

- **Required:** Optional
- **Used in:** `metrics.yml`
- **Purpose:** Steam Web API key used by the `lowlighter/metrics` Steam plugin
  to retrieve gaming statistics and achievements. If this token is absent, the
  Steam section of the legacy metrics SVG is simply omitted.
- **Example:** Obtain a key from <https://steamcommunity.com/dev/apikey> using
  a Steam account.

---

### `PERSONAL_ACCESS_KEY`

- **Required:** Optional (workflow steps are skipped when absent)
- **Used in:** `profile-summary-cards.yml`
- **Purpose:** GitHub personal access token used to check out the main profile
  repository and the private `github-profile-summary-cards` action, and to
  authenticate the card-generation action itself. The workflow checks for this
  secret at runtime and skips all steps if it is not set, so the workflow
  degrades gracefully without it.
- **Example:** A classic PAT with `repo` scope (needed to access private
  action repositories and push generated card images).

---

## Summary Table

| Secret                | Required | Workflow                    |
| --------------------- | -------- | --------------------------- |
| `GITHUB_TOKEN`        | Auto     | `update-readme.yml`         |
| `METRICS_TOKEN`       | Yes      | `metrics.yml`               |
| `STEAM_TOKEN`         | Optional | `metrics.yml`               |
| `PERSONAL_ACCESS_KEY` | Optional | `profile-summary-cards.yml` |

---

## Notes

- Never commit actual secret values to the repository.
- Rotate tokens regularly and apply the principle of least privilege when
  creating PATs.
- If a workflow behaves unexpectedly, verify that all required secrets are
  present and have the correct scopes.
