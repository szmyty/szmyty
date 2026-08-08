import 'package:egohygiene/shared/services/crash_reporting_manager.dart';
import 'package:egohygiene/shared/services/crash_reporting_provider.dart';
import 'package:egohygiene/shared/services/impl/noop_crash_reporting_provider.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Fake provider that records every call for assertion
// ---------------------------------------------------------------------------

class _CapturingProvider implements CrashReportingProvider {
  bool initialized = false;
  bool disposed = false;
  final List<CrashReport> submitted = [];
  final List<CrashBreadcrumb> breadcrumbs = [];
  final Map<String, String> tags = {};
  bool breadcrumbsCleared = false;

  @override
  String get providerId => 'capturing';

  @override
  bool get isEnabled => true;

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<void> submitReport(CrashReport report) async => submitted.add(report);

  @override
  Future<void> addBreadcrumb(CrashBreadcrumb breadcrumb) async => breadcrumbs.add(breadcrumb);

  @override
  Future<void> clearBreadcrumbs() async {
    breadcrumbs.clear();
    breadcrumbsCleared = true;
  }

  @override
  Future<void> setTag(String key, String value) async => tags[key] = value;

  @override
  Future<void> removeTag(String key) async => tags.remove(key);

  @override
  Future<void> dispose() async => disposed = true;
}

/// A provider that throws on every submit call.
class _ThrowingProvider extends _CapturingProvider {
  @override
  Future<void> submitReport(CrashReport report) async => throw Exception('provider failure');
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── ErrorSeverity ────────────────────────────────────────────────────────

  group('ErrorSeverity', () {
    test('has four levels', () {
      expect(ErrorSeverity.values, hasLength(4));
    });

    test('levels are ordered info < warning < error < fatal', () {
      expect(ErrorSeverity.info.index, lessThan(ErrorSeverity.warning.index));
      expect(
        ErrorSeverity.warning.index,
        lessThan(ErrorSeverity.error.index),
      );
      expect(ErrorSeverity.error.index, lessThan(ErrorSeverity.fatal.index));
    });
  });

  // ── ErrorContext ─────────────────────────────────────────────────────────

  group('ErrorContext', () {
    test('default instance has empty maps', () {
      const ctx = ErrorContext();
      expect(ctx.tags, isEmpty);
      expect(ctx.extras, isEmpty);
    });

    test('toString includes tags and extras', () {
      const ctx = ErrorContext(
        tags: {'feature': 'reflection'},
        extras: {'retry': 3},
      );
      expect(ctx.toString(), contains('feature'));
      expect(ctx.toString(), contains('retry'));
    });
  });

  // ── CrashBreadcrumb ──────────────────────────────────────────────────────

  group('CrashBreadcrumb', () {
    test('now() captures a timestamp close to DateTime.now', () {
      final before = DateTime.now();
      final b = CrashBreadcrumb.now(message: 'nav to home');
      final after = DateTime.now();

      expect(
        b.timestamp.isAfter(before) || b.timestamp.isAtSameMomentAs(before),
        isTrue,
      );
      expect(
        b.timestamp.isBefore(after) || b.timestamp.isAtSameMomentAs(after),
        isTrue,
      );
    });

    test('toString includes message and category', () {
      final b = CrashBreadcrumb.now(
        message: 'button tapped',
        category: 'ui',
      );
      expect(b.toString(), contains('button tapped'));
      expect(b.toString(), contains('ui'));
    });

    test('toString includes metadata', () {
      final b = CrashBreadcrumb.now(
        message: 'request sent',
        metadata: {'url': '/api/v1/entries'},
      );
      expect(b.toString(), contains('/api/v1/entries'));
    });

    test('category is optional', () {
      final b = CrashBreadcrumb.now(message: 'something happened');
      expect(b.category, isNull);
    });
  });

  // ── CrashReport ──────────────────────────────────────────────────────────

  group('CrashReport', () {
    test('toString includes severity and error', () {
      final report = CrashReport(
        error: Exception('disk full'),
        severity: ErrorSeverity.error,
      );
      expect(report.toString(), contains('error'));
      expect(report.toString(), contains('disk full'));
    });

    test('toString includes optional message', () {
      final report = CrashReport(
        error: Exception('oops'),
        severity: ErrorSeverity.warning,
        message: 'extra detail',
      );
      expect(report.toString(), contains('extra detail'));
    });

    test('toString includes breadcrumbs', () {
      final report = CrashReport(
        error: Exception('crash'),
        severity: ErrorSeverity.fatal,
        breadcrumbs: [
          CrashBreadcrumb.now(message: 'step one'),
        ],
      );
      expect(report.toString(), contains('step one'));
    });

    test('default context is empty', () {
      final report = CrashReport(
        error: Exception('e'),
        severity: ErrorSeverity.info,
      );
      expect(report.context.tags, isEmpty);
      expect(report.context.extras, isEmpty);
    });
  });

  // ── CrashReportingManager ────────────────────────────────────────────────

