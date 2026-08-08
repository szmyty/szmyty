# Insight Framework

## Metadata

- **Spec ID:** `insight-framework`
- **File Name:** `insight-framework.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #9
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-21

---

# 1. Purpose

Define how observations, patterns, and insights are represented throughout the system.

Insights are a core output of Ego Hygiene. The system exists to help people develop self-awareness — and insights are the artifacts that capture and preserve that awareness. This specification defines what an insight is, how it is created, stored, and surfaced.

---

# 2. Goals

- Define the canonical data model for an insight.
- Distinguish between observations, patterns, and insights.
- Define how insights are generated (manually, from practice completions, from AI).
- Define how insights relate to domains and practices.
- Establish a local-first insight storage model.
- Define how insights are surfaced in the application.

---

# 3. Non-Goals

- This spec does not define AI backend integration in detail (see AI provider abstraction in `flutter-engineer.spec.md`).
- This spec does not define the practice completion model (see `practice-framework.spec.md`).
- This spec does not define storage schema in full detail (see `offline-first-storage.spec.md`).
- This spec does not define notification delivery for insight surfacing.

---

# 4. Context

Ego Hygiene emphasizes understanding over optimization. Insights are the mechanism that makes that understanding visible and persistent.

The system must support three types of cognitive artifacts:

- **Observations** — raw, immediate, unprocessed captures (e.g., "I noticed I felt anxious before my presentation")
- **Patterns** — recurring observations connected over time (e.g., "I consistently feel anxious before performance events")
- **Insights** — interpreted patterns with meaning attached (e.g., "My anxiety before performance events is linked to my fear of judgment, not incompetence")

Research documentation in `docs/research/README.md` emphasizes:

> "A specification represents: Decision. Research represents: Possibility."

Insights bridge the gap — they are not decisions, but they are not pure research. They are crystallized understanding.

---

# 5. Requirements

## 5.1 Functional Requirements

- The system must support creating an observation manually.
- The system must support creating an insight manually.
- Observations and insights must be associated with one or more domains.
- Observations and insights must support optional association with a practice.
- Insights must support a confidence level (low, medium, high).
- Insights must support tagging for discovery and filtering.
- Insights must be browsable, searchable, and filterable.
- Insight creation must work fully offline.
- Insights must support optional AI-assisted generation from observations.
- The system must surface related insights when viewing a domain or practice.

## 5.2 Non-Functional Requirements

- Insight models must be immutable (use `freezed`).
- Insight identifiers must be stable.
- Insight content must be stored locally in a structured database.
- Insights must be serializable to and from JSON.
- Insight queries must remain performant as data grows.
- AI-generated insights must be clearly marked to distinguish them from human-authored insights.

---

# 6. Architecture

## 6.1 Insight Type Hierarchy

```
InsightType
  observation   — raw capture, minimal processing
  pattern       — recurring theme identified by user or AI
  insight       — interpreted meaning, highest cognitive artifact
```

## 6.2 Insight Model Structure

```
Insight
  id: String
  type: InsightType           — observation | pattern | insight
  title: String               — short summary
  body: String                — full content
  domainIds: List<String>     — associated domains
  practiceId: String?         — optional linked practice
  tags: List<String>
  confidence: ConfidenceLevel — low | medium | high
  sourceType: InsightSource   — manual | ai-generated | practice-derived
  relatedInsightIds: List<String>
  createdAt: DateTime
  updatedAt: DateTime

ConfidenceLevel
  low
  medium
  high

InsightSource
  manual
  aiGenerated
  practiceDerived
```

## 6.3 Components

- **Insight Model** — Immutable data class.
- **Insight Repository** — Interface for CRUD operations on insights.
- **Insight Provider** — Riverpod providers exposing insight state.
- **Insight Generator** — Service interface for AI-assisted insight creation.
- **Insight Feature** — UI screens for viewing and creating insights.

## 6.4 Data Flow

### Manual Insight Creation
```
User input
  ↓
Insight creation form
  ↓
InsightRepository.create()
  ↓
Local database (Drift)
  ↓
Insight providers refresh
  ↓
