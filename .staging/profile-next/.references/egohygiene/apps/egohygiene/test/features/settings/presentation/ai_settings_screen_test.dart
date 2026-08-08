import 'package:egohygiene/features/settings/presentation/ai_settings_screen.dart';
import 'package:egohygiene/features/settings/providers/ai_settings_providers.dart';
import 'package:egohygiene/features/settings/providers/settings_providers.dart';
import 'package:egohygiene/shared/ai/ai_mode.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/providers/ai_provider_registry_providers.dart';
import 'package:egohygiene/shared/providers/ai_tool_registry_providers.dart';
import 'package:egohygiene/shared/providers/storage_providers.dart';
import 'package:egohygiene/shared/services/ai_provider.dart';
import 'package:egohygiene/shared/services/ai_tool.dart';
import 'package:egohygiene/shared/settings/settings_category.dart';
import 'package:egohygiene/shared/settings/settings_definition.dart';
import 'package:egohygiene/shared/settings/settings_entry.dart';
import 'package:egohygiene/shared/settings/settings_manager.dart';
import 'package:egohygiene/shared/settings/settings_repository.dart';
import 'package:egohygiene/shared/settings/settings_value.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod/misc.dart' show Override;

import '../../../helpers/fake_storage_service.dart';

class _InMemorySettingsRepository implements SettingsRepository {
  final Map<String, SettingsEntry> _store = {};

  @override
  Future<void> init() async {}

  @override
  Future<SettingsEntry?> get(String key) async => _store[key];

  @override
  Future<void> save(SettingsEntry entry) async => _store[entry.key] = entry;

  @override
  Future<void> delete(String key) async => _store.remove(key);

  @override
  Future<Map<String, SettingsEntry>> getAll() async => Map.of(_store);

  @override
  Future<void> clear() async => _store.clear();
}

// ---------------------------------------------------------------------------
// Minimal fake provider for override tests
// ---------------------------------------------------------------------------

class _FakeProvider implements AIProvider {
  const _FakeProvider({
    required this.name,
    required this.configuration,
  }) : providerStatus = AIProviderStatus.available;

  @override
  final String name;

  @override
  final AIProviderConfiguration configuration;

  final AIProviderStatus providerStatus;

  @override
  AIProviderStatus get status => providerStatus;

  @override
  ProviderCapabilities get capabilities => const ProviderCapabilities(
    chat: true,
    localFirst: true,
  );

  @override
  Future<void> init() async {}

  @override
  Future<bool> isAvailable() async => providerStatus == AIProviderStatus.available;
}

// ---------------------------------------------------------------------------
// Minimal fake tool for override tests
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
  Set<ToolCapability> get capabilities => const {ToolCapability.local};

  @override
  List<ToolParameter> get parameters => const [];

  @override
  Future<ToolResult> invoke(ToolInvocation invocation) async {
    return ToolResult(
      invocationId: invocation.invocationId,
      output: 'fake output',
    );
  }
}

List<Override> _makeOverrides() {
  final repository = _InMemorySettingsRepository();
  return [
    storageServiceProvider.overrideWithValue(FakeStorageService()),
    settingsRepositoryProvider.overrideWith((_) => repository),
    settingsManagerProvider.overrideWith((_) {
      const aiModeDef = SettingsDefinition(
        key: 'ai.mode',
        category: SettingsCategory.ai,
        defaultValue: StringSettingsValue('disabled'),
        label: 'AI Mode',
      );
      const aiPrivacyDef = SettingsDefinition(
        key: 'ai.privacy_mode',
        category: SettingsCategory.ai,
        defaultValue: BoolSettingsValue(false),
        label: 'Privacy Mode',
      );
      final manager = SettingsManager(repository: repository);
      manager.registerAll([aiModeDef, aiPrivacyDef]);
      return manager;
    }),
  ];
}

Widget _buildApp({List<Override> overrides = const []}) {
  final router = GoRouter(
    initialLocation: '/settings/ai',
    routes: [
      GoRoute(
        path: '/settings',
        builder: (context, state) => const Scaffold(body: Center(child: Text('Settings'))),
        routes: [
          GoRoute(
            path: 'ai',
            builder: (context, state) => const AiSettingsScreen(),
          ),
        ],
      ),
    ],
  );

  return ProviderScope(
    overrides: [..._makeOverrides(), ...overrides],
    child: TranslationProvider(
      child: MaterialApp.router(
        theme: AppTheme.light(useGoogleFonts: false),
        routerConfig: router,
      ),
    ),
  );
}

