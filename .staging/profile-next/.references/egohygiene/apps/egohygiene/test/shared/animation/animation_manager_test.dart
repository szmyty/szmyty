import 'package:egohygiene/shared/animation/animation_engine.dart';
import 'package:egohygiene/shared/assets/assets.dart';
import 'package:egohygiene/shared/providers/animation_providers.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:egohygiene/shared/theme/motion.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rive/rive.dart' as rive;

void main() {
  group('AnimationRegistry', () {
    test('registers the shared ambient hero for supported surfaces', () {
      final splashEntry = AnimationRegistry.defaults.primaryFor(
        AnimationSurface.splash,
      );

      expect(splashEntry, isNotNull);
      expect(splashEntry?.id, AnimationRegistry.ambientHeroId);
      expect(
        splashEntry?.surfaces,
        containsAll([
          AnimationSurface.splash,
          AnimationSurface.onboarding,
          AnimationSurface.emptyState,
          AnimationSurface.loadingState,
          AnimationSurface.celebration,
          AnimationSurface.ambientBackground,
          AnimationSurface.websiteHero,
        ]),
      );
    });
  });

  testWidgets('AnimationManager resolves reduced motion and themed tokens', (
    tester,
  ) async {
    const manager = AnimationManager(registry: AnimationRegistry.defaults);
    final darkTheme = AppTheme.dark(useGoogleFonts: false);
    late AnimationPresentation presentation;

    await tester.pumpWidget(
      MediaQuery(
        data: const MediaQueryData(
          disableAnimations: true,
          accessibleNavigation: true,
        ),
        child: MaterialApp(
          theme: darkTheme,
          home: Builder(
            builder: (context) {
              presentation = manager.resolve(
                context,
                surface: AnimationSurface.splash,
              );
              return const SizedBox.shrink();
            },
          ),
        ),
      ),
    );

    expect(presentation.entry.id, AnimationRegistry.ambientHeroId);
    expect(presentation.motionPreset, MotionPreset.loading);
    expect(presentation.shouldAnimate, isFalse);
    expect(presentation.duration, Duration.zero);
    expect(presentation.theme.primary, darkTheme.colorScheme.primary);
    expect(presentation.theme.secondary, darkTheme.colorScheme.secondary);
  });

  testWidgets('ManagedAnimationScene resolves animations through provider overrides', (
    tester,
  ) async {
    const customEntry = AnimationEntry(
      id: 'custom-splash',
      scene: RiveSceneAsset(
        asset: AppAssets.ambientStartupHero,
        semanticLabel: 'Custom splash illustration',
      ),
      motionPreset: MotionPreset.loading,
      surfaces: {
        AnimationSurface.splash,
      },
    );
    const customRegistry = AnimationRegistry(
      entries: {
        'custom-splash': customEntry,
      },
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          animationRegistryProvider.overrideWithValue(customRegistry),
        ],
        child: MediaQuery(
          data: const MediaQueryData(
            disableAnimations: true,
            accessibleNavigation: true,
          ),
          child: MaterialApp(
            theme: AppTheme.light(useGoogleFonts: false),
            home: Scaffold(
              body: ManagedAnimationScene(
                surface: AnimationSurface.splash,
                fallbackBuilder: (context, presentation) => Text(
                  presentation.entry.id,
                ),
              ),
            ),
          ),
        ),
      ),
    );

    expect(find.text('custom-splash'), findsOneWidget);
    expect(find.byType(rive.RiveWidgetBuilder), findsNothing);
  });
}
