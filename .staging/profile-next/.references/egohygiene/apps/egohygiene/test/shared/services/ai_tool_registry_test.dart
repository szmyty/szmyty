import 'package:egohygiene/shared/providers/ai_tool_registry_providers.dart';
import 'package:egohygiene/shared/services/ai_tool.dart';
import 'package:egohygiene/shared/services/impl/demo_tools.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Minimal fake tool for registry-level tests
// ---------------------------------------------------------------------------

class _FakeTool implements Tool {
  const _FakeTool({
    required this.id,
    required this.name,
    required this.description,
  });

  @override
  final String id;

  @override
  final String name;

  @override
  final String description;

  @override
  Set<ToolCapability> get capabilities => const {
    ToolCapability.local,
  };

  @override
  List<ToolParameter> get parameters => const [];

  @override
  Future<ToolResult> invoke(ToolInvocation invocation) async {
    return ToolResult(
      invocationId: invocation.invocationId,
      output: 'fake output for ${invocation.toolId}',
    );
  }
}

void main() {
  // -------------------------------------------------------------------------
  // ToolCapability
  // -------------------------------------------------------------------------

  group('ToolCapability', () {
    test('all expected values are present', () {
      expect(
        ToolCapability.values,
        containsAll(<ToolCapability>[
          ToolCapability.mcp,
          ToolCapability.functionCalling,
          ToolCapability.structuredOutputs,
          ToolCapability.local,
          ToolCapability.remote,
        ]),
      );
    });
  });

  // -------------------------------------------------------------------------
  // ToolParameter
  // -------------------------------------------------------------------------

  group('ToolParameter', () {
    test('defaults type to string and required to false', () {
      const param = ToolParameter(name: 'x', description: 'desc');
      expect(param.type, 'string');
      expect(param.required, isFalse);
    });

    test('stores custom type and required flag', () {
      const param = ToolParameter(
        name: 'count',
        description: 'items',
        type: 'number',
        required: true,
      );
      expect(param.type, 'number');
      expect(param.required, isTrue);
    });
  });

  // -------------------------------------------------------------------------
  // ToolInvocation
  // -------------------------------------------------------------------------

  group('ToolInvocation', () {
    test('stores toolId, invocationId, and parameters', () {
      const invocation = ToolInvocation(
        toolId: 'my_tool',
        invocationId: 'inv-1',
        parameters: <String, Object?>{'key': 'value'},
      );

      expect(invocation.toolId, 'my_tool');
      expect(invocation.invocationId, 'inv-1');
      expect(invocation.parameters, <String, Object?>{'key': 'value'});
    });

    test('parameters default to empty map', () {
      const invocation = ToolInvocation(
        toolId: 'tool',
        invocationId: 'inv-2',
      );
      expect(invocation.parameters, isEmpty);
    });
  });

  // -------------------------------------------------------------------------
  // ToolResult
  // -------------------------------------------------------------------------

  group('ToolResult', () {
    test('defaults to success, not placeholder', () {
      const result = ToolResult(invocationId: 'inv-1', output: 'ok');
      expect(result.isSuccess, isTrue);
      expect(result.isPlaceholder, isFalse);
      expect(result.error, isNull);
    });

    test('failure factory sets isSuccess false and empty output', () {
      final result = ToolResult.failure(
        invocationId: 'inv-2',
        error: 'something went wrong',
      );
      expect(result.isSuccess, isFalse);
      expect(result.output, isEmpty);
      expect(result.error, 'something went wrong');
    });

    test('failure factory stores metadata', () {
      final result = ToolResult.failure(
        invocationId: 'inv-3',
        error: 'err',
        metadata: <String, Object?>{'code': 404},
      );
      expect(result.metadata['code'], 404);
    });

    test('stores output and invocationId', () {
      const result = ToolResult(invocationId: 'inv-4', output: 'hello');
      expect(result.output, 'hello');
      expect(result.invocationId, 'inv-4');
    });
  });

  // -------------------------------------------------------------------------
  // ToolRegistry
  // -------------------------------------------------------------------------

  group('ToolRegistry', () {
    test('register() and contains() work correctly', () {
      final registry = ToolRegistry()
        ..register(
          const _FakeTool(id: 'a', name: 'A', description: 'desc'),
        );

      expect(registry.contains('a'), isTrue);
      expect(registry.contains('b'), isFalse);
    });

    test('byId() returns the registered tool', () {
      const tool = _FakeTool(id: 'x', name: 'X', description: 'desc');
      final registry = ToolRegistry()..register(tool);

      expect(registry.byId('x')?.name, 'X');
    });

    test('byId() returns null for unknown id', () {
      expect(ToolRegistry().byId('missing'), isNull);
    });

    test('registerAll() registers multiple tools', () {
      final registry = ToolRegistry()
        ..registerAll(const [
          _FakeTool(id: 'p', name: 'P', description: 'desc'),
          _FakeTool(id: 'q', name: 'Q', description: 'desc'),
        ]);

      expect(registry.contains('p'), isTrue);
      expect(registry.contains('q'), isTrue);
    });

    test('all returns all registered tools', () {
      final registry = ToolRegistry()
        ..registerAll(const [
          _FakeTool(id: '1', name: '1', description: 'desc'),
          _FakeTool(id: '2', name: '2', description: 'desc'),
        ]);

      expect(registry.all, hasLength(2));
    });

    test('registering the same id replaces the previous tool', () {
      final registry = ToolRegistry()
        ..register(const _FakeTool(id: 'dup', name: 'First', description: ''))
        ..register(const _FakeTool(id: 'dup', name: 'Second', description: ''));

      expect(registry.all, hasLength(1));
      expect(registry.byId('dup')?.name, 'Second');
    });

    test('invoke() routes to correct tool', () async {
      final registry = ToolRegistry()..register(const _FakeTool(id: 'echo', name: 'Echo', description: ''));

      final result = await registry.invoke(
        const ToolInvocation(toolId: 'echo', invocationId: 'inv-echo'),
      );

      expect(result.isSuccess, isTrue);
      expect(result.invocationId, 'inv-echo');
      expect(result.output, contains('echo'));
    });

    test('invoke() returns failure for unknown tool', () async {
      final result = await ToolRegistry().invoke(
        const ToolInvocation(toolId: 'ghost', invocationId: 'inv-ghost'),
      );

      expect(result.isSuccess, isFalse);
      expect(result.invocationId, 'inv-ghost');
      expect(result.error, contains('ghost'));
    });
  });

  // -------------------------------------------------------------------------
  // Demo tools
  // -------------------------------------------------------------------------

  group('ReflectionTool', () {
    const tool = ReflectionTool();

    test('has correct id and name', () {
      expect(tool.id, 'reflection');
      expect(tool.name, 'Reflection');
    });

    test('supports local capability', () {
      expect(tool.capabilities, contains(ToolCapability.local));
    });

    test('invoke returns placeholder result', () async {
      final result = await tool.invoke(
        const ToolInvocation(toolId: 'reflection', invocationId: 'r-1'),
      );

      expect(result.isSuccess, isTrue);
      expect(result.isPlaceholder, isTrue);
      expect(result.invocationId, 'r-1');
      expect(result.output, isNotEmpty);
    });
  });

  group('TimelineTool', () {
    const tool = TimelineTool();

    test('has correct id', () => expect(tool.id, 'timeline'));

    test('invoke returns placeholder result', () async {
      final result = await tool.invoke(
        const ToolInvocation(toolId: 'timeline', invocationId: 't-1'),
      );

      expect(result.isPlaceholder, isTrue);
      expect(result.isSuccess, isTrue);
    });
  });

  group('PracticeTool', () {
    const tool = PracticeTool();

    test('has correct id', () => expect(tool.id, 'practice'));

    test('invoke returns placeholder result', () async {
      final result = await tool.invoke(
        const ToolInvocation(toolId: 'practice', invocationId: 'p-1'),
      );

      expect(result.isPlaceholder, isTrue);
      expect(result.isSuccess, isTrue);
    });
  });

  group('GoalTool', () {
    const tool = GoalTool();

    test('has correct id', () => expect(tool.id, 'goal'));

    test('invoke returns placeholder result', () async {
      final result = await tool.invoke(
        const ToolInvocation(toolId: 'goal', invocationId: 'g-1'),
      );

      expect(result.isPlaceholder, isTrue);
      expect(result.isSuccess, isTrue);
    });
  });

  group('InsightTool', () {
    const tool = InsightTool();

    test('has correct id', () => expect(tool.id, 'insight'));

    test('supports local and functionCalling capabilities', () {
      expect(tool.capabilities, contains(ToolCapability.local));
      expect(tool.capabilities, contains(ToolCapability.functionCalling));
    });

    test('invoke returns placeholder result', () async {
      final result = await tool.invoke(
        const ToolInvocation(toolId: 'insight', invocationId: 'i-1'),
      );

      expect(result.isPlaceholder, isTrue);
      expect(result.isSuccess, isTrue);
    });
  });

  group('KnowledgeGraphTool', () {
    const tool = KnowledgeGraphTool();

    test('has correct id', () => expect(tool.id, 'knowledge_graph'));

    test('supports local and structuredOutputs capabilities', () {
      expect(tool.capabilities, contains(ToolCapability.local));
      expect(tool.capabilities, contains(ToolCapability.structuredOutputs));
    });

    test('invoke returns placeholder result', () async {
      final result = await tool.invoke(
        const ToolInvocation(
          toolId: 'knowledge_graph',
          invocationId: 'kg-1',
          parameters: <String, Object?>{'query': 'test'},
        ),
      );

      expect(result.isPlaceholder, isTrue);
      expect(result.isSuccess, isTrue);
    });
  });

  group('ResearchTool', () {
    const tool = ResearchTool();

    test('has correct id', () => expect(tool.id, 'research'));

    test('supports remote and functionCalling capabilities', () {
      expect(tool.capabilities, contains(ToolCapability.remote));
      expect(tool.capabilities, contains(ToolCapability.functionCalling));
    });

    test('invoke returns placeholder result', () async {
      final result = await tool.invoke(
        const ToolInvocation(
          toolId: 'research',
          invocationId: 'res-1',
          parameters: <String, Object?>{'query': 'test topic'},
        ),
      );

      expect(result.isPlaceholder, isTrue);
      expect(result.isSuccess, isTrue);
    });
  });

  // -------------------------------------------------------------------------
  // aiToolRegistryProvider
  // -------------------------------------------------------------------------

  group('aiToolRegistryProvider', () {
    test('includes all seven demo tools', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final registry = container.read(aiToolRegistryProvider);

      expect(registry.contains('reflection'), isTrue);
      expect(registry.contains('timeline'), isTrue);
      expect(registry.contains('practice'), isTrue);
      expect(registry.contains('goal'), isTrue);
      expect(registry.contains('insight'), isTrue);
      expect(registry.contains('knowledge_graph'), isTrue);
      expect(registry.contains('research'), isTrue);
    });

    test('all tools return placeholder results on invocation', () async {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final registry = container.read(aiToolRegistryProvider);

      for (final tool in registry.all) {
        final result = await registry.invoke(
          ToolInvocation(
            toolId: tool.id,
            invocationId: 'smoke-${tool.id}',
          ),
        );
        expect(result.isSuccess, isTrue, reason: '${tool.id} should succeed');
        expect(
          result.isPlaceholder,
          isTrue,
          reason: '${tool.id} should be placeholder',
        );
      }
    });
  });
}
