import 'package:egohygiene/features/memory/presentation/memory_screen.dart';
import 'package:egohygiene/features/memory/presentation/widgets/memory_card.dart';
import 'package:egohygiene/features/memory/providers/memory_providers.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/memory/memory.dart';
import 'package:egohygiene/shared/memory/memory_type.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:riverpod/misc.dart' show Override;

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

Memory _memory({
  String id = 'mem-1',
  MemoryType type = MemoryType.episodic,
  String content = 'Test memory content',
  String? source,
  List<String> tags = const [],
  double confidence = 1.0,
  DateTime? createdAt,
}) {
  final now = DateTime(2025, 6);
  return Memory(
    id: id,
    type: type,
    content: content,
    source: source,
    tags: tags,
    confidence: confidence,
    createdAt: createdAt ?? now,
    updatedAt: createdAt ?? now,
  );
}

Widget _wrap(Widget child, {List<Override> overrides = const []}) {
  return ProviderScope(
    overrides: overrides,
    child: TranslationProvider(
      child: MaterialApp(
        theme: AppTheme.light(useGoogleFonts: false),
        home: child,
      ),
    ),
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  setUpAll(() async {
    await initializeDateFormatting('en');
  });

  group('MemoryScreen', () {
    testWidgets('shows loading indicator while memories are loading', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const MemoryScreen(),
          overrides: [
            filteredMemoriesProvider.overrideWithValue(
              const AsyncValue<List<Memory>>.loading(),
            ),
          ],
        ),
      );

      // Pump one frame — provider is still loading
      await tester.pump();

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows empty state when no memories are stored', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const MemoryScreen(),
          overrides: [
            memoriesProvider.overrideWith((ref) async => const <Memory>[]),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('No memories yet'), findsOneWidget);
    });

    testWidgets('renders a MemoryCard for each stored memory', (tester) async {
      final memories = [
        _memory(id: '1', content: 'First memory'),
        _memory(id: '2', content: 'Second memory'),
      ];

      await tester.pumpWidget(
        _wrap(
          const MemoryScreen(),
          overrides: [
            memoriesProvider.overrideWith((ref) async => memories),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(MemoryCard), findsNWidgets(2));
      expect(find.text('First memory'), findsOneWidget);
      expect(find.text('Second memory'), findsOneWidget);
    });

    testWidgets('shows error state when memories fail to load', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const MemoryScreen(),
          overrides: [
            memoriesProvider.overrideWith(
              (ref) async => throw Exception('Load failed'),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.error_outline_rounded), findsOneWidget);
      expect(find.text('Unable to load memories.'), findsOneWidget);
    });

    testWidgets('filter chips are rendered for all memory types', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const MemoryScreen(),
          overrides: [
            memoriesProvider.overrideWith((ref) async => const <Memory>[]),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('All'), findsOneWidget);
      expect(find.text('Episodic'), findsOneWidget);
      expect(find.text('Semantic'), findsOneWidget);
      expect(find.text('Preference'), findsOneWidget);
      expect(find.text('Journey'), findsOneWidget);
      expect(find.text('Relationship'), findsOneWidget);
    });

    testWidgets('tapping a type filter chip hides non-matching memories', (tester) async {
      final memories = [
        _memory(id: '1', content: 'Episodic memory'),
        _memory(id: '2', content: 'Semantic memory', type: MemoryType.semantic),
      ];

      await tester.pumpWidget(
        _wrap(
          const MemoryScreen(),
          overrides: [
            memoriesProvider.overrideWith((ref) async => memories),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // Both memories visible initially
      expect(find.text('Episodic memory'), findsOneWidget);
      expect(find.text('Semantic memory'), findsOneWidget);

      // Tap the "Episodic" filter chip
      await tester.tap(find.widgetWithText(FilterChip, 'Episodic'));
      await tester.pumpAndSettle();

      // Only episodic memory visible
      expect(find.text('Episodic memory'), findsOneWidget);
      expect(find.text('Semantic memory'), findsNothing);
    });

    testWidgets('tapping active filter chip removes the filter', (tester) async {
      final memories = [
        _memory(id: '1', content: 'Episodic memory'),
        _memory(id: '2', content: 'Semantic memory', type: MemoryType.semantic),
      ];

      await tester.pumpWidget(
        _wrap(
          const MemoryScreen(),
          overrides: [
            memoriesProvider.overrideWith((ref) async => memories),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // Apply and then remove the Episodic filter
      await tester.tap(find.widgetWithText(FilterChip, 'Episodic'));
      await tester.pumpAndSettle();

      expect(find.text('Semantic memory'), findsNothing);

      await tester.tap(find.widgetWithText(FilterChip, 'Episodic'));
      await tester.pumpAndSettle();

      // Both memories visible again
      expect(find.text('Episodic memory'), findsOneWidget);
      expect(find.text('Semantic memory'), findsOneWidget);
    });

    testWidgets('shows no-filter-results state when filter yields no matches', (tester) async {
      final memories = [
        _memory(id: '1', content: 'Episodic memory'),
      ];

      await tester.pumpWidget(
        _wrap(
          const MemoryScreen(),
          overrides: [
            memoriesProvider.overrideWith((ref) async => memories),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // Filter by Semantic — no matches
      await tester.tap(find.text('Semantic'));
      await tester.pumpAndSettle();

      expect(find.text('No memories match the selected filter.'), findsOneWidget);
    });
  });

  group('MemoryCard', () {
    testWidgets('renders memory content', (tester) async {
      final memory = _memory(content: 'A meaningful moment');

      await tester.pumpWidget(
        _wrap(MemoryCard(memory: memory)),
      );

      expect(find.text('A meaningful moment'), findsOneWidget);
    });

    testWidgets('renders source when provided', (tester) async {
      final memory = _memory(source: 'reflection');

      await tester.pumpWidget(
        _wrap(MemoryCard(memory: memory)),
      );

      expect(find.text('reflection'), findsOneWidget);
    });

    testWidgets('renders tags when provided', (tester) async {
      final memory = _memory(tags: ['growth', 'clarity']);

      await tester.pumpWidget(
        _wrap(MemoryCard(memory: memory)),
      );

      expect(find.text('growth'), findsOneWidget);
      expect(find.text('clarity'), findsOneWidget);
    });

    testWidgets('does not render confidence bar when confidence is 1.0', (tester) async {
      final memory = _memory();

      await tester.pumpWidget(
        _wrap(MemoryCard(memory: memory)),
      );

      expect(find.byType(LinearProgressIndicator), findsNothing);
    });

    testWidgets('renders confidence bar when confidence is less than 1.0', (tester) async {
      final memory = _memory(confidence: 0.75);

      await tester.pumpWidget(
        _wrap(MemoryCard(memory: memory)),
      );

      expect(find.byType(LinearProgressIndicator), findsOneWidget);
      expect(find.text('75%'), findsOneWidget);
    });
  });
}
