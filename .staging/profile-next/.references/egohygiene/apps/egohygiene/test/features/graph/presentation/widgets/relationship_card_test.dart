import 'package:egohygiene/features/graph/presentation/widgets/relationship_card.dart';
import 'package:egohygiene/features/graph/providers/graph_feature_providers.dart';
import 'package:egohygiene/shared/graph/graph_engine.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

GraphNode _node({
  required String id,
  required GraphNodeType type,
  required String label,
}) {
  final now = DateTime(2025, 6);
  return GraphNode(
    id: id,
    type: type,
    label: label,
    createdAt: now,
    updatedAt: now,
  );
}

GraphRelationship _rel({
  required String id,
  required String sourceId,
  required String targetId,
  required GraphRelationshipType type,
  double? weight,
}) {
  return GraphRelationship(
    id: id,
    sourceId: sourceId,
    targetId: targetId,
    type: type,
    weight: weight,
    createdAt: DateTime(2025, 6),
  );
}

RelationshipViewModel _viewModel({
  GraphRelationshipType relType = GraphRelationshipType.relatesTo,
  GraphNodeType sourceType = GraphNodeType.reflection,
  GraphNodeType targetType = GraphNodeType.insight,
  double? weight,
}) {
  final source = _node(id: 'src', type: sourceType, label: 'Source Label');
  final target = _node(id: 'tgt', type: targetType, label: 'Target Label');
  final rel = _rel(
    id: 'r1',
    sourceId: source.id,
    targetId: target.id,
    type: relType,
    weight: weight,
  );
  return RelationshipViewModel(
    relationship: rel,
    sourceNode: source,
    targetNode: target,
  );
}

Widget _wrap(Widget child) {
  return ProviderScope(
    child: TranslationProvider(
      child: MaterialApp(
        theme: AppTheme.light(useGoogleFonts: false),
        home: Scaffold(body: SingleChildScrollView(child: child)),
      ),
    ),
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  group('RelationshipCard', () {
    testWidgets('renders source and target node labels', (tester) async {
      await tester.pumpWidget(_wrap(RelationshipCard(viewModel: _viewModel())));
      await tester.pumpAndSettle();

      expect(find.text('Source Label'), findsOneWidget);
      expect(find.text('Target Label'), findsOneWidget);
    });

    testWidgets('renders relationship type badge', (tester) async {
      final vm = _viewModel(relType: GraphRelationshipType.supports);
      await tester.pumpWidget(_wrap(RelationshipCard(viewModel: vm)));
      await tester.pumpAndSettle();

      // The _RelationshipTypeBadge shows the type name
      expect(find.text('supports'), findsOneWidget);
    });

    testWidgets('renders weight indicator when weight is set', (tester) async {
      final vm = _viewModel(weight: 0.8);
      await tester.pumpWidget(_wrap(RelationshipCard(viewModel: vm)));
      await tester.pumpAndSettle();

      expect(find.text('80%'), findsOneWidget);
    });

    testWidgets('does not render weight indicator when weight is null', (tester) async {
      final vm = _viewModel();
      await tester.pumpWidget(_wrap(RelationshipCard(viewModel: vm)));
      await tester.pumpAndSettle();

      expect(find.text('%'), findsNothing);
    });

    testWidgets('renders GraphNodeTypeBadge for each endpoint', (tester) async {
      final vm = _viewModel(
        targetType: GraphNodeType.goal,
      );
      await tester.pumpWidget(_wrap(RelationshipCard(viewModel: vm)));
      await tester.pumpAndSettle();

      expect(find.byType(GraphNodeTypeBadge), findsNWidgets(2));
    });
  });

  group('GraphNodeTypeBadge', () {
    for (final type in GraphNodeType.values) {
      testWidgets('renders badge for $type', (tester) async {
        await tester.pumpWidget(
          _wrap(GraphNodeTypeBadge(type: type)),
        );
        await tester.pumpAndSettle();

        // The badge displays the type name text
        expect(find.text(type.name), findsOneWidget);
      });
    }
  });
}
