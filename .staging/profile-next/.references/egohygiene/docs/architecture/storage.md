# Storage Architecture

This document covers the storage service abstractions, encryption architecture, storage layer, privacy engine, data portability engine, and conflict resolution engine.

---

## Service Abstractions

### Storage Services
- `StorageService` - Key-value storage interface
- `SecureStorageService` - Secure storage interface
- Implementations in `lib/shared/services/impl/`

---

## Encryption Architecture

### Principles

The encryption layer follows a **local-first, at-rest** design.  Keys never
leave the device without explicit user consent.  Feature modules never
interact with cryptographic primitives directly; they use [EncryptionManager]
exclusively.

### Layered Architecture

```
Feature Provider
  → Repository / Manager
    → EncryptedStorageService (transparent key-value decorator)
      → EncryptionManager      (lib/shared/services/encryption_manager.dart)
        → KeyManager           (lib/shared/services/key_manager.dart)
        |   → SecureStorageService  (hardware-backed key storage)
        → EncryptionProvider   (lib/shared/services/encryption_provider.dart)
            → cryptography package (AES-256-GCM)
```

### Components

#### EncryptedPayload (`lib/shared/storage/encrypted_payload.dart`)

`EncryptedPayload` is the portable container for encrypted data.  It carries:

| Field | Description |
|---|---|
| `version` | Schema version for future format migrations |
| `algorithmId` | Identifies the algorithm (e.g. `'aes-gcm-256'`) |
| `ciphertext` | Encrypted bytes |
| `nonce` | Random nonce / IV used during encryption |
| `mac` | Authentication tag (for authenticated encryption) |

Payloads serialise to/from JSON and compact Base64 for storage and future
encrypted sync:

```dart
final encoded = payload.toBase64();
final restored = EncryptedPayload.fromBase64(encoded);
```

#### EncryptionProvider (`lib/shared/services/encryption_provider.dart`)

Stateless cryptographic operations:

```dart
abstract class EncryptionProvider {
  String get algorithmId;
  Future<List<int>> generateKey();
  Future<EncryptedPayload> encrypt(List<int> plaintext, List<int> key);
  Future<List<int>> decrypt(EncryptedPayload payload, List<int> key);
}
```

Default implementation: `AesGcmEncryptionProvider` (AES-256-GCM).

#### KeyManager (`lib/shared/services/key_manager.dart`)

Key lifecycle management:

```dart
abstract class KeyManager {
  Future<List<int>> getOrCreateKey(String keyId);
  Future<List<int>?> getKey(String keyId);
  Future<void> storeKey(String keyId, List<int> key);
  Future<void> deleteKey(String keyId);
  Future<bool> keyExists(String keyId);
  Future<List<int>> rotateKey(String keyId);
}
```

Default implementation: `SecureStorageKeyManager`, which stores keys as
Base64 strings under `encryption.key.v1.<keyId>` in `SecureStorageService`.

Key identifiers should be domain-scoped:

```
'reflection.entries'
'settings.sensitive'
'backup.archive'
```

#### EncryptionManager (`lib/shared/services/encryption_manager.dart`)

The single entry point for feature modules:

```dart
// Encrypt sensitive text for at-rest storage
final payload = await encryptionManager.encryptString(text, 'reflection.entries');

// Decrypt when reading back
final plaintext = await encryptionManager.decryptString(payload, 'reflection.entries');
```

#### EncryptedStorageService (`lib/shared/services/impl/encrypted_storage_service.dart`)

Transparent at-rest encryption for existing key-value repositories:

```dart
final storage = EncryptedStorageService(
  storage: SharedPreferencesStorage(),
  encryptionManager: encryptionManager,
);
```

Responsibilities:

- encrypt values before persisting them in the underlying `StorageService`
- decrypt values when reading them back
- migrate legacy plaintext values on first read
- keep repository contracts unchanged so higher layers remain encryption-agnostic

Encrypted values are stored as versioned envelopes with the prefix `enc:v1:`
followed by a Base64-encoded `EncryptedPayload`. Values without that prefix are
treated as legacy plaintext and re-saved in encrypted form after a successful
read.

#### Exception Hierarchy (`lib/shared/storage/encryption_exception.dart`)

All encryption errors propagate as typed `EncryptionException` subclasses:

