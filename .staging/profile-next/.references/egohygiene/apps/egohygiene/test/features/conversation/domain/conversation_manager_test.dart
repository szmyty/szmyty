import 'package:egohygiene/features/conversation/domain/conversation.dart';
import 'package:egohygiene/features/conversation/domain/conversation_manager.dart';
import 'package:egohygiene/features/conversation/domain/conversation_state.dart';
import 'package:egohygiene/features/conversation/domain/conversation_summary.dart';
import 'package:egohygiene/features/conversation/domain/message.dart';
import 'package:egohygiene/features/conversation/providers/conversation_providers.dart';
import 'package:egohygiene/shared/context/context_manager.dart';
import 'package:egohygiene/shared/context/context_source.dart';
import 'package:egohygiene/shared/memory/impl/in_memory_memory_store.dart';
import 'package:egohygiene/shared/memory/memory.dart';
import 'package:egohygiene/shared/memory/memory_manager.dart';
import 'package:egohygiene/shared/memory/memory_type.dart';
import 'package:egohygiene/shared/services/ai_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Fake providers
// ---------------------------------------------------------------------------

class _FixedChatProvider implements ChatProvider {
  _FixedChatProvider({required this.reply, this.shouldThrow = false});

  final String reply;
  final bool shouldThrow;

  @override
  final AIProviderConfiguration configuration = const AIProviderConfiguration(
    id: 'fake-chat',
    displayName: 'Fake Chat',
  );

  @override
  ProviderCapabilities get capabilities => const ProviderCapabilities(chat: true, streaming: true);

  @override
  String get name => configuration.displayName;

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
    if (shouldThrow) throw Exception('provider failure');
    return reply;
  }

  @override
  Stream<String> streamMessage(
    String message, {
    List<String>? conversationHistory,
  }) {
    if (shouldThrow) return Stream.error(Exception('stream failure'));
    return Stream.value(reply);
  }
}

class _FixedSummarizationProvider implements SummarizationProvider, InsightProvider {
  const _FixedSummarizationProvider();

  @override
  final AIProviderConfiguration configuration = const AIProviderConfiguration(
    id: 'fake-summarizer',
    displayName: 'Fake Summarizer',
  );

  @override
  ProviderCapabilities get capabilities => const ProviderCapabilities(summarization: true, insightGeneration: true);

  @override
  String get name => configuration.displayName;

  @override
  AIProviderStatus get status => AIProviderStatus.available;

  @override
  Future<void> init() async {}

  @override
  Future<bool> isAvailable() async => true;

  @override
  Future<String> summarize(String content, {int? maxLength}) async =>
      'Fake summary of: ${content.substring(0, content.length > 20 ? 20 : content.length)}';

  @override
  Future<String> briefSummary(String content) async => summarize(content);

  @override
  Future<String> generateInsight(String content) async => 'Fake insight for: $content';

  @override
  Future<List<String>> extractThemes(String content) async => ['reflection', 'growth', 'self-awareness'];
}

/// A fake [ContextSource] that returns a fixed map of entries.
class _FixedContextSource implements ContextSource {
  _FixedContextSource({
    required this.sourceId,
    this._entries = const {},
  });

  @override
  final String sourceId;

  @override
  String get displayName => 'Fixed Context Source';

  final Map<String, Object?> _entries;

  @override
  Future<void> initialize() async {}

  @override
  Future<Map<String, Object?>> buildContext() async => _entries;

  @override
  Future<void> dispose() async {}
}

/// A [ChatProvider] that captures the history passed to each [sendMessage] call.
class _HistoryCapturingChatProvider implements ChatProvider {
  _HistoryCapturingChatProvider({
    required this.reply,
    required this.onSend,
  });

  final String reply;
  final void Function(List<String> history) onSend;

  @override
  final AIProviderConfiguration configuration = const AIProviderConfiguration(
    id: 'capturing-chat',
    displayName: 'Capturing Chat',
  );

  @override
  ProviderCapabilities get capabilities => const ProviderCapabilities(chat: true, streaming: true);

