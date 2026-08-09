# Resume Privacy and Metadata Checklist

Use this checklist before setting `enabled: true` in
`profile/content/resume-config.yml` or linking to any public resume artifact.

---

## Content checks

- [ ] **No home address** — street, city, state, ZIP, and country are removed.
- [ ] **No private phone number** — only a public contact method (e.g. GitHub noreply) appears.
- [ ] **No personal email** — only the GitHub noreply address or an explicitly approved address.
- [ ] **No employer details beyond those already intentionally public** — confirm against the evidence catalog.
- [ ] **No client or project names under NDA** — verify each entry is public information.
- [ ] **No embedded comments or revision history** — strip Word change-tracking and PDF comments.

## PDF metadata checks

- [ ] **Author field** — confirm it contains only the public name (Alan Szmyt) or is blank.
- [ ] **Creator/Producer fields** — contain no personal software license identifiers or internal tool versions.
- [ ] **Keywords/Subject fields** — contain no sensitive tags.
- [ ] **Creation/Modification dates** — do not reveal timezone or internal workflow details.
- [ ] **No hyperlinks to private or internal resources** (e.g. internal wikis, private repos).

## File delivery checks

- [ ] **Stable URL or path** — the `public_url` in `resume-config.yml` resolves without redirect loops.
- [ ] **File size is reasonable** — under 2 MB for a plain resume PDF.
- [ ] **Filename contains no version numbers or dates** that would break the public URL on update.

## Final sign-off

- [ ] Alan has reviewed and approved the final artifact.
- [ ] The evidence record `resume-public-document` in `profile/content/evidence.yml` is updated to `status: verified`.
- [ ] `enabled: true` is set in `profile/content/resume-config.yml`.

---

After all items are checked, commit the updated config and evidence record in
the same changeset as the public artifact to keep the repository in a
consistent, reviewable state.
