# 🔔 Flutter Notifications Skill

---

# Purpose

This skill defines notification architecture standards for Flutter applications built within the Ego Hygiene engineering ecosystem.

Notifications are considered a core platform capability.

The goal is to support:

- reminders
- routines
- reflection prompts
- milestone recognition
- scheduled activities
- future AI-assisted recommendations

while preserving user trust and minimizing notification fatigue.

---

# Core Philosophy

Notifications should support:

    Intention

not:

    Interruption

The system should help users maintain awareness without competing for attention.

---

# Primary Standard

Use:

    flutter_local_notifications
    timezone

as the primary notification stack.

---

# Notification Types

## Reminders

Examples:

- journaling reminders
- gratitude reminders
- routine reminders
- reflection reminders

---

## Milestones

Examples:

- achievements
- reflection milestones
- progress recognition

---

## Informational

Examples:

- synchronization status
- backup completion
- insight availability

---

## Future AI-Assisted

Examples:

- suggested reflection prompts
- contextual reminders
- adaptive support

These should remain optional.

---

# Notification Architecture

Notifications should be treated as a capability.

Prefer:

    NotificationProvider

over:

    FlutterNotificationImplementation

at architectural boundaries.

---

# Permission Strategy

Permissions should be:

- explicit
- understandable
- reversible

Users should know:

- why notifications are requested
- what types of notifications will be sent
- how to disable them

Avoid aggressive permission requests during onboarding.

---

# Scheduling Philosophy

Scheduling should support:

- one-time events
- recurring events
- future adaptive scheduling

Schedules should be deterministic and inspectable.

---

# Offline First

Notifications should function without:

- cloud services
- external APIs
- active internet connectivity

Local reminders are the default.

---

# Timezone Support

Always use:

    timezone

for scheduled notifications.

Avoid assuming:

    device local time only

The system should remain robust across:

- travel
- daylight savings changes
- locale changes

---

# Reflection Integration

Reflection is a first-class domain.

Notifications may support:

- journaling prompts
- gratitude prompts
- insight review reminders
- reflection checkpoints

The goal is to encourage awareness, not compliance.

---

# Achievement Integration

Achievements should be:

- meaningful
- infrequent
- celebratory

Avoid:

- excessive achievement spam
- meaningless rewards

Recognition should feel earned.

---

# Notification Fatigue

Notification volume should remain low.

Prefer:

    fewer meaningful notifications

over:

    many low-value notifications

---

# User Control

Users should be able to:

- enable categories
- disable categories
- adjust schedules
- pause notifications

Control should remain local and transparent.

---

# Accessibility

Notifications should support:

- localized content
- accessibility labels
- readable formatting

---

# Testing

Verify:

- scheduling
- cancellation
- recurrence
- timezone handling
- permission flows

Notification behavior should be testable.

---

# Future Capability Inventory

Potential future enhancements:

    awesome_notifications

Examples:

- richer layouts
- advanced actions
- notification grouping

These remain optional.

---

# Architectural Smells

Watch for:

- hardcoded notification text
- cloud-dependent reminders
- hidden scheduling logic
- excessive frequency
- permission pressure

---

# Final Rule

Notifications should create clarity.

If notifications become noise:

    reduce them.
