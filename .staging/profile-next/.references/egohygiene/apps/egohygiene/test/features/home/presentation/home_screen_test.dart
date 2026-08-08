import 'package:egohygiene/features/check_in/feature.dart';
import 'package:egohygiene/features/conversation/feature.dart';
import 'package:egohygiene/features/home/feature.dart';
import 'package:egohygiene/features/reflection/feature.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

class _FakeReflectionRepository implements ReflectionRepository {
  _FakeReflectionRepository(this._reflections);

  final List<ReflectionModel> _reflections;

  @override
  Future<ReflectionModel> create({
    required String body,
    String? title,
    List<String> tags = const [],
  }) async {
    final now = DateTime.parse('2026-06-29T10:00:00.000Z');
    final reflection = ReflectionModel(
      id: 'reflection_${_reflections.length + 1}',
      createdAt: now,
      updatedAt: now,
      title: title,
      body: body,
      tags: tags,
    );
    _reflections.insert(0, reflection);
    return reflection;
  }

  @override
  Future<List<ReflectionModel>> getAll() async => _reflections;

  @override
  Future<ReflectionModel?> getById(String id) async {
    for (final reflection in _reflections) {
      if (reflection.id == id) {
        return reflection;
      }
    }
    return null;
  }

  @override
  Future<ReflectionModel> update(ReflectionModel reflection) async => reflection;

  @override
  Future<void> deleteById(String id) async {
    _reflections.removeWhere((r) => r.id == id);
  }
}

class _FakeCheckInRepository implements CheckInRepository {
  _FakeCheckInRepository({this.todaysEntry});

  final CheckInEntry? todaysEntry;

  @override
  Future<List<CheckInEntry>> getAll() async => const [];

  @override
  Future<CheckInEntry?> getById(String id) async => null;

  @override
  Future<CheckInEntry?> getTodaysEntry() async => todaysEntry;

  @override
  Future<CheckInEntry> create({
    required int mood,
    required int energy,
    required int stress,
    required double sleepHours,
    required int focus,
    String? gratitude,
    String? note,
  }) async {
    throw UnimplementedError();
  }

  @override
  Future<CheckInEntry> update(CheckInEntry entry) async => entry;

  @override
  Future<void> deleteById(String id) async {}
}

