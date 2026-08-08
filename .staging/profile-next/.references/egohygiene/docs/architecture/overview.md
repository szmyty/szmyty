# Architecture Overview

Ego Hygiene follows a **foundation-first architecture** with clear separation of concerns, leveraging modern Flutter best practices and patterns.

Foundation-first means reusable platform capabilities are designed first, and application-specific features are layered on top.

The long-term direction is explicit:

- ~80% of the repository should be reusable Flutter infrastructure.
- ~20% should be Ego Hygiene-specific capabilities.

Ego Hygiene is both:

- a human-centered application
- the reference implementation used to validate a reusable Flutter foundation

## Core Architecture Principles

### 1. Feature-First Organization

Each feature is self-contained with its own presentation, business logic, and data layers:

```
features/
  feature_name/
    presentation/  - UI components and screens
    providers/     - Feature-specific state management
    domain/        - Business logic and entities
    data/          - Data sources and repositories
```

### 2. Shared Foundation

Common functionality is centralized in the `shared/` directory:

```
shared/
  theme/         - Design system (colors, spacing, typography)
  routing/       - Navigation configuration
  localization/  - Internationalization
  services/      - Service abstractions
  providers/     - App-wide state management
  models/        - Shared domain models
  widgets/       - Reusable UI components
```

Canonical taxonomy and ownership boundaries are documented in:

- [apps/egohygiene/lib/shared/README.md](../../apps/egohygiene/lib/shared/README.md)

### 3. 80/20 Boundary

Reusable foundation categories include:

- Authentication
- Startup lifecycle
- Permission lifecycle
- Notification lifecycle
- Routing and navigation
- Theme and design system
- Localization
- Storage
- State management
- AI abstractions
- Context assembly
- Lifecycle managers
- Developer experience
- CI/CD
- Release pipeline
- Testing

Ego Hygiene-specific concepts include:

- Ontology
- Domains
- Practices
- Reflection
- Insights
- Therapy
- Knowledge Graph
- Human Development

### 4. Framework Before Features

Whenever a capability could reasonably benefit future Flutter applications, it should first be designed as reusable infrastructure.

Application-specific behavior should build on that framework rather than be embedded inside it.

## Documentation Index

| Document | Description |
|---|---|
| [flutter-foundation.md](./flutter-foundation.md) | Technology stack, state management, localization, build system, CI/CD, service abstractions, and application engines |
| [design-system.md](./design-system.md) | Design tokens, colors, spacing, typography, and accessibility |
| [storage.md](./storage.md) | Encryption, storage architecture, privacy, data portability, and conflict resolution |
| [ai.md](./ai.md) | AI providers, context assembly engine, memory engine, and knowledge graph |
| [routing.md](./routing.md) | Navigation and router configuration |
| [testing.md](./testing.md) | Testing strategy, test types, and shared helpers |
| [startup.md](./startup.md) | Environment management foundation and feature flag engine |
| [extraction-plan.md](./extraction-plan.md) | Flutter Foundation extraction plan: boundaries, phases, package structure, and migration risks |

## Resources

- [.engineering/architecture/FOUNDATIONS.md](../../.engineering/architecture/FOUNDATIONS.md) - Project philosophy
- [.engineering/architecture/DESIGN.md](../../.engineering/architecture/DESIGN.md) - Design principles
- [SYSTEM.md](../../SYSTEM.md) - Engineering system index
- [apps/egohygiene/lib/README.md](../../apps/egohygiene/lib/README.md) - Code structure
- [Flutter Spec](../../.github/specs/flutter-engineer.spec.md) - Flutter standards
