import 'package:egohygiene/shared/theme/shadows.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppShadows', () {
    test('none is an empty list', () {
      expect(AppShadows.none, isEmpty);
    });

    test('all non-empty presets contain at least one BoxShadow', () {
      expect(AppShadows.xs, isNotEmpty);
      expect(AppShadows.sm, isNotEmpty);
      expect(AppShadows.card, isNotEmpty);
      expect(AppShadows.cardElevated, isNotEmpty);
      expect(AppShadows.appBar, isNotEmpty);
      expect(AppShadows.bottomSheet, isNotEmpty);
      expect(AppShadows.dialog, isNotEmpty);
    });

    test('card shadow has two layers for depth', () {
      expect(AppShadows.card.length, 2);
    });

    test('cardElevated shadow has two layers for depth', () {
      expect(AppShadows.cardElevated.length, 2);
    });

    test('shadow offsets use positive Y for downward shadows', () {
      for (final shadow in AppShadows.card) {
        expect(shadow.offset.dy, greaterThanOrEqualTo(0));
      }
    });

    test('bottom sheet shadow uses negative Y for upward shadow', () {
      for (final shadow in AppShadows.bottomSheet) {
        expect(shadow.offset.dy, lessThanOrEqualTo(0));
      }
    });

    test('shadow colors are semi-transparent', () {
      for (final preset in [
        AppShadows.xs,
        AppShadows.sm,
        AppShadows.card,
        AppShadows.cardElevated,
        AppShadows.appBar,
        AppShadows.bottomSheet,
        AppShadows.dialog,
      ]) {
        for (final shadow in preset) {
          expect(
            shadow.color.a,
            lessThan(1.0),
            reason: 'Shadow color should be semi-transparent',
          );
        }
      }
    });
  });
}
