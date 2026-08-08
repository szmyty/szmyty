/// Integration test: first launch.
///
/// Verifies that a brand-new user (onboarding not yet completed) is routed to
/// the onboarding screen rather than the home screen after startup.
///
/// Run with:
/// ```
/// flutter test integration_test/first_launch_test.dart
/// ```
///
/// On a real device or emulator:
/// ```
/// flutter test integration_test/first_launch_test.dart -d <device-id>
/// ```
library;

import 'package:egohygiene/features/onboarding/providers/onboarding_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'helpers/integration_test_helpers.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('First launch', () {
    testWidgets(
      'new user is routed to the onboarding screen after startup',
      (tester) async {
        await pumpApp(
          tester,
          overrides: [
            onboardingManagerProvider.overrideWith(
              RequiredOnboardingManager.new,
            ),
          ],
        );

        // The onboarding screen (page 1) should be visible.
        expect(
          find.text('A quiet space for reflection.'),
          findsOneWidget,
        );

        // The persistent navigation shell (home shell) must NOT be shown.
        expect(find.byType(NavigationBar), findsNothing);
      },
    );

    testWidgets(
      'new user does not see the home dashboard before onboarding',
      (tester) async {
        await pumpApp(
          tester,
          overrides: [
            onboardingManagerProvider.overrideWith(
              RequiredOnboardingManager.new,
            ),
          ],
        );

        // The "Ego Hygiene" home header must not be visible.
        expect(find.text('Ego Hygiene'), findsNothing);

        // The skip action of the onboarding screen must be present.
        expect(find.text('Skip'), findsOneWidget);
      },
    );
  });
}
