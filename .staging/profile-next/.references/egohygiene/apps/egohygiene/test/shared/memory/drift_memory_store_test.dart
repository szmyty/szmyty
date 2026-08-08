import 'package:drift/native.dart';
import 'package:egohygiene/shared/memory/impl/drift_memory_store.dart';
import 'package:egohygiene/shared/memory/memory.dart';
import 'package:egohygiene/shared/memory/memory_type.dart';
import 'package:egohygiene/shared/storage/app_database.dart';
import 'package:flutter_test/flutter_test.dart';

Memory _memory({
  String id = 'mem-1',
  MemoryType type = MemoryType.episodic,
  String content = 'Test memory content',
  String? source,
  List<String> tags = const [],
  double confidence = 1.0,
  DateTime? createdAt,
  DateTime? updatedAt,
}) {
  final now = DateTime(2025);
  return Memory(
    id: id,
    type: type,
    content: content,
    source: source,
    tags: tags,
    confidence: confidence,
    createdAt: createdAt ?? now,
    updatedAt: updatedAt ?? now,
  );
}

void main() {
  group('DriftMemoryStore', () {
    late AppDatabase database;
    late DriftMemoryStore store;

    setUp(() async {
      database = AppDatabase(executor: NativeDatabase.memory());
      store = DriftMemoryStore(database: database);
      await store.init();
    });

    tearDown(() async {
      await database.close();
    });

    test('save and findById persist memory', () async {
      final memory = _memory(id: 'find-me');
      await store.save(memory);
      final loaded = await store.findById('find-me');
      expect(loaded, memory);
    });

    test('findAll returns createdAt ascending', () async {
      final t1 = DateTime(2025);
      final t2 = DateTime(2025, 1, 2);
      await store.save(_memory(id: 'b', createdAt: t2, updatedAt: t2));
      await store.save(_memory(id: 'a', createdAt: t1, updatedAt: t1));

      final all = await store.findAll();
      expect(all.map((memory) => memory.id), ['a', 'b']);
    });

    test('findByType and findBySource filter persisted rows', () async {
      await store.save(_memory(id: '1', type: MemoryType.semantic, source: 'reflection'));
      await store.save(_memory(id: '2', source: 'conversation'));
      await store.save(_memory(id: '3', type: MemoryType.semantic, source: 'reflection'));

      final byType = await store.findByType(MemoryType.semantic);
      final bySource = await store.findBySource('reflection');

      expect(byType, hasLength(2));
      expect(bySource, hasLength(2));
    });

    test('saveAll, deleteById, clear and count work', () async {
      await store.saveAll([_memory(id: 'a'), _memory(id: 'b')]);
      expect(await store.count(), 2);

      await store.deleteById('a');
      expect(await store.count(), 1);

      await store.clear();
      expect(await store.count(), 0);
    });
  });
}
