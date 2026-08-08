import 'package:egohygiene/shared/practice/impl/in_memory_practice_store.dart';
import 'package:egohygiene/shared/practice/practice_completion.dart';
import 'package:egohygiene/shared/practice/practice_manager.dart';
import 'package:egohygiene/shared/practice/practice_progress.dart';
import 'package:egohygiene/shared/practice/practice_schedule.dart';
import 'package:egohygiene/shared/practice/practice_source.dart';
import 'package:egohygiene/shared/practice/practice_state.dart';
import 'package:egohygiene/shared/practice/practice_store.dart';
import 'package:egohygiene/shared/practice/practice_type.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

PracticeCompletion _completion({
  String id = 'comp-1',
  PracticeType type = PracticeType.mindfulness,
  DateTime? completedAt,
  String? notes,
  int? durationMinutes,
}) {
  return PracticeCompletion(
    id: id,
    type: type,
    completedAt: completedAt ?? DateTime(2026, 1, 1, 10),
    notes: notes,
    durationMinutes: durationMinutes,
  );
}

/// A [PracticeSource] that returns a fixed list of completions.
class _FixedPracticeSource implements PracticeSource {
  _FixedPracticeSource({
    required this.sourceId,
    Set<PracticeType>? supportedTypes,
    this._completions = const [],
    this.throwOnLoad = false,
  }) : displayName = 'Fixed Source',
       supportedTypes = supportedTypes ?? PracticeType.values.toSet();

  @override
  final String sourceId;

  @override
  final String displayName;

  @override
  final Set<PracticeType> supportedTypes;

  final List<PracticeCompletion> _completions;
  final bool throwOnLoad;

  bool initialized = false;
  bool disposed = false;
  int loadCallCount = 0;

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<List<PracticeCompletion>> loadCompletions(PracticeType type) async {
    loadCallCount++;
    if (throwOnLoad) throw Exception('source failure');
    return _completions.where((c) => c.type == type).toList();
  }

  @override
  Future<void> dispose() async => disposed = true;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── PracticeType ───────────────────────────────────────────────────────────

  group('PracticeType', () {
    test('has six practice types', () {
      expect(PracticeType.values, hasLength(6));
    });

    test('contains all expected types', () {
      expect(
        PracticeType.values,
        containsAll([
          PracticeType.reflection,
          PracticeType.gratitude,
          PracticeType.abundance,
          PracticeType.mindfulness,
          PracticeType.journaling,
          PracticeType.sleepHygiene,
        ]),
      );
    });

    test('defaultSet includes all six types', () {
      expect(PracticeType.defaultSet, hasLength(6));
    });
  });

  // ── PracticeState ──────────────────────────────────────────────────────────

  group('PracticeState', () {
    test('has three states', () {
      expect(PracticeState.values, hasLength(3));
    });

    test('contains active, paused, and archived', () {
      expect(
        PracticeState.values,
        containsAll([
          PracticeState.active,
          PracticeState.paused,
          PracticeState.archived,
        ]),
      );
    });
  });

  // ── PracticeCompletion ─────────────────────────────────────────────────────

  group('PracticeCompletion', () {
    test('constructs with required fields', () {
      final c = _completion();
      expect(c.id, 'comp-1');
      expect(c.type, PracticeType.mindfulness);
      expect(c.notes, isNull);
      expect(c.durationMinutes, isNull);
      expect(c.metadata, isEmpty);
    });

    test('copyWith replaces specified fields', () {
      final original = _completion(id: 'orig', notes: 'original');
      final updated = original.copyWith(notes: 'updated', durationMinutes: 10);
      expect(updated.id, 'orig');
      expect(updated.notes, 'updated');
      expect(updated.durationMinutes, 10);
    });

    test('equality is based on id and type', () {
      final a = _completion(id: 'x', type: PracticeType.gratitude);
      final b = _completion(id: 'x', type: PracticeType.gratitude, notes: 'diff');
      expect(a, equals(b));
    });

    test('different id produces different identity', () {
      final a = _completion(id: 'a');
      final b = _completion(id: 'b');
      expect(a, isNot(equals(b)));
    });

    test('toString includes id and type', () {
      final c = _completion(id: 'abc', type: PracticeType.journaling);
      expect(c.toString(), contains('abc'));
      expect(c.toString(), contains('journaling'));
    });
  });

