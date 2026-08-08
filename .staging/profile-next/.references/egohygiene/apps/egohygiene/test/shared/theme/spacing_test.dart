import 'package:egohygiene/shared/theme/spacing.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppSpacing', () {
    test('spacing values follow 8-point grid', () {
      expect(AppSpacing.xs, 4.0);
      expect(AppSpacing.sm, 8.0);
      expect(AppSpacing.md, 12.0);
      expect(AppSpacing.lg, 16.0);
      expect(AppSpacing.xl, 24.0);
      expect(AppSpacing.xxl, 32.0);
      expect(AppSpacing.xxxl, 48.0);
      expect(AppSpacing.huge, 64.0);
    });
  });

  group('AppRadius', () {
    test('radius values are defined', () {
      expect(AppRadius.sm, 4.0);
      expect(AppRadius.md, 8.0);
      expect(AppRadius.lg, 12.0);
      expect(AppRadius.xl, 16.0);
      expect(AppRadius.xxl, 24.0);
      expect(AppRadius.full, 9999.0);
    });
  });
}
