import 'package:egohygiene/shared/personal_health/health_dosage.dart';
import 'package:egohygiene/shared/personal_health/health_evidence_level.dart';
import 'package:egohygiene/shared/personal_health/health_ingredient.dart';
import 'package:egohygiene/shared/personal_health/health_interaction.dart';
import 'package:egohygiene/shared/personal_health/health_item.dart';
import 'package:egohygiene/shared/personal_health/health_item_category.dart';
import 'package:egohygiene/shared/personal_health/health_item_store.dart';
import 'package:egohygiene/shared/personal_health/health_manager.dart';
import 'package:egohygiene/shared/personal_health/health_research_reference.dart';
import 'package:egohygiene/shared/personal_health/health_schedule.dart';
import 'package:egohygiene/shared/personal_health/health_warning.dart';
import 'package:egohygiene/shared/personal_health/impl/in_memory_health_item_store.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

HealthItem _item({
  String id = 'item-1',
  String name = 'Vitamin D3',
  String? brand = 'Nature Made',
  HealthItemCategory category = HealthItemCategory.vitamin,
  String? purpose = 'Support bone health',
  bool isActive = true,
  DateTime? startedAt,
  DateTime? discontinuedAt,
  DateTime? createdAt,
  DateTime? updatedAt,
  List<HealthIngredient> ingredients = const [],
  HealthDosage? dosage,
  HealthSchedule? schedule,
  HealthEvidenceLevel evidenceLevel = HealthEvidenceLevel.moderate,
  List<String> tags = const [],
}) {
  final now = DateTime(2026, 1, 1, 10);
  return HealthItem(
    id: id,
    name: name,
    brand: brand,
    category: category,
    purpose: purpose,
    ingredients: ingredients,
    dosage: dosage,
    schedule: schedule,
    evidenceLevel: evidenceLevel,
    isActive: isActive,
    startedAt: startedAt,
    discontinuedAt: discontinuedAt,
    createdAt: createdAt ?? now,
    updatedAt: updatedAt ?? now,
    tags: tags,
  );
}

