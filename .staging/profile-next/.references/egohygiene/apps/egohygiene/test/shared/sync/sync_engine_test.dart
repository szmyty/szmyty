import 'package:egohygiene/shared/providers/sync_providers.dart';
import 'package:egohygiene/shared/sync/impl/in_memory_sync_queue.dart';
import 'package:egohygiene/shared/sync/sync_checkpoint.dart';
import 'package:egohygiene/shared/sync/sync_manager.dart';
import 'package:egohygiene/shared/sync/sync_operation.dart';
import 'package:egohygiene/shared/sync/sync_provider.dart';
import 'package:egohygiene/shared/sync/sync_status.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

SyncOperation _operation({
  String id = 'op-1',
  String entityType = 'reflection',
  String entityId = 'entity-1',
  SyncOperationType type = SyncOperationType.upsert,
  DateTime? createdAt,
  int priority = 0,
  Map<String, dynamic>? payload,
  int attemptCount = 0,
  DateTime? lastAttemptAt,
}) {
  return SyncOperation(
    id: id,
    entityType: entityType,
    entityId: entityId,
    type: type,
    createdAt: createdAt ?? DateTime.utc(2026, 7, 1, 10),
    priority: priority,
    payload: payload,
    attemptCount: attemptCount,
    lastAttemptAt: lastAttemptAt,
  );
}

class _FakeSyncProvider implements SyncProvider {
  _FakeSyncProvider({
    required this.providerId,
    this.available = true,
    SyncStatus? syncResult,
    this.checkpoint,
  }) : syncResult =
           syncResult ??
           SyncStatus.succeeded(
             lastSyncAt: DateTime.utc(2026, 7, 1, 12),
           );

  @override
  final String providerId;

  bool available;
  SyncStatus syncResult;
  SyncCheckpoint? checkpoint;

  int syncCallCount = 0;
  List<SyncOperation> syncedOperations = const [];
  SyncCheckpoint? receivedCheckpoint;
  SyncCheckpoint? savedCheckpoint;

  @override
  Future<bool> get isAvailable async => available;

  @override
  Future<SyncCheckpoint?> loadCheckpoint() async => checkpoint;

  @override
  Future<void> saveCheckpoint(SyncCheckpoint checkpoint) async {
    savedCheckpoint = checkpoint;
    this.checkpoint = checkpoint;
  }

  @override
  Future<SyncStatus> sync({
    required List<SyncOperation> operations,
    SyncCheckpoint? checkpoint,
  }) async {
    syncCallCount++;
    syncedOperations = List<SyncOperation>.of(operations);
    receivedCheckpoint = checkpoint;
    return syncResult;
  }

  @override
  Future<SyncStatus> pull(SyncCheckpoint? checkpoint) async => syncResult;

  @override
  Future<SyncStatus> push(List<SyncOperation> operations) async => syncResult;
}

