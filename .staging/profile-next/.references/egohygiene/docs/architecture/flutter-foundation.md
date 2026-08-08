# Flutter Foundation

This document covers the technology stack, shared service abstractions, state management, localization, build system, CI/CD pipeline, development guidelines, and the application-level engines that form the Flutter foundation of Ego Hygiene.

---

## Technology Stack

### State Management
- **Flutter Riverpod** (v3.3.2) - Reactive state management
- **riverpod_annotation** - Code generation for providers
- **riverpod_generator** - Provider code generator

### Navigation
- **go_router** (v17.3.0) - Declarative routing with deep linking support

### Localization
- **slang** (v4.16.0) - Type-safe internationalization
- **intl** (v0.20.2) - Internationalization utilities

### Theme System
- **flex_color_scheme** (v8.4.0) - Advanced theming
- **google_fonts** (v8.1.0) - Typography (Inter + Crimson Pro)
- **dynamic_color** (v1.8.1) - Material You support

### Storage
- **drift** (v2.34.0) - Type-safe SQL database
- **shared_preferences** (v2.5.5) - Key-value storage
- **flutter_secure_storage** (v10.3.1) - Secure credential storage

### Networking
- **dio** (v5.9.2) - HTTP client
- **pretty_dio_logger** (v1.4.0) - Request/response logging (dev only)

### Notifications
- **flutter_local_notifications** (v22.0.1) - Local notifications
- **timezone** (v0.11.0) - Timezone support

### UI Components
- **flutter_animate** (v4.5.2) - Animations
- **lottie** (v3.3.3) - Lottie animations
- **flutter_svg** (v2.3.0) - SVG support
- **fl_chart** (v1.2.0) - Charts and graphs

### Forms
- **flutter_form_builder** (v10.3.0+2) - Form building
- **form_builder_validators** (v11.3.0) - Form validation

### Code Generation
- **build_runner** (v2.15.0) - Code generation runner
- **freezed** (v3.2.5) - Immutable data classes
- **json_serializable** (v6.14.0) - JSON serialization

### Testing
- **mocktail** (v1.0.5) - Mocking
- **golden_toolkit** (v0.15.0) - Golden tests

---

## Service Abstractions

All external dependencies are abstracted behind interfaces.

### Notification Lifecycle
- `NotificationService` - Platform adapter abstraction (show, schedule, cancel)
- `NotificationManager` - Lifecycle orchestrator; the single entry point for features
- `NotificationScheduler` - Scheduling strategy abstraction (immediate, scheduled, delayed, daily)
- `NotificationChannel` - Platform channel/category configuration (Android channels, iOS categories)
- `LocalNotificationScheduler` - Default scheduler for local notifications
- `NoopNotificationService` - Safe no-op fallback for tests and startup
- Lifecycle: Application → NotificationManager → NotificationScheduler → NotificationService → Platform
- Prepared for: push notifications, action buttons, deep links, quiet hours, smart scheduling

### Permission Management
- `PermissionManager` - Centralized permission lifecycle orchestration
- `PermissionPlatform` - Cross-platform permission abstraction
- `PermissionState` / `PermissionResult` - Shared status model (`undetermined`, denied, permanently denied, limited, unavailable)
- `PermissionRequest` - Canonical rationale, denial copy, retry labels, settings deep link metadata, manual fallback metadata, and provider requirements
- `permissionPlatformProvider` - Location-aware platform adapter: routes location permission checks/requests through `LocationManager`
- Supports notifications, location, weather, health connect, Apple Health, calendar, storage, microphone, camera, bluetooth, photos, and health
- UI patterns: `ContextPermissionCard` for reusable rationale/denial/retry/manual-fallback presentation

### Location Engine
- `LocationManager` - Central orchestrator; single entry point for all location-related features
- `LocationProvider` - Platform location adapter abstraction (disabled / manual / GPS)
- `GeocodingProvider` - Forward and reverse geocoding abstraction
- `TimezoneResolver` - Coordinate → IANA timezone and BCP 47 locale abstraction
- `AppLocation` - Core location entity (coordinate, accuracy, mode, address, timezone)
- `LocationCoordinate` - Immutable lat/lng value object
- `LocationSnapshot` - Immutable point-in-time view for context assembly
- `LocationMode` - Privacy model: disabled | approximate | precise | manual
- `DisabledLocationProvider` - Safe no-op default; never accesses device hardware
- `ManualLocationProvider` - User-chosen coordinate; no permission required
- `NoopGeocodingProvider` - Safe default; returns null for all geocoding queries
- `NoopTimezoneResolver` - Safe default; returns null for all resolution queries
- `LocationContextSource` - [ContextSource] integration for the Context Assembly Engine
- Privacy: Location is always user-controlled. The app degrades gracefully when unavailable.
- Lifecycle: Application → LocationManager → LocationProvider → Platform (or manual)