| Exception | Meaning |
|---|---|
| `EncryptionFailedException` | Encryption operation failed |
| `DecryptionFailedException` | Decryption failed (tampered, wrong key) |
| `KeyNotFoundException` | Requested key does not exist |
| `KeyRotationException` | Key rotation failed |
| `UnsupportedAlgorithmException` | Payload algorithm not recognised |

### Riverpod Providers (`lib/shared/providers/encryption_providers.dart`)

| Provider | Type | Purpose |
|---|---|---|
| `encryptionProviderProvider` | `EncryptionProvider` | Active crypto algorithm |
| `keyManagerProvider` | `KeyManager` | Key lifecycle management |
| `encryptionManagerProvider` | `EncryptionManager` | Feature-facing facade |

### Future Compatibility

The encryption layer is designed to support:

- **Key rotation** — `KeyManager.rotateKey(keyId)` replaces the active key
- **User passphrases** — A future `PassphraseKeyManager` can derive keys from a
  user-supplied passphrase (e.g. via PBKDF2 or Argon2)
- **Recovery keys** — A secondary key can be stored separately from the device
  key to allow data recovery
- **Encrypted backups** — A `BackupService` implementation can call
  `EncryptionManager.encryptBytes` on the serialised `BackupPayload`
- **Encrypted cloud sync** — `SyncProvider` can transmit `EncryptedPayload`
  values; the cloud never sees plaintext
- **Institutional requirements** — The `EncryptionProvider` abstraction lets
  compliant algorithms be swapped in without changing feature code

---

## Storage Architecture

### Principles

The storage layer follows a **local-first** design: the device database is the
primary source of truth. Remote synchronisation (when added) merges into local
state rather than replacing it. Feature modules never interact with storage
backends directly — they communicate exclusively through repository interfaces.

### Layered Architecture

```
Feature Provider
  → Domain Repository Interface  (lib/features/<feature>/domain/)
    → Repository Implementation  (lib/features/<feature>/data/)
      → StorageService / AppDatabase  (lib/shared/storage/ + lib/shared/services/)
        → shared_preferences / Drift / flutter_secure_storage
```

### Abstractions

#### Generic Repository (`lib/shared/storage/repository.dart`)

`Repository<T, ID>` defines the contract for persistence operations:

- `findById(id)` — look up a single entity
- `findAll()` — return all entities
- `save(entity)` — upsert an entity
- `deleteById(id)` — remove an entity
- `existsById(id)` — check existence
- `count()` — total entity count

Domain repository interfaces extend or mirror this contract and may add
domain-specific query methods.

#### Pagination (`lib/shared/storage/pageable.dart`)

`PageRequest` + `Page<T>` provide cursor-free offset pagination for large
collections. Repositories that may return many rows should expose a paginated
variant:

```dart
Future<Page<ReflectionModel>> findAllPaged(PageRequest request);
```

#### Storage Services

| Interface | Implementation | Purpose |
|---|---|---|
| `StorageService` | `SharedPreferencesStorage` | Key-value persistence |
| `SecureStorageService` | `FlutterSecureStorageImpl` | Secure credential storage |

Providers: `storageServiceProvider`, `secureStorageServiceProvider`

#### Drift Database

`AppDatabase` (in `apps/egohygiene/lib/shared/storage/app_database.dart`) is
the production persistence boundary for relational storage and currently owns:

- `reflections`
- `check_ins`
- `memories`

The database now centralizes reusable SQL projections in
`AppDatabaseQueries` so repositories and stores use shared query definitions
instead of copy-pasted column lists.

### Schema Migrations

Drift manages migrations via `MigrationStrategy`:

```dart
MigrationStrategy(
  onCreate: (m) async => _ensureSchema(),
  onUpgrade: (m, from, to) async {
    if (from < 2 && to >= 2) {
      await _migrateToV2();
    }
  },
)
```

Rules:
- Never alter or delete old migration steps.
- Each schema bump increments `schemaVersion` by exactly one.
- Migration logic is covered by `apps/egohygiene/test/shared/storage/app_database_test.dart`.
- Maintain a human-readable migration log in `docs/storage/migrations.md`.

### Data Versioning

Entities stored in key-value storage use versioned keys (e.g.
`reflection.entries.v1`) so that format changes can be handled gracefully via
a read-time migration:

```dart
final raw = await storage.get('reflection.entries.v1') ??
    await _migrateFromV0();
```

