import 'package:egohygiene/app/authentication/domain/authentication_session.dart';
import 'package:egohygiene/app/authentication/domain/authentication_state.dart';
import 'package:egohygiene/features/onboarding/feature.dart';
import 'package:egohygiene/shared/routing/app_router.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  final readyState = AuthenticationState.ready(
    AuthenticationSession(
      userId: 'user-1',
      providerId: 'demo',
      authenticatedAt: DateTime(2026),
    ),
  );

  group('AppRouter auth redirect', () {
    test('redirects unauthenticated users away from feature routes', () {
      final redirect = AppRouter.authRedirectForLocation(
        authenticationState: const AuthenticationState.idle(),
        location: '/reflection',
      );

      expect(redirect, AppRouter.startupPath);
    });

    test('keeps restoring/authenticating users on startup flow', () {
      final restoringRedirect = AppRouter.authRedirectForLocation(
        authenticationState: const AuthenticationState(
          status: AuthenticationStatus.restoringSession,
        ),
        location: '/startup',
      );
      final authenticatingRedirect = AppRouter.authRedirectForLocation(
        authenticationState: const AuthenticationState(
          status: AuthenticationStatus.authenticating,
        ),
        location: '/progress',
      );

      expect(restoringRedirect, isNull);
      expect(authenticatingRedirect, AppRouter.startupPath);
    });

    test('allows ready users into app shell and off startup (onboarding completed)', () {
      final startupRedirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        location: AppRouter.startupPath,
      );
      final featureRedirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        location: '/memory',
      );

      expect(startupRedirect, AppRouter.homePath);
      expect(featureRedirect, isNull);
    });

    test('allows ready users to access debug center routes', () {
      final debugRedirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        location: '/settings/debug',
      );
      final logsRedirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        location: '/settings/debug/logs',
      );
      final systemInfoRedirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        location: '/settings/debug/system',
      );

      expect(debugRedirect, isNull);
      expect(logsRedirect, isNull);
      expect(systemInfoRedirect, isNull);
    });
  });

  group('AppRouter onboarding redirect', () {
    test('redirects to onboarding from startup when onboarding is required', () {
      final redirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        onboardingStatus: OnboardingStatus.required,
        location: AppRouter.startupPath,
      );

      expect(redirect, AppRouter.onboardingPath);
    });

    test('allows onboarding route when onboarding is required', () {
      final redirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        onboardingStatus: OnboardingStatus.required,
        location: AppRouter.onboardingPath,
      );

      expect(redirect, isNull);
    });

    test('blocks app shell routes until onboarding is completed', () {
      final homeRedirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        onboardingStatus: OnboardingStatus.required,
        location: '/',
      );
      final reflectionRedirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        onboardingStatus: OnboardingStatus.required,
        location: '/reflection',
      );

      expect(homeRedirect, AppRouter.onboardingPath);
      expect(reflectionRedirect, AppRouter.onboardingPath);
    });

    test('allows all routes once onboarding is completed', () {
      final homeRedirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        location: '/',
      );
      final reflectionRedirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        location: '/reflection',
      );

      expect(homeRedirect, isNull);
      expect(reflectionRedirect, isNull);
    });

    test('unknown onboarding status does not block app shell routes', () {
      final redirect = AppRouter.authRedirectForLocation(
        authenticationState: readyState,
        onboardingStatus: OnboardingStatus.unknown,
        location: '/',
      );

      expect(redirect, isNull);
    });
  });
}
