# 🧭 Flutter Routing Skill

---

# Purpose

This skill defines how navigation and routing are implemented within Flutter applications built using the Ego Hygiene engineering ecosystem.

The goal is to create:

- predictable navigation
- deep-link friendly experiences
- role-aware interfaces
- scalable route organization
- cognition-friendly user flows

Navigation should help users understand:

    Where Am I?

    Where Can I Go?

    How Do I Get Back?

---

# Primary Standard

Use:

    go_router

as the primary routing solution.

All navigation should be centralized.

Avoid scattered route definitions.

---

# Core Philosophy

Navigation is not merely screen switching.

Navigation is:

    Context Management

Users should always understand:

- current location
- available actions
- surrounding context

---

# Route Organization

Routes should be grouped by feature.

Prefer:

    features/
      reflection/
      navigation/
      memory/
      progress/

over:

    pages/
    routes/

Route ownership should remain close to feature ownership.

---

# Route Hierarchy

Prefer:

    App
        ↓
    Domain
        ↓
    Feature
        ↓
    Detail

Examples:

    /
    /reflection
    /reflection/entry
    /memory
    /memory/insight

---

# Deep Linking

All major screens should support deep linking.

Deep links should:

- restore context
- preserve navigation state
- remain shareable

Avoid route structures that cannot be reconstructed.

---

# Role-Aware Navigation

Navigation may vary by role.

Examples:

    User
    Therapist
    Administrator

Role differences should primarily affect:

- visibility
- navigation options
- workflow access

Avoid duplicating route trees unnecessarily.

---

# Navigation Boundaries

Routes should not contain business logic.

Routes should:

- declare destinations
- define navigation structure
- coordinate context transitions

Business logic belongs elsewhere.

---

# Shell Navigation

Use shell routes when appropriate.

Examples:

- bottom navigation
- tab navigation
- persistent layouts

Avoid rebuilding major navigation structures unnecessarily.

---

# Mobile Philosophy

Mobile navigation should prioritize:

- simplicity
- thumb reachability
- low cognitive overhead

Users should rarely feel lost.

---

# Web Philosophy

Web navigation should prioritize:

- discoverability
- deep linking
- browser compatibility

URLs should remain meaningful.

---

# Desktop Philosophy

Desktop navigation should support:

- larger information density
- contextual sidebars
- expanded workflows

Desktop experiences may expose additional context.

---

# Cognitive Navigation

Long-term, navigation may represent:

- domains
- memories
- insights
- projects
- relationships

Navigation should support exploration without creating confusion.

The user should feel:

    guided

rather than:

    constrained

---

# Information Architecture

Navigation should emerge from domains.

Do not create navigation structures first.

Instead:

    Domain
        ↓
    Experience
        ↓
    Navigation

---

# Transition Philosophy

Transitions should:

- preserve orientation
- communicate movement
- reduce confusion

Avoid:

- flashy transitions
- unnecessary animation

Motion should support cognition.

---

# Error Handling

Invalid routes should:

- fail gracefully
- provide recovery options
- preserve user context when possible

Avoid dead ends.

---

# Testing

Navigation should be testable.

Test:

- route access
- role-based visibility
- deep linking
- redirects
- error handling

---

# Architectural Smells

Watch for:

- route duplication
- feature leakage
- navigation-driven business logic
- hidden redirects
- inconsistent route naming

---

# Future Vision

Navigation may eventually become:

    Cognitive Navigation

where users navigate:

- domains
- memories
- insights
- reflections

rather than simply screens.

Routing architecture should remain flexible enough to support this evolution.

---

# Final Rule

Navigation should reduce uncertainty.

If users are confused about where they are:

    navigation has failed.
