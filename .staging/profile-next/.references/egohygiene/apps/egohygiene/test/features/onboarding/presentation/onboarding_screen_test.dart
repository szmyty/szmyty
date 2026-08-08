import 'package:egohygiene/features/onboarding/presentation/onboarding_screen.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/providers/storage_providers.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:egohygiene/shared/theme/motion.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod/misc.dart' show Override;

import '../../../helpers/fake_storage_service.dart';

Widget _buildApp({
  String initialLocation = '/onboarding',
  List<Override> overrides = const [],
}) {
  final router = GoRouter(
    initialLocation: initialLocation,
    routes: [
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(
        path: '/',
        builder: (context, state) => const Scaffold(body: Center(child: Text('Home'))),
      ),
      GoRoute(
        path: '/reflection/new',
        builder: (context, state) => const Scaffold(body: Center(child: Text('New Reflection'))),
      ),
    ],
  );

  return ProviderScope(
    overrides: [
      storageServiceProvider.overrideWithValue(FakeStorageService()),
      ...overrides,
    ],
    child: TranslationProvider(
      child: MaterialApp.router(
        theme: AppTheme.light(useGoogleFonts: false),
        routerConfig: router,
      ),
    ),
  );
}

void main() {
  group('OnboardingScreen', () {
    testWidgets('renders first page with welcome title', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      expect(find.text('A quiet space for reflection.'), findsOneWidget);
    });

    testWidgets('shows Skip button on every page', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      expect(find.text('Skip'), findsOneWidget);
    });

    testWidgets('shows Continue button on non-last pages', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      expect(find.text('Continue'), findsOneWidget);
    });

    testWidgets('Continue button advances to the next page', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Continue'));
      await tester.pumpAndSettle();

      expect(find.text('Your data stays with you.'), findsOneWidget);
    });

    testWidgets('page indicator uses shared motion tokens', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      final indicator = tester.widgetList<AnimatedContainer>(find.byType(AnimatedContainer)).first;

      expect(indicator.duration, AppDurations.fast);
      expect(indicator.curve, AppCurves.standard);
    });

    testWidgets('last page shows Start first reflection button', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      // Advance to the last page (page 5: AI selection) by tapping Continue 4 times.
      for (var i = 0; i < 4; i++) {
        await tester.tap(find.text('Continue'));
        await tester.pumpAndSettle();
      }

      expect(find.text('Start your first reflection'), findsOneWidget);
      expect(find.text('Maybe later'), findsOneWidget);
    });

    testWidgets('Skip navigates to home and marks onboarding completed', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Skip'));
      await tester.pumpAndSettle();

      expect(find.text('Home'), findsOneWidget);
    });

    testWidgets('Maybe later on last page navigates to home', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      // Navigate to last page.
      for (var i = 0; i < 4; i++) {
        await tester.tap(find.text('Continue'));
        await tester.pumpAndSettle();
      }

      await tester.tap(find.text('Maybe later'));
      await tester.pumpAndSettle();

      expect(find.text('Home'), findsOneWidget);
    });

    testWidgets('Start first reflection navigates to reflection creation', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      // Navigate to last page.
      for (var i = 0; i < 4; i++) {
        await tester.tap(find.text('Continue'));
        await tester.pumpAndSettle();
      }

      await tester.tap(find.text('Start your first reflection'));
      await tester.pumpAndSettle();

      expect(find.text('New Reflection'), findsOneWidget);
    });
  });
}
