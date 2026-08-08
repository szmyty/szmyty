/// Integration test: onboarding flow.
///
/// Verifies the complete onboarding journey:
///   - Skipping from page one routes the user directly to the home screen.
///   - Navigating through every page and tapping "Maybe later" lands on home.
///   - Navigating through every page and tapping "Start your first reflection"
///     routes the user to the reflection-creation form.
///
/// Run with:
/// ```
/// flutter test integration_test/onboarding_test.dart
/// ```
///
/// On a real device or emulator:
/// ```
/// flutter test integration_test/onboarding_test.dart -d <device-id>
/// ```
library;

import 'package:egohygiene/features/onboarding/providers/onboarding_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'helpers/integration_test_helpers.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Onboarding flow', () {
    testWidgets(
      'skip on first page routes to home screen',
      (tester) async {
        await pumpApp(
          tester,
          overrides: [
            onboardingManagerProvider.overrideWith(
              RequiredOnboardingManager.new,
            ),
          ],
        );

        // Verify we are on the onboarding screen.
        expect(find.text('A quiet space for reflection.'), findsOneWidget);

        // Tap the top-level Skip button.
        await tester.tap(find.text('Skip'));
        await tester.pumpAndSettle();

        // The navigation shell (home screen) must now be visible.
        expect(find.byType(NavigationBar), findsOneWidget);
        expect(find.text('Ego Hygiene'), findsOneWidget);
      },
    );

    testWidgets(
      'completing all pages and tapping Maybe later routes to home screen',
      (tester) async {
        await pumpApp(
          tester,
          overrides: [
            onboardingManagerProvider.overrideWith(
              RequiredOnboardingManager.new,
            ),
          ],
        );

        // Navigate through the four informational pages.
        for (var i = 0; i < 4; i++) {
          await tester.tap(find.text('Continue'));
          await tester.pumpAndSettle();
        }

        // Now on the AI mode selection (last) page.
        expect(find.text('Choose Your AI Experience'), findsOneWidget);

        // Tap "Maybe later" to complete without selecting an AI mode.
        await tester.tap(find.text('Maybe later'));
        await tester.pumpAndSettle();

        // Home screen must be visible.
        expect(find.byType(NavigationBar), findsOneWidget);
        expect(find.text('Ego Hygiene'), findsOneWidget);
      },
    );

    testWidgets(
      'tapping Start your first reflection opens the creation form',
      (tester) async {
        await pumpApp(
          tester,
          overrides: [
            onboardingManagerProvider.overrideWith(
              RequiredOnboardingManager.new,
            ),
          ],
        );

        // Navigate through the four informational pages.
        for (var i = 0; i < 4; i++) {
          await tester.tap(find.text('Continue'));
          await tester.pumpAndSettle();
        }

        // Tap the primary CTA to begin reflecting.
        await tester.tap(find.text('Start your first reflection'));
        await tester.pumpAndSettle();

        // The New Reflection form must be visible.
        expect(find.text('New Reflection'), findsOneWidget);
        expect(find.text('Save Reflection'), findsOneWidget);
      },
    );
  });
}
