import 'package:egohygiene/shared/services/encryption_provider.dart';
import 'package:egohygiene/shared/services/impl/aes_gcm_encryption_provider.dart';
import 'package:egohygiene/shared/services/impl/noop_encryption_provider.dart';
import 'package:egohygiene/shared/storage/encrypted_payload.dart';
import 'package:egohygiene/shared/storage/encryption_exception.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AesGcmEncryptionProvider', () {
    late EncryptionProvider provider;

    setUp(() {
      provider = const AesGcmEncryptionProvider();
    });

    test('algorithmId is aes-gcm-256', () {
      expect(provider.algorithmId, 'aes-gcm-256');
    });

    test('generateKey returns 32 bytes', () async {
      final key = await provider.generateKey();
      expect(key.length, 32);
    });

    test('generateKey returns different values each call', () async {
      final key1 = await provider.generateKey();
      final key2 = await provider.generateKey();
      expect(key1, isNot(equals(key2)));
    });

    test('encrypt returns a payload with aes-gcm-256 algorithmId', () async {
      final key = await provider.generateKey();
      final payload = await provider.encrypt([1, 2, 3], key);
      expect(payload.algorithmId, 'aes-gcm-256');
    });

    test('encrypt produces non-empty ciphertext', () async {
      final key = await provider.generateKey();
      final payload = await provider.encrypt([1, 2, 3], key);
      expect(payload.ciphertext, isNotEmpty);
    });

    test('encrypt produces non-empty nonce', () async {
      final key = await provider.generateKey();
      final payload = await provider.encrypt([1, 2, 3], key);
      expect(payload.nonce, isNotEmpty);
    });

    test('encrypt produces non-empty mac', () async {
      final key = await provider.generateKey();
      final payload = await provider.encrypt([1, 2, 3], key);
      expect(payload.mac, isNotEmpty);
    });

    test('encrypt / decrypt round-trips bytes', () async {
      final key = await provider.generateKey();
      final plaintext = [10, 20, 30, 40, 50];
      final payload = await provider.encrypt(plaintext, key);
      final decrypted = await provider.decrypt(payload, key);
      expect(decrypted, plaintext);
    });

    test('each encrypt call produces a different ciphertext (random nonce)', () async {
      final key = await provider.generateKey();
      final plaintext = [1, 2, 3];
      final payload1 = await provider.encrypt(plaintext, key);
      final payload2 = await provider.encrypt(plaintext, key);
      expect(payload1.ciphertext, isNot(equals(payload2.ciphertext)));
    });

    test('decrypt throws DecryptionFailedException for wrong key', () async {
      final key1 = await provider.generateKey();
      final key2 = await provider.generateKey();
      final payload = await provider.encrypt([1, 2, 3], key1);
      expect(
        () => provider.decrypt(payload, key2),
        throwsA(isA<DecryptionFailedException>()),
      );
    });

    test('decrypt throws DecryptionFailedException for tampered ciphertext', () async {
      final key = await provider.generateKey();
      final payload = await provider.encrypt([1, 2, 3], key);
      final tampered = EncryptedPayload(
        ciphertext: List<int>.from(payload.ciphertext)..[0] ^= 0xFF,
        nonce: payload.nonce,
        mac: payload.mac,
        algorithmId: payload.algorithmId,
      );
      expect(
        () => provider.decrypt(tampered, key),
        throwsA(isA<DecryptionFailedException>()),
      );
    });

    test('decrypt throws UnsupportedAlgorithmException for unknown algorithmId', () async {
      final key = await provider.generateKey();
      final payload = await provider.encrypt([1, 2, 3], key);
      final wrongAlgo = EncryptedPayload(
        ciphertext: payload.ciphertext,
        nonce: payload.nonce,
        mac: payload.mac,
        algorithmId: 'chacha20-poly1305',
      );
      expect(
        () => provider.decrypt(wrongAlgo, key),
        throwsA(isA<UnsupportedAlgorithmException>()),
      );
    });
  });

  group('NoopEncryptionProvider', () {
    late EncryptionProvider provider;

    setUp(() {
      provider = const NoopEncryptionProvider();
    });

    test('algorithmId is noop', () {
      expect(provider.algorithmId, 'noop');
    });

    test('generateKey returns 32 zero bytes', () async {
      final key = await provider.generateKey();
      expect(key.length, 32);
      expect(key, everyElement(equals(0)));
    });

    test('encrypt / decrypt round-trips bytes unchanged', () async {
      final key = await provider.generateKey();
      final plaintext = [5, 10, 15];
      final payload = await provider.encrypt(plaintext, key);
      final decrypted = await provider.decrypt(payload, key);
      expect(decrypted, plaintext);
    });

    test('ciphertext equals plaintext (no encryption)', () async {
      final key = await provider.generateKey();
      final plaintext = [5, 10, 15];
      final payload = await provider.encrypt(plaintext, key);
      expect(payload.ciphertext, plaintext);
    });
  });
}
