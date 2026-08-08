# Schemas

`schemas/` stores repository-level canonical schemas used to define durable content/data contracts.

## Ownership

- **Owned by:** repository architecture/foundation work
- **Current maintained scope:** practice-domain schemas used outside a single Flutter implementation

## Current Scope

- `practices/reflection.schema.json` defines the canonical reflection record contract.

The schema is intentionally implementation-independent and can be consumed by Flutter, publishing tooling, and future services.

## Relationship to Publishing Schemas

- `schemas/` is for repository-level canonical contracts.
- `publishing/schemas/` is for publishing-pipeline/content-channel-specific contracts.

When a schema is cross-system and long-lived, it belongs here.  
When a schema is channel/tool specific, it belongs under `publishing/schemas/`.

## Evolution Boundary

- Prefer additive, backward-compatible changes.
- Version through `$id` and schema metadata when breaking changes are unavoidable.
- Keep implementation details out of canonical schemas.
