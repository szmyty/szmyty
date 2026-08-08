# Audits

This directory is the canonical location for all repository audit reports.

---

## Audit System

Audits are periodic, evidence-based assessments of the repository's health — covering architecture, implementation quality, documentation accuracy, CI correctness, and strategic alignment.

Audits produce structured reports that become the basis for follow-up GitHub issues and backlog work.

---

## Where Audits Are Written

New audits are written to this directory:

```text
audits/
    README.md                               — this file
    repository-health-<YYYY-MM-DD>.md       — timestamped audit reports
```

**Example:**

```text
audits/repository-health-2026-07-06.md
```

---

## Naming Convention

All audit files follow this naming pattern:

```
repository-health-<YYYY-MM-DD>.md
```

Use the ISO 8601 date of the audit run.

For scoped audits (e.g., security-only or CI-only), use a descriptive prefix:

```
security-<YYYY-MM-DD>.md
ci-pipeline-<YYYY-MM-DD>.md
```

---

## Audit Status Tracking

Audit findings are tracked through GitHub Issues.

The recommended workflow:

1. An audit report is generated and committed to `audits/`.
2. Each finding of significance is converted into a GitHub Issue with a reference back to the audit report.
3. The GitHub Issue tracks remediation progress.
4. When a finding is resolved, the issue is closed and linked to the resolving PR.

Audit reports themselves are **not updated** after initial publication. They are immutable records of the repository state at a point in time.

---

## Immutability

Audit reports are immutable once committed.

Do not edit an audit report to reflect post-audit changes.

If a finding is superseded or resolved, document that in the resolving GitHub Issue or PR — not in the original audit file.

---

## How Findings Become Backlog Work

Each audit finding is tagged with:

- **ID** — e.g., `AUDIT-012`
- **Severity** — Critical, High, Medium, Low, or Polish
- **Summary** — brief description
- **Recommendation** — what action should be taken

To convert a finding to backlog work:

1. Open a GitHub Issue referencing the audit finding ID.
2. Add the issue to the relevant project backlog.
3. Link the issue back to the audit report for traceability.

Issues created from audit findings are typically labeled `audit` or tagged with the relevant phase.

---

## Superseded Audits

When a newer holistic audit is run after an older one:

- The older audit is **preserved** and not deleted.
- The newer audit includes a summary of what has changed since the previous audit.
- Both files remain in `audits/` as historical record.

---

## Relationship to `docs/AUDIT.md`

`docs/AUDIT.md` contains the first comprehensive architecture and UX audit conducted for Ego Hygiene (dated 2026-07-06). It was created before the formal `audits/` system was established.

That report is preserved in its original location as a historical artifact.

Future audits are written to this directory.

For historical reference: [`docs/AUDIT.md`](../docs/AUDIT.md)

---

## Scoped vs. Holistic Audits

**Holistic audits** assess the full repository across architecture, implementation, documentation, CI, and strategic alignment.

**Scoped audits** focus on a specific system or concern, such as:

- security posture
- CI pipeline health
- Flutter application architecture
- documentation accuracy

Both types follow the same naming convention and immutability rules.

---

## Operator Notes

The `auditor` agent is configured to write reports to this directory.

See `.github/agents/auditor.agent.md` for the agent definition and `.github/specs/auditor.spec.md` for the auditor specification.
