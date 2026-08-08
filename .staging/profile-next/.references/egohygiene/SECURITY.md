# Security Policy

Ego Hygiene is a personal cognition system that stores sensitive personal data — reflections, mental states, goals, and cognition patterns. The security and privacy of that data is a core project commitment.

This document defines how security vulnerabilities are reported, how they are handled, and what reporters can expect.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| `development` (latest main) | ✅ Active |
| Latest stable release | ✅ Active |
| Older releases | ❌ Not actively patched — upgrade to latest |

Security fixes are applied to the current `main` branch and the latest stable release. Older releases do not receive backported patches.

---

## Reporting a Vulnerability

**Do not report vulnerabilities through public GitHub issues.**

Public disclosure before a fix is available can put users at risk.

### Preferred Channel: GitHub Private Security Advisories

The preferred method for reporting vulnerabilities is through GitHub's private Security Advisory system:

1. Navigate to the [Security tab](https://github.com/egohygiene/egohygiene/security) of this repository.
2. Click **"Report a vulnerability"**.
3. Provide the information requested in the next section.

This channel is private, encrypted, and directly accessible to the repository maintainers.

---

## What to Include in Your Report

A useful report includes:

- **Description** — a clear summary of the vulnerability
- **Component** — which part of the system is affected (e.g., storage layer, AI provider, CI pipeline)
- **Steps to reproduce** — the minimum steps needed to trigger the issue
- **Impact** — who is affected and what an attacker could do
- **Environment** — platform (Android, Web, Linux), OS version, app version or commit SHA
- **Suggested fix** (optional) — if you have a proposed remediation

You do not need to have a working exploit. Partial or theoretical findings are welcome.

---

## Acknowledgment and Response

| Milestone | Expected Window |
|-----------|-----------------|
| Initial acknowledgment | Within 5 business days |
| Status update | Within 10 business days |
| Patch or mitigation plan | Determined by severity |

These are targets, not guarantees. Complex or severe issues may require more time.

---

## Responsible Disclosure

We ask that reporters:

- Allow reasonable time for a fix before public disclosure.
- Avoid accessing, modifying, or exfiltrating user data during research.
- Avoid denial-of-service testing or disruptive testing against production systems.
- Act in good faith throughout the disclosure process.

We commit to:

- Acknowledging your report promptly.
- Keeping you informed of progress.
- Crediting you in the release notes if you choose (reporter's choice).
- Not pursuing legal action against good-faith security researchers.

---

## Safe Harbor

Ego Hygiene supports responsible security research. Good-faith vulnerability research that complies with this policy will not result in legal action. We view security researchers as collaborators, not adversaries.

This safe harbor applies only to research conducted within the scope defined in this policy.

---

## Handling of Sensitive Personal and Mental Health Data

Ego Hygiene stores highly sensitive personal data including reflections, emotional states, cognition patterns, and goals. Security reports involving potential exposure of this class of data are treated with the highest priority.

If your report involves a vulnerability that could expose stored personal or mental-health-adjacent data, please note this explicitly in your report. We will fast-track review and remediation for this class of finding.

---

## Scope

**In scope:**

- The Ego Hygiene Flutter application (`apps/egohygiene/`)
- Local data storage and persistence layer
- AI provider abstractions and conversation pipeline
- CI/CD pipeline and GitHub Actions workflows
- Publishing automation workflows
- Repository configuration and secrets handling

**Out of scope:**

- Third-party dependencies (report these to their upstream maintainers; see [Dependencies](#dependencies-and-third-party-vulnerabilities) below)
- The `mindgarden/` Obsidian vault (personal knowledge management, not application code)
- Theoretical vulnerabilities with no practical exploit path
- Social engineering attacks

---

## Dependencies and Third-Party Vulnerabilities

Ego Hygiene uses a number of open-source dependencies including Flutter packages, Python libraries, and GitHub Actions. If you discover a vulnerability in a third-party dependency:

1. Report it to the upstream package maintainer.
2. If the vulnerability is specifically exploitable through Ego Hygiene's use of that dependency, also report it to us using the process above.

We monitor dependency updates and apply patches as part of regular maintenance.

---

## Questions

If you have questions about this policy or are unsure whether something qualifies as a security issue, open a private GitHub Security Advisory to ask. We will respond and guide you to the right process.
