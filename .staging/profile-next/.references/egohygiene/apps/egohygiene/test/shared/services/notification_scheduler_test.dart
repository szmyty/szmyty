import 'package:egohygiene/shared/services/notification_scheduler.dart';
import 'package:egohygiene/shared/services/notification_service.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeNotificationService implements NotificationService {
  final List<Map<String, Object?>> shown = [];
  final List<Map<String, Object?>> scheduled = [];
  final List<int> cancelled = [];
  bool cancelledAll = false;
  List<PendingNotification> pendingStub = [];

  @override
  Future<void> init() async {}

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

void main() {
  group('LocalNotificationScheduler', () {
    const request0 = NotificationRequest(
      id: 1,
      title: 'Test',
      body: 'Body',
      schedule: ImmediateSchedule(),
    );

    test('ImmediateSchedule calls showNotification', () async {
      final service = _FakeNotificationService();
      final scheduler = LocalNotificationScheduler();

      await scheduler.schedule(
        request: const NotificationRequest(
          id: 1,
          title: 'Now',
          body: 'Immediate body',
          schedule: ImmediateSchedule(),
          payload: 'p1',
        ),
        service: service,
      );

      expect(service.shown, hasLength(1));
      expect(service.shown.first['id'], 1);
      expect(service.shown.first['title'], 'Now');
      expect(service.shown.first['body'], 'Immediate body');
      expect(service.shown.first['payload'], 'p1');
      expect(service.scheduled, isEmpty);
    });

    test('ScheduledAtSchedule calls scheduleNotification with the given time', () async {
      final service = _FakeNotificationService();
      final scheduler = LocalNotificationScheduler();
      final target = DateTime(2030, 1, 15, 9);

      await scheduler.schedule(
        request: NotificationRequest(
          id: 2,
          title: 'Future',
          body: 'Scheduled body',
          schedule: ScheduledAtSchedule(target),
        ),
        service: service,
      );

      expect(service.scheduled, hasLength(1));
      expect(service.scheduled.first['scheduledDate'], target);
      expect(service.shown, isEmpty);
    });

    test('DelayedSchedule schedules relative to clock', () async {
      final service = _FakeNotificationService();
      final fixed = DateTime(2030, 6, 1, 12);
      final scheduler = LocalNotificationScheduler(clock: () => fixed);

      await scheduler.schedule(
        request: const NotificationRequest(
          id: 3,
          title: 'Delayed',
          body: 'Delay body',
          schedule: DelayedSchedule(Duration(hours: 2)),
        ),
        service: service,
      );

      final expected = DateTime(2030, 6, 1, 14);
      expect(service.scheduled.first['scheduledDate'], expected);
    });

    test(
      'DailyReminderSchedule targets today when time is still ahead',
      () async {
        final service = _FakeNotificationService();
        final fixed = DateTime(2030, 6, 1, 8);
        final scheduler = LocalNotificationScheduler(clock: () => fixed);

        await scheduler.schedule(
          request: const NotificationRequest(
            id: 4,
            title: 'Daily',
            body: 'Daily body',
            schedule: DailyReminderSchedule(hour: 9, minute: 0),
          ),
          service: service,
        );

        final expected = DateTime(2030, 6, 1, 9);
        expect(service.scheduled.first['scheduledDate'], expected);
      },
    );

    test(
      'DailyReminderSchedule rolls to tomorrow when time has already passed',
      () async {
        final service = _FakeNotificationService();
        final fixed = DateTime(2030, 6, 1, 10);
        final scheduler = LocalNotificationScheduler(clock: () => fixed);

        await scheduler.schedule(
          request: const NotificationRequest(
            id: 5,
            title: 'Daily late',
            body: 'Tomorrow body',
            schedule: DailyReminderSchedule(hour: 9, minute: 0),
          ),
          service: service,
        );

        final expected = DateTime(2030, 6, 2, 9);
        expect(service.scheduled.first['scheduledDate'], expected);
      },
    );

    test('cancel delegates to cancelNotification', () async {
      final service = _FakeNotificationService();
      final scheduler = LocalNotificationScheduler();

      await scheduler.cancel(id: 7, service: service);

      expect(service.cancelled, [7]);
    });

    test('cancelAll delegates to cancelAllNotifications', () async {
      final service = _FakeNotificationService();
      final scheduler = LocalNotificationScheduler();

      await scheduler.cancelAll(service: service);

      expect(service.cancelledAll, isTrue);
    });

    test('getPending delegates to getPendingNotifications', () async {
      final service = _FakeNotificationService()
        ..pendingStub = [
          const PendingNotification(id: 1, title: 'P', body: 'B'),
        ];
      final scheduler = LocalNotificationScheduler();

      final pending = await scheduler.getPending(service: service);

      expect(pending, hasLength(1));
      expect(pending.first.id, 1);
    });

    test('NotificationRequest preserves all fields', () {
      const request = NotificationRequest(
        id: 42,
        title: 'Title',
        body: 'Body',
        schedule: ImmediateSchedule(),
        channelId: 'reminders',
        payload: 'data',
      );

      expect(request.id, 42);
      expect(request.title, 'Title');
      expect(request.body, 'Body');
      expect(request.channelId, 'reminders');
      expect(request.payload, 'data');
      expect(request.schedule, isA<ImmediateSchedule>());
    });

    test('NotificationRequest const constructor compiles', () {
      expect(request0.id, 1);
    });
  });
}