For encrypted key-value data, migration is also envelope-aware:

- unprefixed values are interpreted as legacy plaintext
- `enc:v1:` values are decoded as encrypted payloads
- a future `enc:v2:` envelope can introduce new metadata without changing
  repository contracts

### Backup & Restore (`lib/shared/storage/backup_service.dart`)

`BackupService` defines export/import of all persisted data as a
`BackupPayload`:

```dart
abstract class BackupService {
  Future<BackupPayload> exportBackup();
  Future<void> importBackup(BackupPayload payload);
}
```

The current implementation is `NoopBackupService`. Future implementations may
write encrypted archives to local file storage or a cloud provider.

### Cloud Sync (`lib/shared/storage/sync_provider.dart`)

`SyncProvider` establishes the future sync boundary. It is deliberately not
implemented today; the provider slot is occupied by `null`:

```dart
final syncProviderProvider = Provider<SyncProvider?>(_ => null);
```

Sync lifecycle (planned):
```
Application
  → SyncProvider.sync()
    → Pull remote changes
      → Apply ConflictResolutionStrategy
        → Merge into local storage
    → Push local changes to remote
```

Conflict resolution strategies (`LocalWinsStrategy`, `RemoteWinsStrategy`) are
already defined; custom strategies can implement `ConflictResolutionStrategy<T>`.

### Exception Hierarchy (`lib/shared/storage/storage_exception.dart`)

All storage errors propagate as typed `StorageException` subclasses:

| Exception | Meaning |
|---|---|
| `EntityNotFoundException` | Requested entity does not exist |
| `DuplicateEntityException` | Insert violates uniqueness |
| `StorageUnavailableException` | Backend unreachable |
| `StorageCorruptionException` | Stored data cannot be deserialised |
| `MigrationException` | Schema migration failed |

### Future Compatibility

The storage layer is designed to support:

- **Cloud synchronisation** — via a `SyncProvider` implementation
- **Conflict resolution** — via `ConflictResolutionStrategy<T>`
- **Encrypted backups** — via a `BackupService` implementation that encrypts `BackupPayload`
- **Multiple storage providers** — by overriding `storageServiceProvider` or `secureStorageServiceProvider`
- **Data portability** — via `BackupService.exportBackup` / `importBackup`

---

## Privacy Engine

Privacy is treated as an **architectural layer**, not a settings checkbox.
All privacy behavior is declared up-front and enforced centrally so that no
feature can accidentally transmit user data outside its declared contract.

### Design Principles

- **Local-first** — all data stays on-device by default (`PrivacyMode.localFirst`).
- **User-controlled** — every external data flow requires an explicit consent grant.
- **Transparent** — features declare their data handling via `PrivacyPolicy`.
- **Reversible** — consent can be revoked and data deleted at any time.
- **Minimal collection** — features request only the consent scopes they need.

### Architecture

```
PrivacyManager             — orchestrator; single entry point for features
  ├── ConsentManager       — consent storage and retrieval
  │     └── ConsentStore   — persistence abstraction (pluggable backend)
  │           └── InMemoryConsentStore  — default transient implementation
  └── PrivacyPolicyRegistry — registry of feature privacy declarations

Domain types:
  ConsentScope             — distinct consent area (crashReporting, analytics, …)
  ConsentStatus            — granted / denied / pending
  ConsentEntry             — immutable timestamped consent record
  DataVisibilityRule       — declares maximum data visibility for a category
  VisibilityLevel          — localOnly → sharedWithTherapist → … → public
  DataRetentionRule        — declares how long data is kept
  RetentionPolicy          — keepForever / deleteAfterDays / deleteOnRequest / …
  PrivacyMode              — localFirst (default) / standard / enhanced
  PrivacyPolicy            — full declared privacy contract for a feature
```

### Core Types

#### `PrivacyManager` (`lib/shared/privacy/privacy_manager.dart`)

The single entry point for application code and feature modules.  Coordinates
between the [ConsentManager] and the [PrivacyPolicyRegistry].

Key operations:
- `initialize()` — initialise the consent store
- `hasConsent(scope)` — primary consent gate for a single scope
- `grant(scope)` / `deny(scope)` / `revoke(scope)` — record decisions
- `revokeAll()` — remove all consent (use during sign-out / data deletion)
- `isFeaturePermitted(featureId)` — checks all required consents for a policy
- `registerPolicy(policy)` — register a feature's privacy contract
- `visibilityRulesFor(featureId)` — data visibility constraints
- `retentionRulesFor(featureId)` — data retention lifecycle rules
- `setMode(mode)` — change the active `PrivacyMode`

