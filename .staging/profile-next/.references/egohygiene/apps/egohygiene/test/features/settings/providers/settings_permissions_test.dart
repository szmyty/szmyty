import 'package:egohygiene/features/settings/providers/settings_permissions.dart';
import 'package:egohygiene/shared/location/app_location.dart';
import 'package:egohygiene/shared/location/location_coordinate.dart';
import 'package:egohygiene/shared/location/location_mode.dart';
import 'package:egohygiene/shared/location/location_permission_status.dart';
import 'package:egohygiene/shared/location/location_provider.dart';
import 'package:egohygiene/shared/providers/location_providers.dart';
import 'package:egohygiene/shared/providers/permission_providers.dart';
import 'package:egohygiene/shared/services/permission_manager.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakePermissionPlatform implements PermissionPlatform {
  _FakePermissionPlatform(this.result);

  final PermissionResult result;
  PermissionRequest? lastRequest;
  int requestCount = 0;
  int checkCount = 0;

  @override
  Future<PermissionResult> checkPermission(PermissionRequest request) async {
    checkCount += 1;
    lastRequest = request;
    return result;
  }

  @override
  Future<PermissionResult> requestPermission(PermissionRequest request) async {
    requestCount += 1;
    lastRequest = request;
    return result;
  }
}

class _FakeLocationProvider implements LocationProvider {
  LocationCoordinate? manualCoordinate;

  @override
  Future<void> clearManualCoordinate() async {
    manualCoordinate = null;
  }

  @override
  Future<void> dispose() async {}

  @override
  Future<AppLocation?> getCurrentLocation() async => null;

  @override
  Future<AppLocation?> getLastKnownLocation() async => null;

  @override
  Future<void> initialize() async {}

  @override
  Future<bool> get isAvailable async => false;

  @override
  LocationMode get mode => LocationMode.manual;

  @override
  Future<LocationPermissionStatus> get permissionStatus async => LocationPermissionStatus.granted;

  @override
  String get providerId => 'manual-fake';

  @override
  Future<LocationPermissionStatus> requestPermission() async => LocationPermissionStatus.granted;

  @override
  Future<void> setManualCoordinate(LocationCoordinate coordinate) async {
    manualCoordinate = coordinate;
  }
}

void main() {
  group('settings permissions', () {
    test('uses the shared permission manager for notification access', () async {
      const request = PermissionRequest(
        permission: PermissionType.notifications,
        title: 'Notifications',
        rationale: 'Needed for reminders.',
        denialMessage: 'Retry later.',
        flow: 'settings',
        retryLabel: 'Retry notifications',
      );
      final platform = _FakePermissionPlatform(
        PermissionResult.denied(request),
      );
      final container = ProviderContainer(
        overrides: [
          permissionPlatformProvider.overrideWithValue(platform),
          settingsNotificationPermissionRequestProvider.overrideWithValue(request),
        ],
      );
      addTearDown(container.dispose);

      final coordinator = container.read(
        settingsNotificationPermissionCoordinatorProvider,
      );
      final state = await coordinator.requestAccess();

      expect(platform.requestCount, 1);
      expect(platform.lastRequest?.permission, PermissionType.notifications);
      expect(platform.lastRequest?.flow, 'settings');
      expect(state.request, request);
      expect(state.isDenied, isTrue);
      expect(coordinator.state.isDenied, isTrue);
    });

    test('refreshes notification permission state through the manager', () async {
      const request = PermissionRequest(
        permission: PermissionType.notifications,
        title: 'Notifications',
        rationale: 'Needed for reminders.',
        denialMessage: 'Retry later.',
      );
      final platform = _FakePermissionPlatform(
        PermissionResult.granted(request),
      );
      final container = ProviderContainer(
        overrides: [
          permissionPlatformProvider.overrideWithValue(platform),
          settingsNotificationPermissionRequestProvider.overrideWithValue(request),
        ],
      );
      addTearDown(container.dispose);

      final coordinator = container.read(
        settingsNotificationPermissionCoordinatorProvider,
      );
      final state = await coordinator.refresh();

      expect(platform.checkCount, 1);
      expect(state.isGranted, isTrue);
    });

    test('exposes location permission request metadata with manual fallback', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final request = container.read(settingsLocationPermissionRequestProvider);

      expect(request.permission, PermissionType.location);
      expect(request.settingsDeepLink, 'app-settings:location');
      expect(request.manualFallback?.actionLabel, 'Use manual location');
      expect(request.providerRequirements, isNotEmpty);
    });

    test('uses the shared manager for location permission requests', () async {
      const request = PermissionRequest(
        permission: PermissionType.location,
        title: 'Location',
        rationale: 'Needed for context.',
        denialMessage: 'Retry later.',
      );
      final platform = _FakePermissionPlatform(
        PermissionResult.granted(request),
      );
      final container = ProviderContainer(
        overrides: [
          permissionPlatformProvider.overrideWithValue(platform),
          settingsLocationPermissionRequestProvider.overrideWithValue(request),
        ],
      );
      addTearDown(container.dispose);

      final coordinator = container.read(
        settingsLocationPermissionCoordinatorProvider,
      );
      final state = await coordinator.requestAccess();

      expect(platform.requestCount, 1);
      expect(platform.lastRequest?.permission, PermissionType.location);
      expect(state.isGranted, isTrue);
    });

    test('supports manual location fallback flow', () async {
      final locationProvider = _FakeLocationProvider();
      final container = ProviderContainer(
        overrides: [
          locationProviderProvider.overrideWithValue(locationProvider),
        ],
      );
      addTearDown(container.dispose);

      final coordinator = container.read(
        settingsLocationPermissionCoordinatorProvider,
      );
      const coordinate = LocationCoordinate(latitude: 10.1, longitude: 20.2);
      await coordinator.useManualLocation(coordinate);

      expect(locationProvider.manualCoordinate, coordinate);
    });
  });
}
