import 'package:egohygiene/features/progress/presentation/progress_screen.dart';
import 'package:egohygiene/shared/goal/goal_engine.dart';
import 'package:egohygiene/shared/health/domain_health_engine.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/providers/domain_health_providers.dart';
import 'package:egohygiene/shared/providers/goal_providers.dart';
import 'package:egohygiene/shared/providers/timeline_providers.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:egohygiene/shared/timeline/timeline_engine.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeTimelineSource implements TimelineSource {
  const _FakeTimelineSource(this.events);

  final List<TimelineEvent> events;

  @override
  String get displayName => 'Fake Timeline';

  @override
  String get sourceId => 'fake';

  @override
  Future<void> dispose() async {}

  @override
  Future<List<TimelineEvent>> getEvents() async => events;

  @override
  Future<void> initialize() async {}
}

Widget _wrap({
  required GoalManager goalManager,
  required TimelineManager timelineManager,
  required Future<List<DomainSummary>> Function(Ref ref) domainSummaryLoader,
}) {
  return ProviderScope(
    overrides: [
      goalManagerProvider.overrideWith((ref) => goalManager),
      timelineManagerProvider.overrideWith((ref) => timelineManager),
      domainSummariesProvider.overrideWith(domainSummaryLoader),
    ],
    child: MaterialApp(
      theme: AppTheme.light(useGoogleFonts: false),
      home: TranslationProvider(child: const ProgressScreen()),
    ),
  );
}

Future<GoalManager> _buildGoalManagerWithData() async {
  final manager = GoalManager(store: InMemoryGoalStore());
  await manager.initialize();
  final goal = await manager.createGoal(
    id: 'goal-1',
    title: 'Build reflection habit',
    priority: GoalPriority.high,
    milestones: const [
      Milestone(id: 'm1', title: 'Start'),
      Milestone(id: 'm2', title: 'Repeat'),
      Milestone(id: 'm3', title: 'Reflect'),
      Milestone(id: 'm4', title: 'Sustain'),
    ],
  );
  await manager.completeMilestone(goal.id, 'm1');
  await manager.completeMilestone(goal.id, 'm2');
  return manager;
}

void main() {
  group('ProgressScreen', () {
    testWidgets('renders connected progress sections', (tester) async {
      final goalManager = await _buildGoalManagerWithData();
      final timelineManager = TimelineManager(
        sources: [
          _FakeTimelineSource([
            TimelineEvent(
              id: 'event-1',
              type: TimelineEventType.reflection,
              sourceId: 'reflection',
              occurredAt: DateTime.now().subtract(const Duration(days: 1)),
              title: 'Morning reflection',
              description: 'Captured a meaningful win.',
            ),
            TimelineEvent(
              id: 'event-2',
              type: TimelineEventType.practiceCompletion,
              sourceId: 'practice',
              occurredAt: DateTime.now().subtract(const Duration(days: 2)),
              title: 'Practice completed',
            ),
            TimelineEvent(
              id: 'event-3',
              type: TimelineEventType.goal,
              sourceId: 'goal',
              occurredAt: DateTime.now().subtract(const Duration(days: 3)),
              title: 'Build reflection habit',
            ),
          ]),
        ],
      );

      await tester.pumpWidget(
        _wrap(
          goalManager: goalManager,
          timelineManager: timelineManager,
          domainSummaryLoader: (ref) async => [
            DomainSummary(
              domain: HealthDomain.mentalEmotional,
              status: DomainStatus.active,
              trend: DomainTrend.improving,
              confidence: 0.85,
              supportingSignals: const [],
              computedAt: DateTime.now(),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // Sections visible in the initial viewport.
      expect(find.text('Gentle Next Step'), findsOneWidget);
      expect(find.text('Check in now'), findsOneWidget);
      expect(find.text('Capture reflection'), findsOneWidget);

      // Sections below the fold — scroll until each becomes visible.
      await tester.scrollUntilVisible(find.text('Insight Summary'), 300);
      expect(find.text('Insight Summary'), findsOneWidget);

      await tester.scrollUntilVisible(find.text('Goal Progress'), 300);
      expect(find.text('Goal Progress'), findsOneWidget);
      expect(find.text('Build reflection habit'), findsAtLeastNWidgets(1));
      expect(find.text('2 / 4 milestones • High priority'), findsOneWidget);

      await tester.scrollUntilVisible(find.text('Practice Consistency'), 300);
      expect(find.text('Practice Consistency'), findsOneWidget);
      expect(find.text('Current streak'), findsOneWidget);
      expect(find.text('2 days'), findsOneWidget);

      await tester.scrollUntilVisible(find.text('Journey Milestones'), 300);
      expect(find.text('Journey Milestones'), findsOneWidget);
      expect(find.text('Morning reflection'), findsOneWidget);

      await tester.scrollUntilVisible(find.text('Domain Trends'), 300);
      expect(find.text('Domain Trends'), findsOneWidget);
      expect(find.text('Mental & Emotional Health'), findsOneWidget);
    });

    testWidgets('shows empty states when no progress data exists', (tester) async {
      final goalManager = GoalManager(store: InMemoryGoalStore());
      await goalManager.initialize();
      final timelineManager = TimelineManager(
        sources: const [_FakeTimelineSource([])],
      );

      await tester.pumpWidget(
        _wrap(
          goalManager: goalManager,
          timelineManager: timelineManager,
          domainSummaryLoader: (ref) async => const <DomainSummary>[],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Gentle Next Step'), findsOneWidget);

      await tester.scrollUntilVisible(find.text('No goals yet'), 300);
      expect(find.text('No goals yet'), findsOneWidget);
      expect(
        find.text(
          'Start a goal when you want clearer momentum and milestones.',
        ),
        findsOneWidget,
      );

      await tester.scrollUntilVisible(find.text('No active streak yet'), 300);
      expect(find.text('No active streak yet'), findsOneWidget);

      await tester.scrollUntilVisible(find.text('No milestones yet'), 300);
      expect(find.text('No milestones yet'), findsOneWidget);
      expect(
        find.text(
          'Your milestones and moments will appear here as you reflect and check in.',
        ),
        findsOneWidget,
      );

      await tester.scrollUntilVisible(find.text('No domain trends yet'), 300);
      expect(find.text('No domain trends yet'), findsOneWidget);
      expect(
        find.text(
          'Domain trends will appear here as your check-in and reflection data grows.',
        ),
        findsOneWidget,
      );
    });
  });
}
