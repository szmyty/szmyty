import 'package:egohygiene/shared/assets/app_assets.dart';
import 'package:egohygiene/shared/assets/asset_category.dart';
import 'package:egohygiene/shared/assets/asset_ref.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppAssets.ambientStartupHero', () {
    test('is a RiveAsset', () {
      expect(AppAssets.ambientStartupHero, isA<RiveAsset>());
    });

    test('path points to the animations directory', () {
      expect(
        AppAssets.ambientStartupHero.path,
        'assets/animations/ambient_startup_hero.riv',
      );
    });

    test('category is animations', () {
      expect(AppAssets.ambientStartupHero.category, AssetCategory.animations);
    });

    test('has a non-null label', () {
      expect(AppAssets.ambientStartupHero.label, isNotNull);
      expect(AppAssets.ambientStartupHero.label, isNotEmpty);
    });
  });

  group('AppAssets category lists', () {
    test('animations list contains ambientStartupHero', () {
      expect(AppAssets.animations, contains(AppAssets.ambientStartupHero));
    });

    test('images list is defined', () {
      expect(AppAssets.images, isA<List<ImageAsset>>());
    });

    test('svgs list is defined', () {
      expect(AppAssets.svgs, isA<List<SvgAsset>>());
    });

    test('icons list is defined', () {
      expect(AppAssets.icons, isA<List<IconAsset>>());
    });

    test('illustrations list is defined', () {
      expect(AppAssets.illustrations, isA<List<IllustrationAsset>>());
    });

    test('branding list is defined', () {
      expect(AppAssets.branding, isA<List<BrandingAsset>>());
    });
  });

  group('AppAssets.all', () {
    test('includes all animation entries', () {
      for (final ref in AppAssets.animations) {
        expect(AppAssets.all, contains(ref));
      }
    });

    test('every entry has a non-empty path', () {
      for (final ref in AppAssets.all) {
        expect(ref.path, isNotEmpty);
      }
    });

    test('paths are unique', () {
      final paths = AppAssets.all.map((r) => r.path).toList();
      expect(paths.toSet(), hasLength(paths.length));
    });
  });

  group('AppAssets.forCategory', () {
    test('returns only animations for AssetCategory.animations', () {
      final result = AppAssets.forCategory(AssetCategory.animations);
      expect(result, isNotEmpty);
      expect(result.every((r) => r.category == AssetCategory.animations), isTrue);
    });

    test('returns empty list for categories with no registered assets', () {
      // Categories without entries yet should return an empty list.
      for (final category in [
        AssetCategory.images,
        AssetCategory.svgs,
        AssetCategory.icons,
        AssetCategory.illustrations,
        AssetCategory.branding,
      ]) {
        final result = AppAssets.forCategory(category);
        expect(result, isEmpty, reason: '${category.name} should be empty');
      }
    });
  });
}
