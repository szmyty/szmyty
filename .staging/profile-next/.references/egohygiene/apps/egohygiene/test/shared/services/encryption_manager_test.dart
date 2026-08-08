import 'package:egohygiene/shared/services/encryption_manager.dart';
import 'package:egohygiene/shared/services/impl/noop_encryption_provider.dart';
import 'package:egohygiene/shared/services/key_manager.dart';
import 'package:egohygiene/shared/storage/encrypted_payload.dart';
import 'package:egohygiene/shared/storage/encryption_exception.dart';
import 'package:flutter_test/flutter_test.dart';

/// In-memory [KeyManager] for testing.
class _InMemoryKeyManager implements KeyManager {
  final Map<String, List<int>> _keys = {};
  final _provider = const NoopEncryptionProvider();

  @override
  Future<List<int>> getOrCreateKey(String keyId) async {
    return _keys.putIfAbsent(
      keyId,
      () => List.filled(32, keyId.hashCode & 0xFF),
    );
  }

  @override
  Future<List<int>?> getKey(String keyId) async => _keys[keyId];

  @override
  Future<void> storeKey(String keyId, List<int> key) async {
    _keys[keyId] = key;
  }

  @override
  Future<void> deleteKey(String keyId) async => _keys.remove(keyId);

  @override
  Future<bool> keyExists(String keyId) async => _keys.containsKey(keyId);

  @override
  Future<List<int>> rotateKey(String keyId) async {
    final newKey = await _provider.generateKey();
    _keys[keyId] = newKey;
    return newKey;
  }
}

void main() {
  group('EncryptionManager', () {
    late EncryptionManager manager;

    setUp(() {
      manager = EncryptionManager(
        provider: const NoopEncryptionProvider(),
        keyManager: _InMemoryKeyManager(),
      );
    });

    group('encryptString / decryptString', () {
      test('round-trips a simple string', () async {
        const keyId = 'test.string';
        const plaintext = 'Hello, world!';

        final payload = await manager.encryptString(plaintext, keyId);
        final result = await manager.decryptString(payload, keyId);

        expect(result, plaintext);
      });

      test('round-trips an empty string', () async {
        const keyId = 'test.empty';
        const plaintext = '';

        final payload = await manager.encryptString(plaintext, keyId);
        final result = await manager.decryptString(payload, keyId);

        expect(result, plaintext);
      });

      test('round-trips a Unicode string', () async {
        const keyId = 'test.unicode';
        const plaintext = '🔑 encrypt me 🌿';

        final payload = await manager.encryptString(plaintext, keyId);
        final result = await manager.decryptString(payload, keyId);

        expect(result, plaintext);
      });

      test('returns an EncryptedPayload', () async {
        final payload = await manager.encryptString('text', 'test.key');
        expect(payload, isA<EncryptedPayload>());
      });

      test('throws KeyNotFoundException when decrypting with unknown keyId', () async {
        final payload = await manager.encryptString('text', 'known.key');
        expect(
          () => manager.decryptString(payload, 'unknown.key'),
          throwsA(isA<KeyNotFoundException>()),
        );
      });

      test('different keyIds produce different payloads', () async {
        final payload1 = await manager.encryptString('text', 'key.a');
        final payload2 = await manager.encryptString('text', 'key.b');
        expect(payload1, isA<EncryptedPayload>());
        expect(payload2, isA<EncryptedPayload>());
      });
    });

    group('encryptBytes / decryptBytes', () {
      test('round-trips raw bytes', () async {
        const keyId = 'test.bytes';
        final plaintext = [1, 2, 3, 4, 5];

        final payload = await manager.encryptBytes(plaintext, keyId);
        final result = await manager.decryptBytes(payload, keyId);

        expect(result, plaintext);
      });

      test('round-trips empty bytes', () async {
        const keyId = 'test.empty.bytes';
        final payload = await manager.encryptBytes([], keyId);
        final result = await manager.decryptBytes(payload, keyId);
        expect(result, isEmpty);
      });
    });
  });
}
