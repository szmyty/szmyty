/// Smoke test: verifies the app launches and displays the Home screen.
///
/// This is the foundational integration test.  It exercises the full startup
/// lifecycle from Flutter bootstrap through every [StartupStage] and asserts
/// that the persistent navigation shell and home-screen content are visible
/// once the app is ready.
///
/// Run with:
/// ```
/// flutter test integration_test/app_smoke_test.dart
/// ```
///
/// On a real device or emulator:
/// ```
/// flutter test integration_test/app_smoke_test.dart -d <device-id>
/// ```
library;

import 'package:egohygiene/app/startup/domain/startup_state.dart' show StartupStage;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'helpers/integration_test_helpers.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('App smoke test', () {
    testWidgets('startup completes and Home screen is displayed', (
      tester,
    ) async {
      await pumpApp(tester);

      // The persistent navigation shell must be present — this confirms the
      // startup lifecycle completed and the router redirected to the home route.
      expect(find.byType(NavigationBar), findsOneWidget);

      // Core home-screen content is visible.
      expect(find.text('Ego Hygiene'), findsOneWidget);
      expect(find.text("Today's Reflection"), findsOneWidget);
    });
  });
}
