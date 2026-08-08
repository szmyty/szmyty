import 'package:egohygiene/features/check_in/domain/check_in_entry.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('CheckInEntry', () {
    final createdAt = DateTime.parse('2026-07-01T08:00:00.000Z');
    final updatedAt = DateTime.parse('2026-07-01T08:01:00.000Z');

    CheckInEntry entry0({
      String id = 'checkin_1',
      int mood = 4,
      int energy = 3,
      int stress = 2,
      double sleepHours = 7.5,
      int focus = 4,
      String? gratitude = 'Morning coffee',
      String? note = 'Felt grounded today.',
    }) {
      return CheckInEntry(
        id: id,
        createdAt: createdAt,
        updatedAt: updatedAt,
        mood: mood,
        energy: energy,
        stress: stress,
        sleepHours: sleepHours,
        focus: focus,
        gratitude: gratitude,
        note: note,
      );
    }

    test('serializes and deserializes correctly', () {
      final entry = entry0();
      final json = entry.toJson();
      final fromJson = CheckInEntry.fromJson(Map<String, dynamic>.from(json));
      expect(fromJson, entry);
    });

    test('round-trips with null optional fields', () {
      final entry = entry0(gratitude: null, note: null);
      final json = entry.toJson();
      final fromJson = CheckInEntry.fromJson(Map<String, dynamic>.from(json));
      expect(fromJson, entry);
      expect(fromJson.gratitude, isNull);
      expect(fromJson.note, isNull);
    });

    test('copyWith applies updated fields and preserves others', () {
      final base = entry0();
      final updated = base.copyWith(mood: 5, note: 'Changed note');
      expect(updated.id, base.id);
      expect(updated.createdAt, base.createdAt);
      expect(updated.mood, 5);
      expect(updated.energy, base.energy);
      expect(updated.note, 'Changed note');
      expect(updated.gratitude, base.gratitude);
    });

    test('equality holds for identical entries', () {
      final a = entry0();
      final b = entry0();
      expect(a, equals(b));
      expect(a.hashCode, equals(b.hashCode));
    });

    test('inequality when any field differs', () {
      expect(entry0(), isNot(equals(entry0(mood: 3))));
      expect(entry0(), isNot(equals(entry0(sleepHours: 6))));
    });

    test('toJson encodes sleepHours as double', () {
      final json = entry0().toJson();
      expect(json['sleepHours'], 7.5);
    });

    test('fromJson handles integer sleepHours from JSON', () {
      final json = entry0(sleepHours: 7).toJson()..['sleepHours'] = 7;
      final entry = CheckInEntry.fromJson(Map<String, dynamic>.from(json));
      expect(entry.sleepHours, 7.0);
    });
  });
}
