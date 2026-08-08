# Startup

Startup covers two complementary engines: **Environment Management** and **Feature Flags**. Both must be initialized once during app startup before any feature code runs.

---

## Environment Management Foundation

The Environment Management Foundation provides a centralized, pluggable system for determining how the application behaves in each deployment context. All environment-specific branching — logging verbosity, analytics, crash reporting, AI provider selection, feature flag sources, sync behaviour, and debug tooling — flows through `EnvironmentManager` rather than being scattered across feature code.

### Directory layout

```
lib/shared/environment/
  environment_engine.dart           — barrel export
  environment.dart                  — AppEnvironment enum
  environment_configuration.dart    — immutable configuration bundle
  environment_provider.dart         — abstract EnvironmentProvider interface
  environment_manager.dart          — central orchestrator
  impl/
    local_environment_provider.dart — default static implementation

lib/shared/providers/
  environment_providers.dart        — Riverpod providers
```

### `AppEnvironment`

| Value | Description |
|---|---|
| `development` | Local development — verbose logging and debug tooling active |
| `staging` | Pre-production — crash reporting active; mirrors production config |
| `production` | Live user traffic — analytics and crash reporting fully enabled |
| `testing` | Automated test suites — all side-effects mocked or disabled |
| `demo` | Walkthroughs / previews — no real data, sync, or API keys needed |

### `EnvironmentConfiguration`

Immutable bundle describing every environment-specific value.

| Field | Type | Description |
|---|---|---|
| `environment` | `AppEnvironment` | The deployment context this config describes |
| `isLoggingEnabled` | `bool` | Whether log output is emitted |
| `isAnalyticsEnabled` | `bool` | Whether analytics events are forwarded |
| `isCrashReportingEnabled` | `bool` | Whether crash / error reports are sent |
| `isDebuggingEnabled` | `bool` | Whether developer tooling is exposed |
| `isSyncEnabled` | `bool` | Whether background sync operations run |
| `isAiEnabled` | `bool` | Whether AI features are active |
| `useMockAiProvider` | `bool` | Whether to use a mock AI provider |
| `useRemoteFeatureFlags` | `bool` | Whether flags are sourced from a remote config |
| `metadata` | `Map<String, Object?>` | Arbitrary extension values |

Default baselines per environment:

| Environment | log | analytics | crash | debug | sync | ai | mock ai | remote flags |
|-------------|-----|-----------|-------|-------|------|----|---------|--------------|
| development | ✓   |           |       | ✓     | ✓    | ✓  |         |              |
| staging     | ✓   |           | ✓     |       | ✓    | ✓  |         | ✓            |
| production  |     | ✓         | ✓     |       | ✓    | ✓  |         | ✓            |
| testing     |     |           |       | ✓     |      |    | ✓       |              |
| demo        |     |           |       |       |      | ✓  | ✓       |              |

Use `EnvironmentConfiguration.defaults(environment)` for the recommended baseline, and `copyWith` for targeted customization:

```dart
final config = EnvironmentConfiguration.defaults(AppEnvironment.staging)
    .copyWith(isAnalyticsEnabled: true);
```

### `EnvironmentProvider`

Abstract interface for configuration backends.

- `initialize()` — one-time startup; fetch initial payload where needed
- `loadConfiguration()` — returns the active `EnvironmentConfiguration`; must not throw (degrade to defaults on failure)
- `dispose()` — resource cleanup

### `LocalEnvironmentProvider`

Default implementation. Returns a static `EnvironmentConfiguration` with no network dependency.

```dart
// Development defaults
const provider = LocalEnvironmentProvider();

// Specific environment
const provider = LocalEnvironmentProvider(
  environment: AppEnvironment.production,
);

// Fully custom (useful in test harnesses)
final provider = LocalEnvironmentProvider(
  configuration: EnvironmentConfiguration.defaults(AppEnvironment.testing)
      .copyWith(isSyncEnabled: false),
);
```

### `EnvironmentManager`

The single entry point that feature modules, engines, and services use to inspect the current deployment context.

- `initialize()` — must be called once on startup; no-op thereafter
- `configuration` — resolved `EnvironmentConfiguration`; falls back to development defaults if called before `initialize()`
- `environment` — active `AppEnvironment`
- `isDevelopment` / `isStaging` / `isProduction` / `isTesting` / `isDemo` — convenience guards

```dart
final env = ref.read(environmentManagerProvider);

if (env.configuration.isLoggingEnabled) {
  logger.verbose('request started');
}

if (env.configuration.isAiEnabled) {
  final aiProvider = env.configuration.useMockAiProvider
      ? mockProvider
      : realProvider;
}
```

### Riverpod Providers

