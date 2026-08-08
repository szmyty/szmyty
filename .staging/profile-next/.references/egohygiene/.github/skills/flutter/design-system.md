# 🎨 Flutter Design System Skill

---

# Purpose

This skill defines how visual systems are implemented within Flutter applications built using the Ego Hygiene engineering ecosystem.

The goal is to translate design philosophy into reusable, consistent, scalable UI systems.

The design system should support:

- clarity
- cognition
- accessibility
- beauty
- maintainability

---

# Core Philosophy

Interfaces should support:

    Understanding

not:

    Stimulation

Design exists to reduce cognitive load.

Design should guide attention intentionally.

---

# Design Hierarchy

Prefer:

    Design Tokens
        ↓
    Components
        ↓
    Screens
        ↓
    Experiences

Avoid:

    Screen-specific styling

whenever possible.

---

# Design Tokens

All visual properties should originate from tokens.

Examples:

    Colors
    Typography
    Spacing
    Border Radius
    Elevation
    Motion

Avoid hardcoded values.

---

# Theme System

Use:

    flex_color_scheme

as the primary theme foundation.

Applications should support:

- light mode
- dark mode
- future brand themes

Theme switching should be centralized.

---

# Typography

Use:

    google_fonts

Typography should prioritize:

- readability
- hierarchy
- breathing room

Avoid:

- decorative fonts
- excessive variation
- dense layouts

---

# Color Philosophy

Colors should:

- communicate hierarchy
- guide attention
- reinforce meaning

Avoid:

- excessive saturation
- visual noise
- attention competition

Accent colors should be intentional.

---

# Spacing System

Spacing should follow a predictable scale.

Example:

    4
    8
    12
    16
    24
    32
    48
    64

Consistency is more important than novelty.

---

# Component Philosophy

Components should be:

- reusable
- composable
- testable

Avoid:

- one-off widgets
- duplicated UI patterns

---

# Shared Component Structure

Examples:

    AppButton
    AppCard
    AppTextField
    AppDialog
    AppListTile

Shared components belong in:

    shared/widgets/

---

# Motion Philosophy

Motion should support cognition.

Motion should:

- explain transitions
- reinforce progress
- create delight

Motion should not:

- distract
- delay interaction
- overwhelm users

---

# Motion Hierarchy

## Utility Motion

Examples:

- page transitions
- state changes
- navigation feedback

Fast and subtle.

---

## Reinforcement Motion

Examples:

- task completion
- insight generation
- achievement moments

Visible but restrained.

---

## Wonder Motion

Examples:

- onboarding
- milestone celebrations
- major life events

Rare and memorable.

---

# Animation Standards

Preferred:

    flutter_animate

For lightweight motion.

Preferred:

    lottie

for asset-driven animations.

Optional:

    rive

for advanced interactive motion.

---

# 3D Philosophy

3D is an identity layer.

3D should be used for:

- onboarding
- branding
- achievement moments
- atmospheric experiences

Avoid using 3D as a primary interaction mechanism.

---

# Illustration Philosophy

Illustrations should:

- support understanding
- reinforce identity
- reduce intimidation

Illustrations should not exist solely for decoration.

---

# Information Density

Prefer:

    Progressive Disclosure

Users should encounter:

- simple entry points
- optional depth

Avoid overwhelming first impressions.

---

# Accessibility

Design systems must support:

- scalable text
- screen readers
- color contrast
- keyboard navigation
- assistive technologies

Accessibility is a requirement.

Not an enhancement.

---

# Insight Artifacts

Insights are first-class objects.

Important insights may become:

- cards
- summaries
- diagrams
- visual artifacts

Visual representation should improve understanding.

---

# Gamification Philosophy

Prefer:

- milestones
- recognition
- progress visibility

Avoid:

- addiction loops
- meaningless points
- artificial urgency

The goal is growth.

Not engagement.

---

# Branding Philosophy

The application should feel:

- calm
- intelligent
- trustworthy
- personal
- modern

The visual system should communicate:

    Growth Through Understanding

rather than:

    Productivity Through Pressure

---

# Architectural Smells

Watch for:

- hardcoded colors
- duplicated components
- ad hoc animations
- inconsistent spacing
- visual clutter

---

# Final Rule

If something is beautiful but distracting:

    remove it.

If something is beautiful and clarifying:

    keep it.
