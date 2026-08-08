import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:egohygiene/shared/widgets/app_section_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('exposes the section title as a semantic header', (tester) async {
    final semanticsHandle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light(useGoogleFonts: false),
          home: const Scaffold(
            body: AppSectionCard(
              title: 'Accessibility',
              subtitle: 'Shared foundation',
              icon: Icons.accessibility_new,
              child: Text('Reusable content'),
            ),
          ),
        ),
      );

      final semantics = tester.getSemantics(find.text('Accessibility'));
      expect(semantics.flagsCollection.isHeader, isTrue);
      expect(semantics.label, contains('Accessibility'));
    } finally {
      semanticsHandle.dispose();
    }
  });

  testWidgets('renders safely with large text scaling', (tester) async {
    await tester.pumpWidget(
      MediaQuery(
        data: const MediaQueryData(textScaler: TextScaler.linear(2)),
        child: MaterialApp(
          theme: AppTheme.light(useGoogleFonts: false),
          home: const Scaffold(
            body: AppSectionCard(
              title: 'Accessibility',
              subtitle: 'Shared foundation',
              child: Text('Reusable content'),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Accessibility'), findsOneWidget);
    expect(find.text('Reusable content'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
