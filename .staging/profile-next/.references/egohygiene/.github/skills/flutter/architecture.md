# 🏗️ Flutter Architecture Skill

---

# Purpose

This skill defines the architectural conventions used by Flutter applications within the Ego Hygiene ecosystem.

The goal is to create:

- maintainable systems
- reusable modules
- predictable structures
- AI-friendly repositories
- low cognitive overhead

Architecture should optimize for:

    Understanding
    ↓
    Reuse
    ↓
    Maintainability
    ↓
    Speed

---

# Core Philosophy

Applications should be:

- feature-first
- offline-first
- modular
- composable
- provider-driven
- testable

Avoid:

- monolithic architectures
- global mutable state
- tightly coupled modules
- vendor lock-in

---

# Layer Hierarchy

Applications should follow:

    Presentation
    ↓
    Providers
    ↓
    Domain
    ↓
    Data
    ↓
    Infrastructure

Dependencies should flow downward only.

---

# Feature-First Organization

Prefer:

    features/
      reflection/
      navigation/
      memory/
      progress/

over:

    screens/
    widgets/
    models/

Features represent business capabilities.

---

# Shared Architecture

Shared functionality belongs in:

    lib/shared/

Potential shared areas:

    shared/models/
    shared/providers/
    shared/services/
    shared/widgets/
    shared/extensions/
    shared/utils/

Shared code should remain domain-agnostic.

---

# Domain Models

Domain models are authoritative.

Prefer:

    Reflection
    Insight
    Memory
    Task
    Habit

over:

    ApiReflection
    ReflectionScreenModel
    ReflectionDatabaseObject

Infrastructure should adapt to domain models.

Domain models should not adapt to infrastructure.

---

# Provider Architecture

Use Riverpod as the primary architecture.

Providers should expose:

- state
- behavior
- dependencies

Providers should not contain:

- UI concerns
- navigation concerns
- widget logic

---

# Service Architecture

Services encapsulate capabilities.

Examples:

    AIService
    NotificationService
    StorageService
    SyncService

Services should expose interfaces.

Implementations should remain replaceable.

---

# Capability First Design

Architect around capabilities.

Avoid architecting around vendors.

Prefer:

    AIProvider

over:

    OpenAIProvider everywhere

Prefer:

    SyncProvider

over:

    FirebaseProvider everywhere

Capabilities are stable.

Vendors change.

---

# Offline First

Local functionality should be primary.

Cloud functionality should be secondary.

Applications should remain usable when:

- offline
- disconnected
- unauthenticated

whenever possible.

---

# Role-Based Experiences

Experiences may vary by role.

Examples:

    User
    Therapist
    Administrator

Shared domain models should remain consistent.

Only presentation and workflows should differ.

---

# Navigation Boundaries

Navigation should be:

- declarative
- centralized
- role aware

Avoid:

- scattered route definitions
- ad hoc navigation logic

---

# Design System Integration

UI should consume:

- design tokens
- theme definitions
- spacing standards

Avoid:

- hardcoded colors
- ad hoc styling
- duplicated UI patterns

---

# AI Integration

AI should be isolated behind abstractions.

Examples:

    SummarizationProvider
    ChatProvider
    InsightProvider

UI should never directly depend on:

    OpenAI
    Gemini
    Ollama

---

# Testing Boundaries

Architecture should support:

- unit testing
- widget testing
- integration testing

Code that cannot be tested easily is often poorly structured.

---

# Extension Strategy

New capabilities should be added by:

- creating features
- extending providers
- extending services

Avoid modifying stable foundations when possible.

Prefer:

    extension

over:

    replacement

---

# Architectural Smells

Watch for:

- duplicated business logic
- vendor-specific coupling
- global state abuse
- circular dependencies
- UI-driven architecture
- oversized providers

---

# Final Rule

Structure should reduce thinking.

A future contributor should be able to:

- find code quickly
- understand responsibilities quickly
- extend functionality safely

Good architecture reduces cognitive load.

That is the primary objective.
