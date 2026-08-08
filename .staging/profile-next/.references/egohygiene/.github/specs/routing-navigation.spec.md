# Routing & Navigation

## Metadata

- **Spec ID:** `routing-navigation`
- **File Name:** `routing-navigation.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #9
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-21

---

# 1. Purpose

Define the navigation architecture and route structure for Ego Hygiene.

This specification establishes how routes are defined, organized, and navigated throughout the application. It ensures that navigation is declarative, type-safe, deep-linkable, and consistent across platforms.

---

# 2. Goals

- Define the canonical route structure.
- Establish type-safe route generation conventions.
- Define navigation patterns (push, replace, go, pop).
- Define route guards and conditional navigation.
- Support deep linking from launch.
- Support future web compatibility.

---

# 3. Non-Goals

- This spec does not define individual screen implementations.
- This spec does not define bottom navigation bar design (see `design-system.spec.md`).
- This spec does not define authentication flows (future concern).
- This spec does not define notification tap routing logic in detail.

---

# 4. Context

The application already uses `go_router` for navigation, defined in `lib/shared/routing/app_router.dart`.

Current routes (as documented in `ARCHITECTURE.md`):

```
/ (home)
/reflection
/memory
/progress
/settings
```

As features grow (domains, practices, insights, reflection, settings), the route tree must expand in a structured, maintainable way. This spec defines that structure before feature development accelerates.

---

# 5. Requirements

## 5.1 Functional Requirements

- The application must support declarative routing via `go_router`.
- All routes must be defined in a single authoritative router configuration.
- Routes must support path parameters for entity detail views.
- Routes must support deep linking via URI-based navigation.
- Navigation must support push, pop, replace, and go operations.
- The application must handle unknown routes with a 404 screen.
- Navigation must support nested shell routes for persistent bottom navigation.
- Route guards must support redirect logic for future authentication.

## 5.2 Non-Functional Requirements

- Routes must be defined as typed constants to avoid string literal errors.
- Route generation via `go_router_builder` is preferred for type safety.
- Navigation must not cause unnecessary widget rebuilds.
- Router configuration must be testable.
- Navigation state must survive application lifecycle events where possible.

---

# 6. Architecture

## 6.1 Canonical Route Tree

```
/                          — Shell (bottom navigation)
  /home                    — Home / Dashboard
  /domains                 — Domain list
    /domains/:domainId     — Domain detail
  /practices               — Practice list
    /practices/:practiceId — Practice detail
    /practices/:practiceId/session  — Active practice session
  /insights                — Insight list
    /insights/new          — Create insight
    /insights/:insightId   — Insight detail
/settings                  — Settings (full-screen, outside shell)
/onboarding                — Onboarding flow (future)
/404                       — Not found
```

## 6.2 Router Configuration Structure

```
lib/shared/routing/
  app_router.dart         — GoRouter configuration
  app_router.g.dart       — Generated (go_router_builder)
  routes.dart             — Route path constants
  shell_scaffold.dart     — Shell scaffold with bottom navigation
```

### Route Constants (`routes.dart`)

```
class Routes {
  static const home = '/home';
  static const domains = '/domains';
  static const domainDetail = '/domains/:domainId';
  static const practices = '/practices';
  static const practiceDetail = '/practices/:practiceId';
  static const practiceSession = '/practices/:practiceId/session';
  static const insights = '/insights';
  static const insightNew = '/insights/new';
  static const insightDetail = '/insights/:insightId';
  static const settings = '/settings';
}
```

## 6.3 Shell Route (Persistent Navigation)

The main application uses a `ShellRoute` to maintain a persistent bottom navigation bar across the core sections:

```
ShellScaffold
  BottomNavigationBar
    Home
    Domains
    Practices
    Insights
```

Settings is accessed from Home or a dedicated button and navigates outside the shell.

## 6.4 Navigation Patterns

```dart
// Navigate to a route (replace stack)
context.go(Routes.home);

// Push onto stack (back button returns)
context.push(Routes.insightNew);

// Navigate with parameters
context.go('/domains/$domainId');

// Pop back
context.pop();
```

## 6.5 Route Guards

Route guards are implemented using GoRouter's `redirect` callback.

```
redirect (builder)
  ↓
Check guard conditions
  (e.g., isAuthenticated — future)
  ↓
Return null (allow) or redirectPath (block + redirect)
```

Guard conditions are evaluated via Riverpod providers passed into the router configuration.

## 6.6 Deep Linking

Deep link format:

```
egohygiene://domains/physical-health
egohygiene://practices/gratitude
egohygiene://insights/abc123
```

Web URL format:

```
https://app.egohygiene.com/domains/physical-health
```

Platform-specific deep link configuration:

- Android: `AndroidManifest.xml` intent filters
- iOS: `Info.plist` URL schemes and Associated Domains
- Web: standard URL routing via `go_router`

## 6.7 Dependencies

- `go_router` — declarative routing
- `go_router_builder` — type-safe route generation (optional, add when route count grows)
- `flutter_riverpod` — router dependency injection

---

# 7. Implementation Plan

## Phase 1 — Route Audit and Constants

- [ ] Audit current `app_router.dart` against the canonical route tree above.
- [ ] Create `routes.dart` with typed route path constants.
- [ ] Add missing routes for domains, practices, and insights.
- [ ] Implement the 404 not-found screen.

## Phase 2 — Shell Route

- [ ] Implement `ShellScaffold` with persistent bottom navigation.
- [ ] Connect Home, Domains, Practices, and Insights tabs.
- [ ] Verify shell route preserves tab state during navigation.

## Phase 3 — Deep Linking

- [ ] Configure Android deep link intent filters.
- [ ] Configure iOS URL schemes.
- [ ] Validate deep link routing manually.

## Phase 4 — Route Guards

- [ ] Implement redirect callback in GoRouter.
- [ ] Define `RouteGuard` interface for future extensibility.
- [ ] Add placeholder authentication guard (passes through until auth is implemented).

## Phase 5 — Validation

- [ ] Write unit tests for router redirect logic.
- [ ] Write widget tests for ShellScaffold tab switching.
- [ ] Manually validate deep links on Android and iOS.
- [ ] Validate back navigation behavior on all tabs.

---

# 8. Validation Plan

- Unit tests for route redirect logic and guard behavior.
- Widget tests for `ShellScaffold` navigation and tab state.
- Manual deep link testing on Android and iOS.
- Manual web URL routing validation.
- CI must pass all tests.

---

# 9. Acceptance Criteria

- [ ] Canonical route tree is fully implemented.
- [ ] All routes are defined as typed constants.
- [ ] Shell route with persistent bottom navigation is working.
- [ ] Deep linking is configured for Android, iOS, and web.
- [ ] Unknown routes display a 404 screen.
- [ ] Route guards are in place and extensible.
- [ ] All route tests pass.
- [ ] Navigation works offline.

---

# 10. Open Questions

- Should `go_router_builder` be adopted for type-safe route generation now or deferred?
- Should the bottom navigation bar show badges for pending insights or practice reminders?
- Should deep links be handled as URI schemes or Universal Links / App Links?
- How should navigation state be preserved when the app is backgrounded and restored?
- Should onboarding be implemented as a separate full-screen flow or a route stack overlay?
