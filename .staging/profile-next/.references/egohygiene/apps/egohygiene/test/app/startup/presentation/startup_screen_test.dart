import 'package:egohygiene/app/startup/domain/initialization_task.dart';
import 'package:egohygiene/app/startup/domain/startup_state.dart';
import 'package:egohygiene/app/startup/presentation/splash_experience.dart';
import 'package:egohygiene/app/startup/presentation/splash_transition.dart';
import 'package:egohygiene/app/startup/presentation/startup_screen.dart';
import 'package:egohygiene/app/startup/providers/startup_manager.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

class _TestSplashExperience extends SplashExperience {
  const _TestSplashExperience();

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Splash experience'));
  }
}

void main() {
  testWidgets('navigates to dashboard after startup lifecycle completes', (tester) async {
    final router = GoRouter(
      initialLocation: '/startup',
      routes: [
        GoRoute(
          path: '/startup',
          builder: (context, state) => const StartupScreen(
            homeRoute: '/home',
            splashExperience: _TestSplashExperience(),
          ),
        ),
        GoRoute(
          path: '/home',
          builder: (context, state) => const Scaffold(
            body: Center(child: Text('Home Dashboard')),
          ),
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          startupInitializationTasksProvider.overrideWithValue([
            const InitializationTask(stage: StartupStage.dependencyInitialization, run: _noOp),
          ]),
          startupTransitionProvider.overrideWithValue(
            const SplashTransition(minimumDisplayDuration: Duration.zero),
          ),
        ],
        child: TranslationProvider(
          child: MaterialApp.router(routerConfig: router),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Home Dashboard'), findsOneWidget);
  });
}

Future<void> _noOp() async {}
