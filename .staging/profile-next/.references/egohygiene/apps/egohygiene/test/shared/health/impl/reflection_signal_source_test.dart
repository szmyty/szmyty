import 'package:egohygiene/features/reflection/feature.dart';
import 'package:egohygiene/shared/health/impl/reflection_signal_source.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ReflectionSignalSource', () {
    test('sourceId is "reflection"', () {
      final source = ReflectionSignalSource(
        repository: _FakeReflectionRepository([]),
      );
      expect(source.sourceId, 'reflection');
    });

    test('displayName is human readable', () {
      final source = ReflectionSignalSource(
        repository: _FakeReflectionRepository([]),
      );
      expect(source.displayName, isNotEmpty);
    });

    test('collectTimestamps() returns empty map (reflections are global signals)', () async {
      final now = DateTime.utc(2026, 7, 3, 12);
      final source = ReflectionSignalSource(
        repository: _FakeReflectionRepository([
          _reflection('r1', now.subtract(const Duration(days: 1))),
          _reflection('r2', now.subtract(const Duration(days: 2))),
        ]),
      );

      final timestamps = await source.collectTimestamps();

      expect(timestamps, isEmpty);
    });

    test('collectReflectionTimestamps() returns createdAt for each reflection', () async {
      final now = DateTime.utc(2026, 7, 3, 12);
      final ts1 = now.subtract(const Duration(days: 1));
      final ts2 = now.subtract(const Duration(days: 3));

      final source = ReflectionSignalSource(
        repository: _FakeReflectionRepository([
          _reflection('r1', ts1),
          _reflection('r2', ts2),
        ]),
      );

      final timestamps = await source.collectReflectionTimestamps();

      expect(timestamps, containsAll([ts1, ts2]));
      expect(timestamps, hasLength(2));
    });

    test('collectReflectionTimestamps() returns empty list when no reflections', () async {
      final source = ReflectionSignalSource(
        repository: _FakeReflectionRepository([]),
      );

      final timestamps = await source.collectReflectionTimestamps();

      expect(timestamps, isEmpty);
    });

    test('collectReflectionTimestamps() suppresses repository failures', () async {
      final source = ReflectionSignalSource(
        repository: _ThrowingReflectionRepository(),
      );

      // Must not throw.
      final timestamps = await source.collectReflectionTimestamps();

      expect(timestamps, isEmpty);
    });

    test('collectPracticeTimestamps() returns empty list (practices are separate)', () async {
      final now = DateTime.utc(2026, 7, 3, 12);
      final source = ReflectionSignalSource(
        repository: _FakeReflectionRepository([
          _reflection('r1', now.subtract(const Duration(days: 1))),
        ]),
      );

      final timestamps = await source.collectPracticeTimestamps();

      expect(timestamps, isEmpty);
    });

    test('initialize() and dispose() complete without error', () async {
      final source = ReflectionSignalSource(
        repository: _FakeReflectionRepository([]),
      );

      await expectLater(source.initialize(), completes);
      await expectLater(source.dispose(), completes);
    });
  });
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

ReflectionModel _reflection(String id, DateTime createdAt) => ReflectionModel(
  id: id,
  createdAt: createdAt,
  updatedAt: createdAt,
  body: 'test reflection body',
);

class _FakeReflectionRepository implements ReflectionRepository {
  _FakeReflectionRepository(List<ReflectionModel> reflections) : _reflections = List<ReflectionModel>.of(reflections);

  final List<ReflectionModel> _reflections;

  @override
  Future<List<ReflectionModel>> getAll() async => _reflections;

  @override
  Future<ReflectionModel?> getById(String id) async => _reflections.where((r) => r.id == id).firstOrNull;

  @override
  Future<ReflectionModel> create({
    required String body,
    String? title,
    List<String> tags = const [],
  }) async {
    final now = DateTime.now();
    final model = ReflectionModel(
      id: 'fake_${now.microsecondsSinceEpoch}',
      createdAt: now,
      updatedAt: now,
      title: title,
      body: body,
      tags: tags,
    );
    _reflections.add(model);
    return model;
  }

  @override
  Future<ReflectionModel> update(ReflectionModel reflection) async => reflection;

  @override
  Future<void> deleteById(String id) async {
    _reflections.removeWhere((r) => r.id == id);
  }
}

class _ThrowingReflectionRepository implements ReflectionRepository {
  @override
  Future<List<ReflectionModel>> getAll() async => throw Exception('repository failure');

  @override
  Future<ReflectionModel?> getById(String id) async => null;

  @override
  Future<ReflectionModel> create({
    required String body,
    String? title,
    List<String> tags = const [],
  }) async => throw UnimplementedError();

  @override
  Future<ReflectionModel> update(ReflectionModel reflection) async => throw UnimplementedError();

  @override
  Future<void> deleteById(String id) async => throw UnimplementedError();
}
