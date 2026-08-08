# 🧠 Flutter State Management Skill

---

# Purpose

This skill defines how state is managed within Flutter applications built using the Ego Hygiene engineering system.

The primary objective is:

    predictable state
    ↓
    composable state
    ↓
    maintainable state

while minimizing architectural complexity.

---

# Primary Standard

Use:

    flutter_riverpod

as the default state management framework.

Supporting packages:

    riverpod_annotation
    riverpod_generator

Riverpod is the preferred solution for:

- dependency injection
- application state
- async state
- service registration
- provider composition

---

# Core Philosophy

State should be:

- explicit
- observable
- testable
- composable

Avoid:

- hidden state
- global mutable state
- widget-owned business logic

---

# Provider Hierarchy

Preferred hierarchy:

    App Providers
        ↓
    Feature Providers
        ↓
    Domain Providers
        ↓
    Infrastructure Providers

Dependencies should flow downward.

---

# Provider Responsibilities

Providers should:

- expose state
- expose behavior
- expose dependencies

Providers should NOT:

- contain UI code
- contain widget rendering logic
- contain styling concerns

---

# State Categories

## Application State

Examples:

    Theme
    Authentication
    Settings
    Localization

Long-lived.

---

## Feature State

Examples:

    Reflection Session
    Insight Generation
    Task Editing

Scoped to a feature.

---

## Transient UI State

Examples:

    Selected Tab
    Expanded Card

Keep local when possible.

Do not elevate unnecessarily.

---

# Async State

Use:

    AsyncValue<T>

for async operations.

Examples:

- AI requests
- storage operations
- synchronization
- network calls

Prefer explicit loading and error states.

---

# Provider Naming

Prefer:

    reflectionProvider
    aiProvider
    memoryProvider

Avoid:

    reflectionManager
    reflectionServiceProviderProvider

Names should remain concise.

---

# Notifiers

Use notifiers for behavior.

Examples:

    ReflectionNotifier
    InsightNotifier

Notifiers should:

- mutate state
- coordinate workflows
- call services

Notifiers should not contain UI concerns.

---

# Service Injection

Inject services via providers.

Example:

    AIService
    StorageService
    NotificationService

Never instantiate services directly inside widgets.

---

# State Persistence

Default persistence should be:

- Drift
- Local Storage
- Secure Storage

Persistence should occur through services.

Not directly inside providers.

---

# Offline First

State should assume:

    local availability

before:

    remote availability

Providers should degrade gracefully when offline.

---

# Error Handling

Expose errors through state.

Avoid:

- swallowed exceptions
- hidden failures

Prefer:

    explicit error states

that can be surfaced to users.

---

# Derived State

Prefer computed providers.

Examples:

    filteredTasksProvider
    activeInsightsProvider
    progressSummaryProvider

Avoid duplicating state unnecessarily.

---

# Testing

Providers should be testable independently.

Prefer:

- provider tests
- notifier tests

before widget tests.

---

# Architectural Smells

Watch for:

- business logic in widgets
- oversized providers
- duplicated state
- provider chains that are difficult to follow
- unnecessary global state

---

# Role-Based State

Role differences should affect:

- visibility
- workflows
- presentation

Role differences should not duplicate domain state.

---

# AI Integration

AI should be accessed through providers.

Examples:

    chatProvider
    summarizationProvider
    insightProvider

Providers should depend on abstractions rather than vendors.

---

# Final Rule

State should answer:

    What is true?

Behavior should answer:

    What can happen?

Keep these responsibilities separate whenever possible.
