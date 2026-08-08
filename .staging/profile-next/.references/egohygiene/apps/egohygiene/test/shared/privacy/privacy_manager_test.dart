import 'package:egohygiene/shared/privacy/consent.dart';
import 'package:egohygiene/shared/privacy/consent_manager.dart';
import 'package:egohygiene/shared/privacy/consent_store.dart';
import 'package:egohygiene/shared/privacy/data_retention_rule.dart';
import 'package:egohygiene/shared/privacy/data_visibility_rule.dart';
import 'package:egohygiene/shared/privacy/impl/in_memory_consent_store.dart';
import 'package:egohygiene/shared/privacy/privacy_manager.dart';
import 'package:egohygiene/shared/privacy/privacy_mode.dart';
import 'package:egohygiene/shared/privacy/privacy_policy.dart';
import 'package:egohygiene/shared/privacy/privacy_policy_registry.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

ConsentManager _makeConsentManager() => ConsentManager(store: InMemoryConsentStore());

PrivacyManager _makePrivacyManager({PrivacyMode mode = PrivacyMode.localFirst}) => PrivacyManager(
  consentManager: _makeConsentManager(),
  registry: PrivacyPolicyRegistry(),
  mode: mode,
);

// ---------------------------------------------------------------------------
// ConsentScope
// ---------------------------------------------------------------------------

