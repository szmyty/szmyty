import 'package:flutter_test/flutter_test.dart';

import 'fake_storage_service.dart';

void main() {
  group('FakeStorageService', () {
    test('saves, reads, and lists keys', () async {
      final storage = FakeStorageService();

      await storage.save('alpha', '1');
      await storage.save('beta', '2');

      expect(await storage.get('alpha'), '1');
      expect(await storage.exists('beta'), isTrue);
      expect(await storage.getAllKeys(), containsAll(['alpha', 'beta']));
    });

    test('deletes and clears values', () async {
      final storage = FakeStorageService();
      await storage.save('alpha', '1');
      await storage.save('beta', '2');

      await storage.delete('alpha');
      expect(await storage.exists('alpha'), isFalse);
      expect(await storage.get('beta'), '2');

      await storage.clear();
      expect(await storage.getAllKeys(), isEmpty);
    });
  });
}
