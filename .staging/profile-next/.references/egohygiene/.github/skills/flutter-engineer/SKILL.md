---
name: flutter-engineer
description: Implement Flutter features within the Ego Hygiene ecosystem following repository architecture and engineering standards.
version: 1.0.0
status: draft
---

# Flutter Engineer

Implement Flutter features within the Ego Hygiene ecosystem.

---

## Purpose

This skill encodes Flutter implementation workflows for the `apps/egohygiene` application. It delegates to the `flutter-engineer` agent for complex, autonomous implementation tasks, and provides lightweight guidance for targeted feature work.

> **Note:** This skill is a placeholder. Full implementation is tracked as follow-up work.
> For autonomous implementation tasks, use the `flutter-engineer` agent directly.

---

## References

- `.github/agents/flutter-engineer.agent.md` — authoritative Flutter agent definition
- `.github/specs/flutter-engineer.spec.md` — Flutter engineering contract
- `.github/skills/flutter/` — Flutter reference material (architecture, state management, testing, and more)
- `ARCHITECTURE.md` — repository architecture conventions
- `apps/egohygiene/` — Flutter application source

---

## Constraints

- All Flutter work must follow `.github/specs/flutter-engineer.spec.md`.
- All file operations must be relative to `apps/egohygiene/` unless explicitly modifying root repository files.
- Do not introduce dependencies not already approved in the specification.
