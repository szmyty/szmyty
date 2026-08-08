import 'package:egohygiene/shared/graph/graph_engine.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

GraphNode _node({
  String id = 'node-1',
  GraphNodeType type = GraphNodeType.domain,
  String label = 'Test Node',
  List<String> tags = const [],
  DateTime? createdAt,
  DateTime? updatedAt,
}) {
  final now = DateTime(2025);
  return GraphNode(
    id: id,
    type: type,
    label: label,
    tags: tags,
    createdAt: createdAt ?? now,
    updatedAt: updatedAt ?? now,
  );
}

GraphRelationship _rel({
  String id = 'rel-1',
  String sourceId = 'node-1',
  String targetId = 'node-2',
  GraphRelationshipType type = GraphRelationshipType.relatesTo,
  double? weight,
  DateTime? createdAt,
}) {
  return GraphRelationship(
    id: id,
    sourceId: sourceId,
    targetId: targetId,
    type: type,
    weight: weight,
    createdAt: createdAt ?? DateTime(2025),
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── GraphNodeType ──────────────────────────────────────────────────────────

  group('GraphNodeType', () {
    test('has seven types', () {
      expect(GraphNodeType.values, hasLength(7));
    });

    test('contains all expected types', () {
      expect(
        GraphNodeType.values,
        containsAll([
          GraphNodeType.domain,
          GraphNodeType.practice,
          GraphNodeType.reflection,
          GraphNodeType.insight,
          GraphNodeType.goal,
          GraphNodeType.research,
          GraphNodeType.memory,
        ]),
      );
    });
  });

  // ── GraphRelationshipType ──────────────────────────────────────────────────

  group('GraphRelationshipType', () {
    test('has ten types', () {
      expect(GraphRelationshipType.values, hasLength(10));
    });

    test('contains all expected types', () {
      expect(
        GraphRelationshipType.values,
        containsAll([
          GraphRelationshipType.relatesTo,
          GraphRelationshipType.supports,
          GraphRelationshipType.contradicts,
          GraphRelationshipType.derivesFrom,
          GraphRelationshipType.influences,
          GraphRelationshipType.achieves,
          GraphRelationshipType.tracks,
          GraphRelationshipType.belongsTo,
          GraphRelationshipType.generated,
          GraphRelationshipType.informs,
        ]),
      );
    });
  });

  // ── GraphNode ──────────────────────────────────────────────────────────────

  group('GraphNode', () {
    test('constructs with required fields', () {
      final n = _node();
      expect(n.id, 'node-1');
      expect(n.type, GraphNodeType.domain);
      expect(n.label, 'Test Node');
      expect(n.tags, isEmpty);
      expect(n.properties, isEmpty);
    });

    test('copyWith replaces specified fields', () {
      final original = _node(id: 'orig', label: 'original');
      final updated = original.copyWith(label: 'updated', type: GraphNodeType.goal);
      expect(updated.id, 'orig');
      expect(updated.label, 'updated');
      expect(updated.type, GraphNodeType.goal);
    });

    test('copyWith preserves unspecified fields', () {
      final original = _node(id: 'x', tags: ['a', 'b']);
      final copy = original.copyWith(label: 'new label');
      expect(copy.tags, ['a', 'b']);
    });

    test('equality is based on id and type', () {
      final a = _node(id: 'x', type: GraphNodeType.practice);
      final b = _node(id: 'x', type: GraphNodeType.practice, label: 'different');
      expect(a, equals(b));
    });

    test('different id produces different identity', () {
      final a = _node(id: 'a');
      final b = _node(id: 'b');
      expect(a, isNot(equals(b)));
    });

    test('toString includes id, type, and label', () {
      final n = _node(id: 'abc', type: GraphNodeType.insight, label: 'My Insight');
      expect(n.toString(), contains('abc'));
      expect(n.toString(), contains('insight'));
      expect(n.toString(), contains('My Insight'));
    });
  });

  // ── GraphRelationship ──────────────────────────────────────────────────────

  group('GraphRelationship', () {
    test('constructs with required fields', () {
      final r = _rel();
      expect(r.id, 'rel-1');
      expect(r.sourceId, 'node-1');
      expect(r.targetId, 'node-2');
      expect(r.type, GraphRelationshipType.relatesTo);
      expect(r.weight, isNull);
      expect(r.properties, isEmpty);
    });

    test('copyWith replaces specified fields', () {
      final original = _rel(id: 'r1');
      final updated = original.copyWith(
        type: GraphRelationshipType.supports,
        weight: 0.8,
      );
      expect(updated.id, 'r1');
      expect(updated.type, GraphRelationshipType.supports);
      expect(updated.weight, 0.8);
    });

    test('equality is based on id, sourceId, and targetId', () {
      final a = _rel(id: 'r', sourceId: 's', targetId: 't');
      final b = _rel(id: 'r', sourceId: 's', targetId: 't', weight: 0.5);
      expect(a, equals(b));
    });

    test('different id produces different identity', () {
      final a = _rel(id: 'r1');
      final b = _rel(id: 'r2');
      expect(a, isNot(equals(b)));
    });

    test('toString includes id, sourceId, targetId, and type', () {
      final r = _rel(
        id: 'edge-1',
        sourceId: 'a',
        targetId: 'b',
        type: GraphRelationshipType.influences,
      );
      expect(r.toString(), contains('edge-1'));
      expect(r.toString(), contains('influences'));
    });
  });

  // ── InMemoryGraphStore ─────────────────────────────────────────────────────

  group('InMemoryGraphStore', () {
    late InMemoryGraphStore store;

    setUp(() async {
      store = InMemoryGraphStore();
      await store.init();
    });

    // ── init ──

    test('init() completes without error', () async {
      await expectLater(store.init(), completes);
    });

    // ── nodes ──

    test('starts with zero nodes', () async {
      expect(await store.nodeCount(), 0);
      expect(await store.findAllNodes(), isEmpty);
    });

    test('saveNode() persists a node', () async {
      await store.saveNode(_node(id: 'n1'));
      expect(await store.nodeCount(), 1);
    });

    test('saveNode() returns the persisted node', () async {
      final n = _node(id: 'ret');
      final result = await store.saveNode(n);
      expect(result.id, 'ret');
    });

    test('saveNode() replaces existing node with same id', () async {
      await store.saveNode(_node(id: 'dup', label: 'first'));
      await store.saveNode(_node(id: 'dup', label: 'second'));
      expect(await store.nodeCount(), 1);
      final result = await store.findNodeById('dup');
      expect(result!.label, 'second');
    });

    test('findNodeById() returns the saved node', () async {
      await store.saveNode(_node(id: 'find-me'));
      final result = await store.findNodeById('find-me');
      expect(result, isNotNull);
      expect(result!.id, 'find-me');
    });

    test('findNodeById() returns null for unknown id', () async {
      expect(await store.findNodeById('ghost'), isNull);
    });

    test('findAllNodes() returns nodes ordered by createdAt ascending', () async {
      final t1 = DateTime(2025);
      final t2 = DateTime(2025, 1, 2);
      final t3 = DateTime(2025, 1, 3);

      await store.saveNode(_node(id: 'c', createdAt: t3, updatedAt: t3));
      await store.saveNode(_node(id: 'a', createdAt: t1, updatedAt: t1));
      await store.saveNode(_node(id: 'b', createdAt: t2, updatedAt: t2));

      final all = await store.findAllNodes();
      expect(all.map((n) => n.id), ['a', 'b', 'c']);
    });

    test('findNodesByType() returns only matching nodes', () async {
      await store.saveNode(_node(id: '1'));
      await store.saveNode(_node(id: '2', type: GraphNodeType.practice));
      await store.saveNode(_node(id: '3'));

      final domains = await store.findNodesByType(GraphNodeType.domain);
      expect(domains, hasLength(2));
      expect(domains.every((n) => n.type == GraphNodeType.domain), isTrue);
    });

    test('findNodesByTag() returns only tagged nodes', () async {
      await store.saveNode(_node(id: '1', tags: ['health', 'core']));
      await store.saveNode(_node(id: '2', tags: ['core']));
      await store.saveNode(_node(id: '3', tags: ['other']));

      final coreNodes = await store.findNodesByTag('core');
      expect(coreNodes, hasLength(2));
    });

    test('deleteNode() removes the node', () async {
      await store.saveNode(_node(id: 'del-me'));
      await store.deleteNode('del-me');
      expect(await store.findNodeById('del-me'), isNull);
      expect(await store.nodeCount(), 0);
    });

    test('deleteNode() is a no-op for unknown id', () async {
      await expectLater(store.deleteNode('ghost'), completes);
    });

    test('deleteNode() cascades to relationships referencing the node', () async {
      await store.saveNode(_node(id: 'a'));
      await store.saveNode(_node(id: 'b'));
      await store.saveRelationship(_rel(id: 'r1', sourceId: 'a', targetId: 'b'));
      await store.saveRelationship(_rel(id: 'r2', sourceId: 'b', targetId: 'a'));

      await store.deleteNode('a');

      expect(await store.relationshipCount(), 0);
    });

    test('clearNodes() removes all nodes and relationships', () async {
      await store.saveNode(_node(id: 'a'));
      await store.saveNode(_node(id: 'b'));
      await store.saveRelationship(_rel(id: 'r1', sourceId: 'a', targetId: 'b'));
      await store.clearNodes();
      expect(await store.nodeCount(), 0);
      expect(await store.relationshipCount(), 0);
    });

    // ── relationships ──

    test('starts with zero relationships', () async {
      expect(await store.relationshipCount(), 0);
    });

    test('saveRelationship() persists a relationship', () async {
      await store.saveNode(_node(id: 'a'));
      await store.saveNode(_node(id: 'b'));
      await store.saveRelationship(_rel(sourceId: 'a', targetId: 'b'));
      expect(await store.relationshipCount(), 1);
    });

    test('saveRelationship() returns the persisted relationship', () async {
      final r = _rel(id: 'ret-r');
      final result = await store.saveRelationship(r);
      expect(result.id, 'ret-r');
    });

    test('saveRelationship() replaces existing with same id', () async {
      await store.saveRelationship(_rel(id: 'dup', weight: 0.5));
      await store.saveRelationship(_rel(id: 'dup', weight: 0.9));
      expect(await store.relationshipCount(), 1);
      final result = await store.findRelationshipById('dup');
      expect(result!.weight, 0.9);
    });

    test('findRelationshipById() returns null for unknown id', () async {
      expect(await store.findRelationshipById('ghost'), isNull);
    });

    test('findRelationshipsBySource() filters correctly', () async {
      await store.saveRelationship(_rel(id: 'r1', sourceId: 'a', targetId: 'b'));
      await store.saveRelationship(_rel(id: 'r2', sourceId: 'a', targetId: 'c'));
      await store.saveRelationship(_rel(id: 'r3', sourceId: 'b', targetId: 'a'));

      final fromA = await store.findRelationshipsBySource('a');
      expect(fromA, hasLength(2));
    });

    test('findRelationshipsByTarget() filters correctly', () async {
      await store.saveRelationship(_rel(id: 'r1', sourceId: 'a', targetId: 'b'));
      await store.saveRelationship(_rel(id: 'r2', sourceId: 'c', targetId: 'b'));
      await store.saveRelationship(_rel(id: 'r3', sourceId: 'b', targetId: 'a'));

      final toB = await store.findRelationshipsByTarget('b');
      expect(toB, hasLength(2));
    });

    test('findRelationshipsByType() filters correctly', () async {
      await store.saveRelationship(
        _rel(id: 'r1', type: GraphRelationshipType.supports),
      );
      await store.saveRelationship(
        _rel(id: 'r2', type: GraphRelationshipType.influences),
      );
      await store.saveRelationship(
        _rel(id: 'r3', type: GraphRelationshipType.supports),
      );

      final supports = await store.findRelationshipsByType(
        GraphRelationshipType.supports,
      );
      expect(supports, hasLength(2));
    });

    test('findRelationshipsByNode() returns outgoing and incoming', () async {
      await store.saveRelationship(_rel(id: 'r1', sourceId: 'a', targetId: 'b'));
      await store.saveRelationship(_rel(id: 'r2', sourceId: 'c', targetId: 'a'));
      await store.saveRelationship(_rel(id: 'r3', sourceId: 'b', targetId: 'c'));

      final nodeARels = await store.findRelationshipsByNode('a');
      expect(nodeARels, hasLength(2));
      expect(nodeARels.map((r) => r.id), containsAll(['r1', 'r2']));
    });

    test('deleteRelationship() removes the relationship', () async {
      await store.saveRelationship(_rel(id: 'del-r'));
      await store.deleteRelationship('del-r');
      expect(await store.findRelationshipById('del-r'), isNull);
    });

    test('deleteRelationship() is a no-op for unknown id', () async {
      await expectLater(store.deleteRelationship('ghost'), completes);
    });

    test('clearRelationships() removes only relationships, not nodes', () async {
      await store.saveNode(_node(id: 'n1'));
      await store.saveRelationship(_rel(id: 'r1'));
      await store.clearRelationships();
      expect(await store.relationshipCount(), 0);
      expect(await store.nodeCount(), 1);
    });
  });

  // ── GraphManager ───────────────────────────────────────────────────────────

  group('GraphManager', () {
    late InMemoryGraphStore store;
    late GraphManager manager;

    setUp(() async {
      store = InMemoryGraphStore();
      manager = GraphManager(store: store);
      await manager.initialize();
    });

    // ── initialization ──

    test('initialize() completes without error', () async {
      final m = GraphManager(store: InMemoryGraphStore());
      await expectLater(m.initialize(), completes);
    });

    test('calling initialize() twice is a no-op', () async {
      await expectLater(manager.initialize(), completes);
    });

    // ── addNode / findNode ──

    test('addNode() persists a node', () async {
      await manager.addNode(_node(id: 'n1'));
      expect(await manager.nodeCount, 1);
    });

    test('findNode() returns the node', () async {
      await manager.addNode(_node(id: 'find-this'));
      final result = await manager.findNode('find-this');
      expect(result, isNotNull);
      expect(result!.id, 'find-this');
    });

    test('findNode() returns null for unknown id', () async {
      expect(await manager.findNode('ghost'), isNull);
    });

    test('allNodes() returns all stored nodes', () async {
      await manager.addNode(_node(id: 'a'));
      await manager.addNode(_node(id: 'b'));
      final nodes = await manager.allNodes();
      expect(nodes, hasLength(2));
    });

    test('nodesByType() filters correctly', () async {
      await manager.addNode(_node(id: '1', type: GraphNodeType.practice));
      await manager.addNode(_node(id: '2', type: GraphNodeType.goal));
      final practices = await manager.nodesByType(GraphNodeType.practice);
      expect(practices, hasLength(1));
      expect(practices.first.type, GraphNodeType.practice);
    });

    test('nodesByTag() filters correctly', () async {
      await manager.addNode(_node(id: '1', tags: ['health']));
      await manager.addNode(_node(id: '2', tags: ['other']));
      final tagged = await manager.nodesByTag('health');
      expect(tagged, hasLength(1));
    });

    test('removeNode() removes the node', () async {
      await manager.addNode(_node(id: 'del'));
      await manager.removeNode('del');
      expect(await manager.findNode('del'), isNull);
    });

    // ── connect / findRelationship ──

    test('connect() persists a relationship', () async {
      await manager.connect(
        id: 'r1',
        sourceId: 'a',
        targetId: 'b',
        type: GraphRelationshipType.influences,
      );
      expect(await manager.relationshipCount, 1);
    });

    test('connect() returns the persisted relationship', () async {
      final r = await manager.connect(
        id: 'r2',
        sourceId: 'a',
        targetId: 'b',
        type: GraphRelationshipType.supports,
        weight: 0.7,
      );
      expect(r.id, 'r2');
      expect(r.type, GraphRelationshipType.supports);
      expect(r.weight, 0.7);
    });

    test('findRelationship() returns the relationship', () async {
      await manager.connect(
        id: 'find-r',
        sourceId: 'x',
        targetId: 'y',
        type: GraphRelationshipType.relatesTo,
      );
      final result = await manager.findRelationship('find-r');
      expect(result, isNotNull);
      expect(result!.id, 'find-r');
    });

    test('findRelationship() returns null for unknown id', () async {
      expect(await manager.findRelationship('ghost'), isNull);
    });

    test('outgoing() returns only outgoing edges', () async {
      await manager.connect(
        id: 'r1',
        sourceId: 'a',
        targetId: 'b',
        type: GraphRelationshipType.relatesTo,
      );
      await manager.connect(
        id: 'r2',
        sourceId: 'c',
        targetId: 'a',
        type: GraphRelationshipType.relatesTo,
      );

      final out = await manager.outgoing('a');
      expect(out, hasLength(1));
      expect(out.first.id, 'r1');
    });

    test('incoming() returns only incoming edges', () async {
      await manager.connect(
        id: 'r1',
        sourceId: 'a',
        targetId: 'b',
        type: GraphRelationshipType.relatesTo,
      );
      await manager.connect(
        id: 'r2',
        sourceId: 'c',
        targetId: 'b',
        type: GraphRelationshipType.relatesTo,
      );

      final inc = await manager.incoming('b');
      expect(inc, hasLength(2));
    });

    test('removeRelationship() removes the relationship', () async {
      await manager.connect(
        id: 'del-r',
        sourceId: 'x',
        targetId: 'y',
        type: GraphRelationshipType.relatesTo,
      );
      await manager.removeRelationship('del-r');
      expect(await manager.findRelationship('del-r'), isNull);
    });

    test('relationshipsByType() filters correctly', () async {
      await manager.connect(
        id: 'r1',
        sourceId: 'a',
        targetId: 'b',
        type: GraphRelationshipType.achieves,
      );
      await manager.connect(
        id: 'r2',
        sourceId: 'b',
        targetId: 'c',
        type: GraphRelationshipType.tracks,
      );
      final achieves = await manager.relationshipsByType(
        GraphRelationshipType.achieves,
      );
      expect(achieves, hasLength(1));
    });

    // ── many-to-many ──

    test('many-to-many: a node can have multiple outgoing edges', () async {
      await manager.connect(
        id: 'r1',
        sourceId: 'a',
        targetId: 'b',
        type: GraphRelationshipType.relatesTo,
      );
      await manager.connect(
        id: 'r2',
        sourceId: 'a',
        targetId: 'c',
        type: GraphRelationshipType.relatesTo,
      );
      await manager.connect(
        id: 'r3',
        sourceId: 'a',
        targetId: 'd',
        type: GraphRelationshipType.relatesTo,
      );

      final out = await manager.outgoing('a');
      expect(out, hasLength(3));
    });

    test('many-to-many: a node can have multiple incoming edges', () async {
      await manager.connect(
        id: 'r1',
        sourceId: 'a',
        targetId: 'z',
        type: GraphRelationshipType.relatesTo,
      );
      await manager.connect(
        id: 'r2',
        sourceId: 'b',
        targetId: 'z',
        type: GraphRelationshipType.relatesTo,
      );

      final inc = await manager.incoming('z');
      expect(inc, hasLength(2));
    });

    // ── traversal ──

    test('relationshipsOf() returns both directions', () async {
      await manager.connect(
        id: 'r1',
        sourceId: 'hub',
        targetId: 'leaf1',
        type: GraphRelationshipType.relatesTo,
      );
      await manager.connect(
        id: 'r2',
        sourceId: 'leaf2',
        targetId: 'hub',
        type: GraphRelationshipType.relatesTo,
      );

      final rels = await manager.relationshipsOf('hub');
      expect(rels, hasLength(2));
    });

    test('neighborsOf() returns directly connected nodes', () async {
      await manager.addNode(_node(id: 'center'));
      await manager.addNode(_node(id: 'left'));
      await manager.addNode(_node(id: 'right'));

      await manager.connect(
        id: 'r1',
        sourceId: 'center',
        targetId: 'left',
        type: GraphRelationshipType.relatesTo,
      );
      await manager.connect(
        id: 'r2',
        sourceId: 'right',
        targetId: 'center',
        type: GraphRelationshipType.relatesTo,
      );

      final neighbors = await manager.neighborsOf('center');
      expect(neighbors, hasLength(2));
      expect(neighbors.map((n) => n.id), containsAll(['left', 'right']));
    });

    test('neighborsOf() returns empty list when node has no edges', () async {
      await manager.addNode(_node(id: 'isolated'));
      final neighbors = await manager.neighborsOf('isolated');
      expect(neighbors, isEmpty);
    });

    // ── snapshot ──

    test('snapshot() captures all nodes and relationships', () async {
      await manager.addNode(_node(id: 'a'));
      await manager.addNode(_node(id: 'b'));
      await manager.connect(
        id: 'r1',
        sourceId: 'a',
        targetId: 'b',
        type: GraphRelationshipType.relatesTo,
      );

      final snap = await manager.snapshot();
      expect(snap.nodeCount, 2);
      expect(snap.relationshipCount, 1);
    });

    test('snapshot() returns an empty snapshot when graph is empty', () async {
      final snap = await manager.snapshot();
      expect(snap.isEmpty, isTrue);
      expect(snap.nodeCount, 0);
      expect(snap.relationshipCount, 0);
    });

    test('snapshot() captures the moment it was taken', () async {
      final before = DateTime.now();
      final snap = await manager.snapshot();
      final after = DateTime.now();
      expect(
        snap.capturedAt.isAfter(before) || snap.capturedAt.isAtSameMomentAs(before),
        isTrue,
      );
      expect(
        snap.capturedAt.isBefore(after) || snap.capturedAt.isAtSameMomentAs(after),
        isTrue,
      );
    });
  });

  // ── GraphSnapshot ──────────────────────────────────────────────────────────

  group('GraphSnapshot', () {
    test('empty() produces a snapshot with no nodes or relationships', () {
      final snap = GraphSnapshot.empty();
      expect(snap.isEmpty, isTrue);
      expect(snap.nodeCount, 0);
      expect(snap.relationshipCount, 0);
    });

    test('isNotEmpty is true when nodes are present', () {
      final snap = GraphSnapshot(
        nodes: [_node()],
        relationships: const [],
        capturedAt: DateTime.now(),
      );
      expect(snap.isNotEmpty, isTrue);
    });

    test('nodesOfType() filters by GraphNodeType', () {
      final snap = GraphSnapshot(
        nodes: [
          _node(id: '1'),
          _node(id: '2', type: GraphNodeType.practice),
          _node(id: '3'),
        ],
        relationships: const [],
        capturedAt: DateTime.now(),
      );
      expect(snap.nodesOfType(GraphNodeType.domain), hasLength(2));
      expect(snap.nodesOfType(GraphNodeType.practice), hasLength(1));
    });

    test('relationshipsOfType() filters by GraphRelationshipType', () {
      final snap = GraphSnapshot(
        nodes: const [],
        relationships: [
          _rel(id: 'r1', type: GraphRelationshipType.supports),
          _rel(id: 'r2', type: GraphRelationshipType.influences),
          _rel(id: 'r3', type: GraphRelationshipType.supports),
        ],
        capturedAt: DateTime.now(),
      );
      expect(
        snap.relationshipsOfType(GraphRelationshipType.supports),
        hasLength(2),
      );
    });

    test('toString includes nodeCount, relationshipCount, and capturedAt', () {
      final capturedAt = DateTime(2025, 6);
      final snap = GraphSnapshot(
        nodes: [_node()],
        relationships: [_rel()],
        capturedAt: capturedAt,
      );
      expect(snap.toString(), contains('1'));
      expect(snap.toString(), contains('2025'));
    });
  });

  // ── GraphStore contract (abstract behavior via InMemoryGraphStore) ─────────

  group('GraphStore contract', () {
    late GraphStore store;

    setUp(() async {
      store = InMemoryGraphStore();
      await store.init();
    });

    test('saveNode returns the persisted node', () async {
      final n = _node(id: 'ret');
      final result = await store.saveNode(n);
      expect(result.id, 'ret');
    });

    test('nodeCount is zero after clearNodes', () async {
      await store.saveNode(_node());
      await store.clearNodes();
      expect(await store.nodeCount(), 0);
    });

    test('saveRelationship returns the persisted relationship', () async {
      final r = _rel(id: 'ret-r');
      final result = await store.saveRelationship(r);
      expect(result.id, 'ret-r');
    });

    test('relationshipCount is zero after clearRelationships', () async {
      await store.saveRelationship(_rel());
      await store.clearRelationships();
      expect(await store.relationshipCount(), 0);
    });
  });
}
