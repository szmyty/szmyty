import 'package:egohygiene/shared/services/notification_manager.dart';
import 'package:egohygiene/shared/services/notification_scheduler.dart';
import 'package:egohygiene/shared/services/notification_service.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeNotificationService implements NotificationService {
  bool initialized = false;
  final List<Map<String, Object?>> shown = [];
  final List<Map<String, Object?>> scheduled = [];
  final List<int> cancelled = [];
  bool cancelledAll = false;
  List<PendingNotification> pendingStub = [];

  @override
  Future<void> init() async {
    initialized = true;
  }

  @override
  Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    shown.add({'id': id, 'title': title, 'body': body, 'payload': payload});
  }

  @override
  Future<void> scheduleNotification({
    required int id,
    required String title,
    required String body,
    required DateTime scheduledDate,
    String? payload,
  }) async {
    scheduled.add({
      'id': id,
      'title': title,
      'body': body,
      'scheduledDate': scheduledDate,
      'payload': payload,
    });
  }

  @override
  Future<void> cancelNotification(int id) async {
    cancelled.add(id);
  }

  @override
  Future<void> cancelAllNotifications() async {
    cancelledAll = true;
  }

  @override
  Future<List<PendingNotification>> getPendingNotifications() async => pendingStub;
}

class _FakeNotificationScheduler implements NotificationScheduler {
  final List<NotificationRequest> dispatched = [];
  final List<int> cancelled = [];
  bool cancelledAll = false;
  List<PendingNotification> pendingStub = [];

  @override
  Future<void> schedule({
    required NotificationRequest request,
    required NotificationService service,
  }) async {
    dispatched.add(request);
  }

  @override
  Future<void> cancel({
    required int id,
    required NotificationService service,
  }) async {
    cancelled.add(id);
  }

  @override
  Future<void> cancelAll({required NotificationService service}) async {
    cancelledAll = true;
  }

  @override
  Future<List<PendingNotification>> getPending({
    required NotificationService service,
  }) async {
    return pendingStub;
  }
}

void main() {
  group('NotificationManager', () {
    late _FakeNotificationService service;
    late _FakeNotificationScheduler scheduler;
    late NotificationManager manager;

    setUp(() {
      service = _FakeNotificationService();
      scheduler = _FakeNotificationScheduler();
      manager = NotificationManager(service: service, scheduler: scheduler);
    });

    test('initialize calls service.init', () async {
      await manager.initialize();

      expect(service.initialized, isTrue);
    });

    test('dispatch routes request through the scheduler', () async {
      const request = NotificationRequest(
        id: 1,
        title: 'Practice reminder',
        body: 'Time to reflect.',
        schedule: ImmediateSchedule(),
      );

      await manager.dispatch(request);

      expect(scheduler.dispatched, [request]);
    });

    test('manager does not call service directly — only the scheduler does', () async {
      // The manager must delegate all platform work through the scheduler.
      // With a fake scheduler that never forwards calls, the service stays idle.
      await manager.dispatch(
        const NotificationRequest(
          id: 3,
          title: 'Isolated',
          body: 'Body',
          schedule: ImmediateSchedule(),
        ),
      );

      expect(service.shown, isEmpty);
      expect(service.scheduled, isEmpty);
      expect(scheduler.dispatched, hasLength(1));
    });

    test('cancel delegates to scheduler.cancel', () async {
      await manager.cancel(42);

      expect(scheduler.cancelled, [42]);
    });

    test('cancelAll delegates to scheduler.cancelAll', () async {
      await manager.cancelAll();

      expect(scheduler.cancelledAll, isTrue);
    });

    test('getPending delegates to scheduler.getPending', () async {
      scheduler.pendingStub = [
        const PendingNotification(id: 10, title: 'P', body: 'B'),
      ];

      final pending = await manager.getPending();

      expect(pending, hasLength(1));
      expect(pending.first.id, 10);
    });

    test('dispatching multiple requests queues them in order', () async {
      const r1 = NotificationRequest(
        id: 1,
        title: 'First',
        body: 'B',
        schedule: ImmediateSchedule(),
      );
      const r2 = NotificationRequest(
        id: 2,
        title: 'Second',
        body: 'B',
        schedule: ImmediateSchedule(),
      );

      await manager.dispatch(r1);
      await manager.dispatch(r2);

      expect(scheduler.dispatched, [r1, r2]);
    });
  });
}
