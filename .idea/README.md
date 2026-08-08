# JetBrains project configuration

This directory contains the small, portable subset of JetBrains project
configuration maintained by `empathy`.

The active root configuration intentionally stays minimal. Optional
language-specific files live under `profiles/` and are copied into the
JetBrains locations that understand them only when a repository adopts that
profile.

## Active shared configuration

- `.gitignore` keeps machine-local IDE state out of version control.
- `vcs.xml` declares Git as the repository version-control system.

## Optional profiles

| Profile | Purpose | Status |
| --- | --- | --- |
| `flutter` | Shared Flutter `lib/main.dart` run configuration | Ready |
| `java` | Checkstyle IDEA integration using bundled rule sets | Ready |
| `python` | Ruff configuration resolved from `pyproject.toml` | Ready |

Profile source files are inert while they remain under `profiles/`. This is
intentional: repositories can retain future-ready configuration without
forcing unrelated JetBrains plugins or language support onto every project.

## Applying a profile manually

From a repository root, copy the desired profile contents into `.idea/`.
For example:

    cp -R .idea/profiles/flutter/. .idea/

Review the resulting files before committing them. A future `empathy`
installer or `pace` reconciliation step can automate this safely.

## Ownership boundaries

`empathy` owns portable repository-level IDE metadata. It does not own:

- JetBrains installation or IDE edition
- SDK installation and discovery
- plugin installation
- local workspace state
- generated modules and libraries

Those concerns belong to the developer workstation (`realm`) or to each
individual developer's machine.

## Intentionally excluded source files

The original Ego Hygiene `.idea` directory contained generated or local state
that should not become part of a reusable repository foundation:

- `workspace.xml`
- `modules.xml`
- `libraries/`
- `externalDependencies.xml`
- `jpa-buddy.xml`
- `other.xml`
- `res/colors.xml`

The original `detekt.xml` and `google-java-format.xml` only recorded disabled
or declined plugin state, so they were not promoted into reusable profiles.
A real Kotlin or Java formatting profile should be added later from a tested,
intentional configuration.
