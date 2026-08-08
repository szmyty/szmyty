import 'package:egohygiene/shared/goal/goal.dart';
import 'package:egohygiene/shared/goal/goal_manager.dart';
import 'package:egohygiene/shared/goal/goal_priority.dart';
import 'package:egohygiene/shared/goal/goal_progress.dart';
import 'package:egohygiene/shared/goal/goal_source.dart';
import 'package:egohygiene/shared/goal/goal_status.dart';
import 'package:egohygiene/shared/goal/impl/in_memory_goal_store.dart';
import 'package:egohygiene/shared/goal/milestone.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

Goal _goal({
  String id = 'goal-1',
  String title = 'Test Goal',
  String? description,
  GoalStatus status = GoalStatus.active,
  GoalPriority priority = GoalPriority.medium,
  String? domain,
  List<String> relatedPracticeTypes = const [],
  List<Milestone> milestones = const [],
  DateTime? targetDate,
  List<String> tags = const [],
  String? notes,
  DateTime? createdAt,
  DateTime? updatedAt,
  DateTime? completedAt,
}) {
  final now = DateTime(2026, 1, 1, 10);
  return Goal(
    id: id,
    title: title,
    description: description,
    status: status,
    priority: priority,
    domain: domain,
    relatedPracticeTypes: relatedPracticeTypes,
    milestones: milestones,
    targetDate: targetDate,
    tags: tags,
    notes: notes,
    createdAt: createdAt ?? now,
    updatedAt: updatedAt ?? now,
    completedAt: completedAt,
  );
}

Milestone _milestone({
  String id = 'ms-1',
  String title = 'Test Milestone',
  String? description,
  bool isCompleted = false,
  DateTime? completedAt,
  DateTime? targetDate,
}) {
  return Milestone(
    id: id,
    title: title,
    description: description,
    isCompleted: isCompleted,
    completedAt: completedAt,
    targetDate: targetDate,
  );
}

/// A [GoalSource] that returns a fixed list of goals.
class _FixedGoalSource implements GoalSource {
  _FixedGoalSource({
    required this.sourceId,
    this.displayName = 'Fixed Source',
    this._goals = const [],
    this.throwOnLoad = false,
  });

  @override
  final String sourceId;

  @override
  final String displayName;

  final List<Goal> _goals;
  final bool throwOnLoad;

  bool initialized = false;
  bool disposed = false;
  int loadCallCount = 0;

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<List<Goal>> loadGoals() async {
    loadCallCount++;
    if (throwOnLoad) throw Exception('source failure');
    return List<Goal>.of(_goals);
  }

  @override
  Future<void> dispose() async => disposed = true;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── GoalStatus ─────────────────────────────────────────────────────────────

  group('GoalStatus', () {
    test('has five statuses', () {
      expect(GoalStatus.values, hasLength(5));
    });

    test('contains all expected statuses', () {
      expect(
        GoalStatus.values,
        containsAll([
          GoalStatus.active,
          GoalStatus.paused,
          GoalStatus.completed,
          GoalStatus.archived,
          GoalStatus.cancelled,
        ]),
      );
    });

    test('isTerminal is true for completed and cancelled', () {
      expect(GoalStatus.completed.isTerminal, isTrue);
      expect(GoalStatus.cancelled.isTerminal, isTrue);
    });

    test('isTerminal is false for non-terminal statuses', () {
      expect(GoalStatus.active.isTerminal, isFalse);
      expect(GoalStatus.paused.isTerminal, isFalse);
      expect(GoalStatus.archived.isTerminal, isFalse);
    });
  });

  // ── GoalPriority ───────────────────────────────────────────────────────────

  group('GoalPriority', () {
    test('has four priority levels', () {
      expect(GoalPriority.values, hasLength(4));
    });

    test('contains all expected priorities', () {
      expect(
        GoalPriority.values,
        containsAll([
          GoalPriority.low,
          GoalPriority.medium,
          GoalPriority.high,
          GoalPriority.critical,
        ]),
      );
    });

    test('defaultPriority is medium', () {
      expect(GoalPriority.defaultPriority, GoalPriority.medium);
    });
  });