  // ── PracticeSchedule ───────────────────────────────────────────────────────

  group('PracticeSchedule', () {
    test('defaults to daily frequency, enabled, target 1', () {
      const schedule = PracticeSchedule();
      expect(schedule.frequency, PracticeFrequency.daily);
      expect(schedule.isEnabled, isTrue);
      expect(schedule.targetPerPeriod, 1);
    });

    test('isDueOn returns true when no completions today', () {
      const schedule = PracticeSchedule();
      final today = DateTime(2026, 6, 15);
      expect(schedule.isDueOn(today, const []), isTrue);
    });

    test('isDueOn returns false when already completed today', () {
      const schedule = PracticeSchedule();
      final today = DateTime(2026, 6, 15);
      final completions = [DateTime(2026, 6, 15, 9)];
      expect(schedule.isDueOn(today, completions), isFalse);
    });

    test('isDueOn returns false when disabled', () {
      const schedule = PracticeSchedule(isEnabled: false);
      final today = DateTime(2026, 6, 15);
      expect(schedule.isDueOn(today, const []), isFalse);
    });

    test('copyWith replaces specified fields', () {
      const original = PracticeSchedule();
      final updated = original.copyWith(isEnabled: false, targetPerPeriod: 2);
      expect(updated.isEnabled, isFalse);
      expect(updated.targetPerPeriod, 2);
      expect(updated.frequency, PracticeFrequency.daily);
    });

    test('equality reflects all fields', () {
      const a = PracticeSchedule(frequency: PracticeFrequency.weekly);
      const b = PracticeSchedule(frequency: PracticeFrequency.weekly);
      const c = PracticeSchedule();
      expect(a, equals(b));
      expect(a, isNot(equals(c)));
    });

    test('weekly isDueOn false when completed this week', () {
      // Wednesday 2026-06-17 (week: Mon Jun 15 – Sun Jun 21)
      const schedule = PracticeSchedule(frequency: PracticeFrequency.weekly);
      final today = DateTime(2026, 6, 17);
      final completions = [DateTime(2026, 6, 15)]; // Monday same week
      expect(schedule.isDueOn(today, completions), isFalse);
    });
  });

  // ── PracticeProgress ───────────────────────────────────────────────────────

