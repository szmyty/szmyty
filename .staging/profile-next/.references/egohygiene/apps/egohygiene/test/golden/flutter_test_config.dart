import 'dart:async';

import 'package:golden_toolkit/golden_toolkit.dart';

/// Configures deterministic rendering for all golden tests in this directory.
///
/// This file is automatically discovered by Flutter's test runner for any
/// test file in the same directory or a sub-directory. It loads bundled app
/// fonts so golden reference images are stable across machines and CI.
Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  return GoldenToolkit.runWithConfiguration(
    () async {
      await loadAppFonts();
      await testMain();
    },
    config: GoldenToolkitConfiguration(
      defaultDevices: const [Device.phone, Device.tabletPortrait],
      enableRealShadows: true,
      fileNameFactory: (name) => '../goldens/$name.png',
    ),
  );
}
