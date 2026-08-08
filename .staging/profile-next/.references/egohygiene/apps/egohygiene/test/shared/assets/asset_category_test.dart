import 'package:egohygiene/shared/assets/asset_category.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AssetCategory', () {
    test('contains all expected categories', () {
      expect(
        AssetCategory.values.map((c) => c.name),
        containsAll([
          'animations',
          'images',
          'svgs',
          'icons',
          'illustrations',
          'branding',
        ]),
      );
    });

    test('has exactly six categories', () {
      expect(AssetCategory.values, hasLength(6));
    });

    test('values are distinct', () {
      final names = AssetCategory.values.map((c) => c.name).toSet();
      expect(names, hasLength(AssetCategory.values.length));
    });
  });
}
