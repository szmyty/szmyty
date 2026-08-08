import 'package:egohygiene/shared/ai/ai_capability.dart';
import 'package:egohygiene/shared/ai/ai_capability_request.dart';
import 'package:egohygiene/shared/ai/ai_capability_result.dart';
import 'package:egohygiene/shared/ai/ai_capability_router.dart';
import 'package:egohygiene/shared/ai/ai_policy_gateway.dart';
import 'package:egohygiene/shared/services/ai_provider.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AiPolicyGateway', () {
    const gateway = AiPolicyGateway();

    test('blocks diagnosis requests', () {
      final evaluation = gateway.evaluateRequest(
        prompt: 'Can you diagnose me with depression?',
        operation: 'chat.sendMessage',
      );

      expect(evaluation.isBlocked, isTrue);
      expect(evaluation.ruleIds, contains('no_diagnosis'));
      expect(evaluation.blockedResponse, contains('can’t provide a diagnosis'));
    });

    test('adds uncertainty framing for absolute responses', () {
      final evaluation = gateway.evaluateResponse(
        prompt: 'What do you think?',
        response: 'This will definitely solve your issue.',
        operation: 'chat.sendMessage',
      );

      expect(evaluation.ruleIds, contains('uncertainty_scaffold'));
      expect(evaluation.content, contains('not a certainty'));
    });
  });

  group('AiPolicyChatProvider', () {
    test('returns refusal without calling delegate when blocked', () async {
      final delegate = _StubChatProvider();
      final provider = AiPolicyChatProvider(
        delegate: delegate,
        policyGateway: const AiPolicyGateway(),
      );

      final response = await provider.sendMessage(
        'Please diagnose me with a mental illness.',
      );

      expect(delegate.sendCallCount, 0);
      expect(response, contains('can’t provide a diagnosis'));
    });

    test('applies response policy to delegated output', () async {
      final delegate = _StubChatProvider(reply: 'This will definitely resolve everything.');
      final provider = AiPolicyChatProvider(
        delegate: delegate,
        policyGateway: const AiPolicyGateway(),
      );

      final response = await provider.sendMessage('Help me reflect');

      expect(delegate.sendCallCount, 1);
      expect(response, contains('not a certainty'));
    });
  });

  group('PolicyAwareAiCapabilityRouter', () {
    test('short-circuits blocked requests before delegate routing', () async {
      final delegate = _StubRouter();
      final router = PolicyAwareAiCapabilityRouter(
        delegate: delegate,
        policyGateway: const AiPolicyGateway(),
      );

      final result = await router.route(
        const AiCapabilityRequest(
          capability: AiCapability.reflection,
          prompt: 'Can you diagnose me?',
        ),
      );

      expect(delegate.routeCallCount, 0);
      expect(result.providerName, 'AI Policy Gateway');
      expect(result.metadata['policyGateway'], isNotNull);
    });

    test('adds policy audit metadata to successful delegate routing', () async {
      final delegate = _StubRouter(
        responseContent: 'This will definitely work.',
      );
      final router = PolicyAwareAiCapabilityRouter(
        delegate: delegate,
        policyGateway: const AiPolicyGateway(),
      );

      final result = await router.route(
        const AiCapabilityRequest(
          capability: AiCapability.reflection,
          prompt: 'I need perspective',
        ),
      );

      expect(delegate.routeCallCount, 1);
      expect(result.metadata['policyGateway'], isNotNull);
      expect(result.content, contains('not a certainty'));
    });
  });
}

class _StubChatProvider implements ChatProvider {
  _StubChatProvider({
    this.reply = 'ok',
  });

  final String reply;
  int sendCallCount = 0;

  @override
  final AIProviderConfiguration configuration = const AIProviderConfiguration(
    id: 'fake-chat',
    displayName: 'Fake Chat',
  );

  @override
  String get name => configuration.displayName;

  @override
  ProviderCapabilities get capabilities => const ProviderCapabilities(chat: true);

  @override
  AIProviderStatus get status => AIProviderStatus.available;

  @override
  Future<void> init() async {}

  @override
  Future<bool> isAvailable() async => true;

  @override
  Future<String> sendMessage(
    String message, {
    List<String>? conversationHistory,
  }) async {
    sendCallCount++;
    return reply;
  }

  @override
  Stream<String> streamMessage(
    String message, {
    List<String>? conversationHistory,
  }) {
    return Stream<String>.value(reply);
  }
}

class _StubRouter implements AiCapabilityRouter {
  _StubRouter({
    this.responseContent = 'ok',
  });

  final String responseContent;
  int routeCallCount = 0;

  @override
  Future<AiCapabilityResult> route(AiCapabilityRequest request) async {
    routeCallCount++;
    return AiCapabilityResult(
      capability: request.capability,
      content: responseContent,
      providerName: 'Fake Router',
    );
  }

  @override
  Future<bool> canRoute(AiCapability capability) async => true;

  @override
  Future<Set<AiCapability>> availableCapabilities() async => AiCapability.values.toSet();
}
