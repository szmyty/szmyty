import 'package:egohygiene/shared/services/impl/noop_encryption_provider.dart';
import 'package:egohygiene/shared/services/impl/secure_storage_key_manager.dart';
import 'package:egohygiene/shared/services/key_manager.dart';
import 'package:egohygiene/shared/services/secure_storage_service.dart';
import 'package:flutter_test/flutter_test.dart';

/// In-memory [SecureStorageService] for testing.
class _InMemorySecureStorage implements SecureStorageService {
  final Map<String, String> _data = {};

  @override
  Future<void> init() async {}

  @override
  Future<void> saveSecure(String key, String value) async {
    _data[key] = value;
  }

  @override
  Future<String?> getSecure(String key) async => _data[key];

  @override
  Future<void> deleteSecure(String key) async => _data.remove(key);

  @override
  Future<bool> existsSecure(String key) async => _data.containsKey(key);

  @override
  Future<void> clearSecure() async => _data.clear();

  @override
  Future<List<String>> getAllSecureKeys() async => _data.keys.toList();
}

void main() {
  group('SecureStorageKeyManager', () {
    late _InMemorySecureStorage secureStorage;
    late KeyManager keyManager;

    setUp(() {
      secureStorage = _InMemorySecureStorage();
      keyManager = SecureStorageKeyManager(
        secureStorage: secureStorage,
        encryptionProvider: const NoopEncryptionProvider(),
      );
    });

    group('getOrCreateKey', () {
      test('creates a key when none exists', () async {
        final key = await keyManager.getOrCreateKey('test.key');
        expect(key, isNotEmpty);
      });

      test('returns the same key on subsequent calls', () async {
        final key1 = await keyManager.getOrCreateKey('test.key');
        final key2 = await keyManager.getOrCreateKey('test.key');
        expect(key1, equals(key2));
      });

      test('creates different keys for different keyIds', () async {
        // Use real AES-GCM provider so keys are random
        final realProvider = _RandomKeyProvider();
        final manager = SecureStorageKeyManager(
          secureStorage: secureStorage,
          encryptionProvider: realProvider,
        );

        final key1 = await manager.getOrCreateKey('key.a');
        final key2 = await manager.getOrCreateKey('key.b');
        expect(key1, isNot(equals(key2)));
      });
    });

    group('getKey', () {
      test('returns null when key does not exist', () async {
        final key = await keyManager.getKey('nonexistent');
        expect(key, isNull);
      });

      test('returns the stored key', () async {
        await keyManager.storeKey('test.key', [1, 2, 3, 4]);
        final key = await keyManager.getKey('test.key');
        expect(key, [1, 2, 3, 4]);
      });
    });

    group('storeKey', () {
      test('persists key bytes', () async {
        await keyManager.storeKey('test.key', [10, 20, 30]);
        final key = await keyManager.getKey('test.key');
        expect(key, [10, 20, 30]);
      });

      test('overwrites an existing key', () async {
        await keyManager.storeKey('test.key', [1, 2, 3]);
        await keyManager.storeKey('test.key', [4, 5, 6]);
        final key = await keyManager.getKey('test.key');
        expect(key, [4, 5, 6]);
      });
    });

    group('deleteKey', () {
      test('removes the key from storage', () async {
        await keyManager.storeKey('test.key', [1, 2, 3]);
        await keyManager.deleteKey('test.key');
        expect(await keyManager.keyExists('test.key'), isFalse);
      });

      test('is a no-op for non-existent keys', () async {
        await expectLater(
          keyManager.deleteKey('nonexistent'),
          completes,
        );
      });
    });

    group('keyExists', () {
      test('returns false when key is absent', () async {
        expect(await keyManager.keyExists('nonexistent'), isFalse);
      });

      test('returns true after key is stored', () async {
        await keyManager.storeKey('test.key', [1]);
        expect(await keyManager.keyExists('test.key'), isTrue);
      });
    });

    group('rotateKey', () {
      test('replaces the stored key', () async {
        await keyManager.storeKey('test.key', [1, 2, 3]);
        final newKey = await keyManager.rotateKey('test.key');
        final stored = await keyManager.getKey('test.key');
        expect(stored, equals(newKey));
      });

      test('returns the new key bytes', () async {
        await keyManager.storeKey('test.key', [1, 2, 3]);
        final newKey = await keyManager.rotateKey('test.key');
        expect(newKey, isNotEmpty);
      });
    });

    group('storage key namespacing', () {
      test('different keyIds do not collide in secure storage', () async {
        await keyManager.storeKey('a', [1]);
        await keyManager.storeKey('b', [2]);
        expect(await keyManager.getKey('a'), [1]);
        expect(await keyManager.getKey('b'), [2]);
      });
    });
  });
}

/// A key provider that generates distinct random keys (counter-based) for
/// testing isolation between different keyIds.
class _RandomKeyProvider extends NoopEncryptionProvider {
  int _counter = 0;

  @override
  Future<List<int>> generateKey() async {
    _counter++;
    return List.filled(32, _counter);
  }
}