---

## State Management

### Provider Types
- **NotifierProvider** - For mutable state
- **Provider** - For computed values
- **FutureProvider** - For async data
- **StreamProvider** - For stream data

### Code Generation
Providers use Riverpod's code generation:

```dart
@riverpod
class AppThemeMode extends _$AppThemeMode {
  @override
  ThemeMode build() {
    return ThemeMode.system;
  }
  
  void toggle() {
    state = state == ThemeMode.light 
        ? ThemeMode.dark 
        : ThemeMode.light;
  }
}
```

---

## Localization

### Translation Files
- Located in `lib/shared/localization/`
- Format: `app_<locale>.i18n.json`
- Generated code: `strings.g.dart`

### Usage
```dart
import 'package:egohygiene/shared/localization/strings.g.dart';

// Direct access
Text(Translations.appName);

// Extension method
Text(context.t.appName);
```

---

## Build System

### Code Generation
```bash
# Run all generators
fvm dart run build_runner build --delete-conflicting-outputs
fvm dart run slang
```

### Task Runner
Using Taskfile.yml:
```bash
task setup     # Install FVM SDK + dependencies
task generate  # Run code generation
task analyze   # Static analysis
task test      # Run tests
task build:web # Build web release
task run       # Run on default device
task ci:local  # CI-equivalent local checks
```

---

## CI/CD

### GitHub Actions Workflow
Entry workflows:

- `.github/workflows/build.yml` (pull requests / manual dispatch)
- `.github/workflows/development-build.yml` (push to `main` / manual dispatch)

Shared pipeline:

- `.github/workflows/reusable/flutter-ci.yml` (`workflow_call`)

Pipeline stages:

1. Detect Flutter app changes
2. Run code generation once and share generated artifacts
3. Run static analysis
4. Run tests (with coverage artifact upload)
5. Build Android, Web, and Linux when Flutter app sources changed
6. Upload platform artifacts

---

## Development Guidelines

### Adding New Features
1. Create feature directory in `features/`
2. Implement presentation layer
3. Create providers for state
4. Add business logic in domain/
5. Implement data layer
6. Add route to router
7. Write tests
8. Update documentation

### Code Style
- Follow Dart style guide
- Use `very_good_analysis` lints
- Run `flutter analyze` before committing
- Keep functions small and focused
- Document public APIs

### Git Workflow
- Use Conventional Commits
- Feature branches: `feat/<feature-name>`
- Fix branches: `fix/<issue-name>`
- Commit messages: `type: description`

---

## Practice Engine

### Overview

The Practice Engine is the generic, data-driven system that manages every
intentional practice within Ego Hygiene.  Practices are defined by the
`PracticeType` enum and managed consistently by a single `PracticeManager`
rather than having each practice individually implemented.

### Architecture

```
PracticeManager                      — orchestrator; single entry point for features
  ├── PracticeStore                  — persistence abstraction (pluggable)
  │     └── InMemoryPracticeStore   — default transient implementation
  └── PracticeSource (0..*)         — external completion provider (pluggable)
        └── ReflectionPracticeSource — bridges the Reflection feature
```

All files live in `lib/shared/practice/`.

### Core Types

#### `PracticeType` (`lib/shared/practice/practice_type.dart`)

Enum that classifies each supported intentional practice:

| Type | Description |
|---|---|
| `reflection` | Conscious review of experience, patterns, and learning |
| `gratitude` | Intentional acknowledgement of appreciation |
| `abundance` | Cultivating awareness of sufficiency and growth |
| `mindfulness` | Present-moment awareness and attention training |
| `journaling` | Structured written expression and self-inquiry |
| `sleepHygiene` | Intentional preparation for restorative sleep |

#### `PracticeState` (`lib/shared/practice/practice_state.dart`)

Lifecycle state per practice: `active`, `paused`, `archived`.

#### `PracticeSchedule` (`lib/shared/practice/practice_schedule.dart`)

Immutable value object encoding cadence (`daily`, `weekly`, `custom`),
enabled status, and target completions per period.  `isDueOn` determines
whether the practice is due on a given date given completion history.

#### `PracticeCompletion` (`lib/shared/practice/practice_completion.dart`)

