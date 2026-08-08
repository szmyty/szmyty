import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:flutter_test/flutter_test.dart';

/// Validates that the generated localization is internally consistent and
/// that every string key can be resolved without errors.
///
/// This test is intentionally lightweight — it exercises the generated
/// [Translations] object to catch any mismatch between the JSON source
/// file and the generated Dart code early, before the strings are exercised
/// in widget or integration tests.
void main() {
  late Translations t;

  setUpAll(() {
    LocaleSettings.setLocaleRaw('en');
    t = AppLocale.en.buildSync();
  });

  group('Localization key completeness', () {
    test('root-level labels resolve', () {
      expect(t.appName, isNotEmpty);
      expect(t.home, isNotEmpty);
      expect(t.reflection, isNotEmpty);
      expect(t.memory, isNotEmpty);
      expect(t.progress, isNotEmpty);
      expect(t.settings, isNotEmpty);
      expect(t.conversation, isNotEmpty);
      expect(t.personalModel, isNotEmpty);
      expect(t.welcome, isNotEmpty);
      expect(t.welcomeDescription, isNotEmpty);
    });

    test('common keys resolve', () {
      expect(t.common.cancel, isNotEmpty);
      expect(t.common.save, isNotEmpty);
      expect(t.common.delete, isNotEmpty);
      expect(t.common.edit, isNotEmpty);
      expect(t.common.done, isNotEmpty);
      expect(t.common.back, isNotEmpty);
      expect(t.common.next, isNotEmpty);
      expect(t.common.retry, isNotEmpty);
      expect(t.common.loading, isNotEmpty);
      expect(t.common.error, isNotEmpty);
      expect(t.common.openSettings, isNotEmpty);
    });

    test('navigation keys resolve', () {
      expect(t.navigation.goToHome, isNotEmpty);
      expect(t.navigation.goToReflection, isNotEmpty);
      expect(t.navigation.goToMemory, isNotEmpty);
      expect(t.navigation.goToProgress, isNotEmpty);
      expect(t.navigation.goToSettings, isNotEmpty);
      expect(t.navigation.goToConversation, isNotEmpty);
    });

    test('error keys resolve', () {
      expect(t.errors.loadFailed(item: 'data'), isNotEmpty);
      expect(t.errors.loadFailedGeneral, isNotEmpty);
      expect(t.errors.noConnection, isNotEmpty);
    });

    test('settings screen keys resolve', () {
      expect(t.settingsScreen.title, isNotEmpty);
      expect(t.settingsScreen.updates.title, isNotEmpty);
      expect(t.settingsScreen.updates.subtitle, isNotEmpty);
      expect(t.settingsScreen.theme.light, isNotEmpty);
      expect(t.settingsScreen.theme.dark, isNotEmpty);
      expect(t.settingsScreen.theme.amoled, isNotEmpty);
      expect(t.settingsScreen.theme.highContrast, isNotEmpty);
    });

    test('update experience screen keys resolve', () {
      expect(t.updateExperienceScreen.title, isNotEmpty);
      expect(t.updateExperienceScreen.checkingLabel, isNotEmpty);
      expect(t.updateExperienceScreen.readyLabel, isNotEmpty);
      expect(t.updateExperienceScreen.unavailableTitle, isNotEmpty);
      expect(t.updateExperienceScreen.unavailableMessage, isNotEmpty);
      expect(t.updateExperienceScreen.requiredUpdateDialogTitle, isNotEmpty);
      expect(t.updateExperienceScreen.updateAvailableDialogTitle, isNotEmpty);
      expect(t.updateExperienceScreen.laterButton, isNotEmpty);
      expect(t.updateExperienceScreen.whatsNewButton, isNotEmpty);
      expect(t.updateExperienceScreen.installButton, isNotEmpty);
      expect(t.updateExperienceScreen.noReleaseNotes, isNotEmpty);
      expect(t.updateExperienceScreen.migrationNotesTitle, isNotEmpty);
    });

    test('update experience interpolated keys resolve', () {
      expect(
        t.updateExperienceScreen.estimatedTimeLabel(duration: '2 minutes'),
        contains('2 minutes'),
      );
      expect(
        t.updateExperienceScreen.releaseNotesTitle(version: '1.0.0'),
        contains('1.0.0'),
      );
    });

    test('update section widget keys resolve', () {
      expect(t.updateSectionWidgets.viewFullReleaseNotesLabel, isNotEmpty);
      expect(t.updateSectionWidgets.checkAgainLabel, isNotEmpty);
      expect(t.updateSectionWidgets.openReleaseNotesViewerLabel, isNotEmpty);
    });

    test('debug center screen keys resolve', () {
      expect(t.debugCenterScreen.title, isNotEmpty);
      expect(t.debugCenterScreen.systemInfo.title, isNotEmpty);
      expect(t.debugCenterScreen.systemInfo.dashboardTitle, isNotEmpty);
      expect(t.debugCenterScreen.systemInfo.unavailable, isNotEmpty);
    });

    test('onboarding screen keys resolve', () {
      expect(t.onboardingScreen.skip, isNotEmpty);
      expect(t.onboardingScreen.continueButton, isNotEmpty);
      expect(t.onboardingScreen.page1.title, isNotEmpty);
    });

    test('home screen keys resolve', () {
      expect(t.homeScreen.todaysReflection.title, isNotEmpty);
      expect(t.homeScreen.tagline, isNotEmpty);
    });

    test('reflection screen keys resolve', () {
      expect(t.reflectionScreen.title, isNotEmpty);
    });

    test('check-in screen keys resolve', () {
      expect(t.checkInScreen.title, isNotEmpty);
    });
  });
}
