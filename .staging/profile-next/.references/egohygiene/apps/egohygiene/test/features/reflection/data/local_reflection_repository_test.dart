import 'dart:convert';

import 'package:egohygiene/features/reflection/data/local_reflection_repository.dart';
import 'package:egohygiene/features/reflection/domain/reflection_model.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../../helpers/fake_storage_service.dart';

void main() {
  group('LocalReflectionRepository', () {
    test('creates and reads reflections in newest-first order', () async {
      final storage = FakeStorageService();
      var now = DateTime.parse('2026-06-21T12:00:00.000Z');
      final repository = LocalReflectionRepository(
        storage: storage,
        clock: () {
          final current = now;
          now = now.add(const Duration(minutes: 1));
          return current;
        },
      );

      final first = await repository.create(body: 'first');
      final second = await repository.create(body: 'second');

      final all = await repository.getAll();

      expect(all.map((item) => item.id).toList(), [second.id, first.id]);
      expect(all.first.body, 'second');
    });

    test('persists reflections in storage across repository instances', () async {
      final sharedStorage = FakeStorageService();
      final repositoryA = LocalReflectionRepository(storage: sharedStorage);
      final created = await repositoryA.create(
        title: 'Persisted',
        body: 'This should survive repository recreation.',
        tags: const ['journal'],
      );

      final repositoryB = LocalReflectionRepository(storage: sharedStorage);
      final loaded = await repositoryB.getById(created.id);

      expect(loaded, isNotNull);
      expect(loaded?.title, 'Persisted');
      expect(loaded?.tags, const ['journal']);
    });

    test('returns empty list for malformed storage payload', () async {
      final storage = FakeStorageService();
      await storage.save('reflection.entries.v1', jsonEncode({'unexpected': true}));
      final repository = LocalReflectionRepository(storage: storage);

      final result = await repository.getAll();

      expect(result, isEmpty);
    });

    test('parses valid serialized reflections from storage', () async {
      final storage = FakeStorageService();
      final reflection = ReflectionModel(
        id: 'seed-1',
        createdAt: DateTime.parse('2026-06-21T12:00:00.000Z'),
        updatedAt: DateTime.parse('2026-06-21T12:00:00.000Z'),
        title: 'Seeded reflection',
        body: 'Seed body',
        tags: const ['seeded'],
      );

      await storage.save('reflection.entries.v1', jsonEncode([reflection.toJson()]));
      final repository = LocalReflectionRepository(storage: storage);

      final all = await repository.getAll();

      expect(all, [reflection]);
    });

    test('normalizes tags and rejects blank bodies', () async {
      final repository = LocalReflectionRepository(storage: FakeStorageService());

      final created = await repository.create(
        body: '  Reflection body  ',
        tags: const [' clarity ', 'clarity', '', 'pattern'],
      );

      expect(created.body, 'Reflection body');
      expect(created.tags, const ['clarity', 'pattern']);
      await expectLater(
        () => repository.create(body: '   '),
        throwsA(isA<ArgumentError>()),
      );
    });

    // -------------------------------------------------------------------------
    // update
    // -------------------------------------------------------------------------

    group('update', () {
      test('updates an existing reflection', () async {
        final storage = FakeStorageService();
        var now = DateTime.parse('2026-06-21T12:00:00.000Z');
        final repository = LocalReflectionRepository(
          storage: storage,
          clock: () {
            final current = now;
            now = now.add(const Duration(minutes: 1));
            return current;
          },
        );

        final original = await repository.create(body: 'original body');
        final modified = original.copyWith(
          body: 'updated body',
          title: 'New Title',
          tags: const ['updated'],
        );

        final result = await repository.update(modified);

        expect(result.id, original.id);
        expect(result.body, 'updated body');
        expect(result.title, 'New Title');
        expect(result.tags, const ['updated']);
        expect(result.createdAt, original.createdAt);
        expect(result.updatedAt, isNot(equals(original.updatedAt)));
      });

      test('persisted update is visible in subsequent getAll', () async {
        final storage = FakeStorageService();
        final repository = LocalReflectionRepository(storage: storage);

        final created = await repository.create(body: 'before');
        await repository.update(created.copyWith(body: 'after'));

        final all = await repository.getAll();
        expect(all.first.body, 'after');
      });

      test('update trims body and title', () async {
        final repository = LocalReflectionRepository(storage: FakeStorageService());
        final created = await repository.create(body: 'body');
        final result = await repository.update(
          created.copyWith(body: '  trimmed body  ', title: '  trimmed title  '),
        );

        expect(result.body, 'trimmed body');
        expect(result.title, 'trimmed title');
      });

      test('update with blank title sets title to null', () async {
        final repository = LocalReflectionRepository(storage: FakeStorageService());
        final created = await repository.create(body: 'body', title: 'original');
        final result = await repository.update(
          created.copyWith(title: '   '),
        );

        expect(result.title, isNull);
      });

      test('update rejects blank body', () async {
        final repository = LocalReflectionRepository(storage: FakeStorageService());
        final created = await repository.create(body: 'original');

        await expectLater(
          () => repository.update(created.copyWith(body: '   ')),
          throwsA(isA<ArgumentError>()),
        );
      });

      test('update is a no-op when entity does not exist', () async {
        final repository = LocalReflectionRepository(storage: FakeStorageService());

        final phantom = ReflectionModel(
          id: 'non-existent',
          createdAt: DateTime.parse('2026-01-01T00:00:00.000Z'),
          updatedAt: DateTime.parse('2026-01-01T00:00:00.000Z'),
          body: 'phantom body',
        );

        final result = await repository.update(phantom);

        // No entity was created or written.
        expect(await repository.getAll(), isEmpty);
        // The returned value is the input unchanged.
        expect(result.id, phantom.id);
        expect(result.body, phantom.body);
      });
    });

    // -------------------------------------------------------------------------
    // deleteById
    // -------------------------------------------------------------------------

    group('deleteById', () {
      test('removes the reflection from storage', () async {
        final repository = LocalReflectionRepository(storage: FakeStorageService());
        final created = await repository.create(body: 'to delete');

        await repository.deleteById(created.id);

        expect(await repository.getById(created.id), isNull);
        expect(await repository.getAll(), isEmpty);
      });

      test('does not affect other reflections', () async {
        final repository = LocalReflectionRepository(storage: FakeStorageService());
        final a = await repository.create(body: 'keep me');
        final b = await repository.create(body: 'delete me');

        await repository.deleteById(b.id);

        final all = await repository.getAll();
        expect(all.map((r) => r.id), contains(a.id));
        expect(all.map((r) => r.id), isNot(contains(b.id)));
      });

      test('is a no-op for non-existent id', () async {
        final repository = LocalReflectionRepository(storage: FakeStorageService());
        await repository.create(body: 'survivor');

        await repository.deleteById('non-existent-id');

        expect(await repository.getAll(), hasLength(1));
      });
    });
  });
}
