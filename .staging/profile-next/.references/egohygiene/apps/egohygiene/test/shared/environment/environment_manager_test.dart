import 'package:egohygiene/shared/environment/environment.dart';
import 'package:egohygiene/shared/environment/environment_configuration.dart';
import 'package:egohygiene/shared/environment/environment_manager.dart';
import 'package:egohygiene/shared/environment/environment_provider.dart';
import 'package:egohygiene/shared/environment/impl/local_environment_provider.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

class _CapturingProvider implements EnvironmentProvider {
  _CapturingProvider({this.configuration, this.shouldThrow = false});
  bool initialized = false;
  bool disposed = false;
  final EnvironmentConfiguration? configuration;
  bool shouldThrow = false;

  @override
  String get providerId => 'capturing';

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<EnvironmentConfiguration> loadConfiguration() async {
    if (shouldThrow) throw Exception('provider failure');
    return configuration ?? EnvironmentConfiguration.defaults(AppEnvironment.development);
  }

  @override
  Future<void> dispose() async => disposed = true;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── AppEnvironment ─────────────────────────────────────────────────────

  group('AppEnvironment', () {
    test('has five variants', () {
      expect(AppEnvironment.values, hasLength(5));
    });

    test('contains all required variants', () {
      expect(
        AppEnvironment.values,
        containsAll([
          AppEnvironment.development,
          AppEnvironment.staging,
          AppEnvironment.production,
          AppEnvironment.testing,
          AppEnvironment.demo,
        ]),
      );
    });
  });

  // ── EnvironmentConfiguration ────────────────────────────────────────────

  group('EnvironmentConfiguration', () {
    // ── defaults ──

    group('defaults', () {
      test('development has logging and debugging enabled', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.development);
        expect(config.environment, AppEnvironment.development);
        expect(config.isLoggingEnabled, isTrue);
        expect(config.isDebuggingEnabled, isTrue);
        expect(config.isAnalyticsEnabled, isFalse);
        expect(config.isCrashReportingEnabled, isFalse);
        expect(config.useMockAiProvider, isFalse);
        expect(config.useRemoteFeatureFlags, isFalse);
      });

      test('staging has logging and crash reporting enabled', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.staging);
        expect(config.environment, AppEnvironment.staging);
        expect(config.isLoggingEnabled, isTrue);
        expect(config.isCrashReportingEnabled, isTrue);
        expect(config.isDebuggingEnabled, isFalse);
        expect(config.isAnalyticsEnabled, isFalse);
        expect(config.useRemoteFeatureFlags, isTrue);
      });

