import 'package:egohygiene/shared/theme/elevation.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppElevation', () {
    test('none is 0', () {
      expect(AppElevation.none, 0.0);
    });

    test('elevation values are ordered ascending', () {
      expect(AppElevation.none, lessThan(AppElevation.xs));
      expect(AppElevation.xs, lessThan(AppElevation.sm));
      expect(AppElevation.sm, lessThan(AppElevation.card));
      expect(AppElevation.card, lessThan(AppElevation.cardHovered));
      expect(AppElevation.cardHovered, lessThan(AppElevation.appBar));
      expect(AppElevation.appBar, lessThan(AppElevation.fab));
      expect(AppElevation.fab, lessThan(AppElevation.bottomSheet));
      expect(AppElevation.bottomSheet, lessThan(AppElevation.dialog));
      expect(AppElevation.dialog, lessThan(AppElevation.drawer));
    });

    test('specific elevation values match spec', () {
      expect(AppElevation.xs, 1.0);
      expect(AppElevation.sm, 2.0);
      expect(AppElevation.card, 4.0);
      expect(AppElevation.cardHovered, 6.0);
      expect(AppElevation.appBar, 8.0);
      expect(AppElevation.fab, 12.0);
      expect(AppElevation.bottomSheet, 16.0);
      expect(AppElevation.dialog, 24.0);
      expect(AppElevation.drawer, 32.0);
    });
  });
}
