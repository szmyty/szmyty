import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/services/permission_manager.dart';
import 'package:egohygiene/shared/widgets/context_permission_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('shows retry and manual fallback actions for denied permission', (
    tester,
  ) async {
    const request = PermissionRequest(
      permission: PermissionType.location,
      title: 'Location context',
      rationale: 'Needed for timezone context.',
      denialMessage: 'You can keep using the app without this.',
      retryLabel: 'Retry location',
      manualFallback: PermissionManualFallback(
        title: 'Manual location',
        description: 'Set your location manually.',
        actionLabel: 'Use manual location',
      ),
      providerRequirements: [
        PermissionProviderRequirement(
          providerId: 'weather-context-source',
          rationale: 'Supports weather context.',
        ),
      ],
    );
    final state = PermissionState(
      permission: PermissionType.location,
      request: request,
      result: PermissionResult.denied(request),
      requestCount: 1,
    );

    await tester.pumpWidget(
      TranslationProvider(
        child: MaterialApp(
          home: Scaffold(
            body: ContextPermissionCard(
              state: state,
              onRequestOrRetry: () {},
              onUseManualFallback: () {},
            ),
          ),
        ),
      ),
    );

    expect(find.text('You can keep using the app without this.'), findsOneWidget);
    expect(find.text('Retry location'), findsOneWidget);
    expect(find.text('Use manual location'), findsOneWidget);
    expect(find.textContaining('Supports weather context.'), findsOneWidget);
  });
}
