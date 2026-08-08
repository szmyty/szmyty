import 'package:egohygiene/shared/memory/impl/in_memory_memory_store.dart';
import 'package:egohygiene/shared/memory/memory.dart';
import 'package:egohygiene/shared/memory/memory_manager.dart';
import 'package:egohygiene/shared/memory/memory_snapshot.dart';
import 'package:egohygiene/shared/memory/memory_source.dart';
import 'package:egohygiene/shared/memory/memory_store.dart';
import 'package:egohygiene/shared/memory/memory_type.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

Memory _memory({
  String id = 'mem-1',
  MemoryType type = MemoryType.episodic,
  String content = 'Test memory content',
  String? source,
  List<String> tags = const [],
  double confidence = 1.0,
  DateTime? createdAt,
  DateTime? updatedAt,
}) {
  final now = DateTime(2025);
  return Memory(
    id: id,
    type: type,
    content: content,
    source: source,
    tags: tags,
    confidence: confidence,
    createdAt: createdAt ?? now,
    updatedAt: updatedAt ?? now,
  );
}

/// A [MemorySource] that returns a fixed list of memories when extracted.
class _FixedMemorySource implements MemorySource {
  _FixedMemorySource({
    required this.sourceId,
    Set<MemoryType>? supportedTypes,
    this._memories = const [],
    this.throwOnExtract = false,
  }) : displayName = 'Fixed Source',
       supportedTypes = supportedTypes ?? MemoryType.values.toSet();

  @override
  final String sourceId;

  @override
  final String displayName;

  @override
  final Set<MemoryType> supportedTypes;

  final List<Memory> _memories;
  final bool throwOnExtract;

  bool initialized = false;
  bool disposed = false;
  int extractCallCount = 0;

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<List<Memory>> extractMemories(Map<String, Object?> context) async {
    extractCallCount++;
    if (throwOnExtract) throw Exception('source failure');
    return _memories;
  }

  @override
  Future<void> dispose() async => disposed = true;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── MemoryType ─────────────────────────────────────────────────────────────

  group('MemoryType', () {
    test('has five types', () {
      expect(MemoryType.values, hasLength(5));
    });

    test('contains all expected types', () {
      expect(
        MemoryType.values,
        containsAll([
          MemoryType.episodic,
          MemoryType.semantic,
          MemoryType.preference,
          MemoryType.journey,
          MemoryType.relationship,
        ]),
      );
    });
  });

  // ── Memory ─────────────────────────────────────────────────────────────────

  group('Memory', () {
    test('constructs with required fields', () {
      final m = _memory();
      expect(m.id, 'mem-1');
      expect(m.type, MemoryType.episodic);
      expect(m.content, 'Test memory content');
      expect(m.confidence, 1.0);
      expect(m.tags, isEmpty);
      expect(m.metadata, isEmpty);
    });

    test('copyWith replaces specified fields', () {
      final original = _memory(id: 'orig', content: 'original');
      final updated = original.copyWith(content: 'updated', confidence: 0.5);
      expect(updated.id, 'orig');
      expect(updated.content, 'updated');
      expect(updated.confidence, 0.5);
    });

    test('equality is based on id and type', () {
      final a = _memory(id: 'x', type: MemoryType.semantic);
      final b = _memory(id: 'x', type: MemoryType.semantic, content: 'different');
      expect(a, equals(b));
    });

    test('different id produces different identity', () {
      final a = _memory(id: 'a');
      final b = _memory(id: 'b');
      expect(a, isNot(equals(b)));
    });

    test('toString includes id, type, and source', () {
      final m = _memory(id: 'abc', source: 'reflection');
      expect(m.toString(), contains('abc'));
      expect(m.toString(), contains('episodic'));
      expect(m.toString(), contains('reflection'));
    });
  });

  // ── InMemoryMemoryStore ────────────────────────────────────────────────────

