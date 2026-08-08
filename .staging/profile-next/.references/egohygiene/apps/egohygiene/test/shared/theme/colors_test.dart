import 'package:egohygiene/shared/theme/colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppColors — brand palette', () {
    test('primary colors are defined', () {
      expect(AppColors.primary, const Color(0xFF6366F1));
      expect(AppColors.primaryLight, const Color(0xFF818CF8));
      expect(AppColors.primaryDark, const Color(0xFF4F46E5));
    });

    test('secondary colors are defined', () {
      expect(AppColors.secondary, const Color(0xFF8B5CF6));
      expect(AppColors.secondaryLight, const Color(0xFFA78BFA));
      expect(AppColors.secondaryDark, const Color(0xFF7C3AED));
    });

    test('neutral palette is defined', () {
      expect(AppColors.neutral50, const Color(0xFFFAFAFA));
      expect(AppColors.neutral100, const Color(0xFFF5F5F5));
      expect(AppColors.neutral200, const Color(0xFFE5E5E5));
      expect(AppColors.neutral300, const Color(0xFFD4D4D4));
      expect(AppColors.neutral400, const Color(0xFFA3A3A3));
      expect(AppColors.neutral500, const Color(0xFF737373));
      expect(AppColors.neutral600, const Color(0xFF525252));
      expect(AppColors.neutral700, const Color(0xFF404040));
      expect(AppColors.neutral800, const Color(0xFF262626));
      expect(AppColors.neutral900, const Color(0xFF171717));
    });

    test('status / feedback colors are defined', () {
      expect(AppColors.success, const Color(0xFF10B981));
      expect(AppColors.warning, const Color(0xFFF59E0B));
      expect(AppColors.error, const Color(0xFFEF4444));
      expect(AppColors.info, const Color(0xFF3B82F6));
    });

    test('surface colors are defined', () {
      expect(AppColors.surfaceLight, const Color(0xFFFFFFFF));
      expect(AppColors.backgroundLight, const Color(0xFFFAFAFA));
      expect(AppColors.surfaceDark, const Color(0xFF1E1E1E));
      expect(AppColors.backgroundDark, const Color(0xFF121212));
    });
  });

  group('AppColors — Ego Hygiene semantic tokens', () {
    test('positive maps to success', () {
      expect(AppColors.positive, AppColors.success);
    });

    test('caution maps to warning', () {
      expect(AppColors.caution, AppColors.warning);
    });

    test('critical maps to error', () {
      expect(AppColors.critical, AppColors.error);
    });

    test('accent maps to primary', () {
      expect(AppColors.accent, AppColors.primary);
    });

    test('reflection is defined', () {
      expect(AppColors.reflection, const Color(0xFF6366F1));
    });

    test('insight is defined', () {
      expect(AppColors.insight, const Color(0xFF14B8A6));
    });

    test('journey is defined', () {
      expect(AppColors.journey, const Color(0xFFF59E0B));
    });
  });
}
