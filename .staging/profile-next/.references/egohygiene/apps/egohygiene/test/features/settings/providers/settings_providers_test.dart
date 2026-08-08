import 'package:egohygiene/features/settings/providers/settings_providers.dart';
import 'package:egohygiene/shared/providers/storage_providers.dart';
import 'package:egohygiene/shared/settings/settings_category.dart';
import 'package:egohygiene/shared/settings/settings_definition.dart';
import 'package:egohygiene/shared/settings/settings_entry.dart';
import 'package:egohygiene/shared/settings/settings_manager.dart';
import 'package:egohygiene/shared/settings/settings_repository.dart';
import 'package:egohygiene/shared/settings/settings_value.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../../helpers/fake_storage_service.dart';

// ---------------------------------------------------------------------------
// In-memory SettingsRepository for isolated provider tests.
// ---------------------------------------------------------------------------

class _InMemorySettingsRepository implements SettingsRepository {
  final Map<String, SettingsEntry> _store = {};

  @override
  Future<void> init() async {}

  @override
  Future<SettingsEntry?> get(String key) async => _store[key];

  @override
  Future<void> save(SettingsEntry entry) async => _store[entry.key] = entry;

  @override
  Future<void> delete(String key) async => _store.remove(key);

  @override
  Future<Map<String, SettingsEntry>> getAll() async => Map.of(_store);

  @override
  Future<void> clear() async => _store.clear();
}

// ---------------------------------------------------------------------------
// Sample definitions used in tests.
// ---------------------------------------------------------------------------

const _analyticsEnabled = SettingsDefinition(
  key: 'preferences.analytics',
  category: SettingsCategory.preferences,
  defaultValue: BoolSettingsValue(true),
  label: 'Analytics',
);

const _debugMode = SettingsDefinition(
  key: 'developer.debug_mode',
  category: SettingsCategory.developer,
  defaultValue: BoolSettingsValue(false),
);

// ---------------------------------------------------------------------------
// Helper that builds a container with an in-memory repository and the given
// definitions registered on the manager.
// ---------------------------------------------------------------------------

ProviderContainer _makeContainer({
  List<SettingsDefinition> definitions = const [
    _analyticsEnabled,
    _debugMode,
  ],
}) {
  final repository = _InMemorySettingsRepository();
  final container = ProviderContainer(
    overrides: [
      settingsRepositoryProvider.overrideWith((_) => repository),
      settingsManagerProvider.overrideWith((_) {
        final manager = SettingsManager(repository: repository);
        manager.registerAll(definitions);
        return manager;
      }),
    ],
  );
  return container;
}

void main() {
  group('settingsRepositoryProvider', () {
    test('uses overridable storageServiceProvider', () async {
      final storage = FakeStorageService();
      final container = ProviderContainer(
        overrides: [storageServiceProvider.overrideWithValue(storage)],
      );
      addTearDown(container.dispose);

      final repository = container.read(settingsRepositoryProvider);
      const entry = SettingsEntry(
        key: 'preferences.analytics',
        value: BoolSettingsValue(false),
      );

      await repository.save(entry);

      expect(
        await storage.get('settings.v1.preferences.analytics'),
        isNotNull,
      );
      expect(await repository.get('preferences.analytics'), entry);
    });
  });

  group('settingsManagerProvider', () {
    test('creates a manager with registered definitions', () {
      final container = _makeContainer();
      addTearDown(container.dispose);

      final manager = container.read(settingsManagerProvider);
      expect(manager.allDefinitions, isNotEmpty);
    });
  });

  group('SettingsNotifier (settingsProvider)', () {
    test('initial state contains defaults for all registered definitions', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      final state = await container.read(settingsProvider.future);

      expect(state['preferences.analytics'], const BoolSettingsValue(true));
      expect(state['developer.debug_mode'], const BoolSettingsValue(false));
    });

    test('setValue updates state optimistically', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(settingsProvider.future);

      await container.read(settingsProvider.notifier).setValue('preferences.analytics', const BoolSettingsValue(false));

      final state = container.read(settingsProvider).requireValue;
      expect(state['preferences.analytics'], const BoolSettingsValue(false));
    });

    test('setValue persists value to manager', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(settingsProvider.future);

      await container.read(settingsProvider.notifier).setValue('developer.debug_mode', const BoolSettingsValue(true));

      final manager = container.read(settingsManagerProvider);
      final value = await manager.getValue('developer.debug_mode');
      expect(value, const BoolSettingsValue(true));
    });

    test('reset restores definition default', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(settingsProvider.notifier).setValue('preferences.analytics', const BoolSettingsValue(false));

      await container.read(settingsProvider.notifier).reset('preferences.analytics');

      final state = await container.read(settingsProvider.future);
      expect(state['preferences.analytics'], const BoolSettingsValue(true));
    });

    test('resetAll restores all definition defaults', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(settingsProvider.notifier).setValue('preferences.analytics', const BoolSettingsValue(false));
      await container.read(settingsProvider.notifier).setValue('developer.debug_mode', const BoolSettingsValue(true));

      await container.read(settingsProvider.notifier).resetAll();

      final state = await container.read(settingsProvider.future);
      expect(state['preferences.analytics'], const BoolSettingsValue(true));
      expect(state['developer.debug_mode'], const BoolSettingsValue(false));
    });

    test('registerDefinitions adds new definitions and reloads state', () async {
      final container = _makeContainer(definitions: [_analyticsEnabled]);
      addTearDown(container.dispose);

      await container.read(settingsProvider.future);

      const extraDefinition = SettingsDefinition(
        key: 'appearance.compact_mode',
        category: SettingsCategory.appearance,
        defaultValue: BoolSettingsValue(false),
        label: 'Compact Mode',
      );

      await container.read(settingsProvider.notifier).registerDefinitions([extraDefinition]);

      final state = await container.read(settingsProvider.future);
      expect(state['appearance.compact_mode'], const BoolSettingsValue(false));
    });

    test('all AppThemeMode-equivalent: all definition keys are represented after build', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      final state = await container.read(settingsProvider.future);
      expect(state.containsKey('preferences.analytics'), isTrue);
      expect(state.containsKey('developer.debug_mode'), isTrue);
    });
  });
}