  group('InMemoryMemoryStore', () {
    late InMemoryMemoryStore store;

    setUp(() async {
      store = InMemoryMemoryStore();
      await store.init();
    });

    test('init() completes without error', () async {
      await expectLater(store.init(), completes);
    });

    test('starts empty', () async {
      expect(await store.count(), 0);
      expect(await store.findAll(), isEmpty);
    });

    test('save() persists a memory', () async {
      final m = _memory();
      await store.save(m);
      expect(await store.count(), 1);
    });

    test('findById() returns the saved memory', () async {
      final m = _memory(id: 'find-me');
      await store.save(m);
      final result = await store.findById('find-me');
      expect(result, equals(m));
    });

    test('findById() returns null for unknown id', () async {
      expect(await store.findById('ghost'), isNull);
    });

    test('save() replaces existing memory with same id', () async {
      final original = _memory(id: 'dup', content: 'first');
      final replacement = _memory(id: 'dup', content: 'second');
      await store.save(original);
      await store.save(replacement);
      expect(await store.count(), 1);
      final result = await store.findById('dup');
      expect(result!.content, 'second');
    });

    test('findAll() returns memories ordered by createdAt ascending', () async {
      final t1 = DateTime(2025);
      final t2 = DateTime(2025, 1, 2);
      final t3 = DateTime(2025, 1, 3);

      await store.save(_memory(id: 'c', createdAt: t3, updatedAt: t3));
      await store.save(_memory(id: 'a', createdAt: t1, updatedAt: t1));
      await store.save(_memory(id: 'b', createdAt: t2, updatedAt: t2));

      final all = await store.findAll();
      expect(all.map((m) => m.id), ['a', 'b', 'c']);
    });

    test('findByType() returns only matching memories', () async {
      await store.save(_memory(id: '1'));
      await store.save(_memory(id: '2', type: MemoryType.semantic));
      await store.save(_memory(id: '3'));

      final episodic = await store.findByType(MemoryType.episodic);
      expect(episodic, hasLength(2));
      expect(episodic.every((m) => m.type == MemoryType.episodic), isTrue);
    });

    test('findByTag() returns only tagged memories', () async {
      await store.save(_memory(id: '1', tags: ['growth', 'core']));
      await store.save(_memory(id: '2', tags: ['core']));
      await store.save(_memory(id: '3', tags: ['other']));

      final coreMemories = await store.findByTag('core');
      expect(coreMemories, hasLength(2));
    });

    test('findBySource() returns only memories from given source', () async {
      await store.save(_memory(id: '1', source: 'reflection'));
      await store.save(_memory(id: '2', source: 'conversation'));
      await store.save(_memory(id: '3', source: 'reflection'));

      final reflectionMemories = await store.findBySource('reflection');
      expect(reflectionMemories, hasLength(2));
    });

    test('saveAll() persists multiple memories', () async {
      final memories = [
        _memory(id: 'a'),
        _memory(id: 'b'),
        _memory(id: 'c'),
      ];
      await store.saveAll(memories);
      expect(await store.count(), 3);
    });

    test('deleteById() removes the memory', () async {
      await store.save(_memory(id: 'del-me'));
      await store.deleteById('del-me');
      expect(await store.findById('del-me'), isNull);
      expect(await store.count(), 0);
    });

    test('deleteById() is a no-op for unknown id', () async {
      await expectLater(store.deleteById('ghost'), completes);
    });

    test('clear() removes all memories', () async {
      await store.saveAll([_memory(id: 'a'), _memory(id: 'b')]);
      await store.clear();
      expect(await store.count(), 0);
    });
  });

  // ── MemorySnapshot ─────────────────────────────────────────────────────────

