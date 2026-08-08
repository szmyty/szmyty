import 'package:egohygiene/shared/personal_health/health_dosage.dart';
import 'package:egohygiene/shared/personal_health/health_item.dart';
import 'package:egohygiene/shared/personal_health/health_item_category.dart';
import 'package:egohygiene/shared/personal_health/health_schedule.dart';
import 'package:egohygiene/shared/timeline/impl/health_item_timeline_source.dart';
import 'package:egohygiene/shared/timeline/timeline_event.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

HealthItem _item({
  String id = 'h-1',
  String name = 'Vitamin D3',
  HealthItemCategory category = HealthItemCategory.vitamin,
  String? purpose = 'Bone health support',
  String? brand,
  bool isActive = true,
  DateTime? startedAt,
  DateTime? discontinuedAt,
  HealthDosage? dosage,
  HealthSchedule? schedule,
  List<String> tags = const [],
}) {
  final now = DateTime.utc(2026, 1, 15, 10);
  return HealthItem(
    id: id,
    name: name,
    brand: brand,
    category: category,
    purpose: purpose,
    isActive: isActive,
    startedAt: startedAt,
    discontinuedAt: discontinuedAt,
    dosage: dosage,
    schedule: schedule,
    tags: tags,
    createdAt: now,
    updatedAt: now,
  );
}

void main() {
  group('HealthItemTimelineSource', () {
    test('sourceId is healthItem', () {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [],
      );
      expect(source.sourceId, 'healthItem');
    });

    test('displayName is Health Stack', () {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [],
      );
      expect(source.displayName, 'Health Stack');
    });

    test('getEvents returns empty list when no items', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [],
      );
      expect(await source.getEvents(), isEmpty);
    });

    test('getEvents returns one event per active item', () async {
      final items = [
        _item(),
        _item(id: 'h-2'),
      ];
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => items,
      );
      final events = await source.getEvents();
      expect(events, hasLength(2));
    });

    test('getEvents excludes inactive items by default', () async {
      final items = [
        _item(id: 'a'),
        _item(id: 'b', isActive: false),
      ];
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => items,
      );
      final events = await source.getEvents();
      expect(events, hasLength(1));
      expect(events.first.id, 'a');
    });

    test('includeDiscontinued: true includes inactive items', () async {
      final items = [
        _item(id: 'a'),
        _item(id: 'b', isActive: false),
      ];
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => items,
        includeDiscontinued: true,
      );
      final events = await source.getEvents();
      expect(events, hasLength(2));
    });

    test('event type is healthMetric', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [_item()],
      );
      final events = await source.getEvents();
      expect(events.first.type, TimelineEventType.healthMetric);
    });

    test('event title is the item name', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [_item(name: 'Magnesium Glycinate')],
      );
      final events = await source.getEvents();
      expect(events.first.title, 'Magnesium Glycinate');
    });

    test('event description is the item purpose', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [_item(purpose: 'Improve sleep quality')],
      );
      final events = await source.getEvents();
      expect(events.first.description, 'Improve sleep quality');
    });

    test('event occurredAt uses startedAt when set', () async {
      final startedAt = DateTime.utc(2025, 3);
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [_item(startedAt: startedAt)],
      );
      final events = await source.getEvents();
      expect(events.first.occurredAt, startedAt);
    });

    test('event occurredAt falls back to createdAt when startedAt is null', () async {
      final createdAt = DateTime.utc(2026, 1, 15, 10);
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [_item()],
      );
      final events = await source.getEvents();
      expect(events.first.occurredAt, createdAt);
    });

    test('event metadata contains category and isActive', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [_item(id: 'x', category: HealthItemCategory.supplement)],
      );
      final events = await source.getEvents();
      expect(events.first.metadata['category'], 'supplement');
      expect(events.first.metadata['isActive'], isTrue);
    });

    test('event metadata contains brand when set', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [_item(brand: 'Nordic Naturals')],
      );
      final events = await source.getEvents();
      expect(events.first.metadata['brand'], 'Nordic Naturals');
    });

    test('event metadata omits brand when null', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [_item()],
      );
      final events = await source.getEvents();
      expect(events.first.metadata.containsKey('brand'), isFalse);
    });

    test('event metadata contains dosage string when set', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [
          _item(
            dosage: const HealthDosage(amount: 2000, unit: 'IU'),
          ),
        ],
      );
      final events = await source.getEvents();
      expect(events.first.metadata['dosage'], '2000.0 IU');
    });

    test('event metadata contains schedule frequency when set', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [
          _item(
            schedule: const HealthSchedule(frequency: 'once daily'),
          ),
        ],
      );
      final events = await source.getEvents();
      expect(events.first.metadata['schedule'], 'once daily');
    });

    test('event metadata contains discontinuedAt for inactive items', () async {
      final discontinuedAt = DateTime.utc(2026, 6);
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [
          _item(
            isActive: false,
            discontinuedAt: discontinuedAt,
          ),
        ],
        includeDiscontinued: true,
      );
      final events = await source.getEvents();
      expect(
        events.first.metadata['discontinuedAt'],
        discontinuedAt.toIso8601String(),
      );
    });

    test('event id matches item id', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [_item(id: 'specific-id')],
      );
      final events = await source.getEvents();
      expect(events.first.id, 'specific-id');
    });

    test('initialize and dispose complete without error', () async {
      final source = HealthItemTimelineSource(
        healthItemLoader: () async => [],
      );
      await expectLater(source.initialize(), completes);
      await expectLater(source.dispose(), completes);
    });
  });
}
