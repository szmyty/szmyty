import 'package:egohygiene/shared/health/impl/practice_signal_source.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('PracticeSignalSource', () {
    test('sourceId is "practice"', () {
      final source = PracticeSignalSource(
        completionLoader: () async => const [],
      );
      expect(source.sourceId, 'practice');
    });

    test('displayName is human readable', () {
      final source = PracticeSignalSource(
        completionLoader: () async => const [],
      );
      expect(source.displayName, isNotEmpty);
    });

    test('collectTimestamps() returns empty map (practices are global signals)', () async {
      final now = DateTime.utc(2026, 7, 3, 12);
      final source = PracticeSignalSource(
        completionLoader: () async => [
          now.subtract(const Duration(days: 1)),
          now.subtract(const Duration(days: 2)),
        ],
      );

      final timestamps = await source.collectTimestamps();

      expect(timestamps, isEmpty);
    });

    test('collectPracticeTimestamps() returns all completion timestamps', () async {
      final now = DateTime.utc(2026, 7, 3, 12);
      final ts1 = now.subtract(const Duration(days: 1));
      final ts2 = now.subtract(const Duration(days: 4));
      final ts3 = now.subtract(const Duration(days: 7));

      final source = PracticeSignalSource(
        completionLoader: () async => [ts1, ts2, ts3],
      );

      final timestamps = await source.collectPracticeTimestamps();

      expect(timestamps, containsAll([ts1, ts2, ts3]));
      expect(timestamps, hasLength(3));
    });

    test('collectPracticeTimestamps() returns empty list when no completions', () async {
      final source = PracticeSignalSource(
        completionLoader: () async => const [],
      );

      final timestamps = await source.collectPracticeTimestamps();

      expect(timestamps, isEmpty);
    });

    test('collectPracticeTimestamps() suppresses loader failures', () async {
      final source = PracticeSignalSource(
        completionLoader: () async => throw Exception('loader failure'),
      );

      // Must not throw.
      final timestamps = await source.collectPracticeTimestamps();

      expect(timestamps, isEmpty);
    });

    test('collectReflectionTimestamps() returns empty list (reflections are separate)', () async {
      final now = DateTime.utc(2026, 7, 3, 12);
      final source = PracticeSignalSource(
        completionLoader: () async => [now.subtract(const Duration(days: 1))],
      );

      final timestamps = await source.collectReflectionTimestamps();

      expect(timestamps, isEmpty);
    });

    test('initialize() and dispose() complete without error', () async {
      final source = PracticeSignalSource(
        completionLoader: () async => const [],
      );

      await expectLater(source.initialize(), completes);
      await expectLater(source.dispose(), completes);
    });
  });
}
