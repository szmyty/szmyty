# Profile README adaptation guide

Step-by-step instructions for adapting
`templates/profile/README.md` to a personal GitHub profile.

A profile README lives in a repository named `<username>/<username>` and is
displayed at `https://github.com/<username>`.

---

## How the profile template relates to the repository template

The profile template **extends** the shared principles from the repository
template rather than duplicating them:

- It uses the same token syntax (`{{TOKEN}}`), optional-block markers, and
  generated-region markers.
- It replaces the project-centric sections (Installation, Usage, Configuration)
  with profile-centric sections (About, Highlights, Pinned projects, Metrics).
- Validation rules are identical; only the personal-identifier block-list
  differs (the profile template may contain *your* username but must not
  contain tokens referencing other individuals).

---

## 1. Required tokens

| Token | Example value |
|-------|---------------|
| `{{PROFILE_USERNAME}}` | `octocat` |
| `{{PROFILE_TAGLINE}}` | `Software engineer who loves open source` |

---

## 2. Optional tokens

| Token | Block | Example value |
|-------|-------|---------------|
| `{{PROFILE_LOCATION}}` | location-badge | `San Francisco, CA` |
| `{{PROFILE_HIGHLIGHT_1}}` | highlights | `Building developer tools` |
| `{{PROFILE_HIGHLIGHT_2}}` | highlights | `Open-source contributor` |
| `{{PROFILE_HIGHLIGHT_3}}` | highlights | `Writing about systems design` |

---

## 3. Remove optional sections

Remove any block you do not want by deleting from
`<!-- OPTIONAL BLOCK: name -->` through `<!-- END:name -->` inclusive.

**Sections and typical reasons to remove:**

| Section | Remove when |
|---------|-------------|
| location-badge | You prefer privacy or work remotely without a fixed city |
| highlights | The About paragraph already covers key points |
| pinned-projects | GitHub's built-in six-pin feature is sufficient |
| metrics-dashboard | You do not run a metrics workflow |
| social-links | You rely on the GitHub profile sidebar for links |

---

## 4. Validate

```sh
python templates/validate_template.py path/to/your/profile/README.md
```

The validator applies the same rules as the repository template plus one
additional check: the profile template must not contain tokens that reference
personal identifiers other than `{{PROFILE_USERNAME}}` and
`{{PROFILE_TAGLINE}}`.

---

## 5. Adaptation walkthrough — personal GitHub profile

Goal: a profile README that establishes trust with a visitor in under 30 seconds.

1. Copy `templates/profile/README.md` to `<username>/<username>/README.md`.
2. Replace all required tokens.
3. Write the **About** paragraph in first person.  Two or three sentences is
   enough.  Avoid listing employers by name or including employment dates.
4. Fill in three **Highlights** that reflect current interests, not a CV.
5. Remove `pinned-projects` if you use GitHub's built-in pin feature.
6. Remove `metrics-dashboard` if you have not set up a metrics workflow.
7. Run the validator.  Fix any errors before pushing.

---

## 6. Heading hierarchy reference

```
# H1   — your username (exactly one)
## H2  — top-level profile sections
### H3 — subsections (use sparingly in profiles)
```
