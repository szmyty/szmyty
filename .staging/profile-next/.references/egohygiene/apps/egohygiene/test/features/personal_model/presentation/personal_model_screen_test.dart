import 'package:egohygiene/features/personal_model/presentation/personal_model_screen.dart';
import 'package:egohygiene/features/personal_model/providers/personal_model_providers.dart';
import 'package:egohygiene/features/progress/providers/progress_providers.dart';
import 'package:egohygiene/shared/health/domain_health_engine.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod/misc.dart' show Override;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

Widget _wrap(Widget child, {List<Override> overrides = const []}) {
  return ProviderScope(
    overrides: overrides,
    child: TranslationProvider(
      child: MaterialApp(
        theme: AppTheme.light(useGoogleFonts: false),
        home: child,
      ),
    ),
  );
}

PersonalModelSnapshot _emptySnapshot() {
  return PersonalModelSnapshot(
    domains: const [],
    goals: const [],
    consistency: PracticeConsistencySummary.empty(),
    memories: const [],
    journeyEventCount: 0,
  );
}

PersonalModelSnapshot _snapshotWithDomains(List<DomainSummary> domains) {
  final now = DateTime(2025, 6);
  return PersonalModelSnapshot(
    domains: domains,
    goals: const [],
    consistency: PracticeConsistencySummary.empty(now: now),
    memories: const [],
    journeyEventCount: 0,
  );
}

DomainSummary _domain({
  required HealthDomain domain,
  DomainStatus status = DomainStatus.active,
  DomainTrend trend = DomainTrend.stable,
  double confidence = 0.75,
}) {
  return DomainSummary(
    domain: domain,
    status: status,
    trend: trend,
    confidence: confidence,
    supportingSignals: const [],
    computedAt: DateTime(2025, 6),
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  group('PersonalModelScreen', () {
    testWidgets('shows loading indicator while snapshot is loading', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const PersonalModelScreen(),
          overrides: [
            personalModelSnapshotProvider.overrideWithValue(
              const AsyncValue<PersonalModelSnapshot>.loading(),
            ),
          ],
        ),
      );

      await tester.pump();
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows tagline and overview card for empty snapshot', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const PersonalModelScreen(),
          overrides: [
            personalModelSnapshotProvider.overrideWithValue(
              AsyncValue.data(_emptySnapshot()),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Personal Model'), findsWidgets);
      expect(find.text('Model Overview'), findsOneWidget);
    });

    testWidgets('shows overview stats with zero signals for empty snapshot', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const PersonalModelScreen(),
          overrides: [
            personalModelSnapshotProvider.overrideWithValue(
              AsyncValue.data(_emptySnapshot()),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('0'), findsAtLeastNWidgets(2));
    });

    testWidgets('shows empty state in domains card when no domains', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const PersonalModelScreen(),
          overrides: [
            personalModelSnapshotProvider.overrideWithValue(
              AsyncValue.data(_emptySnapshot()),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('No domain signals yet'), findsOneWidget);
    });

    testWidgets('renders domain rows when domains are available', (tester) async {
      final snapshot = _snapshotWithDomains([
        _domain(domain: HealthDomain.mentalEmotional),
        _domain(domain: HealthDomain.physical, confidence: 0.5),
      ]);

      await tester.pumpWidget(
        _wrap(
          const PersonalModelScreen(),
          overrides: [
            personalModelSnapshotProvider.overrideWithValue(
              AsyncValue.data(snapshot),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Mental & Emotional Health'), findsOneWidget);
      expect(find.text('Physical Health'), findsOneWidget);
      // Two LinearProgressIndicators for the two domain rows
      expect(find.byType(LinearProgressIndicator), findsNWidgets(2));
    });

    testWidgets('shows AI Transparency card', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const PersonalModelScreen(),
          overrides: [
            personalModelSnapshotProvider.overrideWithValue(
              AsyncValue.data(_emptySnapshot()),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('AI Transparency'), findsOneWidget);
      expect(find.text('Reflections'), findsOneWidget);
      expect(find.text('Daily check-ins'), findsOneWidget);
    });

    testWidgets('shows Practices, Memories, Goals, Journey section titles', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const PersonalModelScreen(),
          overrides: [
            personalModelSnapshotProvider.overrideWithValue(
              AsyncValue.data(_emptySnapshot()),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Practices'), findsOneWidget);
      expect(find.text('No active streak yet'), findsOneWidget);
      expect(find.text('Memories'), findsOneWidget);
      expect(find.text('Goals'), findsOneWidget);
      expect(find.text('Journey'), findsOneWidget);
    });

    testWidgets('shows error state when snapshot fails', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const PersonalModelScreen(),
          overrides: [
            personalModelSnapshotProvider.overrideWithValue(
              const AsyncValue.error('load failed', StackTrace.empty),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(CircularProgressIndicator), findsNothing);
    });
  });

  group('PersonalModelSnapshot', () {
    test('dimensionsWithSignals counts non-empty dimensions', () {
      final now = DateTime(2025, 6);
      final snapshot = PersonalModelSnapshot(
        domains: [
          _domain(domain: HealthDomain.mentalEmotional),
        ],
        goals: const [],
        consistency: PracticeConsistencySummary.empty(now: now),
        memories: const [],
        journeyEventCount: 5,
      );

      // domains (1) + journeyEventCount > 0 (1) = 2
      expect(snapshot.dimensionsWithSignals, 2);
    });

    test('totalSignals sums contributions from all dimensions', () {
      final now = DateTime(2025, 6);
      final snapshot = PersonalModelSnapshot(
        domains: [
          _domain(domain: HealthDomain.physical),
          _domain(domain: HealthDomain.relational),
        ],
        goals: const [],
        consistency: PracticeConsistencySummary.empty(now: now),
        memories: const [],
        journeyEventCount: 3,
      );

      // 2 domains + 0 goals + 0 memories + 0 activeDays + 3 journey events
      expect(snapshot.totalSignals, 5);
    });
  });
}
