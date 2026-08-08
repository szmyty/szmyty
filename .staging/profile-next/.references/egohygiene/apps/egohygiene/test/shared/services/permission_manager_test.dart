import 'package:egohygiene/shared/services/permission_manager.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakePermissionPlatform implements PermissionPlatform {
  final List<PermissionRequest> checkedRequests = [];
  final List<PermissionRequest> requestedPermissions = [];
  final List<PermissionResult> _checkResponses = [];
  final List<PermissionResult> _requestResponses = [];

  void enqueueCheck(PermissionResult result) => _checkResponses.add(result);

  void enqueueRequest(PermissionResult result) => _requestResponses.add(result);

  @override
  Future<PermissionResult> checkPermission(PermissionRequest request) async {
    checkedRequests.add(request);
    return _checkResponses.removeAt(0);
  }

  @override
  Future<PermissionResult> requestPermission(PermissionRequest request) async {
    requestedPermissions.add(request);
    return _requestResponses.removeAt(0);
  }
}

void main() {
  group('PermissionManager', () {
    const notificationRequest = PermissionRequest(
      permission: PermissionType.notifications,
      title: 'Notifications',
      rationale: 'Needed for reminders.',
      denialMessage: 'You can retry later.',
      flow: 'settings',
      retryLabel: 'Retry',
    );

    test('tracks granted permission requests', () async {
      final platform = _FakePermissionPlatform()..enqueueRequest(PermissionResult.granted(notificationRequest));
      final manager = PermissionManager(platform: platform);

      final state = await manager.requestPermission(notificationRequest);

      expect(platform.requestedPermissions, [notificationRequest]);
      expect(state.permission, PermissionType.notifications);
      expect(state.request, notificationRequest);
      expect(state.requestCount, 1);
      expect(state.isGranted, isTrue);
      expect(state.canRetry, isFalse);
      expect(manager.stateFor(PermissionType.notifications), same(state));
    });

    test('retries denied permissions and preserves rationale metadata', () async {
      final platform = _FakePermissionPlatform()
        ..enqueueRequest(PermissionResult.denied(notificationRequest))
        ..enqueueRequest(PermissionResult.limited(notificationRequest));
      final manager = PermissionManager(platform: platform);

      final deniedState = await manager.requestPermission(notificationRequest);
      final retriedState = await manager.retryPermissionRequest(notificationRequest);

      expect(deniedState.isDenied, isTrue);
      expect(deniedState.canRetry, isTrue);
      expect(retriedState.isLimited, isTrue);
      expect(retriedState.request?.rationale, notificationRequest.rationale);
      expect(retriedState.requestCount, 2);
      expect(platform.requestedPermissions, [notificationRequest, notificationRequest]);
    });

    test('does not retry permanently denied permissions without a fresh check', () async {
      final platform = _FakePermissionPlatform()
        ..enqueueRequest(PermissionResult.permanentlyDenied(notificationRequest));
      final manager = PermissionManager(platform: platform);

      final deniedState = await manager.requestPermission(notificationRequest);
      final retriedState = await manager.retryPermissionRequest(notificationRequest);

      expect(deniedState.isPermanentlyDenied, isTrue);
      expect(retriedState.isPermanentlyDenied, isTrue);
      expect(retriedState.requestCount, 1);
      expect(platform.requestedPermissions, [notificationRequest]);
    });

    test('refreshes permission state through the platform abstraction', () async {
      final platform = _FakePermissionPlatform()
        ..enqueueCheck(PermissionResult.unavailable(notificationRequest))
        ..enqueueCheck(PermissionResult.granted(notificationRequest));
      final manager = PermissionManager(platform: platform);

      final initialState = await manager.checkPermission(notificationRequest);
      final refreshedState = await manager.checkPermission(notificationRequest);

      expect(initialState.isUnavailable, isTrue);
      expect(refreshedState.isGranted, isTrue);
      expect(platform.checkedRequests, [notificationRequest, notificationRequest]);
    });

    test('tracks undetermined status as retryable', () async {
      final platform = _FakePermissionPlatform()..enqueueCheck(PermissionResult.undetermined(notificationRequest));
      final manager = PermissionManager(platform: platform);

      final state = await manager.checkPermission(notificationRequest);

      expect(state.isUndetermined, isTrue);
      expect(state.canRetry, isTrue);
    });

    test('stores manual fallback and provider requirements in request metadata', () {
      const request = PermissionRequest(
        permission: PermissionType.location,
        title: 'Location',
        rationale: 'Enable context.',
        denialMessage: 'You can continue without location.',
        settingsDeepLink: 'app-settings:location',
        manualFallback: PermissionManualFallback(
          title: 'Manual setup',
          description: 'Use manual location instead.',
        ),
        providerRequirements: [
          PermissionProviderRequirement(
            providerId: 'weather-context-source',
            rationale: 'Needs location-derived weather.',
          ),
        ],
      );

      expect(request.settingsDeepLink, 'app-settings:location');
      expect(request.manualFallback?.title, 'Manual setup');
      expect(request.providerRequirements, hasLength(1));
    });
  });
}
