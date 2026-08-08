import 'dart:async';

import 'package:egohygiene/features/health/presentation/health_screen.dart';
import 'package:egohygiene/features/health/providers/health_feature_providers.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/personal_health/health_item.dart';
import 'package:egohygiene/shared/personal_health/health_item_category.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod/misc.dart' show Override;

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

HealthItem _item({
  String id = 'h-1',
  String name = 'Vitamin D3',
  HealthItemCategory category = HealthItemCategory.vitamin,
  String? purpose = 'Bone health',
  bool isActive = true,
  DateTime? createdAt,
}) {
  final now = DateTime(2026);
  return HealthItem(
    id: id,
    name: name,
    category: category,
    purpose: purpose,
    isActive: isActive,
    createdAt: createdAt ?? now,
    updatedAt: createdAt ?? now,
  );
}

Widget _wrap(Widget child, {List<Override> overrides = const []}) {
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp(
      theme: AppTheme.light(useGoogleFonts: false),
      home: TranslationProvider(child: child),
    ),
  );
}

void main() {
  group('HealthScreen', () {
    testWidgets('renders app bar with Health Stack title', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const HealthScreen(),
          overrides: [
            healthItemsProvider.overrideWith((_) async => const []),
          ],
        ),
      );
      await tester.pump();

      expect(find.text('Health Stack'), findsOneWidget);
    });

    testWidgets('shows empty state when no items', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const HealthScreen(),
          overrides: [
            healthItemsProvider.overrideWith((_) async => const []),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('No health items yet'), findsOneWidget);
    });

    testWidgets('renders item cards for each health item', (tester) async {
      final items = [
        _item(id: 'i-1'),
        _item(id: 'i-2', name: 'Omega-3'),
      ];

      await tester.pumpWidget(
        _wrap(
          const HealthScreen(),
          overrides: [
            healthItemsProvider.overrideWith((_) async => items),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Vitamin D3'), findsOneWidget);
      expect(find.text('Omega-3'), findsOneWidget);
    });

    testWidgets('displays loading indicator while fetching', (tester) async {
      // Use a Completer that never resolves to keep the provider in loading
      // state without leaving any pending timers that would fail test cleanup.
      final completer = Completer<List<HealthItem>>();
      await tester.pumpWidget(
        _wrap(
          const HealthScreen(),
          overrides: [
            healthItemsProvider.overrideWith(
              (_) => completer.future,
            ),
          ],
        ),
      );

      // Only pump one frame — loading state should still be visible.
      await tester.pump();

      expect(find.byType(CircularProgressIndicator), findsWidgets);
    });

    testWidgets('shows category chips in filter bar', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const HealthScreen(),
          overrides: [
            healthItemsProvider.overrideWith((_) async => const []),
          ],
        ),
      );
      await tester.pump();

      // The "All" chip should always be present.
      expect(find.text('All'), findsOneWidget);
    });

    testWidgets('shows filtered empty state when category selected but empty', (tester) async {
      await tester.pumpWidget(
        _wrap(
          const HealthScreen(),
          overrides: [
            healthItemsProvider.overrideWith((_) async => const []),
            healthCategoryFilterProvider.overrideWith((_) => HealthItemCategory.prescription),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('No items in this category'), findsOneWidget);
    });

    testWidgets('item card shows brand when set', (tester) async {
      final items = [
        HealthItem(
          id: 'b-1',
          name: 'Vitamin D3',
          brand: 'Nature Made',
          category: HealthItemCategory.vitamin,
          createdAt: DateTime(2026),
          updatedAt: DateTime(2026),
        ),
      ];

      await tester.pumpWidget(
        _wrap(
          const HealthScreen(),
          overrides: [
            healthItemsProvider.overrideWith((_) async => items),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Nature Made'), findsOneWidget);
    });
  });
}
