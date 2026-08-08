import 'package:egohygiene/shared/theme/app_theme_mode.dart';
import 'package:egohygiene/shared/theme/models/theme_source.dart';
import 'package:egohygiene/shared/theme/personalization/theme_cache.dart';
import 'package:egohygiene/shared/theme/personalization/theme_generator.dart';
import 'package:egohygiene/shared/theme/personalization/theme_personalization_manager.dart';
import 'package:egohygiene/shared/theme/theme_preferences.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ThemePersonalizationManager', () {
    late ThemePersonalizationManager manager;

    setUp(() {
      manager = ThemePersonalizationManager(
        generator: const ThemeGenerator(),
        cache: ThemeCache(),
      );
    });

    group('resolveSchemes', () {
      test('returns defaults when no seed or image cache', () {
        const prefs = ThemePreferences();
        final resolved = manager.resolveSchemes(prefs);

        expect(resolved.source, ThemeSource.defaultTheme);
        expect(resolved.lightScheme, isNull);
        expect(resolved.darkScheme, isNull);
      });

      test('returns seed schemes when seedColor is set and no image cache', () {
        const seed = Color(0xFF6366F1);
        const prefs = ThemePreferences(seedColor: seed);
        final resolved = manager.resolveSchemes(prefs);

        expect(resolved.source, ThemeSource.seed);
        expect(resolved.lightScheme, isNotNull);
        expect(resolved.darkScheme, isNotNull);
      });

      test('returns image cache over seed when cache is populated', () {
        const seed = Color(0xFF6366F1);
        const prefs = ThemePreferences(seedColor: seed);

        // Pre-populate image cache
        const imageLight = ColorScheme.light(primary: Colors.red);
        const imageDark = ColorScheme.dark(primary: Colors.red);
        manager.applySeedColor(seed);

        // Overwrite with image schemes manually via a new manager that has
        // an image cache already set via the cache field.
        final cacheWithImage = ThemeCache()
          ..store(
            light: imageLight,
            dark: imageDark,
            source: ThemeSource.image,
          );
        final managerWithImage = ThemePersonalizationManager(
          generator: const ThemeGenerator(),
          cache: cacheWithImage,
        );

        final resolved = managerWithImage.resolveSchemes(prefs);
        expect(resolved.source, ThemeSource.image);
        expect(resolved.lightScheme, imageLight);
        expect(resolved.darkScheme, imageDark);
      });
    });

    group('applySeedColor', () {
      test('returns non-null schemes from seed color', () {
        const seed = Color(0xFF6366F1);
        final resolved = manager.applySeedColor(seed);

        expect(resolved.source, ThemeSource.seed);
        expect(resolved.lightScheme, isNotNull);
        expect(resolved.darkScheme, isNotNull);
      });

      test('subsequent resolveSchemes returns cached seed schemes', () {
        const seed = Color(0xFF6366F1);
        manager.applySeedColor(seed);

        // Without seedColor in prefs – should still return cached schemes
        const prefs = ThemePreferences();
        final resolved = manager.resolveSchemes(prefs);

        expect(resolved.source, ThemeSource.seed);
        expect(resolved.lightScheme, isNotNull);
      });

      test('clears any previous image cache when seed is applied', () {
        // First set an image cache
        const imageLight = ColorScheme.light(primary: Colors.blue);
        const imageDark = ColorScheme.dark(primary: Colors.blue);
        final cacheWithImage = ThemeCache()
          ..store(
            light: imageLight,
            dark: imageDark,
            source: ThemeSource.image,
          );
        final m = ThemePersonalizationManager(
          generator: const ThemeGenerator(),
          cache: cacheWithImage,
        );

        // Now apply a seed color – this should clear the image cache
        m.applySeedColor(const Color(0xFF6366F1));

        const prefs = ThemePreferences();
        final resolved = m.resolveSchemes(prefs);

        // Source should now be seed, not image
        expect(resolved.source, ThemeSource.seed);
      });
    });

    group('reset', () {
      test('clears cache so defaults are returned', () {
        manager.applySeedColor(const Color(0xFF6366F1));
        manager.reset();

        const prefs = ThemePreferences();
        final resolved = manager.resolveSchemes(prefs);

        expect(resolved.source, ThemeSource.defaultTheme);
        expect(resolved.lightScheme, isNull);
        expect(resolved.darkScheme, isNull);
      });
    });

    group('theme mode compatibility', () {
      test('resolveSchemes returns seed schemes for all AppThemeModes', () {
        const seed = Color(0xFF6366F1);

        for (final mode in AppThemeMode.values) {
          // Create a fresh manager per mode to avoid cache state bleed
          final m = ThemePersonalizationManager(
            generator: const ThemeGenerator(),
            cache: ThemeCache(),
          );
          final prefs = ThemePreferences(
            themeMode: mode,
            seedColor: seed,
          );
          final resolved = m.resolveSchemes(prefs);
          expect(
            resolved.source,
            ThemeSource.seed,
            reason: 'seed color is set so source must be seed for $mode',
          );
          expect(resolved.lightScheme, isNotNull);
          expect(resolved.darkScheme, isNotNull);
        }
      });
    });
  });
}
