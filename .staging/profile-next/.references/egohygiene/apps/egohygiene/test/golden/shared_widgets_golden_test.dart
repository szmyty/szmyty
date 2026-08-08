import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:egohygiene/shared/widgets/app_card.dart';
import 'package:egohygiene/shared/widgets/app_empty_state.dart';
import 'package:egohygiene/shared/widgets/app_error_state.dart';
import 'package:egohygiene/shared/widgets/app_loading_indicator.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

/// Builds a deterministic [MaterialApp] wrapping [child] with the given [theme].
///
/// [useGoogleFonts] is always `false` so tests do not require network access.
Widget _themed({required Widget child, required ThemeData theme}) {
  return MaterialApp(
    debugShowCheckedModeBanner: false,
    theme: theme,
    home: Scaffold(
      body: Center(child: child),
    ),
  );
}

/// Generates one golden image per theme variant for the given [widget].
///
/// Produces four golden files named
/// `goldens/<name>_<variant>.png` (light, dark, amoled, high_contrast).
Future<void> _multiThemeGolden(
  WidgetTester tester, {
  required String name,
  required Widget widget,
}) async {
  final variants = <String, ThemeData>{
    'light': AppTheme.light(useGoogleFonts: false),
    'dark': AppTheme.dark(useGoogleFonts: false),
    'amoled': AppTheme.amoled(useGoogleFonts: false),
    'high_contrast': AppTheme.highContrast(useGoogleFonts: false),
  };

  for (final entry in variants.entries) {
    await tester.pumpWidget(
      _themed(
        child: widget,
        theme: entry.value,
      ),
    );
    await tester.pump();
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('../goldens/${name}_${entry.key}.png'),
    );
  }
}

void main() {
  group('AppCard golden tests', () {
    testWidgets('renders across all theme variants', (tester) async {
      await tester.binding.setSurfaceSize(const Size(400, 200));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await _multiThemeGolden(
        tester,
        name: 'app_card',
        widget: const SizedBox(
          width: 360,
          child: AppCard(
            child: Text('Golden baseline — AppCard'),
          ),
        ),
      );
    });

    testWidgets('renders tappable variant', (tester) async {
      await tester.binding.setSurfaceSize(const Size(400, 200));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        _themed(
          child: SizedBox(
            width: 360,
            child: AppCard(
              onTap: () {},
              child: const Text('Tappable AppCard'),
            ),
          ),
          theme: AppTheme.light(useGoogleFonts: false),
        ),
      );
      await tester.pump();
      await expectLater(
        find.byType(MaterialApp),
        matchesGoldenFile('../goldens/app_card_tappable.png'),
      );
    });
  });

  group('AppLoadingIndicator golden tests', () {
    testWidgets('renders across all theme variants', (tester) async {
      await tester.binding.setSurfaceSize(const Size(200, 200));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await _multiThemeGolden(
        tester,
        name: 'app_loading_indicator',
        widget: const AppLoadingIndicator(),
      );
    });

    testWidgets('renders non-centered variant', (tester) async {
      await tester.binding.setSurfaceSize(const Size(200, 200));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        _themed(
          child: const AppLoadingIndicator(centered: false),
          theme: AppTheme.light(useGoogleFonts: false),
        ),
      );
      await tester.pump();
      await expectLater(
        find.byType(MaterialApp),
        matchesGoldenFile('../goldens/app_loading_indicator_inline.png'),
      );
    });
  });

  group('AppErrorState golden tests', () {
    testWidgets('renders across all theme variants', (tester) async {
      await tester.binding.setSurfaceSize(const Size(400, 300));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await _multiThemeGolden(
        tester,
        name: 'app_error_state',
        widget: const SizedBox(
          width: 360,
          child: AppErrorState(
            message: 'Something went wrong',
            description: 'Please try again.',
          ),
        ),
      );
    });

    testWidgets('renders with action button', (tester) async {
      await tester.binding.setSurfaceSize(const Size(400, 320));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        _themed(
          child: SizedBox(
            width: 360,
            child: AppErrorState(
              message: 'Something went wrong',
              description: 'Please try again.',
              action: FilledButton(
                onPressed: () {},
                child: const Text('Try again'),
              ),
            ),
          ),
          theme: AppTheme.light(useGoogleFonts: false),
        ),
      );
      await tester.pump();
      await expectLater(
        find.byType(MaterialApp),
        matchesGoldenFile('../goldens/app_error_state_with_action.png'),
      );
    });
  });

  group('AppEmptyState golden tests', () {
    testWidgets('renders across all theme variants', (tester) async {
      await tester.binding.setSurfaceSize(const Size(400, 320));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await _multiThemeGolden(
        tester,
        name: 'app_empty_state',
        widget: const SizedBox(
          width: 360,
          child: AppEmptyState(
            icon: Icons.inbox_outlined,
            title: 'Nothing here yet',
            description: 'Your entries will appear here.',
          ),
        ),
      );
    });

    testWidgets('renders with action button', (tester) async {
      await tester.binding.setSurfaceSize(const Size(400, 360));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        _themed(
          child: SizedBox(
            width: 360,
            child: AppEmptyState(
              icon: Icons.inbox_outlined,
              title: 'Nothing here yet',
              description: 'Your entries will appear here.',
              action: FilledButton(
                onPressed: () {},
                child: const Text('Create entry'),
              ),
            ),
          ),
          theme: AppTheme.light(useGoogleFonts: false),
        ),
      );
      await tester.pump();
      await expectLater(
        find.byType(MaterialApp),
        matchesGoldenFile('../goldens/app_empty_state_with_action.png'),
      );
    });
  });
}