Insight appears in list
```

### AI-Assisted Insight Generation
```
User selects observations
  ↓
InsightGenerator.generate(observations)
  ↓
AIProvider.summarize() or AIProvider.analyze()
  ↓
Draft insight returned
  ↓
User reviews and confirms
  ↓
InsightRepository.create()
  ↓
Local database
```

## 6.5 Feature Directory Structure

```
lib/features/insights/
  presentation/
    insight_list_screen.dart
    insight_detail_screen.dart
    insight_create_screen.dart
    widgets/
      insight_card.dart
      insight_type_badge.dart
      insight_confidence_indicator.dart
  providers/
    insights_provider.dart
    insights_provider.g.dart
    insight_generator_provider.dart
    insight_generator_provider.g.dart
  domain/
    insight.dart
    insight.freezed.dart
    insight.g.dart
    insight_type.dart
    confidence_level.dart
    insight_source.dart
  data/
    insight_repository.dart
    insight_repository_impl.dart
    insight_generator.dart
    insight_generator_impl.dart
```

## 6.6 Dependencies

- `freezed` + `freezed_annotation` — immutable models
- `json_serializable` + `json_annotation` — serialization
- `flutter_riverpod` + `riverpod_annotation` — state management
- `drift` — local storage
- `AIProvider` abstraction — AI-assisted generation (optional, gracefully degraded)

---

# 7. Implementation Plan

## Phase 1 — Model and Storage

- [ ] Define `Insight` model using `freezed`.
- [ ] Define `InsightType`, `ConfidenceLevel`, `InsightSource` enums.
- [ ] Create `InsightRepository` interface.
- [ ] Implement `InsightRepositoryImpl` backed by Drift.
- [ ] Define database table schema for insights.

## Phase 2 — Provider and State

- [ ] Create `insightsProvider` using Riverpod code generation.
- [ ] Create `insightByIdProvider`.
- [ ] Create `insightsByDomainProvider`.
- [ ] Create `insightsByPracticeProvider`.

## Phase 3 — Feature UI

- [ ] Create `InsightListScreen`.
- [ ] Create `InsightDetailScreen`.
- [ ] Create `InsightCreateScreen`.
- [ ] Create `InsightCard`, `InsightTypeBadge`, and `InsightConfidenceIndicator` widgets.
- [ ] Add insight routes to app router.

## Phase 4 — AI Integration

- [ ] Define `InsightGenerator` service interface.
- [ ] Implement `AIInsightGeneratorImpl` using `AIProvider` abstraction.
- [ ] Add AI-generated insight creation flow to UI.
- [ ] Mark AI-generated insights with `sourceType: aiGenerated`.

## Phase 5 — Validation

- [ ] Write unit tests for `Insight` model.
- [ ] Write unit tests for `InsightRepository`.
- [ ] Write unit tests for `InsightGenerator`.
- [ ] Write widget tests for `InsightCard`.
- [ ] Validate offline creation and retrieval.

---

# 8. Validation Plan

- Unit tests for insight model serialization and deserialization.
- Unit tests for repository CRUD operations.
- Unit tests for insight filtering by domain and practice.
- Widget tests for insight list and card rendering.
- Integration tests for insight creation flow.
- Manual validation that AI-generated insights are clearly labeled.
- CI must pass all tests.

---

# 9. Acceptance Criteria

- [ ] `Insight` model supports `observation`, `pattern`, and `insight` types.
- [ ] Insights are stored and retrieved locally.
- [ ] Insights are associated with domains and optionally practices.
- [ ] Insights are browsable, filterable, and searchable.
- [ ] AI-generated insights are clearly distinguished from manually authored ones.
- [ ] Insight creation works fully offline.
- [ ] All unit, widget, and integration tests pass.

---

# 10. Open Questions

- Should observations be a separate model from insights, or unified under one type?
- How should insight search be implemented — full-text search in Drift, or in-memory filtering?
- Should AI-generated insights require user confirmation before being persisted?
- How should related insights be linked — explicit user curation or automated similarity matching?
- Should insights support a "revisit" or "aging" mechanism to surface older insights periodically?
