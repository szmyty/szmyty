import 'package:egohygiene/shared/services/encryption_manager.dart';
import 'package:egohygiene/shared/services/impl/encrypted_storage_service.dart';
import 'package:egohygiene/shared/services/impl/noop_encryption_provider.dart';
import 'package:egohygiene/shared/services/key_manager.dart';
import 'package:egohygiene/shared/storage/encryption_exception.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../helpers/fake_storage_service.dart';

class _InMemoryKeyManager implements KeyManager {
  final Map<String, List<int>> _keys = {};
  final _provider = const NoopEncryptionProvider();

  @override
  Future<void> deleteKey(String keyId) async => _keys.remove(keyId);

  @override
  Future<List<int>?> getKey(String keyId) async => _keys[keyId];

  @override
  Future<List<int>> getOrCreateKey(String keyId) async {
    return _keys.putIfAbsent(
      keyId,
      () => List<int>.filled(32, keyId.hashCode & 0xFF),
    );
  }

  @override
  Future<bool> keyExists(String keyId) async => _keys.containsKey(keyId);

  @override
  Future<List<int>> rotateKey(String keyId) async {
    final key = await _provider.generateKey();
    _keys[keyId] = key;
    return key;
  }

  @override
  Future<void> storeKey(String keyId, List<int> key) async {
    _keys[keyId] = key;
  }
}

void main() {
  group('EncryptedStorageService', () {
    late FakeStorageService backingStore;
    late EncryptedStorageService storage;

    setUp(() {
      backingStore = FakeStorageService();
      storage = EncryptedStorageService(
        storage: backingStore,
        encryptionManager: EncryptionManager(
          provider: const NoopEncryptionProvider(),
          keyManager: _InMemoryKeyManager(),
        ),
      );
    });

    test('round-trips plaintext while storing an encrypted envelope', () async {
      await storage.save('reflection.entries.v1', 'sensitive reflection');

      expect(
        await backingStore.get('reflection.entries.v1'),
        startsWith('enc:v1:'),
      );
      expect(
        await backingStore.get('reflection.entries.v1'),
        isNot('sensitive reflection'),
      );
      expect(
        await storage.get('reflection.entries.v1'),
        'sensitive reflection',
      );
    });

    test('migrates legacy plaintext values on first read', () async {
      await backingStore.save('check_in.entries.v1', 'legacy payload');

      expect(await storage.get('check_in.entries.v1'), 'legacy payload');
      expect(
        await backingStore.get('check_in.entries.v1'),
        startsWith('enc:v1:'),
      );
    });

    test('can opt out individual keys from encryption', () async {
      final passthrough = EncryptedStorageService(
        storage: backingStore,
        encryptionManager: EncryptionManager(
          provider: const NoopEncryptionProvider(),
          keyManager: _InMemoryKeyManager(),
        ),
        shouldEncrypt: (key) => key != 'onboarding.completed',
      );

      await passthrough.save('onboarding.completed', 'true');

      expect(await backingStore.get('onboarding.completed'), 'true');
      expect(await passthrough.get('onboarding.completed'), 'true');
    });

    test('throws when an encrypted envelope is malformed', () async {
      await backingStore.save('settings.v1.bad', 'enc:v1:not-base64');

      await expectLater(
        () => storage.get('settings.v1.bad'),
        throwsA(isA<DecryptionFailedException>()),
      );
    });

    test('delegates exists, delete, clear, and getAllKeys', () async {
      await storage.save('key.a', 'value-a');
      await storage.save('key.b', 'value-b');

      expect(await storage.exists('key.a'), isTrue);
      expect(await storage.getAllKeys(), containsAll(['key.a', 'key.b']));

      await storage.delete('key.a');
      expect(await storage.exists('key.a'), isFalse);

      await storage.clear();
      expect(await storage.getAllKeys(), isEmpty);
    });
  });
}
