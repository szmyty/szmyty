import 'package:egohygiene/shared/theme/app_theme_mode.dart';
import 'package:egohygiene/shared/theme/theme_preferences.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ThemePreferences', () {
    test('defaults to system mode with dynamic color disabled', () {
      const prefs = ThemePreferences();
      expect(prefs.themeMode, AppThemeMode.system);
      expect(prefs.useDynamicColor, false);
      expect(prefs.seedColor, isNull);
      expect(prefs.imageReference, isNull);
    });

    test('copyWith returns updated copy', () {
      const prefs = ThemePreferences();

      final updated = prefs.copyWith(themeMode: AppThemeMode.amoled);
      expect(updated.themeMode, AppThemeMode.amoled);
      expect(updated.useDynamicColor, false);

      final withDynamic = prefs.copyWith(useDynamicColor: true);
      expect(withDynamic.themeMode, AppThemeMode.system);
      expect(withDynamic.useDynamicColor, true);
    });

    test('copyWith sets seedColor', () {
      const prefs = ThemePreferences();
      const seed = Color(0xFF6366F1);
      final updated = prefs.copyWith(seedColor: seed);

      expect(updated.seedColor, seed);
      expect(updated.imageReference, isNull);
    });

    test('copyWith clearSeedColor removes seedColor', () {
      const seed = Color(0xFF6366F1);
      const prefs = ThemePreferences(seedColor: seed);

      final cleared = prefs.copyWith(clearSeedColor: true);
      expect(cleared.seedColor, isNull);
    });

    test('copyWith sets imageReference', () {
      const prefs = ThemePreferences();
      final updated = prefs.copyWith(imageReference: 'https://example.com/img.jpg');

      expect(updated.imageReference, 'https://example.com/img.jpg');
    });

    test('copyWith clearImageReference removes imageReference', () {
      const prefs = ThemePreferences(imageReference: 'https://example.com/img.jpg');

      final cleared = prefs.copyWith(clearImageReference: true);
      expect(cleared.imageReference, isNull);
    });

    group('JSON serialisation', () {
      test('roundtrips through toJson / fromJson', () {
        const prefs = ThemePreferences(
          themeMode: AppThemeMode.amoled,
          useDynamicColor: true,
        );

        final json = prefs.toJson();
        final restored = ThemePreferences.fromJson(json);

        expect(restored, prefs);
      });

      test('fromJson falls back to defaults for unknown themeMode', () {
        final prefs = ThemePreferences.fromJson({'themeMode': 'unknownMode'});
        expect(prefs.themeMode, AppThemeMode.system);
      });

      test('fromJson falls back to defaults for missing fields', () {
        final prefs = ThemePreferences.fromJson({});
        expect(prefs.themeMode, AppThemeMode.system);
        expect(prefs.useDynamicColor, false);
        expect(prefs.seedColor, isNull);
        expect(prefs.imageReference, isNull);
      });

      test('roundtrips seedColor through JSON', () {
        const seed = Color(0xFF6366F1);
        const prefs = ThemePreferences(seedColor: seed);

        final json = prefs.toJson();
        expect(json.containsKey('seedColor'), isTrue);

        final restored = ThemePreferences.fromJson(json);
        expect(restored.seedColor, seed);
      });

      test('roundtrips imageReference through JSON', () {
        const ref = 'https://example.com/wallpaper.jpg';
        const prefs = ThemePreferences(imageReference: ref);

        final json = prefs.toJson();
        expect(json['imageReference'], ref);

        final restored = ThemePreferences.fromJson(json);
        expect(restored.imageReference, ref);
      });

      test('toJson omits null seedColor', () {
        const prefs = ThemePreferences();
        final json = prefs.toJson();
        expect(json.containsKey('seedColor'), isFalse);
      });

      test('toJson omits null imageReference', () {
        const prefs = ThemePreferences();
        final json = prefs.toJson();
        expect(json.containsKey('imageReference'), isFalse);
      });

      test('fromJson ignores non-int seedColor gracefully', () {
        final prefs = ThemePreferences.fromJson({'seedColor': 'not-an-int'});
        expect(prefs.seedColor, isNull);
      });

      for (final mode in AppThemeMode.values) {
        test('serialises AppThemeMode.${mode.name}', () {
          final prefs = ThemePreferences(themeMode: mode);
          final json = prefs.toJson();
          expect(json['themeMode'], mode.name);
          final restored = ThemePreferences.fromJson(json);
          expect(restored.themeMode, mode);
        });
      }
    });

    group('equality', () {
      test('equal when all fields match', () {
        const a = ThemePreferences(
          themeMode: AppThemeMode.dark,
          useDynamicColor: true,
        );
        const b = ThemePreferences(
          themeMode: AppThemeMode.dark,
          useDynamicColor: true,
        );
        expect(a, b);
        expect(a.hashCode, b.hashCode);
      });

      test('not equal when themeMode differs', () {
        const a = ThemePreferences(themeMode: AppThemeMode.light);
        const b = ThemePreferences(themeMode: AppThemeMode.dark);
        expect(a, isNot(b));
      });

      test('not equal when useDynamicColor differs', () {
        const a = ThemePreferences();
        const b = ThemePreferences(useDynamicColor: true);
        expect(a, isNot(b));
      });

      test('not equal when seedColor differs', () {
        const a = ThemePreferences(seedColor: Color(0xFF6366F1));
        const b = ThemePreferences(seedColor: Color(0xFFFF5722));
        expect(a, isNot(b));
      });

      test('not equal when imageReference differs', () {
        const a = ThemePreferences(imageReference: 'https://a.com/img.jpg');
        const b = ThemePreferences(imageReference: 'https://b.com/img.jpg');
        expect(a, isNot(b));
      });

      test('equal when seedColor and imageReference both null', () {
        const a = ThemePreferences();
        const b = ThemePreferences();
        expect(a, b);
      });
    });
  });

  group('AppThemeMode', () {
    test('all values convert to FlutterThemeMode without error', () {
      for (final mode in AppThemeMode.values) {
        expect(mode.toFlutterThemeMode, returnsNormally);
      }
    });

    test('system maps to ThemeMode.system', () {
      expect(AppThemeMode.system.toFlutterThemeMode(), ThemeMode.system);
    });

    test('light maps to ThemeMode.light', () {
      expect(AppThemeMode.light.toFlutterThemeMode(), ThemeMode.light);
    });

    test('dark maps to ThemeMode.dark', () {
      expect(AppThemeMode.dark.toFlutterThemeMode(), ThemeMode.dark);
    });

    test('amoled maps to ThemeMode.dark', () {
      expect(AppThemeMode.amoled.toFlutterThemeMode(), ThemeMode.dark);
    });

    test('highContrast maps to ThemeMode.dark', () {
      expect(AppThemeMode.highContrast.toFlutterThemeMode(), ThemeMode.dark);
    });
  });
}
