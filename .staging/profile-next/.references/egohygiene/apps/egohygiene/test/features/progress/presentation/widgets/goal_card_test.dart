import 'package:egohygiene/features/progress/presentation/widgets/goal_card.dart';
import 'package:egohygiene/features/progress/providers/progress_providers.dart';
import 'package:egohygiene/shared/goal/goal_engine.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _wrap(Widget child) {
  return MaterialApp(
    theme: AppTheme.light(useGoogleFonts: false),
    home: Scaffold(body: child),
  );
}

GoalProgressSnapshot _snapshot(Goal goal) {
  return GoalProgressSnapshot(
    goal: goal,
    progress: GoalProgress.compute(goal),
  );
}

void main() {
  group('GoalCard', () {
    testWidgets('renders goal title and status badge', (tester) async {
      final goal = Goal(
        id: 'g1',
        title: 'Build a reflection habit',
        createdAt: DateTime(2024),
        updatedAt: DateTime(2024),
      );

      await tester.pumpWidget(_wrap(GoalCard(snapshot: _snapshot(goal))));

      expect(find.text('Build a reflection habit'), findsOneWidget);
      expect(find.text('Active'), findsOneWidget);
    });

    testWidgets('shows domain chip when domain is set', (tester) async {
      final goal = Goal(
        id: 'g2',
        title: 'Exercise regularly',
        domain: 'physical',
        createdAt: DateTime(2024),
        updatedAt: DateTime(2024),
      );

      await tester.pumpWidget(_wrap(GoalCard(snapshot: _snapshot(goal))));

      expect(find.text('Body'), findsOneWidget);
    });

    testWidgets('shows Mind chip for mentalEmotional domain', (tester) async {
      final goal = Goal(
        id: 'g3',
        title: 'Meditate daily',
        domain: 'mentalEmotional',
        createdAt: DateTime(2024),
        updatedAt: DateTime(2024),
      );

      await tester.pumpWidget(_wrap(GoalCard(snapshot: _snapshot(goal))));

      expect(find.text('Mind'), findsOneWidget);
    });

    testWidgets('does not show domain chip when domain is null', (tester) async {
      final goal = Goal(
        id: 'g4',
        title: 'Read more books',
        createdAt: DateTime(2024),
        updatedAt: DateTime(2024),
      );

      await tester.pumpWidget(_wrap(GoalCard(snapshot: _snapshot(goal))));

      // No domain label chips should appear
      expect(find.text('Body'), findsNothing);
      expect(find.text('Mind'), findsNothing);
      expect(find.text('Money'), findsNothing);
      expect(find.text('Bonds'), findsNothing);
    });

    testWidgets('shows Completed status badge for completed goal', (tester) async {
      final goal = Goal(
        id: 'g5',
        title: 'Finished goal',
        status: GoalStatus.completed,
        milestones: const [
          Milestone(id: 'm1', title: 'Step 1', isCompleted: true),
        ],
        createdAt: DateTime(2024),
        updatedAt: DateTime(2024),
        completedAt: DateTime(2024),
      );

      await tester.pumpWidget(_wrap(GoalCard(snapshot: _snapshot(goal))));

      expect(find.text('Completed'), findsOneWidget);
      expect(find.text('100%'), findsOneWidget);
    });

    testWidgets('shows milestone progress and priority', (tester) async {
      final goal = Goal(
        id: 'g6',
        title: 'Build habit',
        priority: GoalPriority.high,
        milestones: const [
          Milestone(id: 'm1', title: 'Step 1', isCompleted: true),
          Milestone(id: 'm2', title: 'Step 2', isCompleted: true),
          Milestone(id: 'm3', title: 'Step 3'),
          Milestone(id: 'm4', title: 'Step 4'),
        ],
        createdAt: DateTime(2024),
        updatedAt: DateTime(2024),
      );

      await tester.pumpWidget(_wrap(GoalCard(snapshot: _snapshot(goal))));

      expect(find.text('2 / 4 milestones • High priority'), findsOneWidget);
    });

    testWidgets('shows 0 percent for goal with no milestones', (tester) async {
      final goal = Goal(
        id: 'g7',
        title: 'New goal',
        createdAt: DateTime(2024),
        updatedAt: DateTime(2024),
      );

      await tester.pumpWidget(_wrap(GoalCard(snapshot: _snapshot(goal))));

      expect(find.text('0%'), findsOneWidget);
      expect(find.text('0 / 0 milestones • Medium priority'), findsOneWidget);
    });

    testWidgets('shows paused status badge for paused goal', (tester) async {
      final goal = Goal(
        id: 'g8',
        title: 'Paused goal',
        status: GoalStatus.paused,
        createdAt: DateTime(2024),
        updatedAt: DateTime(2024),
      );

      await tester.pumpWidget(_wrap(GoalCard(snapshot: _snapshot(goal))));

      expect(find.text('Paused'), findsOneWidget);
    });

    testWidgets('shows financial domain chip for financial domain', (tester) async {
      final goal = Goal(
        id: 'g9',
        title: 'Save for retirement',
        domain: 'financial',
        createdAt: DateTime(2024),
        updatedAt: DateTime(2024),
      );

      await tester.pumpWidget(_wrap(GoalCard(snapshot: _snapshot(goal))));

      expect(find.text('Money'), findsOneWidget);
    });
  });
}
