import 'package:egohygiene/features/settings/data/local_settings_repository.dart';
import 'package:egohygiene/shared/services/storage_service.dart';
import 'package:egohygiene/shared/settings/settings_entry.dart';
import 'package:egohygiene/shared/settings/settings_value.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// In-memory StorageService for isolated repository tests.
// ---------------------------------------------------------------------------

class _InMemoryStorage implements StorageService {
  final Map<String, String> _data = {};

  @override
  Future<void> init() async {}

  @override
  Future<void> save(String key, String value) async => _data[key] = value;

  @override
  Future<String?> get(String key) async => _data[key];

  @override
  Future<void> delete(String key) async => _data.remove(key);

  @override
  Future<bool> exists(String key) async => _data.containsKey(key);

  @override
  Future<void> clear() async => _data.clear();

  @override
  Future<List<String>> getAllKeys() async => _data.keys.toList();
}

void main() {
  group('LocalSettingsRepository', () {
    late _InMemoryStorage storage;
    late LocalSettingsRepository repository;

    setUp(() {
      storage = _InMemoryStorage();
      repository = LocalSettingsRepository(storage: storage);
    });

    // -------------------------------------------------------------------------
    // get / save
    // -------------------------------------------------------------------------

    group('get / save', () {
      test('returns null when key has not been saved', () async {
        final entry = await repository.get('any.key');
        expect(entry, isNull);
      });

      test('saves and retrieves a BoolSettingsValue', () async {
        const entry = SettingsEntry(
          key: 'preferences.analytics',
          value: BoolSettingsValue(true),
        );
        await repository.save(entry);

        final loaded = await repository.get('preferences.analytics');
        expect(loaded, entry);
      });

      test('saves and retrieves a StringSettingsValue', () async {
        const entry = SettingsEntry(
          key: 'ai.provider',
          value: StringSettingsValue('openai'),
        );
        await repository.save(entry);

        final loaded = await repository.get('ai.provider');
        expect(loaded, entry);
      });

      test('saves and retrieves an IntSettingsValue', () async {
        const entry = SettingsEntry(
          key: 'notifications.reminder_hour',
          value: IntSettingsValue(9),
        );
        await repository.save(entry);

        final loaded = await repository.get('notifications.reminder_hour');
        expect(loaded, entry);
      });

      test('saves and retrieves a DoubleSettingsValue', () async {
        const entry = SettingsEntry(
          key: 'appearance.font_scale',
          value: DoubleSettingsValue(1.5),
        );
        await repository.save(entry);

        final loaded = await repository.get('appearance.font_scale');
        expect(loaded, entry);
      });

      test('save overwrites an existing entry for the same key', () async {
        await repository.save(
          const SettingsEntry(key: 'test.key', value: BoolSettingsValue(true)),
        );
        await repository.save(
          const SettingsEntry(key: 'test.key', value: BoolSettingsValue(false)),
        );

        final loaded = await repository.get('test.key');
        expect(loaded?.value, const BoolSettingsValue(false));
      });
    });

    // -------------------------------------------------------------------------
    // delete
    // -------------------------------------------------------------------------

    group('delete', () {
      test('removes an existing entry', () async {
        await repository.save(
          const SettingsEntry(key: 'test.key', value: BoolSettingsValue(true)),
        );
        await repository.delete('test.key');

        expect(await repository.get('test.key'), isNull);
      });

      test('is a no-op when entry does not exist', () async {
        await expectLater(repository.delete('non.existent'), completes);
      });
    });

    // -------------------------------------------------------------------------
    // getAll
    // -------------------------------------------------------------------------

    group('getAll', () {
      test('returns empty map when nothing is stored', () async {
        final all = await repository.getAll();
        expect(all, isEmpty);
      });

      test('returns all saved entries', () async {
        await repository.save(
          const SettingsEntry(key: 'key.a', value: BoolSettingsValue(true)),
        );
        await repository.save(
          const SettingsEntry(key: 'key.b', value: IntSettingsValue(42)),
        );

        final all = await repository.getAll();
        expect(all.length, 2);
        expect(all['key.a']?.value, const BoolSettingsValue(true));
        expect(all['key.b']?.value, const IntSettingsValue(42));
      });

      test('does not include non-settings keys in the storage', () async {
        // Simulate a foreign key written directly to storage.
        await storage.save('unrelated.key', 'some value');
        await repository.save(
          const SettingsEntry(key: 'settings.only', value: BoolSettingsValue(true)),
        );

        final all = await repository.getAll();
        expect(all.keys, contains('settings.only'));
        expect(all.keys, isNot(contains('unrelated.key')));
      });
    });

    // -------------------------------------------------------------------------
    // clear
    // -------------------------------------------------------------------------

    group('clear', () {
      test('removes all settings entries', () async {
        await repository.save(
          const SettingsEntry(key: 'key.a', value: BoolSettingsValue(true)),
        );
        await repository.save(
          const SettingsEntry(key: 'key.b', value: BoolSettingsValue(false)),
        );

        await repository.clear();

        expect(await repository.getAll(), isEmpty);
      });

      test('does not remove non-settings keys', () async {
        await storage.save('foreign.key', 'stays');
        await repository.save(
          const SettingsEntry(key: 'settings.key', value: BoolSettingsValue(true)),
        );

        await repository.clear();

        expect(await storage.get('foreign.key'), 'stays');
        expect(await repository.get('settings.key'), isNull);
      });
    });

    // -------------------------------------------------------------------------
    // Corrupt data resilience
    // -------------------------------------------------------------------------

    group('corrupt data', () {
      test('get returns null when stored JSON is not a map', () async {
        await storage.save('settings.v1.bad.key', '[1, 2, 3]');
        expect(await repository.get('bad.key'), isNull);
      });

      test('get returns null when stored value has unknown type', () async {
        await storage.save(
          'settings.v1.bad.key',
          '{"type":"unknown","value":"x"}',
        );
        expect(await repository.get('bad.key'), isNull);
      });

      test('get returns null when stored data is not valid JSON', () async {
        await storage.save('settings.v1.bad.key', 'not json {{}}');
        expect(await repository.get('bad.key'), isNull);
      });

      test('getAll skips corrupt entries', () async {
        await storage.save('settings.v1.bad.key', 'not json {{}}');
        await repository.save(
          const SettingsEntry(key: 'good.key', value: BoolSettingsValue(true)),
        );

        final all = await repository.getAll();
        expect(all.keys, contains('good.key'));
        expect(all.keys, isNot(contains('bad.key')));
      });
    });
  });
}
