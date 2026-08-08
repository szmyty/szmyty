# 📚 Reading Order

> *Recommended reading paths by audience.*

---

## Purpose

This document defines the recommended order to read repository documentation.

Different audiences need different context.

Read what is relevant to your role and goal.

---

## Audience Paths

---

### 🧑‍💻 New Human Contributor

You are setting up the project for the first time and want to contribute.

**Minimum path (30 minutes):**

1. [README.md](../README.md) — overview, quick start, development commands
2. [docs/developer-setup.md](developer-setup.md) — environment setup
3. [ARCHITECTURE.md](../ARCHITECTURE.md) — architecture principles
4. [docs/CONTRIBUTOR_GUIDE.md](CONTRIBUTOR_GUIDE.md) — contribution workflow
5. [docs/commits.md](commits.md) — commit conventions

**Extended path:**

6. [.engineering/architecture/FOUNDATIONS.md](../.engineering/architecture/FOUNDATIONS.md) — product philosophy
7. [.engineering/architecture/DESIGN.md](../.engineering/architecture/DESIGN.md) — design system
8. [docs/architecture/overview.md](architecture/overview.md) — feature-first organization
9. [docs/architecture/flutter-foundation.md](architecture/flutter-foundation.md) — stack details
10. [docs/testing.md](testing.md) — testing strategy

---

### 🤖 AI Agent

You are an AI system about to perform implementation work.

Architecture is authoritative. Load context before implementation begins.

**Required reading (load before any task):**

1. [ONBOARDING.md](../ONBOARDING.md) — AI synchronization protocol and operating rules
2. [SYSTEM.md](../SYSTEM.md) — engineering system, AI role, execution model
3. [ARCHITECTURE.md](../ARCHITECTURE.md) — architecture reference and 80/20 boundary
4. [docs/REPOSITORY_MAP.md](REPOSITORY_MAP.md) — full structural map of the repository
5. [.engineering/architecture/FOUNDATIONS.md](../.engineering/architecture/FOUNDATIONS.md) — product philosophy and purpose

**Load based on task domain:**

| Task Area | Read |
|---|---|
| Flutter feature work | [docs/architecture/flutter-foundation.md](architecture/flutter-foundation.md) |
| State management | [.github/skills/flutter/state-management.md](../.github/skills/flutter/state-management.md) |
| Design and theming | [.engineering/architecture/DESIGN.md](../.engineering/architecture/DESIGN.md) · [docs/architecture/design-system.md](architecture/design-system.md) |
| Storage and persistence | [docs/architecture/storage.md](architecture/storage.md) · [.github/skills/flutter/offline-first.md](../.github/skills/flutter/offline-first.md) |
| AI integration | [docs/architecture/ai.md](architecture/ai.md) · [.github/skills/flutter/ai-providers.md](../.github/skills/flutter/ai-providers.md) |
| Navigation | [docs/architecture/routing.md](architecture/routing.md) · [.github/skills/flutter/routing.md](../.github/skills/flutter/routing.md) |
| Localization | [.github/skills/flutter/localization.md](../.github/skills/flutter/localization.md) |
| Testing | [docs/testing.md](testing.md) · [docs/architecture/testing.md](architecture/testing.md) |
| Publishing automation | [docs/architecture/publishing-automation.md](architecture/publishing-automation.md) |
| Architectural decisions | [.engineering/architecture/DECISIONS.md](../.engineering/architecture/DECISIONS.md) |
| New feature | [.github/specs/flutter-application-foundation.spec.md](../.github/specs/flutter-application-foundation.spec.md) |

**Load agent and specification context:**

- [.github/agents/flutter-engineer.agent.md](../.github/agents/flutter-engineer.agent.md)
- Relevant specification file from [.github/specs/](../.github/specs/)

---

### 🏛️ Architecture Explorer

You want to understand how the system is designed.

1. [docs/architecture/overview.md](architecture/overview.md) — principles and 80/20 boundary
2. [ARCHITECTURE.md](../ARCHITECTURE.md) — architecture reference
3. [SYSTEM.md](../SYSTEM.md) — engineering system model
4. [.engineering/architecture/DECISIONS.md](../.engineering/architecture/DECISIONS.md) — architectural decisions and rationale
5. [.engineering/architecture/ECOSYSTEM.md](../.engineering/architecture/ECOSYSTEM.md) — broader ecosystem context
6. [docs/architecture/flutter-foundation.md](architecture/flutter-foundation.md) — stack and engines
7. [docs/architecture/ai.md](architecture/ai.md) — AI architecture
8. [docs/architecture/storage.md](architecture/storage.md) — storage architecture
9. [docs/architecture/publishing-automation.md](architecture/publishing-automation.md) — publishing automation workflows
10. [docs/architecture/extraction-plan.md](architecture/extraction-plan.md) — foundation extraction plan

---

### 🎨 Design and UX Contributor

You are working on design, UI, or the design system.

1. [.engineering/architecture/DESIGN.md](../.engineering/architecture/DESIGN.md) — design principles and visual language
2. [.engineering/architecture/DESIGN_SYSTEM.md](../.engineering/architecture/DESIGN_SYSTEM.md) — design system specification
3. [docs/architecture/design-system.md](architecture/design-system.md) — design tokens and implementation
4. [.github/skills/flutter/design-system.md](../.github/skills/flutter/design-system.md) — design token usage in code

---

### 🧠 Domain and Product Contributor

You are working on product thinking, domain models, or practices.

1. [.engineering/architecture/FOUNDATIONS.md](../.engineering/architecture/FOUNDATIONS.md) — what Ego Hygiene is and why it exists
2. [VISION.md](../VISION.md) — long-term vision
3. [PURPOSE.md](../PURPOSE.md) — mission and core purpose
4. [.engineering/architecture/MANIFESTO.md](../.engineering/architecture/MANIFESTO.md) — beliefs and commitments
5. [.engineering/architecture/ONTOLOGY.md](../.engineering/architecture/ONTOLOGY.md) — domain concepts and relationships
6. [.engineering/architecture/METHODOLOGY.md](../.engineering/architecture/METHODOLOGY.md) — methodology
7. [docs/domains/README.md](domains/README.md) — domain documentation
8. [docs/practices/README.md](practices/README.md) — practice documentation

---

### 🔬 Research Contributor

You are contributing research that informs the product.

1. [.engineering/architecture/FOUNDATIONS.md](../.engineering/architecture/FOUNDATIONS.md) — why this research matters
2. [.engineering/architecture/EPISTEMOLOGY.md](../.engineering/architecture/EPISTEMOLOGY.md) — how knowledge is evaluated
3. [docs/research/README.md](research/README.md) — research documentation index

---

## Full Document Index

For a complete structural map of every file, see [docs/REPOSITORY_MAP.md](REPOSITORY_MAP.md).

---

## Guiding Principle

Read from the general to the specific.

Start with philosophy and architecture.

Then move to implementation.

    Understanding first.
    Implementation second.
