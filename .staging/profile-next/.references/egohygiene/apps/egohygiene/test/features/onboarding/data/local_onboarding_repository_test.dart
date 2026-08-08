import 'package:egohygiene/features/onboarding/data/local_onboarding_repository.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../../helpers/fake_storage_service.dart';

void main() {
  group('LocalOnboardingRepository', () {
    test('isCompleted returns false when no value has been stored', () async {
      final repository = LocalOnboardingRepository(
        storage: FakeStorageService(),
      );

      expect(await repository.isCompleted(), isFalse);
    });

    test('isCompleted returns true after markCompleted is called', () async {
      final repository = LocalOnboardingRepository(
        storage: FakeStorageService(),
      );

      await repository.markCompleted();

      expect(await repository.isCompleted(), isTrue);
    });

    test('markCompleted is idempotent', () async {
      final repository = LocalOnboardingRepository(
        storage: FakeStorageService(),
      );

      await repository.markCompleted();
      await repository.markCompleted();

      expect(await repository.isCompleted(), isTrue);
    });

    test('isCompleted returns false when stored value is not "true"', () async {
      final storage = FakeStorageService();
      await storage.save(LocalOnboardingRepository.storageKey, 'false');

      final repository = LocalOnboardingRepository(storage: storage);

      expect(await repository.isCompleted(), isFalse);
    });

    test('two instances share the same storage state', () async {
      final storage = FakeStorageService();
      final first = LocalOnboardingRepository(storage: storage);
      final second = LocalOnboardingRepository(storage: storage);

      await first.markCompleted();

      expect(await second.isCompleted(), isTrue);
    });
  });
}
