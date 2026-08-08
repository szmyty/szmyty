# Practice Framework

## Metadata

- **Spec ID:** `practice-framework`
- **File Name:** `practice-framework.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #9
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-21

---

# 1. Purpose

Define how practices are structured, documented, implemented, and connected to domains.

Practices are the active layer of Ego Hygiene. Where domains describe areas of life, practices describe what a person actually does. This specification establishes the canonical model for practices and their role in the application.

---

# 2. Goals

- Define the canonical data model for a practice.
- Establish how practices are documented in `docs/practices/`.
- Define the relationship between practices and domains.
- Define how practices support scheduling and reminders.
- Enable consistent practice representation across the application.

---

# 3. Non-Goals

- This spec does not define individual practice content (e.g., specific journaling workflows).
- This spec does not define insight generation (see `insight-framework.spec.md`).
- This spec does not define storage schema (see `offline-first-storage.spec.md`).
- This spec does not define notification scheduling in full detail (see notification infrastructure).

---

# 4. Context

Practices are introduced in `docs/practices/README.md` as the bridge between philosophy and behavior. The concept is:

```
Awareness
  ↓
Action
  ↓
Integration
```

Examples of practices referenced in the documentation:
- Gratitude
- Abundance
- Mindfulness
- Reflection
- Journaling
- Breathwork
- Budget Review

Currently practices exist only as documentation concepts. This spec elevates them to a first-class application model with defined structure, lifecycle, and integration with domains.

---

# 5. Requirements

## 5.1 Functional Requirements

- Each practice must have a unique identifier.
- Each practice must have a name, description, and instructions.
- Each practice must be associated with one or more domains.
- Each practice must support a configurable frequency (e.g., daily, weekly, as-needed).
- Each practice must support a duration estimate.
- Practices must be completable — users must be able to log a practice completion.
- Practice completions must be stored locally with a timestamp.
- Practices must be browsable and filterable by domain.
- Practices must support optional reminder scheduling.
- Practice completion history must be queryable.

## 5.2 Non-Functional Requirements

- Practice models must be immutable (use `freezed`).
- Practice identifiers must be stable across application versions.
- Practice models must be serializable to and from JSON.
- Practice completion records must be stored in a local database.
- Practices must be testable in isolation.

---

# 6. Architecture

## 6.1 Components

- **Practice Model** — Immutable data class representing a practice definition.
- **PracticeCompletion Model** — Record of a completed practice session.
- **Practice Repository** — Interface for reading and writing practice data.
- **Practice Provider** — Riverpod providers for practice state.
- **Practice Documentation** — Markdown files in `docs/practices/` per practice.

## 6.2 Practice Model Structure

```
Practice
  id: String              — stable, kebab-case identifier (e.g., "gratitude-journaling")
  name: String            — display name
  description: String     — purpose statement
  instructions: String    — how to perform the practice
  domainIds: List<String> — associated domain identifiers
  frequency: PracticeFrequency  — daily | weekly | monthly | as-needed
  durationMinutes: int    — estimated duration
  iconName: String        — icon identifier
  tags: List<String>
  createdAt: DateTime
  updatedAt: DateTime

PracticeFrequency
  daily
  weekly
  monthly
  asNeeded

PracticeCompletion
  id: String
  practiceId: String
  completedAt: DateTime
  durationMinutes: int?   — actual duration (optional)
  notes: String?          — optional reflection notes
  mood: MoodRating?       — optional mood capture
```

## 6.3 Data Flow

```
Practice Registry (seeded data)
  ↓
Practice Repository (interface)
  ↓
Practice Provider (Riverpod)
  ↓
Practice UI (feature screens)
  ↓
PracticeCompletion Repository (local DB)
  ↓
Completion History UI
```

## 6.4 Feature Directory Structure

```
lib/features/practices/
  presentation/
    practice_list_screen.dart
    practice_detail_screen.dart
    practice_session_screen.dart
    widgets/
      practice_card.dart
      practice_completion_tile.dart
  providers/
    practices_provider.dart
    practices_provider.g.dart
    practice_completions_provider.dart
    practice_completions_provider.g.dart
  domain/
    practice.dart
    practice.freezed.dart
    practice.g.dart
    practice_completion.dart
    practice_completion.freezed.dart
    practice_completion.g.dart
    practice_frequency.dart
  data/
    practice_repository.dart
    practice_repository_impl.dart
    practice_completion_repository.dart
    practice_completion_repository_impl.dart
```

## 6.5 Documentation Structure

```
docs/practices/
  README.md
  TEMPLATE.md
  gratitude.md
  mindfulness.md
  journaling.md
  breathwork.md
  reflection.md
```

## 6.6 Dependencies

- `freezed` + `freezed_annotation` — immutable models
- `json_serializable` + `json_annotation` — serialization
- `flutter_riverpod` + `riverpod_annotation` — state management
- `drift` — local storage for completions
- `flutter_local_notifications` — optional reminder support

---

# 7. Implementation Plan

## Phase 1 — Model and Documentation

- [ ] Define `Practice` model using `freezed`.
- [ ] Define `PracticeCompletion` model using `freezed`.
- [ ] Define `PracticeFrequency` enum.
- [ ] Create `PracticeRepository` and `PracticeCompletionRepository` interfaces.
- [ ] Seed initial practice list.
- [ ] Create practice documentation files in `docs/practices/`.

## Phase 2 — Provider and State

- [ ] Create `practicesProvider` using Riverpod code generation.
- [ ] Create `practiceByIdProvider`.
- [ ] Create `practiceCompletionsProvider`.
- [ ] Implement `PracticeRepositoryImpl` backed by seeded local data.
- [ ] Implement `PracticeCompletionRepositoryImpl` backed by local database.

## Phase 3 — Feature UI

- [ ] Create `PracticeListScreen`.
- [ ] Create `PracticeDetailScreen`.
- [ ] Create `PracticeSessionScreen`.
- [ ] Create `PracticeCard` widget.
- [ ] Create `PracticeCompletionTile` widget.
- [ ] Add practice routes to app router.

## Phase 4 — Validation

- [ ] Write unit tests for `Practice` model.
- [ ] Write unit tests for `PracticeCompletion` model.
- [ ] Write unit tests for `PracticeRepository`.
- [ ] Write widget tests for `PracticeCard`.
- [ ] Validate offline completion logging.

---

# 8. Validation Plan

- Unit tests for model serialization and deserialization.
- Unit tests for repository operations.
- Widget tests for practice list and card rendering.
- Integration tests for completing a practice and verifying storage.
- CI must pass all tests before merging.

---

# 9. Acceptance Criteria

- [ ] `Practice` model is defined with all required fields.
- [ ] `PracticeCompletion` model is defined with all required fields.
- [ ] At least five canonical practices are seeded.
- [ ] Practice documentation exists for each seeded practice.
- [ ] Practices are filterable by domain.
- [ ] Practice completions are stored and retrievable locally.
- [ ] All unit and widget tests pass.
- [ ] Practices work fully offline.

---

# 10. Open Questions

- Should practices support multi-step workflows (e.g., guided breathwork sequences)?
- Should users be able to create custom practices?
- How should mood ratings be modeled — simple scale or structured enum?
- Should practice completion streaks be calculated at the provider layer or repository layer?
- Should reminder scheduling be in scope for the initial implementation phase?
