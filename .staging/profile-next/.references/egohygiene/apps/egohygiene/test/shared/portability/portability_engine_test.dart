import 'package:egohygiene/shared/portability/data_export_manager.dart';
import 'package:egohygiene/shared/portability/data_import_manager.dart';
import 'package:egohygiene/shared/portability/export_format.dart';
import 'package:egohygiene/shared/portability/export_manifest.dart';
import 'package:egohygiene/shared/portability/export_record.dart';
import 'package:egohygiene/shared/portability/impl/noop_import_validator.dart';
import 'package:egohygiene/shared/portability/import_result.dart';
import 'package:egohygiene/shared/portability/import_validator.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

DataExportManager _makeExportManager({String appVersion = '1.0.0'}) => DataExportManager(
  appVersion: appVersion,
  exportIdGenerator: () => 'test-export-id',
);

DataImportManager _makeImportManager({ImportValidator? validator}) => DataImportManager(
  validator: validator ?? const NoopImportValidator(),
);

ExportRecord _makeRecord({
  String exportId = 'record-id',
  ExportFormat format = ExportFormat.json,
  Map<String, dynamic> data = const {},
}) {
  return ExportRecord(
    manifest: ExportManifest(
      exportId: exportId,
      format: format,
      exportedAt: DateTime.utc(2026, 6, 1, 12),
      schemaVersion: 1,
      appVersion: '1.0.0',
      domains: data.keys.toList(),
      recordCount: data.values.whereType<List<Object?>>().fold(0, (s, l) => s + l.length),
    ),
    data: data,
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── ExportFormat ───────────────────────────────────────────────────────────

  group('ExportFormat', () {
    test('has json, markdown, zip values', () {
      expect(ExportFormat.values, contains(ExportFormat.json));
      expect(ExportFormat.values, contains(ExportFormat.markdown));
      expect(ExportFormat.values, contains(ExportFormat.zip));
    });
  });

  // ── ExportManifest ─────────────────────────────────────────────────────────

  group('ExportManifest', () {
    final manifest = ExportManifest(
      exportId: 'exp-1',
      format: ExportFormat.json,
      exportedAt: DateTime.utc(2026, 6, 1, 12),
      schemaVersion: 1,
      appVersion: '1.0.0',
      domains: ['reflections', 'goals'],
      recordCount: 5,
    );

    test('toJson / fromJson round-trip', () {
      final json = manifest.toJson();
      final restored = ExportManifest.fromJson(json);

      expect(restored.exportId, manifest.exportId);
      expect(restored.format, manifest.format);
      expect(restored.exportedAt, manifest.exportedAt);
      expect(restored.schemaVersion, manifest.schemaVersion);
      expect(restored.appVersion, manifest.appVersion);
      expect(restored.domains, manifest.domains);
      expect(restored.recordCount, manifest.recordCount);
    });

    test('toJson includes all fields', () {
      final json = manifest.toJson();

      expect(json['exportId'], 'exp-1');
      expect(json['format'], 'json');
      expect(json['schemaVersion'], 1);
      expect(json['appVersion'], '1.0.0');
      expect(json['domains'], ['reflections', 'goals']);
      expect(json['recordCount'], 5);
    });

    test('toJson omits metadata when empty', () {
      final json = manifest.toJson();
      expect(json.containsKey('metadata'), isFalse);
    });

    test('toJson includes metadata when non-empty', () {
      final m = ExportManifest(
        exportId: 'x',
        format: ExportFormat.zip,
        exportedAt: DateTime.utc(2026),
        schemaVersion: 2,
        appVersion: '2.0.0',
        domains: const [],
        recordCount: 0,
        metadata: const {'checksum': 'abc123'},
      );

      final json = m.toJson();
      expect(json['metadata'], {'checksum': 'abc123'});
    });

    test('toString contains exportId and format', () {
      expect(manifest.toString(), contains('exp-1'));
      expect(manifest.toString(), contains('json'));
    });
  });

  // ── ExportRecord ───────────────────────────────────────────────────────────

  group('ExportRecord', () {
    test('toJson / fromJson round-trip', () {
      final record = _makeRecord(
        data: {
          'reflections': [
            {'id': 'r1', 'body': 'hello'},
          ],
        },
      );

      final json = record.toJson();
      final restored = ExportRecord.fromJson(json);

      expect(restored.manifest.exportId, record.manifest.exportId);
      expect(restored.data, record.data);
    });

    test('fromJson handles missing data field', () {
      final manifest = ExportManifest(
        exportId: 'x',
        format: ExportFormat.json,
        exportedAt: DateTime.utc(2026),
        schemaVersion: 1,
        appVersion: '1.0.0',
        domains: const [],
        recordCount: 0,
      );

      final json = {
        'manifest': manifest.toJson(),
        // 'data' is intentionally absent
      };

      final record = ExportRecord.fromJson(json);
      expect(record.data, isEmpty);
    });

    test('toString contains domain names', () {
      final record = _makeRecord(
        data: {'reflections': <Object?>[], 'goals': <Object?>[]},
      );

      expect(record.toString(), contains('reflections'));
      expect(record.toString(), contains('goals'));
    });
  });

  // ── ImportResult ───────────────────────────────────────────────────────────

  group('ImportResult', () {
    test('success result has isValid true and no errors', () {
      const result = ImportResult.success();

      expect(result.isValid, isTrue);
      expect(result.isFailure, isFalse);
      expect(result.errors, isEmpty);
      expect(result.warnings, isEmpty);
    });

    test('success result may have warnings', () {
      const result = ImportResult.success(warnings: ['minor issue']);

      expect(result.isValid, isTrue);
      expect(result.warnings, ['minor issue']);
    });

    test('failure result has isValid false and errors', () {
      const result = ImportResult.failure(
        errors: ['schema version mismatch', 'missing domain'],
      );

      expect(result.isValid, isFalse);
      expect(result.isFailure, isTrue);
      expect(result.errors, hasLength(2));
    });

    test('failure result may have warnings alongside errors', () {
      const result = ImportResult.failure(
        errors: ['critical error'],
        warnings: ['non-fatal warning'],
      );

      expect(result.errors, hasLength(1));
      expect(result.warnings, hasLength(1));
    });

    test('toString distinguishes success from failure', () {
      expect(
        const ImportResult.success().toString(),
        contains('success'),
      );
      expect(
        const ImportResult.failure(errors: ['e']).toString(),
        contains('failure'),
      );
    });
  });

  // ── NoopImportValidator ────────────────────────────────────────────────────

  group('NoopImportValidator', () {
    test('validate always returns success', () async {
      const validator = NoopImportValidator();
      final record = _makeRecord();

      final result = await validator.validate(record);

      expect(result.isValid, isTrue);
      expect(result.errors, isEmpty);
    });
  });

  // ── DataExportManager ──────────────────────────────────────────────────────

  group('DataExportManager', () {
    test('registeredDomains is empty by default', () {
      final manager = _makeExportManager();
      expect(manager.registeredDomains, isEmpty);
    });

    test('registerDomainExporter adds a domain', () {
      final manager = _makeExportManager()..registerDomainExporter('reflections', () async => <dynamic>[]);

      expect(manager.registeredDomains, contains('reflections'));
    });

    test('unregisterDomainExporter removes a domain', () {
      final manager = _makeExportManager()
        ..registerDomainExporter('reflections', () async => <dynamic>[])
        ..unregisterDomainExporter('reflections');

      expect(manager.registeredDomains, isEmpty);
    });

    test('export produces ExportRecord with manifest', () async {
      final manager = _makeExportManager()
        ..registerDomainExporter(
          'reflections',
          () async => [
            {'id': 'r1'},
            {'id': 'r2'},
          ],
        )
        ..registerDomainExporter('goals', () async => <dynamic>[]);

      final record = await manager.export();

      expect(record.manifest.exportId, 'test-export-id');
      expect(record.manifest.format, ExportFormat.json);
      expect(record.manifest.schemaVersion, 1);
      expect(record.manifest.appVersion, '1.0.0');
      expect(record.manifest.domains, containsAll(['reflections', 'goals']));
      expect(record.manifest.recordCount, 2); // 2 reflections + 0 goals
    });

    test('export stores collected data in ExportRecord', () async {
      final manager = _makeExportManager()
        ..registerDomainExporter(
          'settings',
          () async => {'theme': 'dark'},
        );

      final record = await manager.export();

      expect(record.data['settings'], {'theme': 'dark'});
    });

    test('export with no domains returns empty record', () async {
      final manager = _makeExportManager();
      final record = await manager.export();

      expect(record.data, isEmpty);
      expect(record.manifest.recordCount, 0);
      expect(record.manifest.domains, isEmpty);
    });

    test('renderJson returns a JSON-compatible map', () async {
      final manager = _makeExportManager()..registerDomainExporter('insights', () async => <dynamic>[]);

      final record = await manager.export();
      final json = manager.renderJson(record);

      expect(json, isA<Map<String, dynamic>>());
      expect(json.containsKey('manifest'), isTrue);
      expect(json.containsKey('data'), isTrue);
    });

    test('renderMarkdown returns a string containing headers', () async {
      final manager = _makeExportManager()
        ..registerDomainExporter(
          'reflections',
          () async => [
            {'id': 'r1', 'body': 'first reflection'},
          ],
        );

      final record = await manager.export();
      final md = manager.renderMarkdown(record);

      expect(md, contains('# Ego Hygiene'));
      expect(md, contains('## Reflections'));
      expect(md, contains('test-export-id'));
    });

    test('renderMarkdown formats empty lists as "No records."', () async {
      final manager = _makeExportManager()..registerDomainExporter('goals', () async => <dynamic>[]);

      final record = await manager.export();
      final md = manager.renderMarkdown(record);

      expect(md, contains('_No records._'));
    });

    test('renderMarkdown formats empty map as "No data."', () async {
      final manager = _makeExportManager()..registerDomainExporter('settings', () async => <String, dynamic>{});

      final record = await manager.export();
      final md = manager.renderMarkdown(record);

      expect(md, contains('_No data._'));
    });

    test('replacing a domain exporter overwrites the previous one', () async {
      final manager = _makeExportManager()
        ..registerDomainExporter('reflections', () async => ['old'])
        ..registerDomainExporter('reflections', () async => ['new']);

      final record = await manager.export();
      expect(record.data['reflections'], ['new']);
    });
  });

  // ── DataImportManager ──────────────────────────────────────────────────────

  group('DataImportManager', () {
    test('registeredDomains is empty by default', () {
      final manager = _makeImportManager();
      expect(manager.registeredDomains, isEmpty);
    });

    test('registerDomainImporter adds a domain', () {
      final manager = _makeImportManager()..registerDomainImporter('reflections', (_) async {});

      expect(manager.registeredDomains, contains('reflections'));
    });

    test('unregisterDomainImporter removes a domain', () {
      final manager = _makeImportManager()
        ..registerDomainImporter('reflections', (_) async {})
        ..unregisterDomainImporter('reflections');

      expect(manager.registeredDomains, isEmpty);
    });

    test('validate delegates to the ImportValidator', () async {
      final manager = _makeImportManager();
      final record = _makeRecord();

      final result = await manager.validate(record);

      expect(result.isValid, isTrue);
    });

    test('applyImport invokes registered domain importers', () async {
      final imported = <String>[];
      final manager = _makeImportManager()
        ..registerDomainImporter('reflections', (data) async {
          imported.add('reflections:${(data as List).length}');
        });

      final record = _makeRecord(
        data: {
          'reflections': [
            {'id': 'r1'},
          ],
        },
      );

      await manager.applyImport(record);

      expect(imported, ['reflections:1']);
    });

    test('applyImport skips domains with no registered importer', () async {
      final imported = <String>[];
      final manager = _makeImportManager()
        ..registerDomainImporter('goals', (data) async {
          imported.add('goals');
        });

      final record = _makeRecord(
        data: {
          'reflections': <Object?>[],
          'goals': <Object?>[],
        },
      );

      await manager.applyImport(record);

      expect(imported, ['goals']);
      expect(imported, isNot(contains('reflections')));
    });

    test('validateAndImport applies data when valid', () async {
      final imported = <String>[];
      final manager = _makeImportManager()
        ..registerDomainImporter('practices', (_) async {
          imported.add('practices');
        });

      final record = _makeRecord(data: {'practices': <Object?>[]});
      final result = await manager.validateAndImport(record);

      expect(result.isValid, isTrue);
      expect(imported, ['practices']);
    });

    test('validateAndImport does not apply data when validation fails', () async {
      final imported = <String>[];

      final failingValidator = _FailingValidator();
      final manager = _makeImportManager(validator: failingValidator)
        ..registerDomainImporter('reflections', (_) async {
          imported.add('should-not-run');
        });

      final record = _makeRecord(data: {'reflections': <Object?>[]});
      final result = await manager.validateAndImport(record);

      expect(result.isValid, isFalse);
      expect(result.errors, isNotEmpty);
      expect(imported, isEmpty);
    });
  });
}

// ---------------------------------------------------------------------------
// Test doubles
// ---------------------------------------------------------------------------

class _FailingValidator implements ImportValidator {
  @override
  Future<ImportResult> validate(ExportRecord record) async =>
      const ImportResult.failure(errors: ['schema version not supported']);
}
