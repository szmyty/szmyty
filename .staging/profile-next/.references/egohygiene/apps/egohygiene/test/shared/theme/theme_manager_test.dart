import 'package:egohygiene/shared/services/storage_service.dart';
import 'package:egohygiene/shared/theme/app_theme_mode.dart';
import 'package:egohygiene/shared/theme/theme_manager.dart';
import 'package:egohygiene/shared/theme/theme_preferences.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

/// In-memory [StorageService] used in tests.
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
  group('ThemeManager', () {
    late ThemeManager manager;

    setUp(() {
      manager = ThemeManager(storage: _InMemoryStorage());
    });

    test('loadPreferences returns defaults when nothing is saved', () async {
      final prefs = await manager.loadPreferences();
      expect(prefs, const ThemePreferences());
    });

    test('savePreferences then loadPreferences roundtrips correctly', () async {
      const saved = ThemePreferences(
        themeMode: AppThemeMode.amoled,
        useDynamicColor: true,
      );

      await manager.savePreferences(saved);
      final loaded = await manager.loadPreferences();

      expect(loaded, saved);
    });

    test('loads all AppThemeMode values correctly', () async {
      for (final mode in AppThemeMode.values) {
        final prefs = ThemePreferences(themeMode: mode);
        await manager.savePreferences(prefs);
        final loaded = await manager.loadPreferences();
        expect(loaded.themeMode, mode);
      }
    });

    test('returns defaults when stored data is corrupt JSON', () async {
      final storage = _InMemoryStorage();
      await storage.save(ThemePreferences.storageKey, 'not valid json{{');
      final corruptManager = ThemeManager(storage: storage);

      final prefs = await corruptManager.loadPreferences();
      expect(prefs, const ThemePreferences());
    });

    test('returns defaults when stored data is valid JSON but wrong type', () async {
      final storage = _InMemoryStorage();
      await storage.save(ThemePreferences.storageKey, '[1, 2, 3]');
      final badTypeManager = ThemeManager(storage: storage);

      final prefs = await badTypeManager.loadPreferences();
      expect(prefs, const ThemePreferences());
    });

    test('overwrites previous preferences on save', () async {
      const first = ThemePreferences(themeMode: AppThemeMode.light);
      const second = ThemePreferences(themeMode: AppThemeMode.dark);

      await manager.savePreferences(first);
      await manager.savePreferences(second);

      final loaded = await manager.loadPreferences();
      expect(loaded, second);
    });

    test('roundtrips seedColor through savePreferences / loadPreferences', () async {
      const seed = Color(0xFF6366F1);
      const saved = ThemePreferences(seedColor: seed);

      await manager.savePreferences(saved);
      final loaded = await manager.loadPreferences();

      expect(loaded.seedColor, seed);
    });

    test('roundtrips imageReference through savePreferences / loadPreferences', () async {
      const ref = 'https://example.com/wallpaper.jpg';
      const saved = ThemePreferences(imageReference: ref);

      await manager.savePreferences(saved);
      final loaded = await manager.loadPreferences();

      expect(loaded.imageReference, ref);
    });

    test('null seedColor is preserved on roundtrip', () async {
      const saved = ThemePreferences(themeMode: AppThemeMode.dark);
      await manager.savePreferences(saved);
      final loaded = await manager.loadPreferences();
      expect(loaded.seedColor, isNull);
    });
  });
}
