import 'package:egohygiene/shared/storage/pageable.dart';
import 'package:egohygiene/shared/storage/repository.dart';
import 'package:egohygiene/shared/storage/storage_exception.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Minimal in-memory Repository implementation for tests.
// ---------------------------------------------------------------------------

class _Item {
  const _Item(this.id, this.value);
  final String id;
  final String value;

  @override
  bool operator ==(Object other) => identical(this, other) || other is _Item && id == other.id && value == other.value;

  @override
  int get hashCode => Object.hash(id, value);
}

class _ItemRepository implements Repository<_Item, String> {
  final Map<String, _Item> _store = {};

  @override
  Future<_Item?> findById(String id) async => _store[id];

  @override
  Future<List<_Item>> findAll() async => _store.values.toList();

  @override
  Future<_Item> save(_Item entity) async {
    _store[entity.id] = entity;
    return entity;
  }

  @override
  Future<void> deleteById(String id) async => _store.remove(id);

  @override
  Future<bool> existsById(String id) async => _store.containsKey(id);

  @override
  Future<int> count() async => _store.length;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  group('Repository contract', () {
    late _ItemRepository repository;

    setUp(() {
      repository = _ItemRepository();
    });

    test('save and findById round-trip', () async {
      const item = _Item('a', 'alpha');
      await repository.save(item);

      final found = await repository.findById('a');
      expect(found, item);
    });

    test('findById returns null for missing id', () async {
      final found = await repository.findById('missing');
      expect(found, isNull);
    });

    test('findAll returns all saved entities', () async {
      await repository.save(const _Item('x', 'x-value'));
      await repository.save(const _Item('y', 'y-value'));

      final all = await repository.findAll();
      expect(all, containsAll([const _Item('x', 'x-value'), const _Item('y', 'y-value')]));
    });

    test('save replaces existing entity with same id', () async {
      await repository.save(const _Item('a', 'original'));
      await repository.save(const _Item('a', 'updated'));

      final found = await repository.findById('a');
      expect(found, const _Item('a', 'updated'));
      expect(await repository.count(), 1);
    });

    test('deleteById removes entity', () async {
      await repository.save(const _Item('a', 'alpha'));
      await repository.deleteById('a');

      expect(await repository.findById('a'), isNull);
    });

    test('deleteById is a no-op for missing id', () async {
      await repository.deleteById('non-existent');
      expect(await repository.count(), 0);
    });

    test('existsById returns true after save', () async {
      await repository.save(const _Item('a', 'alpha'));
      expect(await repository.existsById('a'), isTrue);
    });

    test('existsById returns false for missing id', () async {
      expect(await repository.existsById('missing'), isFalse);
    });

    test('count reflects number of entities', () async {
      expect(await repository.count(), 0);
      await repository.save(const _Item('a', 'alpha'));
      expect(await repository.count(), 1);
      await repository.save(const _Item('b', 'beta'));
      expect(await repository.count(), 2);
      await repository.deleteById('a');
      expect(await repository.count(), 1);
    });
  });

  // -------------------------------------------------------------------------
  // PageRequest
  // -------------------------------------------------------------------------

  group('PageRequest', () {
    test('offset is page * size', () {
      const request = PageRequest(page: 2, size: 10);
      expect(request.offset, 20);
    });

    test('first page has offset 0', () {
      const request = PageRequest(page: 0, size: 25);
      expect(request.offset, 0);
    });

    test('next increments page', () {
      const request = PageRequest(page: 0, size: 10);
      expect(request.next().page, 1);
    });

    test('previous decrements page', () {
      const request = PageRequest(page: 3, size: 10);
      expect(request.previous().page, 2);
    });

    test('previous clamps to page 0', () {
      const request = PageRequest(page: 0, size: 10);
      expect(request.previous().page, 0);
    });

    test('equality', () {
      expect(
        const PageRequest(page: 1, size: 20),
        const PageRequest(page: 1, size: 20),
      );
      expect(
        const PageRequest(page: 1, size: 20),
        isNot(const PageRequest(page: 2, size: 20)),
      );
    });
  });

  // -------------------------------------------------------------------------
  // Page
  // -------------------------------------------------------------------------

  group('Page', () {
    test('totalPages is ceil(totalItems / size)', () {
      const page = Page<int>(
        items: [1, 2, 3],
        totalItems: 23,
        request: PageRequest(page: 0, size: 10),
      );
      expect(page.totalPages, 3);
    });

    test('totalPages is 0 when there are no items', () {
      const page = Page<int>(
        items: [],
        totalItems: 0,
        request: PageRequest(page: 0, size: 10),
      );
      expect(page.totalPages, 0);
    });

    test('hasNext is false on the last page', () {
      const page = Page<int>(
        items: [1],
        totalItems: 5,
        request: PageRequest(page: 4, size: 1),
      );
      expect(page.hasNext, isFalse);
      expect(page.isLast, isTrue);
    });

    test('hasNext is true when more pages exist', () {
      const page = Page<int>(
        items: [1, 2],
        totalItems: 10,
        request: PageRequest(page: 0, size: 2),
      );
      expect(page.hasNext, isTrue);
      expect(page.isLast, isFalse);
    });

    test('hasPrevious is false on the first page', () {
      const page = Page<int>(
        items: [1],
        totalItems: 5,
        request: PageRequest(page: 0, size: 1),
      );
      expect(page.hasPrevious, isFalse);
      expect(page.isFirst, isTrue);
    });

    test('hasPrevious is true on pages after the first', () {
      const page = Page<int>(
        items: [2],
        totalItems: 5,
        request: PageRequest(page: 1, size: 1),
      );
      expect(page.hasPrevious, isTrue);
      expect(page.isFirst, isFalse);
    });
  });

  // -------------------------------------------------------------------------
  // StorageException hierarchy
  // -------------------------------------------------------------------------

  group('StorageException hierarchy', () {
    test('EntityNotFoundException formats message', () {
      const ex = EntityNotFoundException(entityType: 'ReflectionModel', id: '42');
      expect(ex.toString(), contains('ReflectionModel'));
      expect(ex.toString(), contains('42'));
    });

    test('DuplicateEntityException formats message', () {
      const ex = DuplicateEntityException(entityType: 'Note', id: 'n1');
      expect(ex.toString(), contains('Note'));
      expect(ex.toString(), contains('n1'));
    });

    test('StorageUnavailableException carries message and cause', () {
      const cause = 'disk full';
      const ex = StorageUnavailableException('backend unreachable', cause: cause);
      expect(ex.message, 'backend unreachable');
      expect(ex.cause, cause);
      expect(ex.toString(), contains(cause));
    });

    test('MigrationException carries version range', () {
      const ex = MigrationException(
        'migration failed',
        fromVersion: 1,
        toVersion: 2,
      );
      expect(ex.fromVersion, 1);
      expect(ex.toVersion, 2);
    });

    test('StorageCorruptionException is a StorageException', () {
      const ex = StorageCorruptionException('bad json');
      expect(ex, isA<StorageException>());
    });
  });
}