void main() {
  group('SyncCheckpoint', () {
    test('toJson/fromJson round-trips', () {
      final checkpoint = SyncCheckpoint(
        providerId: 'icloud',
        scope: 'reflections',
        syncedAt: DateTime.utc(2026, 7, 1, 12),
        cursor: 'cursor-123',
        metadata: const {'device': 'ios'},
      );

      final restored = SyncCheckpoint.fromJson(checkpoint.toJson());

      expect(restored.providerId, checkpoint.providerId);
      expect(restored.scope, checkpoint.scope);
      expect(restored.syncedAt, checkpoint.syncedAt);
      expect(restored.cursor, checkpoint.cursor);
      expect(restored.metadata, checkpoint.metadata);
    });
  });

  group('SyncOperation', () {
    test('copyWith replaces specified fields', () {
      final updated = _operation().copyWith(
        priority: 3,
        attemptCount: 2,
        payload: const {'body': 'updated'},
      );

      expect(updated.priority, 3);
      expect(updated.attemptCount, 2);
      expect(updated.payload, {'body': 'updated'});
    });

    test('toJson/fromJson round-trips', () {
      final operation = _operation(
        priority: 2,
        payload: const {'title': 'Journal entry'},
        lastAttemptAt: DateTime.utc(2026, 7, 1, 11),
      );

      final restored = SyncOperation.fromJson(operation.toJson());

      expect(restored.id, operation.id);
      expect(restored.entityType, operation.entityType);
      expect(restored.entityId, operation.entityId);
      expect(restored.type, operation.type);
      expect(restored.priority, operation.priority);
      expect(restored.payload, operation.payload);
      expect(restored.lastAttemptAt, operation.lastAttemptAt);
    });
  });

  group('SyncStatus', () {
    test('represents queued work', () {
      final status = SyncStatus.queued(
        pendingOperations: 3,
        automaticSyncEnabled: true,
        activeProviderId: 'icloud',
      );

      expect(status.phase, SyncPhase.queued);
      expect(status.pendingOperations, 3);
      expect(status.automaticSyncEnabled, isTrue);
      expect(status.activeProviderId, 'icloud');
      expect(status.isSuccess, isFalse);
    });

    test('represents successful sync results', () {
      final status = SyncStatus.succeeded(
        pushedCount: 2,
        pulledCount: 1,
        conflictsResolved: 1,
      );

      expect(status.phase, SyncPhase.succeeded);
      expect(status.isSuccess, isTrue);
      expect(status.pushedCount, 2);
      expect(status.pulledCount, 1);
      expect(status.conflictsResolved, 1);
    });
  });

  group('InMemorySyncQueue', () {
    late InMemorySyncQueue queue;

    setUp(() async {
      queue = InMemorySyncQueue();
      await queue.init();
    });

    test('orders higher priority first, then older operations', () async {
      await queue.enqueueAll([
        _operation(
          id: 'old-low',
          createdAt: DateTime.utc(2026, 7, 1, 8),
        ),
        _operation(
          id: 'new-high',
          priority: 2,
          createdAt: DateTime.utc(2026, 7, 1, 10),
        ),
        _operation(
          id: 'old-high',
          priority: 2,
          createdAt: DateTime.utc(2026, 7, 1, 7),
        ),
      ]);

      final operations = await queue.peekAll();

      expect(operations.map((operation) => operation.id), [
        'old-high',
        'new-high',
        'old-low',
      ]);
    });

    test('dequeue removes the next operation', () async {
      await queue.enqueue(_operation(id: 'first'));
      await queue.enqueue(_operation(id: 'second', priority: 1));

      final first = await queue.dequeue();

      expect(first!.id, 'second');
      expect(await queue.count(), 1);
      expect((await queue.peek())!.id, 'first');
    });
  });

  group('SyncManager', () {
    test('defaults to local-first disabled sync when no provider exists', () async {
      final manager = SyncManager(queue: InMemorySyncQueue());

      await manager.initialize();
      final status = await manager.syncNow();

      expect(status.phase, SyncPhase.disabled);
      expect(status.pendingOperations, 0);
    });

    test('reports offline when provider is unavailable', () async {
      final provider = _FakeSyncProvider(
        providerId: 'drive',
        available: false,
      );
      final manager = SyncManager(
        queue: InMemorySyncQueue(),
        provider: provider,
      );

      await manager.initialize();
      await manager.enqueue(_operation());
      final status = await manager.syncNow();

      expect(status.phase, SyncPhase.offline);
      expect(status.pendingOperations, 1);
      expect(provider.syncCallCount, 0);
    });

    test('syncs queued operations and saves checkpoint on success', () async {
      final provider = _FakeSyncProvider(
        providerId: 'icloud',
        checkpoint: SyncCheckpoint(
          providerId: 'icloud',
          syncedAt: DateTime.utc(2026, 7, 1, 9),
          cursor: 'old-cursor',
        ),
        syncResult: SyncStatus.succeeded(
          pushedCount: 2,
          pulledCount: 1,
          checkpoint: SyncCheckpoint(
            providerId: 'icloud',
            syncedAt: DateTime.utc(2026, 7, 1, 12),
            cursor: 'new-cursor',
          ),
          lastSyncAt: DateTime.utc(2026, 7, 1, 12),
        ),
      );
      final manager = SyncManager(
        queue: InMemorySyncQueue(),
        provider: provider,
      );

      await manager.initialize();
      await manager.enqueueAll([
        _operation(),
        _operation(id: 'op-2', entityId: 'entity-2'),
      ]);

      final status = await manager.syncNow();

      expect(status.phase, SyncPhase.succeeded);
      expect(status.pendingOperations, 0);
      expect(status.pushedCount, 2);
      expect(status.pulledCount, 1);
      expect(provider.syncCallCount, 1);
      expect(provider.syncedOperations, hasLength(2));
      expect(provider.receivedCheckpoint!.cursor, 'old-cursor');
      expect(provider.savedCheckpoint!.cursor, 'new-cursor');
      expect(await manager.pendingOperations(), isEmpty);
    });

    test('stores automatic sync configuration for future schedulers', () async {
      final manager = SyncManager(queue: InMemorySyncQueue());

      manager.configureAutomaticSync(
        enabled: true,
        interval: const Duration(minutes: 30),
      );

      expect(manager.automaticSyncEnabled, isTrue);
      expect(manager.automaticSyncInterval, const Duration(minutes: 30));
    });
  });

  group('sync providers', () {
    test('wires queue and provider overrides', () async {
      final queue = InMemorySyncQueue();
      final provider = _FakeSyncProvider(providerId: 'drive');
      final container = ProviderContainer(
        overrides: [
          syncQueueProvider.overrideWithValue(queue),
          syncProviderProvider.overrideWithValue(provider),
        ],
      );
      addTearDown(container.dispose);

      final manager = container.read(syncManagerProvider);
      await manager.initialize();

      expect(manager.status.phase, SyncPhase.idle);
      expect(manager.status.activeProviderId, 'drive');
      expect(container.read(syncQueueProvider), same(queue));
      expect(container.read(syncProviderProvider), same(provider));
    });
  });
}
