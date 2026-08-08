import 'package:egohygiene/shared/services/storage_service.dart';

class FakeStorageService implements StorageService {
  final Map<String, String> _store = {};

  @override
  Future<void> clear() async => _store.clear();

  @override
  Future<void> delete(String key) async => _store.remove(key);

  @override
  Future<bool> exists(String key) async => _store.containsKey(key);

  @override
  Future<String?> get(String key) async => _store[key];

  @override
  Future<List<String>> getAllKeys() async => _store.keys.toList();

  @override
  Future<void> init() async {}

  @override
  Future<void> save(String key, String value) async => _store[key] = value;
}
