# Case Study: egohygiene

**Repository:** [egohygiene/egohygiene](https://github.com/egohygiene/egohygiene)
**Maturity:** Active development — core system under construction
**Evidence ID:** `repo-egohygiene-org`

---

## Problem

Building and maintaining a personal knowledge system, health tracker, and
habit platform across multiple devices requires a consistent data model,
a portable runtime, and a design that keeps all personal data local and
private. Existing consumer apps either lack extensibility or require cloud
data storage.

## Architectural Approach

`egohygiene` is the core application and knowledge system of the Ego Hygiene
organisation — a developer platform designed as a coherent ecosystem of
composable repositories rather than a monolith:

- **Flutter / Dart** — cross-platform UI that targets mobile, desktop, and web
  from a single codebase;
- **Drift ORM** — type-safe SQLite abstraction for local data persistence;
- **TypeScript / Node.js** — server-side tooling and integrations;
- **Python** — data pipelines, analysis, and automation;
- **GitHub Actions** — CI/CD orchestration across the organisation.

The repository sits at the centre of an ecosystem:

| Repo | Role in ecosystem |
|------|------------------|
| `egohygiene` | Core application and data schema |
| `mantle` | Portable host runtime and shared conventions |
| `egolint` | Shared linting and quality policy |
| `aether` | Standards, contracts, schemas, and reusable knowledge |
| `relay` | Reusable GitHub Actions and delivery orchestration |

## Alan's Role and Key Decisions

- Defined the overall ecosystem architecture: treating the organisation as a
  platform with clear layer responsibilities rather than a loose collection
  of repositories.
- Selected Drift ORM for local-first data persistence to ensure all personal
  data stays on-device without requiring a cloud database.
- Established the shared linting baseline via `egolint` to maintain quality
  consistency as the ecosystem grows.

## Current Usable Artifact

The repository contains the application source, data schema definitions, and
CI/CD configuration. It is under active development and not yet released as a
stable user-facing product.

**Evidence:** [github.com/egohygiene](https://github.com/egohygiene)

## Maturity and Next Direction

| Attribute | Status |
|-----------|--------|
| Maturity | Active development; core architecture established |
| Test coverage | Unit and widget tests; expanding |
| Documentation | Architecture documented in the organisation's repositories |
| Next direction | First testable release; public documentation for the ecosystem architecture |
