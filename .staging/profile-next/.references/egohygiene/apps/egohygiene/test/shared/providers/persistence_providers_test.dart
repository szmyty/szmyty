import 'package:drift/native.dart';
import 'package:egohygiene/features/check_in/data/drift_check_in_repository.dart';
import 'package:egohygiene/features/check_in/providers/check_in_providers.dart';
import 'package:egohygiene/features/reflection/data/drift_reflection_repository.dart';
import 'package:egohygiene/features/reflection/providers/reflection_providers.dart';
import 'package:egohygiene/shared/memory/impl/drift_memory_store.dart';
import 'package:egohygiene/shared/providers/database_providers.dart';
import 'package:egohygiene/shared/providers/memory_providers.dart';
import 'package:egohygiene/shared/storage/app_database.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('persistence providers use Drift implementations by default', () async {
    final database = AppDatabase(executor: NativeDatabase.memory());
    final container = ProviderContainer(
      overrides: [appDatabaseProvider.overrideWith((_) => database)],
    );
    addTearDown(() async {
      container.dispose();
      await database.close();
    });

    expect(
      container.read(reflectionRepositoryProvider),
      isA<DriftReflectionRepository>(),
    );
    expect(
      container.read(checkInRepositoryProvider),
      isA<DriftCheckInRepository>(),
    );
    expect(
      container.read(memoryStoreProvider),
      isA<DriftMemoryStore>(),
    );
  });
}
