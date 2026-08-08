import 'package:egohygiene/features/reflection/presentation/reflection_screen.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/timeline/timeline_engine.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';

void main() {
  setUpAll(() async {
    await initializeDateFormatting('en');
  });

  group('ReflectionScreen', () {
    testWidgets('renders empty state when no reflections exist', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            reflectionTimelineProvider.overrideWith(
              (ref) async => const <TimelineEvent>[],
            ),
          ],
          child: TranslationProvider(child: const MaterialApp(home: ReflectionScreen())),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Your reflection space is ready'), findsOneWidget);
      expect(
        find.text(
          'Begin with whatever is on your mind. A small thought is enough to start.',
        ),
        findsOneWidget,
      );
      expect(find.text('New Reflection'), findsOneWidget);
    });

    testWidgets('supports searching and filtering the timeline', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            reflectionTimelineProvider.overrideWith(
              (ref) async => [
                TimelineEvent(
                  id: 'reflection-1',
                  type: TimelineEventType.reflection,
                  sourceId: 'reflection',
                  occurredAt: DateTime.parse('2026-06-21T12:00:00.000Z'),
                  title: 'Morning Reflection',
                  description: 'I noticed a calmer response this morning.',
                ),
                TimelineEvent(
                  id: 'insight-1',
                  type: TimelineEventType.insight,
                  sourceId: 'insight',
                  occurredAt: DateTime.parse('2026-06-22T12:00:00.000Z'),
                  title: 'Pattern spotted',
                  description: 'Calmer mornings follow journaling.',
                ),
              ],
            ),
          ],
          child: TranslationProvider(child: const MaterialApp(home: ReflectionScreen())),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Morning Reflection'), findsOneWidget);
      expect(find.text('Pattern spotted'), findsOneWidget);

      await tester.enterText(find.byType(TextField), 'pattern');
      await tester.pumpAndSettle();

      expect(find.text('Pattern spotted'), findsOneWidget);
      expect(find.text('Morning Reflection'), findsNothing);

      await tester.tap(find.text('Reflections'));
      await tester.pumpAndSettle();

      expect(find.text('No timeline matches'), findsOneWidget);
    });

    testWidgets('loads more timeline cards while scrolling', (tester) async {
      final events = List<TimelineEvent>.generate(
        12,
        (index) => TimelineEvent(
          id: 'event-$index',
          type: TimelineEventType.reflection,
          sourceId: 'reflection',
          occurredAt: DateTime(2026, 7, 12 - index),
          title: 'Reflection $index',
        ),
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            reflectionTimelineProvider.overrideWith((ref) async => events),
          ],
          child: TranslationProvider(child: const MaterialApp(home: ReflectionScreen())),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Reflection 0'), findsOneWidget);
      expect(find.text('Reflection 8'), findsNothing);

      for (var i = 0; i < 4; i++) {
        await tester.drag(find.byType(ListView), const Offset(0, -800));
        await tester.pumpAndSettle();
      }

      expect(find.text('Reflection 11'), findsOneWidget);
    });
  });
}
