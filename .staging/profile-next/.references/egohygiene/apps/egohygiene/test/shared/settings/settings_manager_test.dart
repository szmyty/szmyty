import 'package:egohygiene/shared/settings/settings_category.dart';
import 'package:egohygiene/shared/settings/settings_definition.dart';
import 'package:egohygiene/shared/settings/settings_entry.dart';
import 'package:egohygiene/shared/settings/settings_manager.dart';
import 'package:egohygiene/shared/settings/settings_repository.dart';
import 'package:egohygiene/shared/settings/settings_value.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// In-memory SettingsRepository used across all tests.
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
  label: 'Debug Mode',
);

const _fontScale = SettingsDefinition(
  key: 'appearance.font_scale',
  category: SettingsCategory.appearance,
  defaultValue: DoubleSettingsValue(1),
  label: 'Font Scale',
);

const _aiProvider = SettingsDefinition(
  key: 'ai.provider',
  category: SettingsCategory.ai,
  defaultValue: StringSettingsValue(''),
  label: 'AI Provider',
);

const _reminderHour = SettingsDefinition(
  key: 'notifications.reminder_hour',
  category: SettingsCategory.notifications,
  defaultValue: IntSettingsValue(20),
  label: 'Reminder Hour',
);

void main() {
  group('SettingsManager', () {
    late _InMemorySettingsRepository repository;
    late SettingsManager manager;

    setUp(() {
      repository = _InMemorySettingsRepository();
      manager = SettingsManager(repository: repository);
    });

    // -------------------------------------------------------------------------
    // Definition registry
    // -------------------------------------------------------------------------

    group('definition registry', () {
      test('register adds a single definition', () {
        manager.register(_analyticsEnabled);

        expect(manager.allDefinitions, contains(_analyticsEnabled));
      });

      test('registerAll adds multiple definitions', () {
        manager.registerAll([_analyticsEnabled, _debugMode, _fontScale]);

        expect(manager.allDefinitions, containsAll([_analyticsEnabled, _debugMode, _fontScale]));
      });

      test('register replaces existing definition with same key', () {
        const original = SettingsDefinition(
          key: 'preferences.analytics',
          category: SettingsCategory.preferences,
          defaultValue: BoolSettingsValue(true),
        );
        const replacement = SettingsDefinition(
          key: 'preferences.analytics',
          category: SettingsCategory.preferences,
          defaultValue: BoolSettingsValue(false),
          label: 'Updated Analytics',
        );

        manager.register(original);
        manager.register(replacement);

        expect(manager.allDefinitions.length, 1);
        expect(manager.definitionFor('preferences.analytics'), replacement);
      });

      test('definitionFor returns null for unknown key', () {
        expect(manager.definitionFor('unknown.key'), isNull);
      });

      test('definitionsForCategory returns only matching definitions', () {
        manager.registerAll([
          _analyticsEnabled,
          _debugMode,
          _fontScale,
          _aiProvider,
          _reminderHour,
        ]);

        final developerDefs = manager.definitionsForCategory(SettingsCategory.developer);
        expect(developerDefs, [_debugMode]);

        final appearanceDefs = manager.definitionsForCategory(SettingsCategory.appearance);
        expect(appearanceDefs, [_fontScale]);
      });

      test('definitionsForCategory returns empty list for unregistered category', () {
        manager.register(_analyticsEnabled);

        final result = manager.definitionsForCategory(SettingsCategory.notifications);
        expect(result, isEmpty);
      });
    });

    // -------------------------------------------------------------------------
    // getValue
    // -------------------------------------------------------------------------

    group('getValue', () {
      test('returns default when no stored value exists', () async {
        manager.register(_analyticsEnabled);

        final value = await manager.getValue('preferences.analytics');
        expect(value, const BoolSettingsValue(true));
      });

      test('returns stored value when one exists', () async {
        manager.register(_analyticsEnabled);
        await manager.setValue('preferences.analytics', const BoolSettingsValue(false));

        final value = await manager.getValue('preferences.analytics');
        expect(value, const BoolSettingsValue(false));
      });

      test('returns null for completely unknown key', () async {
        final value = await manager.getValue('completely.unknown');
        expect(value, isNull);
      });

      test('handles all value types', () async {
        manager.registerAll([_fontScale, _aiProvider, _reminderHour]);

        await manager.setValue('appearance.font_scale', const DoubleSettingsValue(1.5));
        await manager.setValue('ai.provider', const StringSettingsValue('openai'));
        await manager.setValue('notifications.reminder_hour', const IntSettingsValue(8));

        expect(await manager.getValue('appearance.font_scale'), const DoubleSettingsValue(1.5));
        expect(await manager.getValue('ai.provider'), const StringSettingsValue('openai'));
        expect(await manager.getValue('notifications.reminder_hour'), const IntSettingsValue(8));
      });
    });

    // -------------------------------------------------------------------------
    // setValue
    // -------------------------------------------------------------------------

    group('setValue', () {
      test('persists value to repository', () async {
        manager.register(_analyticsEnabled);
        await manager.setValue('preferences.analytics', const BoolSettingsValue(false));

        final entry = await repository.get('preferences.analytics');
        expect(entry?.value, const BoolSettingsValue(false));
      });

      test('overrides the previous value', () async {
        manager.register(_fontScale);
        await manager.setValue('appearance.font_scale', const DoubleSettingsValue(1.25));
        await manager.setValue('appearance.font_scale', const DoubleSettingsValue(2));

        final value = await manager.getValue('appearance.font_scale');
        expect(value, const DoubleSettingsValue(2));
      });
    });

    // -------------------------------------------------------------------------
    // reset
    // -------------------------------------------------------------------------

    group('reset', () {
      test('removes stored value so default is returned again', () async {
        manager.register(_analyticsEnabled);
        await manager.setValue('preferences.analytics', const BoolSettingsValue(false));
        await manager.reset('preferences.analytics');

        final value = await manager.getValue('preferences.analytics');
        expect(value, const BoolSettingsValue(true));
      });

      test('is a no-op when no value is stored', () async {
        manager.register(_analyticsEnabled);
        await expectLater(
          manager.reset('preferences.analytics'),
          completes,
        );
      });
    });

    // -------------------------------------------------------------------------
    // resetAll
    // -------------------------------------------------------------------------

    group('resetAll', () {
      test('removes stored overrides for all registered definitions', () async {
        manager.registerAll([_analyticsEnabled, _debugMode]);
        await manager.setValue('preferences.analytics', const BoolSettingsValue(false));
        await manager.setValue('developer.debug_mode', const BoolSettingsValue(true));

        await manager.resetAll();

        expect(await manager.getValue('preferences.analytics'), const BoolSettingsValue(true));
        expect(await manager.getValue('developer.debug_mode'), const BoolSettingsValue(false));
      });
    });

    // -------------------------------------------------------------------------
    // getAllValues
    // -------------------------------------------------------------------------

    group('getAllValues', () {
      test('returns defaults for all registered definitions when nothing is stored', () async {
        manager.registerAll([_analyticsEnabled, _debugMode]);

        final values = await manager.getAllValues();

        expect(values['preferences.analytics'], const BoolSettingsValue(true));
        expect(values['developer.debug_mode'], const BoolSettingsValue(false));
      });

      test('merges stored overrides with defaults', () async {
        manager.registerAll([_analyticsEnabled, _debugMode]);
        await manager.setValue('developer.debug_mode', const BoolSettingsValue(true));

        final values = await manager.getAllValues();

        expect(values['preferences.analytics'], const BoolSettingsValue(true));
        expect(values['developer.debug_mode'], const BoolSettingsValue(true));
      });
    });

    // -------------------------------------------------------------------------
    // Import / Export
    // -------------------------------------------------------------------------

    group('exportToJson / importFromJson', () {
      test('export returns empty entries when nothing is stored', () async {
        final json = await manager.exportToJson();

        expect(json['version'], 1);
        expect(json['entries'], isEmpty);
      });

      test('export roundtrips through import', () async {
        manager.registerAll([_analyticsEnabled, _fontScale]);
        await manager.setValue('preferences.analytics', const BoolSettingsValue(false));
        await manager.setValue('appearance.font_scale', const DoubleSettingsValue(1.5));

        final exported = await manager.exportToJson();

        // Fresh manager with same repository (cleared).
        final freshRepository = _InMemorySettingsRepository();
        final freshManager = SettingsManager(repository: freshRepository);
        freshManager.registerAll([_analyticsEnabled, _fontScale]);

        await freshManager.importFromJson(exported);

        expect(
          await freshManager.getValue('preferences.analytics'),
          const BoolSettingsValue(false),
        );
        expect(
          await freshManager.getValue('appearance.font_scale'),
          const DoubleSettingsValue(1.5),
        );
      });

      test('importFromJson silently skips malformed entries', () async {
        manager.register(_analyticsEnabled);

        await manager.importFromJson({
          'version': 1,
          'entries': {
            'preferences.analytics': {'type': 'unknown_type', 'value': 'x'},
            'appearance.font_scale': 'not_a_map',
          },
        });

        // No crash; existing defaults remain.
        expect(
          await manager.getValue('preferences.analytics'),
          const BoolSettingsValue(true),
        );
      });

      test('importFromJson silently does nothing when entries key is missing', () async {
        await expectLater(
          manager.importFromJson({'version': 1}),
          completes,
        );
      });
    });
  });

  // ---------------------------------------------------------------------------
  // SettingsValue serialisation
  // ---------------------------------------------------------------------------

  group('SettingsValue', () {
    test('BoolSettingsValue roundtrips through toJson/fromJson', () {
      for (final v in [true, false]) {
        final original = BoolSettingsValue(v);
        final roundtripped = SettingsValue.fromJson(original.toJson());
        expect(roundtripped, original);
      }
    });

    test('StringSettingsValue roundtrips through toJson/fromJson', () {
      const original = StringSettingsValue('hello world');
      final roundtripped = SettingsValue.fromJson(original.toJson());
      expect(roundtripped, original);
    });

    test('IntSettingsValue roundtrips through toJson/fromJson', () {
      const original = IntSettingsValue(42);
      final roundtripped = SettingsValue.fromJson(original.toJson());
      expect(roundtripped, original);
    });

    test('DoubleSettingsValue roundtrips through toJson/fromJson', () {
      const original = DoubleSettingsValue(3.14);
      final roundtripped = SettingsValue.fromJson(original.toJson());
      expect(roundtripped, original);
    });

    test('fromJson throws FormatException for unknown type', () {
      expect(
        () => SettingsValue.fromJson({'type': 'unknown', 'value': 'x'}),
        throwsA(isA<FormatException>()),
      );
    });

    test('equality and hashCode are value-based', () {
      expect(const BoolSettingsValue(true), equals(const BoolSettingsValue(true)));
      expect(const BoolSettingsValue(true), isNot(equals(const BoolSettingsValue(false))));
      expect(const StringSettingsValue('a'), equals(const StringSettingsValue('a')));
      expect(const IntSettingsValue(1), isNot(equals(const IntSettingsValue(2))));
      expect(const DoubleSettingsValue(1), equals(const DoubleSettingsValue(1)));
    });
  });

  // ---------------------------------------------------------------------------
  // SettingsDefinition
  // ---------------------------------------------------------------------------

  group('SettingsDefinition', () {
    test('equality is key-based', () {
      const a = SettingsDefinition(
        key: 'test.key',
        category: SettingsCategory.preferences,
        defaultValue: BoolSettingsValue(true),
        label: 'A',
      );
      const b = SettingsDefinition(
        key: 'test.key',
        category: SettingsCategory.preferences,
        defaultValue: BoolSettingsValue(false),
        label: 'B',
      );
      expect(a, equals(b));
      expect(a.hashCode, b.hashCode);
    });

    test('different keys are not equal', () {
      const a = SettingsDefinition(
        key: 'test.a',
        category: SettingsCategory.preferences,
        defaultValue: BoolSettingsValue(true),
      );
      const b = SettingsDefinition(
        key: 'test.b',
        category: SettingsCategory.preferences,
        defaultValue: BoolSettingsValue(true),
      );
      expect(a, isNot(equals(b)));
    });
  });
}
