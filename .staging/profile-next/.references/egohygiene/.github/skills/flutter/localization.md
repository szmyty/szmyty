# 🌍 Flutter Localization Skill

---

# Purpose

This skill defines localization and internationalization standards for Flutter applications built within the Ego Hygiene engineering ecosystem.

Localization is considered a foundational capability.

Applications should be localization-ready from the beginning, regardless of the number of supported languages.

---

# Core Philosophy

Localization is:

    Architecture

not:

    Future Work

The cost of introducing localization late is significantly higher than initializing localization early.

Applications should be localization-ready before the first major feature is implemented.

---

# Primary Standard

Use:

    flutter_localizations
    intl
    slang

as the primary localization stack.

---

# Supported Goals

Localization should support:

- multiple languages
- regional formatting
- pluralization
- date formatting
- number formatting
- future expansion

---

# String Philosophy

All user-facing text should be localizable.

Avoid:

    Text("Hello World")

Prefer:

    context.l10n.helloWorld

or equivalent generated accessors.

---

# Hard Rule

Never hardcode user-facing strings inside:

- widgets
- screens
- dialogs
- notifications

All visible text should originate from localization resources.

---

# Translation Structure

Prefer generated localization files.

Examples:

    app_en.json
    app_es.json
    app_fr.json

Generated code should provide typed accessors.

Avoid manual string key lookups whenever possible.

---

# Accessibility Integration

Localization should support:

- screen readers
- accessibility labels
- semantic descriptions

Localized accessibility content is first-class content.

---

# Notification Localization

Notifications should be localizable.

Examples:

- reminder titles
- reminder bodies
- achievement messages
- reflection prompts

Avoid embedding fixed strings into notification services.

---

# Date & Time Formatting

Use locale-aware formatting.

Examples:

- dates
- times
- durations
- numbers
- percentages

Never assume:

    en_US

formatting.

---

# AI Integration

AI-generated content may remain language-specific.

However:

- prompts
- instructions
- generated summaries
- system messages

should support future localization when practical.

---

# Domain Language

Prefer domain-specific terminology.

Examples:

    Reflection
    Insight
    Memory
    Progress

Terminology should remain consistent across languages.

---

# Developer Experience

Localization should be:

- discoverable
- generated
- type-safe

Developers should not manually manage translation keys whenever possible.

---

# Testing

Verify:

- localization generation
- fallback behavior
- missing translation handling
- locale switching

Localization should fail visibly during development.

---

# Architectural Smells

Watch for:

- hardcoded strings
- duplicated translations
- locale-specific logic
- untranslated notifications
- untranslated accessibility labels

---

# Future Expansion

Applications should be capable of supporting:

- community translations
- user-contributed translations
- machine-assisted translations

without major architectural changes.

---

# Final Rule

If a user-facing string exists:

    it should be localizable.

No exceptions.
