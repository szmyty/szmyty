/// Integration test: restart persistence.
///
/// Verifies that the onboarding completion flag is persisted across a
/// simulated app restart:
///
///   1. First launch — storage is empty → onboarding screen is shown.
///   2. User skips onboarding → completion flag written to [FakeStorageService].
///   3. Simulated restart — new [ProviderScope] with the same storage instance.
///   4. Home screen is shown directly, onboarding is NOT shown again.
///
/// This test intentionally avoids overriding [onboardingManagerProvider] so
/// that the real [OnboardingManager] reads and writes the persisted state.
///
/// Run with:
/// ```
/// flutter test integration_test/restart_persistence_test.dart
/// ```
///
/// On a real device or emulator:
/// ```
/// flutter test integration_test/restart_persistence_test.dart -d <device-id>
/// ```
library;

import 'package:egohygiene/features/onboarding/feature.dart' show OnboardingManager;
import 'package:egohygiene/features/onboarding/providers/onboarding_providers.dart' show OnboardingManager;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart' show ProviderScope;
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'helpers/integration_test_helpers.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Restart persistence', () {
    testWidgets(
      'onboarding completion is remembered across a simulated restart',
      (tester) async {
        // Shared storage instance that persists across both "launches".
        final sharedStorage = FakeStorageService();

        // ── First launch: storage is empty, onboarding is required ──────────
        await pumpAppWithRealOnboarding(
          tester,
          sharedStorage: sharedStorage,
        );

        // The onboarding screen must be visible.
        expect(find.text('A quiet space for reflection.'), findsOneWidget);
        expect(find.byType(NavigationBar), findsNothing);

        // Skip onboarding to write the completion flag to sharedStorage.
        await tester.tap(find.text('Skip'));
        await tester.pumpAndSettle();

        // Verify we reached the home screen after skipping.
        expect(find.byType(NavigationBar), findsOneWidget);
        expect(find.text('Ego Hygiene'), findsOneWidget);

        // ── Simulated restart: same storage, new ProviderScope ───────────────
        await pumpAppWithRealOnboarding(
          tester,
          sharedStorage: sharedStorage,
        );

        // The home screen must be shown — onboarding must NOT appear again.
        expect(find.byType(NavigationBar), findsOneWidget);
        expect(find.text('Ego Hygiene'), findsOneWidget);
        expect(find.text('A quiet space for reflection.'), findsNothing);
      },
    );

    testWidgets(
      'a user who has not completed onboarding always sees onboarding on restart',
      (tester) async {
        // Fresh storage — onboarding never completed.
        final freshStorage = FakeStorageService();

        await pumpAppWithRealOnboarding(
          tester,
          sharedStorage: freshStorage,
        );

        // Onboarding screen is shown.
        expect(find.text('A quiet space for reflection.'), findsOneWidget);

        // Simulate restart without completing onboarding.
        await pumpAppWithRealOnboarding(
          tester,
          sharedStorage: freshStorage,
        );

        // Onboarding screen is shown again (not completed).
        expect(find.text('A quiet space for reflection.'), findsOneWidget);
        expect(find.byType(NavigationBar), findsNothing);
      },
    );
  });
}
