# Routing

Navigation is handled by [GoRouter](https://pub.dev/packages/go_router) configured in `apps/egohygiene/lib/shared/routing/app_router.dart`.

## Route table

| Path | Name | Shell? | Description |
|---|---|---|---|
| `/startup` | `startup` | No | Startup screen — holds until auth is ready |
| `/onboarding` | `onboarding` | No | Onboarding flow — required before accessing the shell |
| `/check-in` | `check-in` | No | Check-in entry screen |
| `/check-in/history` | `check-in-history` | No | Check-in history screen |
| `/settings` | `settings` | No | Settings screen |
| `/graph` | `graph` | No | Knowledge Graph visualization |
| `/personal-model` | `personal-model` | No | Personal Model experience |
| `/` | `home` | Yes — Branch 0 | Home screen |
| `/reflection` | `reflection` | Yes — Branch 1 | Reflection list |
| `/reflection/new` | `reflection-create` | Yes — Branch 1 | New reflection form |
| `/reflection/:id` | `reflection-detail` | Yes — Branch 1 | Reflection detail |
| `/conversation` | `conversation` | Yes — Branch 2 | AI conversation screen |
| `/progress` | `progress` | Yes — Branch 3 | Progress / goal tracking screen |
| `/memory` | `memory` | Yes — Branch 4 | Memory screen |

## Navigation shell

The five primary destinations (Home, Reflection, Conversation, Progress, Memory) are wrapped in a `StatefulShellRoute.indexedStack` that renders `AppNavigationShell` as a persistent bottom navigation bar. Per-branch navigation state (scroll position, nested routes) is preserved when switching tabs.

Routes outside the shell (Startup, Onboarding, Check-In, Settings, Graph, Personal Model) are declared as top-level `GoRoute` entries and render without the bottom bar.

## Navigation patterns

```dart
// Push a new route onto the current branch stack
context.push('/reflection/new');

// Pop back
context.pop();

// Replace the current location (no back-stack entry)
context.go('/');
```

## Auth and onboarding redirect

`AppRouter.authRedirectForLocation` is a pure, testable function that enforces the startup lifecycle:

1. If auth is **not ready**, redirect every location to `/startup`.
2. Once auth is ready and the user is on `/startup`:
   - If onboarding is `required`, redirect to `/onboarding`.
   - Otherwise, redirect to `/` (home).
3. If onboarding is `required` and the user navigates to any non-onboarding route, redirect back to `/onboarding`.

```dart
GoRouter(
  initialLocation: AppRouter.startupPath,
  redirect: (context, state) => AppRouter.authRedirectForLocation(
    authenticationState: authenticationState,
    onboardingStatus: onboardingStatus,
    location: state.matchedLocation,
  ),
  ...
)
```

## Router instantiation

```dart
// Default singleton (development / production)
final router = AppRouter.router;

// Custom instance (e.g., tests with injected auth state)
final router = AppRouter.createRouter(
  authenticationState: const AuthenticationState.authenticated(),
  onboardingStatus: OnboardingStatus.completed,
  observers: [myObserver],
);
```
