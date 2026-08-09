# Case Study: universal

**Repository:** [szmyty/universal](https://github.com/szmyty/universal)
**Maturity:** Active development — usable foundation
**Evidence ID:** `repo-universal`

---

## Problem

Across multiple personal and organisational repositories, code formatting,
linting, spellcheck, and CI conventions diverge as each project acquires its
own bespoke configuration. Onboarding a new contributor or spinning up a new
repository means re-solving the same setup problems, accumulating configuration
drift over time.

## Architectural Approach

`universal` is a composable shell toolkit that centralises developer experience
(DX) conventions for monorepo and multi-project contexts:

- **Formatting** — consistent code style enforced via shared formatter
  configurations;
- **Linting** — opinionated rule sets layered over language-specific linters;
- **Spellcheck** — project-agnostic dictionary and ignore-list management;
- **CI scaffolding** — reusable GitHub Actions workflow templates.

The design principle is *layering without forking*: any repository can include
`universal` conventions without modifying them, keeping the source of truth
centralised.

Key architectural boundaries:

| Boundary | Decision |
|----------|----------|
| Configuration inheritance | Shared configs are sourced; repositories extend rather than copy |
| CI reuse | Workflow templates are parameterised for per-repo customisation |
| Shell portability | POSIX-compatible shell scripts target broad Unix compatibility |

## Alan's Role and Key Decisions

- Identified configuration drift across personal projects as the core problem
  and designed a composition model that scales to multiple repositories.
- Chose shell scripting over a compiled tool to keep the dependency surface
  minimal and allow inline customisation.
- Structured the CI templates to be parameterisable so they serve both small
  personal projects and multi-repository organisations.

## Current Usable Artifact

The repository contains shell scripts, shared lint and formatter configurations,
and GitHub Actions workflow templates that can be adopted by any repository.

**Evidence:** [github.com/szmyty/universal](https://github.com/szmyty/universal)

## Maturity and Next Direction

| Attribute | Status |
|-----------|--------|
| Maturity | Usable foundation; conventions stabilising |
| Test coverage | Manual validation across consuming repositories |
| Documentation | README with integration instructions |
| Next direction | Publish as a GitHub Actions reusable workflow package; add automated compatibility tests |