The core domain entity.  Each instance represents one recorded execution of a
practice — a reflection written, a gratitude log entry, a mindfulness session.

Key fields: `id`, `type`, `completedAt`, `notes`, `durationMinutes`, `metadata`.

#### `PracticeProgress` (`lib/shared/practice/practice_progress.dart`)

Immutable computed statistics for a single practice type.  Produced by
`PracticeProgress.compute(type, completions)`.

Key fields: `currentStreak`, `longestStreak`, `totalCompletions`,
`lastCompletedAt`, `recentHistory`, `isCompletedToday`.

Streak logic: a streak counts consecutive calendar days with at least one
completion.  A gap resets the current streak; the longest streak is tracked
across all history.

#### `PracticeStore` (`lib/shared/practice/practice_store.dart`)

Abstract persistence contract.  `InMemoryPracticeStore` is the default
transient implementation.

#### `PracticeSource` (`lib/shared/practice/practice_source.dart`)

Pluggable interface for external completion providers.  Allows feature modules
such as Reflection to supply completions without modifying the Practice Engine.

#### `ReflectionPracticeSource` (`lib/shared/practice/impl/reflection_practice_source.dart`)

Adapter that bridges the `ReflectionRepository` into the Practice Engine.
Each saved reflection is exposed as a `PracticeCompletion` of type
`PracticeType.reflection` without modifying the reflection creation flow.

#### `PracticeManager` (`lib/shared/practice/practice_manager.dart`)

Central orchestrator.  Coordinates native completion storage, pluggable
source adapters, per-practice state, and schedule configuration.

### Riverpod Providers

| Provider | Type | Description |
|---|---|---|
| `practiceStoreProvider` | `Provider<PracticeStore>` | Active store; override for persistent backend |
| `practiceManagerProvider` | `Provider<PracticeManager>` | App-wide manager with `ReflectionPracticeSource` wired in |

Import the barrel:

```dart
import 'package:egohygiene/shared/practice/practice_engine.dart';
```

### Supported Features

- **Daily completion tracking** — `complete()` records each session
- **Streaks** — `currentStreak` and `longestStreak` via `PracticeProgress.compute`
- **History** — `getCompletions()` merges native and sourced completions
- **Notes** — optional free-text captured on each `PracticeCompletion`
- **Schedule awareness** — `PracticeSchedule.isDueOn` determines due status
- **Future reminders** — extend `PracticeSchedule` with `preferredTime` and `reminderEnabled`
- **Future AI coaching** — wire AI coaching adapters as `PracticeSource` instances

### Future Compatibility

- **Adaptive practices** — swap `PracticeSchedule` for AI-generated schedules
- **Practice recommendations** — add a recommendation source via `PracticeSource`
- **Therapist assignments** — wire a therapist-sync adapter as a `PracticeSource`
- **AI-generated practices** — add new `PracticeType` values without engine changes

---

## Domain Health Engine

### Overview

The Domain Health Engine computes per-domain health summaries from aggregated
activity signals.  It powers the dashboard cards and AI context pipeline.

### Architecture

```
DomainHealthEngine                          — orchestrator; single entry point
  ├── DomainSignalSource (0..*)             — pluggable signal provider
  │     ├── CheckInSignalSource             — daily check-ins (domain-specific)
  │     ├── ReflectionSignalSource          — written reflections (global proxy)
  │     └── PracticeSignalSource            — completed practices (global proxy)
  └── DomainHealthCalculator               — computation strategy
        └── PlaceholderDomainHealthCalculator — default heuristic implementation
```

All files live in `lib/shared/health/`.

### Signal Sources

#### `CheckInSignalSource` (`lib/shared/health/impl/check_in_signal_source.dart`)

Adapts `CheckInRepository` to domain-specific timestamps.  Each daily
check-in is mapped to `HealthDomain.mentalEmotional` and `HealthDomain.physical`.

#### `ReflectionSignalSource` (`lib/shared/health/impl/reflection_signal_source.dart`)

Adapts `ReflectionRepository` to global reflection timestamps.  Reflections
are not domain-specific; the calculator distributes them across all monitored
domains as a proxy signal via `DomainHealthInput.reflectionTimestamps`.

#### `PracticeSignalSource` (`lib/shared/health/impl/practice_signal_source.dart`)

Adapts the `PracticeCompletionLoader` to global practice completion timestamps.
Completions are not domain-specific; the calculator distributes them across all
monitored domains as a proxy signal via
`DomainHealthInput.practiceCompletionTimestamps`.

### Signal Weighting