  group('MemorySnapshot', () {
    test('empty() produces a snapshot with no memories', () {
      final snap = MemorySnapshot.empty();
      expect(snap.isEmpty, isTrue);
      expect(snap.size, 0);
    });

    test('isNotEmpty is true when memories present', () {
      final snap = MemorySnapshot(
        memories: [_memory()],
        capturedAt: DateTime.now(),
      );
      expect(snap.isNotEmpty, isTrue);
    });

    test('ofType() filters by MemoryType', () {
      final snap = MemorySnapshot(
        memories: [
          _memory(id: '1'),
          _memory(id: '2', type: MemoryType.semantic),
        ],
        capturedAt: DateTime.now(),
      );
      expect(snap.ofType(MemoryType.episodic), hasLength(1));
    });

    test('withTag() filters by tag', () {
      final snap = MemorySnapshot(
        memories: [
          _memory(id: '1', tags: ['core']),
          _memory(id: '2', tags: ['other']),
        ],
        capturedAt: DateTime.now(),
      );
      expect(snap.withTag('core'), hasLength(1));
    });

    test('fromSource() filters by source', () {
      final snap = MemorySnapshot(
        memories: [
          _memory(id: '1', source: 'reflection'),
          _memory(id: '2', source: 'conversation'),
        ],
        capturedAt: DateTime.now(),
      );
      expect(snap.fromSource('reflection'), hasLength(1));
    });

    test('byConfidence returns memories sorted highest first', () {
      final snap = MemorySnapshot(
        memories: [
          _memory(id: 'low', confidence: 0.2),
          _memory(id: 'high', confidence: 0.9),
          _memory(id: 'mid', confidence: 0.5),
        ],
        capturedAt: DateTime.now(),
      );
      final sorted = snap.byConfidence;
      expect(sorted.first.id, 'high');
      expect(sorted.last.id, 'low');
    });

    test('byRecency returns memories sorted most recent first', () {
      final snap = MemorySnapshot(
        memories: [
          _memory(
            id: 'old',
            updatedAt: DateTime(2020),
            createdAt: DateTime(2020),
          ),
          _memory(
            id: 'new',
            updatedAt: DateTime(2025),
            createdAt: DateTime(2025),
          ),
        ],
        capturedAt: DateTime.now(),
      );
      expect(snap.byRecency.first.id, 'new');
    });

    test('toString includes size and capturedAt', () {
      final capturedAt = DateTime(2025, 6);
      final snap = MemorySnapshot(
        memories: [_memory()],
        capturedAt: capturedAt,
      );
      expect(snap.toString(), contains('1'));
      expect(snap.toString(), contains('2025'));
    });
  });

  // ── MemoryManager ──────────────────────────────────────────────────────────

