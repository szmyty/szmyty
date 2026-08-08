# 🤝 Contributor Guide

> *How to contribute to Ego Hygiene.*

---

## Welcome

Contributions are welcome from humans and AI agents.

This guide covers the complete contribution workflow: setup, coding standards, testing, and the pull request process.

---

## Before You Begin

### Understand the Architecture

Ego Hygiene is a specification-driven, architecture-first project.

Before writing code, read:

1. [START_HERE.md](../START_HERE.md) — orientation
2. [ARCHITECTURE.md](../ARCHITECTURE.md) — architectural principles
3. [docs/architecture/overview.md](architecture/overview.md) — feature-first organization
4. [docs/developer-setup.md](developer-setup.md) — environment setup

Architecture takes precedence over implementation convenience.

When in doubt, consult the relevant specification in `.github/specs/`.

---

## Environment Setup

Follow [docs/developer-setup.md](developer-setup.md) to configure your local environment.

**Quick setup:**

```bash
git clone https://github.com/egohygiene/egohygiene.git
cd egohygiene
task setup
task generate
task run
```

**Required tools:**

- [FVM](https://fvm.app/) — Flutter version manager (required)
- [Task](https://taskfile.dev/) — task runner (recommended)

---

## Project Structure

```
apps/egohygiene/lib/
├── app/              # App-level config
├── features/         # Feature modules (presentation, providers, domain, data)
└── shared/           # Reusable infrastructure (80/20 boundary)
```

Features are self-contained modules. Shared infrastructure is reusable across features.

See [docs/REPOSITORY_MAP.md](REPOSITORY_MAP.md) for the complete structure.

---

## Coding Standards

### Feature-First Architecture

Every feature lives in `lib/features/<feature_name>/` with four internal layers:

```
feature_name/
├── feature.dart      # Public barrel — export domain types, providers, primary screens only
├── presentation/     # UI screens and widgets
├── providers/        # Riverpod state providers
├── domain/           # Business logic and models
└── data/             # Repositories and storage access
```

Features must not depend on other feature internals.

Cross-feature dependencies go through domain types or shared providers.

### State Management

Use Riverpod with code generation for all state management.

```dart
// Define providers using @riverpod annotation
@riverpod
class MyNotifier extends _$MyNotifier {
  @override
  MyState build() => MyState.initial();
}
```

Run `task generate` after adding or modifying providers.

### Service Abstractions

Never depend directly on concrete implementations.

Use service abstractions from `lib/shared/services/`:

```dart
// ✅ Correct — depend on abstraction
final storage = ref.watch(storageServiceProvider);

// ❌ Incorrect — depend on concrete implementation
final storage = HiveStorageService();
```

### Design Tokens

Use design tokens from `lib/shared/theme/` instead of hardcoded values:

```dart
// ✅ Correct — use design tokens
padding: EdgeInsets.all(AppSpacing.md),
color: AppColors.primary,

// ❌ Incorrect — hardcoded values
padding: EdgeInsets.all(16),
color: Color(0xFF2196F3),
```

Import all tokens via `theme_tokens.dart`.

### Localization

All user-facing strings must use the localization system.

```dart
// ✅ Correct — type-safe localization
Text(context.t.features.checkIn.title)

// ❌ Incorrect — hardcoded string
Text('Daily Check-in')
```

Run `task generate` after modifying any `*.i18n.json` file.

### Barrel Files

Each feature exposes a `feature.dart` barrel that exports only public APIs:

- Domain types
- Public providers
- Primary screens

Data implementations and internal widgets are **not** exported.

---

## Testing

### Running Tests

```bash
# Run all tests
task test

# Run with coverage
task test:coverage

# Run specific test file
cd apps/egohygiene && fvm flutter test test/features/check_in/...
```

### Test Structure

Tests mirror the `lib/` directory structure:

```
test/
├── helpers/          # Shared test helpers (use these; do not redefine fakes)
├── app/              # App-level tests
├── features/         # Feature tests
└── shared/           # Shared infrastructure tests
```

### Test Helpers

Use `test/helpers/fake_storage_service.dart` as the shared in-memory `StorageService` fake.

Do not redefine storage fakes in individual test files.

### Test Requirements

- Unit tests for domain logic and providers
- Widget tests for non-trivial UI
- Integration tests for critical user flows

Not every change requires exhaustive testing.

Focus testing on behavior that could break without notice.

---

## Commit Conventions

Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard.

Commit messages are linted automatically via commitlint.

**Format:**

```
<type>(<scope>): <description>
```

**Common types:**

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change without behavior change |
| `docs` | Documentation change |
| `test` | Test additions or changes |
| `chore` | Build, tooling, or dependency change |
| `style` | Code style (no logic change) |

**Examples:**

```
feat(check-in): add mood intensity slider
fix(storage): resolve migration rollback for v3
docs(architecture): update 80/20 boundary description
```

See [docs/commits.md](commits.md) for full conventions.

---

## Pull Request Process

### Before Opening a PR

1. Run `task ci:local` to verify your changes pass locally
2. Ensure new or modified behavior has test coverage
3. Update documentation if architecture or public APIs changed
4. Write a clear PR description

```bash
task ci:local
```

This runs the same sequence as CI: pub get → generate → analyze → test → coverage.

### PR Description

A good PR description includes:

- **What changed** — summary of the change
- **Why** — motivation or linked issue
- **How tested** — what was run to validate

### Review Expectations

- Architecture decisions are reviewed carefully
- PRs that expand scope beyond the linked issue will be asked to narrow focus
- Generated files (`*.g.dart`, `strings.g.dart`) should not be committed

### Generated Files Policy

Generated files are excluded from version control.

Never commit:

- `*.g.dart` (Riverpod generated providers)
- `strings.g.dart` (Slang localization)

Regenerate locally as needed with `task generate`.

---

## Branch Naming

```
feat/<feature-name>
fix/<bug-description>
chore/<task>
refactor/<area>
docs/<document>
```

---

## Code Generation

Two generators must be run before first build and after relevant changes:

| Generator | Trigger | Command |
|---|---|---|
| `build_runner` | Add/modify `@riverpod` provider | `task generate` |
| `slang` | Add/modify `*.i18n.json` | `task generate` |

Both run together with:

```bash
task generate
```

---

## Working with Specifications

Specifications in `.github/specs/` define how things should be built.

Before implementing anything non-trivial, check whether a relevant specification exists.

If a specification is unclear or missing, surface that before implementing.

    Specifications define intent.
    Implementation follows specifications.
    Specifications should outlive implementation.

---

## Getting Help

- Review [docs/REPOSITORY_MAP.md](REPOSITORY_MAP.md) for any file's purpose
- Review [docs/architecture/](architecture/) for system-level details
- Check [.github/specs/](../.github/specs/) for feature specifications
- Open a GitHub Issue if something is ambiguous or broken

---

## Contribution Principles

- **Scope discipline** — implement what is requested; do not expand scope without discussion
- **Architecture respect** — do not invent architecture; follow what is documented
- **Simplicity first** — clear and maintainable code over cleverness
- **Foundation before feature** — shared infrastructure precedes application-specific work
- **Testable by design** — design code so it can be tested without heroics
