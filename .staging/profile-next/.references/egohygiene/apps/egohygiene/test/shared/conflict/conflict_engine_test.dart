import 'package:egohygiene/shared/conflict/conflict_engine.dart';
import 'package:egohygiene/shared/providers/conflict_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

Conflict _conflict({
  String id = 'conflict-1',
  ConflictType type = ConflictType.concurrentEdit,
  String entityType = 'reflection',
  String entityId = 'entity-1',
  Map<String, dynamic>? localVersion,
  Map<String, dynamic>? remoteVersion,
  DateTime? detectedAt,
  Map<String, Object?>? metadata,
}) {
  return Conflict(
    id: id,
    type: type,
    entityType: entityType,
    entityId: entityId,
    localVersion: localVersion ?? const {'body': 'local text'},
    remoteVersion: remoteVersion ?? const {'body': 'remote text'},
    detectedAt: detectedAt ?? DateTime.utc(2026, 7, 1, 10),
    metadata: metadata ?? const {},
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── ConflictType ───────────────────────────────────────────────────────────

  group('ConflictType', () {
    test('has six types', () {
      expect(ConflictType.values, hasLength(6));
    });

    test('contains all expected types', () {
      expect(
        ConflictType.values,
        containsAll([
          ConflictType.concurrentEdit,
          ConflictType.localDeleteRemoteUpdate,
          ConflictType.remoteDeleteLocalUpdate,
          ConflictType.duplicateCreation,
          ConflictType.outOfOrderSync,
          ConflictType.schemaMismatch,
        ]),
      );
    });
  });

  // ── Conflict ───────────────────────────────────────────────────────────────

  group('Conflict', () {
    test('copyWith replaces specified fields', () {
      final updated = _conflict().copyWith(
        type: ConflictType.duplicateCreation,
        entityType: 'goal',
      );

      expect(updated.type, ConflictType.duplicateCreation);
      expect(updated.entityType, 'goal');
      expect(updated.id, 'conflict-1');
    });

    test('toJson/fromJson round-trips', () {
      final conflict = _conflict(
        metadata: const {'deviceId': 'phone-a', 'schemaVersion': 3},
      );

      final restored = Conflict.fromJson(conflict.toJson());

      expect(restored.id, conflict.id);
      expect(restored.type, conflict.type);
      expect(restored.entityType, conflict.entityType);
      expect(restored.entityId, conflict.entityId);
      expect(restored.localVersion, conflict.localVersion);
      expect(restored.remoteVersion, conflict.remoteVersion);
      expect(restored.detectedAt, conflict.detectedAt);
      expect(restored.metadata, conflict.metadata);
    });

    test('equality is based on id', () {
      final a = _conflict();
      final b = _conflict(entityType: 'goal');
      final c = _conflict(id: 'conflict-2');

      expect(a, equals(b));
      expect(a, isNot(equals(c)));
    });
  });

  // ── ConflictResolutionResult ───────────────────────────────────────────────

  group('ConflictResolutionResult', () {
    test('isResolved is true for automatic and manual outcomes', () {
      expect(
        const ConflictResolutionResult(
          conflictId: 'c-1',
          outcome: ConflictResolutionOutcome.resolvedAutomatically,
        ).isResolved,
        isTrue,
      );
      expect(
        const ConflictResolutionResult(
          conflictId: 'c-1',
          outcome: ConflictResolutionOutcome.resolvedManually,
        ).isResolved,
        isTrue,
      );
    });

    test('isPendingReview is true only for pendingReview outcome', () {
      expect(
        const ConflictResolutionResult(
          conflictId: 'c-1',
          outcome: ConflictResolutionOutcome.pendingReview,
        ).isPendingReview,
        isTrue,
      );
      expect(
        const ConflictResolutionResult(
          conflictId: 'c-1',
          outcome: ConflictResolutionOutcome.resolvedAutomatically,
        ).isPendingReview,
        isFalse,
      );
    });

    test('toJson/fromJson round-trips', () {
      final result = ConflictResolutionResult(
        conflictId: 'conflict-1',
        outcome: ConflictResolutionOutcome.resolvedAutomatically,
        resolvedVersion: const {'body': 'local text'},
        resolvedAt: DateTime.utc(2026, 7, 1, 12),
        strategyId: 'keep_local',
        notes: 'Local version kept.',
      );

      final restored = ConflictResolutionResult.fromJson(result.toJson());

      expect(restored.conflictId, result.conflictId);
      expect(restored.outcome, result.outcome);
      expect(restored.resolvedVersion, result.resolvedVersion);
      expect(restored.resolvedAt, result.resolvedAt);
      expect(restored.strategyId, result.strategyId);
      expect(restored.notes, result.notes);
    });

    test('pending result has null resolvedVersion and resolvedAt', () {
      const result = ConflictResolutionResult(
        conflictId: 'conflict-1',
        outcome: ConflictResolutionOutcome.pendingReview,
      );

      expect(result.resolvedVersion, isNull);
      expect(result.resolvedAt, isNull);
    });
  });

  // ── ConflictResolutionStrategy ─────────────────────────────────────────────

  group('KeepLocalStrategy', () {
    test('resolves to local version automatically', () async {
      const strategy = KeepLocalStrategy();
      final conflict = _conflict();

      final result = await strategy.resolve(conflict);

      expect(result.outcome, ConflictResolutionOutcome.resolvedAutomatically);
      expect(result.resolvedVersion, conflict.localVersion);
      expect(result.strategyId, 'keep_local');
      expect(strategy.requiresUserReview, isFalse);
    });
  });

  group('KeepRemoteStrategy', () {
    test('resolves to remote version automatically', () async {
      const strategy = KeepRemoteStrategy();
      final conflict = _conflict();

      final result = await strategy.resolve(conflict);

      expect(result.outcome, ConflictResolutionOutcome.resolvedAutomatically);
      expect(result.resolvedVersion, conflict.remoteVersion);
      expect(result.strategyId, 'keep_remote');
      expect(strategy.requiresUserReview, isFalse);
    });
  });

  group('RequireManualReviewStrategy', () {
    test('routes conflict to pending review without choosing a version', () async {
      const strategy = RequireManualReviewStrategy();
      final conflict = _conflict();

      final result = await strategy.resolve(conflict);

      expect(result.outcome, ConflictResolutionOutcome.pendingReview);
      expect(result.resolvedVersion, isNull);
      expect(result.strategyId, 'require_manual_review');
      expect(strategy.requiresUserReview, isTrue);
    });
  });

  group('SafeMergeStrategy', () {
    test('applies custom merge function', () async {
      final strategy = SafeMergeStrategy(
        id: 'combine_fields',
        merge: (conflict) => {
          ...conflict.localVersion,
          ...conflict.remoteVersion,
        },
      );
      final conflict = _conflict(
        localVersion: const {'title': 'local title', 'body': 'local body'},
        remoteVersion: const {
          'body': 'remote body',
          'tags': ['a'],
        },
      );

      final result = await strategy.resolve(conflict);

      expect(result.outcome, ConflictResolutionOutcome.resolvedAutomatically);
      expect(result.resolvedVersion!['title'], 'local title');
      expect(result.resolvedVersion!['body'], 'remote body');
      expect(result.resolvedVersion!['tags'], ['a']);
      expect(result.strategyId, 'combine_fields');
    });
  });

  // ── InMemoryConflictStore ──────────────────────────────────────────────────

  group('InMemoryConflictStore', () {
    late InMemoryConflictStore store;

    setUp(() async {
      store = InMemoryConflictStore();
      await store.init();
    });

    test('saves and retrieves a conflict by id', () async {
      final conflict = _conflict();
      await store.save(conflict);

      final found = await store.findById('conflict-1');
      expect(found, conflict);
    });

    test('replaces existing conflict on save with same id', () async {
      await store.save(_conflict());
      await store.save(_conflict(entityType: 'goal'));

      final found = await store.findById('conflict-1');
      expect(found!.entityType, 'goal');
      expect(await store.count(), 1);
    });

    test('returns null for unknown id', () async {
      expect(await store.findById('unknown'), isNull);
    });

    test('findAll returns conflicts ordered by detectedAt', () async {
      await store.save(
        _conflict(
          id: 'c-2',
          detectedAt: DateTime.utc(2026, 7, 1, 11),
        ),
      );
      await store.save(
        _conflict(
          id: 'c-1',
          detectedAt: DateTime.utc(2026, 7, 1, 10),
        ),
      );

      final all = await store.findAll();
      expect(all.map((c) => c.id), ['c-1', 'c-2']);
    });

    test('findByEntityType filters correctly', () async {
      await store.save(_conflict(id: 'c-1'));
      await store.save(_conflict(id: 'c-2', entityType: 'goal'));

      final results = await store.findByEntityType('reflection');
      expect(results, hasLength(1));
      expect(results.first.id, 'c-1');
    });

    test('findByEntityId filters correctly', () async {
      await store.save(_conflict(id: 'c-1'));
      await store.save(_conflict(id: 'c-2', entityId: 'entity-2'));

      final results = await store.findByEntityId('entity-1');
      expect(results, hasLength(1));
      expect(results.first.id, 'c-1');
    });

    test('findPendingReview returns conflicts with no result', () async {
      await store.save(_conflict(id: 'c-1'));
      await store.save(_conflict(id: 'c-2'));
      await store.saveResult(
        ConflictResolutionResult(
          conflictId: 'c-2',
          outcome: ConflictResolutionOutcome.resolvedAutomatically,
          resolvedVersion: const {'body': 'local'},
          resolvedAt: DateTime.utc(2026, 7, 1, 12),
        ),
      );

      final pending = await store.findPendingReview();
      expect(pending.map((c) => c.id), ['c-1']);
    });

    test('findPendingReview includes pendingReview-outcome results', () async {
      await store.save(_conflict(id: 'c-1'));
      await store.saveResult(
        const ConflictResolutionResult(
          conflictId: 'c-1',
          outcome: ConflictResolutionOutcome.pendingReview,
        ),
      );

      final pending = await store.findPendingReview();
      expect(pending, hasLength(1));
    });

    test('findResolved returns only fully resolved conflicts', () async {
      await store.save(_conflict(id: 'c-1'));
      await store.save(_conflict(id: 'c-2'));
      await store.saveResult(
        ConflictResolutionResult(
          conflictId: 'c-1',
          outcome: ConflictResolutionOutcome.resolvedManually,
          resolvedVersion: const {'body': 'merged'},
          resolvedAt: DateTime.utc(2026, 7, 1, 12),
        ),
      );

      final resolved = await store.findResolved();
      expect(resolved.map((c) => c.id), ['c-1']);
    });

    test('delete removes conflict and result', () async {
      await store.save(_conflict());
      await store.saveResult(
        const ConflictResolutionResult(
          conflictId: 'conflict-1',
          outcome: ConflictResolutionOutcome.resolvedManually,
          resolvedVersion: {'body': 'merged'},
        ),
      );

      await store.delete('conflict-1');

      expect(await store.count(), 0);
      expect(await store.findResult('conflict-1'), isNull);
    });

    test('pendingReviewCount matches findPendingReview length', () async {
      await store.save(_conflict(id: 'c-1'));
      await store.save(_conflict(id: 'c-2'));

      expect(await store.pendingReviewCount(), 2);
    });
  });

  // ── ConflictManager ────────────────────────────────────────────────────────

  group('ConflictManager', () {
    late ConflictManager manager;

    setUp(() async {
      manager = ConflictManager(store: InMemoryConflictStore());
      await manager.initialize();
    });

    test('defaults to RequireManualReviewStrategy', () {
      expect(
        manager.defaultStrategy,
        isA<RequireManualReviewStrategy>(),
      );
    });

    test('detect stores conflict and applies default strategy', () async {
      final conflict = _conflict();

      final result = await manager.detect(conflict);

      expect(result.outcome, ConflictResolutionOutcome.pendingReview);
      expect(await manager.conflictCount, 1);
      expect(await manager.pendingReviewCount, 1);
    });

    test('detect with KeepLocalStrategy resolves automatically', () async {
      manager.setDefaultStrategy(const KeepLocalStrategy());
      final conflict = _conflict();

      final result = await manager.detect(conflict);

      expect(result.outcome, ConflictResolutionOutcome.resolvedAutomatically);
      expect(result.resolvedVersion, conflict.localVersion);
      expect(await manager.pendingReviewCount, 0);
    });

    test('detect with KeepRemoteStrategy resolves to remote', () async {
      manager.setDefaultStrategy(const KeepRemoteStrategy());
      final conflict = _conflict();

      final result = await manager.detect(conflict);

      expect(result.outcome, ConflictResolutionOutcome.resolvedAutomatically);
      expect(result.resolvedVersion, conflict.remoteVersion);
    });

    test('detectRaw convenience method builds and detects conflict', () async {
      final result = await manager.detectRaw(
        id: 'raw-1',
        type: ConflictType.outOfOrderSync,
        entityType: 'check_in',
        entityId: 'ci-99',
        localVersion: const {'mood': 7},
        remoteVersion: const {'mood': 6},
        detectedAt: DateTime.utc(2026, 7, 1, 14),
      );

      expect(result.conflictId, 'raw-1');
      expect(await manager.conflictCount, 1);
    });

    test('resolveManually commits user decision', () async {
      await manager.detect(_conflict());

      final resolution = await manager.resolveManually(
        conflictId: 'conflict-1',
        resolvedVersion: const {'body': 'user chose this'},
        notes: 'I prefer the local version with a small tweak.',
      );

      expect(resolution.outcome, ConflictResolutionOutcome.resolvedManually);
      expect(resolution.resolvedVersion, {'body': 'user chose this'});
      expect(resolution.strategyId, 'manual');
      expect(resolution.notes, isNotNull);
      expect(await manager.pendingReviewCount, 0);
    });

    test('resolveManually throws StateError for unknown conflictId', () async {
      expect(
        () => manager.resolveManually(
          conflictId: 'does-not-exist',
          resolvedVersion: const {},
        ),
        throwsStateError,
      );
    });

    test('defer moves conflict to deferred state', () async {
      await manager.detect(_conflict());

      final result = await manager.defer(conflictId: 'conflict-1');

      expect(result.outcome, ConflictResolutionOutcome.deferred);
      // Deferred conflicts still appear in pending review
      expect(await manager.pendingReviewCount, 1);
    });

    test('defer throws StateError for unknown conflictId', () async {
      expect(
        () => manager.defer(conflictId: 'does-not-exist'),
        throwsStateError,
      );
    });

    test('pendingReview returns unresolved conflicts only', () async {
      await manager.detect(_conflict(id: 'c-1'));
      await manager.detect(_conflict(id: 'c-2'));
      await manager.resolveManually(
        conflictId: 'c-1',
        resolvedVersion: const {'body': 'resolved'},
      );

      final pending = await manager.pendingReview();
      expect(pending.map((c) => c.id), ['c-2']);
    });

    test('resolvedConflicts returns only resolved conflicts', () async {
      await manager.detect(_conflict(id: 'c-1'));
      await manager.detect(_conflict(id: 'c-2'));
      await manager.resolveManually(
        conflictId: 'c-1',
        resolvedVersion: const {'body': 'merged'},
      );

      final resolved = await manager.resolvedConflicts();
      expect(resolved.map((c) => c.id), ['c-1']);
    });

    test('allConflicts returns both resolved and unresolved', () async {
      await manager.detect(_conflict(id: 'c-1'));
      await manager.detect(_conflict(id: 'c-2'));
      await manager.resolveManually(
        conflictId: 'c-1',
        resolvedVersion: const {'body': 'merged'},
      );

      final all = await manager.allConflicts();
      expect(all, hasLength(2));
    });

    test('conflictsForEntityType filters by entity type', () async {
      await manager.detectRaw(
        id: 'c-1',
        type: ConflictType.concurrentEdit,
        entityType: 'reflection',
        entityId: 'r-1',
        localVersion: const {},
        remoteVersion: const {},
      );
      await manager.detectRaw(
        id: 'c-2',
        type: ConflictType.concurrentEdit,
        entityType: 'goal',
        entityId: 'g-1',
        localVersion: const {},
        remoteVersion: const {},
      );

      final reflections = await manager.conflictsForEntityType('reflection');
      expect(reflections, hasLength(1));
      expect(reflections.first.entityType, 'reflection');
    });

    test('resultFor returns resolution result for conflictId', () async {
      await manager.detect(_conflict());

      final result = await manager.resultFor('conflict-1');
      expect(result, isNotNull);
      expect(result!.outcome, ConflictResolutionOutcome.pendingReview);
    });

    test('setDefaultStrategy affects subsequent detect calls', () async {
      await manager.detect(_conflict(id: 'c-before'));
      manager.setDefaultStrategy(const KeepLocalStrategy());
      await manager.detect(_conflict(id: 'c-after'));

      final beforeResult = await manager.resultFor('c-before');
      final afterResult = await manager.resultFor('c-after');

      expect(beforeResult!.outcome, ConflictResolutionOutcome.pendingReview);
      expect(
        afterResult!.outcome,
        ConflictResolutionOutcome.resolvedAutomatically,
      );
    });

    test('initialize is idempotent', () async {
      await manager.initialize();
      await manager.initialize();
      expect(await manager.conflictCount, 0);
    });
  });

  // ── Riverpod providers ─────────────────────────────────────────────────────

  group('conflict providers', () {
    test('conflictManagerProvider wires store and strategy', () async {
      final store = InMemoryConflictStore();
      final container = ProviderContainer(
        overrides: [
          conflictStoreProvider.overrideWithValue(store),
          conflictStrategyProvider.overrideWithValue(const KeepLocalStrategy()),
        ],
      );
      addTearDown(container.dispose);

      final manager = container.read(conflictManagerProvider);
      await manager.initialize();

      expect(manager.defaultStrategy, isA<KeepLocalStrategy>());
      expect(container.read(conflictStoreProvider), same(store));
    });

    test('default strategy is RequireManualReviewStrategy', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final strategy = container.read(conflictStrategyProvider);
      expect(strategy, isA<RequireManualReviewStrategy>());
    });
  });
}
