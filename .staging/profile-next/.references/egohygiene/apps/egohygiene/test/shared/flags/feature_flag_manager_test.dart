import 'package:egohygiene/shared/flags/feature_flag.dart';
import 'package:egohygiene/shared/flags/feature_flag_manager.dart';
import 'package:egohygiene/shared/flags/feature_flag_override.dart';
import 'package:egohygiene/shared/flags/feature_flag_provider.dart';
import 'package:egohygiene/shared/flags/feature_flag_state.dart';
import 'package:egohygiene/shared/flags/impl/local_feature_flag_provider.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Test fixtures
// ---------------------------------------------------------------------------

const kStableFlag = FeatureFlag(
  key: 'stable_feature',
  type: FeatureFlagType.stable,
  defaultValue: true,
  description: 'A stable feature enabled for all users.',
);

const kExperimentalFlag = FeatureFlag(
  key: 'experimental_feature',
  type: FeatureFlagType.experimental,
  description: 'An experimental feature disabled by default.',
);

const kBetaFlag = FeatureFlag(
  key: 'beta_feature',
  type: FeatureFlagType.beta,
);

const kDevOnlyFlag = FeatureFlag(
  key: 'dev_only_feature',
  type: FeatureFlagType.developerOnly,
);

const kHiddenFlag = FeatureFlag(
  key: 'hidden_feature',
  type: FeatureFlagType.hidden,
);

const kDeprecatedFlag = FeatureFlag(
  key: 'deprecated_feature',
  type: FeatureFlagType.deprecated,
  defaultValue: true,
  description: 'Deprecated — migrate to stable_feature.',
);

// ---------------------------------------------------------------------------
// Capturing provider that records calls
// ---------------------------------------------------------------------------

class _CapturingProvider implements FeatureFlagProvider {
  _CapturingProvider({Map<String, bool?>? values}) : values = values ?? const {};
  bool initialized = false;
  bool disposed = false;
  final Map<String, bool?> values;

  @override
  String get providerId => 'capturing';

  @override
  Future<void> initialize() async => initialized = true;

  @override
  Future<bool> isEnabled(FeatureFlag flag) async => values[flag.key] ?? flag.defaultValue;

  @override
  Future<bool?> getValue(FeatureFlag flag) async => values[flag.key];

  @override
  Future<void> dispose() async => disposed = true;
}

/// A provider that throws on every call.
class _ThrowingProvider extends _CapturingProvider {
  @override
  Future<bool?> getValue(FeatureFlag flag) async => throw Exception('provider failure');
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── FeatureFlagType ─────────────────────────────────────────────────────

  group('FeatureFlagType', () {
    test('has six variants', () {
      expect(FeatureFlagType.values, hasLength(6));
    });

    test('contains all required variants', () {
      expect(
        FeatureFlagType.values,
        containsAll([
          FeatureFlagType.stable,
          FeatureFlagType.experimental,
          FeatureFlagType.beta,
          FeatureFlagType.developerOnly,
          FeatureFlagType.hidden,
          FeatureFlagType.deprecated,
        ]),
      );
    });
  });

  // ── FeatureFlag ─────────────────────────────────────────────────────────

  group('FeatureFlag', () {
    test('defaultValue is false when not specified', () {
      const flag = FeatureFlag(key: 'my_flag', type: FeatureFlagType.stable);
      expect(flag.defaultValue, isFalse);
    });

    test('description defaults to null', () {
      const flag = FeatureFlag(key: 'my_flag', type: FeatureFlagType.stable);
      expect(flag.description, isNull);
    });

    test('equality is based on key', () {
      const a = FeatureFlag(key: 'flag_a', type: FeatureFlagType.stable);
      const b = FeatureFlag(
        key: 'flag_a',
        type: FeatureFlagType.experimental,
        defaultValue: true,
      );
      expect(a, equals(b));
    });

    test('flags with different keys are not equal', () {
      const a = FeatureFlag(key: 'flag_a', type: FeatureFlagType.stable);
      const b = FeatureFlag(key: 'flag_b', type: FeatureFlagType.stable);
      expect(a, isNot(equals(b)));
    });

    test('toString includes key and type', () {
      expect(kStableFlag.toString(), contains('stable_feature'));
      expect(kStableFlag.toString(), contains('stable'));
    });

    test('toString includes description when present', () {
      expect(kStableFlag.toString(), contains('A stable feature'));
    });

    test('toString omits description when absent', () {
      expect(kBetaFlag.toString(), isNot(contains('description')));
    });
  });

  // ── FeatureFlagState ────────────────────────────────────────────────────

