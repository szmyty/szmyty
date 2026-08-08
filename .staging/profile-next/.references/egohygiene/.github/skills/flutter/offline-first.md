# 📴 Flutter Offline-First Skill

---

# Purpose

This skill defines the offline-first architecture philosophy used within Ego Hygiene applications.

The goal is:

    Local First
    ↓
    Cloud Optional

Applications should remain useful, functional, and trustworthy even when no network connection is available.

Offline-first is considered a core product feature.

---

# Core Philosophy

Assume:

    no network

before assuming:

    network available

Network access should enhance functionality.

Network access should not be required for core functionality.

---

# Why Offline First

Benefits:

- reliability
- privacy
- lower latency
- user ownership
- reduced infrastructure dependency
- reduced operating costs

Offline-first supports:

- personal cognition systems
- journaling
- reflection
- habits
- memory systems
- AI-assisted workflows

---

# Local Source of Truth

The local device is authoritative.

Applications should:

- read locally first
- write locally first

Synchronization should occur afterward.

---

# Storage Hierarchy

Preferred hierarchy:

    Memory
        ↓
    Local Database
        ↓
    Optional Cloud Sync

Cloud services should not become the primary source of truth.

---

# Synchronization Philosophy

Synchronization is:

    capability

not:

    dependency

Examples:

    Local Only
    Google Drive Sync
    Firebase Sync
    Supabase Sync
    Self Hosted Sync

All should be replaceable.

---

# Provider Architecture

Applications should expose:

    SyncProvider

not:

    FirebaseProvider

at the domain level.

Implementations remain replaceable.

---

# AI Philosophy

AI should follow the same pattern.

Prefer:

    AIProvider

rather than:

    OpenAIProvider

at architectural boundaries.

Potential implementations:

    Ollama
    Gemini
    OpenAI
    Local Models

---

# Graceful Degradation

Applications should remain usable when:

- offline
- unauthenticated
- disconnected from cloud services

Features should degrade gracefully.

Avoid:

    hard failure

when remote services are unavailable.

---

# Local AI

Whenever possible:

- perform inference locally
- perform summarization locally
- preserve privacy

Cloud AI should be optional.

Not required.

---

# Sync Strategy

Synchronization should be:

- explicit
- observable
- recoverable

Users should understand:

- what is synced
- where it is stored
- whether synchronization succeeded

---

# Conflict Resolution

Prefer:

    local preservation

over:

    destructive overwrite

When conflicts occur:

- preserve user data
- surface ambiguity
- require explicit resolution

---

# Privacy Philosophy

Users should own their data.

Applications should:

- store data locally by default
- encrypt sensitive information
- minimize cloud dependency

---

# Security Integration

Use:

    flutter_secure_storage

for secrets.

Use encrypted storage when appropriate.

Never assume cloud providers are the only security boundary.

---

# Notifications

Notifications should function locally whenever possible.

Avoid architectures that require:

    cloud notification infrastructure

for basic reminder functionality.

---

# Feature Evaluation Framework

Before introducing a dependency ask:

1. Can this work offline?
2. Can local storage support this?
3. Can synchronization be optional?
4. Can the capability be abstracted?

If the answer is yes:

    prefer local-first design.

---

# Architectural Smells

Watch for:

- cloud-first assumptions
- vendor lock-in
- online-only workflows
- hidden synchronization
- remote-only AI

---

# Long-Term Vision

The ideal architecture:

    Fully Functional Offline

    ↓

    Enhanced By Cloud

rather than:

    Cloud Required

    ↓

    Local Cache

---

# Final Rule

The application should remain valuable on an airplane.

If the internet disappears:

    the product should still work.