  group('CrashReportingManager', () {
    late _CapturingProvider provider;
    late CrashReportingManager manager;

    setUp(() {
      provider = _CapturingProvider();
      manager = CrashReportingManager(provider: provider);
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
      // Provider.initialize is idempotent in this fake, so we just verify
      // the second call does not throw.
      expect(provider.initialized, isTrue);
    });

    // ── reportError ──

    test('reportError() submits a report with correct severity', () async {
      await manager.initialize();
      await manager.reportError(Exception('network timeout'));
      expect(provider.submitted, hasLength(1));
      expect(provider.submitted.first.severity, ErrorSeverity.error);
    });

    test('reportError() forwards custom severity', () async {
      await manager.initialize();
      await manager.reportError(
        Exception('minor'),
        severity: ErrorSeverity.warning,
      );
      expect(provider.submitted.first.severity, ErrorSeverity.warning);
    });

    test('reportError() forwards context', () async {
      await manager.initialize();
      const ctx = ErrorContext(tags: {'feature': 'reflection'});
      await manager.reportError(Exception('e'), context: ctx);
      expect(provider.submitted.first.context.tags['feature'], 'reflection');
    });

    test('reportError() forwards message', () async {
      await manager.initialize();
      await manager.reportError(Exception('e'), message: 'custom message');
      expect(provider.submitted.first.message, 'custom message');
    });

    test('reportError() is suppressed when consent is denied', () async {
      final noConsent = CrashReportingManager(
        provider: provider,
        consentCallback: () => false,
      );
      await noConsent.initialize();
      await noConsent.reportError(Exception('no consent'));
      expect(provider.submitted, isEmpty);
      await noConsent.dispose();
    });

    // ── reportFatal ──

    test('reportFatal() submits a fatal severity report', () async {
      await manager.initialize();
      await manager.reportFatal(Exception('crash'));
      expect(provider.submitted.first.severity, ErrorSeverity.fatal);
    });

    test('reportFatal() is suppressed when consent is denied', () async {
      final noConsent = CrashReportingManager(
        provider: provider,
        consentCallback: () => false,
      );
      await noConsent.initialize();
      await noConsent.reportFatal(Exception('crash'));
      expect(provider.submitted, isEmpty);
      await noConsent.dispose();
    });

    // ── breadcrumbs ──

    test('addBreadcrumb() forwards to provider after init', () async {
      await manager.initialize();
      final b = CrashBreadcrumb.now(message: 'user tapped save');
      await manager.addBreadcrumb(b);
      expect(provider.breadcrumbs, [b]);
    });

    test('breadcrumbs added before init are flushed on initialize()', () async {
      final b = CrashBreadcrumb.now(message: 'early event');
      await manager.addBreadcrumb(b); // before init
      await manager.initialize();
      expect(provider.breadcrumbs, contains(b));
    });

    test('clearBreadcrumbs() removes all breadcrumbs from provider', () async {
      await manager.initialize();
      await manager.addBreadcrumb(CrashBreadcrumb.now(message: 'b1'));
      await manager.clearBreadcrumbs();
      expect(provider.breadcrumbsCleared, isTrue);
      expect(provider.breadcrumbs, isEmpty);
    });

    test('clearBreadcrumbs() before init empties pending buffer', () async {
      await manager.addBreadcrumb(CrashBreadcrumb.now(message: 'queued'));
      await manager.clearBreadcrumbs();
      await manager.initialize();
      expect(provider.breadcrumbs, isEmpty);
    });

    // ── tags ──

    test('setTag() forwards to provider', () async {
      await manager.initialize();
      await manager.setTag('env', 'staging');
      expect(provider.tags['env'], 'staging');
    });

    test('removeTag() removes the tag from provider', () async {
      await manager.initialize();
      await manager.setTag('env', 'staging');
      await manager.removeTag('env');
      expect(provider.tags.containsKey('env'), isFalse);
    });

    test('setTag() before init is a no-op', () async {
      await manager.setTag('env', 'staging');
      expect(provider.tags, isEmpty);
    });

    // ── resilience ──

    test('a throwing provider does not propagate exceptions to callers', () async {
      final throwing = _ThrowingProvider();
      final mgr = CrashReportingManager(provider: throwing);
      await mgr.initialize();
      await expectLater(mgr.reportError(Exception('e')), completes);
      await mgr.dispose();
    });

    // ── dispose ──

    test('dispose() calls provider.dispose()', () async {
      await manager.initialize();
      await manager.dispose();
      expect(provider.disposed, isTrue);
    });
  });

  // ── NoopCrashReportingProvider ───────────────────────────────────────────

  group('NoopCrashReportingProvider', () {
    const noop = NoopCrashReportingProvider();

    test('providerId is "noop"', () {
      expect(noop.providerId, 'noop');
    });

    test('isEnabled is false', () {
      expect(noop.isEnabled, isFalse);
    });

    test('initialize() completes without error', () async {
      await expectLater(noop.initialize(), completes);
    });

    test('submitReport() completes without error', () async {
      final report = CrashReport(
        error: Exception('test'),
        severity: ErrorSeverity.error,
      );
      await expectLater(noop.submitReport(report), completes);
    });

    test('addBreadcrumb() completes without error', () async {
      final b = CrashBreadcrumb.now(message: 'test');
      await expectLater(noop.addBreadcrumb(b), completes);
    });

    test('clearBreadcrumbs() completes without error', () async {
      await expectLater(noop.clearBreadcrumbs(), completes);
    });

    test('setTag() completes without error', () async {
      await expectLater(noop.setTag('k', 'v'), completes);
    });

    test('removeTag() completes without error', () async {
      await expectLater(noop.removeTag('k'), completes);
    });

    test('dispose() completes without error', () async {
      await expectLater(noop.dispose(), completes);
    });

    test('manager backed by noop submits no reports', () async {
      final mgr = CrashReportingManager(provider: noop);
      await mgr.initialize();
      // Should not throw even though the provider is noop.
      await mgr.reportError(Exception('x'));
      await mgr.reportFatal(Exception('y'));
      await mgr.dispose();
    });
  });
}
