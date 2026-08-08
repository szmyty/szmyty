import 'package:egohygiene/features/reflection/feature.dart';
import 'package:egohygiene/shared/goal/goal.dart';
import 'package:egohygiene/shared/goal/goal_priority.dart';
import 'package:egohygiene/shared/goal/goal_status.dart';
import 'package:egohygiene/shared/insight/insight.dart';
import 'package:egohygiene/shared/insight/insight_severity.dart';
import 'package:egohygiene/shared/insight/insight_source.dart';
import 'package:egohygiene/shared/insight/insight_type.dart';
import 'package:egohygiene/shared/timeline/timeline_engine.dart';
import 'package:flutter_test/flutter_test.dart';

class _FixedTimelineSource implements TimelineSource {
  _FixedTimelineSource({
    required this.sourceId,
    required this._events,
    this.throwOnGetEvents = false,
  }) : displayName = 'Fixed Source';

  @override
  final String sourceId;

  @override
  final String displayName;

  final List<TimelineEvent> _events;
  final bool throwOnGetEvents;

  bool initialized = false;
  bool disposed = false;

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<List<TimelineEvent>> getEvents() async {
    if (throwOnGetEvents) {
      throw Exception('source failure');
    }

    return _events;
  }

  @override
  Future<void> dispose() async => disposed = true;
}

class _InMemoryReflectionRepository implements ReflectionRepository {
  _InMemoryReflectionRepository({List<ReflectionModel>? seed})
    : _items = seed != null ? List<ReflectionModel>.of(seed) : [];

  final List<ReflectionModel> _items;

  @override
  Future<ReflectionModel> create({
    required String body,
    String? title,
    List<String> tags = const [],
  }) {
    throw UnimplementedError();
  }

  @override
  Future<void> deleteById(String id) {
    throw UnimplementedError();
  }

  @override
  Future<List<ReflectionModel>> getAll() async => List<ReflectionModel>.of(_items);

  @override
  Future<ReflectionModel?> getById(String id) {
    throw UnimplementedError();
  }

  @override
  Future<ReflectionModel> update(ReflectionModel reflection) {
    throw UnimplementedError();
  }
}

ReflectionModel _reflection({
  required String id,
  required String body,
  required DateTime createdAt,
  String? title,
  List<String> tags = const [],
}) {
  return ReflectionModel(
    id: id,
    createdAt: createdAt,
    updatedAt: createdAt,
    title: title,
    body: body,
    tags: tags,
  );
}

Insight _insight({
  required String id,
  required DateTime createdAt,
  String message = 'Insight message',
}) {
  return Insight(
    id: id,
    type: InsightType.reflectionConsistency,
    source: InsightSource.reflectionHistory,
    severity: InsightSeverity.low,
    message: message,
    createdAt: createdAt,
  );
}

Goal _goal({
  required String id,
  required String title,
  required DateTime createdAt,
  String? description,
  DateTime? targetDate,
  DateTime? completedAt,
  GoalStatus status = GoalStatus.active,
}) {
  return Goal(
    id: id,
    title: title,
    description: description,
    createdAt: createdAt,
    updatedAt: createdAt,
    targetDate: targetDate,
    completedAt: completedAt,
    status: status,
    priority: GoalPriority.high,
    tags: const ['growth'],
  );
}

