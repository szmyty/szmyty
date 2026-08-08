# Design System

## Metadata

- **Spec ID:** `design-system`
- **File Name:** `design-system.spec.md`
- **Status:** Draft
- **Owner:** Sanctuary
- **Related Issues:** #9
- **Related ADRs:** N/A
- **Last Updated:** 2026-06-21

---

# 1. Purpose

Define the visual architecture, design tokens, typography, spacing, and theming strategy for Ego Hygiene.

The design system ensures that all application interfaces share a consistent visual language that supports cognition, reduces cognitive load, and communicates the calm intelligence described in `DESIGN.md`.

---

# 2. Goals

- Define the canonical design token set (colors, spacing, radius, typography).
- Define the theming architecture including light mode, dark mode, and future branding overrides.
- Establish typography conventions and font selections.
- Define spacing system and layout grid.
- Establish the component library structure.
- Ensure the design system is usable by AI agents without ambiguity.

---

# 3. Non-Goals

- This spec does not define individual screen layouts.
- This spec does not define animation choreography in detail.
- This spec does not define domain-specific color systems.
- This spec does not replace `DESIGN.md`, which defines design philosophy; this spec defines implementation.

---

# 4. Context

The `DESIGN.md` document defines the philosophy:

> "Interfaces should support cognition. Interfaces should not compete with cognition."

The application should feel: calm, intelligent, intentional, beautiful, trustworthy, alive.

A foundational design system already exists in `lib/shared/theme/`:

- `colors.dart` — AppColors with primary (Indigo #6366F1), secondary (Purple #8B5CF6), semantic colors, neutral palette
- `spacing.dart` — 8-point grid (xs: 4px through huge: 64px)
- `typography.dart` — Inter (UI) and Crimson Pro (display), Material Design 3 type scale
- `app_theme.dart` — flex_color_scheme based theming

This spec formalizes, extends, and documents that system.

---

# 5. Requirements

## 5.1 Functional Requirements

- The design system must provide a complete color palette via named design tokens.
- The design system must support light mode and dark mode.
- The design system must provide spacing tokens covering the full 8-point grid.
- The design system must provide border radius tokens.
- The design system must provide a typography scale compatible with Material Design 3.
- The design system must expose a reusable component library in `lib/shared/widgets/`.
- The design system must support dynamic color (Material You) where available.
- All hardcoded visual values in the application must be replaced with design tokens.

## 5.2 Non-Functional Requirements

- Design tokens must be defined as Dart constants in `lib/shared/theme/`.
- No raw color hex codes or numeric spacing values should appear in widget code.
- The theme must be configurable from a single root entry point.
- All components must support both light and dark themes without modification.
- Components must meet WCAG AA color contrast requirements.
- The design system must be documented with usage examples.

---

# 6. Architecture

## 6.1 Design Token Structure

### Colors (`lib/shared/theme/colors.dart`)

```
AppColors
  — Primary palette
    primary           #6366F1  (Indigo)
    primaryLight      #818CF8
    primaryDark       #4F46E5

  — Secondary palette
    secondary         #8B5CF6  (Purple)
    secondaryLight    #A78BFA
    secondaryDark     #7C3AED

  — Semantic
    success           #10B981
    warning           #F59E0B
    error             #EF4444
    info              #3B82F6

  — Neutral palette (50–900)
    neutral50  → neutral900

  — Surface tokens
    surface
    onSurface
    surfaceVariant
    background
    onBackground
```

### Spacing (`lib/shared/theme/spacing.dart`)

```
AppSpacing
  xs    4px
  sm    8px
  md    12px
  lg    16px
  xl    24px
  xxl   32px
  xxxl  48px
  huge  64px
```

### Border Radius (`lib/shared/theme/radius.dart`)

```
AppRadius
  none    0px
  xs      4px
  sm      8px
  md      12px
  lg      16px
  xl      24px
  full    9999px  (pill shape)
```

### Typography (`lib/shared/theme/typography.dart`)

```
Font families:
  UI text:      Inter (google_fonts)
  Display text: Crimson Pro (google_fonts)

Type scale (Material Design 3):
  displayLarge / displayMedium / displaySmall
  headlineLarge / headlineMedium / headlineSmall
  titleLarge / titleMedium / titleSmall
  bodyLarge / bodyMedium / bodySmall
  labelLarge / labelMedium / labelSmall
```

## 6.2 Theme Architecture

```
app_theme.dart
  ↓
FlexColorScheme.light()  — light theme
FlexColorScheme.dark()   — dark theme
  ↓
ThemeData (MaterialApp theme / darkTheme)
  ↓
AppThemeModeProvider (Riverpod) — tracks current mode
```

Theme mode is stored in `StorageService` and restored on launch.

## 6.3 Component Library (`lib/shared/widgets/`)

```
lib/shared/widgets/
  buttons/
    app_button.dart         — primary, secondary, ghost variants
    app_icon_button.dart
  cards/
    app_card.dart
  inputs/
    app_text_field.dart
  layout/
    app_scaffold.dart
    app_divider.dart
    app_spacer.dart
  feedback/
    app_loading_indicator.dart
    app_empty_state.dart
    app_error_state.dart
  typography/
    app_text.dart           — opinionated text widget using type scale
  chips/
    app_chip.dart
    app_tag.dart
```

## 6.4 Component Design Principles

- All components accept only semantic tokens, never raw values.
- Components must be stateless where possible.
- Components must support accessibility semantics (`Semantics` widget where needed).
- Components must be testable in isolation (widget tests, golden tests).

## 6.5 Dependencies

- `flex_color_scheme` — advanced Material 3 theming
- `google_fonts` — Inter and Crimson Pro
- `dynamic_color` — Material You / system color support
- `flutter_svg` — SVG icons and illustrations
- `flutter_animate` — declarative animation primitives

---

# 7. Implementation Plan

## Phase 1 — Token Audit and Completion

- [ ] Audit `lib/shared/theme/colors.dart` against the token set defined in this spec.
- [ ] Add missing color tokens (surface tokens, extended neutral palette).
- [ ] Create or verify `lib/shared/theme/radius.dart` with `AppRadius` constants.
- [ ] Verify `AppSpacing` matches the canonical spacing values.
- [ ] Verify `AppTypography` matches Material Design 3 type scale.

## Phase 2 — Theme Architecture

- [ ] Verify `app_theme.dart` generates both light and dark `ThemeData`.
- [ ] Verify `AppThemeModeProvider` persists theme mode via `StorageService`.
- [ ] Validate dynamic color integration via `dynamic_color` package.

## Phase 3 — Component Library

- [ ] Create `AppButton` with primary, secondary, and ghost variants.
- [ ] Create `AppCard` with standard and elevated variants.
- [ ] Create `AppTextField` with standard styling.
- [ ] Create `AppScaffold` with consistent layout structure.
- [ ] Create `AppLoadingIndicator`, `AppEmptyState`, `AppErrorState`.
- [ ] Create `AppText` widget wrapping the type scale.

## Phase 4 — Enforcement

- [ ] Audit existing screens for hardcoded values; replace with tokens.
- [ ] Add lint rules or custom analysis to flag raw numeric values in widget code.

## Phase 5 — Validation

- [ ] Write widget tests for each component.
- [ ] Write golden tests for key components in light and dark mode.
- [ ] Validate color contrast ratios meet WCAG AA.
- [ ] Run `flutter analyze` with zero errors.

---

# 8. Validation Plan

- Widget tests for each component in isolation.
- Golden tests capturing light and dark mode rendering for key components.
- Manual accessibility audit (contrast, readable text, touch targets).
- CI must execute `flutter test` and pass.
- Design review against `DESIGN.md` principles.

---

# 9. Acceptance Criteria

- [ ] All design tokens are defined as named Dart constants.
- [ ] No raw hex codes or numeric spacing values appear in widget code.
- [ ] Light and dark themes are fully functional.
- [ ] Core component library covers buttons, cards, inputs, layout, and feedback.
- [ ] All components pass widget tests.
- [ ] Golden tests exist for key components.
- [ ] WCAG AA contrast is satisfied.
- [ ] `flutter analyze` passes with zero errors.

---

# 10. Open Questions

- Should domain-specific accent colors be a design system concern, or handled per feature?
- Should the design system support a high-contrast accessibility mode?
- Should component golden tests be platform-specific (iOS, Android, Web), or single-platform?
- When should `dynamic_color` (Material You) override the fixed design tokens?
- Should the component library include data visualization primitives (charts, progress rings)?
