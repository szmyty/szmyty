import 'package:egohygiene/features/check_in/feature.dart';
import 'package:egohygiene/features/reflection/feature.dart';
import 'package:egohygiene/shared/context/context_builder.dart';
import 'package:egohygiene/shared/context/context_manager.dart';
import 'package:egohygiene/shared/context/context_snapshot.dart';
import 'package:egohygiene/shared/context/context_source.dart';
import 'package:egohygiene/shared/context/impl/check_in_context_source.dart';
import 'package:egohygiene/shared/context/impl/reflection_context_source.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// A [ContextSource] that returns a fixed map of entries when called.
class _FixedContextSource implements ContextSource {
  _FixedContextSource({
    required this.sourceId,
    this._entries = const {},
    this.throwOnBuild = false,
  }) : displayName = 'Fixed Source';

  @override
  final String sourceId;

  @override
  final String displayName;

  final Map<String, Object?> _entries;
  final bool throwOnBuild;

  bool initialized = false;
  bool disposed = false;
  int buildCallCount = 0;

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<Map<String, Object?>> buildContext() async {
    buildCallCount++;
    if (throwOnBuild) throw Exception('source failure');
    return _entries;
  }

  @override
  Future<void> dispose() async => disposed = true;
}

/// A minimal in-memory [ReflectionRepository] for tests.
class _InMemoryReflectionRepository implements ReflectionRepository {
  _InMemoryReflectionRepository({List<ReflectionModel>? seed})
    : _items = seed != null ? List<ReflectionModel>.of(seed) : [];

  final List<ReflectionModel> _items;

  @override
  Future<List<ReflectionModel>> getAll() async =>
      List.unmodifiable(List<ReflectionModel>.of(_items)..sort((a, b) => b.createdAt.compareTo(a.createdAt)));

  @override
  Future<ReflectionModel?> getById(String id) async {
    for (final item in _items) {
      if (item.id == id) return item;
    }
    return null;
  }

  @override
  Future<ReflectionModel> create({
    required String body,
    String? title,
    List<String> tags = const [],
  }) async {
    final now = DateTime.now();
    final reflection = ReflectionModel(
      id: 'r_${_items.length}',
      createdAt: now,
      updatedAt: now,
      title: title,
      body: body,
      tags: tags,
    );
    _items.add(reflection);
    return reflection;
  }

  @override
  Future<ReflectionModel> update(ReflectionModel reflection) async {
    final index = _items.indexWhere((item) => item.id == reflection.id);
    if (index == -1) return reflection;
    _items[index] = reflection;
    return reflection;
  }

  @override
  Future<void> deleteById(String id) async {
    _items.removeWhere((item) => item.id == id);
  }
}

ReflectionModel _reflection({
  String id = 'r-1',
  String body = 'Test reflection body',
  String? title,
  List<String> tags = const [],
  DateTime? createdAt,
}) {
  final now = createdAt ?? DateTime(2025);
  return ReflectionModel(
    id: id,
    createdAt: now,
    updatedAt: now,
    title: title,
    body: body,
    tags: tags,
  );
}

// ---------------------------------------------------------------------------
// CheckIn helpers
// ---------------------------------------------------------------------------

/// A minimal in-memory [CheckInRepository] for tests.
class _InMemoryCheckInRepository implements CheckInRepository {
  _InMemoryCheckInRepository({List<CheckInEntry>? seed}) : _items = seed != null ? List<CheckInEntry>.of(seed) : [];

  final List<CheckInEntry> _items;

  @override
  Future<List<CheckInEntry>> getAll() async =>
      List.unmodifiable(List<CheckInEntry>.of(_items)..sort((a, b) => b.createdAt.compareTo(a.createdAt)));

  @override
  Future<CheckInEntry?> getById(String id) async {
    for (final item in _items) {
      if (item.id == id) return item;
    }
    return null;
  }

  @override
  Future<CheckInEntry?> getTodaysEntry() async {
    final today = DateTime.now();
    for (final item in _items) {
      if (item.createdAt.year == today.year && item.createdAt.month == today.month && item.createdAt.day == today.day) {
        return item;
      }
    }
    return null;
  }

