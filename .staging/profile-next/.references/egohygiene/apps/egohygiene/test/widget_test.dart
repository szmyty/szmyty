import 'package:egohygiene/app/app.dart';
import 'package:egohygiene/app/authentication/providers/session_manager.dart';
import 'package:egohygiene/app/startup/presentation/splash_transition.dart';
import 'package:egohygiene/app/startup/providers/startup_manager.dart';
import 'package:egohygiene/features/onboarding/feature.dart';
import 'package:egohygiene/features/reflection/feature.dart';
import 'package:egohygiene/shared/providers/theme_providers.dart';
import 'package:egohygiene/shared/theme/theme_manager.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'helpers/fake_storage_service.dart';
import 'helpers/static_splash_experience.dart';

class _FakeReflectionRepository implements ReflectionRepository {
  @override
  Future<ReflectionModel> create({
    required String body,
    String? title,
    List<String> tags = const [],
  }) {
    throw UnimplementedError();
  }

  @override
  Future<List<ReflectionModel>> getAll() async => const [];

  @override
  Future<ReflectionModel?> getById(String id) async => null;

  @override
  Future<ReflectionModel> update(ReflectionModel reflection) async => reflection;

  @override
  Future<void> deleteById(String id) async {}
}

/// [OnboardingManager] override that immediately reports onboarding as
/// completed, simulating a returning user so the test lands on the home screen.
class _CompletedOnboardingManager extends OnboardingManager {
  @override
  OnboardingStatus build() => OnboardingStatus.completed;

  /// No-op: the test starts in the completed state and must not leave it.
  @override
  Future<void> initialize() async {}
}

void main() {
  testWidgets('App launches and shows home screen', (tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authenticationStorageServiceProvider.overrideWithValue(
            FakeStorageService(),
          ),
          themeManagerProvider.overrideWithValue(
            ThemeManager(storage: FakeStorageService()),
          ),
          splashExperienceProvider.overrideWithValue(
            const StaticSplashExperience(),
          ),
          reflectionRepositoryProvider.overrideWith(
            (ref) => _FakeReflectionRepository(),
          ),
          startupTransitionProvider.overrideWithValue(
            const SplashTransition(minimumDisplayDuration: Duration.zero),
          ),
          // Simulate a returning user who has already completed onboarding.
          onboardingManagerProvider.overrideWith(_CompletedOnboardingManager.new),
        ],
        child: const EgoHygieneApp(),
      ),
    );
    await tester.pumpAndSettle();

    // Verify that the persistent navigation shell is present.
    expect(find.byType(NavigationBar), findsOneWidget);

    // Verify that the home screen content is displayed.
    expect(find.text('Ego Hygiene'), findsOneWidget);
    expect(find.text("Today's Gentle Rhythm"), findsOneWidget);

    // 'Reflection' is currently present as the navigation destination label.
    expect(find.text('Reflection'), findsOneWidget);

    // 'Memory' and 'Progress' appear as navigation bar labels.  The explore
    // chips that share the same label live in a lazily-rendered
    // SliverList section that may not yet be in the widget tree, so we only
    // assert at least one occurrence of each.
    expect(find.text('Memory'), findsAtLeastNWidgets(1));
    expect(find.text('Progress'), findsAtLeastNWidgets(1));

    // 'Settings' is only an explore chip — it is not a shell destination.
    // The chip lives in a lazily-rendered section below the fold, so scroll
    // to it before asserting its presence.
    await tester.scrollUntilVisible(find.text('Settings'), 300);
    expect(find.text('Settings'), findsOneWidget);
  });
}
