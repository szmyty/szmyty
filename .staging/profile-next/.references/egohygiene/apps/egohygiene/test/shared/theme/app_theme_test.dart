import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:egohygiene/shared/theme/theme_tokens.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppTheme', () {
    test('light theme is created successfully', () {
      final theme = AppTheme.light(useGoogleFonts: false);
      expect(theme, isA<ThemeData>());
      expect(theme.brightness, Brightness.light);
      expect(theme.useMaterial3, true);
    });

    test('dark theme is created successfully', () {
      final theme = AppTheme.dark(useGoogleFonts: false);
      expect(theme, isA<ThemeData>());
      expect(theme.brightness, Brightness.dark);
      expect(theme.useMaterial3, true);
    });

    test('amoled theme is created successfully', () {
      final theme = AppTheme.amoled(useGoogleFonts: false);
      expect(theme, isA<ThemeData>());
      expect(theme.brightness, Brightness.dark);
      expect(theme.useMaterial3, true);
      expect(theme.scaffoldBackgroundColor, Colors.black);
    });

    test('amoled theme has black surface', () {
      final theme = AppTheme.amoled(useGoogleFonts: false);
      expect(theme.colorScheme.surface, Colors.black);
    });

    test('highContrast theme is created successfully', () {
      final theme = AppTheme.highContrast(useGoogleFonts: false);
      expect(theme, isA<ThemeData>());
      expect(theme.brightness, Brightness.dark);
      expect(theme.useMaterial3, true);
      expect(theme.scaffoldBackgroundColor, Colors.black);
    });

    test('highContrast theme uses white-on-black for maximum contrast', () {
      final theme = AppTheme.highContrast(useGoogleFonts: false);
      expect(theme.colorScheme.surface, const Color(0xFF000000));
      expect(theme.colorScheme.onSurface, const Color(0xFFFFFFFF));
    });

    test('themes have consistent color schemes', () {
      final lightTheme = AppTheme.light(useGoogleFonts: false);
      final darkTheme = AppTheme.dark(useGoogleFonts: false);

      expect(lightTheme.colorScheme.primary, isNotNull);
      expect(darkTheme.colorScheme.primary, isNotNull);
    });

    test('light accepts dynamic color scheme', () {
      const dynamicScheme = ColorScheme.light(primary: Colors.teal);
      final theme = AppTheme.light(
        useGoogleFonts: false,
        dynamicColorScheme: dynamicScheme,
      );
      expect(theme.colorScheme.primary, Colors.teal);
    });

    test('dark accepts dynamic color scheme', () {
      const dynamicScheme = ColorScheme.dark(primary: Colors.teal);
      final theme = AppTheme.dark(
        useGoogleFonts: false,
        dynamicColorScheme: dynamicScheme,
      );
      expect(theme.colorScheme.primary, Colors.teal);
    });

    test('amoled accepts dynamic color scheme but keeps black surface', () {
      const dynamicScheme = ColorScheme.dark(primary: Colors.teal);
      final theme = AppTheme.amoled(
        useGoogleFonts: false,
        dynamicColorScheme: dynamicScheme,
      );
      expect(theme.colorScheme.surface, Colors.black);
    });

    test('themes use padded touch targets', () {
      final theme = AppTheme.light(useGoogleFonts: false);
      expect(theme.materialTapTargetSize, MaterialTapTargetSize.padded);
      expect(
        theme.filledButtonTheme.style?.minimumSize?.resolve({}),
        AppAccessibility.minimumInteractiveSize,
      );
      expect(
        theme.iconButtonTheme.style?.minimumSize?.resolve({}),
        AppAccessibility.minimumInteractiveSize,
      );
    });

    test('themes use reduced-motion-aware page transitions', () {
      final theme = AppTheme.light(useGoogleFonts: false);
      expect(
        theme.pageTransitionsTheme.builders[TargetPlatform.android],
        isA<ReducedMotionPageTransitionsBuilder>(),
      );
      expect(
        theme.pageTransitionsTheme.builders[TargetPlatform.iOS],
        isA<ReducedMotionPageTransitionsBuilder>(),
      );
    });

    test('light theme applies calmer shared surface styling', () {
      final theme = AppTheme.light(useGoogleFonts: false);
      final cardShape = theme.cardTheme.shape! as RoundedRectangleBorder;

      expect(theme.scaffoldBackgroundColor, AppColors.backgroundLight);
      expect(theme.cardTheme.margin, EdgeInsets.zero);
      expect(cardShape.borderRadius, BorderRadius.circular(AppRadius.xl));
      expect(theme.navigationBarTheme.height, 72);
      expect(theme.dividerTheme.space, AppSpacing.xl);
    });

    test('shared controls use softened geometry and accessible sizing', () {
      final theme = AppTheme.light(useGoogleFonts: false);
      final filledStyle = theme.filledButtonTheme.style!;
      final outlinedStyle = theme.outlinedButtonTheme.style!;
      final inputBorder = theme.inputDecorationTheme.border! as OutlineInputBorder;

      expect(
        filledStyle.minimumSize?.resolve({}),
        AppAccessibility.minimumInteractiveSize,
      );
      expect(
        (filledStyle.shape!.resolve({})! as RoundedRectangleBorder).borderRadius,
        BorderRadius.circular(AppRadius.full),
      );
      expect(
        (outlinedStyle.shape!.resolve({})! as RoundedRectangleBorder).borderRadius,
        BorderRadius.circular(AppRadius.full),
      );
      expect(inputBorder.borderRadius, BorderRadius.circular(AppRadius.xl));
    });

    test('typography increases breathing room for readability', () {
      final theme = AppTheme.light(useGoogleFonts: false);

      expect(theme.textTheme.bodyLarge?.height, 1.5);
      expect(theme.textTheme.bodyMedium?.height, 1.5);
      expect(theme.textTheme.titleLarge?.height, 1.28);
      expect(theme.textTheme.titleLarge?.fontWeight, FontWeight.w600);
    });
  });
}
