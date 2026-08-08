import 'package:egohygiene/features/settings/providers/ai_settings_providers.dart';
import 'package:egohygiene/features/settings/providers/settings_providers.dart';
import 'package:egohygiene/shared/ai/ai_mode.dart';
import 'package:egohygiene/shared/settings/settings_category.dart';
import 'package:egohygiene/shared/settings/settings_definition.dart';
import 'package:egohygiene/shared/settings/settings_entry.dart';
import 'package:egohygiene/shared/settings/settings_manager.dart';
import 'package:egohygiene/shared/settings/settings_repository.dart';
import 'package:egohygiene/shared/settings/settings_value.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

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

ProviderContainer _makeContainer({
  List<SettingsDefinition> definitions = const [],
}) {
  final repository = _InMemorySettingsRepository();
  return ProviderContainer(
    overrides: [
      settingsRepositoryProvider.overrideWith((_) => repository),
      settingsManagerProvider.overrideWith((_) {
        const aiModeDef = SettingsDefinition(
          key: 'ai.mode',
          category: SettingsCategory.ai,
          defaultValue: StringSettingsValue('disabled'),
          label: 'AI Mode',
        );
        const aiPrivacyDef = SettingsDefinition(
          key: 'ai.privacy_mode',
          category: SettingsCategory.ai,
          defaultValue: BoolSettingsValue(false),
          label: 'Privacy Mode',
        );
        final manager = SettingsManager(repository: repository);
        manager.registerAll([aiModeDef, aiPrivacyDef, ...definitions]);
        return manager;
      }),
    ],
  );
}

void main() {
  group('AiModeNotifier (aiModeProvider)', () {
    test('defaults to AiMode.disabled when no value is stored', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      final mode = await container.read(aiModeProvider.future);

      expect(mode, AiMode.disabled);
    });

    test('setMode persists and updates state', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(aiModeProvider.future);
      await container.read(aiModeProvider.notifier).setMode(AiMode.hybrid);
      // Wait for any provider rebuild triggered by the settings dependency.
      final mode = await container.read(aiModeProvider.future);

      expect(mode, AiMode.hybrid);
    });

    test('setMode can switch to cloud', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(aiModeProvider.future);
      await container.read(aiModeProvider.notifier).setMode(AiMode.cloud);
      final mode = await container.read(aiModeProvider.future);

      expect(mode, AiMode.cloud);
    });

    test('setMode can switch to local', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(aiModeProvider.future);
      await container.read(aiModeProvider.notifier).setMode(AiMode.local);
      final mode = await container.read(aiModeProvider.future);

      expect(mode, AiMode.local);
    });

    test('setMode can disable AI', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(aiModeProvider.future);
      await container.read(aiModeProvider.notifier).setMode(AiMode.cloud);
      await container.read(aiModeProvider.notifier).setMode(AiMode.disabled);
      final mode = await container.read(aiModeProvider.future);

      expect(mode, AiMode.disabled);
    });
  });

  group('AiPrivacyModeNotifier (aiPrivacyModeProvider)', () {
    test('defaults to false when no value is stored', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      final enabled = await container.read(aiPrivacyModeProvider.future);

      expect(enabled, isFalse);
    });

    test('setPrivacyMode(enabled: true) persists and updates state', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(aiPrivacyModeProvider.future);
      await container.read(aiPrivacyModeProvider.notifier).setPrivacyMode(enabled: true);
      final enabled = await container.read(aiPrivacyModeProvider.future);

      expect(enabled, isTrue);
    });

    test('setPrivacyMode(enabled: false) toggles back', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(aiPrivacyModeProvider.future);
      await container.read(aiPrivacyModeProvider.notifier).setPrivacyMode(enabled: true);
      await container.read(aiPrivacyModeProvider.notifier).setPrivacyMode(enabled: false);
      final enabled = await container.read(aiPrivacyModeProvider.future);

      expect(enabled, isFalse);
    });
  });

  group('AiMode enum', () {
    test('toJson returns the enum name', () {
      expect(AiMode.cloud.toJson(), 'cloud');
      expect(AiMode.local.toJson(), 'local');
      expect(AiMode.hybrid.toJson(), 'hybrid');
      expect(AiMode.disabled.toJson(), 'disabled');
    });

    test('fromJson parses known values correctly', () {
      expect(AiMode.fromJson('cloud'), AiMode.cloud);
      expect(AiMode.fromJson('local'), AiMode.local);
      expect(AiMode.fromJson('hybrid'), AiMode.hybrid);
      expect(AiMode.fromJson('disabled'), AiMode.disabled);
    });

    test('fromJson returns disabled for unrecognised values', () {
      expect(AiMode.fromJson(''), AiMode.disabled);
      expect(AiMode.fromJson('openai'), AiMode.disabled);
      expect(AiMode.fromJson('CLOUD'), AiMode.disabled);
    });

    test('round-trip serialisation is stable', () {
      for (final mode in AiMode.values) {
        expect(AiMode.fromJson(mode.toJson()), mode);
      }
    });
  });
}