#### `ConsentManager` (`lib/shared/privacy/consent_manager.dart`)

Manages consent decisions, delegating persistence to [ConsentStore].

Key operations:
- `grant(scope)` — record user approval
- `deny(scope)` — record user refusal
- `revoke(scope)` — remove a recorded decision
- `hasConsent(scope)` — `true` only when explicitly granted
- `statusOf(scope)` — raw `ConsentStatus`
- `entryFor(scope)` — full `ConsentEntry` with timestamp and version

#### `PrivacyPolicyRegistry` (`lib/shared/privacy/privacy_policy_registry.dart`)

Registry of `PrivacyPolicy` declarations contributed by application features.
Features register their policy at startup; the Privacy Engine evaluates them
to determine which consents are needed, what data may be exported, and which
retention jobs to schedule.

#### `PrivacyPolicy` (`lib/shared/privacy/privacy_policy.dart`)

A declared privacy contract for a named feature:
- `requiredConsents` — consent scopes needed before the feature may operate.
- `visibilityRules` — `DataVisibilityRule` list governing data visibility.
- `retentionRules` — `DataRetentionRule` list governing data lifetime.

### Riverpod Providers (`lib/shared/providers/privacy_providers.dart`)

| Provider | Type | Purpose |
|---|---|---|
| `consentStoreProvider` | `ConsentStore` | Active persistence backend |
| `consentManagerProvider` | `ConsentManager` | Consent orchestrator |
| `privacyPolicyRegistryProvider` | `PrivacyPolicyRegistry` | Feature policy registry |
| `privacyManagerProvider` | `PrivacyManager` | Feature-facing orchestrator |

### Barrel Export (`lib/shared/privacy/privacy_engine.dart`)

Import the barrel for convenient access to the full Privacy Engine API:

```dart
import 'package:egohygiene/shared/privacy/privacy_engine.dart';
```

### Usage Example

```dart
// In a feature module — check consent before transmitting data
final permitted = await ref.read(privacyManagerProvider).isFeaturePermitted('ai_chat');
if (!permitted) return; // prompt user for consent first

// Record a consent decision
await ref.read(privacyManagerProvider).grant(ConsentScope.aiProvider);

// Register a feature policy at app startup
ref.read(privacyManagerProvider).registerPolicy(
  const PrivacyPolicy(
    featureId: 'ai_chat',
    displayName: 'AI Conversation',
    requiredConsents: [ConsentScope.aiProvider],
    visibilityRules: [
      DataVisibilityRule(
        dataCategory: 'conversation_content',
        level: VisibilityLevel.sharedWithAiProvider,
      ),
    ],
    retentionRules: [
      DataRetentionRule(
        dataCategory: 'conversation_content',
        policy: RetentionPolicy.deleteAfterDays,
        retentionDays: 90,
      ),
    ],
  ),
);
```

### Future Compatibility

The Privacy Engine is designed to support:

- **Cloud sync consent** — wire `ConsentScope.cloudSync` to the storage sync provider
- **Therapist sharing** — enforce `VisibilityLevel.sharedWithTherapist` in export workflows
- **Institutional deployments** — pre-seed policies and consent via `PrivacyMode.enhanced`
- **Analytics consent** — gate analytics events behind `ConsentScope.analytics`
- **AI provider consent** — gate LLM calls behind `ConsentScope.aiProvider`
- **Persistent consent store** — swap `consentStoreProvider` with `SecureStorageConsentStore`
- **Data export** — collect all `DataVisibilityRule` entries from the registry
- **Data deletion jobs** — evaluate `DataRetentionRule` entries on a schedule

---

## Data Portability Engine

### Overview

The Data Portability Engine gives users full ownership of their data.  It
provides export and import infrastructure so users can back up, inspect, move,
and restore their personal data at any time.

Data portability is a core trust feature of Ego Hygiene.  The engine is
deliberately designed to be format-agnostic and extensible; new export formats
and domain-specific importers can be added without changing the core
orchestrators.

### Architecture