  @override
  String get name => configuration.displayName;

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
    onSend(conversationHistory ?? []);
    return reply;
  }

  @override
  Stream<String> streamMessage(
    String message, {
    List<String>? conversationHistory,
  }) async* {
    onSend(conversationHistory ?? []);
    yield reply;
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

Message _userMsg({String content = 'hello', String id = 'u1'}) {
  return Message(
    id: id,
    role: MessageRole.user,
    content: content,
    timestamp: DateTime(2025),
  );
}

Message _assistantMsg({String content = 'hi there', String id = 'a1'}) {
  return Message(
    id: id,
    role: MessageRole.assistant,
    content: content,
    timestamp: DateTime(2025),
  );
}

Conversation _emptyConversation() => Conversation.start(id: 'conv-1');

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ── MessageRole ────────────────────────────────────────────────────────────

  group('MessageRole', () {
    test('has three values', () {
      expect(MessageRole.values, hasLength(3));
    });

    test('contains user, assistant, system', () {
      expect(
        MessageRole.values,
        containsAll([
          MessageRole.user,
          MessageRole.assistant,
          MessageRole.system,
        ]),
      );
    });
  });

  // ── Message ────────────────────────────────────────────────────────────────

  group('Message', () {
    test('factory Message.user produces a user message', () {
      final m = Message.user(content: 'Hello');
      expect(m.role, MessageRole.user);
      expect(m.content, 'Hello');
      expect(m.id, isNotEmpty);
      expect(m.isUser, isTrue);
      expect(m.isAssistant, isFalse);
    });

    test('factory Message.assistant produces an assistant message', () {
      final m = Message.assistant(content: 'Hi there');
      expect(m.role, MessageRole.assistant);
      expect(m.isAssistant, isTrue);
    });

    test('factory Message.system produces a system message', () {
      final m = Message.system(content: 'You are a helper');
      expect(m.role, MessageRole.system);
      expect(m.isSystem, isTrue);
    });

    test('copyWith replaces specified fields only', () {
      final original = _userMsg(content: 'original');
      final copy = original.copyWith(content: 'updated');
      expect(copy.content, 'updated');
      expect(copy.id, original.id);
      expect(copy.role, original.role);
    });

    test('equality is based on id, role, content, and timestamp', () {
      final m1 = _userMsg(id: 'x', content: 'hi');
      final m2 = _userMsg(id: 'x', content: 'hi');
      expect(m1, equals(m2));
    });

    test('different content produces different identity', () {
      final m1 = _userMsg();
      final m2 = _userMsg(content: 'goodbye');
      expect(m1, isNot(equals(m2)));
    });

    test('toString includes id, role, and truncated content', () {
      final m = Message(
        id: 'abc',
        role: MessageRole.user,
        content: 'test content',
        timestamp: DateTime(2025),
      );
      expect(m.toString(), contains('abc'));
      expect(m.toString(), contains('user'));
    });
  });

  // ── Conversation ───────────────────────────────────────────────────────────

  group('Conversation', () {
    test('Conversation.start creates an empty conversation', () {
      final conv = _emptyConversation();
      expect(conv.isEmpty, isTrue);
      expect(conv.messages, isEmpty);
      expect(conv.messageCount, 0);
      expect(conv.lastMessage, isNull);
    });

    test('addMessage appends message and updates updatedAt', () {
      final conv = _emptyConversation();
      final msg = _userMsg();
      final updated = conv.addMessage(msg);

      expect(updated.messageCount, 1);
      expect(updated.lastMessage, equals(msg));
      expect(updated.updatedAt, equals(msg.timestamp));
    });

    test('addMessage does not mutate the original', () {
      final original = _emptyConversation();
      original.addMessage(_userMsg());
      expect(original.isEmpty, isTrue);
    });

    test('userMessages returns only user messages', () {
      final conv = _emptyConversation()
          .addMessage(_userMsg())
          .addMessage(_assistantMsg())
          .addMessage(_userMsg(id: 'u2', content: 'second'));

      expect(conv.userMessages, hasLength(2));
      expect(conv.userMessages.every((m) => m.isUser), isTrue);
    });

    test('assistantMessages returns only assistant messages', () {
      final conv = _emptyConversation()
          .addMessage(_userMsg())
          .addMessage(_assistantMsg())
          .addMessage(_assistantMsg(id: 'a2', content: 'also assistant'));

      expect(conv.assistantMessages, hasLength(2));
      expect(conv.assistantMessages.every((m) => m.isAssistant), isTrue);
    });

    test('copyWith replaces specified fields', () {
      final conv = _emptyConversation().addMessage(_userMsg());
      final copy = conv.copyWith(title: 'My chat');
      expect(copy.title, 'My chat');
      expect(copy.messageCount, conv.messageCount);
    });

    test('isNotEmpty is true after adding a message', () {
      final conv = _emptyConversation().addMessage(_userMsg());
      expect(conv.isNotEmpty, isTrue);
    });
  });

  // ── ConversationSummary ────────────────────────────────────────────────────

  group('ConversationSummary', () {
    test('constructs with required fields', () {
      final summary = ConversationSummary(
        conversationId: 'conv-1',
        summary: 'A brief summary',
        themes: ['growth', 'reflection'],
        generatedAt: DateTime(2025),
      );

      expect(summary.conversationId, 'conv-1');
      expect(summary.summary, 'A brief summary');
      expect(summary.themes, hasLength(2));
    });

    test('isEmpty returns true when summary and themes are empty', () {
      final empty = ConversationSummary(
        conversationId: 'c',
        summary: '  ',
        themes: [],
        generatedAt: DateTime(2025),
      );
      expect(empty.isEmpty, isTrue);
    });

    test('isEmpty returns false when summary is present', () {
      final nonEmpty = ConversationSummary(
        conversationId: 'c',
        summary: 'Something meaningful',
        themes: [],
        generatedAt: DateTime(2025),
      );
      expect(nonEmpty.isEmpty, isFalse);
    });

    test('copyWith replaces specified fields', () {
      final original = ConversationSummary(
        conversationId: 'c1',
        summary: 'original',
        themes: [],
        generatedAt: DateTime(2025),
      );
      final copy = original.copyWith(summary: 'updated');
      expect(copy.summary, 'updated');
      expect(copy.conversationId, 'c1');
    });
  });

  // ── ConversationState ──────────────────────────────────────────────────────

  group('ConversationState', () {
    test('initial() produces idle state with empty conversation', () {
      final state = ConversationState.initial();
      expect(state.isIdle, isTrue);
      expect(state.isSending, isFalse);
      expect(state.hasError, isFalse);
      expect(state.conversation.isEmpty, isTrue);
    });

    test('sending() transitions to sending status', () {
      final state = ConversationState.initial().sending();
      expect(state.isSending, isTrue);
      expect(state.errorMessage, isNull);
    });

    test('idle() transitions back to idle status', () {
      final state = ConversationState.initial().sending().idle();
      expect(state.isIdle, isTrue);
    });

    test('withError() transitions to error status with message', () {
      final state = ConversationState.initial().withError('Network failure');
      expect(state.hasError, isTrue);
      expect(state.errorMessage, 'Network failure');
    });

    test('idle() after withError clears the errorMessage', () {
      final state = ConversationState.initial().withError('Some error').idle();
      expect(state.isIdle, isTrue);
      expect(state.errorMessage, isNull);
    });

    test('sending() after withError clears the errorMessage', () {
      final state = ConversationState.initial().withError('Some error').sending();
      expect(state.isSending, isTrue);
      expect(state.errorMessage, isNull);
    });

    test('copyWith with null errorMessage explicitly clears the field', () {
      final withError = ConversationState.initial().withError('Some error');
      final cleared = withError.copyWith(errorMessage: null);
      expect(cleared.errorMessage, isNull);
      expect(cleared.status, ConversationStatus.error);
    });

    test('copyWith omitting errorMessage preserves existing value', () {
      final withError = ConversationState.initial().withError('Preserved error');
      final copy = withError.copyWith(status: ConversationStatus.idle);
      // errorMessage is preserved when not explicitly passed
      expect(copy.errorMessage, 'Preserved error');
    });

    test('copyWith replaces specified fields', () {
      final conv = _emptyConversation().addMessage(_userMsg());
      final state = ConversationState.initial().copyWith(conversation: conv);
      expect(state.conversation.messageCount, 1);
    });

    test('hasSummary is false before summarization', () {
      expect(ConversationState.initial().hasSummary, isFalse);
    });

    test('hasSummary is true after summary is attached', () {
      final summary = ConversationSummary(
        conversationId: 'c',
        summary: 'some summary',
        themes: [],
        generatedAt: DateTime(2025),
      );
      final state = ConversationState.initial().copyWith(summary: summary);
      expect(state.hasSummary, isTrue);
    });
  });

  // ── ConversationManager ────────────────────────────────────────────────────

  group('ConversationManager', () {
    test('sendMessage appends user and assistant messages', () async {
      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: 'Hello back'),
      );

      final result = await manager.sendMessage(
        conversation: _emptyConversation(),
        userMessage: 'Hello',
      );

      expect(result.messageCount, 2);
      expect(result.messages[0].isUser, isTrue);
      expect(result.messages[0].content, 'Hello');
      expect(result.messages[1].isAssistant, isTrue);
      expect(result.messages[1].content, 'Hello back');
    });

    test('sendMessage with empty message returns conversation unchanged', () async {
      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: 'reply'),
      );
      final conv = _emptyConversation();
      final result = await manager.sendMessage(
        conversation: conv,
        userMessage: '   ',
      );
      expect(result.messageCount, 0);
    });

    test('sendMessage rethrows provider exceptions', () async {
      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: '', shouldThrow: true),
      );

      await expectLater(
        () => manager.sendMessage(
          conversation: _emptyConversation(),
          userMessage: 'Hi',
        ),
        throwsException,
      );
    });

    test('streamMessage emits assistant content incrementally', () async {
      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: 'Streaming response'),
      );

      final messages = await manager
          .streamMessage(
            conversation: _emptyConversation(),
            userMessage: 'test',
          )
          .toList();

      expect(messages, isNotEmpty);
      expect(messages.last.isAssistant, isTrue);
      expect(messages.last.content, 'Streaming response');
    });

    test('streamMessage emits nothing for empty user message', () async {
      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: 'ignored'),
      );

      final messages = await manager
          .streamMessage(
            conversation: _emptyConversation(),
            userMessage: '',
          )
          .toList();

      expect(messages, isEmpty);
    });

    test('summarize generates a ConversationSummary', () async {
      final conv = _emptyConversation()
          .addMessage(_userMsg(content: 'I want to grow'))
          .addMessage(_assistantMsg(content: 'Great insight'));

      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: ''),
        summarizationProvider: const _FixedSummarizationProvider(),
      );

      final summary = await manager.summarize(conv);

      expect(summary.conversationId, conv.id);
      expect(summary.summary, isNotEmpty);
      expect(summary.themes, isNotEmpty);
    });

    test('summarize throws StateError without a summarization provider', () async {
      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: ''),
      );

      await expectLater(
        () => manager.summarize(_emptyConversation()),
        throwsA(isA<StateError>()),
      );
    });

    test('summarize includes themes via InsightProvider', () async {
      final conv = _emptyConversation().addMessage(_userMsg()).addMessage(_assistantMsg());

      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: ''),
        summarizationProvider: const _FixedSummarizationProvider(),
      );

      final summary = await manager.summarize(conv);

      expect(summary.themes, contains('reflection'));
    });
  });

  // ── ConversationNotifier ───────────────────────────────────────────────────

  group('ConversationNotifier', () {
    ProviderContainer container0({
      String reply = 'Test reply',
      bool shouldThrow = false,
    }) {
      final demoProvider = _FixedChatProvider(
        reply: reply,
        shouldThrow: shouldThrow,
      );

      return ProviderContainer(
        overrides: [
          conversationManagerProvider.overrideWith(
            (_) => ConversationManager(chatProvider: demoProvider),
          ),
        ],
      );
    }

    test('initial state is idle with an empty conversation', () {
      final container = container0();
      addTearDown(container.dispose);

      final state = container.read(conversationNotifierProvider);
      expect(state.isIdle, isTrue);
      expect(state.conversation.isEmpty, isTrue);
    });

    test('send adds user and assistant messages', () async {
      final container = container0(reply: 'Hello back');
      addTearDown(container.dispose);

      await container.read(conversationNotifierProvider.notifier).send('Hello');

      final state = container.read(conversationNotifierProvider);
      expect(state.conversation.messageCount, 2);
      expect(state.conversation.messages[0].content, 'Hello');
      expect(state.conversation.messages[1].content, 'Hello back');
      expect(state.isIdle, isTrue);
    });

    test('send ignores empty message', () async {
      final container = container0();
      addTearDown(container.dispose);

      await container.read(conversationNotifierProvider.notifier).send('   ');

      expect(
        container.read(conversationNotifierProvider).conversation.isEmpty,
        isTrue,
      );
    });

    test('send transitions to error state on provider failure', () async {
      final container = container0(shouldThrow: true);
      addTearDown(container.dispose);

      await container.read(conversationNotifierProvider.notifier).send('Hello');

      final state = container.read(conversationNotifierProvider);
      expect(state.hasError, isTrue);
      expect(state.errorMessage, isNotNull);
    });

    test('clearError resets error state to idle', () async {
      final container = container0(shouldThrow: true);
      addTearDown(container.dispose);

      await container.read(conversationNotifierProvider.notifier).send('Hello');

      container.read(conversationNotifierProvider.notifier).clearError();

      expect(container.read(conversationNotifierProvider).isIdle, isTrue);
    });

    test('reset clears messages and starts fresh', () async {
      final container = container0(reply: 'hi');
      addTearDown(container.dispose);

      await container.read(conversationNotifierProvider.notifier).send('Hello');

      container.read(conversationNotifierProvider.notifier).reset();

      final state = container.read(conversationNotifierProvider);
      expect(state.conversation.isEmpty, isTrue);
      expect(state.isIdle, isTrue);
    });
  });

  // ── DemoAIProvider responses ───────────────────────────────────────────────

  group('DemoAIProvider', () {
    test('sendMessage returns a non-empty believable response', () async {
      final registry = AIProviderRegistry();
      final provider = DemoAIProvider(registry: registry);

      final response = await provider.sendMessage('How am I doing?');

      expect(response, isNotEmpty);
      expect(response, isNot(startsWith('Demo response:')));
    });

    test('same message always produces the same response (deterministic)', () async {
      final registry = AIProviderRegistry();
      final provider = DemoAIProvider(registry: registry);

      final first = await provider.sendMessage('Tell me something');
      final second = await provider.sendMessage('Tell me something');

      expect(first, equals(second));
    });

    test('different messages can produce different responses', () async {
      final registry = AIProviderRegistry();
      final provider = DemoAIProvider(registry: registry);

      final responses = <String>{};
      const inputs = [
        'hello',
        'how are you',
        'what should I focus on',
        'I feel stressed',
        'tell me about patterns',
        'what is self-care',
        'I need help',
        'tell me more',
        'what does growth mean',
        'I am struggling',
      ];

      for (final input in inputs) {
        responses.add(await provider.sendMessage(input));
      }

      // With 10 different inputs across a 10-item response pool we expect
      // multiple distinct responses.
      expect(responses.length, greaterThan(1));
    });

    test('streamMessage returns the same content as sendMessage', () async {
      final registry = AIProviderRegistry();
      final provider = DemoAIProvider(registry: registry);

      const msg = 'What should I reflect on?';
      final sent = await provider.sendMessage(msg);
      final streamed = await provider.streamMessage(msg).last;

      expect(streamed, equals(sent));
    });
  });

  // ── Context-aware ConversationManager ─────────────────────────────────────

  group('ConversationManager with ContextManager', () {
    test('sendMessage works without a ContextManager (no regression)', () async {
      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: 'ok'),
      );

      final result = await manager.sendMessage(
        conversation: _emptyConversation(),
        userMessage: 'Hello',
      );

      expect(result.messageCount, 2);
      expect(result.messages.last.content, 'ok');
    });

    test('sendMessage assembles context when ContextManager is provided', () async {
      final contextSource = _FixedContextSource(
        sourceId: 'test',
        entries: {'test.key': 'test-value', 'test.count': 42},
      );
      final contextManager = ContextManager(sources: [contextSource]);
      await contextManager.initialize();

      final capturedHistories = <List<String>>[];
      final capturingProvider = _HistoryCapturingChatProvider(
        reply: 'context-aware response',
        onSend: capturedHistories.add,
      );

      final manager = ConversationManager(
        chatProvider: capturingProvider,
        contextManager: contextManager,
      );

      await manager.sendMessage(
        conversation: _emptyConversation(),
        userMessage: 'Hello',
      );

      expect(capturedHistories, hasLength(1));
      final history = capturedHistories.first;
      // The first history entry should be the assembled context system message.
      expect(history.isNotEmpty, isTrue);
      expect(history.first, startsWith('system:'));
      expect(history.first, contains('test.key'));
    });

    test('streamMessage assembles context when ContextManager is provided', () async {
      final contextSource = _FixedContextSource(
        sourceId: 'reflection',
        entries: {'reflection.count': 3},
      );
      final contextManager = ContextManager(sources: [contextSource]);
      await contextManager.initialize();

      final capturedHistories = <List<String>>[];
      final capturingProvider = _HistoryCapturingChatProvider(
        reply: 'streamed response',
        onSend: capturedHistories.add,
      );

      final manager = ConversationManager(
        chatProvider: capturingProvider,
        contextManager: contextManager,
      );

      await manager
          .streamMessage(
            conversation: _emptyConversation(),
            userMessage: 'Hello',
          )
          .toList();

      expect(capturedHistories, hasLength(1));
      final history = capturedHistories.first;
      expect(history.first, startsWith('system:'));
      expect(history.first, contains('reflection.count'));
    });

    test('empty ContextSnapshot does not add system message', () async {
      final contextManager = ContextManager(sources: []);
      await contextManager.initialize();

      final capturedHistories = <List<String>>[];
      final capturingProvider = _HistoryCapturingChatProvider(
        reply: 'no-context response',
        onSend: capturedHistories.add,
      );

      final manager = ConversationManager(
        chatProvider: capturingProvider,
        contextManager: contextManager,
      );

      await manager.sendMessage(
        conversation: _emptyConversation(),
        userMessage: 'Hello',
      );

      final history = capturedHistories.first;
      // No system message when context is empty.
      expect(history.every((h) => !h.startsWith('system:')), isTrue);
    });
  });

  group('ConversationManager with MemoryManager', () {
    MemoryManager createMemoryManager() => MemoryManager(store: InMemoryMemoryStore());

    test('sendMessage includes recalled memory in provider history', () async {
      final memoryManager = createMemoryManager();
      await memoryManager.remember(
        Memory(
          id: 'mem-1',
          type: MemoryType.episodic,
          content: 'User struggles with sleep consistency',
          source: 'reflection',
          createdAt: DateTime(2025),
          updatedAt: DateTime(2025),
        ),
      );

      final capturedHistories = <List<String>>[];
      final manager = ConversationManager(
        chatProvider: _HistoryCapturingChatProvider(
          reply: 'ok',
          onSend: capturedHistories.add,
        ),
        memoryManager: memoryManager,
      );

      await manager.sendMessage(
        conversation: _emptyConversation(),
        userMessage: 'How can I improve my sleep?',
      );

      final history = capturedHistories.single;
      expect(history.first, startsWith('system: Relevant long-term memory:'));
      expect(history.first, contains('sleep consistency'));
    });

    test('sendMessage persists conversation memories', () async {
      final memoryManager = createMemoryManager();
      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: 'Take one step at a time'),
        memoryManager: memoryManager,
      );

      final result = await manager.sendMessage(
        conversation: _emptyConversation(),
        userMessage: 'I feel overwhelmed',
      );

      final memories = await memoryManager.recallBySource('conversation');
      expect(memories, hasLength(2));
      expect(memories.map((m) => m.content), contains('I feel overwhelmed'));
      expect(
        memories.map((m) => m.content),
        contains(result.messages.last.content),
      );
    });

    test('summarize upserts a conversation summary memory', () async {
      final memoryManager = createMemoryManager();
      final manager = ConversationManager(
        chatProvider: _FixedChatProvider(reply: 'ok'),
        summarizationProvider: const _FixedSummarizationProvider(),
        memoryManager: memoryManager,
      );
      final conversation = _emptyConversation().addMessage(
        _userMsg(content: 'I am learning to set boundaries'),
      );

      await manager.summarize(conversation);
      await manager.summarize(conversation);

      final summaryMemories = await memoryManager.recallBySource('conversation_summary');
      expect(summaryMemories, hasLength(1));
      expect(summaryMemories.single.type, MemoryType.journey);
      expect(summaryMemories.single.content, isNotEmpty);
    });
  });
}
