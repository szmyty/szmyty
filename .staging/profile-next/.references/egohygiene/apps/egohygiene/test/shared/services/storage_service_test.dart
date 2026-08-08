import 'package:egohygiene/shared/services/storage_service.dart';
import 'package:flutter_test/flutter_test.dart';

// Mock implementation for testing
class MockStorageService implements StorageService {
  final Map<String, String> _storage = {};

  @override
  Future<void> init() async {}

  @override
  Future<void> save(String key, String value) async {
    _storage[key] = value;
  }

  @override
  Future<String?> get(String key) async {
    return _storage[key];
  }

  @override
  Future<void> delete(String key) async {
    _storage.remove(key);
  }

  @override
  Future<bool> exists(String key) async {
    return _storage.containsKey(key);
  }

  @override
  Future<void> clear() async {
    _storage.clear();
  }

  @override
  Future<List<String>> getAllKeys() async {
    return _storage.keys.toList();
  }
}

void main() {
  group('StorageService', () {
    late StorageService storage;

    setUp(() {
      storage = MockStorageService();
    });

    test('can save and retrieve values', () async {
      await storage.save('test_key', 'test_value');
      final value = await storage.get('test_key');
      expect(value, 'test_value');
    });

    test('returns null for non-existent keys', () async {
      final value = await storage.get('non_existent');
      expect(value, null);
    });

    test('can delete values', () async {
      await storage.save('test_key', 'test_value');
      await storage.delete('test_key');
      final value = await storage.get('test_key');
      expect(value, null);
    });

    test('can check if key exists', () async {
      await storage.save('test_key', 'test_value');
      expect(await storage.exists('test_key'), true);
      expect(await storage.exists('non_existent'), false);
    });

    test('can clear all data', () async {
      await storage.save('key1', 'value1');
      await storage.save('key2', 'value2');
      await storage.clear();
      expect(await storage.get('key1'), null);
      expect(await storage.get('key2'), null);
    });

    test('can get all keys', () async {
      await storage.save('key1', 'value1');
      await storage.save('key2', 'value2');
      final keys = await storage.getAllKeys();
      expect(keys, containsAll(['key1', 'key2']));
    });
  });
}
