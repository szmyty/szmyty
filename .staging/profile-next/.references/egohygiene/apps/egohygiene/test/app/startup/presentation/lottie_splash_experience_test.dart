import 'package:egohygiene/app/startup/presentation/lottie_splash_experience.dart';
import 'package:egohygiene/shared/animation/animation_engine.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rive/rive.dart' as rive;

void main() {
  testWidgets('keeps a static ambient fallback when animations are disabled', (
    tester,
  ) async {
    await tester.pumpWidget(
      MediaQuery(
        data: const MediaQueryData(
          disableAnimations: true,
          accessibleNavigation: true,
        ),
        child: ProviderScope(
          child: MaterialApp(
            theme: AppTheme.light(useGoogleFonts: false),
            home: const Scaffold(body: AmbientSplashExperience()),
          ),
        ),
      ),
    );

    expect(tester.hasRunningAnimations, isFalse);
    expect(find.byType(rive.RiveWidgetBuilder), findsNothing);
    expect(find.byIcon(Icons.psychology_alt_outlined), findsOneWidget);
    expect(find.text('EGO HYGIENE'), findsOneWidget);
    expect(find.text('Preparing your workspace...'), findsOneWidget);
  });

  testWidgets('builds the shared Rive scene when animations are enabled', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.dark(useGoogleFonts: false),
          home: const Scaffold(body: AmbientSplashExperience()),
        ),
      ),
    );
    await tester.pump();
    await tester.pump();

    expect(tester.takeException(), isNull);
    expect(find.byType(ManagedAnimationScene), findsOneWidget);
    expect(find.byIcon(Icons.favorite_border_rounded), findsOneWidget);
    expect(find.byIcon(Icons.self_improvement_outlined), findsOneWidget);
    expect(find.text('EGO HYGIENE'), findsOneWidget);
  });
}
