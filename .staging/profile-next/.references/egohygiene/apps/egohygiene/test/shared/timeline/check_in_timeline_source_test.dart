import 'package:egohygiene/features/check_in/feature.dart';
import 'package:egohygiene/shared/timeline/impl/check_in_timeline_source.dart';
import 'package:egohygiene/shared/timeline/timeline_event.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeCheckInRepository implements CheckInRepository {
  _FakeCheckInRepository(this._entries);

  final List<CheckInEntry> _entries;

  @override
  Future<List<CheckInEntry>> getAll() async => _entries;

  @override
  Future<CheckInEntry?> getById(String id) async => null;

  @override
  Future<CheckInEntry?> getTodaysEntry() async => null;

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
    throw UnimplementedError();
  }

  @override
  Future<CheckInEntry> update(CheckInEntry entry) async => entry;

  @override
  Future<void> deleteById(String id) async {}
}

void main() {
  group('CheckInTimelineSource', () {
    final now = DateTime.utc(2026, 7, 1, 8);

    final entry = CheckInEntry(
      id: 'checkin_1',
      createdAt: now,
      updatedAt: now,
      mood: 4,
      energy: 3,
      stress: 2,
      sleepHours: 7.5,
      focus: 4,
    );

    test('getEvents returns one event per check-in entry', () async {
      final source = CheckInTimelineSource(
        repository: _FakeCheckInRepository([entry]),
      );

      final events = await source.getEvents();

      expect(events, hasLength(1));
      expect(events.first.id, entry.id);
      expect(events.first.type, TimelineEventType.healthMetric);
      expect(events.first.occurredAt, now);
    });

    test('getEvents returns empty list when no entries', () async {
      final source = CheckInTimelineSource(
        repository: _FakeCheckInRepository(const []),
      );

      expect(await source.getEvents(), isEmpty);
    });

    test('event metadata contains mood, energy, stress, sleepHours, focus', () async {
      final source = CheckInTimelineSource(
        repository: _FakeCheckInRepository([entry]),
      );

      final events = await source.getEvents();
      final metadata = events.first.metadata;

      expect(metadata['mood'], 4);
      expect(metadata['energy'], 3);
      expect(metadata['stress'], 2);
      expect(metadata['sleepHours'], 7.5);
      expect(metadata['focus'], 4);
    });

    test('event metadata omits null gratitude and note', () async {
      final source = CheckInTimelineSource(
        repository: _FakeCheckInRepository([entry]),
      );

      final events = await source.getEvents();
      expect(events.first.metadata.containsKey('gratitude'), isFalse);
      expect(events.first.metadata.containsKey('note'), isFalse);
    });

    test('event metadata includes gratitude when set', () async {
      final entryWithGratitude = entry.copyWith(gratitude: 'morning walk');
      final source = CheckInTimelineSource(
        repository: _FakeCheckInRepository([entryWithGratitude]),
      );

      final events = await source.getEvents();
      expect(events.first.metadata['gratitude'], 'morning walk');
    });
  });
}
