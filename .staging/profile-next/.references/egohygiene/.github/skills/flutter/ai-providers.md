# 🤖 Flutter AI Provider Skill

---

# Purpose

This skill defines how AI capabilities are integrated into Flutter applications within the Ego Hygiene ecosystem.

The goal is:

    Capability First
    ↓
    Provider Second
    ↓
    Vendor Last

Applications should depend on AI capabilities rather than specific AI vendors.

---

# Core Philosophy

Architect around:

    What AI Does

not:

    Which AI Vendor Does It

Capabilities should remain stable.

Providers should remain replaceable.

---

# Capability Architecture

Prefer:

    ChatProvider
    SummarizationProvider
    InsightProvider
    EmbeddingProvider

over:

    OpenAIProvider
    GeminiProvider
    OllamaProvider

at architectural boundaries.

---

# Provider Abstraction

Applications should define interfaces.

Examples:

    AIProvider
    ChatProvider
    InsightProvider

Implementations may include:

    OpenAI
    Gemini
    Ollama
    Local Models
    Future Providers

---

# Capability Categories

## Chat

Supports:

- reflection
- exploration
- brainstorming
- guided conversation

---

## Summarization

Supports:

- journal compression
- conversation summaries
- reflection synthesis

---

## Insight Generation

Supports:

- pattern detection
- trend identification
- reflective observations

---

## Embeddings

Supports:

- semantic search
- memory retrieval
- contextual recommendations

---

# Local First Philosophy

Prefer:

    Local Capability

before:

    Remote Capability

Examples:

- local summarization
- local embeddings
- local inference

Cloud AI should enhance functionality.

Cloud AI should not define functionality.

---

# Provider Hierarchy

Preferred hierarchy:

    Capability
        ↓
    Provider
        ↓
    Vendor

Example:

    SummarizationProvider
        ↓
    AIProvider
        ↓
    Gemini

---

# Supported Providers

Potential implementations:

    google_generative_ai
    dart_openai
    ollama_dart

Future providers may be added without changing domain logic.

---

# Context Management

AI systems should receive:

- scoped context
- relevant context
- minimal necessary context

Avoid:

- dumping entire databases
- unrestricted memory access
- excessive prompt inflation

---

# Reflection Philosophy

AI should support:

- reflection
- organization
- synthesis
- understanding

AI should not:

- replace judgment
- replace agency
- replace interpretation

Human understanding remains authoritative.

---

# Privacy Philosophy

Sensitive information should remain local whenever possible.

Before using cloud providers ask:

1. Is cloud inference necessary?
2. Can this run locally?
3. Does the user benefit from cloud processing?
4. Is privacy being preserved?

---

# Error Handling

AI failures should be explicit.

Avoid:

    silent fallback

Prefer:

    observable degradation

Examples:

- local model unavailable
- cloud provider unavailable
- quota exceeded

Users should understand what happened.

---

# Cost Awareness

Cloud AI should be treated as a scarce resource.

Architectures should:

- support local alternatives
- support provider switching
- support capability degradation

Avoid assuming unlimited API usage.

---

# Testing

Providers should be mockable.

Applications should be testable without:

- internet access
- cloud credentials
- external vendors

---

# Future Directions

Potential capabilities:

- memory systems
- reflective compression
- insight artifacts
- semantic navigation
- cognition graphs

These should build on provider abstractions rather than vendor APIs.

---

# Architectural Smells

Watch for:

- vendor lock-in
- provider-specific domain models
- AI logic inside widgets
- hardcoded API assumptions
- cloud-first architecture

---

# Final Rule

AI is a capability.

Vendors are implementations.

Architect around capabilities.