HealthManager _manager() {
  final store = InMemoryHealthItemStore();
  final manager = HealthManager(store: store);
  return manager;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── HealthItemCategory ─────────────────────────────────────────────────────

  group('HealthItemCategory', () {
    test('has expected values', () {
      expect(
        HealthItemCategory.values.map((c) => c.name),
        containsAll([
          'prescription',
          'otc',
          'supplement',
          'vitamin',
          'nutrition',
          'protein',
          'skincare',
          'haircare',
          'hygiene',
          'wearable',
          'other',
        ]),
      );
    });

    test('displayName returns human-readable label', () {
      expect(HealthItemCategory.prescription.displayName, 'Prescription');
      expect(HealthItemCategory.otc.displayName, 'Over-the-Counter');
      expect(HealthItemCategory.supplement.displayName, 'Supplement');
      expect(HealthItemCategory.wearable.displayName, 'Wearable Device');
    });
  });

  // ── HealthEvidenceLevel ────────────────────────────────────────────────────

  group('HealthEvidenceLevel', () {
    test('has expected values', () {
      expect(HealthEvidenceLevel.values.map((e) => e.name), [
        'anecdotal',
        'preliminary',
        'moderate',
        'strong',
        'inconclusive',
      ]);
    });

    test('displayName returns human-readable label', () {
      expect(HealthEvidenceLevel.strong.displayName, 'Strong');
      expect(HealthEvidenceLevel.anecdotal.displayName, 'Anecdotal');
    });
  });

  // ── HealthIngredient ───────────────────────────────────────────────────────

  group('HealthIngredient', () {
    test('constructs with required fields', () {
      const ingredient = HealthIngredient(name: 'Melatonin');
      expect(ingredient.name, 'Melatonin');
      expect(ingredient.amount, isNull);
      expect(ingredient.unit, isNull);
    });

    test('constructs with all fields', () {
      const ingredient = HealthIngredient(name: 'Vitamin D3', amount: 2000, unit: 'IU');
      expect(ingredient.amount, 2000.0);
      expect(ingredient.unit, 'IU');
    });

    test('copyWith replaces fields', () {
      const original = HealthIngredient(name: 'Mg', amount: 200, unit: 'mg');
      final updated = original.copyWith(amount: 400);
      expect(updated.name, 'Mg');
      expect(updated.amount, 400.0);
      expect(updated.unit, 'mg');
    });

    test('toJson / fromJson round-trip', () {
      const ingredient = HealthIngredient(name: 'Zinc', amount: 25, unit: 'mg', notes: 'picolinate form');
      final json = ingredient.toJson();
      final restored = HealthIngredient.fromJson(json.cast<String, dynamic>());
      expect(restored.name, ingredient.name);
      expect(restored.amount, ingredient.amount);
      expect(restored.unit, ingredient.unit);
      expect(restored.notes, ingredient.notes);
    });

    test('equality is based on name, amount, unit', () {
      const a = HealthIngredient(name: 'Mg', amount: 200, unit: 'mg');
      const b = HealthIngredient(name: 'Mg', amount: 200, unit: 'mg');
      const c = HealthIngredient(name: 'Mg', amount: 400, unit: 'mg');
      expect(a, equals(b));
      expect(a, isNot(equals(c)));
    });
  });

  // ── HealthDosage ───────────────────────────────────────────────────────────

  group('HealthDosage', () {
    test('constructs with required fields', () {
      const dosage = HealthDosage(amount: 1, unit: 'tablet');
      expect(dosage.amount, 1.0);
      expect(dosage.unit, 'tablet');
      expect(dosage.notes, isNull);
    });

    test('toJson / fromJson round-trip', () {
      const dosage = HealthDosage(amount: 2.5, unit: 'ml', notes: 'with food');
      final json = dosage.toJson();
      final restored = HealthDosage.fromJson(json.cast<String, dynamic>());
      expect(restored.amount, dosage.amount);
      expect(restored.unit, dosage.unit);
      expect(restored.notes, dosage.notes);
    });
  });

  // ── HealthSchedule ─────────────────────────────────────────────────────────

  group('HealthSchedule', () {
    test('defaults withFood to false', () {
      const schedule = HealthSchedule(frequency: 'once daily');
      expect(schedule.withFood, isFalse);
      expect(schedule.times, isEmpty);
    });

    test('toJson / fromJson round-trip', () {
      const schedule = HealthSchedule(
        frequency: 'twice daily',
        times: ['morning', 'evening'],
        withFood: true,
        notes: 'with meals',
      );
      final json = schedule.toJson();
      final restored = HealthSchedule.fromJson(json.cast<String, dynamic>());
      expect(restored.frequency, schedule.frequency);
      expect(restored.times, schedule.times);
      expect(restored.withFood, schedule.withFood);
      expect(restored.notes, schedule.notes);
    });
  });

  // ── HealthInteraction ──────────────────────────────────────────────────────

  group('HealthInteraction', () {
    test('defaults severity to note', () {
      const interaction = HealthInteraction(
        withName: 'Warfarin',
        description: 'May increase bleeding risk.',
      );
      expect(interaction.severity, HealthSeverity.note);
    });

    test('toJson / fromJson round-trip preserves severity', () {
      const interaction = HealthInteraction(
        withName: 'Alcohol',
        description: 'Increased sedation.',
        severity: HealthSeverity.warning,
      );
      final json = interaction.toJson();
      final restored = HealthInteraction.fromJson(json.cast<String, dynamic>());
      expect(restored.withName, interaction.withName);
      expect(restored.severity, HealthSeverity.warning);
    });
  });

  // ── HealthWarning ──────────────────────────────────────────────────────────

  group('HealthWarning', () {
    test('defaults severity to caution', () {
      const warning = HealthWarning(title: 'Photosensitivity', description: 'Avoid sun.');
      expect(warning.severity, HealthSeverity.caution);
    });

    test('toJson / fromJson round-trip', () {
      const warning = HealthWarning(
        title: 'Pregnancy',
        description: 'Consult doctor.',
        severity: HealthSeverity.warning,
      );
      final json = warning.toJson();
      final restored = HealthWarning.fromJson(json.cast<String, dynamic>());
      expect(restored.title, warning.title);
      expect(restored.severity, HealthSeverity.warning);
    });
  });

  // ── HealthResearchReference ────────────────────────────────────────────────

  group('HealthResearchReference', () {
    test('defaults evidenceLevel to preliminary', () {
      const ref = HealthResearchReference(
        title: 'Study A',
        source: 'PubMed',
      );
      expect(ref.evidenceLevel, HealthEvidenceLevel.preliminary);
    });

    test('toJson / fromJson round-trip', () {
      const ref = HealthResearchReference(
        title: 'Effects of Vitamin D',
        source: 'NEJM',
        url: 'https://nejm.org/example',
        year: 2022,
        evidenceLevel: HealthEvidenceLevel.strong,
        notes: 'RCT with 5000 participants',
      );
      final json = ref.toJson();
      final restored = HealthResearchReference.fromJson(json.cast<String, dynamic>());
      expect(restored.title, ref.title);
      expect(restored.source, ref.source);
      expect(restored.url, ref.url);
      expect(restored.year, ref.year);
      expect(restored.evidenceLevel, HealthEvidenceLevel.strong);
      expect(restored.notes, ref.notes);
    });
  });

  // ── HealthItem ─────────────────────────────────────────────────────────────

  group('HealthItem', () {
    test('equality is id-based', () {
      final a = _item(id: 'x', name: 'A');
      final b = _item(id: 'x', name: 'B');
      final c = _item(id: 'y', name: 'A');
      expect(a, equals(b));
      expect(a, isNot(equals(c)));
    });

    test('copyWith replaces individual fields', () {
      final original = _item(id: 'i-1', name: 'Old Name');
      final updated = original.copyWith(name: 'New Name', isActive: false);
      expect(updated.id, 'i-1');
      expect(updated.name, 'New Name');
      expect(updated.isActive, isFalse);
      expect(original.name, 'Old Name');
    });

    test('toJson / fromJson round-trip with all fields', () {
      final original = HealthItem(
        id: 'h-42',
        name: 'Omega-3',
        brand: 'Nordic Naturals',
        category: HealthItemCategory.supplement,
        purpose: 'Cardiovascular support',
        ingredients: const [
          HealthIngredient(name: 'EPA', amount: 650, unit: 'mg'),
          HealthIngredient(name: 'DHA', amount: 450, unit: 'mg'),
        ],
        dosage: const HealthDosage(amount: 2, unit: 'softgels'),
        schedule: const HealthSchedule(
          frequency: 'once daily',
          times: ['morning'],
          withFood: true,
        ),
        evidenceLevel: HealthEvidenceLevel.strong,
        interactions: const [
          HealthInteraction(
            withName: 'Anticoagulants',
            description: 'High-dose fish oil may increase bleeding risk.',
            severity: HealthSeverity.caution,
          ),
        ],
        warnings: const [
          HealthWarning(
            title: 'High-dose use',
            description: 'Consult physician for doses above 3g daily.',
          ),
        ],
        researchReferences: const [
          HealthResearchReference(
            title: 'ASCEND Trial',
            source: 'NEJM',
            year: 2018,
            evidenceLevel: HealthEvidenceLevel.strong,
          ),
        ],
        notes: 'Take with breakfast',
        tags: ['heart', 'brain'],
        startedAt: DateTime(2025, 1, 15),
        createdAt: DateTime(2025, 1, 15),
        updatedAt: DateTime(2025, 6),
      );

      final json = original.toJson();
      final restored = HealthItem.fromJson(json.cast<String, dynamic>());

      expect(restored.id, original.id);
      expect(restored.name, original.name);
      expect(restored.brand, original.brand);
      expect(restored.category, original.category);
      expect(restored.purpose, original.purpose);
      expect(restored.ingredients, hasLength(2));
      expect(restored.dosage?.amount, 2.0);
      expect(restored.schedule?.frequency, 'once daily');
      expect(restored.schedule?.withFood, isTrue);
      expect(restored.evidenceLevel, HealthEvidenceLevel.strong);
      expect(restored.interactions, hasLength(1));
      expect(restored.warnings, hasLength(1));
      expect(restored.researchReferences, hasLength(1));
      expect(restored.notes, 'Take with breakfast');
      expect(restored.tags, ['heart', 'brain']);
      expect(restored.isActive, isTrue);
      expect(restored.startedAt, DateTime(2025, 1, 15));
    });
  });

  // ── InMemoryHealthItemStore ────────────────────────────────────────────────

  group('InMemoryHealthItemStore', () {
    late HealthItemStore store;

    setUp(() async {
      store = InMemoryHealthItemStore();
      await store.init();
    });

    test('starts empty', () async {
      expect(await store.count(), 0);
      expect(await store.findAll(), isEmpty);
    });

    test('save and findById', () async {
      final item = _item(id: 'i-1');
      await store.save(item);
      final found = await store.findById('i-1');
      expect(found, isNotNull);
      expect(found!.name, 'Vitamin D3');
    });

    test('findById returns null for unknown id', () async {
      expect(await store.findById('missing'), isNull);
    });

    test('save overwrites existing item with same id', () async {
      final original = _item(id: 'i-1', name: 'Old');
      final updated = _item(id: 'i-1', name: 'New');
      await store.save(original);
      await store.save(updated);
      expect(await store.count(), 1);
      final found = await store.findById('i-1');
      expect(found!.name, 'New');
    });

    test('findAll returns items sorted by createdAt', () async {
      final t1 = DateTime(2026);
      final t2 = DateTime(2026, 1, 2);
      final i1 = _item(id: 'a', createdAt: t2, updatedAt: t2);
      final i2 = _item(id: 'b', createdAt: t1, updatedAt: t1);
      await store.saveAll([i1, i2]);
      final all = await store.findAll();
      expect(all.first.id, 'b');
      expect(all.last.id, 'a');
    });

    test('findActive returns only active items', () async {
      final active = _item(id: 'a-1');
      final inactive = _item(id: 'i-1', isActive: false);
      await store.saveAll([active, inactive]);
      final result = await store.findActive();
      expect(result, hasLength(1));
      expect(result.first.id, 'a-1');
    });

    test('findByCategory filters correctly', () async {
      final supplement = _item(id: 's-1', category: HealthItemCategory.supplement);
      final vitamin = _item(id: 'v-1');
      await store.saveAll([supplement, vitamin]);
      final result = await store.findByCategory(HealthItemCategory.supplement);
      expect(result, hasLength(1));
      expect(result.first.id, 's-1');
    });

    test('deleteById removes item', () async {
      await store.save(_item(id: 'del-1'));
      await store.deleteById('del-1');
      expect(await store.findById('del-1'), isNull);
      expect(await store.count(), 0);
    });

    test('deleteById is no-op for unknown id', () async {
      await store.save(_item(id: 'keep-1'));
      await store.deleteById('missing');
      expect(await store.count(), 1);
    });

    test('clear removes all items', () async {
      await store.saveAll([_item(id: 'a'), _item(id: 'b')]);
      await store.clear();
      expect(await store.count(), 0);
    });
  });

  // ── HealthManager ──────────────────────────────────────────────────────────

  group('HealthManager', () {
    late HealthManager manager;

    setUp(() async {
      manager = _manager();
      await manager.initialize();
    });

    tearDown(() async {
      await manager.dispose();
    });

    test('initialize is idempotent', () async {
      await manager.initialize();
      await manager.initialize();
      expect(await manager.getAll(), isEmpty);
    });

    test('addItem persists the item', () async {
      final item = _item(id: 'mgr-1');
      await manager.addItem(item);
      final all = await manager.getAll();
      expect(all, hasLength(1));
      expect(all.first.id, 'mgr-1');
    });

    test('updateItem replaces existing item', () async {
      await manager.addItem(_item(id: 'u-1', name: 'Old'));
      await manager.updateItem(_item(id: 'u-1', name: 'New'));
      final found = await manager.findById('u-1');
      expect(found!.name, 'New');
    });

    test('getActiveItems returns only active items', () async {
      await manager.addItem(_item(id: 'act'));
      await manager.addItem(_item(id: 'dis', isActive: false));
      final active = await manager.getActiveItems();
      expect(active, hasLength(1));
      expect(active.first.id, 'act');
    });

    test('getByCategory filters correctly', () async {
      await manager.addItem(_item(id: 'v'));
      await manager.addItem(_item(id: 's', category: HealthItemCategory.skincare));
      final vitamins = await manager.getByCategory(HealthItemCategory.vitamin);
      expect(vitamins, hasLength(1));
      expect(vitamins.first.id, 'v');
    });

    test('discontinueItem marks item as inactive', () async {
      await manager.addItem(_item(id: 'd-1'));
      await manager.discontinueItem('d-1');
      final found = await manager.findById('d-1');
      expect(found!.isActive, isFalse);
      expect(found.discontinuedAt, isNotNull);
    });

    test('discontinueItem accepts custom discontinuedAt', () async {
      final customDate = DateTime(2025, 6, 15);
      await manager.addItem(_item(id: 'd-2'));
      await manager.discontinueItem('d-2', discontinuedAt: customDate);
      final found = await manager.findById('d-2');
      expect(found!.discontinuedAt, customDate);
    });

    test('discontinueItem is no-op for unknown id', () async {
      await manager.discontinueItem('missing');
      expect(await manager.getAll(), isEmpty);
    });

    test('removeItem permanently deletes the item', () async {
      await manager.addItem(_item(id: 'rm-1'));
      await manager.removeItem('rm-1');
      expect(await manager.findById('rm-1'), isNull);
    });

    test('findById returns null for unknown id', () async {
      expect(await manager.findById('ghost'), isNull);
    });
  });
}
