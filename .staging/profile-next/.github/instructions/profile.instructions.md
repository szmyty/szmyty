# Profile Repository Instructions

These instructions are for GitHub Copilot working in the
`szmyty/szmyty` profile repository (staged as `szmyty/profile-next`).

## Repository Purpose

This is Alan Szmyt's public GitHub profile repository.

The primary product is `README.md`, rendered on Alan's GitHub profile page.

All automation, documentation, and tooling exists to support the quality and
reliability of the public profile.

## Key Documents

Before performing any work, consult:

- `AGENTS.md` — comprehensive AI agent instructions and conventions.
- `PLAN.md` — reconstruction and migration plan.
- `docs/ARCHITECTURE.md` — repository structure and data flow.
- `docs/MODULES.md` — module lifecycle and conventions.
- `docs/ROADMAP.md` — current status and priorities.

## Critical Rules

1. Never hardcode `profile-next` in production files.
2. Never reference `.references/` from production code or workflows.
3. Never commit secrets or personal access tokens.
4. Never include biometric, health, or geolocation data.
5. Always use `${{ github.repository_owner }}` in workflows.
6. Always use relative asset paths in README.
7. Static content before dynamic automation.
8. One module at a time; validate before moving to the next.