  group('PracticeProgress', () {
    final now = DateTime(2026, 6, 15, 12);

    test('empty() produces zero stats', () {
      final p = PracticeProgress.empty(PracticeType.mindfulness);
      expect(p.currentStreak, 0);
      expect(p.longestStreak, 0);
      expect(p.totalCompletions, 0);
      expect(p.lastCompletedAt, isNull);
      expect(p.recentHistory, isEmpty);
      expect(p.isCompletedToday, isFalse);
    });

    test('compute with no completions returns empty progress', () {
      final p = PracticeProgress.compute(
        PracticeType.mindfulness,
        const [],
        now: now,
      );
      expect(p.totalCompletions, 0);
      expect(p.currentStreak, 0);
    });

    test('compute totalCompletions matches list length', () {
      final completions = [
        _completion(id: 'a', completedAt: DateTime(2026, 6, 13, 10)),
        _completion(id: 'b', completedAt: DateTime(2026, 6, 14, 10)),
        _completion(id: 'c', completedAt: DateTime(2026, 6, 15, 10)),
      ];
      final p = PracticeProgress.compute(
        PracticeType.mindfulness,
        completions,
        now: now,
      );
      expect(p.totalCompletions, 3);
    });

    test('compute currentStreak for consecutive days ending today', () {
      final completions = [
        _completion(id: 'a', completedAt: DateTime(2026, 6, 13, 10)),
        _completion(id: 'b', completedAt: DateTime(2026, 6, 14, 10)),
        _completion(id: 'c', completedAt: DateTime(2026, 6, 15, 10)),
      ];
      final p = PracticeProgress.compute(
        PracticeType.mindfulness,
        completions,
        now: now,
      );
      expect(p.currentStreak, 3);
    });

    test('compute currentStreak for consecutive days ending yesterday', () {
      final completions = [
        _completion(id: 'a', completedAt: DateTime(2026, 6, 13, 10)),
        _completion(id: 'b', completedAt: DateTime(2026, 6, 14, 10)),
      ];
      final p = PracticeProgress.compute(
        PracticeType.mindfulness,
        completions,
        now: now,
      );
      // Streak alive because yesterday was completed.
      expect(p.currentStreak, 2);
    });

    test('compute currentStreak resets after a gap', () {
      final completions = [
        _completion(id: 'a', completedAt: DateTime(2026, 6, 10, 10)),
        _completion(id: 'b', completedAt: DateTime(2026, 6, 11, 10)),
        // gap on 12th
        _completion(id: 'c', completedAt: DateTime(2026, 6, 13, 10)),
        _completion(id: 'd', completedAt: DateTime(2026, 6, 14, 10)),
        _completion(id: 'e', completedAt: DateTime(2026, 6, 15, 10)),
      ];
      final p = PracticeProgress.compute(
        PracticeType.mindfulness,
        completions,
        now: now,
      );
      expect(p.currentStreak, 3);
    });

    test('compute longestStreak tracks the historical best', () {
      final completions = [
        _completion(id: 'a', completedAt: DateTime(2026, 6, 1, 10)),
        _completion(id: 'b', completedAt: DateTime(2026, 6, 2, 10)),
        _completion(id: 'c', completedAt: DateTime(2026, 6, 3, 10)),
        _completion(id: 'd', completedAt: DateTime(2026, 6, 4, 10)),
        // gap
        _completion(id: 'e', completedAt: DateTime(2026, 6, 14, 10)),
        _completion(id: 'f', completedAt: DateTime(2026, 6, 15, 10)),
      ];
      final p = PracticeProgress.compute(
        PracticeType.mindfulness,
        completions,
        now: now,
      );
      expect(p.longestStreak, 4);
      expect(p.currentStreak, 2);
    });

    test('multiple completions on same day count as one streak day', () {
      final completions = [
        _completion(id: 'a', completedAt: DateTime(2026, 6, 14, 8)),
        _completion(id: 'b', completedAt: DateTime(2026, 6, 14, 20)),
        _completion(id: 'c', completedAt: DateTime(2026, 6, 15, 10)),
      ];
      final p = PracticeProgress.compute(
        PracticeType.mindfulness,
        completions,
        now: now,
      );
      expect(p.currentStreak, 2);
    });

    test('isCompletedToday is true when latest completion is today', () {
      final completions = [
        _completion(id: 'a', completedAt: DateTime(2026, 6, 15, 8)),
      ];
      final p = PracticeProgress.compute(
        PracticeType.mindfulness,
        completions,
        now: now,
      );
      expect(p.isCompletedToday, isTrue);
    });

    test('isCompletedToday is false when latest completion was yesterday', () {
      final completions = [
        _completion(id: 'a', completedAt: DateTime(2026, 6, 14, 8)),
      ];
      final p = PracticeProgress.compute(
        PracticeType.mindfulness,
        completions,
        now: now,
      );
      expect(p.isCompletedToday, isFalse);
    });

    test('recentHistory is capped at recentHistoryLimit', () {
      final completions = [
        for (int i = 0; i < 50; i++)
          _completion(
            id: 'comp-$i',
            completedAt: DateTime(2026).add(Duration(days: i)),
          ),
      ];
      final p = PracticeProgress.compute(
        PracticeType.mindfulness,
        completions,
        recentHistoryLimit: 10,
      );
      expect(p.recentHistory, hasLength(10));
    });

    test('toString includes type, streaks, and total', () {
      final p = PracticeProgress.empty(PracticeType.reflection);
      expect(p.toString(), contains('reflection'));
      expect(p.toString(), contains('currentStreak'));
    });
  });

