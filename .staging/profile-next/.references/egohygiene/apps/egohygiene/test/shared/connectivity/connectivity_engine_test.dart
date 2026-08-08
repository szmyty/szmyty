import 'package:egohygiene/shared/connectivity/connectivity_manager.dart';
import 'package:egohygiene/shared/connectivity/connectivity_provider.dart';
import 'package:egohygiene/shared/connectivity/connectivity_state.dart';
import 'package:egohygiene/shared/connectivity/impl/local_connectivity_provider.dart';
import 'package:egohygiene/shared/connectivity/offline_mode_manager.dart';
import 'package:egohygiene/shared/providers/connectivity_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Test doubles
// ---------------------------------------------------------------------------

class _FakeConnectivityProvider implements ConnectivityProvider {
  _FakeConnectivityProvider({
    this.state = ConnectivityState.online,
  }) : providerAvailable = true;

  ConnectivityState state;
  bool providerAvailable;

  @override
  String get providerId => 'fake';

  @override
  Future<NetworkStatus> checkStatus() async => NetworkStatus.now(state: state);

  @override
  Future<ProviderAvailability> checkProviderAvailability(
    String providerId,
  ) async {
    return ProviderAvailability.now(
      providerId: providerId,
      isAvailable: providerAvailable,
    );
  }

  @override
  Stream<NetworkStatus>? get statusStream => null;

  @override
  Future<void> dispose() async {}
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  group('ConnectivityState', () {
    test('online state allows sync', () {
      final status = NetworkStatus(
        state: ConnectivityState.online,
        checkedAt: DateTime.utc(2026, 7, 1, 10),
      );

      expect(status.isOnline, isTrue);
      expect(status.canSync, isTrue);
      expect(status.isOffline, isFalse);
    });

    test('offline state disallows sync', () {
      final status = NetworkStatus(
        state: ConnectivityState.offline,
        checkedAt: DateTime.utc(2026, 7, 1, 10),
      );

      expect(status.isOnline, isFalse);
      expect(status.canSync, isFalse);
      expect(status.isOffline, isTrue);
    });

    test('degraded state is online but cannot sync', () {
      final status = NetworkStatus(
        state: ConnectivityState.degraded,
        checkedAt: DateTime.utc(2026, 7, 1, 10),
      );

      expect(status.isOnline, isTrue);
      expect(status.canSync, isFalse);
      expect(status.isOffline, isFalse);
    });

    test('localOnly state is offline and cannot sync', () {
      final status = NetworkStatus(
        state: ConnectivityState.localOnly,
        checkedAt: DateTime.utc(2026, 7, 1, 10),
      );

      expect(status.isOnline, isFalse);
      expect(status.canSync, isFalse);
      expect(status.isOffline, isFalse);
    });
  });

  group('NetworkStatus', () {
    test('copyWith replaces specified fields', () {
      final original = NetworkStatus(
        state: ConnectivityState.online,
        checkedAt: DateTime.utc(2026, 7, 1, 10),
        lastOnlineAt: DateTime.utc(2026, 7, 1, 9),
      );

      final updated = original.copyWith(state: ConnectivityState.offline);

      expect(updated.state, ConnectivityState.offline);
      expect(updated.checkedAt, original.checkedAt);
      expect(updated.lastOnlineAt, original.lastOnlineAt);
    });

    test('copyWith can clear lastOnlineAt', () {
      final original = NetworkStatus(
        state: ConnectivityState.online,
        checkedAt: DateTime.utc(2026, 7, 1, 10),
        lastOnlineAt: DateTime.utc(2026, 7, 1, 9),
      );

      final updated = original.copyWith(lastOnlineAt: null);

      expect(updated.lastOnlineAt, isNull);
    });
  });

  group('ProviderAvailability', () {
    test('represents an available provider', () {
      final availability = ProviderAvailability(
        providerId: 'openai',
        isAvailable: true,
        checkedAt: DateTime.utc(2026, 7, 1, 10),
      );

      expect(availability.providerId, 'openai');
      expect(availability.isAvailable, isTrue);
      expect(availability.reason, isNull);
    });

    test('represents an unavailable provider with reason', () {
      final availability = ProviderAvailability(
        providerId: 'icloud',
        isAvailable: false,
        checkedAt: DateTime.utc(2026, 7, 1, 10),
        reason: 'auth_expired',
      );

      expect(availability.isAvailable, isFalse);
      expect(availability.reason, 'auth_expired');
    });
  });

  group('LocalConnectivityProvider', () {
    test('reports localOnly state', () async {
      const provider = LocalConnectivityProvider();

      final status = await provider.checkStatus();

      expect(status.state, ConnectivityState.localOnly);
      expect(status.isOnline, isFalse);
      expect(status.canSync, isFalse);
    });

    test('reports all providers as unavailable with local_provider reason', () async {
      const provider = LocalConnectivityProvider();

      final availability = await provider.checkProviderAvailability('openai');

      expect(availability.providerId, 'openai');
      expect(availability.isAvailable, isFalse);
      expect(availability.reason, 'local_provider');
    });

    test('has no status stream', () {
      const provider = LocalConnectivityProvider();

      expect(provider.statusStream, isNull);
    });
  });

