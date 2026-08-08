/// Integration test: bottom navigation.
///
/// Verifies that every tab in the persistent navigation shell is reachable and
/// that the expected screen content is visible after each tab switch.
///
/// Tabs under test (in order):
///   0 — Home
///   1 — Reflection
///   2 — Conversation
///   3 — Progress
///   4 — Memory
///
/// Run with:
/// ```
/// flutter test integration_test/navigation_test.dart
/// ```
///
/// On a real device or emulator:
/// ```
/// flutter test integration_test/navigation_test.dart -d <device-id>
/// ```
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'helpers/integration_test_helpers.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Bottom navigation', () {
    testWidgets(
      'app starts on the Home tab',
      (tester) async {
        await pumpApp(tester);

        expect(find.byType(NavigationBar), findsOneWidget);
        expect(find.text('Ego Hygiene'), findsOneWidget);
      },
    );

    testWidgets(
      'tapping Reflection tab shows the Reflection screen',
      (tester) async {
        await pumpApp(tester);

        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Reflection'),
          ),
        );
        await tester.pumpAndSettle();

        // The extended FAB for creating a new reflection is unique to
        // ReflectionScreen and serves as the reliable screen identifier.
        expect(find.text('New Reflection'), findsOneWidget);
      },
    );

    testWidgets(
      'tapping Conversation tab shows the Conversation screen',
      (tester) async {
        await pumpApp(tester);

        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Conversation'),
          ),
        );
        await tester.pumpAndSettle();

        // Empty-state title is always shown when no messages exist.
        expect(find.text('Start a conversation'), findsOneWidget);
      },
    );

    testWidgets(
      'tapping Progress tab shows the Progress screen',
      (tester) async {
        await pumpApp(tester);

        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Progress'),
          ),
        );
        await tester.pumpAndSettle();

        // The Progress screen tagline is only rendered by ProgressScreen.
        expect(
          find.text(
            'Track growth, consistency, and momentum across your journey.',
          ),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'tapping Memory tab shows the Memory screen',
      (tester) async {
        await pumpApp(tester);

        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Memory'),
          ),
        );
        await tester.pumpAndSettle();

        // The search bar placeholder is always visible on MemoryScreen.
        expect(find.text('Semantic search coming soon…'), findsOneWidget);
      },
    );

    testWidgets(
      'tapping Home tab returns to the Home screen from another tab',
      (tester) async {
        await pumpApp(tester);

        // Navigate away from Home.
        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Reflection'),
          ),
        );
        await tester.pumpAndSettle();

        // Navigate back to Home.
        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Home'),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Ego Hygiene'), findsOneWidget);
      },
    );
  });
}