  // ── Milestone ──────────────────────────────────────────────────────────────

  group('Milestone', () {
    test('constructs with required fields', () {
      final ms = _milestone();
      expect(ms.id, 'ms-1');
      expect(ms.title, 'Test Milestone');
      expect(ms.isCompleted, isFalse);
      expect(ms.completedAt, isNull);
      expect(ms.description, isNull);
      expect(ms.metadata, isEmpty);
    });

    test('copyWith replaces specified fields', () {
      final original = _milestone(id: 'ms-orig', title: 'Original');
      final updated = original.copyWith(
        title: 'Updated',
        isCompleted: true,
        completedAt: DateTime(2026, 3),
      );
      expect(updated.id, 'ms-orig');
      expect(updated.title, 'Updated');
      expect(updated.isCompleted, isTrue);
      expect(updated.completedAt, isNotNull);
    });

    test('equality is based on id', () {
      final a = _milestone(id: 'x', title: 'A');
      final b = _milestone(id: 'x', title: 'B');
      expect(a, equals(b));
    });

    test('different id produces different identity', () {
      final a = _milestone(id: 'a');
      final b = _milestone(id: 'b');
      expect(a, isNot(equals(b)));
    });

    test('toString includes id, title, and isCompleted', () {
      final ms = _milestone(id: 'abc', title: 'My Milestone');
      expect(ms.toString(), contains('abc'));
      expect(ms.toString(), contains('My Milestone'));
    });
  });

  // ── Goal ───────────────────────────────────────────────────────────────────

  group('Goal', () {
    test('constructs with required fields', () {
      final g = _goal();
      expect(g.id, 'goal-1');
      expect(g.title, 'Test Goal');
      expect(g.status, GoalStatus.active);
      expect(g.priority, GoalPriority.medium);
      expect(g.description, isNull);
      expect(g.domain, isNull);
      expect(g.relatedPracticeTypes, isEmpty);
      expect(g.milestones, isEmpty);
      expect(g.tags, isEmpty);
      expect(g.notes, isNull);
      expect(g.completedAt, isNull);
      expect(g.metadata, isEmpty);
    });

    test('copyWith replaces specified fields', () {
      final original = _goal(id: 'orig', title: 'Original');
      final updated = original.copyWith(
        title: 'Updated',
        status: GoalStatus.completed,
        priority: GoalPriority.high,
        domain: 'physical',
        notes: 'some notes',
      );
      expect(updated.id, 'orig');
      expect(updated.title, 'Updated');
      expect(updated.status, GoalStatus.completed);
      expect(updated.priority, GoalPriority.high);
      expect(updated.domain, 'physical');
      expect(updated.notes, 'some notes');
    });

    test('equality is based on id', () {
      final a = _goal(id: 'x', title: 'A');
      final b = _goal(id: 'x', title: 'B');
      expect(a, equals(b));
    });

    test('different id produces different identity', () {
      final a = _goal(id: 'a');
      final b = _goal(id: 'b');
      expect(a, isNot(equals(b)));
    });

    test('toString includes id, title, status, and priority', () {
      final g = _goal(
        id: 'g-1',
        title: 'Meditation Goal',
        priority: GoalPriority.high,
      );
      expect(g.toString(), contains('g-1'));
      expect(g.toString(), contains('Meditation Goal'));
      expect(g.toString(), contains('active'));
      expect(g.toString(), contains('high'));
    });

    test('supports relatedPracticeTypes', () {
      final g = _goal(relatedPracticeTypes: ['mindfulness', 'journaling']);
      expect(g.relatedPracticeTypes, hasLength(2));
      expect(g.relatedPracticeTypes, contains('mindfulness'));
    });

    test('supports tags', () {
      final g = _goal(tags: ['wellness', 'mental-health']);
      expect(g.tags, hasLength(2));
      expect(g.tags, contains('wellness'));
    });
  });

