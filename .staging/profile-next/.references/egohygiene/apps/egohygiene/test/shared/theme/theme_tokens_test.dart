import 'package:egohygiene/shared/theme/theme_tokens.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('theme_tokens barrel export', () {
    test('AppColors is accessible', () {
      expect(AppColors.primary, isNotNull);
      expect(AppColors.reflection, isNotNull);
    });

    test('AppSpacing is accessible', () {
      expect(AppSpacing.md, isNotNull);
    });

    test('AppRadius is accessible', () {
      expect(AppRadius.lg, isNotNull);
    });

    test('AppElevation is accessible', () {
      expect(AppElevation.card, isNotNull);
    });

    test('AppShadows is accessible', () {
      expect(AppShadows.card, isNotNull);
    });

    test('AppDurations is accessible', () {
      expect(AppDurations.standard, isNotNull);
    });

    test('AppAccessibility is accessible', () {
      expect(AppAccessibility.minimumInteractiveSize, isNotNull);
    });

    test('AppCurves is accessible', () {
      expect(AppCurves.standard, isNotNull);
    });

    test('AppOpacity is accessible', () {
      expect(AppOpacity.medium, isNotNull);
    });
  });
}
