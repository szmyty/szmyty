# Website Placeholder

`website/` is reserved for the future repository-owned web experience.

## Why this directory exists now

- to reserve a clear architectural home for the website surface
- to avoid future ambiguity about where web-only app code should live
- to keep repository topology stable as web work begins

## Current state

- Website implementation has **not** started.
- The directory currently contains shared TypeScript baseline configuration (`tsconfig.base.json`) only.

## Planned ownership boundary

- **Owned by:** repository/web platform work
- **Intended scope:** website-specific frontend implementation and build configuration
- **Out of scope:** Flutter app code (`apps/egohygiene/`) and publishing channel mirrors (`publishing/channels/website/`)
