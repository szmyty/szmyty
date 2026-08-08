import 'package:egohygiene/shared/animation/animation_engine.dart';
import 'package:egohygiene/shared/assets/assets.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rive/rive.dart' as rive;

const _fallbackText = 'fallback';

void main() {
  const scene = RiveSceneAsset(asset: AppAssets.ambientStartupHero);

  testWidgets('renders fallback immediately when animation is disabled', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.dark(useGoogleFonts: false),
        home: Scaffold(
          body: RiveScene(
            scene: scene,
            animate: false,
            fallbackBuilder: (_, _) => const Text(_fallbackText),
          ),
        ),
      ),
    );

    expect(find.text(_fallbackText), findsOneWidget);
    expect(find.byType(rive.RiveWidgetBuilder), findsNothing);
  });

  testWidgets(
    'renders fallback widget while the Rive scene loads in flutter_test',
    (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark(useGoogleFonts: false),
          home: Scaffold(
            body: RiveScene(
              scene: scene,
              animate: true,
              fallbackBuilder: (_, _) => const Text(_fallbackText),
            ),
          ),
        ),
      );

      expect(tester.takeException(), isNull);
      expect(find.text(_fallbackText), findsOneWidget);
      expect(find.byType(rive.RiveWidgetBuilder), findsOneWidget);
    },
  );
}
