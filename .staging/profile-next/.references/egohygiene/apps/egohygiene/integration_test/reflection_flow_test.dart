/// Integration test: reflection creation flow.
///
/// Exercises the full reflection creation journey:
///   1. Navigate to the Reflection tab.
///   2. Tap the "New Reflection" FAB.
///   3. Fill in the reflection body.
///   4. Save the reflection and verify the return to the Reflection screen.
///
/// An in-memory database (via [appDatabaseProvider] override) is used so no
/// real file I/O is needed and the test starts from a known clean state.
///
/// Run with:
/// ```
/// flutter test integration_test/reflection_flow_test.dart
/// ```
///
/// On a real device or emulator:
/// ```
/// flutter test integration_test/reflection_flow_test.dart -d <device-id>
/// ```
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'helpers/integration_test_helpers.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Reflection creation flow', () {
    testWidgets(
      'Reflection tab shows the New Reflection FAB',
      (tester) async {
        await pumpApp(tester);

        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Reflection'),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('New Reflection'), findsOneWidget);
        expect(find.byType(FloatingActionButton), findsOneWidget);
      },
    );

    testWidgets(
      'tapping the New Reflection FAB opens the creation form',
      (tester) async {
        await pumpApp(tester);

        // Navigate to Reflection tab.
        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Reflection'),
          ),
        );
        await tester.pumpAndSettle();

        // Open the creation form.
        await tester.tap(find.byType(FloatingActionButton));
        await tester.pumpAndSettle();

        expect(find.text('New Reflection'), findsOneWidget);
        expect(find.text('Save Reflection'), findsOneWidget);
      },
    );

    testWidgets(
      'filling the body and saving returns to the Reflection screen',
      (tester) async {
        await pumpApp(tester);

        // Navigate to Reflection tab.
        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Reflection'),
          ),
        );
        await tester.pumpAndSettle();

        // Open the creation form.
        await tester.tap(find.byType(FloatingActionButton));
        await tester.pumpAndSettle();

        // Enter a reflection body (required field).
        await tester.enterText(
          find.widgetWithText(TextFormField, 'Reflection'),
          'Today I noticed that taking breaks improves my focus.',
        );
        await tester.pumpAndSettle();

        // Submit the form.
        await tester.tap(find.text('Save Reflection'));
        await tester.pumpAndSettle();

        // After a successful save the form pops back to the Reflection screen.
        // The FAB must be visible again.
        expect(find.byType(FloatingActionButton), findsOneWidget);
        expect(find.text('New Reflection'), findsOneWidget);
      },
    );

    testWidgets(
      'submitting an empty body shows a validation error',
      (tester) async {
        await pumpApp(tester);

        // Navigate to Reflection tab.
        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Reflection'),
          ),
        );
        await tester.pumpAndSettle();

        // Open the creation form.
        await tester.tap(find.byType(FloatingActionButton));
        await tester.pumpAndSettle();

        // Tap save without entering any text.
        await tester.tap(find.text('Save Reflection'));
        await tester.pumpAndSettle();

        // Validation error must be displayed.
        expect(find.text('Please write your reflection.'), findsOneWidget);

        // The form stays open (not popped).
        expect(find.text('Save Reflection'), findsOneWidget);
      },
    );
  });
}
