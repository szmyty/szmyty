# Content Guidelines

**Repository:** `szmyty/szmyty`
**Status:** Active

This document defines the rules for authoring, updating, and reviewing content
in the public profile README and its supporting evidence catalog.  Following
these rules ensures that every public claim is accurate, bounded, and
maintainable.

---

## 1. Claim and Evidence Rules

### Evidence catalog

All factual claims in `README.md` must have a corresponding record in
`profile/content/evidence.yml` with `status: verified`.

**A claim may only appear in rendered README content when all of the following
are true:**

1. A record exists in `evidence.yml` with a matching `id`.
2. The record has `status: verified`.
3. The record has `sensitivity: public`.
4. The claim text in the README does not exceed the scope of the `claim` field
   in the record.

**A claim must be absent from rendered content when:**

- The record has `status: needs-user-verification`.
- The record has `status: excluded`.
- The record has `sensitivity: sensitive` or `sensitivity: internal`.
- No corresponding record exists in `evidence.yml`.

### Evidence types

| Type | Meaning | Example |
|------|---------|---------|
| `url` | The claim is directly inspectable at a public URL | GitHub repository, merged PR |
| `repo-path` | The claim is supported by a file in this repository (`repo_path` YAML field) | `pyproject.toml` |
| `self-reported` | The claim comes from the subject and cannot be independently verified via a public artifact | GitHub profile bio |
| `inferred` | The claim is a reasonable conclusion from observable public signals, but is not explicitly stated anywhere | Language inferred from repository contents |
| `none` | No supporting artifact has been located yet | Requires user verification |

### Needs-user-verification protocol

When a record is marked `needs-user-verification`:

1. Open or reference an issue requesting the specific artifact or confirmation
   from Alan Szmyt (`@szmyty`).
2. Do not resolve the record to `verified` without an explicit response or a
   publicly inspectable artifact.
3. Do not include the claim in any rendered README section while it remains
   unverified.

---

## 2. Tense and Tone

- Write in **present tense** for current capabilities and ongoing work.
- Write in **past tense** for completed projects and historical events.
- Lead with **outcomes**, not process.  Say what changed or was made possible,
  not only what technology was used.
- State **ownership clearly but proportionally**.  Distinguish sole authorship
  ("designed and built") from collaborative contribution ("contributed and
  merged").  Do not overstate solo authorship for team work.
- Avoid generic evaluative phrases: "results-driven," "passionate about,"
  "expert in," "highly skilled," "world-class."  If the surrounding evidence
  makes such claims unnecessary, omit them.
- Do not convert technology names into accomplishment claims.  "Uses Docker"
  is not an outcome; "packaged the system as a single Docker Compose stack
  that any developer can run with one command" describes a concrete capability.
- Do not fabricate or estimate: repository adoption, stars, users, releases,
  scale, or time savings must not appear without a verifiable source.

---

## 3. Handling Confidential and Restricted Work

### General policy

Employment history is held under a confidentiality policy and is not published
in this repository.  See evidence record `experience-employer-current` for the
rationale.

### MIT Lincoln Laboratory (and similar organisations)

If professional experience at a research laboratory or restricted programme is
ever added to `evidence.yml`, the following rules apply:

- **Do not** publish: system names, programme names, customer or mission
  identities, dataset descriptions, internal performance metrics, security
  clearance level or scope, team or division names, internal tools or
  codebases, or any detail that could narrow the set of programmes the person
  worked on.
- **Do publish** (with user confirmation): employment dates at country-level
  chronological granularity, publicly announced research areas, and job titles
  that are themselves publicly disclosed by the employer.
- Mark any record touching restricted work `sensitivity: internal` and
  `status: excluded` unless specific public disclosure is confirmed in writing
  by the user and supported by a publicly available citation.
- When in doubt, err toward exclusion and request user guidance in the PR.

### Sensitive personal data

Location, personal email, LinkedIn, and other contact details may only appear
in `README.md` when the corresponding evidence record is `verified` and the
user has explicitly confirmed that the specific granularity is acceptable for
public disclosure. See `identity-location` and `contact-linkedin` for claims
that remain gated and excluded from the public README.

---

## 4. How to Update Current Focus and Availability

The **Current Focus** table and any availability or target-role language must
be updated **manually** by the repository owner (`@szmyty`) or by an agent
acting on explicit user instruction.

To update:

1. Identify the evidence record ID for each changed claim (or create a new
   record in `evidence.yml` for new claims).
2. Set the record `status` to `verified` and `last_reviewed` to today's date.
3. Update the corresponding section in `README.md`.
4. Open a pull request referencing the evidence record IDs changed.

Do not update the Current Focus or availability language based on inferred
signals, old README content, or staged content in `.staging/`.

---

## 5. How Accomplishments Graduate from Candidate to Verified

An accomplishment begins its life as a `needs-user-verification` record in
`evidence.yml`.  It graduates to `verified` through the following steps:

| Step | Action | Who |
|------|--------|-----|
| 1 | A candidate claim is drafted and a record is added to `evidence.yml` with `status: needs-user-verification` | Agent or contributor |
| 2 | An issue or PR comment requests confirmation of the specific artifact or metric | Agent |
| 3 | The user (`@szmyty`) supplies the artifact URL, confirms the wording, or provides a clear correction | `@szmyty` |
| 4 | The record is updated to `status: verified` with the confirmed `url` or `repo_path` and today's `last_reviewed` date | Agent acting on user response |
| 5 | The claim is added to the appropriate README section | Agent |
| 6 | A PR is opened referencing the evidence record ID and the user response | Agent |

Claims must **not** graduate automatically.  A human confirmation step is
always required for facts that cannot be independently observed at a public URL.

---

## 6. Content Freshness, Owners, and Review Cadence

### Owners

| Content area | Owner |
|-------------|-------|
| Evidence catalog (`evidence.yml`) | `@szmyty` |
| README narrative sections | `@szmyty` |
| This document | `@szmyty` |

### Review cadence

| Trigger | Action |
|---------|--------|
| Any new role, project, or accomplishment | Add a `needs-user-verification` record; follow the graduation workflow |
| Every six months | Review all `last_reviewed` dates; re-verify any record older than 12 months |
| Repository activity drops or focus shifts | Update the **Current Focus** table and any availability language |
| A linked repository becomes private or is deleted | Remove or update the corresponding README entry; change the evidence record to `status: needs-user-verification` |

### Stale evidence

A record is considered stale when `last_reviewed` is more than 12 months before
today.  Stale records must be re-reviewed before their claims are added to or
retained in the rendered README.

---

## 7. Relationship to the Profile Reconstruction Epic

This document was created as part of the profile reconstruction effort tracked
in [szmyty/szmyty#65](https://github.com/szmyty/szmyty/issues/65) and
specifically addresses the content governance requirement from
[szmyty/szmyty#71](https://github.com/szmyty/szmyty/issues/71).

The queue key for this work stream is `szmyty-profile-rebuild-06`.
