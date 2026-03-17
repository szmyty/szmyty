# Repository Architecture

## Purpose

This repository is the GitHub profile for
[@szmyty](https://github.com/szmyty). It serves as a **profile automation
system** — the `README.md` and all supporting visuals are kept current
automatically, with no manual intervention required after initial setup.

---

## Major Components

### GitHub Actions

All automation runs inside GitHub Actions workflows stored in
`.github/workflows/`. Four workflows handle every aspect of content
generation and quality control.

### Metrics Generation

[lowlighter/metrics](https://github.com/lowlighter/metrics) queries the
GitHub API and renders activity, statistics, language breakdowns, habits, and
achievements as self-hosted SVG files. This eliminates dependency on external
badge services and prevents content gaps caused by third-party downtime.

Generated files are stored in `metrics/` — individual focused SVGs (overview,
stats, languages, contributions).

### Profile Summary Cards

A private action (`szmyty/github-profile-summary-cards`) generates a set of
themed summary cards and writes them to the `profile-summary-card-output/`
directory. The workflow degrades gracefully: if the required secret is absent
all card-generation steps are skipped without failing the run.

### README Updates

Recent public activity is injected into `README.md` by
[jamesgeorge007/github-activity-readme](https://github.com/jamesgeorge007/github-activity-readme).
The action appends or refreshes an activity section on every scheduled run.

---

## Data Flow

```text
GitHub API
    │
    ├─► lowlighter/metrics ──► metrics/*.svg
    │                    └──► github-metrics.svg
    │
    ├─► github-profile-summary-cards ──► profile-summary-card-output/*.svg
    │
    └─► github-activity-readme ──► README.md (activity section)
```

Each workflow commits its generated artifacts directly to the repository.
The `README.md` embeds the SVG files by path, so the profile page always
reflects the latest committed outputs.
