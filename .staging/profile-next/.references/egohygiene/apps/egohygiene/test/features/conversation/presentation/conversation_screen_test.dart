import 'package:egohygiene/features/conversation/domain/conversation_manager.dart';
import 'package:egohygiene/features/conversation/presentation/conversation_screen.dart';
import 'package:egohygiene/features/conversation/providers/conversation_providers.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/services/ai_provider.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod/misc.dart' show Override;

class _ChunkedChatProvider implements ChatProvider {
  _ChunkedChatProvider({
    required this.chunks,
  }) : chunkDelay = const Duration(milliseconds: 20);

  final List<String> chunks;
  final Duration chunkDelay;

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
    return chunks.join();
  }

  @override
  Stream<String> streamMessage(
    String message, {
    List<String>? conversationHistory,
  }) async* {
    for (final chunk in chunks) {
      await Future<void>.delayed(chunkDelay);
      yield chunk;
    }
  }
}

Widget _wrap(Widget child, {required List<Override> overrides}) {
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp(
      theme: AppTheme.light(useGoogleFonts: false),
      home: TranslationProvider(child: child),
    ),
  );
}

void main() {
  group('ConversationScreen', () {
    testWidgets('renders suggestion chips in empty state', (tester) async {
      final provider = _ChunkedChatProvider(chunks: const ['Hello']);

      await tester.pumpWidget(
        _wrap(
          const ConversationScreen(),
          overrides: [
            conversationManagerProvider.overrideWith(
              (_) => ConversationManager(chatProvider: provider),
            ),
          ],
        ),
      );

      expect(
        find.text('What pattern should I pay attention to today?'),
        findsOneWidget,
      );
      expect(find.byType(ActionChip), findsNWidgets(3));
    });

    testWidgets('sending from suggestion shows summary placeholder', (
      tester,
    ) async {
      final provider = _ChunkedChatProvider(chunks: const ['Assistant reply']);

      await tester.pumpWidget(
        _wrap(
          const ConversationScreen(),
          overrides: [
            conversationManagerProvider.overrideWith(
              (_) => ConversationManager(chatProvider: provider),
            ),
          ],
        ),
      );

      await tester.tap(
        find.text('What pattern should I pay attention to today?'),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 60));

      expect(
        find.text('What pattern should I pay attention to today?'),
        findsWidgets,
      );
      expect(find.text('Assistant reply'), findsOneWidget);
      expect(
        find.textContaining('A summary of this conversation'),
        findsOneWidget,
      );
    });

    testWidgets('renders markdown code blocks', (tester) async {
      final provider = _ChunkedChatProvider(
        chunks: const ['# Insight\n```dart\nfinal answer = 42;\n```'],
      );

      await tester.pumpWidget(
        _wrap(
          const ConversationScreen(),
          overrides: [
            conversationManagerProvider.overrideWith(
              (_) => ConversationManager(chatProvider: provider),
            ),
          ],
        ),
      );

      await tester.enterText(find.byType(TextField), 'Show me code');
      await tester.tap(find.byIcon(Icons.send_rounded));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 60));

      expect(find.text('Insight'), findsOneWidget);
      expect(find.text('final answer = 42;'), findsOneWidget);
      expect(find.textContaining('```'), findsNothing);
    });
  });
}
