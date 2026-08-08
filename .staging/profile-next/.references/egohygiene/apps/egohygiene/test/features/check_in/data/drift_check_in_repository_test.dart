import 'package:drift/native.dart';
import 'package:egohygiene/features/check_in/data/drift_check_in_repository.dart';
import 'package:egohygiene/features/check_in/domain/check_in_entry.dart';
import 'package:egohygiene/shared/storage/app_database.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('DriftCheckInRepository', () {
    late AppDatabase database;
    late DriftCheckInRepository repository;

    setUp(() {
      database = AppDatabase(executor: NativeDatabase.memory());
      repository = DriftCheckInRepository(database: database);
    });

    tearDown(() async {
      await database.close();
    });

    test('returns newest entry first from getAll', () async {
      var now = DateTime.parse('2026-07-01T08:00:00.000Z');
      repository = DriftCheckInRepository(
        database: database,
        clock: () {
          final current = now;
          now = now.add(const Duration(hours: 1));
          return current;
        },
      );

      final first = await repository.create(
        mood: 3,
        energy: 3,
        stress: 2,
        sleepHours: 7,
        focus: 3,
      );
      final second = await repository.create(
        mood: 4,
        energy: 4,
        stress: 1,
        sleepHours: 8,
        focus: 4,
      );

      final all = await repository.getAll();
      expect(all.map((entry) => entry.id).toList(), [second.id, first.id]);
    });

    test('normalizes optional text and validates ranges', () async {
      final entry = await repository.create(
        mood: 3,
        energy: 3,
        stress: 2,
        sleepHours: 7,
        focus: 3,
        gratitude: '  morning coffee  ',
        note: '  felt okay  ',
      );

      expect(entry.gratitude, 'morning coffee');
      expect(entry.note, 'felt okay');
      await expectLater(
        () => repository.create(
          mood: 6,
          energy: 3,
          stress: 2,
          sleepHours: 7,
          focus: 3,
        ),
        throwsA(isA<ArgumentError>()),
      );
    });

    test('getTodaysEntry returns current-day entry only', () async {
      final yesterday = DateTime.parse('2026-06-30T10:00:00.000Z');
      final today = DateTime.parse('2026-07-01T08:00:00.000Z');
      repository = DriftCheckInRepository(database: database, clock: () => yesterday);
      await repository.create(
        mood: 3,
        energy: 3,
        stress: 2,
        sleepHours: 7,
        focus: 3,
      );

      repository = DriftCheckInRepository(database: database, clock: () => today);
      expect(await repository.getTodaysEntry(), isNull);

      await repository.create(
        mood: 4,
        energy: 4,
        stress: 1,
        sleepHours: 8,
        focus: 4,
      );
      expect(await repository.getTodaysEntry(), isNotNull);
    });

    test('update is no-op for unknown id', () async {
      final unknown = CheckInEntry(
        id: 'unknown',
        createdAt: _epoch,
        updatedAt: _epoch,
        mood: 3,
        energy: 3,
        stress: 3,
        sleepHours: 7,
        focus: 3,
      );

      final result = await repository.update(unknown);
      expect(result, unknown);
      expect(await repository.getAll(), isEmpty);
    });

    test('deleteById removes entry', () async {
      final created = await repository.create(
        mood: 3,
        energy: 3,
        stress: 2,
        sleepHours: 7,
        focus: 3,
      );

      await repository.deleteById(created.id);
      expect(await repository.getById(created.id), isNull);
    });
  });
}

final _epoch = DateTime.utc(2026, 7, 1, 8);