  group('FeatureFlagState', () {
    test('has three variants', () {
      expect(FeatureFlagState.values, hasLength(3));
    });

    test('contains enabled, disabled, and overridden', () {
      expect(
        FeatureFlagState.values,
        containsAll([
          FeatureFlagState.enabled,
          FeatureFlagState.disabled,
          FeatureFlagState.overridden,
        ]),
      );
    });
  });

  // ── FeatureFlagOverride ─────────────────────────────────────────────────

  group('FeatureFlagOverride', () {
    test('stores key and value', () {
      const o = FeatureFlagOverride(key: 'my_flag', value: true);
      expect(o.key, 'my_flag');
      expect(o.value, isTrue);
    });

    test('reason defaults to null', () {
      const o = FeatureFlagOverride(key: 'my_flag', value: false);
      expect(o.reason, isNull);
    });

    test('equality based on key and value', () {
      const a = FeatureFlagOverride(key: 'flag', value: true);
      const b = FeatureFlagOverride(key: 'flag', value: true, reason: 'test');
      expect(a, equals(b));
    });

    test('overrides with same key but different values are not equal', () {
      const a = FeatureFlagOverride(key: 'flag', value: true);
      const b = FeatureFlagOverride(key: 'flag', value: false);
      expect(a, isNot(equals(b)));
    });

    test('toString includes key and value', () {
      const o = FeatureFlagOverride(key: 'ai_flag', value: true);
      expect(o.toString(), contains('ai_flag'));
      expect(o.toString(), contains('true'));
    });

    test('toString includes reason when present', () {
      const o = FeatureFlagOverride(
        key: 'ai_flag',
        value: true,
        reason: 'qa testing',
      );
      expect(o.toString(), contains('qa testing'));
    });
  });

  // ── FeatureFlagManager ──────────────────────────────────────────────────