  // ── InMemoryPracticeStore ──────────────────────────────────────────────────

  group('InMemoryPracticeStore', () {
    late InMemoryPracticeStore store;

    setUp(() async {
      store = InMemoryPracticeStore();
      await store.init();
    });

    test('init() completes without error', () async {
      await expectLater(store.init(), completes);
    });

    test('starts empty', () async {
      expect(await store.count(), 0);
      expect(await store.findAll(), isEmpty);
    });

    test('save() persists a completion', () async {
      await store.save(_completion());
      expect(await store.count(), 1);
    });

    test('findById() returns the saved completion', () async {
      final c = _completion(id: 'find-me');
      await store.save(c);
      final result = await store.findById('find-me');
      expect(result, equals(c));
    });

    test('findById() returns null for unknown id', () async {
      expect(await store.findById('ghost'), isNull);
    });

    test('save() replaces existing completion with same id', () async {
      final original = _completion(id: 'dup', notes: 'first');
      final replacement = _completion(id: 'dup', notes: 'second');
      await store.save(original);
      await store.save(replacement);
      expect(await store.count(), 1);
      final result = await store.findById('dup');
      expect(result!.notes, 'second');
    });

    test('findAll() returns completions ordered by completedAt ascending', () async {
      final t1 = DateTime(2026);
      final t2 = DateTime(2026, 1, 2);
      final t3 = DateTime(2026, 1, 3);

      await store.save(_completion(id: 'c', completedAt: t3));
      await store.save(_completion(id: 'a', completedAt: t1));
      await store.save(_completion(id: 'b', completedAt: t2));

      final all = await store.findAll();
      expect(all.map((c) => c.id), ['a', 'b', 'c']);
    });

    test('findByType() returns only matching completions', () async {
      await store.save(_completion(id: '1'));
      await store.save(_completion(id: '2', type: PracticeType.gratitude));
      await store.save(_completion(id: '3'));

      final mindfulness = await store.findByType(PracticeType.mindfulness);
      expect(mindfulness, hasLength(2));
      expect(
        mindfulness.every((c) => c.type == PracticeType.mindfulness),
        isTrue,
      );
    });

    test('saveAll() persists multiple completions', () async {
      await store.saveAll([
        _completion(id: 'a'),
        _completion(id: 'b'),
        _completion(id: 'c'),
      ]);
      expect(await store.count(), 3);
    });

    test('deleteById() removes the completion', () async {
      await store.save(_completion(id: 'del-me'));
      await store.deleteById('del-me');
      expect(await store.findById('del-me'), isNull);
      expect(await store.count(), 0);
    });

    test('deleteById() is a no-op for unknown id', () async {
      await expectLater(store.deleteById('ghost'), completes);
    });

    test('clear() removes all completions', () async {
      await store.saveAll([_completion(id: 'a'), _completion(id: 'b')]);
      await store.clear();
      expect(await store.count(), 0);
    });
  });

  // ── PracticeStore contract ─────────────────────────────────────────────────

  group('PracticeStore contract', () {
    late PracticeStore store;

    setUp(() async {
      store = InMemoryPracticeStore();
      await store.init();
    });

    test('save returns the persisted completion', () async {
      final c = _completion(id: 'ret');
      final result = await store.save(c);
      expect(result.id, 'ret');
    });

    test('count is zero after clear', () async {
      await store.save(_completion());
      await store.clear();
      expect(await store.count(), 0);
    });
  });

  // ── PracticeManager ────────────────────────────────────────────────────────

