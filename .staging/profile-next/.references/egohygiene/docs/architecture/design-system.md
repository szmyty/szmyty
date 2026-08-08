# Design System

This document describes the design system used in Ego Hygiene, including colors, spacing, typography, and the accessibility foundation.

---

## Colors

Defined in `lib/shared/theme/colors.dart`:
- Primary: Indigo (#6366F1)
- Secondary: Purple (#8B5CF6)
- Semantic colors: Success, Warning, Error, Info
- Full neutral palette (50-900)

## Spacing

8-point grid system in `lib/shared/theme/spacing.dart`:
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px
- xxl: 32px
- xxxl: 48px
- huge: 64px

## Typography

Defined in `lib/shared/theme/typography.dart`:
- UI Text: Inter
- Display Text: Crimson Pro
- Full Material Design 3 type scale

## Design Token System

Design tokens live in `lib/shared/theme/` and are exported via `theme_tokens.dart`:

| Token | File | Description |
|---|---|---|
| `AppColors` | `colors.dart` | Color palette |
| `AppSpacing` | `spacing.dart` | 8-point spacing scale |
| `AppRadius` | (radius.dart) | Border radius values |
| `AppElevation` | `elevation.dart` | Elevation scale |
| `AppShadows` | `shadows.dart` | Shadow definitions |
| `AppDurations` | `motion.dart` | Animation durations |
| `AppCurves` | `motion.dart` | Animation curves |
| `AppOpacity` | `opacity.dart` | Opacity scale |

Import all tokens via the barrel:

```dart
import 'package:egohygiene/shared/theme/theme_tokens.dart';
```

Always use design tokens instead of hardcoded values.

## Accessibility Foundation

Shared accessibility behavior is centralized instead of being reimplemented per
screen:

- `lib/shared/theme/accessibility.dart` applies reduced-motion-aware page
  transitions, padded touch targets, and minimum interactive sizes through the
  app theme.
- `lib/shared/widgets/app_section_card.dart` provides reusable section cards
  with semantic heading structure for feature screens.
- App-wide focus traversal is established at the `MaterialApp` boundary so
  keyboard navigation follows reading order by default.

### Semantic annotations

| Widget | Behavior |
|---|---|
| `AppEmptyState` | Title exposed as a semantic heading (`Semantics(header: true)`). |
| `AppSectionHeader` | Title exposed as a semantic heading. |
| `AppMessageBubble` | Announces `"$speaker: $message"` as a single label. |
| `AppStatCard` | Merges value and label into one announcement (e.g., `"4/5 Mood"`). |
| `AppLoadingIndicator` | Accepts an optional `semanticLabel` for context-specific announcements. |
| `AppInputBar` | Send icon carries `semanticLabel: 'Send'`; loading state carries `semanticLabel: 'Sending…'`. |
| `AppTimelineTile` | Decorative chevron icon is excluded from the semantics tree. |
| `ProgressBarChart` | Each bar carries a `semanticLabel` describing its value. |

### Reduced motion

`AppAccessibility.disableAnimationsOf(context)` returns `true` when
`MediaQuery.disableAnimations` or `MediaQuery.accessibleNavigation` is set.
Use this gate before starting non-essential animations:

```dart
if (!AppAccessibility.disableAnimationsOf(context)) {
  _controller.forward();
}
```

Page transitions are automatically suppressed for all platforms via
`ReducedMotionPageTransitionsBuilder`.  The Lottie splash screen falls back to a
static icon when reduced motion is requested.

### Touch targets

All interactive controls receive `MaterialTapTargetSize.padded` and a minimum
size of 48×48 dp through `applyAppAccessibility`.  The `AppAccessibility.minTouchTargetSize`
constant (48) is the authoritative reference for any custom interactive widget.
