# Workflows

All workflows are defined in `.github/workflows/`.

---

## `metrics.yml` — Metrics

**Trigger:** daily cron (`0 0 * * *`), `workflow_dispatch`, push to
`master`/`main`

**Purpose:** Generate self-hosted SVG visualizations of GitHub activity and
statistics using [lowlighter/metrics](https://github.com/lowlighter/metrics).

**Generates:**

| File                                        | Contents                                       |
| ------------------------------------------- | ---------------------------------------------- |
| `generated/metrics/overview.svg`            | Header, activity, community, achievements      |
| `generated/metrics/github-stats.svg`        | Repository stats and follow-up issue breakdown |
| `generated/metrics/top-languages.svg`       | Most-used programming languages                |
| `generated/metrics/contributions.svg`       | ISO calendar heatmap and coding habits         |
| `generated/metrics/github-metrics.svg`      | Consolidated legacy SVG (Steam + achievements) |

Requires the `METRICS_TOKEN` secret. Optionally uses `STEAM_TOKEN` for the
Steam plugin in the legacy SVG.

---

## `profile-summary-cards.yml` — Profile Summary Cards

**Trigger:** daily cron (`0 0 * * *`), `workflow_dispatch`

**Purpose:** Run the private `szmyty/github-profile-summary-cards` action to
produce a themed set of profile card SVGs.

**Generates:** `generated/profile-cards/*.svg`

Requires the `PERSONAL_ACCESS_KEY` secret. If the secret is absent, all steps
are skipped and the workflow exits cleanly without error.

---

## `update-readme.yml` — Update README

**Trigger:** daily cron (`0 0 * * *`), `workflow_dispatch`

**Purpose:** Inject the latest public GitHub activity into `README.md` using
[jamesgeorge007/github-activity-readme](https://github.com/jamesgeorge007/github-activity-readme).

**Updates:** `README.md` (activity section)

Uses the built-in `GITHUB_TOKEN` — no additional secrets required.

---

## `lint.yml` — Lint

**Trigger:** every push, every pull request

**Purpose:** Enforce consistent formatting and markdown style across all
repository files.

**Checks:**

- **Prettier** — validates code and prose formatting
- **markdownlint** — validates markdown structure and style

No artifacts are generated; the job fails if any file does not conform.