  group('PracticeManager', () {
    late InMemoryPracticeStore store;
    late PracticeManager manager;

    setUp(() async {
      store = InMemoryPracticeStore();
      manager = PracticeManager(store: store);
      await manager.initialize();
    });

    tearDown(() async => manager.dispose());

    // ── initialization ──

    test('initialize() completes without error', () async {
      final m = PracticeManager(store: InMemoryPracticeStore());
      await expectLater(m.initialize(), completes);
      await m.dispose();
    });

    test('calling initialize() twice is a no-op', () async {
      await expectLater(manager.initialize(), completes);
    });

    test('initialize() calls initialize() on registered sources', () async {
      final source = _FixedPracticeSource(sourceId: 'test');
      final m = PracticeManager(
        store: InMemoryPracticeStore(),
        sources: [source],
      );
      await m.initialize();
      expect(source.initialized, isTrue);
      await m.dispose();
    });

    // ── complete / getCompletions ──

    test('complete() persists a native completion', () async {
      await manager.complete(PracticeType.mindfulness);
      final completions = await manager.getCompletions(PracticeType.mindfulness);
      expect(completions, hasLength(1));
    });

    test('complete() stores notes and duration', () async {
      final c = await manager.complete(
        PracticeType.journaling,
        notes: 'Today was good',
        durationMinutes: 15,
      );
      expect(c.notes, 'Today was good');
      expect(c.durationMinutes, 15);
    });

    test('complete() uses provided id', () async {
      final c = await manager.complete(
        PracticeType.gratitude,
        id: 'custom-id',
      );
      expect(c.id, 'custom-id');
    });

    test('complete() uses provided completedAt', () async {
      final ts = DateTime(2026, 1, 15, 9);
      final c = await manager.complete(
        PracticeType.gratitude,
        completedAt: ts,
      );
      expect(c.completedAt, ts);
    });

    test('getCompletions() returns empty list when nothing recorded', () async {
      final completions = await manager.getCompletions(PracticeType.gratitude);
      expect(completions, isEmpty);
    });

    test('deleteCompletion() removes the native completion', () async {
      final c = await manager.complete(
        PracticeType.mindfulness,
        id: 'del-this',
      );
      await manager.deleteCompletion(c.id);
      final completions = await manager.getCompletions(PracticeType.mindfulness);
      expect(completions.any((x) => x.id == 'del-this'), isFalse);
    });

    // ── getAllCompletions / getCompletionTimestamps ──

    test('getAllCompletions() returns completions across all types', () async {
      await manager.complete(PracticeType.mindfulness);
      await manager.complete(PracticeType.gratitude);
      await manager.complete(PracticeType.journaling);
      final all = await manager.getAllCompletions();
      expect(all, hasLength(3));
    });

    test('getCompletionTimestamps() returns timestamps for all types', () async {
      final ts1 = DateTime(2026, 1, 10);
      final ts2 = DateTime(2026, 1, 11);
      await manager.complete(PracticeType.mindfulness, completedAt: ts1);
      await manager.complete(PracticeType.gratitude, completedAt: ts2);
      final timestamps = await manager.getCompletionTimestamps();
      expect(timestamps, contains(ts1));
      expect(timestamps, contains(ts2));
    });

    // ── source integration ──

    test('getCompletions() merges native and sourced completions', () async {
      final sourcedCompletion = _completion(
        id: 'sourced-1',
        completedAt: DateTime(2026, 1, 5),
      );
      final source = _FixedPracticeSource(
        sourceId: 'ext',
        completions: [sourcedCompletion],
      );
      final m = PracticeManager(
        store: InMemoryPracticeStore(),
        sources: [source],
      );
      await m.initialize();

      await m.complete(
        PracticeType.mindfulness,
        id: 'native-1',
        completedAt: DateTime(2026, 1, 6),
      );

      final completions = await m.getCompletions(PracticeType.mindfulness);
      expect(completions, hasLength(2));
      expect(completions.any((c) => c.id == 'sourced-1'), isTrue);
      expect(completions.any((c) => c.id == 'native-1'), isTrue);
      await m.dispose();
    });

    test('getCompletions() deduplicates by id', () async {
      final dup = _completion(id: 'dup-1');
      final source = _FixedPracticeSource(
        sourceId: 'ext',
        completions: [dup],
      );
      final m = PracticeManager(
        store: InMemoryPracticeStore(),
        sources: [source],
      );
      await m.initialize();
      await m.complete(
        PracticeType.mindfulness,
        id: 'dup-1',
        completedAt: dup.completedAt,
      );

      final completions = await m.getCompletions(PracticeType.mindfulness);
      expect(completions.where((c) => c.id == 'dup-1'), hasLength(1));
      await m.dispose();
    });

    test('source failure is suppressed in getCompletions()', () async {
      final throwing = _FixedPracticeSource(
        sourceId: 'bad',
        throwOnLoad: true,
      );
      final m = PracticeManager(
        store: InMemoryPracticeStore(),
        sources: [throwing],
      );
      await m.initialize();

      await expectLater(
        m.getCompletions(PracticeType.mindfulness),
        completes,
      );
      await m.dispose();
    });

    // ── progress ──

    test('getProgress() returns empty progress when nothing recorded', () async {
      final p = await manager.getProgress(PracticeType.gratitude);
      expect(p.totalCompletions, 0);
      expect(p.currentStreak, 0);
    });

    test('getProgress() computes streak across native completions', () async {
      final now = DateTime(2026, 6, 15, 12);
      for (var i = 0; i < 3; i++) {
        await manager.complete(
          PracticeType.mindfulness,
          completedAt: DateTime(2026, 6, 13 + i, 10),
        );
      }
      final p = await manager.getProgress(PracticeType.mindfulness, now: now);
      expect(p.currentStreak, 3);
    });

    test('isCompletedToday() returns true after completing today', () async {
      final now = DateTime(2026, 6, 15, 12);
      await manager.complete(
        PracticeType.mindfulness,
        completedAt: DateTime(2026, 6, 15, 9),
      );
      final result = await manager.isCompletedToday(
        PracticeType.mindfulness,
        now: now,
      );
      expect(result, isTrue);
    });

    test('isCompletedToday() returns false before completing today', () async {
      final now = DateTime(2026, 6, 15, 12);
      final result = await manager.isCompletedToday(
        PracticeType.mindfulness,
        now: now,
      );
      expect(result, isFalse);
    });

    // ── state management ──

    test('getState() defaults to active', () {
      expect(manager.getState(PracticeType.gratitude), PracticeState.active);
    });

    test('setState() updates state', () {
      manager.setState(PracticeType.gratitude, PracticeState.paused);
      expect(manager.getState(PracticeType.gratitude), PracticeState.paused);
    });

    test('setState() is independent per practice type', () {
      manager.setState(PracticeType.gratitude, PracticeState.paused);
      expect(manager.getState(PracticeType.mindfulness), PracticeState.active);
    });

    // ── schedule management ──

    test('getSchedule() defaults to daily enabled schedule', () {
      final schedule = manager.getSchedule(PracticeType.journaling);
      expect(schedule.frequency, PracticeFrequency.daily);
      expect(schedule.isEnabled, isTrue);
    });

    test('setSchedule() updates schedule', () {
      const newSchedule = PracticeSchedule(
        frequency: PracticeFrequency.weekly,
        isEnabled: false,
      );
      manager.setSchedule(PracticeType.journaling, newSchedule);
      expect(
        manager.getSchedule(PracticeType.journaling),
        equals(newSchedule),
      );
    });

    // ── source registration ──

    test('registerSource() adds source to manager', () {
      final source = _FixedPracticeSource(sourceId: 'late-add');
      manager.registerSource(source);
      expect(manager.sources, hasLength(1));
      expect(manager.sources.first.sourceId, 'late-add');
    });

    test('sources returns an unmodifiable view', () {
      expect(
        () => manager.sources.add(
          _FixedPracticeSource(sourceId: 'rogue'),
        ),
        throwsUnsupportedError,
      );
    });

    // ── dispose ──

    test('dispose() calls dispose() on registered sources', () async {
      final source = _FixedPracticeSource(sourceId: 'disposable');
      final m = PracticeManager(
        store: InMemoryPracticeStore(),
        sources: [source],
      );
      await m.initialize();
      await m.dispose();
      expect(source.disposed, isTrue);
    });
  });
}
