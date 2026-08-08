import 'package:egohygiene/shared/theme/motion.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppDurations', () {
    test('durations are ordered ascending', () {
      expect(
        AppDurations.instant,
        lessThan(AppDurations.fast),
      );
      expect(
        AppDurations.fast,
        lessThan(AppDurations.standard),
      );
      expect(
        AppDurations.standard,
        lessThan(AppDurations.deliberate),
      );
      expect(
        AppDurations.deliberate,
        lessThan(AppDurations.slow),
      );
      expect(
        AppDurations.slow,
        lessThan(AppDurations.complex),
      );
      expect(
        AppDurations.complex,
        lessThan(AppDurations.wonder),
      );
    });

    test('specific duration values match spec', () {
      expect(AppDurations.instant, const Duration(milliseconds: 100));
      expect(AppDurations.fast, const Duration(milliseconds: 150));
      expect(AppDurations.standard, const Duration(milliseconds: 250));
      expect(AppDurations.deliberate, const Duration(milliseconds: 350));
      expect(AppDurations.slow, const Duration(milliseconds: 500));
      expect(AppDurations.complex, const Duration(milliseconds: 700));
      expect(AppDurations.wonder, const Duration(milliseconds: 1200));
    });
  });

  group('AppCurves', () {
    test('curve tokens are non-null', () {
      expect(AppCurves.standard, isNotNull);
      expect(AppCurves.decelerate, isNotNull);
      expect(AppCurves.accelerate, isNotNull);
      expect(AppCurves.emphasized, isNotNull);
      expect(AppCurves.spring, isNotNull);
      expect(AppCurves.linear, isNotNull);
      expect(AppCurves.bounce, isNotNull);
    });

    test('linear curve transforms 0 to 0 and 1 to 1', () {
      expect(AppCurves.linear.transform(0), closeTo(0.0, 0.001));
      expect(AppCurves.linear.transform(1), closeTo(1.0, 0.001));
    });

    test('standard curve starts and ends at boundary values', () {
      expect(AppCurves.standard.transform(0), closeTo(0.0, 0.001));
      expect(AppCurves.standard.transform(1), closeTo(1.0, 0.001));
    });
  });

  group('MotionPolicy', () {
    test('reduced motion collapses shared presets to no-op values', () {
      final policy = MotionManager.resolve(
        platform: TargetPlatform.android,
        reduceMotion: true,
      );

      expect(policy.shouldAnimate, isFalse);
      expect(policy.durationFor(MotionPreset.pageTransition), Duration.zero);
      expect(policy.curveFor(MotionPreset.modal), AppCurves.linear);
      expect(policy.offsetFor(MotionPreset.timeline), Offset.zero);
    });

    test('shared presets map to the expected token values', () {
      final policy = MotionManager.resolve(platform: TargetPlatform.android);

      expect(policy.durationFor(MotionPreset.selection), AppDurations.fast);
      expect(
        policy.durationFor(MotionPreset.pageTransition),
        AppDurations.standard,
      );
      expect(policy.durationFor(MotionPreset.modal), AppDurations.deliberate);
      expect(policy.curveFor(MotionPreset.selection), AppCurves.standard);
      expect(
        policy.curveFor(
          MotionPreset.pageTransition,
          direction: MotionDirection.exit,
        ),
        AppCurves.accelerate,
      );
    });

    test('platform-aware page transitions use horizontal motion on Cupertino', () {
      final cupertino = MotionManager.resolve(platform: TargetPlatform.iOS);
      final material = MotionManager.resolve(platform: TargetPlatform.android);

      expect(
        cupertino.offsetFor(MotionPreset.pageTransition),
        const Offset(0.08, 0),
      );
      expect(
        material.offsetFor(MotionPreset.pageTransition),
        const Offset(0, 0.04),
      );
    });
  });

  testWidgets('MotionManager reads reduced-motion flags from MediaQuery', (
    tester,
  ) async {
    late MotionPolicy policy;

    await tester.pumpWidget(
      MediaQuery(
        data: const MediaQueryData(
          disableAnimations: true,
          accessibleNavigation: true,
        ),
        child: MaterialApp(
          home: Builder(
            builder: (context) {
              policy = MotionManager.of(context);
              return const SizedBox.shrink();
            },
          ),
        ),
      ),
    );

    expect(policy.shouldAnimate, isFalse);
    expect(policy.durationFor(MotionPreset.selection), Duration.zero);
  });
}
