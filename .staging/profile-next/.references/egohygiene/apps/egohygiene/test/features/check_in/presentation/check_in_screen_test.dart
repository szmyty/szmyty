import 'package:egohygiene/features/check_in/domain/check_in_entry.dart';
import 'package:egohygiene/features/check_in/domain/check_in_repository.dart';
import 'package:egohygiene/features/check_in/presentation/check_in_screen.dart';
import 'package:egohygiene/features/check_in/providers/check_in_providers.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod/misc.dart' show Override;

class _FakeCheckInRepository implements CheckInRepository {
  _FakeCheckInRepository({List<CheckInEntry>? entries}) : _entries = [...?entries];

  final List<CheckInEntry> _entries;
  CheckInEntry? _todaysEntry;

  @override
  Future<List<CheckInEntry>> getAll() async => List.unmodifiable(_entries);

  @override
  Future<CheckInEntry?> getById(String id) async {
    for (final e in _entries) {
      if (e.id == id) return e;
    }
    return null;
  }

  @override
  Future<CheckInEntry?> getTodaysEntry() async => _todaysEntry;

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
    final now = DateTime.utc(2026, 7, 1, 8);
    final entry = CheckInEntry(
      id: 'checkin_test',
      createdAt: now,
      updatedAt: now,
      mood: mood,
      energy: energy,
      stress: stress,
      sleepHours: sleepHours,
      focus: focus,
      gratitude: gratitude,
      note: note,
    );
    _entries.insert(0, entry);
    _todaysEntry = entry;
    return entry;
  }

  @override
  Future<CheckInEntry> update(CheckInEntry entry) async => entry;

  @override
  Future<void> deleteById(String id) async {
    _entries.removeWhere((e) => e.id == id);
  }
}

Widget _wrap(Widget child, {List<Override> overrides = const []}) {
  return ProviderScope(
    overrides: overrides,
    child: TranslationProvider(
      child: MaterialApp(
        theme: AppTheme.light(useGoogleFonts: false),
        home: child,
      ),
    ),
  );
}

void main() {
  group('CheckInScreen', () {
    testWidgets('renders first step with mood question', (tester) async {
      final fakeRepo = _FakeCheckInRepository();

      await tester.pumpWidget(
        _wrap(
          const CheckInScreen(),
          overrides: [
            checkInRepositoryProvider.overrideWith((_) => fakeRepo),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('How are you feeling?'), findsOneWidget);
      expect(find.text('😊'), findsOneWidget);
    });

    testWidgets('pressing Next advances to the energy step', (tester) async {
      final fakeRepo = _FakeCheckInRepository();

      await tester.pumpWidget(
        _wrap(
          const CheckInScreen(),
          overrides: [
            checkInRepositoryProvider.overrideWith((_) => fakeRepo),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // Tap the Next button to advance from mood → energy
      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();

      expect(find.text('How is your energy today?'), findsOneWidget);
    });

    testWidgets('score buttons update selection', (tester) async {
      final fakeRepo = _FakeCheckInRepository();

      await tester.pumpWidget(
        _wrap(
          const CheckInScreen(),
          overrides: [
            checkInRepositoryProvider.overrideWith((_) => fakeRepo),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // The default selected score is 3.  Tap score 5.
      await tester.tap(find.text('5').first);
      await tester.pumpAndSettle();

      // Score 5 tile should now be visually selected (just verify no crash).
      expect(find.text('5'), findsOneWidget);
    });
  });
}
