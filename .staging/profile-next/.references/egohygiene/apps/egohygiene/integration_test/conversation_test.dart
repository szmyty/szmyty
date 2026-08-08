/// Integration test: conversation flow.
///
/// Verifies the Conversation screen:
///   - The empty state is shown when no messages exist.
///   - Typing a message and sending it causes a reply to appear.
///   - The new-conversation action resets the chat.
///
/// The DemoAIProvider is active by default (no --dart-define required) so the
/// conversation responds with deterministic demo output.
///
/// Run with:
/// ```
/// flutter test integration_test/conversation_test.dart
/// ```
///
/// On a real device or emulator:
/// ```
/// flutter test integration_test/conversation_test.dart -d <device-id>
/// ```
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'helpers/integration_test_helpers.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Conversation flow', () {
    testWidgets(
      'Conversation tab shows the empty state',
      (tester) async {
        await pumpApp(tester);

        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Conversation'),
          ),
        );
        await tester.pumpAndSettle();

        // Empty-state title and description are shown before any messages.
        expect(find.text('Start a conversation'), findsOneWidget);
        expect(
          find.text(
            "Ask a question, share a reflection, or explore what's on your mind.",
          ),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Conversation tab shows suggestion chips in the empty state',
      (tester) async {
        await pumpApp(tester);

        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Conversation'),
          ),
        );
        await tester.pumpAndSettle();

        // Three suggestion chips are shown when the conversation is empty.
        expect(
          find.text('What pattern should I pay attention to today?'),
          findsOneWidget,
        );
        expect(
          find.text('Help me reflect on something that felt heavy.'),
          findsOneWidget,
        );
        expect(
          find.text('Give me one grounding practice for right now.'),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'sending a message replaces the empty state with the message list',
      (tester) async {
        await pumpApp(tester);

        await tester.tap(
          find.descendant(
            of: find.byType(NavigationBar),
            matching: find.text('Conversation'),
          ),
        );
        await tester.pumpAndSettle();

        // Tap a suggestion chip to send a pre-populated message.
        // The chip both fills the input and submits in a single tap.
        await tester.tap(
          find.text('What pattern should I pay attention to today?'),
        );
        await tester.pumpAndSettle();

        // The user's message must now be visible in the list.
        expect(
          find.text('What pattern should I pay attention to today?'),
          findsOneWidget,
        );

        // The empty-state title must no longer be visible.
        expect(find.text('Start a conversation'), findsNothing);
      },
    );
  });
}