  // ── GoalProgress ───────────────────────────────────────────────────────────

  group('GoalProgress', () {
    test('empty returns zero progress', () {
      final progress = GoalProgress.empty(
        goalId: 'goal-1',
        isComplete: false,
        computedAt: DateTime(2026),
      );
      expect(progress.totalMilestones, 0);
      expect(progress.completedMilestones, 0);
      expect(progress.progressPercent, 0.0);
      expect(progress.isComplete, isFalse);
    });

    test('empty with isComplete true returns 1.0 percent', () {
      final progress = GoalProgress.empty(
        goalId: 'goal-1',
        isComplete: true,
      );
      expect(progress.progressPercent, 1.0);
    });

    test('compute returns 0% when no milestones and not complete', () {
      final g = _goal();
      final progress = GoalProgress.compute(g);
      expect(progress.progressPercent, 0.0);
      expect(progress.isComplete, isFalse);
    });

    test('compute returns 100% for completed goal with no milestones', () {
      final g = _goal(status: GoalStatus.completed);
      final progress = GoalProgress.compute(g);
      expect(progress.progressPercent, 1.0);
      expect(progress.isComplete, isTrue);
    });

    test('compute calculates partial progress correctly', () {
      final ms1 = _milestone(isCompleted: true);
      final ms2 = _milestone(id: 'ms-2');
      final ms3 = _milestone(id: 'ms-3');
      final g = _goal(milestones: [ms1, ms2, ms3]);
      final progress = GoalProgress.compute(g);
      expect(progress.totalMilestones, 3);
      expect(progress.completedMilestones, 1);
      expect(progress.progressPercent, closeTo(1.0 / 3.0, 0.001));
      expect(progress.isComplete, isFalse);
    });

    test('compute returns 100% when all milestones complete', () {
      final ms1 = _milestone(isCompleted: true);
      final ms2 = _milestone(id: 'ms-2', isCompleted: true);
      final g = _goal(milestones: [ms1, ms2]);
      final progress = GoalProgress.compute(g);
      expect(progress.totalMilestones, 2);
      expect(progress.completedMilestones, 2);
      expect(progress.progressPercent, 1.0);
      expect(progress.isComplete, isTrue);
    });

    test('compute isComplete when goal is cancelled', () {
      final g = _goal(status: GoalStatus.cancelled);
      final progress = GoalProgress.compute(g);
      expect(progress.isComplete, isTrue);
    });

    test('compute isComplete when goal is archived is false', () {
      final g = _goal(status: GoalStatus.archived);
      final progress = GoalProgress.compute(g);
      expect(progress.isComplete, isFalse);
    });

    test('toString includes goalId and percentages', () {
      final ms1 = _milestone(isCompleted: true);
      final ms2 = _milestone(id: 'ms-2');
      final g = _goal(id: 'g-42', milestones: [ms1, ms2]);
      final progress = GoalProgress.compute(g);
      expect(progress.toString(), contains('g-42'));
      expect(progress.toString(), contains('1/2'));
    });
  });

  // ── InMemoryGoalStore ──────────────────────────────────────────────────────