void main() {
  // Amount to drag in each scroll step when using scrollUntilVisible.
  const scrollDelta = 100.0;

  group('AiSettingsScreen', () {
    testWidgets('renders without errors', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      expect(find.byType(AiSettingsScreen), findsOneWidget);
    });

    testWidgets('shows all four AI mode options', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      expect(find.text('Cloud'), findsOneWidget);
      expect(find.text('Local'), findsOneWidget);
      expect(find.text('Hybrid'), findsOneWidget);
      expect(find.text('Disabled'), findsOneWidget);
    });

    testWidgets('shows privacy mode switch', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      // The Privacy section is below the fold; scroll to it first.
      await tester.scrollUntilVisible(
        find.byType(SwitchListTile),
        scrollDelta,
        scrollable: find.byType(Scrollable).first,
      );
      expect(find.byType(SwitchListTile), findsOneWidget);
    });

    testWidgets('tapping a mode option selects it', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      // Tap the Cloud option
      await tester.tap(find.text('Cloud'));
      await tester.pumpAndSettle();

      // The check icon should now be visible for Cloud
      expect(find.byIcon(Icons.check_circle_rounded), findsOneWidget);
    });

    testWidgets('back button pops the screen', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.arrow_back));
      await tester.pumpAndSettle();

      expect(find.text('Settings'), findsOneWidget);
    });

    testWidgets('privacy switch can be toggled', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      // The Privacy section is below the fold; scroll to it first.
      final switchListTileFinder = find.byType(SwitchListTile);
      await tester.scrollUntilVisible(
        switchListTileFinder,
        scrollDelta,
        scrollable: find.byType(Scrollable).first,
      );

      // scrollUntilVisible brings the SwitchListTile into the render tree but
      // the Switch's tap-target centre can still sit just outside the 600-px
      // test viewport.  ensureVisible scrolls the Switch itself fully into
      // view before we interact with it.
      final switchFinder = find.byType(Switch);
      await tester.ensureVisible(switchFinder);
      await tester.pumpAndSettle();
      final initialSwitch = tester.widget<Switch>(switchFinder);
      expect(initialSwitch.value, isFalse);

      await tester.tap(switchFinder);
      await tester.pumpAndSettle();

      final updatedSwitch = tester.widget<Switch>(switchFinder);
      expect(updatedSwitch.value, isTrue);
    });

    testWidgets('disabled mode is selected by default', (tester) async {
      await tester.pumpWidget(_buildApp());
      await tester.pumpAndSettle();

      // Only one check icon should be visible (for disabled)
      expect(find.byIcon(Icons.check_circle_rounded), findsOneWidget);
    });

    testWidgets('overriding aiModeProvider shows pre-selected mode', (tester) async {
      await tester.pumpWidget(
        _buildApp(
          overrides: [
            aiModeProvider.overrideWith(_HybridModeNotifier.new),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.check_circle_rounded), findsOneWidget);
    });

    // -------------------------------------------------------------------------
    // Provider section
    // -------------------------------------------------------------------------

    group('Provider section', () {
      testWidgets('shows provider section heading', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        expect(find.text('AI Providers'), findsOneWidget);
      });

      testWidgets('shows demo provider by default', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        expect(find.text('Demo AI Provider'), findsOneWidget);
      });

      testWidgets('shows available status for demo provider', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        expect(find.text('Available'), findsOneWidget);
      });

      testWidgets('shows empty state when registry has no providers', (tester) async {
        final emptyRegistry = AIProviderRegistry();
        await tester.pumpWidget(
          _buildApp(
            overrides: [
              aiProviderRegistryProvider.overrideWithValue(emptyRegistry),
            ],
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('No providers registered'), findsOneWidget);
      });

      testWidgets('shows custom provider name from overridden registry', (tester) async {
        final registry = AIProviderRegistry();
        registry.register(
          const _FakeProvider(
            name: 'Test Provider',
            configuration: AIProviderConfiguration(
              id: 'test',
              displayName: 'Test Provider',
            ),
          ),
        );

        await tester.pumpWidget(
          _buildApp(
            overrides: [
              aiProviderRegistryProvider.overrideWithValue(registry),
            ],
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Test Provider'), findsOneWidget);
      });
    });

    // -------------------------------------------------------------------------
    // Tool section
    // -------------------------------------------------------------------------

    group('Tool section', () {
      testWidgets('shows tool section heading', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        // The Tool section is further down the page; scroll to it.
        await tester.scrollUntilVisible(
          find.text('AI Tools'),
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(find.text('AI Tools'), findsOneWidget);
      });

      testWidgets('shows default demo tools (first tool is visible)', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        // The Reflection tool is always first – scroll to it then verify.
        await tester.scrollUntilVisible(
          find.text('Reflection'),
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(find.text('Reflection'), findsOneWidget);
      });

      testWidgets('shows all seven default tool names when scrolled', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        const toolNames = [
          'Reflection',
          'Timeline',
          'Practice',
          'Goal',
          'Insight',
          'Knowledge Graph',
          'Research',
        ];

        for (final name in toolNames) {
          // Scroll until the tool name is visible, then verify it is found.
          await tester.scrollUntilVisible(
            find.text(name),
            scrollDelta,
            scrollable: find.byType(Scrollable).first,
          );
          expect(find.text(name), findsOneWidget);
        }
      });

      testWidgets('shows empty state when tool registry is empty', (tester) async {
        final emptyRegistry = ToolRegistry();
        await tester.pumpWidget(
          _buildApp(
            overrides: [
              aiToolRegistryProvider.overrideWithValue(emptyRegistry),
            ],
          ),
        );
        await tester.pumpAndSettle();

        final emptyFinder = find.text('No tools registered');
        await tester.scrollUntilVisible(
          emptyFinder,
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(emptyFinder, findsOneWidget);
      });

      testWidgets('shows custom tool name from overridden registry', (tester) async {
        final registry = ToolRegistry()
          ..register(
            const _FakeTool(
              id: 'custom',
              name: 'Custom Tool',
              description: 'A custom test tool',
            ),
          );

        await tester.pumpWidget(
          _buildApp(
            overrides: [
              aiToolRegistryProvider.overrideWithValue(registry),
            ],
          ),
        );
        await tester.pumpAndSettle();

        final nameFinder = find.text('Custom Tool');
        await tester.scrollUntilVisible(
          nameFinder,
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(nameFinder, findsOneWidget);
        expect(find.text('A custom test tool'), findsOneWidget);
      });
    });

    // -------------------------------------------------------------------------
    // Privacy section
    // -------------------------------------------------------------------------

    group('Privacy section', () {
      testWidgets('shows privacy section heading when scrolled', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        await tester.scrollUntilVisible(
          find.text('Privacy'),
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(find.text('Privacy'), findsOneWidget);
      });

      testWidgets('shows tradeoff note when privacy mode is off and scrolled', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        final noteFinder = find.textContaining('Cloud AI may offer better quality');
        await tester.scrollUntilVisible(
          noteFinder,
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(noteFinder, findsOneWidget);
      });

      testWidgets('shows local-only note when privacy mode is on and scrolled', (tester) async {
        await tester.pumpWidget(
          _buildApp(
            overrides: [
              aiPrivacyModeProvider.overrideWith(_PrivacyOnNotifier.new),
            ],
          ),
        );
        await tester.pumpAndSettle();

        final noteFinder = find.textContaining('requests stay on-device');
        await tester.scrollUntilVisible(
          noteFinder,
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(noteFinder, findsOneWidget);
      });
    });

    // -------------------------------------------------------------------------
    // Debug section
    // -------------------------------------------------------------------------

    group('Debug section', () {
      testWidgets('shows debug section heading when scrolled', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        await tester.scrollUntilVisible(
          find.text('Debug Information'),
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(find.text('Debug Information'), findsOneWidget);
      });

      testWidgets('shows active mode label when scrolled', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        await tester.scrollUntilVisible(
          find.text('Active mode'),
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(find.text('Active mode'), findsOneWidget);
      });

      testWidgets('shows registered providers label when scrolled', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        await tester.scrollUntilVisible(
          find.text('Registered providers'),
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(find.text('Registered providers'), findsOneWidget);
      });

      testWidgets('shows available tools label when scrolled', (tester) async {
        await tester.pumpWidget(_buildApp());
        await tester.pumpAndSettle();

        await tester.scrollUntilVisible(
          find.text('Available tools'),
          scrollDelta,
          scrollable: find.byType(Scrollable).first,
        );
        expect(find.text('Available tools'), findsOneWidget);
      });
    });
  });
}

// ---------------------------------------------------------------------------
// Stub notifiers
// ---------------------------------------------------------------------------

/// Stub notifier that always resolves to [AiMode.hybrid] for testing.
class _HybridModeNotifier extends AiModeNotifier {
  @override
  Future<AiMode> build() async => AiMode.hybrid;
}

/// Stub notifier that always resolves privacy mode to `true` for testing.
class _PrivacyOnNotifier extends AiPrivacyModeNotifier {
  @override
  Future<bool> build() async => true;
}
