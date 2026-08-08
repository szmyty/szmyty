import 'package:egohygiene/shared/providers/theme_providers.dart';
import 'package:egohygiene/shared/services/storage_service.dart';
import 'package:egohygiene/shared/theme/app_theme_mode.dart';
import 'package:egohygiene/shared/theme/models/theme_source.dart';
import 'package:egohygiene/shared/theme/personalization/providers/theme_personalization_providers.dart';
import 'package:egohygiene/shared/theme/theme_manager.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

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

ProviderContainer _makeContainer() {
  final storage = _InMemoryStorage();
  return ProviderContainer(
    overrides: [
      themeManagerProvider.overrideWithValue(ThemeManager(storage: storage)),
    ],
  );
}

void main() {
  group('themeSeedSchemesProvider', () {
    test('returns null when no seed color is set', () {
      final container = _makeContainer();
      addTearDown(container.dispose);

      final schemes = container.read(themeSeedSchemesProvider);
      expect(schemes, isNull);
    });

    test('returns non-null schemes when seed color is set', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(const Color(0xFF6366F1));

      final schemes = container.read(themeSeedSchemesProvider);
      expect(schemes, isNotNull);
      expect(schemes!.light.brightness, Brightness.light);
      expect(schemes.dark.brightness, Brightness.dark);
    });

    test('updates when seed color changes', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(const Color(0xFF6366F1));
      final first = container.read(themeSeedSchemesProvider);

      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(const Color(0xFFFF5722));
      final second = container.read(themeSeedSchemesProvider);

      expect(first!.light.primary, isNot(second!.light.primary));
    });

    test('returns null after resetTheme clears seed color', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(const Color(0xFF6366F1));
      await container.read(themePreferencesNotifierProvider.notifier).resetTheme();

      final schemes = container.read(themeSeedSchemesProvider);
      expect(schemes, isNull);
    });
  });

  group('themeResolvedSchemesProvider', () {
    test('defaults to defaultTheme source with null schemes', () {
      final container = _makeContainer();
      addTearDown(container.dispose);

      final resolved = container.read(themeResolvedSchemesProvider);
      expect(resolved.source, ThemeSource.defaultTheme);
      expect(resolved.lightScheme, isNull);
      expect(resolved.darkScheme, isNull);
    });

    test('returns seed source when seed color is set', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(const Color(0xFF6366F1));

      final resolved = container.read(themeResolvedSchemesProvider);
      expect(resolved.source, ThemeSource.seed);
      expect(resolved.lightScheme, isNotNull);
      expect(resolved.darkScheme, isNotNull);
    });

    test('image schemes take priority over seed schemes', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      // Set seed color
      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(const Color(0xFF6366F1));

      // Also set image schemes
      const imageLight = ColorScheme.light(primary: Colors.red);
      const imageDark = ColorScheme.dark(primary: Colors.red);
      container.read(themeImageSchemesNotifierProvider.notifier).setCachedSchemes(imageLight, imageDark);

      final resolved = container.read(themeResolvedSchemesProvider);
      expect(resolved.source, ThemeSource.image);
      expect(resolved.lightScheme, imageLight);
      expect(resolved.darkScheme, imageDark);
    });

    test('falls back to seed after image is cleared', () async {
      final container = _makeContainer();
      addTearDown(container.dispose);

      // Set seed color
      await container.read(themePreferencesNotifierProvider.notifier).setSeedColor(const Color(0xFF6366F1));

      // Set image schemes then clear
      container
          .read(themeImageSchemesNotifierProvider.notifier)
          .setCachedSchemes(
            const ColorScheme.light(primary: Colors.red),
            const ColorScheme.dark(primary: Colors.red),
          );
      container.read(themeImageSchemesNotifierProvider.notifier).clear();

      final resolved = container.read(themeResolvedSchemesProvider);
      expect(resolved.source, ThemeSource.seed);
    });

    test('resolves with all AppThemeModes', () async {
      for (final mode in AppThemeMode.values) {
        final container = _makeContainer();
        addTearDown(container.dispose);

        await container.read(themePreferencesNotifierProvider.notifier).setThemeMode(mode);

        final resolved = container.read(themeResolvedSchemesProvider);
        // No custom schemes set, so should be defaults
        expect(resolved.source, ThemeSource.defaultTheme);
      }
    });
  });

  group('ThemeImageSchemesNotifier', () {
    test('initial state is null', () {
      final container = _makeContainer();
      addTearDown(container.dispose);

      final schemes = container.read(themeImageSchemesNotifierProvider);
      expect(schemes, isNull);
    });

    test('clear resets state to null', () {
      final container = _makeContainer();
      addTearDown(container.dispose);

      container
          .read(themeImageSchemesNotifierProvider.notifier)
          .setCachedSchemes(const ColorScheme.light(), const ColorScheme.dark());
      container.read(themeImageSchemesNotifierProvider.notifier).clear();

      expect(container.read(themeImageSchemesNotifierProvider), isNull);
    });
  });
}
