import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/routing/app_navigation_shell.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

/// Minimal router used by shell tests.
///
/// Each branch contains a single [GoRoute] with a plain text body so tests
/// can verify which branch is currently active without depending on the real
/// feature screens.
GoRouter _buildTestRouter() => GoRouter(
  initialLocation: '/',
  routes: [
    StatefulShellRoute.indexedStack(
      builder: (context, state, navigationShell) => AppNavigationShell(navigationShell: navigationShell),
      branches: [
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/',
              builder: (_, _) => const Scaffold(body: Center(child: Text('Home Screen'))),
            ),
          ],
        ),
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/reflection',
              builder: (_, _) => const Scaffold(body: Center(child: Text('Reflection Screen'))),
              routes: [
                GoRoute(
                  path: 'detail',
                  builder: (_, _) => const Scaffold(
                    body: Center(child: Text('Reflection Detail')),
                  ),
                ),
              ],
            ),
          ],
        ),
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/conversation',
              builder: (_, _) => const Scaffold(
                body: Center(child: Text('Conversation Screen')),
              ),
            ),
          ],
        ),
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/progress',
              builder: (_, _) => const Scaffold(body: Center(child: Text('Progress Screen'))),
            ),
          ],
        ),
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/memory',
              builder: (_, _) => const Scaffold(body: Center(child: Text('Memory Screen'))),
            ),
          ],
        ),
      ],
    ),
  ],
);

Widget _buildApp(GoRouter router) => TranslationProvider(
  child: MaterialApp.router(
    routerConfig: router,
    theme: AppTheme.light(useGoogleFonts: false),
  ),
);

void main() {
  group('AppNavigationShell', () {
    testWidgets('renders NavigationBar with five destinations', (tester) async {
      final router = _buildTestRouter();
      await tester.pumpWidget(_buildApp(router));
      await tester.pumpAndSettle();

      expect(find.byType(NavigationBar), findsOneWidget);
      expect(find.byType(NavigationDestination), findsNWidgets(5));
    });

    testWidgets('shows home content on initial load', (tester) async {
      final router = _buildTestRouter();
      await tester.pumpWidget(_buildApp(router));
      await tester.pumpAndSettle();

      expect(find.text('Home Screen'), findsOneWidget);
    });

    testWidgets('navigates to reflection tab on tap', (tester) async {
      final router = _buildTestRouter();
      await tester.pumpWidget(_buildApp(router));
      await tester.pumpAndSettle();

      // The body uses placeholder text so nav-bar labels are unambiguous.
      await tester.tap(find.text('Reflection'));
      await tester.pumpAndSettle();

      expect(find.text('Reflection Screen'), findsOneWidget);
      expect(find.text('Home Screen'), findsNothing);
    });

    testWidgets('navigates to conversation tab on tap', (tester) async {
      final router = _buildTestRouter();
      await tester.pumpWidget(_buildApp(router));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Conversation'));
      await tester.pumpAndSettle();

      expect(find.text('Conversation Screen'), findsOneWidget);
    });

    testWidgets('navigates to progress tab on tap', (tester) async {
      final router = _buildTestRouter();
      await tester.pumpWidget(_buildApp(router));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Progress'));
      await tester.pumpAndSettle();

      expect(find.text('Progress Screen'), findsOneWidget);
    });

    testWidgets('navigates to memory tab on tap', (tester) async {
      final router = _buildTestRouter();
      await tester.pumpWidget(_buildApp(router));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Memory'));
      await tester.pumpAndSettle();

      expect(find.text('Memory Screen'), findsOneWidget);
    });

    testWidgets('preserves branch state when switching tabs', (tester) async {
      final router = _buildTestRouter();
      await tester.pumpWidget(_buildApp(router));
      await tester.pumpAndSettle();

      // Navigate to reflection and push a nested route.
      await tester.tap(find.text('Reflection'));
      await tester.pumpAndSettle();
      router.push('/reflection/detail');
      await tester.pumpAndSettle();
      expect(find.text('Reflection Detail'), findsOneWidget);

      // Switch to conversation – reflection branch is suspended but preserved.
      await tester.tap(find.text('Conversation'));
      await tester.pumpAndSettle();
      expect(find.text('Conversation Screen'), findsOneWidget);
      expect(find.text('Reflection Detail'), findsNothing);

      // Switch back to reflection – nested route should still be on the stack.
      await tester.tap(find.text('Reflection'));
      await tester.pumpAndSettle();
      expect(find.text('Reflection Detail'), findsOneWidget);
    });

    testWidgets('re-tapping active tab returns to branch root', (tester) async {
      final router = _buildTestRouter();
      await tester.pumpWidget(_buildApp(router));
      await tester.pumpAndSettle();

      // Navigate to reflection and push a nested route.
      await tester.tap(find.text('Reflection'));
      await tester.pumpAndSettle();
      router.push('/reflection/detail');
      await tester.pumpAndSettle();
      expect(find.text('Reflection Detail'), findsOneWidget);

      // Re-tap the reflection tab — should pop back to the branch root.
      await tester.tap(find.text('Reflection'));
      await tester.pumpAndSettle();
      expect(find.text('Reflection Screen'), findsOneWidget);
      expect(find.text('Reflection Detail'), findsNothing);
    });

    testWidgets('NavigationBar labels match destination names', (tester) async {
      final router = _buildTestRouter();
      await tester.pumpWidget(_buildApp(router));
      await tester.pumpAndSettle();

      // Labels are rendered by NavigationDestination inside NavigationBar.
      // Use the NavigationBar widget as ancestor to disambiguate.
      final navBar = find.byType(NavigationBar);
      expect(find.descendant(of: navBar, matching: find.text('Home')), findsOneWidget);
      expect(find.descendant(of: navBar, matching: find.text('Reflection')), findsOneWidget);
      expect(find.descendant(of: navBar, matching: find.text('Conversation')), findsOneWidget);
      expect(find.descendant(of: navBar, matching: find.text('Progress')), findsOneWidget);
      expect(find.descendant(of: navBar, matching: find.text('Memory')), findsOneWidget);
    });
  });
}
