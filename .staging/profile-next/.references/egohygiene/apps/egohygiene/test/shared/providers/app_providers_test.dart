import 'package:egohygiene/app/authentication/domain/authentication_provider.dart';
import 'package:egohygiene/app/authentication/domain/authentication_state.dart';
import 'package:egohygiene/app/authentication/providers/authentication_manager.dart';
import 'package:egohygiene/app/startup/domain/startup_state.dart';
import 'package:egohygiene/app/startup/providers/startup_manager.dart';
import 'package:egohygiene/shared/localization/strings.g.dart';
import 'package:egohygiene/shared/providers/app_providers.dart';
import 'package:egohygiene/shared/providers/locale_provider.dart';
import 'package:egohygiene/shared/providers/theme_providers.dart';
import 'package:egohygiene/shared/theme/theme_preferences.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

void main() {
  test('app provider barrel exports core application providers', () {
    expect(
      authenticationManagerProvider,
      isA<NotifierProvider<AuthenticationManager, AuthenticationState>>(),
    );
    expect(
      authenticationProviderProvider,
      isA<Provider<AuthenticationProvider>>(),
    );
    expect(
      startupManagerProvider,
      isA<NotifierProvider<StartupManager, StartupState>>(),
    );
    expect(
      appLocaleProvider,
      isA<NotifierProvider<AppLocaleNotifier, AppLocale>>(),
    );
    expect(appRouterProvider, isA<Provider<GoRouter>>());
    expect(
      themePreferencesNotifierProvider,
      isA<NotifierProvider<ThemePreferencesNotifier, ThemePreferences>>(),
    );
  });
}
