# Ambient hero startup experience

The startup experience now uses `AmbientSplashExperience` from
`apps/egohygiene/lib/app/startup/presentation/lottie_splash_experience.dart`.
It is wired through `splashExperienceProvider`, but the visual runtime is now
driven by the shared `RiveScene` infrastructure in
`apps/egohygiene/lib/shared/animation/rive_scene.dart`. That makes the same
asset-loading, fallback, and theme-propagation path reusable for splash,
onboarding, empty states, and future ambient hero surfaces without changing the
startup screen contract.

## Runtime architecture

- `AnimationRegistry` centrally maps reusable animation surfaces (splash,
  onboarding, empty state, loading state, celebrations, ambient backgrounds,
  and future website placements) to shared Rive scenes.
- `AnimationManager` resolves a registry entry together with the current
  `MotionPolicy` and `AnimationThemeSnapshot`, so animation consumers inherit
  accessibility and theme state without bespoke wiring.
- `ManagedAnimationScene` is the app-facing widget abstraction; it reads the
  shared Riverpod providers and renders the resolved `RiveScene`.
- `RiveSceneAsset` defines the asset path, renderer choice, optional artboard /
  state machine selectors, and view-model binding point for a scene.
- `RiveScene` owns the `FileLoader`, renders loading/failure fallbacks, and
  rebuilds when application theme colors change so future user-selectable
  themes can propagate through the same animation entry point.

## Motion states

- `reduced motion` — renders a static frame with no running ticker and no
  Rive runtime playback.
- `ambient` — runs the reusable Rive scene behind the branded overlay.
- `fallback` — preserves the same branded frame if the animation asset is
  unavailable or fails to decode.

## Accessibility and performance

- Motion automatically respects `MediaQuery.disableAnimations` and
  `MediaQuery.accessibleNavigation` through `MotionManager.of(context)`.
- The animated scene is bounded to a single square panel and keeps the visual
  system lightweight by centralizing asset loading and failure handling in one
  reusable widget.
- When animation is disabled, the same composition remains visible so the app
  still presents a calm branded entry experience.

## Bootstrap asset note

The initial bundled `.riv` file is a temporary bootstrap asset vendored from
the MIT-licensed `rive-app/rive-flutter` example repository so the application
can start using the Rive runtime and shared animation infrastructure
immediately. The surrounding composition, theming, and accessibility behavior
are application-owned, and the bundled asset can be replaced later without
changing the shared runtime integration.
