# 🧪 Flutter Testing Skill

---

# Purpose

This skill defines testing standards for Flutter applications built within the Ego Hygiene engineering ecosystem.

The goal is to provide confidence, maintainability, and rapid iteration without creating excessive testing burden.

Testing should support:

- safe refactoring
- architectural stability
- issue-driven development
- AI-assisted implementation
- long-term maintainability

---

# Core Philosophy

Testing should validate:

    Behavior

not:

    Implementation Details

The purpose of testing is to increase confidence.

The purpose is not to maximize test count.

---

# Testing Hierarchy

Preferred hierarchy:

    Unit Tests
        ↓
    Provider Tests
        ↓
    Widget Tests
        ↓
    Integration Tests
        ↓
    Golden Tests

Not every feature requires every layer.

---

# Unit Tests

Unit tests should validate:

- pure functions
- business logic
- utility functions
- data transformations

Unit tests should be:

- fast
- deterministic
- isolated

---

# Provider Tests

Provider tests are first-class citizens.

Examples:

- Riverpod providers
- Notifiers
- Derived state

Test:

- state transitions
- async behavior
- error handling
- dependency interactions

---

# Widget Tests

Widget tests should validate:

- rendering
- interaction
- state visibility

Avoid testing implementation details.

Focus on:

    User Observable Behavior

---

# Integration Tests

Use:

    integration_test

for end-to-end verification.

Examples:

- onboarding flow
- reflection flow
- authentication flow
- navigation flow

Integration tests should validate:

- feature behavior
- system interaction
- user journeys

---

# Golden Tests

Use:

    golden_toolkit

for visual verification.

Golden tests should focus on:

- reusable components
- critical screens
- theme consistency

Avoid excessive golden coverage.

---

# Mocking

Use:

    mocktail

for mocking dependencies.

Examples:

- AI providers
- storage providers
- notification providers
- sync providers

Mock capabilities.

Not vendors.

---

# Offline First Testing

Verify:

- no-network behavior
- degraded operation
- local storage recovery

Applications should remain functional when disconnected.

---

# AI Testing

AI provider tests should validate:

- provider behavior
- response handling
- fallback behavior
- error handling

Do not test vendor intelligence.

Test application behavior.

---

# Notification Testing

Verify:

- scheduling
- cancellation
- recurrence
- timezone handling

Notifications should be predictable.

---

# Localization Testing

Verify:

- locale switching
- fallback language behavior
- translation availability

Missing translations should be visible during development.

---

# Accessibility Testing

Validate:

- semantics
- labels
- keyboard navigation
- contrast assumptions

Accessibility should be testable.

---

# CI Integration

Testing should support:

- local execution
- GitHub Actions
- future release pipelines

Tests should remain deterministic.

Avoid flaky tests.

---

# Issue Driven Testing

Each issue should answer:

    What behavior changed?

Tests should validate that behavior.

Avoid creating tests solely for coverage metrics.

---

# Coverage Philosophy

Coverage is a signal.

Coverage is not a goal.

Prefer:

    meaningful tests

over:

    inflated coverage numbers

---

# Architectural Smells

Watch for:

- brittle tests
- implementation-driven tests
- excessive mocking
- flaky integration tests
- snapshot abuse

---

# Future Capability Inventory

Potential future additions:

    patrol

for advanced device-level testing.

Adopt only when justified.

---

# Final Rule

A good test increases confidence.

A bad test increases maintenance.

Prefer confidence.
