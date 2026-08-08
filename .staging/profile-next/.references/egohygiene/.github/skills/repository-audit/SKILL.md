---
name: repository-audit
description: Perform an evidence-based repository audit and produce a structured report under audits/.
version: 1.0.0
status: draft
---

# Repository Audit

Perform an evidence-based audit of this repository and produce a standardized report.

---

## Purpose

This skill encodes the workflow for scoping, executing, and documenting repository audits. It delegates to the `auditor` agent for full audit execution and provides lightweight guidance for targeted audit requests.

> **Note:** This skill is a placeholder. Full implementation is tracked as follow-up work.
> For full audit execution, use the `auditor` agent directly.

---

## References

- `.github/agents/auditor.agent.md` — authoritative auditor agent definition
- `.github/specs/auditor.spec.md` — audit contract and output format
- `audits/` — existing audit reports

---

## Constraints

- Follow `.github/specs/auditor.spec.md` as the authoritative contract.
- Audits are read-only by default — do not modify source files during an audit.
- Evidence must be cited; do not report findings without supporting evidence.
- Report positive observations alongside defect findings.
