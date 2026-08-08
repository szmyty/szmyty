# Domain Framework

## Metadata

- **Spec ID:** `domain-framework`
- **File Name:** `domain-framework.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #9
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-21

---

# 1. Purpose

Define the canonical structure for domains within Ego Hygiene.

Domains are the major areas of life that a person maintains over time. This specification establishes how domains are modeled, documented, and represented at both the knowledge and application layers.

---

# 2. Goals

- Define the canonical data model for a domain.
- Establish how domains are documented in `docs/domains/`.
- Define the relationship between domains, practices, and insights.
- Enable consistent domain representation across the application.
- Provide a stable foundation for feature development organized around domains.

---

# 3. Non-Goals

- This spec does not define individual domain content (e.g., Finance, Health).
- This spec does not implement domain-specific UI screens.
- This spec does not define practice logic or insight logic (see their respective specs).
- This spec does not define storage schema (see `offline-first-storage.spec.md`).

---

# 4. Context

Ego Hygiene is built around the idea that human life can be organized into broad, interconnected domains. These domains are not tasks or habits — they are the major systems that a person maintains over time.

Domains were introduced in `docs/domains/README.md` and `docs/domains/TEMPLATE.md`. The current state is documentation-only. This spec elevates domains to a first-class application concept with a defined model, structure, and boundary.

Examples of domains referenced in the documentation:
- Physical Health
- Mental Health
- Financial Health
- Relationships
- Purpose
- Creativity
- Environment

---

# 5. Requirements

## 5.1 Functional Requirements

- Each domain must have a unique identifier.
- Each domain must have a name and short description.
- Each domain must support association with one or more practices.
- Each domain must support association with one or more insights.
- Domains must be listable and browsable in the application.
- Domains must support a visual icon or symbol for identification.
- Domains must support a color or theme accent for visual distinction.
- Domain data must be stored locally and work offline.

## 5.2 Non-Functional Requirements

- Domain models must be immutable (use `freezed`).
- Domain identifiers must be stable across application versions.
- Domain documentation in `docs/domains/` must follow the existing `TEMPLATE.md` structure.
- Domain models must be serializable to and from JSON.
- Domains must be testable in isolation.

---

# 6. Architecture

## 6.1 Components

- **Domain Model** — Immutable data class representing a domain.
- **Domain Repository** — Interface for reading domain data.
- **Domain Provider** — Riverpod provider exposing domain state.
- **Domain Documentation** — Markdown files in `docs/domains/` per domain.
- **Domain Registry** — Static or seeded list of canonical domains.

## 6.2 Domain Model Structure

```
Domain
  id: String           — stable, kebab-case identifier (e.g., "physical-health")
  name: String         — display name (e.g., "Physical Health")
  description: String  — one-sentence purpose statement
  iconName: String     — icon identifier for UI rendering
  colorToken: String   — design token reference for accent color
  practiceIds: List<String>   — associated practice identifiers
  tags: List<String>   — optional classification tags
  createdAt: DateTime
  updatedAt: DateTime
```

## 6.3 Data Flow

```
Domain Registry (seeded data)
  ↓
Domain Repository (interface)
  ↓
Domain Provider (Riverpod)
  ↓
Domain UI (feature screens)
```

## 6.4 Feature Directory Structure

```
lib/features/domains/
  presentation/
    domain_list_screen.dart
    domain_detail_screen.dart
    widgets/
      domain_card.dart
  providers/
    domains_provider.dart
    domains_provider.g.dart
  domain/
    domain.dart
    domain.freezed.dart
    domain.g.dart
  data/
    domain_repository.dart
    domain_repository_impl.dart
```

## 6.5 Documentation Structure

```
docs/domains/
  README.md         — overview and purpose
  TEMPLATE.md       — canonical documentation template
  physical-health.md
  mental-health.md
  financial-health.md
  relationships.md
  purpose.md
  creativity.md
  environment.md
```

## 6.6 Dependencies

- `freezed` + `freezed_annotation` — immutable domain model
- `json_serializable` + `json_annotation` — serialization
- `flutter_riverpod` + `riverpod_annotation` — state management
- `drift` — local storage (see `offline-first-storage.spec.md`)

---

# 7. Implementation Plan

## Phase 1 — Model and Documentation

- [ ] Define `Domain` model using `freezed`.
- [ ] Add JSON serialization via `json_serializable`.
- [ ] Create `DomainRepository` interface.
- [ ] Seed initial domain list (at minimum: Physical Health, Mental Health, Financial Health, Relationships, Purpose).
- [ ] Create domain documentation files in `docs/domains/` following `TEMPLATE.md`.

## Phase 2 — Provider and State

- [ ] Create `domainsProvider` using Riverpod code generation.
- [ ] Create `domainByIdProvider` for individual domain lookup.
- [ ] Implement `DomainRepositoryImpl` backed by seeded local data.
- [ ] Wire repository into providers.

## Phase 3 — Feature UI

- [ ] Create `DomainListScreen`.
- [ ] Create `DomainDetailScreen`.
- [ ] Create `DomainCard` widget.
- [ ] Add domain routes to app router.

## Phase 4 — Validation

- [ ] Write unit tests for `Domain` model.
- [ ] Write unit tests for `DomainRepository`.
- [ ] Write widget tests for `DomainCard`.
- [ ] Validate offline behavior.

---

# 8. Validation Plan

- Unit tests for domain model serialization and deserialization.
- Unit tests for domain repository lookup and filtering.
- Widget tests for domain list and card rendering.
- Manual validation of domain documentation completeness.
- CI must pass all tests before merging.

---

# 9. Acceptance Criteria

- [ ] `Domain` model is defined with all required fields.
- [ ] At least five canonical domains are seeded.
- [ ] Domain documentation exists for each seeded domain.
- [ ] Domains are accessible via Riverpod providers.
- [ ] Domain list and detail screens render correctly.
- [ ] All unit and widget tests pass.
- [ ] Domains work fully offline.
- [ ] No application code is written outside the `domains` feature boundary.

---

# 10. Open Questions

- Should domains be fully static (seeded at build time) or user-configurable (stored in database)?
- Should users be able to create custom domains in a later phase?
- How are domain-to-practice relationships maintained — by the domain, the practice, or a join model?
- Should domains support an ordering or priority concept?
