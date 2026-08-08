import 'package:egohygiene/shared/analytics/analytics_manager.dart';
import 'package:egohygiene/shared/analytics/analytics_provider.dart';
import 'package:egohygiene/shared/analytics/impl/noop_analytics_provider.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Fake provider that records every call for assertion
// ---------------------------------------------------------------------------

class _CapturingProvider implements AnalyticsProvider {
  bool initialized = false;
  bool disposed = false;
  bool propertiesReset = false;
  bool didReset = false;
  final List<AnalyticsEvent> events = [];
  final List<AnalyticsScreenView> screenViews = [];
  final Map<String, String?> userProperties = {};

  @override
  String get providerId => 'capturing';

  @override
  bool get isEnabled => true;

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<void> trackEvent(AnalyticsEvent event) async => events.add(event);

  @override
  Future<void> trackScreenView(AnalyticsScreenView screenView) async => screenViews.add(screenView);

  @override
  Future<void> setUserProperty(String property, String? value) async => userProperties[property] = value;

  @override
  Future<void> resetUserProperties() async {
    userProperties.clear();
    propertiesReset = true;
  }

  @override
  Future<void> reset() async => didReset = true;

  @override
  Future<void> dispose() async => disposed = true;
}

/// A provider that throws on every tracking call.
class _ThrowingProvider extends _CapturingProvider {
  @override
  Future<void> trackEvent(AnalyticsEvent event) async => throw Exception('provider failure');

  @override
  Future<void> trackScreenView(AnalyticsScreenView screenView) async => throw Exception('provider failure');
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── AnalyticsEvent ───────────────────────────────────────────────────────

  group('AnalyticsEvent', () {
    test('default properties are empty', () {
      const event = AnalyticsEvent(name: 'test_event');
      expect(event.properties, isEmpty);
    });

    test('timestamp defaults to now when not provided', () {
      final before = DateTime.now();
      final event = AnalyticsEvent.now(name: 'test_event');
      final after = DateTime.now();
      expect(
        event.timestamp.isAfter(before) || event.timestamp == before,
        isTrue,
      );
      expect(
        event.timestamp.isBefore(after) || event.timestamp == after,
        isTrue,
      );
    });

    test('explicit timestamp is preserved', () {
      final ts = DateTime(2024);
      final event = AnalyticsEvent(name: 'test_event', timestamp: ts);
      expect(event.timestamp, ts);
    });

    test('toString includes name', () {
      const event = AnalyticsEvent(name: 'reflection_saved');
      expect(event.toString(), contains('reflection_saved'));
    });

    test('toString includes properties when present', () {
      const event = AnalyticsEvent(
        name: 'reflection_saved',
        properties: {'feature': 'reflection'},
      );
      expect(event.toString(), contains('feature'));
    });
  });

  // ── AnalyticsScreenView ──────────────────────────────────────────────────

  group('AnalyticsScreenView', () {
    test('default properties are empty', () {
      const view = AnalyticsScreenView(screenName: 'home');
      expect(view.properties, isEmpty);
    });

    test('screenClass defaults to null', () {
      const view = AnalyticsScreenView(screenName: 'home');
      expect(view.screenClass, isNull);
    });

    test('AnalyticsScreenView.now captures timestamp', () {
      final before = DateTime.now();
      final view = AnalyticsScreenView.now(screenName: 'home');
      final after = DateTime.now();
      expect(
        view.timestamp.isAfter(before) || view.timestamp == before,
        isTrue,
      );
      expect(
        view.timestamp.isBefore(after) || view.timestamp == after,
        isTrue,
      );
    });

    test('toString includes screenName', () {
      const view = AnalyticsScreenView(screenName: 'reflection_editor');
      expect(view.toString(), contains('reflection_editor'));
    });

    test('toString includes screenClass when set', () {
      const view = AnalyticsScreenView(
        screenName: 'home',
        screenClass: 'HomeScreen',
      );
      expect(view.toString(), contains('HomeScreen'));
    });
  });

  // ── AnalyticsConsentState ────────────────────────────────────────────────