```
DataExportManager      — orchestrator; assembles and renders exports
  └── registered domain exporters (pluggable per-domain collectors)

DataImportManager      — orchestrator; validates and applies imports
  ├── ImportValidator  — validation strategy (pluggable)
  │     └── NoopImportValidator  — default pass-through implementation
  └── registered domain importers (pluggable per-domain appliers)

Domain types:
  ExportFormat         — json / markdown / zip
  ExportManifest       — metadata describing an export (ID, version, domains)
  ExportRecord         — complete self-describing export package
  ImportResult         — validation outcome (success / failure with errors)
```

All files live in `lib/shared/portability/`.

### Core Types

#### `ExportFormat` (`lib/shared/portability/export_format.dart`)

Enum controlling how an [ExportRecord] is encoded.

| Value | Description |
|---|---|
| `json` | Structured machine-readable JSON document |
| `markdown` | Human-readable plain-text document |
| `zip` | Archive bundling JSON + Markdown + binary assets |

Planned future values: `csv`, `pdf`, `encryptedArchive`.

#### `ExportManifest` (`lib/shared/portability/export_manifest.dart`)

Immutable metadata record bundled with every export.  Captures everything
needed to understand, verify, and re-import an export package:

- `exportId` — stable opaque identifier (UUID recommended)
- `format` — [ExportFormat] used to encode the data
- `exportedAt` — when the export was produced
- `schemaVersion` — payload schema version (increment on breaking changes)
- `appVersion` — app semver string at export time
- `domains` — list of data domains included (e.g. `['reflections', 'goals']`)
- `recordCount` — total top-level record count across all domains
- `metadata` — extensible key-value bag (planned: `checksum`, `encryptionKeyId`)

#### `ExportRecord` (`lib/shared/portability/export_record.dart`)

Complete self-describing export package.  Bundles an [ExportManifest] with the
actual domain data as a `Map<String, dynamic>`.

```dart
ExportRecord
  ├── manifest  — ExportManifest
  └── data      — { 'reflections': [...], 'goals': [...], … }
```

Supports `toJson` / `fromJson` for round-trip serialisation.

#### `ImportResult` (`lib/shared/portability/import_result.dart`)

Immutable outcome of a validation run.

```dart
ImportResult.success()
ImportResult.success(warnings: ['locale mismatch'])
ImportResult.failure(errors: ['schema version not supported'])
```

- `isValid` — `true` when validation passed
- `errors` — human-readable failure messages (empty on success)
- `warnings` — non-fatal notices (present on both success and failure)

#### `ImportValidator` (`lib/shared/portability/import_validator.dart`)

Abstract validation interface for incoming import packages.

```dart
abstract class ImportValidator {
  Future<ImportResult> validate(ExportRecord record);
}
```

Planned implementors:
- `NoopImportValidator` — accepts every record (default)
- `SchemaImportValidator` — checks schema version and required fields
- `DomainImportValidator` — applies domain-specific business rules

### `DataExportManager` (`lib/shared/portability/data_export_manager.dart`)

Assembles an [ExportRecord] from registered domain collectors and renders it
in the requested format.

Lifecycle:
```
Application startup
  → DataExportManager.registerDomainExporter('reflections', () async => [...])
  → DataExportManager.registerDomainExporter('goals', () async => [...])

User triggers export
  → DataExportManager.export(format: ExportFormat.json)
    → collect data from all registered exporters
      → assemble ExportManifest
        → return ExportRecord

Render
  → DataExportManager.renderJson(record)    — Map<String, dynamic>
  → DataExportManager.renderMarkdown(record) — String
```

### `DataImportManager` (`lib/shared/portability/data_import_manager.dart`)

Validates and applies an [ExportRecord].

Lifecycle:
```
Application startup
  → DataImportManager.registerDomainImporter('reflections', (data) async { … })

User triggers import
  → DataImportManager.validateAndImport(record)
    → ImportValidator.validate(record)      — check schema, domains, rules
      → if invalid: return ImportResult.failure
    → apply registered domain importers
      → return ImportResult.success
```

### Riverpod Providers (`lib/shared/providers/portability_providers.dart`)

| Provider | Type | Purpose |
|---|---|---|
| `importValidatorProvider` | `ImportValidator` | Active validation strategy |
| `dataExportManagerProvider` | `DataExportManager` | Feature-facing export orchestrator |
| `dataImportManagerProvider` | `DataImportManager` | Feature-facing import orchestrator |

