import 'package:egohygiene/features/reflection/domain/reflection_model.dart';
import 'package:egohygiene/features/reflection/domain/reflection_repository.dart';
import 'package:egohygiene/features/reflection/providers/reflection_providers.dart';
import 'package:egohygiene/shared/services/insight_feedback_service.dart';
import 'package:egohygiene/shared/services/insight_summarization_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeReflectionRepository implements ReflectionRepository {
  _FakeReflectionRepository({List<ReflectionModel>? seed}) : _items = [...?seed];

  final List<ReflectionModel> _items;

  @override
  Future<ReflectionModel> create({
    required String body,
    String? title,
    List<String> tags = const [],
  }) async {
    final now = DateTime.parse('2026-06-21T12:00:00.000Z');
    final created = ReflectionModel(
      id: 'created-${_items.length + 1}',
      createdAt: now,
      updatedAt: now,
      title: title,
      body: body,
      tags: tags,
    );
    _items.insert(0, created);
    return created;
  }

  @override
  Future<List<ReflectionModel>> getAll() async => [..._items];

  @override
  Future<ReflectionModel?> getById(String id) async {
    for (final item in _items) {
      if (item.id == id) {
        return item;
      }
    }

    return null;
  }

  @override
  Future<ReflectionModel> update(ReflectionModel reflection) async => reflection;

  @override
  Future<void> deleteById(String id) async {}
}

class _FakeInsightSummarizationService implements InsightSummarizationService {
  @override
  Future<List<String>> extractPossibleThemes({
    required String body,
    String? title,
    List<String> tags = const [],
  }) async {
    return ['clarity', 'pattern'];
  }

  @override
  Future<InsightSummary> summarizeReflection({
    required String body,
    String? title,
    List<String> tags = const [],
  }) async {
    return const InsightSummary(
      summary: 'Stub summary',
      possibleThemes: ['clarity', 'pattern'],
      isPlaceholder: true,
    );
  }
}

class _FakeInsightFeedbackService implements InsightFeedbackService {
  @override
  Future<InsightFeedback> generateReflectionFeedback({
    required String body,
    String? title,
    List<String> tags = const [],
  }) async {
    return const InsightFeedback(
      feedback: 'Stub feedback',
      followUpPrompts: ['Prompt one'],
      isPlaceholder: true,
    );
  }
}

void main() {
  group('reflection providers', () {
    test('loads reflections from repository', () async {
      final seed = ReflectionModel(
        id: 'seed',
        createdAt: DateTime.parse('2026-06-21T11:00:00.000Z'),
        updatedAt: DateTime.parse('2026-06-21T11:00:00.000Z'),
        body: 'Seed reflection',
      );

      final container = ProviderContainer(
        overrides: [
          reflectionRepositoryProvider.overrideWith(
            (ref) => _FakeReflectionRepository(seed: [seed]),
          ),
        ],
      );
      addTearDown(container.dispose);

      await container.read(reflectionsProvider.notifier).loadReflections();

      final state = container.read(reflectionsProvider);
      expect(state.requireValue, [seed]);
    });

    test('createReflection inserts reflection at top of state', () async {
      final container = ProviderContainer(
        overrides: [
          reflectionRepositoryProvider.overrideWith(
            (ref) => _FakeReflectionRepository(),
          ),
        ],
      );
      addTearDown(container.dispose);

      await container
          .read(reflectionsProvider.notifier)
          .createReflection(body: 'A newly created reflection', tags: const ['tag']);

      final state = container.read(reflectionsProvider);
      expect(state.requireValue, isNotEmpty);
      expect(state.requireValue.first.body, 'A newly created reflection');
      expect(state.requireValue.first.tags, const ['tag']);
    });

    test('reflectionByIdProvider resolves using repository', () async {
      final seed = ReflectionModel(
        id: 'seed-lookup',
        createdAt: DateTime.parse('2026-06-21T11:00:00.000Z'),
        updatedAt: DateTime.parse('2026-06-21T11:00:00.000Z'),
        body: 'Lookup reflection',
      );

      final container = ProviderContainer(
        overrides: [
          reflectionRepositoryProvider.overrideWith(
            (ref) => _FakeReflectionRepository(seed: [seed]),
          ),
        ],
      );
      addTearDown(container.dispose);

      final result = await container.read(reflectionByIdProvider(seed.id).future);
      expect(result, seed);
    });

    test('reflection insight hooks use shared insight services', () async {
      final seed = ReflectionModel(
        id: 'seed-insight',
        createdAt: DateTime.parse('2026-06-21T11:00:00.000Z'),
        updatedAt: DateTime.parse('2026-06-21T11:00:00.000Z'),
        title: 'A meaningful moment',
        body: 'I noticed a recurring pattern.',
        tags: const ['pattern'],
      );

      final container = ProviderContainer(
        overrides: [
          reflectionRepositoryProvider.overrideWith(
            (ref) => _FakeReflectionRepository(seed: [seed]),
          ),
          insightSummarizationServiceProvider.overrideWith(
            (ref) => _FakeInsightSummarizationService(),
          ),
          insightFeedbackServiceProvider.overrideWith(
            (ref) => _FakeInsightFeedbackService(),
          ),
        ],
      );
      addTearDown(container.dispose);

      final notifier = container.read(reflectionsProvider.notifier);

      final summary = await notifier.summarizeReflection(seed.id);
      final feedback = await notifier.generateReflectionFeedback(seed.id);
      final themes = await notifier.extractInsightThemes(seed.id);

      expect(summary?.summary, 'Stub summary');
      expect(summary?.possibleThemes, const ['clarity', 'pattern']);
      expect(feedback?.feedback, 'Stub feedback');
      expect(feedback?.followUpPrompts, const ['Prompt one']);
      expect(themes, const ['clarity', 'pattern']);
    });
  });
}