  group('AnalyticsConsentState', () {
    test('has three states', () {
      expect(AnalyticsConsentState.values, hasLength(3));
    });

    test('values include granted, denied, and unknown', () {
      expect(
        AnalyticsConsentState.values,
        containsAll([
          AnalyticsConsentState.granted,
          AnalyticsConsentState.denied,
          AnalyticsConsentState.unknown,
        ]),
      );
    });
  });

  // ── AnalyticsManager ─────────────────────────────────────────────────────

  group('AnalyticsManager', () {
    late _CapturingProvider provider;
    late AnalyticsManager manager;

    setUp(() {
      provider = _CapturingProvider();
      manager = AnalyticsManager(
        provider: provider,
        consentCallback: () => AnalyticsConsentState.granted,
      );
    });

    tearDown(() async => manager.dispose());

    // ── initialization ──

    test('initialize() calls provider.initialize()', () async {
      await manager.initialize();
      expect(provider.initialized, isTrue);
    });

    test('calling initialize() twice is a no-op', () async {
      await manager.initialize();
      await manager.initialize();
      expect(provider.initialized, isTrue);
    });

    // ── consent gate ──

    test('isEnabled is true when initialized and consent granted', () async {
      await manager.initialize();
      expect(manager.isEnabled, isTrue);
    });

    test('isEnabled is false before initialization', () {
      expect(manager.isEnabled, isFalse);
    });

    test('isEnabled is false when consent is denied', () async {
      final mgr = AnalyticsManager(
        provider: provider,
        consentCallback: () => AnalyticsConsentState.denied,
      );
      await mgr.initialize();
      expect(mgr.isEnabled, isFalse);
      await mgr.dispose();
    });

    test('isEnabled is false when consent is unknown', () async {
      final mgr = AnalyticsManager(
        provider: provider,
        consentCallback: () => AnalyticsConsentState.unknown,
      );
      await mgr.initialize();
      expect(mgr.isEnabled, isFalse);
      await mgr.dispose();
    });

    // ── trackEvent ──

    test('trackEvent() forwards event to provider when consent granted', () async {
      await manager.initialize();
      const event = AnalyticsEvent(name: 'onboarding_completed');
      await manager.trackEvent(event);
      expect(provider.events, hasLength(1));
      expect(provider.events.first.name, 'onboarding_completed');
    });

    test('trackEvent() drops event when not initialized', () async {
      const event = AnalyticsEvent(name: 'test_event');
      await manager.trackEvent(event);
      expect(provider.events, isEmpty);
    });

    test('trackEvent() drops event when consent is denied', () async {
      final mgr = AnalyticsManager(
        provider: provider,
        consentCallback: () => AnalyticsConsentState.denied,
      );
      await mgr.initialize();
      await mgr.trackEvent(const AnalyticsEvent(name: 'test_event'));
      expect(provider.events, isEmpty);
      await mgr.dispose();
    });

    test('trackEvent() drops event when consent is unknown', () async {
      final mgr = AnalyticsManager(provider: provider);
      await mgr.initialize();
      await mgr.trackEvent(const AnalyticsEvent(name: 'test_event'));
      expect(provider.events, isEmpty);
      await mgr.dispose();
    });

    // ── trackScreenView ──

    test('trackScreenView() forwards view to provider when consent granted', () async {
      await manager.initialize();
      const view = AnalyticsScreenView(screenName: 'home');
      await manager.trackScreenView(view);
      expect(provider.screenViews, hasLength(1));
      expect(provider.screenViews.first.screenName, 'home');
    });

    test('trackScreenView() drops view when consent is denied', () async {
      final mgr = AnalyticsManager(
        provider: provider,
        consentCallback: () => AnalyticsConsentState.denied,
      );
      await mgr.initialize();
      await mgr.trackScreenView(
        const AnalyticsScreenView(screenName: 'home'),
      );
      expect(provider.screenViews, isEmpty);
      await mgr.dispose();
    });

    // ── setUserProperty ──

    test('setUserProperty() forwards property to provider', () async {
      await manager.initialize();
      await manager.setUserProperty('plan', 'free');
      expect(provider.userProperties['plan'], 'free');
    });

    test('setUserProperty() with null value unsets property', () async {
      await manager.initialize();
      await manager.setUserProperty('plan', 'free');
      await manager.setUserProperty('plan', null);
      expect(provider.userProperties['plan'], isNull);
    });

    test('setUserProperty() is dropped when consent denied', () async {
      final mgr = AnalyticsManager(
        provider: provider,
        consentCallback: () => AnalyticsConsentState.denied,
      );
      await mgr.initialize();
      await mgr.setUserProperty('plan', 'free');
      expect(provider.userProperties, isEmpty);
      await mgr.dispose();
    });

    // ── resetUserProperties ──

    test('resetUserProperties() clears provider properties', () async {
      await manager.initialize();
      await manager.setUserProperty('plan', 'free');
      await manager.resetUserProperties();
      expect(provider.propertiesReset, isTrue);
    });

    test('resetUserProperties() is a no-op before initialization', () async {
      await manager.resetUserProperties();
      expect(provider.propertiesReset, isFalse);
    });

    // ── reset ──

    test('reset() calls provider.reset()', () async {
      await manager.initialize();
      await manager.reset();
      expect(provider.didReset, isTrue);
    });

    test('reset() is a no-op before initialization', () async {
      await manager.reset();
      expect(provider.didReset, isFalse);
    });

    // ── resilience ──

    test('a throwing provider does not propagate exceptions to callers', () async {
      final throwing = _ThrowingProvider();
      final mgr = AnalyticsManager(
        provider: throwing,
        consentCallback: () => AnalyticsConsentState.granted,
      );
      await mgr.initialize();
      await expectLater(
        mgr.trackEvent(const AnalyticsEvent(name: 'test')),
        completes,
      );
      await expectLater(
        mgr.trackScreenView(const AnalyticsScreenView(screenName: 'home')),
        completes,
      );
      await mgr.dispose();
    });

    // ── dispose ──

    test('dispose() calls provider.dispose()', () async {
      await manager.initialize();
      await manager.dispose();
      expect(provider.disposed, isTrue);
    });
  });