  group('InMemoryGoalStore', () {
    late InMemoryGoalStore store;

    setUp(() async {
      store = InMemoryGoalStore();
      await store.init();
    });

    test('init is idempotent', () async {
      await store.init();
      await store.init();
      expect(await store.count(), 0);
    });

    test('findById returns null for unknown id', () async {
      expect(await store.findById('missing'), isNull);
    });

    test('save and findById round-trip', () async {
      final g = _goal(id: 'g-1');
      await store.save(g);
      final retrieved = await store.findById('g-1');
      expect(retrieved, equals(g));
    });

    test('save replaces existing entry with same id', () async {
      final original = _goal(id: 'g-1', title: 'Original');
      final updated = _goal(id: 'g-1', title: 'Updated');
      await store.save(original);
      await store.save(updated);
      final retrieved = await store.findById('g-1');
      expect(retrieved!.title, 'Updated');
    });

    test('findAll returns goals sorted by createdAt ascending', () async {
      final early = _goal(
        id: 'g-early',
        createdAt: DateTime(2026),
        updatedAt: DateTime(2026),
      );
      final late = _goal(
        id: 'g-late',
        createdAt: DateTime(2026, 6),
        updatedAt: DateTime(2026, 6),
      );
      await store.save(late);
      await store.save(early);
      final all = await store.findAll();
      expect(all.first.id, 'g-early');
      expect(all.last.id, 'g-late');
    });

    test('findByStatus returns only matching goals', () async {
      final active = _goal(id: 'g-active');
      final completed = _goal(id: 'g-done', status: GoalStatus.completed);
      await store.save(active);
      await store.save(completed);
      final actives = await store.findByStatus(GoalStatus.active);
      expect(actives, hasLength(1));
      expect(actives.first.id, 'g-active');
    });

    test('findByDomain returns only matching goals', () async {
      final physical = _goal(id: 'g-phys', domain: 'physical');
      final mental = _goal(id: 'g-mental', domain: 'mentalEmotional');
      await store.save(physical);
      await store.save(mental);
      final physicals = await store.findByDomain('physical');
      expect(physicals, hasLength(1));
      expect(physicals.first.id, 'g-phys');
    });

    test('saveAll persists all goals', () async {
      final goals = [_goal(id: 'g-1'), _goal(id: 'g-2'), _goal(id: 'g-3')];
      await store.saveAll(goals);
      expect(await store.count(), 3);
    });

    test('deleteById removes the goal', () async {
      await store.save(_goal(id: 'g-1'));
      await store.deleteById('g-1');
      expect(await store.findById('g-1'), isNull);
    });

    test('deleteById is no-op for missing id', () async {
      await store.save(_goal(id: 'g-1'));
      await store.deleteById('missing');
      expect(await store.count(), 1);
    });

    test('clear removes all goals', () async {
      await store.saveAll([_goal(id: 'g-1'), _goal(id: 'g-2')]);
      await store.clear();
      expect(await store.count(), 0);
    });

    test('count returns correct number of goals', () async {
      await store.save(_goal(id: 'g-1'));
      await store.save(_goal(id: 'g-2'));
      expect(await store.count(), 2);
    });
  });

  // ── GoalManager ────────────────────────────────────────────────────────────