| Provider | Type | Purpose |
|---|---|---|
| `environmentProviderProvider` | `EnvironmentProvider` | Active configuration backend |
| `environmentManagerProvider` | `EnvironmentManager` | App-wide orchestrator |

### Barrel export

```dart
import 'package:egohygiene/shared/environment/environment_engine.dart';
```

### Future compatibility

- **Remote configuration** — swap `environmentProviderProvider` for a network-backed adapter (Firebase Remote Config, custom control plane).
- **App flavors** — a `FlavorEnvironmentProvider` reads `AppEnvironment` from `String.fromEnvironment` build-time constants.
- **White-label applications** — institution-specific values pass via `EnvironmentConfiguration.metadata`.
- **Feature flag integration** — `useRemoteFeatureFlags` signals the Feature Flag Engine to switch to a remote adapter.

---

## Feature Flag Engine

The Feature Flag Engine provides a centralized, overrideable capability gate for all application features. Feature modules check flag availability through `FeatureFlagManager` rather than hardcoding environment conditions, enabling experimental, beta, developer-only, and environment-specific capabilities without architectural changes.

### Directory layout

```
lib/shared/flags/
  feature_flag_engine.dart           — barrel export
  feature_flag.dart                  — FeatureFlag + FeatureFlagType
  feature_flag_state.dart            — FeatureFlagState enum
  feature_flag_override.dart         — FeatureFlagOverride (developer / test)
  feature_flag_provider.dart         — abstract FeatureFlagProvider interface
  feature_flag_manager.dart          — central orchestrator
  impl/
    local_feature_flag_provider.dart — default local/static implementation

lib/shared/providers/
  feature_flag_providers.dart        — Riverpod providers
```

### Evaluation priority

```
Priority (highest → lowest):
  1. Developer override    — setOverride() / clearOverride()
  2. Provider value        — FeatureFlagProvider.getValue()
  3. Flag default value    — FeatureFlag.defaultValue
```

### `FeatureFlagType`

| Value | Meaning |
|---|---|
| `stable` | Production-ready; enabled for all users |
| `experimental` | May change or be removed; disabled by default |
| `beta` | Limited audience / staged rollout; disabled by default |
| `developerOnly` | Engineering use only; must not be enabled in production |
| `hidden` | Internal plumbing; not surfaced in UI or docs |
| `deprecated` | Scheduled for removal; kept for backward compatibility |

### `FeatureFlag`

```dart
const kAiInsightsFlag = FeatureFlag(
  key: 'ai_insights',
  type: FeatureFlagType.experimental,
  defaultValue: false,
  description: 'AI-generated insight summaries on the home screen.',
);
```

Key fields: `key` (stable snake_case identifier), `type`, `defaultValue` (defaults to `false`), `description`.

### `FeatureFlagState`

| Value | Meaning |
|---|---|
| `enabled` | Feature is active |
| `disabled` | Feature is inactive |
| `overridden` | State was forced by a developer override |

### `FeatureFlagOverride`

Forces a flag on or off for a session — intended for development and automated tests.

```dart
manager.setOverride(
  FeatureFlagOverride(key: 'ai_insights', value: true, reason: 'local dev'),
);
```

### `LocalFeatureFlagProvider`

Default implementation. Evaluates flags against their `FeatureFlag.defaultValue` with no network dependency. Accepts an optional `staticValues` map to pin specific flags in test harnesses.

```dart
const prov = LocalFeatureFlagProvider(
  staticValues: {'ai_insights': true},
);
```

### `FeatureFlagManager`

The single entry point for feature modules.

- `initialize()` — must be called once on startup; no-op thereafter
- `isEnabled(flag)` — returns `bool` applying the three-layer priority
- `evaluate(flag)` — returns `FeatureFlagState` (includes override signal)
- `setOverride(override)` — force a flag on or off for this session
- `clearOverride(key)` — revert a single flag to provider / default
- `clearAllOverrides()` — revert all flags
- `overrideFor(key)` — inspect the active override for a flag
- `overrides` — unmodifiable view of all active overrides

### Riverpod Providers

| Provider | Type | Purpose |
|---|---|---|
| `featureFlagProviderProvider` | `FeatureFlagProvider` | Active evaluation backend |
| `featureFlagManagerProvider` | `FeatureFlagManager` | Feature-facing orchestrator |

### Barrel export

```dart
import 'package:egohygiene/shared/flags/feature_flag_engine.dart';
```

### Future compatibility

- **Remote configuration** — swap `featureFlagProviderProvider` for a network-backed adapter (Firebase Remote Config, LaunchDarkly, PostHog).
- **A/B testing** — providers return variant values via `getValue`; no manager changes needed.
- **Staged releases** — percentage-based rollouts expressed in the provider layer.
- **Institutional feature sets** — per-organization flag profiles via provider overrides.
