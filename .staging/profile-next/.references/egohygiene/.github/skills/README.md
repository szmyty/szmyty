# Repository Agent Skills

This directory contains VS Code Agent Skills for the Ego Hygiene repository.

Skills are reusable, composable workflows that GitHub Copilot can discover, load, and execute automatically. They encode common engineering tasks so that Copilot agents can perform them consistently without repeating the same instructions in every prompt.

---

## Directory Layout

```text
.github/
    skills/
        README.md              ← this file

        create-skill/
            SKILL.md           ← how to create a new skill

        flutter-engineer/
            SKILL.md           ← Flutter implementation workflows

        github-issue/
            SKILL.md           ← GitHub issue authoring workflows

        repository-audit/
            SKILL.md           ← repository audit workflows
```

Each skill lives in its own subdirectory. Only `SKILL.md` is required. Additional resources may be added alongside it when justified:

```text
skill-name/
    SKILL.md          ← required
    examples/         ← optional: concrete examples
    templates/        ← optional: reusable output templates
    references/       ← optional: supporting reference material
    scripts/          ← optional: automation scripts
```

---

## Relationship to Other AI Artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Agents | `.github/agents/` | Autonomous, long-running task executors |
| Skills | `.github/skills/` | Reusable, composable task workflows |
| Specifications | `.github/specs/` | Authoritative contracts for agents and skills |
| Flutter skills | `.github/skills/flutter/` | Reference material for Flutter conventions |
| Instructions | `.github/copilot-instructions.md` | Always-on repository instructions |

**Use a Skill when:**

- The workflow is repeatable and well-defined.
- The task is narrowly scoped and composable.
- You want Copilot to follow the same steps consistently.

**Use an Agent when:**

- The task requires autonomous, multi-step execution.
- The agent needs to read specifications and maintain a defined identity.
- The task involves complex decision-making across the repository.

**Use custom instructions when:**

- The guidance applies globally to all Copilot interactions.
- The convention should always be in context, not invoked on demand.

---

## Naming Conventions

- Use `kebab-case` for skill directory names and the `name` frontmatter field.
- Names should be short, descriptive verbs or verb phrases.
- Names must be unique within this directory.
- Prefer specificity over brevity: `create-skill` is better than `create`.

Examples: `create-skill`, `flutter-engineer`, `github-issue`, `repository-audit`.

---

## SKILL.md Frontmatter

Every `SKILL.md` must begin with YAML frontmatter:

```yaml
---
name: skill-name
description: One sentence describing what this skill does.
version: 1.0.0
status: active | draft | deprecated
---
```

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | `kebab-case`, matches directory name |
| `description` | Yes | One sentence, imperative mood |
| `version` | Yes | Semantic version, start at `1.0.0` |
| `status` | Yes | `active`, `draft`, or `deprecated` |

---

## SKILL.md Body

After the frontmatter, the skill body should describe:

1. **Purpose** — what problem the skill solves.
2. **When to use** — clear trigger conditions.
3. **Steps** — ordered, actionable instructions.
4. **References** — links to specifications, agents, or documentation.
5. **Constraints** — what the skill must not do.

Write in clear, imperative language. Prefer links to canonical documents over duplicating their content.

---

## Versioning

- Start every new skill at `1.0.0`.
- Increment the patch version for minor corrections.
- Increment the minor version for new steps or expanded coverage.
- Increment the major version for breaking changes to the skill's contract.

---

## Creating a New Skill

Use the `create-skill` skill to scaffold a new skill for this repository.

Manual steps:

1. Create a new subdirectory under `.github/skills/` using `kebab-case`.
2. Create `SKILL.md` with the required frontmatter and body.
3. Follow the conventions documented in this file.
4. Reference relevant specifications under `.github/specs/`.
5. Avoid duplicating guidance that already exists in other documents.

---

## References

- `.github/agents/` — repository agents
- `.github/specs/` — authoritative specifications
- `AI_CONSTITUTION.md` — repository AI governance
- `ARCHITECTURE.md` — architectural conventions
