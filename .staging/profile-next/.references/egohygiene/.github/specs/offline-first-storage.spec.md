# Offline-First Storage

## Metadata

- **Spec ID:** `offline-first-storage`
- **File Name:** `offline-first-storage.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #9
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-21

---

# 1. Purpose

Define the local-first storage architecture and synchronization boundaries for Ego Hygiene.

Ego Hygiene is a personal cognition system. User data is deeply personal and must be available at all times, including without network access. This specification establishes the canonical storage model, database schema conventions, service abstractions, and future synchronization boundaries.

---

# 2. Goals

- Define the canonical local storage architecture.
- Define the database schema conventions for structured data.
- Establish service abstractions for each storage tier.
- Define data migration strategy.
- Define the synchronization boundary between local and cloud storage.
- Ensure data persistence survives app restarts and offline usage.

---

# 3. Non-Goals

- This spec does not define cloud storage backends.
- This spec does not define real-time synchronization protocols.
- This spec does not define authentication or authorization (future concern).
- This spec does not define individual feature schemas in full detail; it establishes conventions.

---

# 4. Context

The `flutter-engineer.spec.md` defines the technology selections:

- `drift` + `sqlite3_flutter_libs` — primary structured local storage
- `shared_preferences` — lightweight key-value preferences
- `flutter_secure_storage` — secrets and credentials

The `ARCHITECTURE.md` documents that these are active in the codebase.

The application's philosophy (from `MANIFESTO.md` and `SYSTEM.md`) is:

> "Offline behavior should be considered the default. Cloud synchronization should be treated as an enhancement layer."

This spec operationalizes that philosophy into a concrete architecture.

---

# 5. Requirements

## 5.1 Functional Requirements

- All structured user data must be stored in a local SQLite database via Drift.
- The application must function without network access.
- Data must persist across application restarts.
- The database must support typed schema definitions.
- The database must support migrations between schema versions.
- Key-value preferences (e.g., theme mode, locale) must be stored via `shared_preferences`.
- Secrets and tokens must be stored via `flutter_secure_storage`.
- Service abstractions must decouple feature code from storage implementations.
- The storage layer must be mockable for testing.

## 5.2 Non-Functional Requirements

- Database access must be asynchronous.
- Database queries must return typed results.
- Database schema changes must be versioned with explicit migration steps.
- Storage abstractions must follow the interface pattern defined in `lib/shared/services/`.
- Data models returned from the database must map to domain models via mappers.
- Database size must be monitored and managed to avoid unbounded growth.

---

# 6. Architecture

## 6.1 Storage Tiers

```
Tier 1 — Structured Data (Drift / SQLite)
  Domains, Practices, PracticeCompletions, Insights, Settings entities

Tier 2 — Key-Value Preferences (shared_preferences)
  Theme mode, locale, onboarding state, feature flags

Tier 3 — Secure Storage (flutter_secure_storage)
  API tokens, credentials, encryption keys
```

## 6.2 Database Architecture

```
lib/shared/database/
  app_database.dart         — Drift database class (@DriftDatabase)
  app_database.g.dart       — Generated
  tables/
    domains_table.dart
    practices_table.dart
    practice_completions_table.dart
    insights_table.dart
  daos/
    domains_dao.dart
    practices_dao.dart
    practice_completions_dao.dart
    insights_dao.dart
  migrations/
    migration_strategy.dart
```

## 6.3 Table Schema Conventions

All Drift tables must follow these conventions:

```
— Primary key: TEXT (UUID), not auto-increment integer
— Created at: INTEGER (Unix timestamp milliseconds)
— Updated at: INTEGER (Unix timestamp milliseconds)
— Soft delete: BOOLEAN (nullable, defaults to false)
— All nullable fields marked explicitly in schema
```

### Example: InsightsTable

```dart
class InsightsTable extends Table {
  TextColumn get id => text()();
  TextColumn get type => text()();           // observation | pattern | insight
  TextColumn get title => text()();
  TextColumn get body => text()();
  TextColumn get domainIds => text()();      // JSON encoded list
  TextColumn get practiceId => text().nullable()();
  TextColumn get tags => text()();           // JSON encoded list
  TextColumn get confidence => text()();     // low | medium | high
  TextColumn get sourceType => text()();     // manual | aiGenerated | practiceDerived
  IntColumn get createdAt => integer()();
  IntColumn get updatedAt => integer()();
  BoolColumn get isDeleted => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}
```

## 6.4 Data Access Object (DAO) Conventions

```
— Each table has a dedicated DAO.
— DAOs expose typed query methods.
— DAOs do not contain business logic.
— DAOs return Drift-generated row types.
— Feature repositories map row types to domain models.
```

## 6.5 Repository Pattern

```
Feature Layer
  DomainRepository (interface, in lib/features/domains/domain/)
    ↓
  DomainRepositoryImpl (implementation, in lib/features/domains/data/)
    ↓
  DomainsDAO (in lib/shared/database/daos/)
    ↓
  Drift (SQLite)
