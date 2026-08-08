import 'package:egohygiene/features/settings/presentation/update_experience_screen.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/providers/version_providers.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:egohygiene/shared/version/app_version.dart';
import 'package:egohygiene/shared/version/release_metadata.dart';
import 'package:egohygiene/shared/version/update_install_mode.dart';
import 'package:egohygiene/shared/version/update_provider.dart';
import 'package:egohygiene/shared/version/version_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

class _FakeVersionService implements VersionService {
  _FakeVersionService(this.version);

  final String version;

  @override
  Future<String> currentVersion() async => version;
}

class _FakeUpdateProvider implements UpdateProvider {
  _FakeUpdateProvider({
    required this.providerId,
    this.release,
  }) : available = true;

  @override
  final String providerId;

  final bool available;
  final ReleaseMetadata? release;

  @override
  Future<bool> get isAvailable async => available;

  @override
  Future<ReleaseMetadata?> fetchLatestRelease({
    String channel = 'stable',
  }) async => release;
}

Widget _buildApp({
  required String currentVersion,
  required ReleaseMetadata release,
}) {
  final router = GoRouter(
    initialLocation: '/settings/updates',
    routes: [
      GoRoute(
        path: '/settings/updates',
        builder: (context, state) => const UpdateExperienceScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const Scaffold(body: Center(child: Text('Settings'))),
      ),
    ],
  );

  return ProviderScope(
    overrides: [
      versionServiceProvider.overrideWithValue(
        _FakeVersionService(currentVersion),
      ),
      updateProviderProvider.overrideWithValue(
        _FakeUpdateProvider(
          providerId: release.providerId,
          release: release,
        ),
      ),
    ],
    child: TranslationProvider(
      child: MaterialApp.router(
        theme: AppTheme.light(useGoogleFonts: false),
        routerConfig: router,
      ),
    ),
  );
}

void main() {
  ReleaseMetadata flexibleRelease() {
    return ReleaseMetadata(
      providerId: 'play',
      version: AppVersion.parse('1.1.0'),
      publishedAt: DateTime.utc(2026, 7, 1, 12),
      estimatedInstallDuration: 'About 2 minutes',
      highlights: const [
        'Calmer update timing',
        'Clearer release highlights',
        'Migration guidance when needed',
      ],
      releaseNotes: 'A calmer update experience.\n- Flexible update path\n- Required upgrade messaging',
      migrationNotes: const ['Sign in again if your session expires.'],
      availableModes: const {
        UpdateInstallMode.flexible,
        UpdateInstallMode.immediate,
      },
    );
  }

  testWidgets('shows flexible update dialog and release highlights', (tester) async {
    await tester.pumpWidget(
      _buildApp(
        currentVersion: '1.0.0',
        release: flexibleRelease(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Later'), findsOneWidget);
    expect(find.text('Update in background'), findsWidgets);
    expect(find.text('Calmer update timing'), findsWidgets);
    expect(find.textContaining('About 2 minutes'), findsWidgets);
  });

  testWidgets('shows required update flow when minimum supported version is newer', (tester) async {
    final release = ReleaseMetadata(
      providerId: 'play',
      version: AppVersion.parse('2.0.0'),
      publishedAt: DateTime.utc(2026, 7, 1, 12),
      minimumSupportedVersion: AppVersion.parse('1.5.0'),
      availableModes: const {UpdateInstallMode.immediate},
      highlights: const ['A breaking platform migration'],
    );

    await tester.pumpWidget(
      _buildApp(
        currentVersion: '1.0.0',
        release: release,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Required update'), findsWidgets);
    expect(find.text('Later'), findsNothing);
    expect(find.text('Update now'), findsWidgets);
  });

  testWidgets('opens release notes viewer with migration notes', (tester) async {
    await tester.pumpWidget(
      _buildApp(
        currentVersion: '1.1.0',
        release: flexibleRelease(),
      ),
    );
    await tester.pumpAndSettle();

    // The "Open release notes viewer" button may be below the fold.
    // scrollUntilVisible brings it into the render tree, but its centre can
    // still sit outside the 600-px viewport. ensureVisible then scrolls it
    // fully into view before the tap.
    await tester.scrollUntilVisible(
      find.text('Open release notes viewer'),
      100,
    );
    await tester.ensureVisible(find.text('Open release notes viewer'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Open release notes viewer'));
    await tester.pumpAndSettle();

    expect(find.text('Release notes for 1.1.0'), findsOneWidget);
    expect(find.text('Migration notes'), findsAtLeastNWidgets(1));
    expect(find.text('Sign in again if your session expires.'), findsAtLeastNWidgets(1));
  });

  testWidgets('shows progress and welcome content after starting an update', (tester) async {
    await tester.pumpWidget(
      _buildApp(
        currentVersion: '1.0.0',
        release: flexibleRelease(),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(
      find.descendant(
        of: find.byType(AlertDialog),
        matching: find.widgetWithText(FilledButton, 'Update in background'),
      ),
    );
    await tester.pump();

    // The progress indicator may be below the fold after tapping the button.
    await tester.scrollUntilVisible(
      find.byType(LinearProgressIndicator),
      100,
    );
    expect(find.byType(LinearProgressIndicator), findsOneWidget);

    // With this loop to step through the 3 sequential Future.delayed calls:
    for (var i = 0; i < 3; i++) {
      await tester.pump(const Duration(seconds: 1));
    }
    await tester.pumpAndSettle();

    // UpdateStatusSection at the top of the list becomes visible after the
    // update completes and the list rebuilds with the "up to date" state.
    await tester.scrollUntilVisible(find.text('You\u2019re up to date'), -100);
    expect(find.text('You\u2019re up to date'), findsOneWidget);

    // UpdateWelcomeSection is appended at the bottom of the list and may not
    // yet be in the render tree at the current scroll position.  Scroll to
    // it before asserting its presence.
    await tester.scrollUntilVisible(find.text('Welcome to 1.1.0'), 100);
    expect(find.text('Welcome to 1.1.0'), findsOneWidget);
  });
}
