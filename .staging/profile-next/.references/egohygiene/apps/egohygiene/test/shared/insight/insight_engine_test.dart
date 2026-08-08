import 'package:egohygiene/shared/insight/insight_engine.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('DeterministicInsightGenerator', () {
    test('generates deterministic insights across required categories', () async {
      final now = DateTime.utc(2026, 7, 2, 12);
      const generator = DeterministicInsightGenerator();
      final input = InsightInput(
        now: now,
        reflectionTimestamps: [
          now.subtract(const Duration(days: 1)),
          now.subtract(const Duration(days: 2)),
          now.subtract(const Duration(days: 3)),
          now.subtract(const Duration(days: 8)),
          now.subtract(const Duration(days: 9)),
          now.subtract(const Duration(days: 10)),
        ],
        practiceCompletionTimestamps: [
          now.subtract(const Duration(days: 1)),
          now.subtract(const Duration(days: 2)),
          now.subtract(const Duration(days: 3)),
          now.subtract(const Duration(days: 8)),
          now.subtract(const Duration(days: 9)),
          now.subtract(const Duration(days: 10)),
        ],
        domainActivity: {
          'sleep': [now.subtract(const Duration(days: 20))],
          'focus': [
            now.subtract(const Duration(days: 8)),
            now.subtract(const Duration(days: 9)),
            now.subtract(const Duration(days: 10)),
          ],
        },
      );

      final insights = await generator.generate(input);
      final types = insights.map((item) => item.type).toSet();

      expect(types, contains(InsightType.reflectionConsistency));
      expect(types, contains(InsightType.practiceConsistency));
      expect(types, contains(InsightType.missedPractices));
      expect(types, contains(InsightType.positiveStreak));
      expect(types, contains(InsightType.decreasingActivity));
      expect(types, contains(InsightType.domainInactivity));
      expect(
        insights.where((item) => item.type == InsightType.domainInactivity).single.message,
        contains('sleep'),
      );
    });

    test('generates increasing activity when recent activity rises', () async {
      final now = DateTime.utc(2026, 7, 2, 12);
      const generator = DeterministicInsightGenerator();
      final input = InsightInput(
        now: now,
        reflectionTimestamps: [
          now.subtract(const Duration(days: 1)),
          now.subtract(const Duration(days: 2)),
          now.subtract(const Duration(days: 3)),
          now.subtract(const Duration(days: 12)),
        ],
        practiceCompletionTimestamps: [
          now.subtract(const Duration(days: 1)),
          now.subtract(const Duration(days: 2)),
        ],
        domainActivity: {
          'focus': [
            now.subtract(const Duration(days: 1)),
            now.subtract(const Duration(days: 2)),
          ],
        },
      );

      final insights = await generator.generate(input);
      final types = insights.map((item) => item.type).toSet();

      expect(types, contains(InsightType.increasingActivity));
      expect(types, isNot(contains(InsightType.decreasingActivity)));
    });
  });

  group('InsightEngine', () {
    test('aggregates results from registered generators', () async {
      final engine = InsightEngine(
        generators: const [
          _FakeGenerator(),
        ],
      );

      final insights = await engine.generateInsights(
        InsightInput(now: DateTime.utc(2026, 7, 2, 12)),
      );

      expect(insights, hasLength(1));
      expect(insights.single.type, InsightType.reflectionConsistency);
      expect(engine.generators, hasLength(1));
    });
  });
}

class _FakeGenerator implements InsightGenerator {
  const _FakeGenerator();

  @override
  Future<List<Insight>> generate(InsightInput input) async {
    return [
      Insight(
        id: 'fake',
        type: InsightType.reflectionConsistency,
        source: InsightSource.reflectionHistory,
        severity: InsightSeverity.low,
        message: 'fake',
        createdAt: input.now,
      ),
    ];
  }
}
