# Repository README adaptation guide

Step-by-step instructions for adapting
`templates/repository/README.md` to a specific project.

---

## 1. Identify your scenario

| Scenario | Relevant optional blocks to keep | Blocks to remove |
|----------|----------------------------------|-----------------|
| Small library / CLI | badge-row, package-manager-install, extended-example | contributing-link (if no guide yet) |
| Application / service | badge-row, extended-example, contributing-link | package-manager-install |
| Infrastructure repository | badge-row, contributing-link | package-manager-install, extended-example |
| GitHub profile | _(use the profile template instead)_ | — |

---

## 2. Replace required tokens

All `{{TOKEN}}` placeholders **must** be replaced before publishing.
The validator will fail if any remain.

| Token | Where to find the value |
|-------|------------------------|
| `{{PROJECT_NAME}}` | Your repository name or product name |
| `{{PROJECT_DESCRIPTION}}` | One sentence from your project pitch |
| `{{OWNER}}` | Your GitHub username or organisation |
| `{{REPO}}` | Your GitHub repository slug |
| `{{LICENSE_SPDX}}` | SPDX identifier, e.g. `MIT`, `Apache-2.0` |
| `{{LANGUAGE_OR_STACK}}` | Primary language or framework, e.g. `Go`, `Python` |

---

## 3. Handle optional tokens

Optional tokens appear inside optional blocks.  If you remove the block,
delete the token with it.  If you keep the block, replace the token.

| Token | Block | Example value |
|-------|-------|---------------|
| `{{BADGE_CI_WORKFLOW}}` | badge-row | `ci.yml` |
| `{{BADGE_COVERAGE_TOKEN}}` | badge-row | _(remove badge if unused)_ |
| `{{DOCS_URL}}` | contributing-link, reference links | `https://docs.example.com` |
| `{{PACKAGE_MANAGER_INSTALL}}` | package-manager-install | `pip install mypackage` |
| `{{CONTRIBUTING_GUIDE_URL}}` | contributing-link | `CONTRIBUTING.md` |

---

## 4. Remove optional sections

Optional sections are wrapped in `<!-- OPTIONAL BLOCK: name -->` comments
followed by `<!-- BEGIN:name -->` / `<!-- END:name -->` markers.

**Rules when removing an optional section:**
- Delete everything from `<!-- OPTIONAL BLOCK: … -->` through `<!-- END:… -->`.
- Verify that no heading is left orphaned (a heading with no content below it).
- Re-run the validator after removal.

---

## 5. Validate

```sh
python templates/validate_template.py path/to/your/README.md
```

The validator checks:
- No unresolved `{{TOKEN}}` values remain.
- Exactly one H1 heading is present.
- Headings do not skip levels.
- All `<!-- BEGIN:name -->` markers have a matching `<!-- END:name -->`.
- No two headings produce the same GitHub anchor.
- No empty link targets (`[text]()`) or missing alt text (`![](url)`).
- File is within the 500 KB byte budget.
- No personal identifiers from the blocked list appear in the file.

---

## 6. Scenario walkthroughs

### Small library or CLI

Goal: a README that gets a new user from zero to working in under five minutes.

1. Keep: badge-row, package-manager-install, extended-example.
2. In **Usage**, show `pip install mylib` followed by a three-line Python snippet.
3. In **Configuration**, document only the most commonly changed option.
4. Remove contributing-link if no `CONTRIBUTING.md` exists yet.

### Application or service

Goal: a README that explains what the service does and how to run it locally.

1. Keep: badge-row, extended-example, contributing-link.
2. Remove: package-manager-install (replace with `docker run` or `docker compose up`).
3. Expand **Configuration** with a table of all environment variables.
4. Add a **Architecture** section after **Overview** if the service has
   multiple components.

### Infrastructure repository

Goal: a README that explains what the infrastructure manages and how to apply it.

1. Keep: badge-row, contributing-link.
2. Remove: package-manager-install, extended-example.
3. Replace **Usage** with a **Deployment** section describing `terraform apply`
   or equivalent.
4. Add a **Environments** section listing `dev`, `staging`, `prod` if applicable.

---

## 7. Heading hierarchy reference

```
# H1   — repository or project name (exactly one)
## H2  — top-level sections
### H3 — subsections
#### H4 — deep detail (use sparingly)
```

Skipping from H2 to H4 is a validation error.
