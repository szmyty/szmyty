---
name: github-issue
description: Author a scoped, implementation-ready GitHub issue from ideas, specifications, audits, or bug reports.
version: 1.0.0
status: draft
---

# GitHub Issue

Author a scoped, implementation-ready GitHub issue for this repository.

---

## Purpose

This skill encodes the workflow for transforming ideas, specifications, audits, bug reports, and brain dumps into clear GitHub issues that humans and coding agents can execute.

> **Note:** This skill is a placeholder. Full implementation is tracked as follow-up work.
> For complex issue authoring, use the `github-issue-creator` agent directly.

---

## References

- `.github/agents/github-issue-creator.agent.md` — authoritative issue-creator agent definition
- `.github/specs/github-issue-creator.spec.md` — issue authoring contract
- `.github/specs/specfile.spec.md` — specification file contract
- `.github/ISSUE_TEMPLATE/` — repository issue templates

---

## Constraints

- Follow `.github/specs/github-issue-creator.spec.md` as the authoritative contract.
- Do not implement the requested work — create the execution contract only.
- Use repository issue templates when they exist.
