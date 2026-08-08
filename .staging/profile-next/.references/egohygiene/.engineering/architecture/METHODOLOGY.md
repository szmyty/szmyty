🛠️ METHODOLOGY

The engineering methodology followed by Ego Hygiene.

---

Purpose

This document defines how Ego Hygiene is designed, evolved, and implemented.

It is not an implementation guide.

It is an engineering methodology.

The objective is to create systems that evolve through understanding rather than ad hoc development.

---

Core Philosophy

Software should emerge from understanding.

Not the other way around.

Prefer:

Understanding

↓

Structure

↓

Implementation

Instead of:

Idea

↓

Code

↓

Hope

---

The Engineering Loop

Development follows a continuous feedback loop.

Research

↓

Understanding

↓

Ontology

↓

Artifacts

↓

Schemas

↓

Specifications

↓

Agents

↓

Implementation

↓

Validation

↓

Reflection

↓

Research

Every implementation should improve understanding.

Every improvement in understanding should improve future implementations.

---

The Layers

1. Philosophy

Defines why the project exists.

Examples:

- Purpose
- Manifesto
- Principles
- Vision

---

2. Ontology

Defines the conceptual world.

The ontology answers:

"What exists?"

Examples:

- Domains
- Practices
- Reflections
- Insights
- Research

The ontology remains implementation-independent.

---

3. Artifact System

Artifacts define how concepts are represented.

Examples:

- Domains
- Practices
- Research
- Schemas
- Specifications
- Agents

Artifacts are reusable engineering building blocks.

---

4. Schemas

Schemas define structure.

Schemas are:

- implementation-independent
- language-independent
- versioned

Schemas describe:

"What something is."

---

5. Specifications

Specifications define behavior.

They describe:

- responsibilities
- lifecycle
- validation
- implementation expectations

Specifications answer:

"How should this behave?"

---

6. Agents

Agents execute work.

Agents should:

- follow specifications
- respect architecture
- avoid inventing structure
- implement rather than redesign

Agents consume context.

They do not define it.

---

7. Implementation

Implementation realizes the concepts defined by the layers above.

Technology should remain replaceable.

Examples include:

- Flutter
- Python
- Rust
- Web
- Infrastructure

Implementations are projections of the engineering model.

They are not the source of truth.

---

The Source of Truth

The repository intentionally separates concerns.

Philosophy

↓

Ontology

↓

Artifacts

↓

Schemas

↓

Specifications

↓

Implementation

Changes should generally flow downward.

Implementation should rarely redefine higher layers.

---

Context Engineering

AI systems perform best when supplied with rich, structured context.

Rather than relying on increasingly complex prompts, this methodology captures context through:

- philosophy
- ontology
- schemas
- specifications
- documentation
- repository structure

Prompt engineering becomes a thin layer on top of a much richer context model.

---

Continuous Evolution

Repositories are living systems.

Rather than generating a project once, this methodology assumes continuous refinement.

Observe

↓

Understand

↓

Improve

↓

Validate

↓

Repeat

Every iteration should increase coherence.

---

Framework Before Features

Reusable engineering should be identified before application-specific implementation.

Whenever possible:

Generic infrastructure belongs in the framework.

Application-specific behavior belongs in the product.

This allows future extraction into reusable foundations.

---

The 80/20 Principle

Aim for approximately:

- 80% reusable engineering
- 20% application-specific implementation

Examples of reusable infrastructure include:

- startup lifecycle
- authentication lifecycle
- permissions lifecycle
- notification lifecycle
- routing
- state management
- storage
- AI abstractions
- context assembly
- testing
- CI/CD
- release pipeline

Application-specific concepts should remain focused on the unique purpose of the repository.

---

Human + AI Collaboration

Humans provide:

- philosophy
- judgment
- ontology
- architectural direction

AI provides:

- implementation
- refinement
- generation
- repetition
- consistency

The objective is not replacing human reasoning.

The objective is amplifying it.

---

Success

The methodology succeeds when:

- understanding improves over time
- implementation becomes easier
- context is preserved
- repositories evolve intentionally
- architecture becomes increasingly reusable

Software is not the final product.

Understanding is.

