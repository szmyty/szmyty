import 'package:egohygiene/shared/performance/impl/local_performance_provider.dart';
import 'package:egohygiene/shared/performance/navigation_performance_observer.dart';
import 'package:egohygiene/shared/performance/performance_manager.dart';
import 'package:egohygiene/shared/performance/performance_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class _CapturingPerformanceProvider implements PerformanceProvider {
  bool initialized = false;
  bool disposed = false;
  final List<CompletedPerformanceTrace> traces = [];
  final List<PerformanceMarker> markers = [];

  @override
  String get providerId => 'capturing';

  @override
  bool get isEnabled => true;

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<void> recordTrace(CompletedPerformanceTrace trace) async {
    traces.add(trace);
  }

  @override
  Future<void> recordMarker(PerformanceMarker marker) async {
    markers.add(marker);
  }

  @override
  Future<void> dispose() async => disposed = true;
}

class _ThrowingPerformanceProvider extends _CapturingPerformanceProvider {
  @override
  Future<void> recordTrace(CompletedPerformanceTrace trace) async {
    throw Exception('provider failure');
  }

  @override
  Future<void> recordMarker(PerformanceMarker marker) async {
    throw Exception('provider failure');
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('PerformanceManager', () {
    late _CapturingPerformanceProvider provider;
    late PerformanceManager manager;

    setUp(() {
      provider = _CapturingPerformanceProvider();
      manager = PerformanceManager(provider: provider);
    });

    tearDown(() async => manager.dispose());

    test('initialize() calls provider.initialize()', () async {
      await manager.initialize();
      expect(provider.initialized, isTrue);
    });

    test('startTrace + stop() emits completed trace', () async {
      await manager.initialize();

      final trace = manager.startTrace('startup_lifecycle', category: 'startup');
      trace
        ..addMarker(
          PerformanceMarker.now(
            name: 'flutterBootstrap',
            type: PerformanceMarkerType.lifecycle,
          ),
        )
        ..addMetric(
          const PerformanceMetric(
            name: 'startup_duration_ms',
            value: 10,
            unit: PerformanceMetricUnit.milliseconds,
          ),
        );

      await trace.stop();

      expect(provider.traces, hasLength(1));
      expect(provider.traces.first.name, 'startup_lifecycle');
      expect(provider.traces.first.markers, hasLength(1));
      expect(provider.traces.first.metrics, hasLength(1));
    });

    test('timeAsyncTask() emits trace with success outcome', () async {
      await manager.initialize();

      final value = await manager.timeAsyncTask<int>('test_task', () async => 42);

      expect(value, 42);
      expect(provider.traces, hasLength(1));
      expect(provider.traces.first.outcome, 'success');
      expect(provider.traces.first.metrics, isNotEmpty);
    });

    test('timeAsyncTask() emits failure trace and rethrows', () async {
      await manager.initialize();

      await expectLater(
        manager.timeAsyncTask<void>('test_task', () async {
          throw StateError('boom');
        }),
        throwsStateError,
      );

      expect(provider.traces, hasLength(1));
      expect(provider.traces.first.outcome, 'failure');
    });

    test('recordBuildDuration() emits rendering trace', () async {
      await manager.initialize();

      await manager.recordBuildDuration(
        widgetName: 'HomeScreen',
        duration: const Duration(milliseconds: 15),
      );

      expect(provider.traces, hasLength(1));
      expect(provider.traces.first.category, 'rendering');
      expect(provider.traces.first.metrics.first.name, 'build_duration_ms');
    });

    test('provider failures are swallowed', () async {
      final throwingManager = PerformanceManager(
        provider: _ThrowingPerformanceProvider(),
      );
      await throwingManager.initialize();
      final trace = throwingManager.startTrace('failing_trace');

      await expectLater(trace.stop(), completes);
      await expectLater(
        throwingManager.recordMarker(PerformanceMarker.now(name: 'm')),
        completes,
      );
      await throwingManager.dispose();
    });
  });

  group('NavigationPerformanceObserver', () {
    testWidgets('didPush emits navigation trace after next frame', (tester) async {
      final provider = _CapturingPerformanceProvider();
      final manager = PerformanceManager(provider: provider);
      await manager.initialize();

      final observer = NavigationPerformanceObserver(performanceManager: manager);

      await tester.pumpWidget(
        MaterialApp(
          navigatorObservers: [observer],
          onGenerateRoute: (settings) => MaterialPageRoute<void>(
            settings: settings,
            builder: (_) => const SizedBox.shrink(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(provider.traces, isNotEmpty);
      final trace = provider.traces.first;
      expect(trace.name, 'navigation_transition');
      expect(trace.metrics.any((m) => m.name == 'transition_duration_ms'), isTrue);

      await manager.dispose();
    });
  });

  group('LocalPerformanceProvider', () {
    test('debugReport reflects captured data', () async {
      final provider = LocalPerformanceProvider();
      await provider.initialize();

      await provider.recordMarker(PerformanceMarker.now(name: 'first_frame'));
      await provider.recordTrace(
        CompletedPerformanceTrace(
          id: 'trace_1',
          name: 'startup',
          startedAt: DateTime.now(),
          endedAt: DateTime.now(),
        ),
      );

      expect(provider.debugReport(), contains('traces: 1'));
      expect(provider.debugReport(), contains('markers: 1'));
      await provider.dispose();
    });
  });
}
