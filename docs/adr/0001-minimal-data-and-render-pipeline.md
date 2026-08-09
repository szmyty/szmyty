# ADR 0001: Minimal Data-and-Render Pipeline

**Status:** Accepted  
**Date:** 2026-08-09  
**Stable queue key:** `szmyty-profile-rebuild-09`  
**Closes:** szmyty/szmyty#74

---

## Context

Two duplicated staged implementations exist under `.staging/scripts/` and
`.staging/engine/`.  Both grew organically and share overlapping utilities,
models, and generators without a clear boundary between data fetching,
normalization, and rendering.  Neither is in production.  The goal is to
replace them with one deterministic, minimal pipeline that owns only generated
profile regions and artifacts.

---

## Decision

Introduce a single importable package at `tools/profile_builder/` and a
corresponding content tree under `profile/` with the following shape:

```
profile/
  content/         # hand-authored YAML inputs (existing)
  schemas/         # JSON Schema documents for every public input
  templates/       # Jinja2 templates for each profile region
tools/
  profile_builder/
    __init__.py
    cli.py         # Click entry-point; one subcommand per required action
    models.py      # Pydantic models for all normalized public inputs
    regions.py     # README region detection, atomic writes, change detection
    rendering.py   # Pure renderers: accept normalized model → return str
tests/             # Unit tests; no network access, no external services
```

### Retained behaviors from staging

| Behavior | Source | Disposition |
|----------|--------|-------------|
| Schema-validated inputs | `engine/profile_engine/models/` | REWRITE — Pydantic v2 models in `models.py` |
| Atomic file writes | `engine/profile_engine/utils/utils.py` | REWRITE — `regions.py:atomic_write` |
| SHA-256 change detection | `engine/profile_engine/utils/change_detection.py` | REWRITE — `regions.py:content_hash` |
| SVG sanitization | `engine/profile_engine/utils/sanitize_svg.py` | DEFER — out of scope until SVG artifacts are needed |
| Structured diagnostics | `engine/profile_engine/utils/logging_utils.py` | DISCARD — stdlib `logging` is sufficient at this scale |

### Explicitly rejected behaviors

| Behavior | Reason |
|----------|--------|
| FastAPI / Uvicorn service | No long-running web API is required |
| Runtime plugin framework | No second concrete module needs the abstraction yet |
| Volatile timestamps in output | Create meaningless scheduled commits |
| Provider fetching inside renderers | Violates separation; renderers must be pure |
| Full regeneration of hand-authored README prose | README regions are protected; only owned regions are overwritten |

---

## Consequences

* One Python version (3.12) aligned with the root `pyproject.toml`.
* One dependency manager (Poetry) with one lock strategy (`poetry.lock`).
* One importable package boundary (`tools/profile_builder`).
* Renderers accept normalized local input → tests never require network access.
* Writes are atomic; a failed module cannot corrupt another module's region.
* The staged implementations (`.staging/scripts/`, `.staging/engine/`) remain
  in place as historical evidence and are marked `ARCHIVE` in `docs/MIGRATION.md`.

---

## Required CLI commands

| Long-form command | Behavior |
|-------------------|----------|
| `profile-builder validate` | Validate public content and normalized module data |
| `profile-builder render MODULE` | Render one named module |
| `profile-builder render --all` | Render all enabled modules |
| `profile-builder check` | Report whether rendering would change tracked output |
| `profile-builder status` | Explain module status and stale/fallback behavior |