  group('GoalManager', () {
    late InMemoryGoalStore store;
    late GoalManager manager;

    setUp(() async {
      store = InMemoryGoalStore();
      manager = GoalManager(store: store);
      await manager.initialize();
    });

    tearDown(() async {
      await manager.dispose();
    });

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    test('initialize is idempotent', () async {
      await manager.initialize();
      await manager.initialize();
      expect(await store.count(), 0);
    });

    test('dispose marks manager as uninitialized', () async {
      await manager.dispose();
      // Re-initialize should work cleanly.
      await manager.initialize();
      expect(await store.count(), 0);
    });

    // ── Sources ───────────────────────────────────────────────────────────────

    test('sources is initially empty', () {
      expect(manager.sources, isEmpty);
    });

    test('registerSource adds a source', () {
      final source = _FixedGoalSource(sourceId: 'test-source');
      manager.registerSource(source);
      expect(manager.sources, hasLength(1));
    });

    test('sources list is unmodifiable', () {
      expect(() => manager.sources.add(_FixedGoalSource(sourceId: 'x')), throwsUnsupportedError);
    });

    test('registered sources are initialized at initialize()', () async {
      final source = _FixedGoalSource(sourceId: 's1');
      final mgr = GoalManager(store: store, sources: [source]);
      await mgr.initialize();
      expect(source.initialized, isTrue);
      await mgr.dispose();
    });

    test('registered sources are disposed at dispose()', () async {
      final source = _FixedGoalSource(sourceId: 's1');
      final mgr = GoalManager(store: store, sources: [source]);
      await mgr.initialize();
      await mgr.dispose();
      expect(source.disposed, isTrue);
    });

    test('failing source does not crash getAllGoals()', () async {
      final failingSource = _FixedGoalSource(
        sourceId: 'bad-source',
        throwOnLoad: true,
      );
      manager.registerSource(failingSource);
      final goals = await manager.getAllGoals();
      expect(goals, isEmpty);
    });

    // ── Goal creation ─────────────────────────────────────────────────────────

    test('createGoal persists a goal and returns it', () async {
      final goal = await manager.createGoal(title: 'My Goal');
      expect(goal.title, 'My Goal');
      expect(goal.status, GoalStatus.active);
      expect(goal.priority, GoalPriority.medium);
      expect(await store.count(), 1);
    });

    test('createGoal uses provided id', () async {
      final goal = await manager.createGoal(id: 'g-custom', title: 'Custom');
      expect(goal.id, 'g-custom');
    });

    test('createGoal sets domain and relatedPracticeTypes', () async {
      final goal = await manager.createGoal(
        title: 'Fitness Goal',
        domain: 'physical',
        relatedPracticeTypes: ['mindfulness', 'sleepHygiene'],
      );
      expect(goal.domain, 'physical');
      expect(goal.relatedPracticeTypes, hasLength(2));
    });

    test('createGoal sets priority', () async {
      final goal = await manager.createGoal(
        title: 'Urgent Goal',
        priority: GoalPriority.critical,
      );
      expect(goal.priority, GoalPriority.critical);
    });

    test('createGoal sets initial milestones', () async {
      final ms = _milestone(id: 'ms-init');
      final goal = await manager.createGoal(
        title: 'Milestone Goal',
        milestones: [ms],
      );
      expect(goal.milestones, hasLength(1));
      expect(goal.milestones.first.id, 'ms-init');
    });

    // ── Goal updates ──────────────────────────────────────────────────────────

    test('updateGoal persists changes', () async {
      final created = await manager.createGoal(id: 'g-1', title: 'Original');
      final modified = created.copyWith(title: 'Updated', notes: 'notes here');
      final updated = await manager.updateGoal(modified);
      expect(updated.title, 'Updated');
      expect(updated.notes, 'notes here');
      final retrieved = await store.findById('g-1');
      expect(retrieved!.title, 'Updated');
    });

    test('updateGoal stamps updatedAt', () async {
      final created = await manager.createGoal(id: 'g-1', title: 'Goal');
      final before = created.updatedAt;
      await Future<void>.delayed(const Duration(milliseconds: 1));
      final updated = await manager.updateGoal(created.copyWith(title: 'New'));
      expect(updated.updatedAt.isAfter(before), isTrue);
    });

    test('deleteGoal removes the goal', () async {
      await manager.createGoal(id: 'g-1', title: 'Goal');
      await manager.deleteGoal('g-1');
      expect(await store.findById('g-1'), isNull);
    });

    test('deleteGoal is no-op for missing id', () async {
      await manager.createGoal(id: 'g-1', title: 'Goal');
      await manager.deleteGoal('missing');
      expect(await store.count(), 1);
    });

    // ── Retrieval ─────────────────────────────────────────────────────────────

    test('getGoal returns the goal by id', () async {
      await manager.createGoal(id: 'g-1', title: 'My Goal');
      final goal = await manager.getGoal('g-1');
      expect(goal, isNotNull);
      expect(goal!.title, 'My Goal');
    });

    test('getGoal returns null for missing id', () async {
      expect(await manager.getGoal('missing'), isNull);
    });

    test('getAllGoals merges native and source goals by id', () async {
      await manager.createGoal(id: 'g-native', title: 'Native');
      final source = _FixedGoalSource(
        sourceId: 's1',
        goals: [_goal(id: 'g-external', title: 'External')],
      );
      manager.registerSource(source);
      final all = await manager.getAllGoals();
      expect(all, hasLength(2));
      expect(all.map((g) => g.id), containsAll(['g-native', 'g-external']));
    });

    test('getAllGoals deduplicates by id (native wins via upsert)', () async {
      await manager.createGoal(id: 'g-1', title: 'Native');
      final source = _FixedGoalSource(
        sourceId: 's1',
        goals: [_goal(id: 'g-1', title: 'Source')],
      );
      manager.registerSource(source);
      final all = await manager.getAllGoals();
      expect(all, hasLength(1));
    });

    test('getAllGoals is sorted by createdAt ascending', () async {
      await manager.createGoal(
        id: 'g-late',
        title: 'Late',
        createdAt: DateTime(2026, 6),
      );
      await manager.createGoal(
        id: 'g-early',
        title: 'Early',
        createdAt: DateTime(2026),
      );
      final all = await manager.getAllGoals();
      expect(all.first.id, 'g-early');
      expect(all.last.id, 'g-late');
    });

    test('getActiveGoals returns only active goals', () async {
      await manager.createGoal(id: 'g-active', title: 'Active');
      final completed = (await manager.createGoal(id: 'g-done', title: 'Done')).copyWith(status: GoalStatus.completed);
      await store.save(completed);
      final actives = await manager.getActiveGoals();
      expect(actives, hasLength(1));
      expect(actives.first.id, 'g-active');
    });

    test('getGoalsByStatus filters correctly', () async {
      await manager.createGoal(id: 'g-1', title: 'Active 1');
      await manager.createGoal(id: 'g-2', title: 'Active 2');
      final paused = (await manager.createGoal(id: 'g-3', title: 'Paused')).copyWith(status: GoalStatus.paused);
      await store.save(paused);
      final pausedGoals = await manager.getGoalsByStatus(GoalStatus.paused);
      expect(pausedGoals, hasLength(1));
      expect(pausedGoals.first.id, 'g-3');
    });

    test('getGoalsByDomain returns only matching goals', () async {
      await manager.createGoal(id: 'g-phys', title: 'Physical', domain: 'physical');
      await manager.createGoal(id: 'g-mental', title: 'Mental', domain: 'mentalEmotional');
      final physical = await manager.getGoalsByDomain('physical');
      expect(physical, hasLength(1));
      expect(physical.first.id, 'g-phys');
    });

    // ── Milestone management ──────────────────────────────────────────────────

    test('addMilestone appends to goal milestones', () async {
      await manager.createGoal(id: 'g-1', title: 'Goal');
      final ms = _milestone(title: 'Step 1');
      final updated = await manager.addMilestone('g-1', ms);
      expect(updated, isNotNull);
      expect(updated!.milestones, hasLength(1));
      expect(updated.milestones.first.id, 'ms-1');
    });

    test('addMilestone returns null for unknown goalId', () async {
      final ms = _milestone();
      expect(await manager.addMilestone('missing', ms), isNull);
    });

    test('completeMilestone marks milestone as done', () async {
      final ms = _milestone();
      await manager.createGoal(id: 'g-1', title: 'Goal', milestones: [ms]);
      final updated = await manager.completeMilestone('g-1', 'ms-1');
      expect(updated, isNotNull);
      expect(updated!.milestones.first.isCompleted, isTrue);
      expect(updated.milestones.first.completedAt, isNotNull);
    });

    test('completeMilestone returns null for unknown goalId', () async {
      expect(await manager.completeMilestone('missing', 'ms-1'), isNull);
    });

    test('completeMilestone returns null for unknown milestoneId', () async {
      await manager.createGoal(id: 'g-1', title: 'Goal');
      expect(await manager.completeMilestone('g-1', 'missing'), isNull);
    });

    test('completeMilestone accepts custom completedAt', () async {
      final ms = _milestone();
      await manager.createGoal(id: 'g-1', title: 'Goal', milestones: [ms]);
      final customTime = DateTime(2026, 5, 15, 12);
      final updated = await manager.completeMilestone('g-1', 'ms-1', completedAt: customTime);
      expect(updated!.milestones.first.completedAt, customTime);
    });

    // ── Goal completion ───────────────────────────────────────────────────────

    test('completeGoal marks goal as completed', () async {
      await manager.createGoal(id: 'g-1', title: 'Goal');
      final completed = await manager.completeGoal('g-1');
      expect(completed, isNotNull);
      expect(completed!.status, GoalStatus.completed);
      expect(completed.completedAt, isNotNull);
    });

    test('completeGoal accepts custom completedAt', () async {
      await manager.createGoal(id: 'g-1', title: 'Goal');
      final customTime = DateTime(2026, 12, 31);
      final completed = await manager.completeGoal('g-1', completedAt: customTime);
      expect(completed!.completedAt, customTime);
    });

    test('completeGoal returns null for unknown id', () async {
      expect(await manager.completeGoal('missing'), isNull);
    });

    // ── Progress ──────────────────────────────────────────────────────────────

    test('getProgress returns null for missing goal', () async {
      expect(await manager.getProgress('missing'), isNull);
    });

    test('getProgress returns zero progress for new goal', () async {
      await manager.createGoal(id: 'g-1', title: 'Goal');
      final progress = await manager.getProgress('g-1');
      expect(progress, isNotNull);
      expect(progress!.progressPercent, 0.0);
      expect(progress.isComplete, isFalse);
    });

    test('getProgress reflects milestone completions', () async {
      final ms1 = _milestone(isCompleted: true);
      final ms2 = _milestone(id: 'ms-2');
      await manager.createGoal(id: 'g-1', title: 'Goal', milestones: [ms1, ms2]);
      final progress = await manager.getProgress('g-1');
      expect(progress!.totalMilestones, 2);
      expect(progress.completedMilestones, 1);
      expect(progress.progressPercent, 0.5);
    });

    test('getProgress returns 100% for completed goal', () async {
      await manager.createGoal(id: 'g-1', title: 'Goal');
      await manager.completeGoal('g-1');
      final progress = await manager.getProgress('g-1');
      expect(progress!.progressPercent, 1.0);
      expect(progress.isComplete, isTrue);
    });
  });

  // ── GoalSource contract ────────────────────────────────────────────────────

  group('GoalSource contract', () {
    test('_FixedGoalSource initializes and reports correctly', () async {
      final source = _FixedGoalSource(
        sourceId: 'test-src',
        displayName: 'Test Source',
        goals: [_goal(id: 'g-ext')],
      );
      expect(source.initialized, isFalse);
      await source.initialize();
      expect(source.initialized, isTrue);
      final goals = await source.loadGoals();
      expect(goals, hasLength(1));
      expect(goals.first.id, 'g-ext');
      await source.dispose();
      expect(source.disposed, isTrue);
    });

    test('_FixedGoalSource tracks load call count', () async {
      final source = _FixedGoalSource(sourceId: 'src');
      await source.loadGoals();
      await source.loadGoals();
      expect(source.loadCallCount, 2);
    });

    test('failing source returns empty via manager (not rethrown)', () async {
      final store = InMemoryGoalStore();
      await store.init();
      final source = _FixedGoalSource(sourceId: 'bad', throwOnLoad: true);
      final mgr = GoalManager(store: store, sources: [source]);
      await mgr.initialize();
      expect(await mgr.getAllGoals(), isEmpty);
      await mgr.dispose();
    });
  });
}
