import 'package:egohygiene/shared/theme/opacity.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppOpacity', () {
    test('boundary values are correct', () {
      expect(AppOpacity.full, 1.0);
      expect(AppOpacity.none, 0.0);
    });

    test('opacity values are ordered descending', () {
      expect(AppOpacity.full, greaterThan(AppOpacity.high));
      expect(AppOpacity.high, greaterThan(AppOpacity.medium));
      expect(AppOpacity.medium, greaterThan(AppOpacity.hint));
      expect(AppOpacity.hint, greaterThan(AppOpacity.muted));
      expect(AppOpacity.muted, greaterThan(AppOpacity.disabled));
      expect(AppOpacity.disabled, greaterThan(AppOpacity.overlay));
      expect(AppOpacity.overlay, greaterThan(AppOpacity.subtle));
      expect(AppOpacity.subtle, greaterThan(AppOpacity.none));
    });

    test('all values are in the range [0, 1]', () {
      for (final value in [
        AppOpacity.full,
        AppOpacity.high,
        AppOpacity.medium,
        AppOpacity.hint,
        AppOpacity.muted,
        AppOpacity.disabled,
        AppOpacity.overlay,
        AppOpacity.subtle,
        AppOpacity.none,
      ]) {
        expect(value, inInclusiveRange(0.0, 1.0));
      }
    });

    test('specific values match spec', () {
      expect(AppOpacity.high, 0.87);
      expect(AppOpacity.medium, 0.70);
      expect(AppOpacity.hint, 0.54);
      expect(AppOpacity.muted, 0.50);
      expect(AppOpacity.disabled, 0.38);
      expect(AppOpacity.overlay, 0.12);
      expect(AppOpacity.subtle, 0.08);
    });
  });
}
