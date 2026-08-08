import 'package:egohygiene/app/startup/presentation/splash_experience.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart' show WidgetTester;

/// Lightweight [SplashExperience] used in widget tests to avoid repeating
/// Lottie animations that prevent [WidgetTester.pumpAndSettle] from settling.
///
/// Use it by overriding [splashExperienceProvider]:
/// ```dart
/// splashExperienceProvider.overrideWithValue(const StaticSplashExperience()),
/// ```
class StaticSplashExperience extends SplashExperience {
  const StaticSplashExperience({super.key});

  @override
  Widget build(BuildContext context) => const SizedBox.shrink();
}
