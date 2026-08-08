/// Reusable helpers for Ego Hygiene integration tests.
///
/// Provides common fakes, overrides, and pump utilities so each integration
/// test file can stay focused on the flow it exercises.
library;

import 'package:drift/native.dart';
import 'package:egohygiene/app/app.dart';
import 'package:egohygiene/app/authentication/providers/session_manager.dart';
import 'package:egohygiene/app/startup/presentation/splash_transition.dart';
import 'package:egohygiene/app/startup/providers/startup_manager.dart';
import 'package:egohygiene/features/onboarding/providers/onboarding_providers.dart';
import 'package:egohygiene/shared/providers/database_providers.dart';
import 'package:egohygiene/shared/providers/storage_providers.dart';
import 'package:egohygiene/shared/services/storage_service.dart';
import 'package:egohygiene/shared/storage/app_database.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod/misc.dart' show Override;

// ---------------------------------------------------------------------------
// Fakes
// ---------------------------------------------------------------------------

/// In-memory [StorageService] that avoids platform-specific persistence.
///
/// Use this in integration tests to keep state isolated and deterministic.
class FakeStorageService implements StorageService {
  final Map<String, String> _store = {};

  @override
  Future<void> clear() async => _store.clear();

  @override
  Future<void> delete(String key) async => _store.remove(key);

  @override
  Future<bool> exists(String key) async => _store.containsKey(key);

  @override
  Future<String?> get(String key) async => _store[key];

  @override
  Future<List<String>> getAllKeys() async => _store.keys.toList();

  @override
  Future<void> init() async {}

  @override
  Future<void> save(String key, String value) async => _store[key] = value;
}

/// [OnboardingManager] override that immediately reports onboarding as
/// completed, simulating a returning user so tests land on the home screen.
class CompletedOnboardingManager extends OnboardingManager {
  @override
  OnboardingStatus build() => OnboardingStatus.completed;

  @override
  Future<void> initialize() async {}
}

/// [OnboardingManager] override that immediately reports onboarding as
/// required, simulating a first-time user who has not completed the flow.
class RequiredOnboardingManager extends OnboardingManager {
  @override
  OnboardingStatus build() => OnboardingStatus.required;

  @override
  Future<void> initialize() async {}
}

// ---------------------------------------------------------------------------
// Pump helpers
// ---------------------------------------------------------------------------

/// Pumps [EgoHygieneApp] with the standard integration-test overrides and
/// waits for the widget tree to settle.
///
/// Overrides applied:
/// - [authenticationStorageServiceProvider] → [FakeStorageService]
/// - [storageServiceProvider] → [FakeStorageService]
/// - [appDatabaseProvider] → in-memory [AppDatabase] (no file-system I/O)
/// - [startupTransitionProvider] → zero-duration splash (no artificial delay)
/// - [onboardingManagerProvider] → [CompletedOnboardingManager]
///
/// Additional [overrides] are merged on top of the defaults, allowing callers
/// to customize providers for specific flows.
Future<void> pumpApp(
  WidgetTester tester, {
  Iterable<Override> overrides = const [],
}) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        authenticationStorageServiceProvider.overrideWithValue(
          FakeStorageService(),
        ),
        storageServiceProvider.overrideWithValue(FakeStorageService()),
        appDatabaseProvider.overrideWithValue(
          AppDatabase(executor: NativeDatabase.memory()),
        ),
        startupTransitionProvider.overrideWithValue(
          const SplashTransition(minimumDisplayDuration: Duration.zero),
        ),
        onboardingManagerProvider.overrideWith(
          CompletedOnboardingManager.new,
        ),
        ...overrides,
      ],
      child: const EgoHygieneApp(),
    ),
  );

  await tester.pumpAndSettle();
}

/// Pumps [EgoHygieneApp] with the real [OnboardingManager] backed by
/// [sharedStorage], allowing restart-persistence tests to simulate a cold
/// app launch against a pre-seeded storage state.
///
/// Unlike [pumpApp], this helper does NOT override
/// [onboardingManagerProvider], so the real [OnboardingManager] reads the
/// completion flag from [sharedStorage] during startup.
Future<void> pumpAppWithRealOnboarding(
  WidgetTester tester, {
  required FakeStorageService sharedStorage,
  Iterable<Override> overrides = const [],
}) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        authenticationStorageServiceProvider.overrideWithValue(
          FakeStorageService(),
        ),
        storageServiceProvider.overrideWithValue(sharedStorage),
        appDatabaseProvider.overrideWithValue(
          AppDatabase(executor: NativeDatabase.memory()),
        ),
        startupTransitionProvider.overrideWithValue(
          const SplashTransition(minimumDisplayDuration: Duration.zero),
        ),
        ...overrides,
      ],
      child: const EgoHygieneApp(),
    ),
  );

  await tester.pumpAndSettle();
}