void main() {
  group('ConsentScope', () {
    test('has expected values', () {
      expect(ConsentScope.values, contains(ConsentScope.crashReporting));
      expect(ConsentScope.values, contains(ConsentScope.analytics));
      expect(ConsentScope.values, contains(ConsentScope.aiProvider));
      expect(ConsentScope.values, contains(ConsentScope.therapistSharing));
      expect(ConsentScope.values, contains(ConsentScope.cloudSync));
    });
  });

  // ── ConsentStatus ──────────────────────────────────────────────────────────

  group('ConsentStatus', () {
    test('has granted, denied, pending', () {
      expect(ConsentStatus.values, hasLength(3));
      expect(
        ConsentStatus.values,
        containsAll([
          ConsentStatus.granted,
          ConsentStatus.denied,
          ConsentStatus.pending,
        ]),
      );
    });
  });

  // ── ConsentEntry ──────────────────────────────────────────────────────────

  group('ConsentEntry', () {
    final now = DateTime(2025);

    test('isGranted is true when status is granted', () {
      final entry = ConsentEntry(
        scope: ConsentScope.analytics,
        status: ConsentStatus.granted,
        decidedAt: now,
      );
      expect(entry.isGranted, isTrue);
      expect(entry.isDenied, isFalse);
      expect(entry.isPending, isFalse);
    });

    test('isDenied is true when status is denied', () {
      final entry = ConsentEntry(
        scope: ConsentScope.analytics,
        status: ConsentStatus.denied,
        decidedAt: now,
      );
      expect(entry.isDenied, isTrue);
      expect(entry.isGranted, isFalse);
    });

    test('isPending is true when status is pending', () {
      final entry = ConsentEntry(
        scope: ConsentScope.analytics,
        status: ConsentStatus.pending,
        decidedAt: now,
      );
      expect(entry.isPending, isTrue);
    });

    test('copyWith replaces fields', () {
      final entry = ConsentEntry(
        scope: ConsentScope.analytics,
        status: ConsentStatus.granted,
        decidedAt: now,
      );
      final updated = entry.copyWith(status: ConsentStatus.denied);
      expect(updated.scope, ConsentScope.analytics);
      expect(updated.status, ConsentStatus.denied);
      expect(updated.decidedAt, now);
    });

    test('equality based on scope and status', () {
      final a = ConsentEntry(
        scope: ConsentScope.analytics,
        status: ConsentStatus.granted,
        decidedAt: DateTime(2024),
      );
      final b = ConsentEntry(
        scope: ConsentScope.analytics,
        status: ConsentStatus.granted,
        decidedAt: DateTime(2025),
      );
      expect(a, equals(b));
    });

    test('toString includes scope and status', () {
      final entry = ConsentEntry(
        scope: ConsentScope.analytics,
        status: ConsentStatus.granted,
        decidedAt: now,
      );
      expect(entry.toString(), contains('analytics'));
      expect(entry.toString(), contains('granted'));
    });
  });

  // ── InMemoryConsentStore ──────────────────────────────────────────────────

  group('InMemoryConsentStore', () {
    late InMemoryConsentStore store;

    setUp(() {
      store = InMemoryConsentStore();
    });

    test('init() completes without error', () async {
      await expectLater(store.init(), completes);
    });

    test('save() and findByScope() round-trip', () async {
      final entry = ConsentEntry(
        scope: ConsentScope.crashReporting,
        status: ConsentStatus.granted,
        decidedAt: DateTime.now(),
      );
      await store.save(entry);
      final found = await store.findByScope(ConsentScope.crashReporting);
      expect(found, isNotNull);
      expect(found!.scope, ConsentScope.crashReporting);
      expect(found.isGranted, isTrue);
    });

    test('findByScope() returns null for unknown scope', () async {
      final found = await store.findByScope(ConsentScope.analytics);
      expect(found, isNull);
    });

    test('save() overwrites an existing entry', () async {
      final granted = ConsentEntry(
        scope: ConsentScope.analytics,
        status: ConsentStatus.granted,
        decidedAt: DateTime.now(),
      );
      final denied = ConsentEntry(
        scope: ConsentScope.analytics,
        status: ConsentStatus.denied,
        decidedAt: DateTime.now(),
      );
      await store.save(granted);
      await store.save(denied);
      final found = await store.findByScope(ConsentScope.analytics);
      expect(found!.isDenied, isTrue);
    });

    test('findAll() returns all saved entries', () async {
      await store.save(
        ConsentEntry(
          scope: ConsentScope.analytics,
          status: ConsentStatus.granted,
          decidedAt: DateTime.now(),
        ),
      );
      await store.save(
        ConsentEntry(
          scope: ConsentScope.crashReporting,
          status: ConsentStatus.denied,
          decidedAt: DateTime.now(),
        ),
      );
      final all = await store.findAll();
      expect(all, hasLength(2));
    });

    test('deleteByScope() removes the entry', () async {
      await store.save(
        ConsentEntry(
          scope: ConsentScope.analytics,
          status: ConsentStatus.granted,
          decidedAt: DateTime.now(),
        ),
      );
      await store.deleteByScope(ConsentScope.analytics);
      final found = await store.findByScope(ConsentScope.analytics);
      expect(found, isNull);
    });

    test('deleteByScope() is a no-op for unknown scope', () async {
      await expectLater(
        store.deleteByScope(ConsentScope.cloudSync),
        completes,
      );
    });

    test('clear() removes all entries', () async {
      await store.save(
        ConsentEntry(
          scope: ConsentScope.analytics,
          status: ConsentStatus.granted,
          decidedAt: DateTime.now(),
        ),
      );
      await store.clear();
      final all = await store.findAll();
      expect(all, isEmpty);
    });
  });

  // ── ConsentManager ────────────────────────────────────────────────────────

  group('ConsentManager', () {
    late ConsentStore store;
    late ConsentManager manager;

    setUp(() {
      store = InMemoryConsentStore();
      manager = ConsentManager(store: store);
    });

    tearDown(() async => manager.dispose());

    test('initialize() completes without error', () async {
      await expectLater(manager.initialize(), completes);
    });

    test('calling initialize() twice is a no-op', () async {
      await manager.initialize();
      await expectLater(manager.initialize(), completes);
    });

    test('hasConsent() returns false before any decision', () async {
      await manager.initialize();
      expect(await manager.hasConsent(ConsentScope.analytics), isFalse);
    });

    test('statusOf() returns pending before any decision', () async {
      await manager.initialize();
      expect(
        await manager.statusOf(ConsentScope.analytics),
        ConsentStatus.pending,
      );
    });

    test('grant() records a granted entry', () async {
      await manager.initialize();
      await manager.grant(ConsentScope.analytics);
      expect(await manager.hasConsent(ConsentScope.analytics), isTrue);
      expect(
        await manager.statusOf(ConsentScope.analytics),
        ConsentStatus.granted,
      );
    });

    test('deny() records a denied entry', () async {
      await manager.initialize();
      await manager.deny(ConsentScope.analytics);
      expect(await manager.hasConsent(ConsentScope.analytics), isFalse);
      expect(
        await manager.statusOf(ConsentScope.analytics),
        ConsentStatus.denied,
      );
    });

    test('revoke() removes a granted entry', () async {
      await manager.initialize();
      await manager.grant(ConsentScope.analytics);
      await manager.revoke(ConsentScope.analytics);
      expect(await manager.hasConsent(ConsentScope.analytics), isFalse);
      expect(
        await manager.statusOf(ConsentScope.analytics),
        ConsentStatus.pending,
      );
    });

    test('revokeAll() removes all entries', () async {
      await manager.initialize();
      await manager.grant(ConsentScope.analytics);
      await manager.grant(ConsentScope.crashReporting);
      await manager.revokeAll();
      final entries = await manager.allEntries();
      expect(entries, isEmpty);
    });

    test('entryFor() returns null when no decision recorded', () async {
      await manager.initialize();
      expect(await manager.entryFor(ConsentScope.cloudSync), isNull);
    });

    test('entryFor() returns the stored entry', () async {
      await manager.initialize();
      await manager.grant(ConsentScope.cloudSync, version: '1.0');
      final entry = await manager.entryFor(ConsentScope.cloudSync);
      expect(entry, isNotNull);
      expect(entry!.version, '1.0');
    });

    test('grant() forwards version and metadata', () async {
      await manager.initialize();
      await manager.grant(
        ConsentScope.aiProvider,
        version: '2.1',
        metadata: {'locale': 'en'},
      );
      final entry = await manager.entryFor(ConsentScope.aiProvider);
      expect(entry!.version, '2.1');
      expect(entry.metadata['locale'], 'en');
    });

    test('allEntries() returns all recorded entries', () async {
      await manager.initialize();
      await manager.grant(ConsentScope.analytics);
      await manager.deny(ConsentScope.crashReporting);
      final entries = await manager.allEntries();
      expect(entries, hasLength(2));
    });
  });

  // ── DataVisibilityRule ────────────────────────────────────────────────────

  group('DataVisibilityRule', () {
    test('equality based on dataCategory and level', () {
      const a = DataVisibilityRule(
        dataCategory: 'reflection_content',
        level: VisibilityLevel.localOnly,
      );
      const b = DataVisibilityRule(
        dataCategory: 'reflection_content',
        level: VisibilityLevel.localOnly,
      );
      expect(a, equals(b));
    });

    test('toString includes dataCategory and level', () {
      const rule = DataVisibilityRule(
        dataCategory: 'mood_score',
        level: VisibilityLevel.sharedWithTherapist,
      );
      expect(rule.toString(), contains('mood_score'));
      expect(rule.toString(), contains('sharedWithTherapist'));
    });
  });

  // ── DataRetentionRule ─────────────────────────────────────────────────────

  group('DataRetentionRule', () {
    test('keepForever policy does not require retentionDays', () {
      const rule = DataRetentionRule(
        dataCategory: 'reflection_content',
        policy: RetentionPolicy.keepForever,
      );
      expect(rule.retentionDays, isNull);
    });

    test('deleteAfterDays requires retentionDays', () {
      // Should not throw.
      const rule = DataRetentionRule(
        dataCategory: 'crash_report',
        policy: RetentionPolicy.deleteAfterDays,
        retentionDays: 90,
      );
      expect(rule.retentionDays, 90);
    });

    test('toString includes retentionDays when set', () {
      const rule = DataRetentionRule(
        dataCategory: 'crash_report',
        policy: RetentionPolicy.deleteAfterDays,
        retentionDays: 30,
      );
      expect(rule.toString(), contains('30'));
    });

    test('equality based on dataCategory and policy', () {
      const a = DataRetentionRule(
        dataCategory: 'mood_score',
        policy: RetentionPolicy.keepForever,
      );
      const b = DataRetentionRule(
        dataCategory: 'mood_score',
        policy: RetentionPolicy.keepForever,
      );
      expect(a, equals(b));
    });
  });

  // ── PrivacyMode ───────────────────────────────────────────────────────────

  group('PrivacyMode', () {
    test('has localFirst, standard, enhanced', () {
      expect(PrivacyMode.values, hasLength(3));
      expect(PrivacyMode.values, contains(PrivacyMode.localFirst));
      expect(PrivacyMode.values, contains(PrivacyMode.standard));
      expect(PrivacyMode.values, contains(PrivacyMode.enhanced));
    });
  });

  // ── PrivacyPolicy ─────────────────────────────────────────────────────────

  group('PrivacyPolicy', () {
    test('equality based on featureId', () {
      const a = PrivacyPolicy(featureId: 'reflection', displayName: 'A');
      const b = PrivacyPolicy(featureId: 'reflection', displayName: 'B');
      expect(a, equals(b));
    });

    test('toString includes featureId and displayName', () {
      const policy = PrivacyPolicy(
        featureId: 'reflection',
        displayName: 'Reflection',
      );
      expect(policy.toString(), contains('reflection'));
      expect(policy.toString(), contains('Reflection'));
    });
  });

  // ── PrivacyPolicyRegistry ─────────────────────────────────────────────────

  group('PrivacyPolicyRegistry', () {
    test('starts empty', () {
      final registry = PrivacyPolicyRegistry();
      expect(registry.count, 0);
      expect(registry.all, isEmpty);
    });

    test('register() adds a policy', () {
      final registry = PrivacyPolicyRegistry();
      const policy = PrivacyPolicy(
        featureId: 'reflection',
        displayName: 'Reflection',
      );
      registry.register(policy);
      expect(registry.count, 1);
      expect(registry.hasPolicy('reflection'), isTrue);
    });

    test('policyFor() returns registered policy', () {
      final registry = PrivacyPolicyRegistry();
      const policy = PrivacyPolicy(
        featureId: 'reflection',
        displayName: 'Reflection',
      );
      registry.register(policy);
      expect(registry.policyFor('reflection'), policy);
    });

    test('policyFor() returns null for unknown featureId', () {
      final registry = PrivacyPolicyRegistry();
      expect(registry.policyFor('unknown'), isNull);
    });

    test('register() replaces an existing policy', () {
      final registry = PrivacyPolicyRegistry();
      registry.register(
        const PrivacyPolicy(featureId: 'reflection', displayName: 'Old'),
      );
      registry.register(
        const PrivacyPolicy(featureId: 'reflection', displayName: 'New'),
      );
      expect(registry.policyFor('reflection')!.displayName, 'New');
      expect(registry.count, 1);
    });

    test('registerAll() adds multiple policies', () {
      final registry = PrivacyPolicyRegistry();
      registry.registerAll([
        const PrivacyPolicy(featureId: 'reflection', displayName: 'R'),
        const PrivacyPolicy(featureId: 'conversation', displayName: 'C'),
      ]);
      expect(registry.count, 2);
    });

    test('constructor accepts initial policies', () {
      final registry = PrivacyPolicyRegistry(
        policies: [
          const PrivacyPolicy(featureId: 'reflection', displayName: 'R'),
        ],
      );
      expect(registry.count, 1);
    });
  });

  // ── PrivacyManager ────────────────────────────────────────────────────────

  group('PrivacyManager', () {
    late PrivacyManager manager;

    setUp(() {
      manager = _makePrivacyManager();
    });

    tearDown(() async => manager.dispose());

    // ── initialization ──

    test('initialize() completes without error', () async {
      await expectLater(manager.initialize(), completes);
    });

    test('calling initialize() twice is a no-op', () async {
      await manager.initialize();
      await expectLater(manager.initialize(), completes);
    });

    // ── mode ──

    test('default mode is localFirst', () {
      expect(manager.mode, PrivacyMode.localFirst);
    });

    test('setMode() changes the active mode', () {
      manager.setMode(PrivacyMode.standard);
      expect(manager.mode, PrivacyMode.standard);
    });

    // ── consent delegation ──

    test('hasConsent() returns false before any grant', () async {
      await manager.initialize();
      expect(await manager.hasConsent(ConsentScope.analytics), isFalse);
    });

    test('grant() makes hasConsent() return true', () async {
      await manager.initialize();
      await manager.grant(ConsentScope.analytics);
      expect(await manager.hasConsent(ConsentScope.analytics), isTrue);
    });

    test('deny() makes hasConsent() return false', () async {
      await manager.initialize();
      await manager.deny(ConsentScope.analytics);
      expect(await manager.hasConsent(ConsentScope.analytics), isFalse);
    });

    test('revoke() removes consent', () async {
      await manager.initialize();
      await manager.grant(ConsentScope.analytics);
      await manager.revoke(ConsentScope.analytics);
      expect(await manager.hasConsent(ConsentScope.analytics), isFalse);
    });

    test('revokeAll() removes all consent entries', () async {
      await manager.initialize();
      await manager.grant(ConsentScope.analytics);
      await manager.grant(ConsentScope.crashReporting);
      await manager.revokeAll();
      final entries = await manager.allEntries();
      expect(entries, isEmpty);
    });

    test('statusOf() returns pending before any decision', () async {
      await manager.initialize();
      expect(
        await manager.statusOf(ConsentScope.cloudSync),
        ConsentStatus.pending,
      );
    });

    // ── policy registration ──

    test('registerPolicy() and policyFor() round-trip', () {
      const policy = PrivacyPolicy(
        featureId: 'reflection',
        displayName: 'Reflection',
      );
      manager.registerPolicy(policy);
      expect(manager.policyFor('reflection'), policy);
    });

    test('policyFor() returns null for unregistered feature', () {
      expect(manager.policyFor('unknown'), isNull);
    });

    // ── isFeaturePermitted ──

    test('isFeaturePermitted() returns true for unregistered feature', () async {
      await manager.initialize();
      expect(await manager.isFeaturePermitted('unknown'), isTrue);
    });

    test('isFeaturePermitted() returns true for policy with no required consents', () async {
      await manager.initialize();
      manager.registerPolicy(
        const PrivacyPolicy(
          featureId: 'reflection',
          displayName: 'Reflection',
        ),
      );
      expect(await manager.isFeaturePermitted('reflection'), isTrue);
    });

    test('isFeaturePermitted() returns false when required consent is missing', () async {
      await manager.initialize();
      manager.registerPolicy(
        const PrivacyPolicy(
          featureId: 'ai_chat',
          displayName: 'AI Chat',
          requiredConsents: [ConsentScope.aiProvider],
        ),
      );
      expect(await manager.isFeaturePermitted('ai_chat'), isFalse);
    });

    test('isFeaturePermitted() returns true after required consent is granted', () async {
      await manager.initialize();
      manager.registerPolicy(
        const PrivacyPolicy(
          featureId: 'ai_chat',
          displayName: 'AI Chat',
          requiredConsents: [ConsentScope.aiProvider],
        ),
      );
      await manager.grant(ConsentScope.aiProvider);
      expect(await manager.isFeaturePermitted('ai_chat'), isTrue);
    });

    test('isFeaturePermitted() returns false when any required consent is missing', () async {
      await manager.initialize();
      manager.registerPolicy(
        const PrivacyPolicy(
          featureId: 'therapist_sync',
          displayName: 'Therapist Sync',
          requiredConsents: [
            ConsentScope.therapistSharing,
            ConsentScope.cloudSync,
          ],
        ),
      );
      await manager.grant(ConsentScope.therapistSharing);
      // cloudSync not granted → should still be false
      expect(await manager.isFeaturePermitted('therapist_sync'), isFalse);
    });

    // ── data rules ──

    test('visibilityRulesFor() returns empty list for unregistered feature', () {
      expect(manager.visibilityRulesFor('unknown'), isEmpty);
    });

    test('visibilityRulesFor() returns rules from registered policy', () {
      manager.registerPolicy(
        const PrivacyPolicy(
          featureId: 'reflection',
          displayName: 'Reflection',
          visibilityRules: [
            DataVisibilityRule(
              dataCategory: 'reflection_content',
              level: VisibilityLevel.localOnly,
            ),
          ],
        ),
      );
      final rules = manager.visibilityRulesFor('reflection');
      expect(rules, hasLength(1));
      expect(rules.first.dataCategory, 'reflection_content');
      expect(rules.first.level, VisibilityLevel.localOnly);
    });

    test('retentionRulesFor() returns empty list for unregistered feature', () {
      expect(manager.retentionRulesFor('unknown'), isEmpty);
    });

    test('retentionRulesFor() returns rules from registered policy', () {
      manager.registerPolicy(
        const PrivacyPolicy(
          featureId: 'reflection',
          displayName: 'Reflection',
          retentionRules: [
            DataRetentionRule(
              dataCategory: 'reflection_content',
              policy: RetentionPolicy.keepForever,
            ),
          ],
        ),
      );
      final rules = manager.retentionRulesFor('reflection');
      expect(rules, hasLength(1));
      expect(rules.first.policy, RetentionPolicy.keepForever);
    });

    // ── dispose ──

    test('dispose() completes without error', () async {
      await manager.initialize();
      await expectLater(manager.dispose(), completes);
    });
  });
}
