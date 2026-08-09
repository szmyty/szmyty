<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 1. HERO                                                                     -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

<div align="center">

<!-- Banner: replace banner-light.svg / banner-dark.svg with final ChatGPT-generated artwork.
     Critical identity text is preserved as Markdown below so it remains readable
     even when the images do not load. See assets/profile/ASSET-BRIEF.md. -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="assets/profile/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/profile/banner-light.svg">
  <img src="assets/profile/banner-light.svg"
       alt="Alan Szmyt — Software Engineer, Systems Architect, Creative Technologist"
       width="100%">
</picture>

# Alan Szmyt

**Software Engineer · Systems Architect · Creative Technologist**

[![GitHub](https://img.shields.io/badge/GitHub-szmyty-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/szmyty)

</div>

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 2. THIRTY-SECOND BRIEF                                                      -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Brief

I build **cloud-native platforms**, **developer experience tooling**, and
**AI-assisted workflows** with a strong emphasis on privacy, automation, and
long-term maintainability.

I think in systems. I care about the experience of building as much as the
experience of using. I value automation that removes friction rather than adding
ceremony, and documentation that reveals architecture rather than restating code.

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 3. PROOF AT A GLANCE                                                        -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Proof at a Glance

| Claim | Evidence ID | Public Artifact |
|-------|-------------|-----------------|
| Software engineer | `identity-role-software-engineer` | [github.com/szmyty](https://github.com/szmyty) |
| Open-source systems builder | `repo-soliloquy` · `repo-universal` · `repo-openai-retro` | [szmyty repositories](https://github.com/szmyty?tab=repositories) |
| Ego Hygiene organisation contributor | `repo-egohygiene-org` · `oss-egolint-pr` | [github.com/egohygiene](https://github.com/egohygiene) |
| Local-LLM tooling (soliloquy) | `repo-soliloquy` | [szmyty/soliloquy](https://github.com/szmyty/soliloquy) |
| Monorepo DX tooling (universal) | `repo-universal` | [szmyty/universal](https://github.com/szmyty/universal) |
| AI game agent (NEAT / gym-retro) | `repo-openai-retro` | [OpenAI-Retro-SuperMarioWorld-SNES](https://github.com/szmyty/OpenAI-Retro-SuperMarioWorld-SNES) |
| Shared linting contribution | `repo-egolint` · `oss-egolint-pr` | [egohygiene/egolint](https://github.com/egohygiene/egolint) |
| Evidence catalog | `repo-szmyty-szmyty` | [profile/content/evidence.yml](profile/content/evidence.yml) |

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 4. SELECTED IMPACT                                                          -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Selected Impact

> Each entry below is backed by an inspectable public artifact.
> Evidence IDs reference [profile/content/evidence.yml](profile/content/evidence.yml).

| Area | Context · Ownership · Outcome | Evidence |
|------|-------------------------------|----------|
| **Offline-first LLM chat** | Without a budget for cloud API calls or a willingness to send private documents to third-party servers, designed and built [soliloquy](https://github.com/szmyty/soliloquy) — a single Docker Compose stack that routes PDF queries through a locally running LLM. Outcome: a reproducible, zero-cloud-dependency workflow that any developer can run with one command. | `repo-soliloquy` · [github.com/szmyty/soliloquy](https://github.com/szmyty/soliloquy) |
| **Monorepo developer experience** | Across multiple projects with inconsistent formatting, linting, and CI conventions, authored [universal](https://github.com/szmyty/universal) — a composable shell toolkit that consolidates formatting, linting, spellcheck, and CI scaffolding. Outcome: a single source of DX conventions that can be layered into any repository without bespoke setup. | `repo-universal` · [github.com/szmyty/universal](https://github.com/szmyty/universal) |
| **Reinforcement-learning experiment** | To understand emergent agent behaviour from raw game-state input, trained a NEAT recurrent neural network to navigate SNES Super Mario World levels using gym-retro. Outcome: a publicly documented experiment showing the training loop, configuration, and results in a reproducible form. | `repo-openai-retro` · [github.com/szmyty/OpenAI-Retro-SuperMarioWorld-SNES](https://github.com/szmyty/OpenAI-Retro-SuperMarioWorld-SNES) |
| **Shared linting infrastructure** | To reduce lint-rule drift across repositories in the Ego Hygiene organisation, contributed and merged the initial opinionated rule set in [egolint](https://github.com/egohygiene/egolint). Outcome: a shared linting baseline that any organisation repository can inherit, reducing per-repo configuration overhead. | `repo-egolint` · `oss-egolint-pr` · [egohygiene/egolint#1](https://github.com/egohygiene/egolint/pull/1) |

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 5. FEATURED SYSTEMS                                                         -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Featured Systems

### [soliloquy](https://github.com/szmyty/soliloquy)

Privately chat with and summarize PDFs using a fully local LLM. No data leaves
your machine. Packaged as a single Docker Compose stack.

**Stack:** Python · Docker · Ollama

---

### [universal](https://github.com/szmyty/universal)

All-in-one monorepo DX: formatting, linting, spellcheck, and CI-ready
automation in a single composable shell toolkit.

**Stack:** Shell · GitHub Actions

---

### [OpenAI-Retro-SuperMarioWorld-SNES](https://github.com/szmyty/OpenAI-Retro-SuperMarioWorld-SNES)

NEAT-Python recurrent neural network that trains an AI agent to complete levels
in Super Mario World on SNES via gym-retro.

**Stack:** Python · NEAT · OpenAI Gym Retro

---

### [egohygiene](https://github.com/egohygiene/egohygiene)

Core application and knowledge system within the Ego Hygiene organisation.

**Stack:** Dart · Flutter · TypeScript · Python · GitHub Actions

---

### [szmyty/szmyty](https://github.com/szmyty/szmyty)

This profile repository — schema-validated evidence catalog, automated
validation tooling, and the structured README you are reading.

**Stack:** Python · YAML · GitHub Actions · Markdown

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 6. EGO HYGIENE ECOSYSTEM                                                    -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Ego Hygiene Ecosystem

[Ego Hygiene](https://github.com/egohygiene) is an interconnected developer
platform — not a collection of unrelated repositories.

| Repository | Role |
|------------|------|
| [egohygiene](https://github.com/egohygiene/egohygiene) | Core application and knowledge system |
| [mantle](https://github.com/egohygiene/mantle) | Shared infrastructure and conventions |
| [egolint](https://github.com/egohygiene/egolint) | Opinionated linting rules for the ecosystem |

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 7. ENGINEERING CAPABILITIES                                                 -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Engineering Capabilities

| Domain | Skills | Representative artifact |
|--------|--------|------------------------|
| **Languages** | Python · TypeScript · Dart · Java · Bash · SQL | [szmyty repos](https://github.com/szmyty?tab=repositories) |
| **Platforms** | Flutter · Docker · Linux · Android · Node.js | [soliloquy](https://github.com/szmyty/soliloquy) |
| **Data** | SQLite · PostgreSQL · Drift ORM | [egohygiene](https://github.com/egohygiene/egohygiene) |
| **CI/CD & automation** | GitHub Actions · Task · Poetry · FVM | [universal](https://github.com/szmyty/universal) |
| **AI / ML** | Local LLM integration · NEAT · gym-retro | [OpenAI-Retro-SuperMarioWorld-SNES](https://github.com/szmyty/OpenAI-Retro-SuperMarioWorld-SNES) |
| **DX practices** | Specification-driven development · Architecture-first design · Conventional Commits | [szmyty/szmyty](https://github.com/szmyty/szmyty) |

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 8. EXPERIENCE AND EDUCATION                                                 -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Experience and Education

Employment history is held under a confidentiality policy and is not published
here. The public record of applied skills is the open-source portfolio above.

Education details will be added when a verified public artifact exists.

> See [profile/content/evidence.yml](profile/content/evidence.yml) for the
> complete evidence catalog and verification status of each claim.

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 9. OPEN SOURCE AND COLLABORATION                                            -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Open Source and Collaboration

- Personal repositories and experiments: [github.com/szmyty](https://github.com/szmyty)
  — [evidence: `identity-github-username`]
- Ego Hygiene organisation: [github.com/egohygiene](https://github.com/egohygiene)
  — publicly accessible multi-repository developer platform [evidence: `repo-egohygiene-org`]
- Merged PR in egolint establishing shared lint conventions:
  [egohygiene/egolint#1](https://github.com/egohygiene/egolint/pull/1)
  — inspectable contribution history [evidence: `oss-egolint-pr`]

Contributions, issues, and discussions welcome. See open issues in this
repository at [szmyty/szmyty/issues](https://github.com/szmyty/szmyty/issues).

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 10. CREATIVE PRACTICE                                                       -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Creative Practice

Music production, sound design, and generative audio are a continuous thread
through my work. Creative technology — the intersection of code, sound, and
interactive media — is not separate from my engineering practice; it informs it.

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 11. CURRENT FOCUS                                                           -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Current Focus

| Stream | Description |
|--------|-------------|
| **AI tooling and agents** | Production-grade agent workflows: structured prompting, tool orchestration, and multi-agent coordination |
| **Developer experience** | Composable monorepo scaffolds, shared linting, and CI automation foundations |
| **Offline-first systems** | Local LLM integrations and privacy-preserving data patterns |
| **Knowledge systems** | Structured approaches to personal knowledge management and continuous learning |

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 12. CONTACT                                                                 -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

## Contact

| Channel | Address |
|---------|---------|
| **GitHub** | [@szmyty](https://github.com/szmyty) |
| **Organisation** | [github.com/egohygiene](https://github.com/egohygiene) |

---

<!-- ════════════════════════════════════════════════════════════════════════════ -->
<!-- 13. GENERATED REGIONS (reserved — not required for static profile)          -->
<!-- ════════════════════════════════════════════════════════════════════════════ -->

<!-- GENERATED:ACTIVITY:START -->
<!-- GENERATED:ACTIVITY:END -->

<!-- GENERATED:METRICS:START -->
<!-- GENERATED:METRICS:END -->

<!-- GENERATED:MUSIC:START -->
<!-- GENERATED:MUSIC:END -->

---

<div align="center">
<sub>Profile composed per the evidence-first engineering standard defined in
<a href="https://github.com/szmyty/szmyty/issues/65">szmyty/szmyty#65</a>.
Evidence catalog: <a href="profile/content/evidence.yml">profile/content/evidence.yml</a>.</sub>
</div>
