import 'package:egohygiene/app/authentication/domain/authentication_provider.dart';
import 'package:egohygiene/app/authentication/domain/authentication_session.dart';
import 'package:egohygiene/app/authentication/domain/authentication_state.dart';
import 'package:egohygiene/app/authentication/domain/user_role.dart';
import 'package:egohygiene/app/authentication/providers/authentication_manager.dart';
import 'package:egohygiene/app/authentication/providers/session_manager.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../../helpers/fake_storage_service.dart';

class _FakeAuthenticationProvider implements AuthenticationProvider {
  _FakeAuthenticationProvider({
    required this.session,
  }) : role = UserRole.individual;

  final AuthenticationSession session;
  final UserRole role;

  int authenticateCalls = 0;
  int resolveRoleCalls = 0;

  @override
  String get id => session.providerId;

  @override
  Future<AuthenticationSession> authenticate() async {
    authenticateCalls += 1;
    return session;
  }

  @override
  Future<UserRole> resolveRole(AuthenticationSession session) async {
    resolveRoleCalls += 1;
    return role;
  }
}

void main() {
  group('AuthenticationManager', () {
    test('restores a saved session without reauthenticating', () async {
      final storage = FakeStorageService();
      final savedSession = AuthenticationSession(
        userId: 'saved-user',
        providerId: 'demo',
        authenticatedAt: DateTime(2026),
        displayName: 'Saved User',
        role: UserRole.therapist,
      );
      final provider = _FakeAuthenticationProvider(
        session: AuthenticationSession(
          userId: 'new-user',
          providerId: 'demo',
          authenticatedAt: DateTime(2026, 1, 2),
        ),
      );

      await SessionManager(storage: storage).save(savedSession);

      final container = ProviderContainer(
        overrides: [
          authenticationStorageServiceProvider.overrideWithValue(storage),
          authenticationProviderProvider.overrideWithValue(provider),
        ],
      );
      addTearDown(container.dispose);

      await container.read(authenticationManagerProvider.notifier).initialize();

      final state = container.read(authenticationManagerProvider);
      expect(state.status, AuthenticationStatus.ready);
      expect(state.session?.userId, savedSession.userId);
      expect(state.session?.role, UserRole.therapist);
      expect(provider.authenticateCalls, 0);
      expect(provider.resolveRoleCalls, 0);
    });

    test('authenticates, resolves the role, and persists the session', () async {
      final storage = FakeStorageService();
      final provider = _FakeAuthenticationProvider(
        session: AuthenticationSession(
          userId: 'demo-user',
          providerId: 'demo',
          authenticatedAt: DateTime(2026),
          displayName: 'Demo User',
        ),
      );

      final container = ProviderContainer(
        overrides: [
          authenticationStorageServiceProvider.overrideWithValue(storage),
          authenticationProviderProvider.overrideWithValue(provider),
        ],
      );
      addTearDown(container.dispose);

      await container.read(authenticationManagerProvider.notifier).initialize();

      final state = container.read(authenticationManagerProvider);
      final restored = await SessionManager(storage: storage).restore();

      expect(state.status, AuthenticationStatus.ready);
      expect(state.session?.displayName, 'Demo User');
      expect(state.session?.role, UserRole.individual);
      expect(provider.authenticateCalls, 1);
      expect(provider.resolveRoleCalls, 1);
      expect(restored?.userId, 'demo-user');
      expect(restored?.role, UserRole.individual);
    });
  });
}
