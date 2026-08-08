import 'package:egohygiene/shared/capture/context_capture_engine.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// A [ContextProvider] that returns a fixed list of signals when called.
class _FixedContextProvider implements ContextProvider {
  _FixedContextProvider({
    required this.providerId,
    required this.category,
    this.signals = const [],
    this.throwOnCapture = false,
    this.available = true,
  }) : displayName = 'Fixed Provider';

  @override
  final String providerId;

  @override
  final String displayName;

  @override
  final ContextCategory category;

  @override
  bool get isAvailable => available;

  final bool available;
  final List<ContextSignal> signals;
  final bool throwOnCapture;

  bool initialized = false;
  bool disposed = false;
  int captureCallCount = 0;

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<List<ContextSignal>> capture() async {
    captureCallCount++;
    if (throwOnCapture) throw Exception('provider failure');
    return signals;
  }

  @override
  Future<void> dispose() async => disposed = true;
}

/// Creates a [ContextSignal] with the supplied values.
ContextSignal _signal({
  String key = 'test.key',
  Object? value = 42,
  ContextCategory category = ContextCategory.custom,
  String providerId = 'test',
}) {
  return ContextSignal(
    key: key,
    value: value,
    category: category,
    providerId: providerId,
    capturedAt: DateTime(2025),
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── ContextCategory ──────────────────────────────────────────────────────

  group('ContextCategory', () {
    test('has eight variants', () {
      expect(ContextCategory.values, hasLength(8));
    });

    test('contains all required variants', () {
      expect(
        ContextCategory.values,
        containsAll([
          ContextCategory.weather,
          ContextCategory.environment,
          ContextCategory.location,
          ContextCategory.health,
          ContextCategory.calendar,
          ContextCategory.device,
          ContextCategory.time,
          ContextCategory.custom,
        ]),
      );
    });
  });

  // ── ContextSignal ────────────────────────────────────────────────────────

  group('ContextSignal', () {
    test('stores all required fields', () {
      final now = DateTime(2025, 6, 1, 10);
      final signal = ContextSignal(
        key: 'time.hour_of_day',
        value: 10,
        category: ContextCategory.time,
        providerId: 'time',
        capturedAt: now,
        metadata: const {'unit': 'hour'},
      );

      expect(signal.key, 'time.hour_of_day');
      expect(signal.value, 10);
      expect(signal.category, ContextCategory.time);
      expect(signal.providerId, 'time');
      expect(signal.capturedAt, now);
      expect(signal.metadata, {'unit': 'hour'});
    });

    test('metadata defaults to empty map', () {
      final signal = _signal();
      expect(signal.metadata, isEmpty);
    });

    test('toString contains key and category', () {
      final signal = _signal(key: 'device.battery', category: ContextCategory.device);
      final str = signal.toString();
      expect(str, contains('device.battery'));
      expect(str, contains('device'));
    });
  });

  // ── ContextCaptureResult ─────────────────────────────────────────────────

  group('ContextCaptureResult', () {
    // ── success ──

    group('success', () {
      test('isSuccess is true', () {
        final result = ContextCaptureResult.success(
          providerId: 'time',
          signals: [_signal()],
        );
        expect(result.isSuccess, isTrue);
        expect(result.isFailure, isFalse);
        expect(result.error, isNull);
      });

      test('carries the supplied signals', () {
        final sig = _signal(key: 'time.hour_of_day', value: 10);
        final result = ContextCaptureResult.success(
          providerId: 'time',
          signals: [sig],
        );
        expect(result.signals, hasLength(1));
        expect(result.signals.first.key, 'time.hour_of_day');
      });

      test('signals list is unmodifiable', () {
        final result = ContextCaptureResult.success(
          providerId: 'time',
          signals: [_signal()],
        );
        expect(() => (result.signals as dynamic).add(_signal()), throwsUnsupportedError);
      });

      test('uses provided capturedAt', () {
        final ts = DateTime(2025);
        final result = ContextCaptureResult.success(
          providerId: 'time',
          signals: [],
          capturedAt: ts,
        );
        expect(result.capturedAt, ts);
      });
    });

    // ── failure ──

    group('failure', () {
      test('isFailure is true', () {
        final result = ContextCaptureResult.failure(
          providerId: 'weather',
          error: 'network error',
        );
        expect(result.isFailure, isTrue);
        expect(result.isSuccess, isFalse);
        expect(result.error, 'network error');
      });

      test('signals list is empty', () {
        final result = ContextCaptureResult.failure(
          providerId: 'weather',
          error: Exception('boom'),
        );
        expect(result.signals, isEmpty);
      });

      test('toString contains error', () {
        final result = ContextCaptureResult.failure(
          providerId: 'weather',
          error: 'timeout',
        );
        expect(result.toString(), contains('timeout'));
      });
    });
  });

  // ── ContextCaptureSnapshot ───────────────────────────────────────────────

  group('ContextCaptureSnapshot', () {
    test('empty() produces an empty snapshot', () {
      final snap = ContextCaptureSnapshot.empty();
      expect(snap.isEmpty, isTrue);
      expect(snap.size, 0);
      expect(snap.signals, isEmpty);
      expect(snap.results, isEmpty);
    });

    test('empty() uses provided capturedAt', () {
      final ts = DateTime(2025, 3);
      final snap = ContextCaptureSnapshot.empty(capturedAt: ts);
      expect(snap.capturedAt, ts);
    });

    test('isNotEmpty is true when signals are present', () {
      final snap = ContextCaptureSnapshot(
        signals: [_signal()],
        capturedAt: DateTime.now(),
        results: const [],
      );
      expect(snap.isNotEmpty, isTrue);
    });

    test('size matches signal count', () {
      final snap = ContextCaptureSnapshot(
        signals: [
          _signal(),
          _signal(key: 'x.y'),
        ],
        capturedAt: DateTime.now(),
        results: const [],
      );
      expect(snap.size, 2);
    });

    test('byCategory returns only matching signals', () {
      final snap = ContextCaptureSnapshot(
        signals: [
          _signal(key: 'time.hour', category: ContextCategory.time),
          _signal(key: 'device.battery', category: ContextCategory.device),
          _signal(key: 'time.weekday', category: ContextCategory.time),
        ],
        capturedAt: DateTime.now(),
        results: const [],
      );
      final time = snap.byCategory(ContextCategory.time);
      expect(time, hasLength(2));
      expect(time.map((s) => s.key), containsAll(['time.hour', 'time.weekday']));
    });

    test('signalByKey returns correct signal', () {
      final sig = _signal(key: 'time.hour_of_day', value: 14);
      final snap = ContextCaptureSnapshot(
        signals: [sig],
        capturedAt: DateTime.now(),
        results: const [],
      );
      expect(snap.signalByKey('time.hour_of_day'), sig);
    });

    test('signalByKey returns null for missing key', () {
      final snap = ContextCaptureSnapshot.empty();
      expect(snap.signalByKey('missing'), isNull);
    });

    test('get<T> returns typed value', () {
      final snap = ContextCaptureSnapshot(
        signals: [_signal(key: 'time.hour', value: 9)],
        capturedAt: DateTime.now(),
        results: const [],
      );
      expect(snap.get<int>('time.hour'), 9);
    });

    test('get<T> returns null for wrong type', () {
      final snap = ContextCaptureSnapshot(
        signals: [_signal(key: 'time.hour', value: 9)],
        capturedAt: DateTime.now(),
        results: const [],
      );
      expect(snap.get<String>('time.hour'), isNull);
    });

    test('contributingProviders lists successful providers with signals', () {
      final snap = ContextCaptureSnapshot(
        signals: [_signal(providerId: 'time')],
        capturedAt: DateTime.now(),
        results: [
          ContextCaptureResult.success(
            providerId: 'time',
            signals: [_signal()],
          ),
          ContextCaptureResult.failure(
            providerId: 'weather',
            error: 'offline',
          ),
        ],
      );
      expect(snap.contributingProviders, contains('time'));
      expect(snap.contributingProviders, isNot(contains('weather')));
    });

    test('failedProviders lists failed providers', () {
      final snap = ContextCaptureSnapshot(
        signals: const [],
        capturedAt: DateTime.now(),
        results: [
          ContextCaptureResult.failure(
            providerId: 'weather',
            error: 'timeout',
          ),
        ],
      );
      expect(snap.failedProviders, contains('weather'));
    });

    test('toString contains signal count and capturedAt', () {
      final snap = ContextCaptureSnapshot.empty(capturedAt: DateTime(2025));
      final str = snap.toString();
      expect(str, contains('signals: 0'));
      expect(str, contains('2025'));
    });
  });

  // ── NoopContextProvider ──────────────────────────────────────────────────

  group('NoopContextProvider', () {
    test('providerId contains category name', () {
      const prov = NoopContextProvider(category: ContextCategory.weather);
      expect(prov.providerId, contains('weather'));
    });

    test('isAvailable is true', () {
      expect(const NoopContextProvider().isAvailable, isTrue);
    });

    test('initialize() completes without error', () async {
      await expectLater(
        const NoopContextProvider().initialize(),
        completes,
      );
    });

    test('capture() returns empty list', () async {
      final signals = await const NoopContextProvider().capture();
      expect(signals, isEmpty);
    });

    test('dispose() completes without error', () async {
      await expectLater(
        const NoopContextProvider().dispose(),
        completes,
      );
    });
  });

  // ── TimeContextProvider ──────────────────────────────────────────────────

  group('TimeContextProvider', () {
    test('providerId is "time"', () {
      expect(const TimeContextProvider().providerId, 'time');
    });

    test('category is time', () {
      expect(const TimeContextProvider().category, ContextCategory.time);
    });

    test('isAvailable is always true', () {
      expect(const TimeContextProvider().isAvailable, isTrue);
    });

    test('capture() returns expected signal keys', () async {
      final signals = await const TimeContextProvider().capture();
      final keys = signals.map((s) => s.key).toList();
      expect(keys, contains('time.iso8601'));
      expect(keys, contains('time.hour_of_day'));
      expect(keys, contains('time.minute'));
      expect(keys, contains('time.weekday'));
      expect(keys, contains('time.day_of_month'));
      expect(keys, contains('time.month'));
      expect(keys, contains('time.year'));
      expect(keys, contains('time.is_weekend'));
    });

    test('all signals have category time', () async {
      final signals = await const TimeContextProvider().capture();
      expect(signals.every((s) => s.category == ContextCategory.time), isTrue);
    });

    test('all signals have providerId "time"', () async {
      final signals = await const TimeContextProvider().capture();
      expect(signals.every((s) => s.providerId == 'time'), isTrue);
    });

    test('hour_of_day is in 0..23 range', () async {
      final signals = await const TimeContextProvider().capture();
      final hour = signals.firstWhere((s) => s.key == 'time.hour_of_day').value! as int;
      expect(hour, greaterThanOrEqualTo(0));
      expect(hour, lessThanOrEqualTo(23));
    });

    test('weekday is in 1..7 range', () async {
      final signals = await const TimeContextProvider().capture();
      final weekday = signals.firstWhere((s) => s.key == 'time.weekday').value! as int;
      expect(weekday, greaterThanOrEqualTo(1));
      expect(weekday, lessThanOrEqualTo(7));
    });

    test('is_weekend is bool', () async {
      final signals = await const TimeContextProvider().capture();
      final isWeekend = signals.firstWhere((s) => s.key == 'time.is_weekend').value;
      expect(isWeekend, isA<bool>());
    });
  });

  // ── ContextCaptureEngine ─────────────────────────────────────────────────

  group('ContextCaptureEngine', () {
    late _FixedContextProvider provider;
    late ContextCaptureEngine engine;

    setUp(() {
      provider = _FixedContextProvider(
        providerId: 'fixed',
        category: ContextCategory.custom,
        signals: [_signal()],
      );
      engine = ContextCaptureEngine(providers: [provider]);
    });

    tearDown(() async => engine.dispose());

    // ── initialization ──

    test('initialize() calls provider.initialize()', () async {
      await engine.initialize();
      expect(provider.initialized, isTrue);
    });

    test('calling initialize() twice is a no-op', () async {
      await engine.initialize();
      await engine.initialize();
      expect(provider.initialized, isTrue);
    });

    test('initialize() with no providers completes without error', () async {
      final empty = ContextCaptureEngine();
      await expectLater(empty.initialize(), completes);
      await empty.dispose();
    });

    // ── provider registry ──

    test('providers list reflects registered providers', () {
      expect(engine.providers, hasLength(1));
      expect(engine.providers.first.providerId, 'fixed');
    });

    test('registerProvider adds a provider', () {
      final extra = _FixedContextProvider(
        providerId: 'extra',
        category: ContextCategory.time,
      );
      engine.registerProvider(extra);
      expect(engine.providers, hasLength(2));
    });

    test('providers list is unmodifiable', () {
      expect(
        () => (engine.providers as dynamic).add(provider),
        throwsUnsupportedError,
      );
    });

    // ── capture ──

    test('capture() returns snapshot with signals', () async {
      await engine.initialize();
      final snap = await engine.capture();
      expect(snap.isNotEmpty, isTrue);
      expect(snap.signals, hasLength(1));
    });

    test('capture() stores snapshot as latestSnapshot', () async {
      await engine.initialize();
      expect(engine.latestSnapshot, isNull);
      final snap = await engine.capture();
      expect(engine.latestSnapshot, same(snap));
    });

    test('capture() with no providers returns empty snapshot', () async {
      final empty = ContextCaptureEngine();
      await empty.initialize();
      final snap = await empty.capture();
      expect(snap.isEmpty, isTrue);
      await empty.dispose();
    });

    test('capture() skips unavailable providers', () async {
      final unavailable = _FixedContextProvider(
        providerId: 'unavailable',
        category: ContextCategory.weather,
        available: false,
        signals: [_signal(key: 'weather.temp')],
      );
      final eng = ContextCaptureEngine(providers: [unavailable]);
      await eng.initialize();
      final snap = await eng.capture();
      expect(snap.isEmpty, isTrue);
      expect(unavailable.captureCallCount, 0);
      await eng.dispose();
    });

    test('capture() records failure result when provider throws', () async {
      final throwing = _FixedContextProvider(
        providerId: 'throwing',
        category: ContextCategory.health,
        throwOnCapture: true,
      );
      final eng = ContextCaptureEngine(providers: [throwing]);
      await eng.initialize();
      final snap = await eng.capture();
      expect(snap.failedProviders, contains('throwing'));
      expect(snap.isEmpty, isTrue);
      await eng.dispose();
    });

    test('capture() continues past a failing provider', () async {
      final good = _FixedContextProvider(
        providerId: 'good',
        category: ContextCategory.time,
        signals: [_signal(key: 'time.hour')],
      );
      final bad = _FixedContextProvider(
        providerId: 'bad',
        category: ContextCategory.weather,
        throwOnCapture: true,
      );
      final eng = ContextCaptureEngine(providers: [bad, good]);
      await eng.initialize();
      final snap = await eng.capture();
      expect(snap.signals, hasLength(1));
      expect(snap.failedProviders, contains('bad'));
      expect(snap.contributingProviders, contains('good'));
      await eng.dispose();
    });

    test('capture() assembles signals from multiple providers', () async {
      final time = _FixedContextProvider(
        providerId: 'time',
        category: ContextCategory.time,
        signals: [_signal(key: 'time.hour', category: ContextCategory.time)],
      );
      final device = _FixedContextProvider(
        providerId: 'device',
        category: ContextCategory.device,
        signals: [
          _signal(key: 'device.battery', category: ContextCategory.device),
        ],
      );
      final eng = ContextCaptureEngine(providers: [time, device]);
      await eng.initialize();
      final snap = await eng.capture();
      expect(snap.signals, hasLength(2));
      expect(snap.byCategory(ContextCategory.time), hasLength(1));
      expect(snap.byCategory(ContextCategory.device), hasLength(1));
      await eng.dispose();
    });

    // ── dispose ──

    test('dispose() calls provider.dispose()', () async {
      await engine.initialize();
      await engine.dispose();
      expect(provider.disposed, isTrue);
    });

    test('dispose() clears latestSnapshot', () async {
      await engine.initialize();
      await engine.capture();
      await engine.dispose();
      expect(engine.latestSnapshot, isNull);
    });

    test('latestSnapshot is null before first capture', () async {
      await engine.initialize();
      expect(engine.latestSnapshot, isNull);
    });
  });
}
