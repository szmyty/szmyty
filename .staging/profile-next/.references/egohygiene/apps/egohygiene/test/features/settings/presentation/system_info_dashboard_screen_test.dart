import 'package:egohygiene/features/settings/presentation/system_info_dashboard_screen.dart';
import 'package:egohygiene/features/settings/providers/system_info_providers.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/theme/app_theme.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod/misc.dart' show Override;

Widget _buildApp({List<Override> overrides = const []}) {
  final router = GoRouter(
    initialLocation: '/settings/debug/system',
    routes: [
      GoRoute(
        path: '/settings',
        builder: (context, state) => const Scaffold(body: Center(child: Text('Settings'))),
        routes: [
          GoRoute(
            path: 'debug',
            builder: (context, state) => const Scaffold(body: Center(child: Text('Debug Center'))),
            routes: [
              GoRoute(
                path: 'system',
                builder: (context, state) => const SystemInfoDashboardScreen(),
              ),
            ],
          ),
        ],
      ),
    ],
  );

  return ProviderScope(
    overrides: overrides,
    child: TranslationProvider(
      child: MaterialApp.router(
        theme: AppTheme.light(useGoogleFonts: false),
        routerConfig: router,
      ),
    ),
  );
}

void main() {
  testWidgets('renders all dashboard sections with provider overrides', (tester) async {
    await tester.pumpWidget(
      _buildApp(
        overrides: [
          appInfoProvider.overrideWith(
            (ref) async => const AppInfoData(
              appName: 'Ego Hygiene',
              packageName: 'io.egohygiene.app',
              version: '1.0.0',
              buildNumber: '42',
              buildMode: 'debug',
            ),
          ),
          deviceInfoProvider.overrideWith(
            (ref) async => const DeviceInfoData(
              platform: 'android',
              osVersion: '14',
              model: 'Pixel',
              manufacturer: 'Google',
              deviceType: 'Mobile',
              isPhysicalDevice: true,
            ),
          ),
          batteryStreamProvider.overrideWith(
            (ref) => Stream.value(
              const BatteryInfoData(
                level: 88,
                state: 'Charging',
                isBatterySaverOn: false,
                levelHistory: [82, 84, 88],
              ),
            ),
          ),
          connectivityStreamProvider.overrideWith(
            (ref) => Stream.value(
              const ConnectivityInfoData(
                connectionTypes: ['Wi-Fi'],
                isOnline: true,
                onlineHistory: [true, true, false, true],
              ),
            ),
          ),
          networkInfoProvider.overrideWith(
            (ref) async => const NetworkInfoData(
              wifiName: 'Office Network',
              ipAddress: '192.168.1.2',
              gatewayIp: '192.168.1.1',
              subnetMask: '255.255.255.0',
            ),
          ),
          sensorSnapshotProvider.overrideWith(
            (ref) => Stream.value(
              const SensorSnapshot(
                accelerometer: SensorAxisData(x: 0.1, y: 0.2, z: 0.3),
                gyroscope: SensorAxisData(x: 1.1, y: 1.2, z: 1.3),
                magnetometer: SensorAxisData(x: 2.1, y: 2.2, z: 2.3),
                accelerometerMagnitudeHistory: [0.4, 0.5, 0.6],
                availabilityMessages: [],
              ),
            ),
          ),
        ],
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('App Info'), findsOneWidget);
    expect(find.text('Device Info'), findsOneWidget);

    // Battery card may be below the fold; scroll to it.
    await tester.scrollUntilVisible(
      find.text('Battery'),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('Battery'), findsOneWidget);

    // Connectivity card is immediately below Battery and may still be
    // partially outside the viewport after scrolling to Battery.
    await tester.scrollUntilVisible(
      find.text('Connectivity'),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('Connectivity'), findsOneWidget);
    expect(find.text('Network Info'), findsOneWidget);
    expect(find.text('Sensors'), findsOneWidget);
  });

  testWidgets('back button navigates to debug center', (tester) async {
    await tester.pumpWidget(
      _buildApp(
        overrides: [
          appInfoProvider.overrideWith(
            (ref) async => const AppInfoData(
              appName: 'Ego Hygiene',
              packageName: 'io.egohygiene.app',
              version: '1.0.0',
              buildNumber: '42',
              buildMode: 'debug',
            ),
          ),
          deviceInfoProvider.overrideWith(
            (ref) async => const DeviceInfoData(
              platform: 'android',
              osVersion: '14',
              model: 'Pixel',
              manufacturer: 'Google',
              deviceType: 'Mobile',
              isPhysicalDevice: true,
            ),
          ),
          batteryStreamProvider.overrideWith(
            (ref) => Stream.value(
              const BatteryInfoData(
                level: 88,
                state: 'Charging',
                levelHistory: [88],
              ),
            ),
          ),
          connectivityStreamProvider.overrideWith(
            (ref) => Stream.value(
              const ConnectivityInfoData(
                connectionTypes: ['Wi-Fi'],
                isOnline: true,
                onlineHistory: [true],
              ),
            ),
          ),
          networkInfoProvider.overrideWith(
            (ref) async => const NetworkInfoData(),
          ),
          sensorSnapshotProvider.overrideWith(
            (ref) => Stream.value(
              const SensorSnapshot(
                accelerometer: null,
                gyroscope: null,
                magnetometer: null,
                accelerometerMagnitudeHistory: [],
                availabilityMessages: [],
              ),
            ),
          ),
        ],
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(LineChart), findsNothing);
    await tester.tap(find.byIcon(Icons.arrow_back));
    await tester.pumpAndSettle();

    expect(find.text('Debug Center'), findsOneWidget);
  });
}
