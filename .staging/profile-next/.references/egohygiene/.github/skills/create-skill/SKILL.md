---
name: create-skill
description: Scaffold a new VS Code Agent Skill for this repository following established conventions.
version: 1.0.0
status: active
---

# Create Skill

Scaffold a new VS Code Agent Skill under `.github/skills/` in this repository.

---

## Purpose

This skill encodes the complete workflow for creating a new repository skill — from naming and directory layout through frontmatter, body structure, and integration with existing repository documentation.

Use this skill whenever a new repeatable workflow should be made available to Copilot agents.

---

## When to Use

Use this skill when:

- A common engineering task is performed repeatedly and should be standardized.
- An agent needs a focused, composable workflow that does not warrant a full agent definition.
- Existing agents reference a workflow that should be extracted and reused independently.
- A specification or document describes a repeatable process that Copilot should be able to execute on demand.

Do not use this skill when:

- The guidance should always be in context for every Copilot interaction — use `.github/copilot-instructions.md` instead.
- The task requires autonomous, multi-step execution with complex decision-making — use an agent under `.github/agents/` instead.
- The workflow already exists as a skill — extend the existing `SKILL.md` instead of creating a duplicate.

---

## Steps

### 1. Determine the Skill Name

Choose a `kebab-case` name that describes what the skill does.

Rules:

- Names must be unique within `.github/skills/`.
- Names should be short verb or verb-phrase strings.
- Prefer specificity: `create-github-issue` is better than `create`.

### 2. Create the Skill Directory

Create a new subdirectory:

```text
.github/skills/<skill-name>/
```

### 3. Create SKILL.md

Create `.github/skills/<skill-name>/SKILL.md` with the required frontmatter:

```markdown
---
name: <skill-name>
description: <One sentence describing what this skill does, in imperative mood.>
version: 1.0.0
status: active
---

# <Skill Title>

<One-paragraph summary of what the skill does and when to use it.>

---

## Purpose

<Explain the problem this skill solves.>

---

## When to Use

<Describe the conditions that should trigger this skill. Include both positive and negative examples.>

---

## Steps

<Ordered, actionable instructions. Number each step. Use sub-steps for complex actions. Reference relevant specifications.>

---

## References

<Links to related specifications, agents, documentation, or source files.>

---

## Constraints

<List what the skill must not do.>
```

### 4. Write the Skill Body

Follow these writing guidelines:

- Use clear, imperative language throughout.
- Number steps and use sub-bullets for detail.
- Link to canonical documents instead of duplicating their content.
- Reference authoritative specifications under `.github/specs/` where they exist.
- Keep the skill narrowly focused on one workflow.
- Do not include repository-sensitive information or credentials.

### 5. Add Optional Resources

If the skill benefits from additional resources, create them alongside `SKILL.md`:

```text
.github/skills/<skill-name>/
    SKILL.md           ← required
    examples/          ← optional: concrete before/after examples
    templates/         ← optional: reusable output templates
    references/        ← optional: supporting reference material
    scripts/           ← optional: automation scripts
```

Only add resources that provide genuine value. Prefer links to existing documents.

### 6. Update the README

After creating the skill, add it to the directory layout table in `.github/skills/README.md`.

### 7. Validate the Skill

Confirm:

- [ ] The skill directory name matches the `name` frontmatter field.
- [ ] The frontmatter contains all required fields.
- [ ] The skill body includes Purpose, When to Use, Steps, References, and Constraints.
- [ ] No repository documentation is duplicated — links are used instead.
- [ ] The skill loads in the VS Code Agent Skills UI.

---

## References

- `.github/skills/README.md` — repository skill conventions
- `.github/agents/` — existing repository agents
- `.github/specs/` — authoritative specifications
- `AI_CONSTITUTION.md` — repository AI governance

---

## Constraints

- Do not duplicate guidance already maintained in specifications or documentation.
- Do not include credentials, secrets, or environment-specific configuration.
- Do not create a skill that replicates an existing skill — extend it instead.
- Keep skills portable across repository contributors and AI environments.