### Barrel Export (`lib/shared/portability/portability_engine.dart`)

Import the barrel for convenient access to the full Portability Engine API:

```dart
import 'package:egohygiene/shared/portability/portability_engine.dart';
```

### Usage Example

```dart
// Register domain exporters at app startup
ref.read(dataExportManagerProvider)
  ..registerDomainExporter('reflections', () async => reflectionRepo.findAll())
  ..registerDomainExporter('goals', () async => goalsRepo.findAll());

// Export as JSON
final record = await ref.read(dataExportManagerProvider)
    .export(format: ExportFormat.json);
final json = ref.read(dataExportManagerProvider).renderJson(record);

// Export as Markdown
final md = ref.read(dataExportManagerProvider).renderMarkdown(record);

// Import with validation
final result = await ref.read(dataImportManagerProvider).validateAndImport(record);
if (!result.isValid) {
  for (final error in result.errors) {
    logger.error(error);
  }
}
```

### Future Compatibility

The Data Portability Engine is designed to support:

- **CSV export** — tabular format for spreadsheet consumers
- **PDF export** — formatted document for printing or sharing
- **Encrypted backup** — end-to-end encrypted archive for cloud restore
- **Full account migration** — import/export across devices or user accounts
- **Therapist handoff packets** — scoped exports filtered by visibility rules
- **Cloud restore** — upload/download via a `BackupService` implementation
- **Schema validators** — real `ImportValidator` implementations that enforce
  schema version ranges and domain-specific rules

---

## Conflict Resolution Engine

### Overview

The Conflict Resolution Engine provides a first-class architecture for
detecting and resolving data conflicts that arise in a local-first sync
system. Conflict handling is modelled explicitly as a domain concern — not
as an afterthought buried inside sync logic — so that user control,
auditability, and reversibility are built into the foundation.

**Design principles:**
- _Safe merges over blind overwrites._
- _User control_ — manual review is always a supported path.
- _Auditability_ — every conflict and outcome is recorded.
- _Reversibility_ — both versions of every conflict are preserved.
- _No silent data loss_ — strategies must account for discarded data.

### Architecture

```
ConflictManager                    — orchestrator; single entry point
  ├── ConflictStore                — persistence abstraction (pluggable)
  │     └── InMemoryConflictStore  — default transient implementation
  └── ConflictResolutionStrategy   — pluggable resolution policy
        ├── KeepLocalStrategy      — auto-resolves to local version
        ├── KeepRemoteStrategy     — auto-resolves to remote version
        ├── RequireManualReviewStrategy — always routes to user (default)
        └── SafeMergeStrategy      — custom merge function

Conflict                           — detected conflict record
ConflictType                       — conflict scenario enum
ConflictResolutionResult           — outcome of resolution
ConflictResolutionOutcome          — outcome classification enum
```

All files live in `lib/shared/conflict/`.

### Core Types

#### `ConflictType` (`lib/shared/conflict/conflict_type.dart`)

Enumerates the common local-first conflict scenarios:

| Value | Description |
|---|---|
| `concurrentEdit` | Same record modified on two devices before sync |
| `localDeleteRemoteUpdate` | Deleted locally, updated remotely |
| `remoteDeleteLocalUpdate` | Deleted remotely, updated locally |
| `duplicateCreation` | Same logical entity created independently on two devices |
| `outOfOrderSync` | Changes arrived in an order inconsistent with their timestamps |
| `schemaMismatch` | Incompatible schema versions between local and remote copy |

#### `Conflict` (`lib/shared/conflict/conflict.dart`)

The core conflict record. Both `localVersion` and `remoteVersion` are
preserved as `Map<String, dynamic>` snapshots for auditability and rollback:

```dart
final conflict = Conflict(
  id: 'conflict-uuid',
  type: ConflictType.concurrentEdit,
  entityType: 'reflection',
  entityId: 'r-123',
  localVersion: {'body': 'local text', 'updatedAt': '...'},
  remoteVersion: {'body': 'remote text', 'updatedAt': '...'},
  detectedAt: DateTime.now(),
);
```

`Conflict` is immutable. Copies are produced with `copyWith`. JSON
round-trip is supported via `toJson` / `fromJson`.

#### `ConflictResolutionOutcome` (`lib/shared/conflict/conflict_resolution_result.dart`)

