import 'package:egohygiene/shared/theme/models/theme_source.dart';
import 'package:egohygiene/shared/theme/personalization/theme_cache.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ThemeCache', () {
    late ThemeCache cache;

    // Minimal ColorSchemes for testing.
    const lightScheme = ColorScheme.light();
    const darkScheme = ColorScheme.dark();

    setUp(() {
      cache = ThemeCache();
    });

    test('starts with no schemes', () {
      expect(cache.hasSchemes, isFalse);
    });

    test('schemes returns defaults when empty', () {
      final schemes = cache.schemes;
      expect(schemes.lightScheme, isNull);
      expect(schemes.darkScheme, isNull);
      expect(schemes.source, ThemeSource.defaultTheme);
    });

    test('store makes hasSchemes true', () {
      cache.store(
        light: lightScheme,
        dark: darkScheme,
        source: ThemeSource.seed,
      );

      expect(cache.hasSchemes, isTrue);
    });

    test('store updates schemes and source', () {
      cache.store(
        light: lightScheme,
        dark: darkScheme,
        source: ThemeSource.image,
      );

      final schemes = cache.schemes;
      expect(schemes.lightScheme, lightScheme);
      expect(schemes.darkScheme, darkScheme);
      expect(schemes.source, ThemeSource.image);
    });

    test('clear resets all values', () {
      cache.store(
        light: lightScheme,
        dark: darkScheme,
        source: ThemeSource.seed,
      );

      cache.clear();

      expect(cache.hasSchemes, isFalse);
      expect(cache.schemes.lightScheme, isNull);
      expect(cache.schemes.darkScheme, isNull);
      expect(cache.schemes.source, ThemeSource.defaultTheme);
    });

    test('store overwrites previous values', () {
      cache.store(
        light: lightScheme,
        dark: darkScheme,
        source: ThemeSource.seed,
      );

      const updatedLight = ColorScheme.light(primary: Colors.red);
      cache.store(
        light: updatedLight,
        dark: darkScheme,
        source: ThemeSource.image,
      );

      expect(cache.schemes.lightScheme, updatedLight);
      expect(cache.schemes.source, ThemeSource.image);
    });
  });
}