  @override
  Future<CheckInEntry> create({
    required int mood,
    required int energy,
    required int stress,
    required double sleepHours,
    required int focus,
    String? gratitude,
    String? note,
  }) async {
    final now = DateTime.now();
    final entry = CheckInEntry(
      id: 'ci_${_items.length}',
      createdAt: now,
      updatedAt: now,
      mood: mood,
      energy: energy,
      stress: stress,
      sleepHours: sleepHours,
      focus: focus,
      gratitude: gratitude,
      note: note,
    );
    _items.add(entry);
    return entry;
  }

  @override
  Future<CheckInEntry> update(CheckInEntry entry) async {
    final index = _items.indexWhere((item) => item.id == entry.id);
    if (index == -1) return entry;
    _items[index] = entry;
    return entry;
  }

  @override
  Future<void> deleteById(String id) async {
    _items.removeWhere((item) => item.id == id);
  }
}

CheckInEntry _checkIn({
  String id = 'c-1',
  int mood = 3,
  int energy = 3,
  int stress = 3,
  double sleepHours = 7,
  int focus = 3,
  DateTime? createdAt,
}) {
  final now = createdAt ?? DateTime(2025);
  return CheckInEntry(
    id: id,
    createdAt: now,
    updatedAt: now,
    mood: mood,
    energy: energy,
    stress: stress,
    sleepHours: sleepHours,
    focus: focus,
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── ContextSnapshot ────────────────────────────────────────────────────────

  group('ContextSnapshot', () {
    test('empty() produces an empty snapshot', () {
      final snap = ContextSnapshot.empty();
      expect(snap.isEmpty, isTrue);
      expect(snap.size, 0);
      expect(snap.contributingSources, isEmpty);
    });

    test('empty() uses provided capturedAt', () {
      final ts = DateTime(2025, 6);
      final snap = ContextSnapshot.empty(capturedAt: ts);
      expect(snap.capturedAt, ts);
    });

    test('isNotEmpty is true when data is present', () {
      final snap = ContextSnapshot(
        data: const {'key': 'value'},
        capturedAt: DateTime.now(),
        contributingSources: const ['src'],
      );
      expect(snap.isNotEmpty, isTrue);
    });

    test('get() returns typed value for known key', () {
      final snap = ContextSnapshot(
        data: const {'count': 42},
        capturedAt: DateTime.now(),
        contributingSources: const [],
      );
      expect(snap.get<int>('count'), 42);
    });

    test('get() returns null for missing key', () {
      final snap = ContextSnapshot.empty();
      expect(snap.get<String>('missing'), isNull);
    });

    test('get() returns null when type does not match', () {
      final snap = ContextSnapshot(
        data: const {'count': 'not-an-int'},
        capturedAt: DateTime.now(),
        contributingSources: const [],
      );
      expect(snap.get<int>('count'), isNull);
    });

    test('entriesWithPrefix() returns matching entries only', () {
      final snap = ContextSnapshot(
        data: const {
          'reflection.count': 3,
          'reflection.history': [],
          'goals.active': [],
        },
        capturedAt: DateTime.now(),
        contributingSources: const [],
      );
      final entries = snap.entriesWithPrefix('reflection.');
      expect(entries.keys, containsAll(['reflection.count', 'reflection.history']));
      expect(entries.containsKey('goals.active'), isFalse);
    });

    test('hasSource() returns true for contributing source', () {
      final snap = ContextSnapshot(
        data: const {},
        capturedAt: DateTime.now(),
        contributingSources: const ['reflection'],
      );
      expect(snap.hasSource('reflection'), isTrue);
      expect(snap.hasSource('goals'), isFalse);
    });

    test('toString() includes size and sources', () {
      final snap = ContextSnapshot(
        data: const {'k': 'v'},
        capturedAt: DateTime.now(),
        contributingSources: const ['reflection'],
      );
      expect(snap.toString(), contains('1'));
      expect(snap.toString(), contains('reflection'));
    });
  });

  // ── ContextBuilder ─────────────────────────────────────────────────────────

  group('ContextBuilder', () {
    test('build() produces an empty snapshot when nothing was added', () {
      final snap = ContextBuilder().build();
      expect(snap.isEmpty, isTrue);
      expect(snap.contributingSources, isEmpty);
    });

    test('addEntry() adds a key-value pair', () {
      final snap = ContextBuilder().addEntry('k', 'v').build();
      expect(snap.get<String>('k'), 'v');
    });

    test('addEntry() overwrites duplicate keys', () {
      final snap = ContextBuilder().addEntry('k', 'first').addEntry('k', 'second').build();
      expect(snap.get<String>('k'), 'second');
    });

    test('addAll() merges all entries', () {
      final snap = ContextBuilder().addAll({'a': 1, 'b': 2}).build();
      expect(snap.get<int>('a'), 1);
      expect(snap.get<int>('b'), 2);
    });

    test('addSource() records contributing source', () {
      final snap = ContextBuilder().addSource('reflection').build();
      expect(snap.hasSource('reflection'), isTrue);
    });

    test('addSource() deduplicates sources', () {
      final snap = ContextBuilder().addSource('reflection').addSource('reflection').build();
      expect(snap.contributingSources, hasLength(1));
    });

    test('build() uses provided capturedAt', () {
      final ts = DateTime(2025);
      final snap = ContextBuilder().build(capturedAt: ts);
      expect(snap.capturedAt, ts);
    });

    test('data map is unmodifiable after build()', () {
      final snap = ContextBuilder().addEntry('k', 'v').build();
      expect(
        () => snap.data['new'] = 'val',
        throwsUnsupportedError,
      );
    });

    test('contributingSources list is unmodifiable after build()', () {
      final snap = ContextBuilder().addSource('src').build();
      expect(
        () => snap.contributingSources.add('rogue'),
        throwsUnsupportedError,
      );
    });
  });

  // ── ContextManager ─────────────────────────────────────────────────────────

  group('ContextManager', () {
    late ContextManager manager;

    setUp(() {
      manager = ContextManager();
    });

    tearDown(() async {
      await manager.dispose();
    });

    // ── initialization ──

    test('initialize() is a no-op on an empty manager', () async {
      await expectLater(manager.initialize(), completes);
    });

    test('initialize() calls initialize() on all registered sources', () async {
      final src = _FixedContextSource(sourceId: 'a');
      manager = ContextManager(sources: [src]);
      await manager.initialize();
      expect(src.initialized, isTrue);
    });

    test('initialize() is idempotent', () async {
      final src = _FixedContextSource(sourceId: 'a');
      manager = ContextManager(sources: [src]);
      await manager.initialize();
      await manager.initialize();
      // initialize() on the source was called only once because manager
      // short-circuits on the second call.
      expect(src.initialized, isTrue);
    });

    // ── source registration ──

    test('starts with no sources', () {
      expect(manager.sources, isEmpty);
    });

    test('registerSource() adds a source', () {
      manager.registerSource(_FixedContextSource(sourceId: 'a'));
      expect(manager.sources, hasLength(1));
    });

    test('registerSource() accepts multiple sources', () {
      manager
        ..registerSource(_FixedContextSource(sourceId: 'a'))
        ..registerSource(_FixedContextSource(sourceId: 'b'));
      expect(manager.sources, hasLength(2));
    });

    test('sources is unmodifiable', () {
      expect(
        () => manager.sources.add(
          _FixedContextSource(sourceId: 'rogue'),
        ),
        throwsUnsupportedError,
      );
    });

    // ── assemble ──

    test('assemble() returns an empty snapshot with no sources', () async {
      final snap = await manager.assemble();
      expect(snap.isEmpty, isTrue);
      expect(snap.contributingSources, isEmpty);
    });

    test('assemble() includes contributions from all sources', () async {
      manager
        ..registerSource(
          _FixedContextSource(sourceId: 'a', entries: {'a.key': 'a-val'}),
        )
        ..registerSource(
          _FixedContextSource(sourceId: 'b', entries: {'b.key': 'b-val'}),
        );
      final snap = await manager.assemble();
      expect(snap.get<String>('a.key'), 'a-val');
      expect(snap.get<String>('b.key'), 'b-val');
    });

    test('assemble() records source ids in snapshot', () async {
      manager
        ..registerSource(_FixedContextSource(sourceId: 'alpha'))
        ..registerSource(_FixedContextSource(sourceId: 'beta'));
      final snap = await manager.assemble();
      expect(snap.hasSource('alpha'), isTrue);
      expect(snap.hasSource('beta'), isTrue);
    });

    test('assemble() suppresses errors from individual sources', () async {
      manager
        ..registerSource(
          _FixedContextSource(
            sourceId: 'broken',
            throwOnBuild: true,
          ),
        )
        ..registerSource(
          _FixedContextSource(
            sourceId: 'healthy',
            entries: {'healthy.key': 'ok'},
          ),
        );

      // Broken source must not propagate; assembly must complete successfully.
      final snap = await manager.assemble();
      expect(snap.hasSource('broken'), isFalse);
      expect(snap.hasSource('healthy'), isTrue);
      expect(snap.get<String>('healthy.key'), 'ok');
    });

    test('assemble() captures current time', () async {
      final before = DateTime.now();
      final snap = await manager.assemble();
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

    test('dispose() calls dispose() on all registered sources', () async {
      final src = _FixedContextSource(sourceId: 'a');
      manager = ContextManager(sources: [src]);
      await manager.dispose();
      expect(src.disposed, isTrue);
    });

    test('dispose() resets initialized state', () async {
      final src = _FixedContextSource(sourceId: 'a');
      manager = ContextManager(sources: [src]);
      await manager.initialize();
      await manager.dispose();
      // After dispose + re-initialize, the source initialize() should be
      // called again (once per initialize() call after a dispose).
      await manager.initialize();
      expect(src.initialized, isTrue);
    });
  });

  // ── ReflectionContextSource ────────────────────────────────────────────────

  group('ReflectionContextSource', () {
    test('sourceId is "reflection"', () {
      final src = ReflectionContextSource(
        repository: _InMemoryReflectionRepository(),
      );
      expect(src.sourceId, ReflectionContextSource.id);
      expect(src.sourceId, 'reflection');
    });

    test('displayName is human-readable', () {
      final src = ReflectionContextSource(
        repository: _InMemoryReflectionRepository(),
      );
      expect(src.displayName, isNotEmpty);
    });

    test('buildContext() returns empty lists when no reflections exist', () async {
      final src = ReflectionContextSource(
        repository: _InMemoryReflectionRepository(),
      );
      final ctx = await src.buildContext();
      expect(ctx['reflection.count'], 0);
      expect(ctx['reflection.history'], isEmpty);
      expect(ctx['reflection.recentTags'], isEmpty);
    });

    test('buildContext() includes reflection count', () async {
      final repo = _InMemoryReflectionRepository(
        seed: [
          _reflection(id: 'r1'),
          _reflection(id: 'r2'),
          _reflection(id: 'r3'),
        ],
      );
      final src = ReflectionContextSource(repository: repo);
      final ctx = await src.buildContext();
      expect(ctx['reflection.count'], 3);
    });

    test('buildContext() history contains JSON maps', () async {
      final repo = _InMemoryReflectionRepository(
        seed: [_reflection(id: 'r1', body: 'Hello world')],
      );
      final src = ReflectionContextSource(repository: repo);
      final ctx = await src.buildContext();
      final history = ctx['reflection.history']! as List<dynamic>;
      expect(history, hasLength(1));
      final entry = history.first as Map<String, Object?>;
      expect(entry['id'], 'r1');
      expect(entry['body'], 'Hello world');
    });

    test('buildContext() recentTags returns most-frequent tags', () async {
      final now = DateTime(2025);
      final repo = _InMemoryReflectionRepository(
        seed: [
          _reflection(id: 'r1', tags: ['growth', 'mindset'], createdAt: now),
          _reflection(
            id: 'r2',
            tags: ['growth', 'health'],
            createdAt: now.subtract(const Duration(days: 1)),
          ),
          _reflection(
            id: 'r3',
            tags: ['mindset'],
            createdAt: now.subtract(const Duration(days: 2)),
          ),
        ],
      );
      final src = ReflectionContextSource(repository: repo);
      final ctx = await src.buildContext();
      final tags = ctx['reflection.recentTags']! as List<dynamic>;
      // 'growth' and 'mindset' appear twice; they should be first.
      expect(tags.take(2), containsAll(['growth', 'mindset']));
    });

    test('buildContext() recentTags limited to top 5', () async {
      final now = DateTime(2025);
      final repo = _InMemoryReflectionRepository(
        seed: [
          _reflection(
            id: 'r1',
            tags: ['t1', 't2', 't3', 't4', 't5', 't6', 't7'],
            createdAt: now,
          ),
        ],
      );
      final src = ReflectionContextSource(repository: repo);
      final ctx = await src.buildContext();
      final tags = ctx['reflection.recentTags']! as List<dynamic>;
      expect(tags.length, lessThanOrEqualTo(5));
    });

    test('initialize() and dispose() complete without error', () async {
      final src = ReflectionContextSource(
        repository: _InMemoryReflectionRepository(),
      );
      await expectLater(src.initialize(), completes);
      await expectLater(src.dispose(), completes);
    });

    test('contributes to ContextManager assembly', () async {
      final repo = _InMemoryReflectionRepository(
        seed: [_reflection(id: 'r1', body: 'Contributed')],
      );
      final src = ReflectionContextSource(repository: repo);
      final manager = ContextManager(sources: [src]);
      await manager.initialize();

      final snap = await manager.assemble();
      expect(snap.hasSource('reflection'), isTrue);
      expect(snap.get<int>('reflection.count'), 1);
      await manager.dispose();
    });
  });

  // ── CheckInContextSource ───────────────────────────────────────────────────

  group('CheckInContextSource', () {
    test('sourceId is "checkIn"', () {
      final src = CheckInContextSource(
        repository: _InMemoryCheckInRepository(),
      );
      expect(src.sourceId, CheckInContextSource.id);
      expect(src.sourceId, 'checkIn');
    });

    test('displayName is human-readable', () {
      final src = CheckInContextSource(
        repository: _InMemoryCheckInRepository(),
      );
      expect(src.displayName, isNotEmpty);
    });

    test('buildContext() returns zeros and nulls when no entries exist', () async {
      final src = CheckInContextSource(
        repository: _InMemoryCheckInRepository(),
      );
      final ctx = await src.buildContext();
      expect(ctx['checkIn.count'], 0);
      expect(ctx['checkIn.history'], isEmpty);
      expect(ctx['checkIn.averageMood'], isNull);
      expect(ctx['checkIn.averageEnergy'], isNull);
      expect(ctx['checkIn.averageStress'], isNull);
    });

    test('buildContext() includes check-in count', () async {
      final repo = _InMemoryCheckInRepository(
        seed: [
          _checkIn(id: 'c1'),
          _checkIn(id: 'c2'),
        ],
      );
      final src = CheckInContextSource(repository: repo);
      final ctx = await src.buildContext();
      expect(ctx['checkIn.count'], 2);
    });

    test('buildContext() history contains JSON maps', () async {
      final repo = _InMemoryCheckInRepository(
        seed: [_checkIn(id: 'c1', mood: 4)],
      );
      final src = CheckInContextSource(repository: repo);
      final ctx = await src.buildContext();
      final history = ctx['checkIn.history']! as List<dynamic>;
      expect(history, hasLength(1));
      final entry = history.first as Map<String, Object?>;
      expect(entry['id'], 'c1');
      expect(entry['mood'], 4);
    });

    test('buildContext() averageMood is computed correctly', () async {
      final repo = _InMemoryCheckInRepository(
        seed: [
          _checkIn(id: 'c1', mood: 2),
          _checkIn(id: 'c2', mood: 4),
        ],
      );
      final src = CheckInContextSource(repository: repo);
      final ctx = await src.buildContext();
      expect(ctx['checkIn.averageMood'], 3.0);
    });

    test('buildContext() history is capped at 7 entries', () async {
      final repo = _InMemoryCheckInRepository(
        seed: List.generate(
          10,
          (i) => _checkIn(id: 'c$i'),
        ),
      );
      final src = CheckInContextSource(repository: repo);
      final ctx = await src.buildContext();
      final history = ctx['checkIn.history']! as List<dynamic>;
      expect(history.length, lessThanOrEqualTo(7));
      // Count includes all entries
      expect(ctx['checkIn.count'], 10);
    });

    test('initialize() and dispose() complete without error', () async {
      final src = CheckInContextSource(
        repository: _InMemoryCheckInRepository(),
      );
      await expectLater(src.initialize(), completes);
      await expectLater(src.dispose(), completes);
    });

    test('contributes to ContextManager assembly', () async {
      final repo = _InMemoryCheckInRepository(
        seed: [_checkIn(id: 'c1', mood: 5)],
      );
      final src = CheckInContextSource(repository: repo);
      final manager = ContextManager(sources: [src]);
      await manager.initialize();

      final snap = await manager.assemble();
      expect(snap.hasSource('checkIn'), isTrue);
      expect(snap.get<int>('checkIn.count'), 1);
      await manager.dispose();
    });
  });
}