Classifies the terminal or intermediate state of a conflict:

| Value | Description |
|---|---|
| `resolvedAutomatically` | Resolved by a strategy without user input |
| `pendingReview` | Queued for user review; no version committed yet |
| `resolvedManually` | Resolved by explicit user interaction |
| `deferred` | Acknowledged but postponed for later review |

#### `ConflictResolutionResult` (`lib/shared/conflict/conflict_resolution_result.dart`)

Captures the outcome of applying a strategy to a conflict:

```dart
class ConflictResolutionResult {
  final String conflictId;
  final ConflictResolutionOutcome outcome;
  final Map<String, dynamic>? resolvedVersion; // null when pending
  final DateTime? resolvedAt;
  final String? strategyId;
  final String? notes;
}
```

A result with `pendingReview` outcome has a `null` `resolvedVersion` — no
data is committed until the user makes a decision.

#### `ConflictResolutionStrategy` (`lib/shared/conflict/conflict_resolution_strategy.dart`)

Abstract policy interface:

```dart
abstract class ConflictResolutionStrategy {
  String get strategyId;
  bool get requiresUserReview;
  Future<ConflictResolutionResult> resolve(Conflict conflict);
}
```

Built-in implementations:

| Class | Behaviour |
|---|---|
| `KeepLocalStrategy` | Picks `localVersion`; records remote in conflict for rollback |
| `KeepRemoteStrategy` | Picks `remoteVersion`; records local in conflict for rollback |
| `RequireManualReviewStrategy` | Always returns `pendingReview`; no data committed (default) |
| `SafeMergeStrategy` | Applies a caller-supplied merge function |

#### `ConflictStore` (`lib/shared/conflict/conflict_store.dart`)

Persistence abstraction for conflict records and their resolution results:

Key operations:
- `save(conflict)` — persist or replace a conflict
- `saveResult(result)` — persist a resolution result
- `findPendingReview()` — conflicts awaiting user decision
- `findResolved()` — conflicts with a terminal outcome
- `delete(id)` — remove conflict and result (pruning / clean-up)

#### `InMemoryConflictStore` (`lib/shared/conflict/impl/in_memory_conflict_store.dart`)

Default transient implementation. Replaceable with a Drift-backed store
when persistence is required.

#### `ConflictManager` (`lib/shared/conflict/conflict_manager.dart`)

The single entry point for feature modules and the sync layer.

Key operations:
- `initialize()` — must be called once on startup; no-op thereafter
- `detect(conflict)` — register a conflict and apply the default strategy
- `detectRaw(...)` — convenience builder for `detect`
- `resolveManually(conflictId, resolvedVersion, notes)` — user resolution
- `defer(conflictId)` — postpone a conflict for later review
- `pendingReview()` — list conflicts awaiting user decision
- `resolvedConflicts()` — audit history
- `allConflicts()` — all stored conflicts
- `resultFor(conflictId)` — fetch the result for a specific conflict
- `setDefaultStrategy(strategy)` — change the resolution policy

### Riverpod Providers (`lib/shared/providers/conflict_providers.dart`)

| Provider | Type | Purpose |
|---|---|---|
| `conflictStoreProvider` | `ConflictStore` | Active persistence backend |
| `conflictStrategyProvider` | `ConflictResolutionStrategy` | Default resolution policy |
| `conflictManagerProvider` | `ConflictManager` | Feature-facing orchestrator |

### Barrel Export (`lib/shared/conflict/conflict_engine.dart`)

```dart
import 'package:egohygiene/shared/conflict/conflict_engine.dart';
```

### Future Compatibility

The Conflict Resolution Engine is prepared for:

- **Encrypted sync** — conflict records carry `metadata` for vector clocks,
  device IDs, and provider diagnostics; encryption layers attach at the
  store boundary.
- **Multi-device support** — `ConflictType.concurrentEdit` and
  `outOfOrderSync` model the primary multi-device scenarios.
- **Therapist sharing** — `RequireManualReviewStrategy` ensures therapist-
  shared data is never silently overwritten; `resolveManually` supports
  collaborative review workflows.
- **Collaborative workflows** — `SafeMergeStrategy` is the extension point
  for CRDT and field-level merge algorithms.
- **Backup restore conflicts** — `ConflictType.schemaMismatch` and
  `remoteDeleteLocalUpdate` cover restore-from-backup edge cases.