void main() {
  group('HomeScreen', () {
    testWidgets('renders journey sections and placeholders', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            reflectionRepositoryProvider.overrideWith(
              (ref) => _FakeReflectionRepository(const []),
            ),
            checkInRepositoryProvider.overrideWith(
              (ref) => _FakeCheckInRepository(),
            ),
          ],
          child: TranslationProvider(
            child: MaterialApp(
              theme: AppTheme.light(useGoogleFonts: false),
              home: const HomeScreen(),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Core journey sections visible in the initial viewport.
      expect(find.text("Today's Gentle Rhythm"), findsOneWidget);
      expect(find.text('Daily Check-In'), findsAtLeastNWidgets(1));
      expect(find.text('Conversation'), findsOneWidget);
      expect(find.text('Progress'), findsOneWidget);

      // The empty state card may be just below the fold depending on the
      // viewport, so scroll to it before asserting.
      await tester.scrollUntilVisible(
        find.text('Your journey starts here.'),
        300,
      );
      expect(find.text('Your journey starts here.'), findsOneWidget);
      expect(find.text('Create reflection').first, findsOneWidget);

      // New journey sections — scroll until each becomes visible.
      await tester.scrollUntilVisible(
        find.text("Today's Reflection").last, // Target the actual section card below
        300,
      );
      expect(find.text("Today's Reflection"), findsAtLeastNWidgets(1));

      await tester.scrollUntilVisible(find.text('A Gentle Insight'), 300);
      expect(find.text('A Gentle Insight'), findsOneWidget);

      await tester.scrollUntilVisible(find.text('Evening Review'), 300);
      expect(find.text('Evening Review'), findsOneWidget);

      await tester.scrollUntilVisible(find.text('Explore when needed'), 300);
      expect(find.text('Explore when needed'), findsOneWidget);
      expect(find.text('Reflection'), findsWidgets);
    });

    testWidgets('shows continue action when reflection exists', (tester) async {
      final reflection = ReflectionModel(
        id: 'reflection_1',
        createdAt: DateTime.parse('2026-06-29T10:00:00.000Z'),
        updatedAt: DateTime.parse('2026-06-29T10:00:00.000Z'),
        title: 'Evening Check-in',
        body: 'Noticed more clarity after a short walk.',
        tags: const ['awareness'],
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            reflectionRepositoryProvider.overrideWith(
              (ref) => _FakeReflectionRepository([reflection]),
            ),
            checkInRepositoryProvider.overrideWith(
              (ref) => _FakeCheckInRepository(),
            ),
          ],
          child: TranslationProvider(
            child: MaterialApp(
              theme: AppTheme.light(useGoogleFonts: false),
              home: const HomeScreen(),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Continue reflection'), findsOneWidget);
      expect(find.text('Evening Check-in'), findsOneWidget);
      expect(find.text('Your journey starts here.'), findsNothing);
    });

    testWidgets('adapts rhythm actions when today already has a check-in', (
      tester,
    ) async {
      final entry = CheckInEntry(
        id: 'check_in_1',
        createdAt: DateTime.parse('2026-06-29T08:00:00.000Z'),
        updatedAt: DateTime.parse('2026-06-29T08:00:00.000Z'),
        mood: 4,
        energy: 3,
        stress: 2,
        sleepHours: 7.5,
        focus: 4,
        gratitude: 'A quiet morning',
        note: 'Feeling steady.',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            reflectionRepositoryProvider.overrideWith(
              (ref) => _FakeReflectionRepository(const []),
            ),
            checkInRepositoryProvider.overrideWith(
              (ref) => _FakeCheckInRepository(todaysEntry: entry),
            ),
          ],
          child: TranslationProvider(
            child: MaterialApp(
              theme: AppTheme.light(useGoogleFonts: false),
              home: const HomeScreen(),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // ContinueJourneyCard (in the initial viewport) shows the check-in
      // subtitle exactly once — before DailyCheckInCard scrolls into view.
      expect(
        find.text('You have already paused to notice how today feels.'),
        findsOneWidget,
      );

      // DailyCheckInCard (below the fold) also provides a 'View history'
      // action. Scroll until it becomes visible to confirm both cards offer
      // the action when the user has already checked in today.
      await tester.scrollUntilVisible(find.text('Mood'), 300);
      expect(find.text('View history'), findsNWidgets(2));
    });

    testWidgets('navigates to conversation via explore button', (tester) async {
      final router = GoRouter(
        routes: [
          GoRoute(
            path: '/',
            builder: (context, state) => const HomeScreen(),
          ),
          GoRoute(
            path: '/conversation',
            builder: (context, state) => const ConversationScreen(),
          ),
        ],
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            reflectionRepositoryProvider.overrideWith(
              (ref) => _FakeReflectionRepository(const []),
            ),
            checkInRepositoryProvider.overrideWith(
              (ref) => _FakeCheckInRepository(),
            ),
          ],
          child: TranslationProvider(
            child: MaterialApp.router(
              theme: AppTheme.light(useGoogleFonts: false),
              routerConfig: router,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // The daily rhythm card is shown first, but scroll to ensure the CTA
      // remains visible on smaller test viewports.
      await tester.scrollUntilVisible(
        find.text('Open conversation space'),
        300,
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Open conversation space').first);
      await tester.pumpAndSettle();

      expect(find.text('Conversation'), findsOneWidget);
      expect(find.text('Start a conversation'), findsOneWidget);
    });

    testWidgets('supports large text scaling without layout exceptions', (
      tester,
    ) async {
      await tester.pumpWidget(
        MediaQuery(
          data: const MediaQueryData(
            textScaler: TextScaler.linear(2),
          ),
          child: ProviderScope(
            overrides: [
              reflectionRepositoryProvider.overrideWith(
                (ref) => _FakeReflectionRepository(const []),
              ),
              checkInRepositoryProvider.overrideWith(
                (ref) => _FakeCheckInRepository(),
              ),
            ],
            child: TranslationProvider(
              child: MaterialApp(
                theme: AppTheme.light(useGoogleFonts: false),
                home: const HomeScreen(),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // With 2× text scaling the header expands, pushing lower sections
      // off-screen.  Scroll to "Today's Reflection" before asserting.
      await tester.scrollUntilVisible(find.text("Today's Reflection"), 300);
      expect(find.text("Today's Reflection"), findsAtLeastNWidgets(1));
      expect(tester.takeException(), isNull);
    });
  });
}