```

Feature repositories accept DAO dependencies. Domain models are never directly tied to Drift-generated classes — mappers translate between them.

## 6.6 Synchronization Boundary

The synchronization boundary separates local-first storage from future cloud backends:

```
Local-First Layer (current)
  Drift (SQLite)
  shared_preferences
  flutter_secure_storage

Sync Layer (future)
  SyncService interface
  ConflictResolutionStrategy
  SyncQueue
  RemoteRepository adapters
```

The application never directly calls remote APIs from feature code. All remote access is routed through a `SyncService` that manages conflict resolution and queue management.

## 6.7 Migration Strategy

```
— Migrations are numbered sequentially (v1 → v2 → v3 ...).
— Each migration is defined as a MigrationStep.
— Migrations are never destructive without explicit user notification.
— The database version is stored in app_database.dart as a constant.
— Migration tests are required for each schema change.
```

## 6.8 Service Abstractions

```
StorageService
  get(key) → Future<String?>
  set(key, value) → Future<void>
  delete(key) → Future<void>
  clear() → Future<void>

SecureStorageService
  read(key) → Future<String?>
  write(key, value) → Future<void>
  delete(key) → Future<void>
  deleteAll() → Future<void>
```

Both interfaces live in `lib/shared/services/`.

## 6.9 Dependencies

- `drift` + `drift_flutter` — structured local storage
- `sqlite3_flutter_libs` — SQLite native binaries
- `shared_preferences` — key-value preferences
- `flutter_secure_storage` — secure credential storage
- `uuid` — UUID generation for primary keys
- `path_provider` — database file path resolution

---

# 7. Implementation Plan

## Phase 1 — Database Foundation

- [ ] Create `AppDatabase` class with `@DriftDatabase` annotation.
- [ ] Define `DomainsTable`, `PracticesTable`, `PracticeCompletionsTable`, `InsightsTable`.
- [ ] Run code generation via `build_runner`.
- [ ] Create DAOs for each table.
- [ ] Wire `AppDatabase` into Riverpod as a singleton provider.

## Phase 2 — Service Abstractions

- [ ] Verify `StorageService` and `SecureStorageService` interfaces are complete.
- [ ] Verify `SharedPreferencesStorageServiceImpl` is implemented and tested.
- [ ] Verify `FlutterSecureStorageServiceImpl` is implemented and tested.

## Phase 3 — Repository Implementations

- [ ] Implement `DomainRepositoryImpl` using `DomainsDAO`.
- [ ] Implement `PracticeRepositoryImpl` using `PracticesDAO`.
- [ ] Implement `PracticeCompletionRepositoryImpl` using `PracticeCompletionsDAO`.
- [ ] Implement `InsightRepositoryImpl` using `InsightsDAO`.
- [ ] Define domain-to-DAO mappers for each entity.

## Phase 4 — Migration Infrastructure

- [ ] Define initial database version (v1).
- [ ] Create `MigrationStrategy` in `migration_strategy.dart`.
- [ ] Write migration tests for the initial schema.

## Phase 5 — Validation

- [ ] Write unit tests for each DAO.
- [ ] Write unit tests for each repository implementation.
- [ ] Write integration tests for full write/read/delete cycles.
- [ ] Validate offline persistence across app restarts.

---

# 8. Validation Plan

- Unit tests for all DAOs (CRUD operations).
- Unit tests for all repository implementations.
- Unit tests for domain-model mappers.
- Integration tests for complete data lifecycle (create, read, update, delete).
- Manual validation of persistence across app restarts.
- Manual validation of offline behavior (flight mode).
- CI must pass all tests.

---

# 9. Acceptance Criteria

- [ ] `AppDatabase` is defined with all required tables.
- [ ] DAOs exist for each table with typed query methods.
- [ ] Repository implementations are complete for domains, practices, practice completions, and insights.
- [ ] Domain-to-DAO mappers are implemented for all entities.
- [ ] `StorageService` and `SecureStorageService` abstractions are in place with implementations.
- [ ] Database migration infrastructure is initialized.
- [ ] All DAO and repository unit tests pass.
- [ ] Application data persists across restarts.
- [ ] Application functions fully offline.

---

# 10. Open Questions

- Should the database file be encrypted at rest using sqlcipher in the initial implementation?
- Should soft deletes be standard across all tables, or only for user-created entities?
- How should the synchronization queue be modeled when cloud sync is added?
- Should `shared_preferences` be replaced with a single-table Drift preferences store for consistency?
- Should the database include a full-text search index for insights from the start?
