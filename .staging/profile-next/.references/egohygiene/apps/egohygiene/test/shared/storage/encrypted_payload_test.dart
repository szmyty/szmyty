import 'dart:convert';

import 'package:egohygiene/shared/storage/encrypted_payload.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('EncryptedPayload', () {
    const algorithmId = 'aes-gcm-256';
    final ciphertext = [1, 2, 3, 4, 5];
    final nonce = [10, 11, 12];
    final mac = [20, 21, 22, 23];

    EncryptedPayload makePayload({int version = 1}) => EncryptedPayload(
      ciphertext: ciphertext,
      nonce: nonce,
      mac: mac,
      algorithmId: algorithmId,
      version: version,
    );

    group('construction', () {
      test('stores all fields', () {
        final payload = makePayload();
        expect(payload.version, 1);
        expect(payload.algorithmId, algorithmId);
        expect(payload.ciphertext, ciphertext);
        expect(payload.nonce, nonce);
        expect(payload.mac, mac);
      });

      test('defaults version to 1', () {
        final payload = EncryptedPayload(
          ciphertext: ciphertext,
          nonce: nonce,
          mac: mac,
          algorithmId: algorithmId,
        );
        expect(payload.version, 1);
      });
    });

    group('toJson / fromJson', () {
      test('round-trips all fields', () {
        final payload = makePayload();
        final json = payload.toJson();
        final restored = EncryptedPayload.fromJson(json);

        expect(restored.version, payload.version);
        expect(restored.algorithmId, payload.algorithmId);
        expect(restored.ciphertext, payload.ciphertext);
        expect(restored.nonce, payload.nonce);
        expect(restored.mac, payload.mac);
      });

      test('toJson encodes bytes as Base64', () {
        final payload = makePayload();
        final json = payload.toJson();

        expect(json['ciphertext'], isA<String>());
        expect(json['nonce'], isA<String>());
        expect(json['mac'], isA<String>());
        // Verify round-trip decoding
        expect(base64Decode(json['ciphertext'] as String), ciphertext);
      });

      test('fromJson handles missing mac field', () {
        final json = {
          'version': 1,
          'algorithmId': algorithmId,
          'ciphertext': base64Encode(ciphertext),
          'nonce': base64Encode(nonce),
        };
        final payload = EncryptedPayload.fromJson(json);
        expect(payload.mac, isEmpty);
      });

      test('fromJson handles missing version field', () {
        final json = {
          'algorithmId': algorithmId,
          'ciphertext': base64Encode(ciphertext),
          'nonce': base64Encode(nonce),
          'mac': base64Encode(mac),
        };
        final payload = EncryptedPayload.fromJson(json);
        expect(payload.version, 1);
      });
    });

    group('toBase64 / fromBase64', () {
      test('round-trips through Base64', () {
        final payload = makePayload();
        final encoded = payload.toBase64();
        final restored = EncryptedPayload.fromBase64(encoded);

        expect(restored.version, payload.version);
        expect(restored.algorithmId, payload.algorithmId);
        expect(restored.ciphertext, payload.ciphertext);
        expect(restored.nonce, payload.nonce);
        expect(restored.mac, payload.mac);
      });

      test('toBase64 returns a valid Base64 string', () {
        final encoded = makePayload().toBase64();
        expect(() => base64Decode(encoded), returnsNormally);
      });
    });

    group('toString', () {
      test('contains algorithmId and byte counts', () {
        final s = makePayload().toString();
        expect(s, contains(algorithmId));
        expect(s, contains('ciphertextBytes: 5'));
        expect(s, contains('nonceBytes: 3'));
        expect(s, contains('macBytes: 4'));
      });
    });

    group('equality', () {
      test('equal payloads are ==', () {
        expect(makePayload(), equals(makePayload()));
      });

      test('different versions are not equal', () {
        expect(makePayload(), isNot(equals(makePayload(version: 2))));
      });

      test('different ciphertexts are not equal', () {
        final a = EncryptedPayload(
          ciphertext: [1],
          nonce: nonce,
          mac: mac,
          algorithmId: algorithmId,
        );
        final b = EncryptedPayload(
          ciphertext: [2],
          nonce: nonce,
          mac: mac,
          algorithmId: algorithmId,
        );
        expect(a, isNot(equals(b)));
      });

      test('equal payloads have the same hash code', () {
        expect(makePayload().hashCode, makePayload().hashCode);
      });
    });
  });
}
