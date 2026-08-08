import 'package:egohygiene/shared/health/domain_health_engine.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('PlaceholderDomainHealthCalculator', () {
    const calculator = PlaceholderDomainHealthCalculator();
    final now = DateTime.utc(2026, 7, 3, 12);

    test('returns unknown status and insufficient trend when no signals', () {
      final input = DomainHealthInput(now: now);
      final summary = calculator.calculate(HealthDomain.mentalEmotional, input);

      expect(summary.domain, HealthDomain.mentalEmotional);
      expect(summary.status, DomainStatus.unknown);
      expect(summary.trend, DomainTrend.insufficient);
      expect(summary.confidence, 0.0);
      expect(summary.supportingSignals, hasLength(1));
      expect(summary.supportingSignals.first.type, DomainSignalType.placeholder);
    });

    test('returns active status when recent domain check-ins are present', () {
      final input = DomainHealthInput(
        now: now,
        domainCheckIns: {
          HealthDomain.physical: [
            now.subtract(const Duration(days: 1)),
            now.subtract(const Duration(days: 2)),
            now.subtract(const Duration(days: 3)),
          ],
        },
      );

      final summary = calculator.calculate(HealthDomain.physical, input);

      expect(summary.status, DomainStatus.active);
      expect(summary.confidence, greaterThan(0.0));
    });

    test('returns improving trend when recent activity exceeds previous', () {
      final input = DomainHealthInput(
        now: now,
        domainCheckIns: {
          HealthDomain.financial: [
            // 3 in the recent 7-day window
            now.subtract(const Duration(days: 1)),
            now.subtract(const Duration(days: 2)),
            now.subtract(const Duration(days: 3)),
            // 1 in the previous 7-day window
            now.subtract(const Duration(days: 10)),
          ],
        },
      );

      final summary = calculator.calculate(HealthDomain.financial, input);

      expect(summary.trend, DomainTrend.improving);
    });

    test('returns declining trend when recent activity is below previous', () {
      final input = DomainHealthInput(
        now: now,
        domainCheckIns: {
          HealthDomain.relational: [
            // 1 in the recent 7-day window
            now.subtract(const Duration(days: 2)),
            // 3 in the previous 7-day window
            now.subtract(const Duration(days: 9)),
            now.subtract(const Duration(days: 10)),
            now.subtract(const Duration(days: 11)),
          ],
        },
      );

      final summary = calculator.calculate(HealthDomain.relational, input);

      expect(summary.trend, DomainTrend.declining);
    });

    test('returns stable trend when recent equals previous activity', () {
      final input = DomainHealthInput(
        now: now,
        domainCheckIns: {
          HealthDomain.mentalEmotional: [
            now.subtract(const Duration(days: 2)),
            now.subtract(const Duration(days: 9)),
          ],
        },
      );

      final summary = calculator.calculate(HealthDomain.mentalEmotional, input);

      expect(summary.trend, DomainTrend.stable);
    });

    test('uses global activity as proxy when no domain check-ins exist', () {
      final input = DomainHealthInput(
        now: now,
        reflectionTimestamps: [
          now.subtract(const Duration(days: 1)),
          now.subtract(const Duration(days: 2)),
          now.subtract(const Duration(days: 8)),
        ],
      );

      final summary = calculator.calculate(HealthDomain.physical, input);

      // Status should not be unknown because global activity is present.
      expect(summary.status, isNot(DomainStatus.unknown));
      expect(summary.confidence, greaterThan(0.0));
      // Should include placeholder observation noting global-only data.
      expect(
        summary.supportingSignals.any(
          (s) => s.type == DomainSignalType.placeholder,
        ),
        isTrue,
      );
    });

    test('confidence is capped at 1.0', () {
      // Create a very large number of check-ins to push raw confidence > 1.
      final checkIns = [
        for (int i = 0; i < 50; i++) now.subtract(Duration(days: i % 30 + 1)),
      ];
      final input = DomainHealthInput(
        now: now,
        domainCheckIns: {HealthDomain.physical: checkIns},
      );

      final summary = calculator.calculate(HealthDomain.physical, input);

      expect(summary.confidence, lessThanOrEqualTo(1.0));
    });

    test('computedAt matches the input now timestamp', () {
      final input = DomainHealthInput(now: now);
      final summary = calculator.calculate(HealthDomain.relational, input);

      expect(summary.computedAt, now);
    });
  });

  group('DomainHealthEngine', () {
    final now = DateTime.utc(2026, 7, 3, 12);

    test('computeSummaries covers all monitored domains by default', () async {
      final engine = DomainHealthEngine();
      final summaries = await engine.computeSummaries(
        additionalInput: DomainHealthInput(now: now),
        now: now,
      );

      final domains = summaries.map((s) => s.domain).toSet();
      expect(domains, containsAll(HealthDomain.defaultSet));
      expect(summaries, hasLength(HealthDomain.defaultSet.length));
    });

    test('computeSummaryFor returns summary for the requested domain', () async {
      final engine = DomainHealthEngine();
      final summary = await engine.computeSummaryFor(
        HealthDomain.financial,
        now: now,
      );

      expect(summary.domain, HealthDomain.financial);
    });

    test('aggregates timestamps from registered signal sources', () async {
      final source = _FakeSignalSource(
        sourceId: 'fake',
        timestamps: {
          HealthDomain.physical: [
            now.subtract(const Duration(days: 1)),
            now.subtract(const Duration(days: 2)),
          ],
        },
      );

      final engine = DomainHealthEngine(sources: [source]);
      await engine.initialize();

      final summary = await engine.computeSummaryFor(
        HealthDomain.physical,
        now: now,
      );

      expect(summary.status, isNot(DomainStatus.unknown));
      expect(source.initialized, isTrue);
    });

    test('suppresses signal source failures and still computes summaries', () async {
      final engine = DomainHealthEngine(
        sources: [_ThrowingSignalSource()],
      );
      await engine.initialize();

      // Should not throw even though the source throws.
      final summaries = await engine.computeSummaries(
        additionalInput: DomainHealthInput(now: now),
        now: now,
      );

      expect(summaries, hasLength(HealthDomain.defaultSet.length));
    });

    test('merges additional input with source timestamps', () async {
      final source = _FakeSignalSource(
        sourceId: 'source',
        timestamps: {
          HealthDomain.physical: [now.subtract(const Duration(days: 3))],
        },
      );
      final engine = DomainHealthEngine(sources: [source]);

      final summary = await engine.computeSummaryFor(
        HealthDomain.physical,
        additionalInput: DomainHealthInput(
          domainCheckIns: {
            HealthDomain.physical: [now.subtract(const Duration(days: 1))],
          },
          now: now,
        ),
        now: now,
      );

      // Two check-ins total (one from source, one from additionalInput).
      expect(
        summary.supportingSignals.where((s) => s.type == DomainSignalType.checkIn).single.metadata['totalCheckIns'],
        2,
      );
    });

    test('registerSource adds source to the engine', () {
      final engine = DomainHealthEngine();
      expect(engine.sources, isEmpty);

      engine.registerSource(
        _FakeSignalSource(sourceId: 'late', timestamps: {}),
      );

      expect(engine.sources, hasLength(1));
    });

    test('initialize() and dispose() call source lifecycle hooks', () async {
      final source = _FakeSignalSource(sourceId: 'lifecycle', timestamps: {});
      final engine = DomainHealthEngine(sources: [source]);

      await engine.initialize();
      await engine.dispose();

      expect(source.initialized, isTrue);
      expect(source.disposed, isTrue);
    });

    test('custom monitored domains restrict output', () async {
      final engine = DomainHealthEngine(
        monitoredDomains: {HealthDomain.physical},
      );
      final summaries = await engine.computeSummaries(
        additionalInput: DomainHealthInput(now: now),
        now: now,
      );

      expect(summaries, hasLength(1));
      expect(summaries.single.domain, HealthDomain.physical);
    });

    test('collects reflection timestamps from sources', () async {
      final source = _FakeSignalSourceWithGlobal(
        sourceId: 'reflection_src',
        reflectionTimestamps: [
          now.subtract(const Duration(days: 1)),
          now.subtract(const Duration(days: 2)),
        ],
      );

      final engine = DomainHealthEngine(sources: [source]);
      final summary = await engine.computeSummaryFor(
        HealthDomain.mentalEmotional,
        now: now,
      );

      // Global activity signal should be present since reflections were found.
      expect(summary.status, isNot(DomainStatus.unknown));
      expect(
        summary.supportingSignals.any(
          (s) => s.type == DomainSignalType.reflectionActivity,
        ),
        isTrue,
      );
    });

    test('collects practice timestamps from sources', () async {
      final source = _FakeSignalSourceWithGlobal(
        sourceId: 'practice_src',
        practiceTimestamps: [
          now.subtract(const Duration(days: 1)),
          now.subtract(const Duration(days: 3)),
          now.subtract(const Duration(days: 5)),
        ],
      );

      final engine = DomainHealthEngine(sources: [source]);
      final summary = await engine.computeSummaryFor(
        HealthDomain.physical,
        now: now,
      );

      // PlaceholderDomainHealthCalculator combines reflections and practices
      // into a single "Global activity" signal of type reflectionActivity.
      // Expect the signal to be present, confirming practice timestamps flow
      // through the engine into the calculator's global activity pool.
      expect(summary.status, isNot(DomainStatus.unknown));
      expect(
        summary.supportingSignals.any(
          (s) => s.type == DomainSignalType.reflectionActivity,
        ),
        isTrue,
      );
    });

    test('merges source global timestamps with additionalInput global timestamps', () async {
      final source = _FakeSignalSourceWithGlobal(
        sourceId: 'global_src',
        reflectionTimestamps: [now.subtract(const Duration(days: 2))],
      );

      final engine = DomainHealthEngine(sources: [source]);
      final summary = await engine.computeSummaryFor(
        HealthDomain.mentalEmotional,
        additionalInput: DomainHealthInput(
          reflectionTimestamps: [now.subtract(const Duration(days: 4))],
          now: now,
        ),
        now: now,
      );

      // Combined: 1 from source + 1 from additionalInput = 2 total.
      expect(
        summary.supportingSignals
            .where((s) => s.type == DomainSignalType.reflectionActivity)
            .single
            .metadata['totalGlobal'],
        2,
      );
    });
  });

  group('DomainSummary', () {
    test('confidence assertion fires outside [0.0, 1.0]', () {
      expect(
        () => DomainSummary(
          domain: HealthDomain.physical,
          status: DomainStatus.unknown,
          trend: DomainTrend.insufficient,
          confidence: -0.1,
          supportingSignals: const [],
          computedAt: DateTime.now(),
        ),
        throwsA(isA<AssertionError>()),
      );

      expect(
        () => DomainSummary(
          domain: HealthDomain.physical,
          status: DomainStatus.unknown,
          trend: DomainTrend.insufficient,
          confidence: 1.1,
          supportingSignals: const [],
          computedAt: DateTime.now(),
        ),
        throwsA(isA<AssertionError>()),
      );
    });
  });
}

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

