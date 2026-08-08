# Architecture

This file is the root index for repository architecture.

## Canonical Sources

- [Repository architecture reference](.engineering/architecture/ARCHITECTURE.md)
- [Architectural decisions](.engineering/architecture/DECISIONS.md)
- [Architecture overview](docs/architecture/overview.md)
- [Flutter foundation implementation](docs/architecture/flutter-foundation.md)
- [Publishing automation](docs/architecture/publishing-automation.md)
- [Shared module taxonomy](apps/egohygiene/lib/shared/README.md)
- [Schema boundaries](schemas/README.md)
- [Website placeholder boundary](website/README.md)
- [Audit reports](audits/README.md)

## Boundary Summary

- `apps/egohygiene/lib/features/` contains application-specific product features.
- `apps/egohygiene/lib/shared/` contains reusable cross-feature foundation modules.
- `schemas/` contains canonical JSON schemas for cross-system contracts.
- `website/` is reserved for a future repository-owned web surface and is intentionally unimplemented today.
- `audits/` contains timestamped repository health audit reports.
