# 🎨 Ego Hygiene — Design System

---

# Purpose

This document defines the visual, experiential, and emotional design principles of Ego Hygiene.

The goal is not simply to create an attractive application.

The goal is to create an environment that supports:

- reflection
- clarity
- navigation
- insight
- growth

The design system exists to reduce cognitive load while preserving delight, curiosity, and engagement.

---

# Design Philosophy

Ego Hygiene should feel:

- calm
- intelligent
- intentional
- beautiful
- trustworthy
- alive

The system should communicate:

    clarity over complexity

and

    understanding over optimization

---

# Core Principle

Interfaces should support cognition.

Interfaces should not compete with cognition.

The best interface often disappears.

---

# Emotional Design

The application should never feel:

- stressful
- overwhelming
- noisy
- manipulative
- addictive

Avoid:

- engagement farming
- attention hijacking
- artificial urgency

The system should instead encourage:

- awareness
- curiosity
- reflection
- intentional action

---

# Visual Identity

The visual language should feel:

- modern
- minimal
- elegant
- expressive

Visuals should communicate:

    calm sophistication

rather than:

    enterprise productivity

---

# Motion Philosophy

Motion exists to:

- communicate state
- reinforce understanding
- celebrate progress
- create delight

Motion does NOT exist to:

- distract
- entertain endlessly
- increase cognitive load

---

# Motion Hierarchy

## Level 1 — Utility

Used frequently.

Examples:

- page transitions
- state changes
- navigation feedback

Subtle and fast.

---

## Level 2 — Reinforcement

Used occasionally.

Examples:

- task completion
- insight generation
- milestone recognition

Noticeable but restrained.

---

## Level 3 — Wonder

Used rarely.

Examples:

- onboarding
- major achievements
- meaningful life milestones

These moments should feel memorable.

---

# 3D Philosophy

3D is an identity layer.

3D is not the primary interface.

Use 3D to:

- create atmosphere
- reinforce branding
- support onboarding
- celebrate progress

Avoid using 3D for:

- routine interaction
- core workflows
- essential navigation

---

# Color Philosophy

Color should support cognition.

Avoid:

- overly saturated palettes
- aggressive contrast
- visual noise

Prefer:

- soft gradients
- natural transitions
- emotionally neutral foundations

Accent colors should guide attention intentionally.

---

# Typography

Typography should prioritize:

- readability
- hierarchy
- breathing room

Avoid:

- dense information walls
- excessive font variation
- decorative typography

---

# Information Density

The system should favor:

    progressive disclosure

over:

    information overload

Users should be able to:

- start simple
- go deeper intentionally

---

# Reflection-First UX

Reflection is a primary capability.

The interface should encourage:

- journaling
- contemplation
- synthesis
- insight generation

without creating friction.

---

# Cognitive Navigation

Long-term, Ego Hygiene should support:

- navigable cognition
- visual relationships
- contextual exploration

The system should help users answer:

    Where am I?

    What matters?

    What changed?

    What should I focus on next?

---

# Insight Artifacts

Insights are first-class objects.

Important realizations should be capable of becoming:

- summaries
- visualizations
- diagrams
- reflection artifacts

These artifacts should feel:

- meaningful
- personal
- memorable

---

# Gamification Philosophy

Gamification should reinforce growth.

Avoid:

- addiction loops
- arbitrary point systems
- meaningless streak pressure

Prefer:

- milestone recognition
- progress visibility
- reflection rewards
- meaningful achievements

---

# Branding Philosophy

Ego Hygiene should feel:

- personal
- human
- thoughtful

The brand should communicate:

    growth through understanding

rather than:

    productivity through pressure

---

# Design Constraints

Every design decision should improve at least one of:

- clarity
- navigation
- reflection
- understanding
- emotional safety

If a feature is visually impressive but does not improve these outcomes:

    remove it.

---

# Long-Term Vision

The ultimate design goal is:

    a beautiful cognition environment

An interface that helps people:

- understand themselves
- navigate complexity
- externalize insight
- transform reflection into action

while remaining calm, approachable, and deeply human.

---

# Voice & Microcopy

## Personality

The application voice should feel:

- calm
- encouraging
- thoughtful
- clear
- non-judgmental

Avoid technical language where unnecessary.
Avoid overwhelming users.

## Principles

**Be human, not robotic.**

    ✅ "Nothing here yet — your reflections will appear as you begin."
    ❌ "No records found."

**Acknowledge without alarming.**

    ✅ "Something didn't load as expected. Try again when you're ready."
    ❌ "Error 500: Internal server failure."

**Stay calm under pressure.**

    ✅ "Unable to load right now. You can still continue."
    ❌ "Fatal error. Please contact support."

**Encourage without pressure.**

    ✅ "Begin with whatever is on your mind."
    ❌ "You must complete this step to continue."

**Be specific without being technical.**

    ✅ "Unable to load reflections right now."
    ❌ "FutureProvider threw an exception."

## Shared State Patterns

### Empty States

Empty states should feel like an *invitation*, not a failure.

- Lead with a short, human title.
- Use a description that orients the user and reduces anxiety.
- Offer a gentle next action where appropriate.

```
Title: "Your reflection space is ready"
Description: "Begin with whatever is on your mind. A small thought is enough to start."
Action: "Start your first reflection"
```

### Loading States

Loading states should feel *light and confident*, not uncertain.

- Use `AppLoadingIndicator` for inline or full-screen loading.
- Provide a `semanticLabel` where context matters (e.g. "Sending message…").
- Avoid loading text unless the operation may take more than a few seconds.

### Error States

Error states should feel *calm and recoverable*, not alarming.

- Use `AppErrorState` for all full-screen error presentations.
- Always use `theme.colorScheme.error` for the icon — never bright red hardcoded values.
- Provide a retry action wherever possible.
- Keep the message concise and non-technical.

```dart
AppErrorState(
  message: t.myScreen.loadError,
  action: FilledButton(
    onPressed: () => ref.invalidate(myProvider),
    child: Text(t.common.retry),
  ),
)
```

## Localization Strings

All user-facing strings live in `lib/shared/localization/en.i18n.json`.

Key shared strings:

| Key | Value | Use |
|-----|-------|-----|
| `common.retry` | "Try again" | Retry button label |
| `common.error` | "Something went wrong" | Generic fallback error title |
| `common.loading` | "Loading…" | Generic loading label |
| `errors.loadFailed` | "Unable to load $item right now." | Parameterized load error |
| `errors.loadFailedGeneral` | "Unable to load content. You can still continue." | Non-blocking load error |

---

# Final Rule

If the interface is beautiful but distracting:

    it has failed.

If the interface is beautiful and clarifying:

    it is working.
