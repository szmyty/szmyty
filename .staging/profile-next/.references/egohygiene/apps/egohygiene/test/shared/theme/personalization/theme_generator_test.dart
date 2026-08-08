import 'package:egohygiene/shared/theme/personalization/theme_generator.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ThemeGenerator', () {
    late ThemeGenerator generator;

    setUp(() {
      generator = const ThemeGenerator();
    });

    test('generateLight returns a light ColorScheme', () {
      const seed = Color(0xFF6366F1);
      final scheme = generator.generateLight(seed);

      expect(scheme.brightness, Brightness.light);
    });

    test('generateDark returns a dark ColorScheme', () {
      const seed = Color(0xFF6366F1);
      final scheme = generator.generateDark(seed);

      expect(scheme.brightness, Brightness.dark);
    });

    test('generatePair returns matching light and dark schemes', () {
      const seed = Color(0xFF6366F1);
      final (light, dark) = generator.generatePair(seed);

      expect(light.brightness, Brightness.light);
      expect(dark.brightness, Brightness.dark);
    });

    test('generateLight and generateDark produce different schemes', () {
      const seed = Color(0xFF6366F1);
      final light = generator.generateLight(seed);
      final dark = generator.generateDark(seed);

      // Light and dark must differ in at least one meaningful colour.
      expect(light.surface, isNot(dark.surface));
    });

    test('different seed colors produce different primary colors', () {
      final schemeA = generator.generateLight(const Color(0xFF6366F1));
      final schemeB = generator.generateLight(const Color(0xFFFF5722));

      expect(schemeA.primary, isNot(schemeB.primary));
    });

    test('generatePair is consistent with separate generate calls', () {
      const seed = Color(0xFF6366F1);
      final (pairLight, pairDark) = generator.generatePair(seed);
      final singleLight = generator.generateLight(seed);
      final singleDark = generator.generateDark(seed);

      expect(pairLight.primary, singleLight.primary);
      expect(pairDark.primary, singleDark.primary);
    });
  });
}