  group('OfflineModeManager', () {
    late OfflineModeManager manager;

    setUp(() {
      manager = OfflineModeManager();
    });

    test('defaults to online mode with no pending sync', () {
      expect(manager.isOfflineModeEnabled, isFalse);
      expect(manager.hasPendingSync, isFalse);
      expect(manager.lastSyncedAt, isNull);
    });

    test('enableOfflineMode activates local-only operation', () {
      manager.enableOfflineMode();

      expect(manager.isOfflineModeEnabled, isTrue);
    });

    test('disableOfflineMode returns to normal operation', () {
      manager.enableOfflineMode();
      manager.disableOfflineMode();

      expect(manager.isOfflineModeEnabled, isFalse);
    });

    test('recordSync stores timestamp and clears pending flag', () {
      final syncTime = DateTime.utc(2026, 7, 1, 12);
      manager.markSyncPending();

      manager.recordSync(syncedAt: syncTime);

      expect(manager.lastSyncedAt, syncTime);
      expect(manager.hasPendingSync, isFalse);
    });

    test('markSyncPending sets pending flag', () {
      manager.markSyncPending();

      expect(manager.hasPendingSync, isTrue);
    });

    test('reset clears all state', () {
      manager.enableOfflineMode();
      manager.markSyncPending();
      manager.recordSync(syncedAt: DateTime.utc(2026, 7, 1, 12));
      manager.enableOfflineMode();

      manager.reset();

      expect(manager.isOfflineModeEnabled, isFalse);
      expect(manager.hasPendingSync, isFalse);
      expect(manager.lastSyncedAt, isNull);
    });
  });

  group('ConnectivityManager', () {
    test('defaults to localOnly state before initialization', () {
      final provider = _FakeConnectivityProvider();
      final manager = ConnectivityManager(provider: provider);

      expect(manager.lastKnownStatus.state, ConnectivityState.localOnly);
      expect(manager.isOnline, isFalse);
      expect(manager.canSync, isFalse);
    });

    test('reports online after initialization with online provider', () async {
      final provider = _FakeConnectivityProvider();
      final manager = ConnectivityManager(provider: provider);

      await manager.initialize();

      expect(manager.lastKnownStatus.state, ConnectivityState.online);
      expect(manager.isOnline, isTrue);
      expect(manager.canSync, isTrue);
    });

    test('reports offline when provider reports offline', () async {
      final provider = _FakeConnectivityProvider(state: ConnectivityState.offline);
      final manager = ConnectivityManager(provider: provider);

      await manager.initialize();
      final status = await manager.currentStatus();

      expect(status.state, ConnectivityState.offline);
      expect(status.isOnline, isFalse);
      expect(status.canSync, isFalse);
    });

    test('reports localOnly when offline mode is enabled regardless of network', () async {
      final provider = _FakeConnectivityProvider();
      final offlineManager = OfflineModeManager();
      final manager = ConnectivityManager(
        provider: provider,
        offlineModeManager: offlineManager,
      );

      offlineManager.enableOfflineMode();
      await manager.initialize();

      expect(manager.lastKnownStatus.state, ConnectivityState.localOnly);
      expect(manager.isOnline, isFalse);
    });

    test('tracks lastOnlineAt across status transitions', () async {
      final provider = _FakeConnectivityProvider();
      final manager = ConnectivityManager(provider: provider);

      await manager.initialize();
      final onlineStatus = manager.lastKnownStatus;
      expect(onlineStatus.lastOnlineAt, isNotNull);

      provider.state = ConnectivityState.offline;
      final offlineStatus = await manager.currentStatus();

      expect(offlineStatus.state, ConnectivityState.offline);
      expect(
        offlineStatus.lastOnlineAt,
        onlineStatus.lastOnlineAt,
        reason: 'lastOnlineAt should be preserved when going offline',
      );
    });

    test('checkProviderAvailability delegates to provider when online', () async {
      final provider = _FakeConnectivityProvider();
      final manager = ConnectivityManager(provider: provider);

      await manager.initialize();
      final availability = await manager.checkProviderAvailability('openai');

      expect(availability.providerId, 'openai');
      expect(availability.isAvailable, isTrue);
    });

    test('checkProviderAvailability returns unavailable when offline mode is on', () async {
      final provider = _FakeConnectivityProvider();
      final offlineManager = OfflineModeManager()..enableOfflineMode();
      final manager = ConnectivityManager(
        provider: provider,
        offlineModeManager: offlineManager,
      );

      final availability = await manager.checkProviderAvailability('openai');

      expect(availability.isAvailable, isFalse);
      expect(availability.reason, 'offline_mode');
    });

    test('initialize is idempotent', () async {
      final provider = _FakeConnectivityProvider();
      final manager = ConnectivityManager(provider: provider);

      await manager.initialize();
      provider.state = ConnectivityState.offline;
      await manager.initialize(); // should be a no-op

      expect(manager.lastKnownStatus.state, ConnectivityState.online);
    });
  });

  group('connectivity providers', () {
    test('wires connectivity provider and offline mode manager overrides', () async {
      final fakeProvider = _FakeConnectivityProvider();
      final offlineManager = OfflineModeManager();
      final container = ProviderContainer(
        overrides: [
          connectivityProviderProvider.overrideWithValue(fakeProvider),
          offlineModeManagerProvider.overrideWithValue(offlineManager),
        ],
      );
      addTearDown(container.dispose);

      final manager = container.read(connectivityManagerProvider);
      await manager.initialize();

      expect(manager.lastKnownStatus.state, ConnectivityState.online);
      expect(container.read(connectivityProviderProvider), same(fakeProvider));
      expect(
        container.read(offlineModeManagerProvider),
        same(offlineManager),
      );
    });

    test('default provider is LocalConnectivityProvider', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final provider = container.read(connectivityProviderProvider);

      expect(provider, isA<LocalConnectivityProvider>());
    });
  });
}
