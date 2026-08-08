import 'package:egohygiene/features/graph/presentation/graph_screen.dart';
import 'package:egohygiene/features/graph/presentation/widgets/relationship_card.dart';
import 'package:egohygiene/features/graph/providers/graph_feature_providers.dart';
import 'package:egohygiene/shared/graph/graph_engine.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod/misc.dart' show Override;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

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

GraphNode _node({
  required String id,
  required GraphNodeType type,
  String? label,
}) {
  final now = DateTime(2025, 6);
  return GraphNode(
    id: id,
    type: type,
    label: label ?? id,
    createdAt: now,
    updatedAt: now,
  );
}

GraphSnapshot _emptySnapshot() => GraphSnapshot.empty();

GraphSnapshot _snapshotWith({
  List<GraphNode> nodes = const [],
  List<GraphRelationship> relationships = const [],
}) {
  return GraphSnapshot(
    nodes: nodes,
    relationships: relationships,
    capturedAt: DateTime(2025, 6),
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  group('GraphScreen', () {
    testWidgets('shows loading indicator while snapshot is loading', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const GraphScreen(),
          overrides: [
            graphSummaryProvider.overrideWithValue(
              const AsyncValue<GraphSummary>.loading(),
            ),
            graphRelationshipViewModelsProvider.overrideWithValue(
              const AsyncValue<List<RelationshipViewModel>>.loading(),
            ),
          ],
        ),
      );

      await tester.pump(); // one frame — still loading
      expect(find.byType(CircularProgressIndicator), findsWidgets);
    });

    testWidgets('shows summary card with zero counts for empty graph', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const GraphScreen(),
          overrides: [
            graphSnapshotProvider.overrideWith(
              (ref) async => _emptySnapshot(),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // Summary section present
      expect(find.text('Graph Overview'), findsOneWidget);
      // Zero stats
      expect(find.text('0'), findsAtLeastNWidgets(2));
    });

    testWidgets('shows empty state message when no relationships exist', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const GraphScreen(),
          overrides: [
            graphSnapshotProvider.overrideWith(
              (ref) async => _emptySnapshot(),
            ),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('No relationships yet'), findsOneWidget);
    });

    testWidgets('renders RelationshipCard for each resolved relationship', (tester) async {
      final domainNode = _node(id: 'd1', type: GraphNodeType.domain, label: 'Mental Health');
      final practiceNode = _node(id: 'p1', type: GraphNodeType.practice, label: 'Meditation');
      final snapshot = _snapshotWith(
        nodes: [domainNode, practiceNode],
        relationships: [
          GraphRelationship(
            id: 'r1',
            sourceId: practiceNode.id,
            targetId: domainNode.id,
            type: GraphRelationshipType.influences,
            createdAt: DateTime(2025, 6),
          ),
        ],
      );

      await tester.pumpWidget(
        _wrap(
          const GraphScreen(),
          overrides: [
            graphSnapshotProvider.overrideWith((ref) async => snapshot),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(RelationshipCard), findsOneWidget);
      expect(find.text('Mental Health'), findsOneWidget);
      expect(find.text('Meditation'), findsOneWidget);
    });

    testWidgets('excludes relationships with unresolvable node endpoints', (tester) async {
      // Relationship whose target node is not in the snapshot
      final practiceNode = _node(id: 'p1', type: GraphNodeType.practice, label: 'Yoga');
      final snapshot = _snapshotWith(
        nodes: [practiceNode],
        relationships: [
          GraphRelationship(
            id: 'r1',
            sourceId: practiceNode.id,
            targetId: 'missing-node',
            type: GraphRelationshipType.relatesTo,
            createdAt: DateTime(2025, 6),
          ),
        ],
      );

      await tester.pumpWidget(
        _wrap(
          const GraphScreen(),
          overrides: [
            graphSnapshotProvider.overrideWith((ref) async => snapshot),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // No relationship cards should render
      expect(find.byType(RelationshipCard), findsNothing);
      // Empty state appears
      expect(find.text('No relationships yet'), findsOneWidget);
    });
  });
}