void main() {
  group('TimelineManager', () {
    test('initialize() and dispose() call source lifecycle hooks', () async {
      final source = _FixedTimelineSource(
        sourceId: 'lifecycle',
        events: const [],
      );
      final manager = TimelineManager(sources: [source]);

      await manager.initialize();
      await manager.dispose();

      expect(source.initialized, isTrue);
      expect(source.disposed, isTrue);
    });

    test('collects and sorts events from all sources by recency', () async {
      final manager = TimelineManager(
        sources: [
          _FixedTimelineSource(
            sourceId: 'a',
            events: [
              TimelineEvent(
                id: 'older',
                type: TimelineEventType.goal,
                sourceId: 'a',
                occurredAt: DateTime(2026),
                title: 'Older',
              ),
            ],
          ),
          _FixedTimelineSource(
            sourceId: 'b',
            events: [
              TimelineEvent(
                id: 'newer',
                type: TimelineEventType.insight,
                sourceId: 'b',
                occurredAt: DateTime(2026, 1, 2),
                title: 'Newer',
              ),
            ],
          ),
        ],
      );

      final timeline = await manager.getTimeline();

      expect(timeline.map((event) => event.id), ['newer', 'older']);
    });

    test('suppresses source failures and still returns healthy source events', () async {
      Object? capturedError;
      StackTrace? capturedStackTrace;
      String? capturedSourceId;

      final manager = TimelineManager(
        onSourceError: (error, stackTrace, source) {
          capturedError = error;
          capturedStackTrace = stackTrace;
          capturedSourceId = source.sourceId;
        },
        sources: [
          _FixedTimelineSource(
            sourceId: 'broken',
            events: const [],
            throwOnGetEvents: true,
          ),
          _FixedTimelineSource(
            sourceId: 'healthy',
            events: [
              TimelineEvent(
                id: 'ok',
                type: TimelineEventType.reflection,
                sourceId: 'healthy',
                occurredAt: DateTime(2026, 1, 2),
                title: 'OK',
              ),
            ],
          ),
        ],
      );

      final timeline = await manager.getTimeline();

      expect(timeline, hasLength(1));
      expect(timeline.single.id, 'ok');
      expect(capturedError, isA<Exception>());
      expect(capturedStackTrace, isNotNull);
      expect(capturedSourceId, 'broken');
    });

    test('applies filtering by type, source, range, and query', () async {
      final manager = TimelineManager(
        sources: [
          _FixedTimelineSource(
            sourceId: 'reflection',
            events: [
              TimelineEvent(
                id: 'reflection-1',
                type: TimelineEventType.reflection,
                sourceId: 'reflection',
                occurredAt: DateTime(2026, 1, 2),
                title: 'Morning reflection',
                description: 'Felt grounded.',
              ),
            ],
          ),
          _FixedTimelineSource(
            sourceId: 'insight',
            events: [
              TimelineEvent(
                id: 'insight-1',
                type: TimelineEventType.insight,
                sourceId: 'insight',
                occurredAt: DateTime(2026),
                title: 'pattern found',
              ),
            ],
          ),
        ],
      );

      final timeline = await manager.getTimeline(
        filter: TimelineFilter(
          from: DateTime(2026, 1, 2),
          to: DateTime(2026, 1, 3),
          types: const {TimelineEventType.reflection},
          sourceIds: const {'reflection'},
          query: 'morning',
        ),
      );

      expect(timeline, hasLength(1));
      expect(timeline.single.id, 'reflection-1');
    });
  });

  group('ReflectionTimelineSource', () {
    test('maps reflections to timeline reflection events', () async {
      final source = ReflectionTimelineSource(
        repository: _InMemoryReflectionRepository(
          seed: [
            _reflection(
              id: 'r1',
              title: 'Title',
              body: 'Body',
              createdAt: DateTime(2026, 7),
              tags: const ['growth'],
            ),
          ],
        ),
      );

      final events = await source.getEvents();

      expect(events, hasLength(1));
      expect(events.single.type, TimelineEventType.reflection);
      expect(events.single.sourceId, ReflectionTimelineSource.id);
      expect(events.single.title, 'Title');
    });
  });

  group('PracticeTimelineSource', () {
    test('maps completion timestamps to practice completion events', () async {
      final source = PracticeTimelineSource(
        completionLoader: () async => [DateTime(2026, 7, 1, 8)],
      );

      final events = await source.getEvents();

      expect(events, hasLength(1));
      expect(events.single.type, TimelineEventType.practiceCompletion);
      expect(events.single.sourceId, PracticeTimelineSource.id);
      expect(events.single.title, 'Practice completed');
    });
  });

  group('InsightTimelineSource', () {
    test('maps insights to timeline insight events', () async {
      final source = InsightTimelineSource(
        insightLoader: () async => [
          _insight(id: 'i1', createdAt: DateTime(2026, 7), message: 'Insight!'),
        ],
      );

      final events = await source.getEvents();

      expect(events, hasLength(1));
      expect(events.single.id, 'i1');
      expect(events.single.type, TimelineEventType.insight);
      expect(events.single.description, 'Insight!');
    });
  });

  group('GoalTimelineSource', () {
    test('maps goals to timeline goal events', () async {
      final source = GoalTimelineSource(
        goalLoader: () async => [
          _goal(
            id: 'g1',
            title: 'Sleep more consistently',
            description: 'Aim for a steadier evening routine.',
            createdAt: DateTime(2026, 7),
            targetDate: DateTime(2026, 7, 10),
          ),
        ],
      );

      final events = await source.getEvents();

      expect(events, hasLength(1));
      expect(events.single.id, 'g1');
      expect(events.single.type, TimelineEventType.goal);
      expect(events.single.sourceId, GoalTimelineSource.id);
      expect(events.single.occurredAt, DateTime(2026, 7, 10));
      expect(events.single.metadata['priority'], 'high');
      expect(events.single.metadata['tags'], const ['growth']);
    });
  });
}