  // ── NoopAnalyticsProvider ────────────────────────────────────────────────

  group('NoopAnalyticsProvider', () {
    const noop = NoopAnalyticsProvider();

    test('providerId is "noop"', () {
      expect(noop.providerId, 'noop');
    });

    test('isEnabled is false', () {
      expect(noop.isEnabled, isFalse);
    });

    test('initialize() completes without error', () async {
      await expectLater(noop.initialize(), completes);
    });

    test('trackEvent() completes without error', () async {
      await expectLater(
        noop.trackEvent(const AnalyticsEvent(name: 'test')),
        completes,
      );
    });

    test('trackScreenView() completes without error', () async {
      await expectLater(
        noop.trackScreenView(const AnalyticsScreenView(screenName: 'home')),
        completes,
      );
    });

    test('setUserProperty() completes without error', () async {
      await expectLater(noop.setUserProperty('plan', 'free'), completes);
    });

    test('resetUserProperties() completes without error', () async {
      await expectLater(noop.resetUserProperties(), completes);
    });

    test('reset() completes without error', () async {
      await expectLater(noop.reset(), completes);
    });

    test('dispose() completes without error', () async {
      await expectLater(noop.dispose(), completes);
    });

    test('manager backed by noop tracks no events', () async {
      final mgr = AnalyticsManager(
        provider: noop,
        consentCallback: () => AnalyticsConsentState.granted,
      );
      await mgr.initialize();
      // isEnabled is false because noop.isEnabled is false.
      expect(mgr.isEnabled, isFalse);
      // trackEvent should complete without error.
      await expectLater(
        mgr.trackEvent(const AnalyticsEvent(name: 'test')),
        completes,
      );
      await mgr.dispose();
    });
  });

  // ── default consent behavior ─────────────────────────────────────────────

  group('default consent behavior', () {
    test('manager with no consentCallback defaults to unknown — events dropped', () async {
      final provider = _CapturingProvider();
      final manager = AnalyticsManager(provider: provider);
      await manager.initialize();
      await manager.trackEvent(const AnalyticsEvent(name: 'test'));
      expect(provider.events, isEmpty);
      await manager.dispose();
    });
  });
}