      test('production has analytics and crash reporting enabled', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.production);
        expect(config.environment, AppEnvironment.production);
        expect(config.isAnalyticsEnabled, isTrue);
        expect(config.isCrashReportingEnabled, isTrue);
        expect(config.isLoggingEnabled, isFalse);
        expect(config.isDebuggingEnabled, isFalse);
        expect(config.useRemoteFeatureFlags, isTrue);
      });

      test('testing has debug enabled and most side-effects disabled', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.testing);
        expect(config.environment, AppEnvironment.testing);
        expect(config.isDebuggingEnabled, isTrue);
        expect(config.isSyncEnabled, isFalse);
        expect(config.isAiEnabled, isFalse);
        expect(config.useMockAiProvider, isTrue);
        expect(config.isAnalyticsEnabled, isFalse);
        expect(config.isCrashReportingEnabled, isFalse);
        expect(config.useRemoteFeatureFlags, isFalse);
      });

      test('demo has AI with mock provider and no sync or analytics', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.demo);
        expect(config.environment, AppEnvironment.demo);
        expect(config.isAiEnabled, isTrue);
        expect(config.useMockAiProvider, isTrue);
        expect(config.isSyncEnabled, isFalse);
        expect(config.isAnalyticsEnabled, isFalse);
        expect(config.isCrashReportingEnabled, isFalse);
        expect(config.isDebuggingEnabled, isFalse);
      });
    });

    // ── copyWith ──

    group('copyWith', () {
      test('returns new instance with updated field', () {
        final base = EnvironmentConfiguration.defaults(AppEnvironment.development);
        final updated = base.copyWith(isAnalyticsEnabled: true);
        expect(updated.isAnalyticsEnabled, isTrue);
        expect(updated.environment, base.environment);
        expect(updated.isLoggingEnabled, base.isLoggingEnabled);
      });

      test('original is not mutated', () {
        final base = EnvironmentConfiguration.defaults(AppEnvironment.development);
        base.copyWith(isAnalyticsEnabled: true);
        expect(base.isAnalyticsEnabled, isFalse);
      });

      test('all fields can be overridden', () {
        final config =
            EnvironmentConfiguration.defaults(
              AppEnvironment.production,
            ).copyWith(
              environment: AppEnvironment.staging,
              isLoggingEnabled: true,
              isAnalyticsEnabled: false,
              isCrashReportingEnabled: false,
              isDebuggingEnabled: true,
              isSyncEnabled: false,
              isAiEnabled: false,
              useMockAiProvider: true,
              useRemoteFeatureFlags: false,
              metadata: const {'key': 'value'},
            );

        expect(config.environment, AppEnvironment.staging);
        expect(config.isLoggingEnabled, isTrue);
        expect(config.isAnalyticsEnabled, isFalse);
        expect(config.isCrashReportingEnabled, isFalse);
        expect(config.isDebuggingEnabled, isTrue);
        expect(config.isSyncEnabled, isFalse);
        expect(config.isAiEnabled, isFalse);
        expect(config.useMockAiProvider, isTrue);
        expect(config.useRemoteFeatureFlags, isFalse);
        expect(config.metadata, {'key': 'value'});
      });
    });

    // ── derived helpers ──

    group('derived helpers', () {
      test('isDevelopment is true for development environment', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.development);
        expect(config.isDevelopment, isTrue);
        expect(config.isProduction, isFalse);
        expect(config.isStaging, isFalse);
        expect(config.isTesting, isFalse);
        expect(config.isDemo, isFalse);
      });

      test('isProduction is true for production environment', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.production);
        expect(config.isProduction, isTrue);
        expect(config.isDevelopment, isFalse);
      });

      test('isStaging is true for staging environment', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.staging);
        expect(config.isStaging, isTrue);
        expect(config.isDevelopment, isFalse);
      });

      test('isTesting is true for testing environment', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.testing);
        expect(config.isTesting, isTrue);
        expect(config.isDevelopment, isFalse);
      });

      test('isDemo is true for demo environment', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.demo);
        expect(config.isDemo, isTrue);
        expect(config.isDevelopment, isFalse);
      });
    });

    // ── equality ──

    group('equality', () {
      test('two configs with the same values are equal', () {
        final a = EnvironmentConfiguration.defaults(AppEnvironment.development);
        final b = EnvironmentConfiguration.defaults(AppEnvironment.development);
        expect(a, equals(b));
      });

      test('configs with different environments are not equal', () {
        final a = EnvironmentConfiguration.defaults(AppEnvironment.development);
        final b = EnvironmentConfiguration.defaults(AppEnvironment.production);
        expect(a, isNot(equals(b)));
      });

      test('configs with different metadata are not equal', () {
        final a = EnvironmentConfiguration.defaults(AppEnvironment.development).copyWith(metadata: const {'key': 'a'});
        final b = EnvironmentConfiguration.defaults(AppEnvironment.development).copyWith(metadata: const {'key': 'b'});
        expect(a, isNot(equals(b)));
      });

      test('configs with same metadata are equal', () {
        final a = EnvironmentConfiguration.defaults(
          AppEnvironment.development,
        ).copyWith(metadata: const {'key': 'value'});
        final b = EnvironmentConfiguration.defaults(
          AppEnvironment.development,
        ).copyWith(metadata: const {'key': 'value'});
        expect(a, equals(b));
      });

      test('hashCode is consistent with equality', () {
        final a = EnvironmentConfiguration.defaults(AppEnvironment.development);
        final b = EnvironmentConfiguration.defaults(AppEnvironment.development);
        expect(a.hashCode, b.hashCode);
      });
    });

    // ── toString ──

    group('toString', () {
      test('includes environment name', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.production);
        expect(config.toString(), contains('production'));
      });

      test('includes key field values', () {
        final config = EnvironmentConfiguration.defaults(AppEnvironment.development);
        final str = config.toString();
        expect(str, contains('logging=true'));
        expect(str, contains('debug=true'));
      });
    });
  });

  // ── EnvironmentManager ──────────────────────────────────────────────────

  group('EnvironmentManager', () {
    late _CapturingProvider provider;
    late EnvironmentManager manager;

    setUp(() {
      provider = _CapturingProvider();
      manager = EnvironmentManager(provider: provider);
    });

    tearDown(() async => manager.dispose());

    // ── initialization ──

    test('initialize() calls provider.initialize()', () async {
      await manager.initialize();
      expect(provider.initialized, isTrue);
    });

    test('initialize() loads configuration from provider', () async {
      final config = EnvironmentConfiguration.defaults(AppEnvironment.staging);
      final prov = _CapturingProvider(configuration: config);
      final mgr = EnvironmentManager(provider: prov);
      await mgr.initialize();
      expect(mgr.configuration, config);
      await mgr.dispose();
    });

    test('calling initialize() twice is a no-op', () async {
      await manager.initialize();
      await manager.initialize();
      expect(provider.initialized, isTrue);
    });

    // ── configuration before initialization ──

    test('configuration falls back to development defaults before init', () {
      expect(
        manager.configuration.environment,
        AppEnvironment.development,
      );
    });

    // ── environment accessors ──

    test('isDevelopment is true when environment is development', () async {
      await manager.initialize();
      // default provider returns development config
      expect(manager.isDevelopment, isTrue);
      expect(manager.isStaging, isFalse);
      expect(manager.isProduction, isFalse);
      expect(manager.isTesting, isFalse);
      expect(manager.isDemo, isFalse);
    });

    test('isProduction is true when environment is production', () async {
      final config = EnvironmentConfiguration.defaults(AppEnvironment.production);
      final prov = _CapturingProvider(configuration: config);
      final mgr = EnvironmentManager(provider: prov);
      await mgr.initialize();
      expect(mgr.isProduction, isTrue);
      expect(mgr.isDevelopment, isFalse);
      await mgr.dispose();
    });

    test('isStaging is true when environment is staging', () async {
      final config = EnvironmentConfiguration.defaults(AppEnvironment.staging);
      final prov = _CapturingProvider(configuration: config);
      final mgr = EnvironmentManager(provider: prov);
      await mgr.initialize();
      expect(mgr.isStaging, isTrue);
      await mgr.dispose();
    });

    test('isTesting is true when environment is testing', () async {
      final config = EnvironmentConfiguration.defaults(AppEnvironment.testing);
      final prov = _CapturingProvider(configuration: config);
      final mgr = EnvironmentManager(provider: prov);
      await mgr.initialize();
      expect(mgr.isTesting, isTrue);
      await mgr.dispose();
    });

    test('isDemo is true when environment is demo', () async {
      final config = EnvironmentConfiguration.defaults(AppEnvironment.demo);
      final prov = _CapturingProvider(configuration: config);
      final mgr = EnvironmentManager(provider: prov);
      await mgr.initialize();
      expect(mgr.isDemo, isTrue);
      await mgr.dispose();
    });

    // ── resilience ──

    test('a throwing provider falls back to development defaults', () async {
      final throwing = _CapturingProvider(shouldThrow: true);
      final mgr = EnvironmentManager(provider: throwing);
      await expectLater(mgr.initialize(), completes);
      expect(mgr.configuration.environment, AppEnvironment.development);
      await mgr.dispose();
    });

    // ── dispose ──

    test('dispose() calls provider.dispose()', () async {
      await manager.initialize();
      await manager.dispose();
      expect(provider.disposed, isTrue);
    });
  });

  // ── LocalEnvironmentProvider ────────────────────────────────────────────

  group('LocalEnvironmentProvider', () {
    test('providerId is "local"', () {
      expect(const LocalEnvironmentProvider().providerId, 'local');
    });

    test('initialize() completes without error', () async {
      await expectLater(
        const LocalEnvironmentProvider().initialize(),
        completes,
      );
    });

    test('dispose() completes without error', () async {
      await expectLater(
        const LocalEnvironmentProvider().dispose(),
        completes,
      );
    });

    test('returns development defaults when no arguments supplied', () async {
      const prov = LocalEnvironmentProvider();
      final config = await prov.loadConfiguration();
      expect(config.environment, AppEnvironment.development);
    });

    test('returns defaults for supplied environment', () async {
      const prov = LocalEnvironmentProvider(
        environment: AppEnvironment.production,
      );
      final config = await prov.loadConfiguration();
      expect(config.environment, AppEnvironment.production);
      expect(config.isAnalyticsEnabled, isTrue);
    });

    test('returns pinned configuration when supplied', () async {
      final pinned = EnvironmentConfiguration.defaults(AppEnvironment.testing);
      final prov = LocalEnvironmentProvider(configuration: pinned);
      final config = await prov.loadConfiguration();
      expect(config, pinned);
    });

    test('pinned configuration takes precedence over environment', () async {
      final pinned = EnvironmentConfiguration.defaults(AppEnvironment.testing);
      final prov = LocalEnvironmentProvider(
        configuration: pinned,
        environment: AppEnvironment.production,
      );
      final config = await prov.loadConfiguration();
      expect(config.environment, AppEnvironment.testing);
    });
  });
}
