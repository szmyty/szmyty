import 'package:egohygiene/shared/assets/assets.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('assets barrel export', () {
    test('AppAssets is accessible', () {
      expect(AppAssets.ambientStartupHero, isNotNull);
    });

    test('AssetCategory is accessible', () {
      expect(AssetCategory.animations, isNotNull);
      expect(AssetCategory.values, isNotEmpty);
    });

    test('RiveAsset is accessible', () {
      const ref = RiveAsset(path: 'assets/animations/test.riv');
      expect(ref.path, isNotEmpty);
    });

    test('LottieAsset is still accessible', () {
      const ref = LottieAsset(path: 'assets/animations/test.json');
      expect(ref.path, isNotEmpty);
    });

    test('ImageAsset is accessible', () {
      const ref = ImageAsset(path: 'assets/images/test.png');
      expect(ref.path, isNotEmpty);
    });

    test('SvgAsset is accessible', () {
      const ref = SvgAsset(path: 'assets/svgs/test.svg');
      expect(ref.path, isNotEmpty);
    });

    test('IconAsset is accessible', () {
      const ref = IconAsset(path: 'assets/icons/test.svg');
      expect(ref.path, isNotEmpty);
    });

    test('IllustrationAsset is accessible', () {
      const ref = IllustrationAsset(path: 'assets/illustrations/test.svg');
      expect(ref.path, isNotEmpty);
    });

    test('BrandingAsset is accessible', () {
      const ref = BrandingAsset(path: 'assets/branding/test.svg');
      expect(ref.path, isNotEmpty);
    });

    test('FlutterAssetLoader is accessible', () {
      const loader = FlutterAssetLoader();
      expect(loader, isA<AssetLoader>());
    });
  });
}