  group('MemoryManager', () {
    late InMemoryMemoryStore store;
    late MemoryManager manager;

    setUp(() async {
      store = InMemoryMemoryStore();
      manager = MemoryManager(store: store);
      await manager.initialize();
    });

    tearDown(() async => manager.dispose());

    // ── initialization ──

    test('initialize() completes without error', () async {
      final m = MemoryManager(store: InMemoryMemoryStore());
      await expectLater(m.initialize(), completes);
      await m.dispose();
    });

    test('calling initialize() twice is a no-op', () async {
      await expectLater(manager.initialize(), completes);
    });

    test('initialize() calls initialize() on registered sources', () async {
      final source = _FixedMemorySource(sourceId: 'test');
      final m = MemoryManager(store: InMemoryMemoryStore(), sources: [source]);
      await m.initialize();
      expect(source.initialized, isTrue);
      await m.dispose();
    });

    // ── remember / recall ──

    test('remember() persists a memory', () async {
      await manager.remember(_memory(id: 'r1'));
      expect(await manager.count, 1);
    });

    test('recall() returns all stored memories', () async {
      await manager.remember(_memory(id: 'a'));
      await manager.remember(_memory(id: 'b'));
      final memories = await manager.recall();
      expect(memories, hasLength(2));
    });

    test('recallById() returns the memory', () async {
      await manager.remember(_memory(id: 'find-this'));
      final result = await manager.recallById('find-this');
      expect(result, isNotNull);
      expect(result!.id, 'find-this');
    });

    test('recallById() returns null for unknown id', () async {
      expect(await manager.recallById('ghost'), isNull);
    });

    test('recallByType() filters correctly', () async {
      await manager.remember(_memory(id: '1', type: MemoryType.semantic));
      await manager.remember(_memory(id: '2'));
      final semantic = await manager.recallByType(MemoryType.semantic);
      expect(semantic, hasLength(1));
      expect(semantic.first.type, MemoryType.semantic);
    });

    test('recallByTag() filters correctly', () async {
      await manager.remember(_memory(id: '1', tags: ['growth']));
      await manager.remember(_memory(id: '2', tags: ['other']));
      final tagged = await manager.recallByTag('growth');
      expect(tagged, hasLength(1));
    });

    test('recallBySource() filters correctly', () async {
      await manager.remember(_memory(id: '1', source: 'reflection'));
      await manager.remember(_memory(id: '2', source: 'conversation'));
      final reflectionMemories = await manager.recallBySource('reflection');
      expect(reflectionMemories, hasLength(1));
    });

    test('rememberAll() persists multiple memories', () async {
      await manager.rememberAll([_memory(id: 'a'), _memory(id: 'b')]);
      expect(await manager.count, 2);
    });

    // ── forget ──

    test('forget() removes the memory', () async {
      await manager.remember(_memory(id: 'del'));
      await manager.forget('del');
      expect(await manager.recallById('del'), isNull);
    });

    test('forgetAll() removes every memory', () async {
      await manager.rememberAll([_memory(id: 'a'), _memory(id: 'b')]);
      await manager.forgetAll();
      expect(await manager.count, 0);
    });

    // ── consolidate ──

    test('consolidate() extracts and persists memories from sources', () async {
      final extractedMemory = _memory(id: 'extracted', source: 'test-source');
      final source = _FixedMemorySource(
        sourceId: 'test-source',
        memories: [extractedMemory],
      );
      final m = MemoryManager(store: InMemoryMemoryStore(), sources: [source]);
      await m.initialize();

      final result = await m.consolidate({'key': 'value'});

      expect(result, hasLength(1));
      expect(result.first.id, 'extracted');
      expect(await m.count, 1);
      await m.dispose();
    });

    test('consolidate() returns empty list when no sources registered', () async {
      final result = await manager.consolidate({'key': 'value'});
      expect(result, isEmpty);
    });

    test('consolidate() suppresses exceptions from failing sources', () async {
      final throwingSource = _FixedMemorySource(
        sourceId: 'bad-source',
        throwOnExtract: true,
      );
      final m = MemoryManager(
        store: InMemoryMemoryStore(),
        sources: [throwingSource],
      );
      await m.initialize();

      await expectLater(m.consolidate({}), completes);
      await m.dispose();
    });

    test('consolidate() calls all sources even if one fails', () async {
      final throwing = _FixedMemorySource(
        sourceId: 'bad',
        throwOnExtract: true,
      );
      final good = _FixedMemorySource(
        sourceId: 'good',
        memories: [_memory(id: 'good-mem')],
      );
      final m = MemoryManager(
        store: InMemoryMemoryStore(),
        sources: [throwing, good],
      );
      await m.initialize();

      final result = await m.consolidate({});
      expect(result, hasLength(1));
      expect(result.first.id, 'good-mem');
      await m.dispose();
    });

    // ── source registration ──

    test('registerSource() adds a source to the list', () async {
      final source = _FixedMemorySource(sourceId: 'late-add');
      manager.registerSource(source);
      expect(manager.sources, hasLength(1));
      expect(manager.sources.first.sourceId, 'late-add');
    });

    test('sources() returns an unmodifiable view', () {
      expect(
        () => manager.sources.add(
          _FixedMemorySource(sourceId: 'rogue'),
        ),
        throwsUnsupportedError,
      );
    });

    // ── snapshot ──

    test('snapshot() captures all stored memories', () async {
      await manager.remember(_memory(id: 'a'));
      await manager.remember(_memory(id: 'b'));
      final snap = await manager.snapshot();
      expect(snap.size, 2);
    });

    test('snapshot() returns an empty snapshot when no memories exist', () async {
      final snap = await manager.snapshot();
      expect(snap.isEmpty, isTrue);
    });

    test('snapshot() captures the moment it was taken', () async {
      final before = DateTime.now();
      final snap = await manager.snapshot();
      final after = DateTime.now();
      expect(
        snap.capturedAt.isAfter(before) || snap.capturedAt.isAtSameMomentAs(before),
        isTrue,
      );
      expect(
        snap.capturedAt.isBefore(after) || snap.capturedAt.isAtSameMomentAs(after),
        isTrue,
      );
    });

    // ── dispose ──

    test('dispose() calls dispose() on registered sources', () async {
      final source = _FixedMemorySource(sourceId: 'disposable');
      final m = MemoryManager(store: InMemoryMemoryStore(), sources: [source]);
      await m.initialize();
      await m.dispose();
      expect(source.disposed, isTrue);
    });
  });

  // ── MemoryStore contract (abstract behavior via InMemoryMemoryStore) ───────

  group('MemoryStore contract', () {
    late MemoryStore store;

    setUp(() async {
      store = InMemoryMemoryStore();
      await store.init();
    });

    test('save returns the persisted memory', () async {
      final m = _memory(id: 'ret');
      final result = await store.save(m);
      expect(result.id, 'ret');
    });

    test('count is zero after clear', () async {
      await store.save(_memory());
      await store.clear();
      expect(await store.count(), 0);
    });
  });
}
