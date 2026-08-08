import 'package:egohygiene/features/reflection/domain/reflection_model.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ReflectionModel', () {
    test('serializes and deserializes correctly', () {
      final createdAt = DateTime.parse('2026-06-21T12:00:00.000Z');
      final updatedAt = DateTime.parse('2026-06-21T12:05:00.000Z');
      final model = ReflectionModel(
        id: 'reflection_1',
        createdAt: createdAt,
        updatedAt: updatedAt,
        title: 'Morning Reflection',
        body: 'Today I noticed I reacted less and listened more.',
        tags: const ['awareness', 'listening'],
      );

      final json = model.toJson();
      final fromJson = ReflectionModel.fromJson(Map<String, dynamic>.from(json));

      expect(fromJson, model);
    });

    test('copyWith applies updated fields and preserves others', () {
      final base = ReflectionModel(
        id: 'reflection_1',
        createdAt: DateTime.parse('2026-06-21T12:00:00.000Z'),
        updatedAt: DateTime.parse('2026-06-21T12:00:00.000Z'),
        body: 'Base body',
      );

      final updated = base.copyWith(title: 'Updated Title', body: 'Updated body');

      expect(updated.id, base.id);
      expect(updated.title, 'Updated Title');
      expect(updated.body, 'Updated body');
      expect(updated.createdAt, base.createdAt);
    });
  });
}
