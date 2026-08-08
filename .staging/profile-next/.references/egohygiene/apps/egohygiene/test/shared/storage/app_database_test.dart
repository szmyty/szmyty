import 'package:drift/native.dart';
import 'package:egohygiene/shared/storage/app_database.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppDatabase', () {
    test('exposes current schema version', () {
      expect(AppDatabaseSchema.currentVersion, 2);
    });

    test('initialize creates required tables and indexes', () async {
      final database = AppDatabase(executor: NativeDatabase.memory());
      addTearDown(database.close);

      await database.initialize();

      final tables = await database.customSelect(
        '''
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name IN ('reflections', 'check_ins', 'memories')
            ORDER BY name
            ''',
      ).get();
      expect(
        tables.map((row) => row.read<String>('name')).toList(),
        equals(['check_ins', 'memories', 'reflections']),
      );

      final indexes = await database.customSelect(
        '''
            SELECT name
            FROM sqlite_master
            WHERE type = 'index' AND name IN (
              'idx_reflections_created_at',
              'idx_check_ins_created_at',
              'idx_memories_type',
              'idx_memories_source'
            )
            ORDER BY name
            ''',
      ).get();
      expect(
        indexes.map((row) => row.read<String>('name')).toList(),
        equals([
          'idx_check_ins_created_at',
          'idx_memories_source',
          'idx_memories_type',
          'idx_reflections_created_at',
        ]),
      );
    });

    test('migrates legacy v1 database to v2 without data loss', () async {
      final database = AppDatabase(
        executor: NativeDatabase.memory(
          setup: (rawDb) {
            rawDb.execute('''
              CREATE TABLE IF NOT EXISTS reflections (
                id TEXT PRIMARY KEY NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                title TEXT,
                body TEXT NOT NULL,
                tags_json TEXT NOT NULL
              );
            ''');

            rawDb.execute('''
              CREATE TABLE IF NOT EXISTS check_ins (
                id TEXT PRIMARY KEY NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                mood INTEGER NOT NULL,
                energy INTEGER NOT NULL,
                stress INTEGER NOT NULL,
                sleep_hours REAL NOT NULL,
                focus INTEGER NOT NULL,
                gratitude TEXT,
                note TEXT
              );
            ''');

            rawDb.execute('''
              CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                tags_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata_json TEXT NOT NULL
              );
            ''');

            rawDb.execute('''
              INSERT INTO memories (
                id,
                type,
                content,
                source,
                tags_json,
                confidence,
                created_at,
                updated_at,
                metadata_json
              ) VALUES (
                'mem-1',
                'episodic',
                'Legacy memory',
                'legacy',
                '[]',
                1.0,
                '2026-01-01T00:00:00.000Z',
                '2026-01-01T00:00:00.000Z',
                '{}'
              );
            ''');

            rawDb.execute('PRAGMA user_version = 1;');
          },
        ),
      );
      addTearDown(database.close);

      await database.initialize();

      final schemaVersion = await database.customSelect('PRAGMA user_version').getSingle();
      expect(schemaVersion.read<int>('user_version'), AppDatabaseSchema.currentVersion);

      final sourceIndex = await database.customSelect(
        '''
            SELECT name
            FROM sqlite_master
            WHERE type = 'index' AND name = 'idx_memories_source'
            ''',
      ).getSingleOrNull();
      expect(sourceIndex, isNotNull);

      final count = await database.customSelect('SELECT COUNT(*) AS total FROM memories').getSingle();
      expect(count.read<int>('total'), 1);
    });
  });
}