class _FakeSignalSource implements DomainSignalSource {
  _FakeSignalSource({
    required this.sourceId,
    required this._timestamps,
  });

  @override
  final String sourceId;

  @override
  String get displayName => sourceId;

  final Map<HealthDomain, List<DateTime>> _timestamps;

  bool initialized = false;
  bool disposed = false;

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<Map<HealthDomain, List<DateTime>>> collectTimestamps() async => _timestamps;

  @override
  Future<List<DateTime>> collectReflectionTimestamps() async => const [];

  @override
  Future<List<DateTime>> collectPracticeTimestamps() async => const [];

  @override
  Future<void> dispose() async => disposed = true;
}

class _ThrowingSignalSource implements DomainSignalSource {
  @override
  String get sourceId => 'throwing';

  @override
  String get displayName => 'Throwing Source';

  @override
  Future<void> initialize() async {}

  @override
  Future<Map<HealthDomain, List<DateTime>>> collectTimestamps() async {
    throw Exception('source failure');
  }

  @override
  Future<List<DateTime>> collectReflectionTimestamps() async => const [];

  @override
  Future<List<DateTime>> collectPracticeTimestamps() async => const [];

  @override
  Future<void> dispose() async {}
}

class _FakeSignalSourceWithGlobal implements DomainSignalSource {
  _FakeSignalSourceWithGlobal({
    required this.sourceId,
    this._reflectionTimestamps = const [],
    this._practiceTimestamps = const [],
  });

  @override
  final String sourceId;

  @override
  String get displayName => sourceId;

  final List<DateTime> _reflectionTimestamps;
  final List<DateTime> _practiceTimestamps;

  @override
  Future<void> initialize() async {}

  @override
  Future<Map<HealthDomain, List<DateTime>>> collectTimestamps() async => const {};

  @override
  Future<List<DateTime>> collectReflectionTimestamps() async => _reflectionTimestamps;

  @override
  Future<List<DateTime>> collectPracticeTimestamps() async => _practiceTimestamps;

  @override
  Future<void> dispose() async {}
}
