import 'package:drift/native.dart';
import 'package:egohygiene/features/reflection/data/drift_reflection_repository.dart';
import 'package:egohygiene/features/reflection/domain/reflection_model.dart';
import 'package:egohygiene/shared/storage/app_database.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('DriftReflectionRepository', () {
    late AppDatabase database;
    late DriftReflectionRepository repository;

    setUp(() {
      database = AppDatabase(executor: NativeDatabase.memory());
      repository = DriftReflectionRepository(database: database);
    });

    tearDown(() async {
      await database.close();
    });

    test('creates and reads reflections in newest-first order', () async {
      var now = DateTime.parse('2026-06-21T12:00:00.000Z');
      repository = DriftReflectionRepository(
        database: database,
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
    });

    test('normalizes tags and rejects blank bodies', () async {
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

    test('update persists changes and sets updatedAt', () async {
      var now = DateTime.parse('2026-06-21T12:00:00.000Z');
      repository = DriftReflectionRepository(
        database: database,
        clock: () {
          final current = now;
          now = now.add(const Duration(minutes: 1));
          return current;
        },
      );
      final original = await repository.create(body: 'before');

      final updated = await repository.update(
        original.copyWith(body: 'after', title: '  Updated  '),
      );

      final loaded = await repository.getById(original.id);
      expect(updated.title, 'Updated');
      expect(updated.updatedAt, isNot(equals(original.updatedAt)));
      expect(loaded?.body, 'after');
    });

    test('update is a no-op for unknown id', () async {
      final phantom = ReflectionModel(
        id: 'missing',
        createdAt: DateTime.parse('2026-01-01T00:00:00.000Z'),
        updatedAt: DateTime.parse('2026-01-01T00:00:00.000Z'),
        body: 'ghost',
      );

      final result = await repository.update(phantom);
      expect(result, phantom);
      expect(await repository.getAll(), isEmpty);
    });

    test('deleteById removes reflection', () async {
      final created = await repository.create(body: 'to delete');
      await repository.deleteById(created.id);
      expect(await repository.getById(created.id), isNull);
    });
  });
}
