# Ego Hygiene Architecture

Ego Hygiene follows a **foundation-first architecture** with clear separation of concerns, leveraging modern Flutter best practices and patterns.

Foundation-first means reusable platform capabilities are designed first, and application-specific features are layered on top. The long-term direction is explicit:

- ~80% of the repository should be reusable Flutter infrastructure.
- ~20% should be Ego Hygiene-specific capabilities.

Ego Hygiene is both a human-centered application and the reference implementation used to validate a reusable Flutter foundation.

## Architecture documentation

Detailed architecture documentation lives in `docs/architecture/`:

| Document | Contents |
|---|---|
| [overview.md](./docs/architecture/overview.md) | Core principles and 80/20 boundary |
| [flutter-foundation.md](./docs/architecture/flutter-foundation.md) | Technology stack, state management, localization, build system, CI/CD, development guidelines, service abstractions, and application engines |
| [design-system.md](./docs/architecture/design-system.md) | Design tokens, colors, spacing, typography, and accessibility |
| [storage.md](./docs/architecture/storage.md) | Encryption, storage architecture, privacy engine, data portability, and conflict resolution |
| [ai.md](./docs/architecture/ai.md) | AI providers, context assembly engine, memory engine, and knowledge graph |
| [routing.md](./docs/architecture/routing.md) | Navigation and router configuration |
| [testing.md](./docs/architecture/testing.md) | Testing strategy, test types, and shared helpers |
| [startup.md](./docs/architecture/startup.md) | Environment management foundation and feature flag engine |
| [extraction-plan.md](./docs/architecture/extraction-plan.md) | Flutter Foundation extraction plan: boundaries, phases, package structure, and migration risks |

## Resources

- [FOUNDATIONS.md](./FOUNDATIONS.md) — Project philosophy
- [DESIGN.md](./DESIGN.md) — Design principles
- [../../SYSTEM.md](../../SYSTEM.md) — Engineering system index
- [../../apps/egohygiene/lib/README.md](../../apps/egohygiene/lib/README.md) — Code structure
- [../../apps/egohygiene/lib/shared/README.md](../../apps/egohygiene/lib/shared/README.md) — Shared taxonomy
- [Flutter Spec](../../.github/specs/flutter-engineer.spec.md) — Flutter engineering standards