  group('FeatureFlagManager', () {
    late _CapturingProvider provider;
    late FeatureFlagManager manager;

    setUp(() {
      provider = _CapturingProvider();
      manager = FeatureFlagManager(provider: provider);
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
      // initialized was only set the first time (CapturingProvider booleans don't toggle)
      expect(provider.initialized, isTrue);
    });

    // ── isEnabled — default values ──

    test('isEnabled returns defaultValue when provider has no opinion', () async {
      await manager.initialize();
      expect(await manager.isEnabled(kStableFlag), isTrue);
      expect(await manager.isEnabled(kExperimentalFlag), isFalse);
    });

    test('isEnabled returns flag defaultValue before initialization', () async {
      // No initialize() call — should still degrade to default.
      expect(await manager.isEnabled(kStableFlag), isTrue);
      expect(await manager.isEnabled(kExperimentalFlag), isFalse);
    });

    // ── isEnabled — provider values ──

    test('isEnabled returns provider value when provider has opinion', () async {
      final prov = _CapturingProvider(
        values: {'experimental_feature': true},
      );
      final mgr = FeatureFlagManager(provider: prov);
      await mgr.initialize();
      expect(await mgr.isEnabled(kExperimentalFlag), isTrue);
      await mgr.dispose();
    });

    test('isEnabled returns defaultValue when provider returns null', () async {
      await manager.initialize();
      // provider has no entry for kBetaFlag → falls back to defaultValue=false
      expect(await manager.isEnabled(kBetaFlag), isFalse);
    });

    // ── isEnabled — override priority ──

    test('isEnabled returns override value when override is set', () async {
      await manager.initialize();
      manager.setOverride(
        const FeatureFlagOverride(key: 'experimental_feature', value: true),
      );
      expect(await manager.isEnabled(kExperimentalFlag), isTrue);
    });

    test('override takes priority over provider value', () async {
      final prov = _CapturingProvider(
        values: {'experimental_feature': true},
      );
      final mgr = FeatureFlagManager(provider: prov);
      await mgr.initialize();
      mgr.setOverride(
        const FeatureFlagOverride(key: 'experimental_feature', value: false),
      );
      expect(await mgr.isEnabled(kExperimentalFlag), isFalse);
      await mgr.dispose();
    });

    test('override takes priority over defaultValue', () async {
      await manager.initialize();
      // kStableFlag.defaultValue is true; force it off
      manager.setOverride(
        const FeatureFlagOverride(key: 'stable_feature', value: false),
      );
      expect(await manager.isEnabled(kStableFlag), isFalse);
    });

    // ── evaluate ──

    test('evaluate returns enabled for a flag that is on', () async {
      await manager.initialize();
      expect(await manager.evaluate(kStableFlag), FeatureFlagState.enabled);
    });

    test('evaluate returns disabled for a flag that is off', () async {
      await manager.initialize();
      expect(
        await manager.evaluate(kExperimentalFlag),
        FeatureFlagState.disabled,
      );
    });

    test('evaluate returns overridden when an override is active', () async {
      await manager.initialize();
      manager.setOverride(
        const FeatureFlagOverride(key: 'stable_feature', value: false),
      );
      expect(await manager.evaluate(kStableFlag), FeatureFlagState.overridden);
    });

    // ── setOverride / clearOverride ──

    test('setOverride stores override accessible via overrideFor()', () {
      const o = FeatureFlagOverride(key: 'beta_feature', value: true);
      manager.setOverride(o);
      expect(manager.overrideFor('beta_feature'), o);
    });

    test('clearOverride removes the override', () async {
      await manager.initialize();
      manager.setOverride(
        const FeatureFlagOverride(key: 'experimental_feature', value: true),
      );
      manager.clearOverride('experimental_feature');
      expect(await manager.isEnabled(kExperimentalFlag), isFalse);
      expect(manager.overrideFor('experimental_feature'), isNull);
    });

    test('clearOverride is a no-op when no override exists', () {
      expect(() => manager.clearOverride('nonexistent'), returnsNormally);
    });

    test('clearAllOverrides removes every override', () async {
      await manager.initialize();
      manager.setOverride(
        const FeatureFlagOverride(key: 'stable_feature', value: false),
      );
      manager.setOverride(
        const FeatureFlagOverride(key: 'experimental_feature', value: true),
      );
      manager.clearAllOverrides();
      expect(manager.overrides, isEmpty);
      expect(await manager.isEnabled(kStableFlag), isTrue);
      expect(await manager.isEnabled(kExperimentalFlag), isFalse);
    });

    test('overrides returns unmodifiable map', () {
      manager.setOverride(
        const FeatureFlagOverride(key: 'stable_feature', value: false),
      );
      expect(
        () => manager.overrides['new_key'] = const FeatureFlagOverride(key: 'new_key', value: true),
        throwsUnsupportedError,
      );
    });

    // ── resilience ──

    test('a throwing provider does not propagate exceptions to callers', () async {
      final throwing = _ThrowingProvider();
      final mgr = FeatureFlagManager(provider: throwing);
      await mgr.initialize();
      await expectLater(mgr.isEnabled(kExperimentalFlag), completes);
      // Should fall back to defaultValue (false)
      expect(await mgr.isEnabled(kExperimentalFlag), isFalse);
      await mgr.dispose();
    });

    // ── dispose ──

    test('dispose() calls provider.dispose()', () async {
      await manager.initialize();
      await manager.dispose();
      expect(provider.disposed, isTrue);
    });

    // ── all flag types ──

    test('stable flag is enabled by default', () async {
      await manager.initialize();
      expect(await manager.isEnabled(kStableFlag), isTrue);
    });

    test('experimental flag is disabled by default', () async {
      await manager.initialize();
      expect(await manager.isEnabled(kExperimentalFlag), isFalse);
    });

    test('beta flag is disabled by default', () async {
      await manager.initialize();
      expect(await manager.isEnabled(kBetaFlag), isFalse);
    });

    test('developerOnly flag is disabled by default', () async {
      await manager.initialize();
      expect(await manager.isEnabled(kDevOnlyFlag), isFalse);
    });

    test('hidden flag is disabled by default', () async {
      await manager.initialize();
      expect(await manager.isEnabled(kHiddenFlag), isFalse);
    });

    test('deprecated flag respects its defaultValue', () async {
      await manager.initialize();
      expect(await manager.isEnabled(kDeprecatedFlag), isTrue);
    });
  });

  // ── LocalFeatureFlagProvider ────────────────────────────────────────────

  group('LocalFeatureFlagProvider', () {
    test('providerId is "local"', () {
      expect(const LocalFeatureFlagProvider().providerId, 'local');
    });

    test('initialize() completes without error', () async {
      await expectLater(
        const LocalFeatureFlagProvider().initialize(),
        completes,
      );
    });

    test('dispose() completes without error', () async {
      await expectLater(
        const LocalFeatureFlagProvider().dispose(),
        completes,
      );
    });

    test('isEnabled returns flag defaultValue when no staticValues supplied', () async {
      const prov = LocalFeatureFlagProvider();
      expect(await prov.isEnabled(kStableFlag), isTrue);
      expect(await prov.isEnabled(kExperimentalFlag), isFalse);
    });

    test('isEnabled returns staticValues entry when present', () async {
      const prov = LocalFeatureFlagProvider(
        staticValues: {'experimental_feature': true},
      );
      expect(await prov.isEnabled(kExperimentalFlag), isTrue);
    });

    test('getValue returns null when flag not in staticValues', () async {
      const prov = LocalFeatureFlagProvider();
      expect(await prov.getValue(kStableFlag), isNull);
    });

    test('getValue returns value when flag is in staticValues', () async {
      const prov = LocalFeatureFlagProvider(
        staticValues: {'stable_feature': false},
      );
      expect(await prov.getValue(kStableFlag), isFalse);
    });
  });
}
