import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:egohygiene/shared/widgets/shared_widgets.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('shared_widgets barrel export', () {
    test('core shared widgets are accessible', () {
      final controller = TextEditingController();
      addTearDown(controller.dispose);

      expect(
        const AppErrorState(
          message: 'Something went wrong',
        ),
        isNotNull,
      );
      expect(const AppCard(child: SizedBox.shrink()), isNotNull);
      expect(
        const AppEmptyState(
          icon: Icons.inbox_outlined,
          title: 'Empty',
        ),
        isNotNull,
      );
      expect(const AppLoadingIndicator(), isNotNull);
      expect(
        AppInputBar(
          controller: controller,
          isSending: false,
          showSuggestions: false,
          suggestions: const <String>[],
          onSuggestionSelected: _noopString,
          onSubmit: _noop,
        ),
        isNotNull,
      );
      expect(
        const AppMessageBubble(
          isUser: true,
          messageText: 'Hello',
          child: Text('Hello'),
        ),
        isNotNull,
      );
      expect(
        const AppSearchBar(
          hintText: 'Search',
        ),
        isNotNull,
      );
      expect(
        const AppSectionCard(
          title: 'Section',
          child: SizedBox.shrink(),
        ),
        isNotNull,
      );
      expect(
        const AppSectionHeader(
          title: 'Section',
        ),
        isNotNull,
      );
      expect(
        const AppStatCard(
          label: 'Label',
          value: '42',
        ),
        isNotNull,
      );
      expect(
        const AppTimelineTile(
          categoryLabel: 'Reflection',
          dateLabel: 'Jul 4',
          title: 'Today',
          icon: Icons.auto_stories_outlined,
          accentColor: Colors.blue,
        ),
        isNotNull,
      );
    });
  });

  testWidgets('AppEmptyState exposes the title as a semantic header', (
    tester,
  ) async {
    final semanticsHandle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light(useGoogleFonts: false),
          home: const Scaffold(
            body: AppEmptyState(
              icon: Icons.inbox_outlined,
              title: 'Nothing here yet',
              description: 'Try adding your first entry.',
            ),
          ),
        ),
      );

      expect(
        tester.getSemantics(find.text('Nothing here yet')),
        matchesSemantics(label: 'Nothing here yet', isHeader: true),
      );
    } finally {
      semanticsHandle.dispose();
    }
  });

  testWidgets('AppMessageBubble announces the speaker and content', (
    tester,
  ) async {
    final semanticsHandle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light(useGoogleFonts: false),
          home: const Scaffold(
            body: AppMessageBubble(
              isUser: false,
              messageText: 'Shared widgets reduce duplication.',
              child: Text('Shared widgets reduce duplication.'),
            ),
          ),
        ),
      );

      expect(
        tester.getSemantics(find.byType(AppMessageBubble)),
        matchesSemantics(label: 'Assistant: Shared widgets reduce duplication.'),
      );
    } finally {
      semanticsHandle.dispose();
    }
  });

  testWidgets('AppStatCard announces value and label as a single item', (
    tester,
  ) async {
    final semanticsHandle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light(useGoogleFonts: false),
          home: const Scaffold(
            body: AppStatCard(label: 'Mood', value: '4/5'),
          ),
        ),
      );

      final node = tester.getSemantics(find.byType(AppStatCard));
      expect(node.label, contains('4/5'));
      expect(node.label, contains('Mood'));
    } finally {
      semanticsHandle.dispose();
    }
  });

  testWidgets('AppLoadingIndicator forwards semanticLabel to indicator', (
    tester,
  ) async {
    final semanticsHandle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light(useGoogleFonts: false),
          home: const Scaffold(
            body: AppLoadingIndicator(semanticLabel: 'Sending message…'),
          ),
        ),
      );

      expect(
        tester.getSemantics(find.byType(CircularProgressIndicator)),
        matchesSemantics(label: 'Sending message…'),
      );
    } finally {
      semanticsHandle.dispose();
    }
  });

  testWidgets('AppLoadingIndicator shows a subtle delight icon', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.light(useGoogleFonts: false),
        home: const Scaffold(
          body: AppLoadingIndicator(),
        ),
      ),
    );

    expect(find.byIcon(Icons.auto_awesome_rounded), findsOneWidget);
  });

  testWidgets('AppErrorState renders message and optional action', (
    tester,
  ) async {
    var retried = false;

    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.light(useGoogleFonts: false),
        home: Scaffold(
          body: AppErrorState(
            message: 'Unable to load content.',
            description: 'Please try again.',
            action: FilledButton(
              onPressed: () => retried = true,
              child: const Text('Try again'),
            ),
          ),
        ),
      ),
    );

    expect(find.text('Unable to load content.'), findsOneWidget);
    expect(find.text('Please try again.'), findsOneWidget);
    expect(find.text('Try again'), findsOneWidget);

    await tester.tap(find.text('Try again'));
    expect(retried, isTrue);
  });

  testWidgets('AppErrorState renders without optional fields', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.light(useGoogleFonts: false),
        home: const Scaffold(
          body: AppErrorState(message: 'Unable to load content.'),
        ),
      ),
    );

    expect(find.text('Unable to load content.'), findsOneWidget);
    expect(find.byType(FilledButton), findsNothing);
  });

  testWidgets('AppInputBar send button has a semantic label', (tester) async {
    final controller = TextEditingController();
    addTearDown(controller.dispose);

    final semanticsHandle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light(useGoogleFonts: false),
          home: Scaffold(
            body: AppInputBar(
              controller: controller,
              isSending: false,
              showSuggestions: false,
              suggestions: const <String>[],
              onSuggestionSelected: _noopString,
              onSubmit: _noop,
            ),
          ),
        ),
      );

      // The send icon should expose a semantic label so screen readers
      // announce "Send" rather than a bare unlabelled button.
      expect(find.bySemanticsLabel('Send'), findsOneWidget);
    } finally {
      semanticsHandle.dispose();
    }
  });
}

void _noop() {}

void _noopString(String _) {}