`PlaceholderDomainHealthCalculator` applies the following weights when
computing domain status, trend, and confidence:

| Signal type              | Weight | Scope          |
|--------------------------|--------|----------------|
| Domain check-in          | 3×     | Domain-specific |
| Reflection entry         | 1×     | Global proxy   |
| Practice completion      | 1×     | Global proxy   |

Domain check-ins carry a higher weight because they represent explicit,
domain-scoped engagement.  Reflections and practices are general-purpose
proxy signals that contribute to all domains when no domain-specific data
is available.

Confidence is computed as:

```
confidence = clamp((checkIns * 3 + globalActivity) / 30, 0.0, 1.0)
```

### Core Types

#### `DomainHealthInput` (`lib/shared/health/domain_health_engine.dart`)

Aggregated signal data supplied to a `DomainHealthCalculator`.  Carries both
domain-specific check-in timestamps and global reflection / practice timestamps.

#### `DomainSummary` (`lib/shared/health/domain_summary.dart`)

Immutable per-domain result.  Includes `DomainStatus`, `DomainTrend`,
`confidence`, `supportingSignals`, and `computedAt`.

#### `DomainSignalSource` (`lib/shared/health/domain_signal_source.dart`)

Pluggable interface for signal providers.  Override `collectTimestamps()` for
domain-specific signals, `collectReflectionTimestamps()` for global reflection
timestamps, or `collectPracticeTimestamps()` for global practice timestamps.

### Riverpod Providers (`lib/shared/providers/domain_health_providers.dart`)

- `domainHealthEngineProvider` — app-wide `DomainHealthEngine` with all three
  built-in signal sources registered.
- `domainSummariesProvider` — current `List<DomainSummary>` for the dashboard.

### Future Compatibility

- **Wearables** — implement a `WearableSignalSource` with domain-specific
  timestamps for `HealthDomain.physical`.
- **Sleep / Nutrition** — add domain-mapped sources for the `physical` domain.
- **Dreams** — contribute to `HealthDomain.mentalEmotional` via a new source.
- **Therapist observations** — wire an external observation provider as a
  domain-specific `DomainSignalSource`.

---

## Goal Engine

### Overview

Goals represent desired future states.  Practices represent movement toward
those states.  The Goal Engine provides a reusable, pluggable architecture
for defining, tracking, and completing goals across all life domains.

The Goal Engine connects naturally to the Practice Engine (related practice
types), the Domain Health Engine (domain label), and the Timeline Engine
(goal events).

### Architecture

```
GoalManager                      — orchestrator; single entry point for features
  ├── GoalStore                  — persistence abstraction (pluggable)
  │     └── InMemoryGoalStore   — default transient implementation
  └── GoalSource (0..*)         — external goal provider (pluggable)
        └── (future: TherapistGoalSource, AiPlanningSource)
```

All files live in `lib/shared/goal/`.

### Core Types

#### `GoalStatus` (`lib/shared/goal/goal_status.dart`)

Lifecycle state for a goal:

| Status | Description |
|---|---|
| `active` | Currently being pursued |
| `paused` | Temporarily on hold |
| `completed` | Successfully achieved |
| `archived` | Not actively tracked; history retained |
| `cancelled` | Explicitly abandoned |

`GoalStatus.isTerminal` returns `true` for `completed` and `cancelled`.

#### `GoalPriority` (`lib/shared/goal/goal_priority.dart`)

Importance level:

| Priority | Description |
|---|---|
| `low` | Addressed when higher-priority items are done |
| `medium` | Default priority for new goals |
| `high` | Should be addressed soon |
| `critical` | Requires immediate attention |

#### `Milestone` (`lib/shared/goal/milestone.dart`)

An immutable discrete checkpoint embedded within a [Goal].  Each milestone
carries an `id`, `title`, optional `description`, `isCompleted` flag,
`completedAt` timestamp, and an optional `targetDate`.

#### `Goal` (`lib/shared/goal/goal.dart`)

The core domain entity.  Each instance represents one desired future state.

Key fields: `id`, `title`, `description`, `status`, `priority`, `domain`,
`relatedPracticeTypes`, `milestones`, `targetDate`, `tags`, `notes`,
`createdAt`, `updatedAt`, `completedAt`, `metadata`.

`domain` is a string label linking to the Domain Health Engine (e.g.
`'mentalEmotional'`, `'physical'`).  `relatedPracticeTypes` lists practice
type names that support this goal.

#### `GoalProgress` (`lib/shared/goal/goal_progress.dart`)

Immutable computed progress statistics for a single goal.  Produced by
`GoalProgress.compute(goal)`.

