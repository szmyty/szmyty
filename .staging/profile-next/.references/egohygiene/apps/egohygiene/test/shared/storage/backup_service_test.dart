import 'package:egohygiene/shared/storage/backup_service.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('BackupPayload', () {
    test('toJson / fromJson round-trip', () {
      final payload = BackupPayload(
        version: 1,
        createdAt: DateTime.utc(2026, 6, 1, 12),
        data: const {
          'reflections': [
            {'id': 'r1', 'body': 'test'},
          ],
        },
      );

      final json = payload.toJson();
      final restored = BackupPayload.fromJson(json);

      expect(restored.version, payload.version);
      expect(restored.createdAt, payload.createdAt);
      expect(restored.data, payload.data);
    });

    test('fromJson handles missing data field', () {
      final payload = BackupPayload.fromJson(<String, Object?>{
        'version': 2,
        'createdAt': '2026-01-01T00:00:00.000Z',
      });
      expect(payload.data, isEmpty);
    });

    test('toString contains version and createdAt', () {
      final payload = BackupPayload(
        version: 3,
        createdAt: DateTime.utc(2026),
        data: const {'settings': <String, Object?>{}},
      );
      expect(payload.toString(), contains('version: 3'));
      expect(payload.toString(), contains('settings'));
    });
  });

  group('NoopBackupService', () {
    test('exportBackup returns an empty payload', () async {
      const service = NoopBackupService();
      final payload = await service.exportBackup();

      expect(payload.version, 1);
      expect(payload.data, isEmpty);
    });

    test('importBackup completes without error', () async {
      const service = NoopBackupService();
      final payload = BackupPayload(
        version: 1,
        createdAt: DateTime.now(),
        data: const {'reflections': <Object?>[]},
      );

      await expectLater(service.importBackup(payload), completes);
    });
  });
}
