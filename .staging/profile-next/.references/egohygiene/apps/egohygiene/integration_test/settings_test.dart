/// Integration test: settings navigation.
///
/// Verifies that the Settings screen and its sub-routes are reachable and
/// render their expected content.
///
/// Run with:
/// ```
/// flutter test integration_test/settings_test.dart
/// ```
///
/// On a real device or emulator:
/// ```
/// flutter test integration_test/settings_test.dart -d <device-id>
/// ```
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'helpers/integration_test_helpers.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Settings navigation', () {
    testWidgets(
      'home screen shows the Settings quick-action chip',
      (tester) async {
        await pumpApp(tester);

        // Scroll down until the Settings chip is visible.
        await tester.scrollUntilVisible(
          find.widgetWithText(ActionChip, 'Settings'),
          400,
          scrollable: find.byType(Scrollable).first,
        );

        expect(find.widgetWithText(ActionChip, 'Settings'), findsOneWidget);
      },
    );

    testWidgets(
      'tapping the Settings chip navigates to the Settings screen',
      (tester) async {
        await pumpApp(tester);

        await tester.scrollUntilVisible(
          find.widgetWithText(ActionChip, 'Settings'),
          400,
          scrollable: find.byType(Scrollable).first,
        );

        await tester.tap(find.widgetWithText(ActionChip, 'Settings'));
        await tester.pumpAndSettle();

        // The Settings AppBar title must be visible.
        expect(find.text('Settings'), findsWidgets);

        // Key settings sections must be rendered.
        expect(find.text('Language'), findsOneWidget);
        expect(find.text('Theme'), findsOneWidget);
        expect(find.text('Artificial Intelligence'), findsOneWidget);
      },
    );

    testWidgets(
      'tapping AI settings navigates to the AI settings screen',
      (tester) async {
        await pumpApp(tester);

        // Navigate to Settings first.
        await tester.scrollUntilVisible(
          find.widgetWithText(ActionChip, 'Settings'),
          400,
          scrollable: find.byType(Scrollable).first,
        );

        await tester.tap(find.widgetWithText(ActionChip, 'Settings'));
        await tester.pumpAndSettle();

        // Tap the AI settings ListTile (title = "Artificial Intelligence").
        await tester.scrollUntilVisible(
          find.widgetWithText(ListTile, 'Artificial Intelligence'),
          200,
          scrollable: find.byType(Scrollable).first,
        );

        await tester.tap(
          find.widgetWithText(ListTile, 'Artificial Intelligence'),
        );
        await tester.pumpAndSettle();

        // The AI settings screen must show the four mode options.
        expect(find.text('Cloud'), findsWidgets);
        expect(find.text('Local'), findsWidgets);
        expect(find.text('Hybrid'), findsWidgets);
        expect(find.text('Disabled'), findsWidgets);
      },
    );
  });
}
