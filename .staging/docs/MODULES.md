# Modules

This document defines what constitutes a module, the required and optional
module files, the module lifecycle, failure isolation conventions, and README
integration standards.

---

## What Is a Module?

A **module** is a self-contained unit that manages one or more profile
sections.

A module may be:

- **Static** — hand-authored content that does not need automation.
- **Dynamic** — generates artifacts through scheduled GitHub Actions
  workflows.

A section should become a dynamic module only when:

1. The content changes on a schedule that makes manual updates impractical.
2. The automation reduces maintenance rather than adding fragility.
3. A reliable data source exists.

---

## Module Locations

| Asset type | Path |
|-----------|------|
| Specification | `.github/specs/<module>.spec.md` |
| Scripts | `.github/scripts/<module>/` |
| Provider | `.github/scripts/<module>/provider.py` |
| Normalizer | `.github/scripts/<module>/normalizer.py` |
| Renderer | `.github/scripts/<module>/renderer.py` |
| Templates | `.github/scripts/<module>/templates/` |
| Generated artifacts | `.github/artifacts/<module>/` |
| Workflow | `.github/workflows/<module>.yml` |
| Tests | `tests/test_<module>.py` |

---

## Required Module Files

Every dynamic module must have:

- A specification (`.github/specs/<module>.spec.md`).
- At least one script under `.github/scripts/<module>/`.
- Generated artifacts under `.github/artifacts/<module>/`.
- A workflow under `.github/workflows/<module>.yml`.

Optional but encouraged:

- Tests under `tests/`.
- A templates directory under `.github/scripts/<module>/templates/`.

---

## Module Lifecycle

```
Discovery
    ↓
Design (define purpose, data source, output format)
    ↓
Specification (.github/specs/<module>.spec.md)
    ↓
Static prototype (hand-authored placeholder in README)
    ↓
Provider implementation (.github/scripts/<module>/provider.py)
    ↓
Normalizer implementation (.github/scripts/<module>/normalizer.py)
    ↓
Renderer implementation (.github/scripts/<module>/renderer.py)
    ↓
Artifact generation (.github/artifacts/<module>/)
    ↓
Tests (tests/test_<module>.py)
    ↓
Workflow (.github/workflows/<module>.yml)
    ↓
README integration
    ↓
Validation (rendered output, both themes, narrow layout)
    ↓
Maintenance
```

---

## Module Script Responsibilities

### Provider

Fetches or reads raw data from an external source.

- Must handle API errors gracefully.
- Must not crash on empty or partial responses.
- Must return a structured Python object or `None` on failure.
- Must not cache state in global variables.

### Normalizer

Transforms provider output into a canonical internal representation.

- Must accept `None` from the provider (return a safe default).
- Must produce a consistent schema regardless of provider variations.
- Must be unit-testable without a live API.

### Renderer

Converts normalized data into the output artifact format (SVG, JSON, Markdown).

- Must produce well-formed output.
- Must handle empty data gracefully (render a minimal valid artifact).
- Must not hardcode repository names or owner usernames.
- SVG renderers must produce accessible output (include `<title>`).

---

## Failure Isolation

Each module must fail independently.

**Requirements:**

- A module workflow failing must not affect other modules or the main README.
- The workflow must not delete an existing artifact if generation fails.
- If the API is unavailable, the last committed artifact stays in place.
- Workflow jobs must not set `fail-fast: true` across unrelated modules.

**Implementation pattern:**

```yaml
steps:
  - name: Generate artifact
    id: generate
    continue-on-error: true
    run: python .github/scripts/<module>/renderer.py

  - name: Commit artifact
    if: steps.generate.outcome == 'success'
    run: |
      git add .github/artifacts/<module>/
      git diff --staged --quiet || git commit -m "chore(artifacts): update <module>"
```

---

## README Integration

Modules embed their artifacts using relative paths:

```markdown
<img src=".github/artifacts/github-stats/overview.svg" alt="GitHub Overview" width="100%"/>
```

Rules:
- Always use relative paths (never absolute GitHub raw URLs that include
  the repository name).
- Always include `alt` text.
- Always specify `width` to prevent layout shifts.
- Wrap in a `<div align="center">` block if centering is desired.
- Do not break other sections if the artifact file is missing.

---

## Defined Modules

### `github-stats`

Generates GitHub statistics SVGs using `lowlighter/metrics`.

| Artifact | Description |
|----------|-------------|
| `overview.svg` | Contribution overview |
| `languages.svg` | Top programming languages |
| `contributions.svg` | Contribution calendar |

Status: **Planned** (Phase 4)

---

### `activity`

Generates a recent public GitHub activity section.

| Artifact | Description |
|----------|-------------|
| `recent.md` | 5 most recent public events |

Status: **Planned** (Phase 4)

---

### `branding`

Hand-authored visual assets. Not a dynamic module — no workflow required.

| Asset | Description |
|-------|-------------|
| `assets/branding/header.svg` | Profile header banner |
| `assets/branding/footer.svg` | Profile footer banner |
| `assets/branding/logo.svg` | Personal logo/monogram |

Status: **In progress**

---

## Deferred Modules

The following modules are identified but deferred until after the first
migration milestone:

| Module | Reason for deferral |
|--------|-------------------|
| `music` | API strategy not defined |
| `oura` | Privacy concern; biometric data |
| `location` | Privacy concern; geolocation |
| `dashboard` | Overengineered; discarded |
| `profile-summary-cards` | Requires private action PAT |

---

## Module Naming Conventions

- Use `kebab-case` for module names.
- Module name must match across all locations:
  `.github/specs/`, `.github/scripts/`, `.github/artifacts/`,
  `.github/workflows/`, `tests/`.
- Workflow file must be named `<module>.yml`.
- Test file must be named `test_<module>.py`.
