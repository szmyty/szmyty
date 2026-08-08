import 'package:egohygiene/app/startup/domain/initialization_task.dart';
import 'package:egohygiene/app/startup/domain/startup_state.dart';
import 'package:egohygiene/app/startup/presentation/splash_transition.dart';
import 'package:egohygiene/app/startup/providers/startup_manager.dart';
import 'package:egohygiene/shared/performance/performance_manager.dart';
import 'package:egohygiene/shared/performance/performance_provider.dart';
import 'package:egohygiene/shared/providers/performance_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _CapturingPerformanceProvider implements PerformanceProvider {
  final List<CompletedPerformanceTrace> traces = [];

  @override
  String get providerId => 'capturing';

  @override
  bool get isEnabled => true;

  @override
  Future<void> initialize() async {}

  @override
  Future<void> recordMarker(PerformanceMarker marker) async {}

  @override
  Future<void> recordTrace(CompletedPerformanceTrace trace) async {
    traces.add(trace);
  }

  @override
  Future<void> dispose() async {}
}

void main() {
  group('StartupManager', () {
    test('runs initialization tasks and reaches ready state', () async {
      final executedStages = <StartupStage>[];
      final performanceProvider = _CapturingPerformanceProvider();
      final container = ProviderContainer(
        overrides: [
          performanceManagerProvider.overrideWith(
            (ref) => PerformanceManager(provider: performanceProvider),
          ),
          startupInitializationTasksProvider.overrideWithValue([
            InitializationTask(
              stage: StartupStage.dependencyInitialization,
              run: () async => executedStages.add(StartupStage.dependencyInitialization),
            ),
            InitializationTask(
              stage: StartupStage.configuration,
              run: () async => executedStages.add(StartupStage.configuration),
            ),
          ]),
          startupTransitionProvider.overrideWithValue(
            const SplashTransition(minimumDisplayDuration: Duration.zero),
          ),
        ],
      );
      addTearDown(container.dispose);

      await container.read(startupManagerProvider.notifier).initialize();

      final state = container.read(startupManagerProvider);
      expect(executedStages, [
        StartupStage.dependencyInitialization,
        StartupStage.configuration,
      ]);
      expect(state.status, StartupStatus.ready);
      expect(state.stage, StartupStage.complete);
      expect(state.progress, 1.0);
      expect(performanceProvider.traces, hasLength(1));
      expect(performanceProvider.traces.first.name, 'startup_lifecycle');
    });

    test('moves to failure state when a task throws', () async {
      final performanceProvider = _CapturingPerformanceProvider();
      final container = ProviderContainer(
        overrides: [
          performanceManagerProvider.overrideWith(
            (ref) => PerformanceManager(provider: performanceProvider),
          ),
          startupInitializationTasksProvider.overrideWithValue([
            InitializationTask(
              stage: StartupStage.dependencyInitialization,
              run: () async {
                throw StateError('dependency init failed');
              },
            ),
          ]),
          startupTransitionProvider.overrideWithValue(
            const SplashTransition(minimumDisplayDuration: Duration.zero),
          ),
        ],
      );
      addTearDown(container.dispose);

      await container.read(startupManagerProvider.notifier).initialize();

      final state = container.read(startupManagerProvider);
      expect(state.status, StartupStatus.failure);
      expect(state.hasError, isTrue);
      expect(performanceProvider.traces, hasLength(1));
      expect(performanceProvider.traces.first.outcome, 'failure');
    });

    test('default task list includes onboarding, permission and notification stages in correct order', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final tasks = container.read(startupInitializationTasksProvider);
      final stages = tasks.map((t) => t.stage).toList();

      final authIndex = stages.indexOf(StartupStage.authentication);
      final onboardingIndex = stages.indexOf(StartupStage.onboardingInitialization);
      final permissionIndex = stages.indexOf(StartupStage.permissionInitialization);
      final notificationIndex = stages.indexOf(StartupStage.notificationInitialization);
      final navigationIndex = stages.indexOf(StartupStage.navigationInitialization);

      expect(onboardingIndex, greaterThan(authIndex), reason: 'onboarding comes after authentication');
      expect(permissionIndex, greaterThan(onboardingIndex), reason: 'permission comes after onboarding');
      expect(notificationIndex, greaterThan(permissionIndex), reason: 'notification comes after permission');
      expect(navigationIndex, greaterThan(notificationIndex), reason: 'navigation comes after notification');
    });
  });
}
