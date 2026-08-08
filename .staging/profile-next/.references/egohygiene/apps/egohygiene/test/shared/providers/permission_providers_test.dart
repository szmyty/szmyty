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
  PermissionRequest? lastRequest;
  int requestCalls = 0;

  @override
  Future<PermissionResult> checkPermission(PermissionRequest request) async {
    lastRequest = request;
    return PermissionResult.denied(request);
  }

  @override
  Future<PermissionResult> requestPermission(PermissionRequest request) async {
    requestCalls += 1;
    lastRequest = request;
    return PermissionResult.granted(request);
  }
}

class _FakeLocationProvider implements LocationProvider {
  _FakeLocationProvider({
    required this.permission,
  }) : requestedPermission = LocationPermissionStatus.granted;

  final LocationPermissionStatus permission;
  final LocationPermissionStatus requestedPermission;
  int requestCalls = 0;

  @override
  Future<LocationPermissionStatus> get permissionStatus async => permission;

  @override
  Future<LocationPermissionStatus> requestPermission() async {
    requestCalls += 1;
    return requestedPermission;
  }

  @override
  Future<void> clearManualCoordinate() async {}

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
  LocationMode get mode => LocationMode.disabled;

  @override
  String get providerId => 'fake';

  @override
  Future<void> setManualCoordinate(LocationCoordinate coordinate) async {}
}

void main() {
  group('permission providers', () {
    test('maps location provider permission through the shared permission manager', () async {
      final fallback = _FakePermissionPlatform();
      final locationProvider = _FakeLocationProvider(
        permission: LocationPermissionStatus.undetermined,
      );
      final container = ProviderContainer(
        overrides: [
          permissionBasePlatformProvider.overrideWithValue(fallback),
          locationProviderProvider.overrideWithValue(locationProvider),
        ],
      );
      addTearDown(container.dispose);

      final manager = container.read(permissionManagerProvider);
      const request = PermissionRequest(
        permission: PermissionType.location,
        title: 'Location',
        rationale: 'Needed for context.',
        denialMessage: 'Retry later.',
      );
      final initial = await manager.checkPermission(request);
      final updated = await manager.requestPermission(request);

      expect(initial.isUndetermined, isTrue);
      expect(updated.isGranted, isTrue);
      expect(locationProvider.requestCalls, 1);
      expect(fallback.requestCalls, 0);
    });

    test('uses fallback platform for non-location permissions', () async {
      final fallback = _FakePermissionPlatform();
      final container = ProviderContainer(
        overrides: [
          permissionBasePlatformProvider.overrideWithValue(fallback),
        ],
      );
      addTearDown(container.dispose);

      final manager = container.read(permissionManagerProvider);
      const request = PermissionRequest(
        permission: PermissionType.notifications,
        title: 'Notifications',
        rationale: 'Needed for reminders.',
        denialMessage: 'Retry later.',
      );
      await manager.requestPermission(request);

      expect(fallback.requestCalls, 1);
      expect(fallback.lastRequest?.permission, PermissionType.notifications);
    });
  });
}
