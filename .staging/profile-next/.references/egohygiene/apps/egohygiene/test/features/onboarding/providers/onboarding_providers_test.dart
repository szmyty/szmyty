import 'package:egohygiene/features/onboarding/data/local_onboarding_repository.dart';
import 'package:egohygiene/features/onboarding/data/onboarding_repository.dart';
import 'package:egohygiene/features/onboarding/providers/onboarding_providers.dart';
import 'package:egohygiene/shared/providers/storage_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../../helpers/fake_storage_service.dart';

void main() {
  ProviderContainer makeContainer({
    Map<String, String> initialStorage = const {},
  }) {
    final storage = FakeStorageService();
    for (final entry in initialStorage.entries) {
      storage.save(entry.key, entry.value);
    }

    return ProviderContainer(
      overrides: [
        storageServiceProvider.overrideWithValue(storage),
      ],
    );
  }

  group('OnboardingManager', () {
    test('initial state is unknown', () {
      final container = makeContainer();
      addTearDown(container.dispose);

      expect(
        container.read(onboardingManagerProvider),
        OnboardingStatus.unknown,
      );
    });

    test('initialize sets status to required when storage is empty', () async {
      final container = makeContainer();
      addTearDown(container.dispose);

      await container.read(onboardingManagerProvider.notifier).initialize();

      expect(
        container.read(onboardingManagerProvider),
        OnboardingStatus.required,
      );
    });

    test('initialize sets status to completed when storage key is true', () async {
      final container = makeContainer(
        initialStorage: {LocalOnboardingRepository.storageKey: 'true'},
      );
      addTearDown(container.dispose);

      await container.read(onboardingManagerProvider.notifier).initialize();

      expect(
        container.read(onboardingManagerProvider),
        OnboardingStatus.completed,
      );
    });

    test('markCompleted persists and updates status to completed', () async {
      final container = makeContainer();
      addTearDown(container.dispose);

      await container.read(onboardingManagerProvider.notifier).initialize();
      expect(
        container.read(onboardingManagerProvider),
        OnboardingStatus.required,
      );

      await container.read(onboardingManagerProvider.notifier).markCompleted();

      expect(
        container.read(onboardingManagerProvider),
        OnboardingStatus.completed,
      );

      // Confirm the completion is persisted in storage.
      final repository = container.read(onboardingRepositoryProvider);
      expect(await repository.isCompleted(), isTrue);
    });

    test('markCompleted is callable without prior initialize', () async {
      final container = makeContainer();
      addTearDown(container.dispose);

      await container.read(onboardingManagerProvider.notifier).markCompleted();

      expect(
        container.read(onboardingManagerProvider),
        OnboardingStatus.completed,
      );
    });
  });

  group('onboardingRepositoryProvider', () {
    test('provides a LocalOnboardingRepository', () {
      final container = makeContainer();
      addTearDown(container.dispose);

      expect(
        container.read(onboardingRepositoryProvider),
        isA<OnboardingRepository>(),
      );
    });
  });
}
