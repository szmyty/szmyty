import 'package:egohygiene/shared/assets/asset_category.dart';
import 'package:egohygiene/shared/assets/asset_ref.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AssetRef equality', () {
    test('two refs with the same path are equal', () {
      const a = RiveAsset(path: 'assets/animations/foo.riv');
      const b = RiveAsset(path: 'assets/animations/foo.riv');
      expect(a, equals(b));
    });

    test('two refs with different paths are not equal', () {
      const a = RiveAsset(path: 'assets/animations/foo.riv');
      const b = RiveAsset(path: 'assets/animations/bar.riv');
      expect(a, isNot(equals(b)));
    });

    test('hashCode matches for equal refs', () {
      const a = RiveAsset(path: 'assets/animations/foo.riv');
      const b = RiveAsset(path: 'assets/animations/foo.riv');
      expect(a.hashCode, equals(b.hashCode));
    });

    test('can be used as a map key', () {
      const ref = RiveAsset(path: 'assets/animations/foo.riv');
      final map = {ref: 'value'};
      expect(map[const RiveAsset(path: 'assets/animations/foo.riv')], 'value');
    });
  });

  group('AnimationAsset', () {
    const ref = RiveAsset(
      path: 'assets/animations/startup.riv',
      label: 'Startup illustration',
    );

    test('category is animations', () {
      expect(ref.category, AssetCategory.animations);
    });

    test('path is preserved', () {
      expect(ref.path, 'assets/animations/startup.riv');
    });

    test('label is preserved', () {
      expect(ref.label, 'Startup illustration');
    });

    test('label defaults to null', () {
      const noLabel = RiveAsset(path: 'assets/animations/foo.riv');
      expect(noLabel.label, isNull);
    });

    test('toString contains path and category', () {
      expect(ref.toString(), contains('assets/animations/startup.riv'));
      expect(ref.toString(), contains('animations'));
    });
  });

  group('LottieAsset', () {
    const ref = LottieAsset(path: 'assets/animations/legacy.json');

    test('still registers as an animation asset', () {
      expect(ref.category, AssetCategory.animations);
    });
  });

  group('ImageAsset', () {
    const ref = ImageAsset(path: 'assets/images/hero.png');

    test('category is images', () {
      expect(ref.category, AssetCategory.images);
    });
  });

  group('SvgAsset', () {
    const ref = SvgAsset(path: 'assets/svgs/logo.svg');

    test('category is svgs', () {
      expect(ref.category, AssetCategory.svgs);
    });
  });

  group('IconAsset', () {
    const ref = IconAsset(path: 'assets/icons/checkmark.svg');

    test('category is icons', () {
      expect(ref.category, AssetCategory.icons);
    });
  });

  group('IllustrationAsset', () {
    const ref = IllustrationAsset(path: 'assets/illustrations/empty_state.svg');

    test('category is illustrations', () {
      expect(ref.category, AssetCategory.illustrations);
    });
  });

  group('BrandingAsset', () {
    const ref = BrandingAsset(path: 'assets/branding/logo.svg');

    test('category is branding', () {
      expect(ref.category, AssetCategory.branding);
    });
  });
}