Key fields: `goalId`, `totalMilestones`, `completedMilestones`,
`progressPercent` (0.0–1.0), `isComplete`, `computedAt`.

A goal is considered complete when all milestones are done or the status is
a terminal state (`completed` or `cancelled`).

#### `GoalStore` (`lib/shared/goal/goal_store.dart`)

Abstract persistence contract.  `InMemoryGoalStore` is the default transient
implementation.

Key operations: `findById`, `findAll`, `findByStatus`, `findByDomain`,
`save`, `saveAll`, `deleteById`, `clear`, `count`.

#### `GoalSource` (`lib/shared/goal/goal_source.dart`)

Pluggable interface for external goal providers.  Allows external systems
(therapist portal, AI planner) to contribute goals without modifying the
Goal Engine.

#### `GoalManager` (`lib/shared/goal/goal_manager.dart`)

Central orchestrator.  Coordinates native goal storage, pluggable source
adapters, milestone management, and goal completion.

Key operations:

| Method | Description |
|---|---|
| `createGoal(...)` | Create and persist a new goal |
| `updateGoal(goal)` | Persist a modified goal |
| `deleteGoal(id)` | Remove a goal from storage |
| `getGoal(id)` | Retrieve a single goal by ID |
| `getAllGoals()` | All goals merged from store and sources |
| `getActiveGoals()` | Goals with `GoalStatus.active` |
| `getGoalsByStatus(status)` | Filter by lifecycle state |
| `getGoalsByDomain(domain)` | Filter by life domain label |
| `addMilestone(goalId, ms)` | Append a milestone to a goal |
| `completeMilestone(goalId, msId)` | Mark a milestone as achieved |
| `completeGoal(id)` | Mark the goal as successfully achieved |
| `getProgress(id)` | Compute `GoalProgress` for a goal |

### Riverpod Providers

| Provider | Type | Description |
|---|---|---|
| `goalStoreProvider` | `Provider<GoalStore>` | Active store; override for persistent backend |
| `goalManagerProvider` | `Provider<GoalManager>` | App-wide manager |

Import the barrel:

```dart
import 'package:egohygiene/shared/goal/goal_engine.dart';
```

### Supported Features

- **Goal lifecycle** — create, update, complete, archive, and cancel goals
- **Milestone tracking** — attach discrete checkpoints and mark them done
- **Progress computation** — `GoalProgress.compute` derives percent complete
- **Domain integration** — `goal.domain` links to the Domain Health Engine
- **Practice integration** — `relatedPracticeTypes` connects goals to practices
- **External sources** — `GoalSource` bridges therapist or AI-generated goals

### Future Compatibility

- **Persistent backend** — swap `InMemoryGoalStore` for a `LocalGoalStore`
- **Therapist goals** — wire a therapist portal as a `GoalSource`
- **AI planning** — wire an AI planning assistant as a `GoalSource`
- **Habit suggestions** — surface habit-based goals via `GoalSource`
- **Timeline integration** — emit `goal` events to the Timeline Engine
- **Reflection linkage** — link reflections to goals via metadata

---

## Timeline Engine

### Overview

The Timeline Engine provides a unified chronological stream of user journey
activity. Everything is represented as a `TimelineEvent` and collected through
pluggable `TimelineSource` implementations.

### Architecture

```
TimelineManager                   — orchestrator; single entry point
  └── TimelineSource (0..*)       — event publisher interface (pluggable)
        ├── ReflectionTimelineSource
        ├── PracticeTimelineSource
        └── InsightTimelineSource

TimelineEvent                     — immutable event model
TimelineFilter                    — filtering (type, source, date, query)
```

All files live in `lib/shared/timeline/`.

### Integration

- Reflection data maps to `TimelineEventType.reflection`.
- Practice completion timestamps map to `TimelineEventType.practiceCompletion`.
- Generated insights map to `TimelineEventType.insight`.
- Future event categories (`goal`, `healthMetric`, `aiConversation`) are first-class in `TimelineEventType` for forward compatibility.

### Future Compatibility

The Timeline Engine is prepared for search, filtering, calendar views,
therapist review, and AI summarization by design through typed events and
source-level decoupling.

---

## Future Enhancements

### Planned Features
- Reflection module
- Memory module
- Progress visualization
- Settings and preferences
- Offline-first synchronization
- AI integration
- Notification workflows

### Technical Improvements
- Drift database schema
- API client implementation
- Authentication system
- Background task scheduling
- Analytics integration
- Error monitoring (Sentry)
