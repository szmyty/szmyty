import 'dart:convert';

import 'package:egohygiene/features/check_in/data/local_check_in_repository.dart';
import 'package:egohygiene/features/check_in/domain/check_in_entry.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../../helpers/fake_storage_service.dart';

void main() {
  group('LocalCheckInRepository', () {
    // -------------------------------------------------------------------------
    // create
    // -------------------------------------------------------------------------

    group('create', () {
      test('returns newest entry first from getAll', () async {
        var now = DateTime.parse('2026-07-01T08:00:00.000Z');
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
          clock: () {
            final t = now;
            now = now.add(const Duration(hours: 1));
            return t;
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
        expect(all.map((e) => e.id).toList(), [second.id, first.id]);
      });

      test('normalizes whitespace in gratitude and note', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );

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
      });

      test('stores null when gratitude and note are whitespace-only', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );

        final entry = await repository.create(
          mood: 3,
          energy: 3,
          stress: 2,
          sleepHours: 7,
          focus: 3,
          gratitude: '   ',
          note: '',
        );

        expect(entry.gratitude, isNull);
        expect(entry.note, isNull);
      });

      test('throws ArgumentError for out-of-range mood', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );

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
        await expectLater(
          () => repository.create(
            mood: 0,
            energy: 3,
            stress: 2,
            sleepHours: 7,
            focus: 3,
          ),
          throwsA(isA<ArgumentError>()),
        );
      });

      test('throws ArgumentError for out-of-range sleepHours', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );

        await expectLater(
          () => repository.create(
            mood: 3,
            energy: 3,
            stress: 2,
            sleepHours: 13,
            focus: 3,
          ),
          throwsA(isA<ArgumentError>()),
        );
        await expectLater(
          () => repository.create(
            mood: 3,
            energy: 3,
            stress: 2,
            sleepHours: -1,
            focus: 3,
          ),
          throwsA(isA<ArgumentError>()),
        );
      });
    });

    // -------------------------------------------------------------------------
    // getAll / getById
    // -------------------------------------------------------------------------

    group('getAll', () {
      test('returns empty list when no data is stored', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );
        expect(await repository.getAll(), isEmpty);
      });

      test('returns pre-seeded entries from storage', () async {
        final storage = FakeStorageService();
        final now = DateTime.parse('2026-07-01T08:00:00.000Z');
        final entry = CheckInEntry(
          id: 'checkin_seed',
          createdAt: now,
          updatedAt: now,
          mood: 4,
          energy: 3,
          stress: 2,
          sleepHours: 7,
          focus: 4,
        );
        await storage.save('check_in.entries.v1', jsonEncode([entry.toJson()]));

        final repository = LocalCheckInRepository(storage: storage);
        final all = await repository.getAll();
        expect(all, [entry]);
      });
    });

    group('getById', () {
      test('returns null for unknown id', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );
        expect(await repository.getById('no_such'), isNull);
      });

      test('returns correct entry by id', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );
        final created = await repository.create(
          mood: 5,
          energy: 5,
          stress: 1,
          sleepHours: 9,
          focus: 5,
        );
        final found = await repository.getById(created.id);
        expect(found, created);
      });
    });

    // -------------------------------------------------------------------------
    // getTodaysEntry
    // -------------------------------------------------------------------------

    group('getTodaysEntry', () {
      test('returns null when no check-in today', () async {
        final yesterday = DateTime.parse('2026-06-30T10:00:00.000Z');
        final today = DateTime.parse('2026-07-01T08:00:00.000Z');
        final storage = FakeStorageService();

        final repositoryYesterday = LocalCheckInRepository(
          storage: storage,
          clock: () => yesterday,
        );
        await repositoryYesterday.create(
          mood: 3,
          energy: 3,
          stress: 2,
          sleepHours: 7,
          focus: 3,
        );

        // Same storage, but clock returns today — yesterday's entry is not today
        final repositoryToday = LocalCheckInRepository(
          storage: storage,
          clock: () => today,
        );
        expect(await repositoryToday.getTodaysEntry(), isNull);
      });

      test('returns entry created today', () async {
        final today = DateTime.parse('2026-07-01T08:00:00.000Z');
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
          clock: () => today,
        );

        final created = await repository.create(
          mood: 4,
          energy: 4,
          stress: 2,
          sleepHours: 8,
          focus: 4,
        );
        final todays = await repository.getTodaysEntry();
        expect(todays, created);
      });
    });

    // -------------------------------------------------------------------------
    // update
    // -------------------------------------------------------------------------

    group('update', () {
      test('updates an existing entry', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );

        final created = await repository.create(
          mood: 3,
          energy: 3,
          stress: 3,
          sleepHours: 7,
          focus: 3,
        );
        final updated = await repository.update(
          created.copyWith(mood: 5, note: 'Updated'),
        );

        expect(updated.mood, 5);
        expect(updated.note, 'Updated');

        final found = await repository.getById(created.id);
        expect(found?.mood, 5);
      });

      test('is a no-op for an unknown entry id', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );
        final unknown = CheckInEntry(
          id: 'nonexistent',
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
    });

    // -------------------------------------------------------------------------
    // deleteById
    // -------------------------------------------------------------------------

    group('deleteById', () {
      test('removes the entry and leaves others intact', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );

        final a = await repository.create(
          mood: 3,
          energy: 3,
          stress: 2,
          sleepHours: 7,
          focus: 3,
        );
        final b = await repository.create(
          mood: 4,
          energy: 4,
          stress: 1,
          sleepHours: 8,
          focus: 4,
        );

        await repository.deleteById(a.id);

        final all = await repository.getAll();
        expect(all.map((e) => e.id), [b.id]);
      });

      test('is a no-op for an unknown id', () async {
        final repository = LocalCheckInRepository(
          storage: FakeStorageService(),
        );
        await repository.create(
          mood: 3,
          energy: 3,
          stress: 2,
          sleepHours: 7,
          focus: 3,
        );

        await repository.deleteById('no_such');
        expect(await repository.getAll(), hasLength(1));
      });
    });

    // -------------------------------------------------------------------------
    // persistence across instances
    // -------------------------------------------------------------------------

    test('persists entries across repository instances', () async {
      final storage = FakeStorageService();
      final repositoryA = LocalCheckInRepository(storage: storage);
      final created = await repositoryA.create(
        mood: 4,
        energy: 3,
        stress: 2,
        sleepHours: 7.5,
        focus: 4,
        gratitude: 'health',
      );

      final repositoryB = LocalCheckInRepository(storage: storage);
      final loaded = await repositoryB.getById(created.id);
      expect(loaded, created);
    });
  });
}

final _epoch = DateTime.utc(2026, 7, 1, 8);
