import 'package:egohygiene/shared/providers/theme_providers.dart';
import 'package:egohygiene/shared/services/storage_service.dart';
import 'package:egohygiene/shared/theme/app_theme_mode.dart';
import 'package:egohygiene/shared/theme/theme_manager.dart';
import 'package:egohygiene/shared/theme/theme_preferences.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

/// In-memory [StorageService] for isolated provider tests.
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

/// Creates a [ProviderContainer] with an isolated in-memory storage backend.
ProviderContainer _makeContainer() {
  final storage = _InMemoryStorage();
  return ProviderContainer(
    overrides: [
      themeManagerProvider.overrideWithValue(
        ThemeManager(storage: storage),
      ),
    ],
  );
}

void main() {
  group('ThemePreferencesNotifier', () {
    test('initial state is default ThemePreferences', () {
      final container = _makeContainer();
      addTearDown(container.dispose);

      final prefs = container.read(themePreferencesNotifierProvider);
      expect(prefs, const ThemePreferences());
    });

    test('setThemeMode updates state', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).setThemeMode(AppThemeMode.amoled);

      final prefs = container.read(themePreferencesNotifierProvider);
      expect(prefs.themeMode, AppThemeMode.amoled);
    });

    test('setUseDynamicColor updates state', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).setUseDynamicColor(value: true);

      final prefs = container.read(themePreferencesNotifierProvider);
      expect(prefs.useDynamicColor, true);
    });

    test('setSeedColor updates state', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      const seed = Color(0xFF6366F1);
      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(seed);

      final prefs = container.read(themePreferencesNotifierProvider);
      expect(prefs.seedColor, seed);
    });

    test('setSeedColor null clears the seed color', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      const seed = Color(0xFF6366F1);
      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(seed);
      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(null);

      final prefs = container.read(themePreferencesNotifierProvider);
      expect(prefs.seedColor, isNull);
    });

    test('setImageReference updates state', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      const ref = 'https://example.com/img.jpg';
      await container.read(themePreferencesNotifierProvider.notifier).setImageReference(ref);

      final prefs = container.read(themePreferencesNotifierProvider);
      expect(prefs.imageReference, ref);
    });

    test('resetTheme clears seedColor and imageReference', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(const Color(0xFF6366F1));
      await container.read(themePreferencesNotifierProvider.notifier).resetTheme();

      final prefs = container.read(themePreferencesNotifierProvider);
      expect(prefs.seedColor, isNull);
      expect(prefs.imageReference, isNull);
    });

    test('resetTheme preserves themeMode', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).setThemeMode(AppThemeMode.dark);
      await container.read(themePreferencesNotifierProvider.notifier).resetTheme();

      final prefs = container.read(themePreferencesNotifierProvider);
      expect(prefs.themeMode, AppThemeMode.dark);
    });

    test('loadFromStorage restores persisted preferences', () async {
      final storage = _InMemoryStorage();
      final manager = ThemeManager(storage: storage);

      // Pre-seed storage with known preferences.
      await manager.savePreferences(
        const ThemePreferences(
          themeMode: AppThemeMode.highContrast,
          useDynamicColor: true,
        ),
      );

      final container = ProviderContainer(
        overrides: [themeManagerProvider.overrideWithValue(manager)],
      );
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).loadFromStorage();

      final prefs = container.read(themePreferencesNotifierProvider);
      expect(prefs.themeMode, AppThemeMode.highContrast);
      expect(prefs.useDynamicColor, true);
    });

    test('setThemeMode persists change to storage', () async {
      final storage = _InMemoryStorage();
      final manager = ThemeManager(storage: storage);

      final container = ProviderContainer(
        overrides: [themeManagerProvider.overrideWithValue(manager)],
      );
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).setThemeMode(AppThemeMode.dark);

      // Verify that the manager can reload the saved value.
      final loaded = await manager.loadPreferences();
      expect(loaded.themeMode, AppThemeMode.dark);
    });

    test('setSeedColor persists to storage', () async {
      final storage = _InMemoryStorage();
      final manager = ThemeManager(storage: storage);

      final container = ProviderContainer(
        overrides: [themeManagerProvider.overrideWithValue(manager)],
      );
      addTearDown(container.dispose);

      const seed = Color(0xFF6366F1);
      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(seed);

      final loaded = await manager.loadPreferences();
      expect(loaded.seedColor, seed);
    });

    test('resetTheme persists cleared values to storage', () async {
      final storage = _InMemoryStorage();
      final manager = ThemeManager(storage: storage);

      final container = ProviderContainer(
        overrides: [themeManagerProvider.overrideWithValue(manager)],
      );
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(const Color(0xFF6366F1));
      await container.read(themePreferencesNotifierProvider.notifier).resetTheme();

      final loaded = await manager.loadPreferences();
      expect(loaded.seedColor, isNull);
    });

    test('all AppThemeMode values can be set without error', () async {
      for (final mode in AppThemeMode.values) {
        final container = _makeContainer();
        addTearDown(container.dispose);

        await expectLater(
          container.read(themePreferencesNotifierProvider.notifier).setThemeMode(mode),
          completes,
        );

        final prefs = container.read(themePreferencesNotifierProvider);
        expect(prefs.themeMode, mode);
      }
    });
  });
}
