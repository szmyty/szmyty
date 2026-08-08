# Developer Setup

This guide covers local setup and the default workflow for Ego Hygiene.

## Prerequisites

- Git
- [FVM](https://fvm.app/) (Flutter Version Management)
- [Task](https://taskfile.dev/) (optional, for one-command shortcuts)
- Android Studio (Android SDK + emulator tooling)
- Chrome (for Flutter web)

Project Flutter version is pinned in `.fvmrc` (`3.44.2`).

## First-build checklist

Complete this sequence once after a fresh clone:

- [ ] Install [FVM](https://fvm.app/) and add it to your `PATH`
- [ ] Install [Task](https://taskfile.dev/) (optional but recommended)
- [ ] Run `fvm install --setup` at repository root
- [ ] Run generation commands from `apps/egohygiene`
- [ ] Run `fvm flutter run` from `apps/egohygiene` to launch the app

> The app **will not compile** until `cd apps/egohygiene && fvm dart run build_runner build --delete-conflicting-outputs && fvm dart run slang` has been run at least once.

## One-command setup

```bash
fvm install --setup
```

Equivalent command:

```bash
fvm install --setup
cd apps/egohygiene
fvm flutter pub get
```

## Code generation

The project uses two code generators that must run before the first build and after any relevant source change:

| Generator | Command | What it produces |
| --- | --- | --- |
| `build_runner` / `riverpod_generator` | `cd apps/egohygiene && fvm dart run build_runner build --delete-conflicting-outputs` | `*.g.dart` files containing generated Riverpod provider boilerplate |
| `slang` | `cd apps/egohygiene && fvm dart run slang` | `strings.g.dart` — strongly-typed localization classes from `app_en.i18n.json` |

Run both together with:

```bash
cd apps/egohygiene && fvm dart run build_runner build --delete-conflicting-outputs && fvm dart run slang
```

Re-run `cd apps/egohygiene && fvm dart run build_runner build --delete-conflicting-outputs && fvm dart run slang` whenever you:

- Add or modify a `@riverpod`-annotated provider
- Add, rename, or update keys in any `*.i18n.json` file

### Generated file policy

Generated Riverpod files (`*.g.dart` from `riverpod_generator`) are excluded from version control. They are reproducible from source and should never be committed.

Generated localization files (`strings.g.dart` from `slang`) are also excluded from version control. Although they are derived deterministically from the source JSON files, they are kept out of the repository to maintain a single source of truth and avoid merge noise. Run `cd apps/egohygiene && fvm dart run build_runner build --delete-conflicting-outputs && fvm dart run slang` after any `*.i18n.json` change.

## One-command workflows

Use either Taskfile commands or VS Code tasks (`Terminal → Run Task`).

| Goal | Command |
| --- | --- |
| Analyze | `cd apps/egohygiene && fvm flutter analyze` |
| Test | `cd apps/egohygiene && fvm flutter test` |
| Coverage | `cd apps/egohygiene && fvm flutter test --coverage` |
| Build | `cd apps/egohygiene && fvm flutter build web --release` |
| Run | `cd apps/egohygiene && fvm flutter run` |
| Code generation | `cd apps/egohygiene && fvm dart run build_runner build --delete-conflicting-outputs && fvm dart run slang` |
| Local CI parity | `cd apps/egohygiene && fvm flutter pub get && fvm dart run build_runner build --delete-conflicting-outputs && fvm dart run slang && fvm flutter analyze && fvm flutter test --coverage` |

## VS Code workflow

Included in `.vscode/`:

- `tasks.json` for setup, generate, analyze, test, run, and build
- `launch.json` for Flutter launch (default device + Chrome)
- `extensions.json` with focused Flutter/dev tooling recommendations

## Android emulator setup

List available emulators:

```bash
cd apps/egohygiene
fvm flutter emulators
```

Launch an emulator:

```bash
cd apps/egohygiene
fvm flutter emulators --launch <emulator_id>
```

Run app on emulator:

```bash
cd apps/egohygiene
fvm flutter run -d <emulator_id>
```

## Flutter web setup

Enable web support once:

```bash
cd apps/egohygiene
fvm flutter config --enable-web
```

Run web app:

```bash
cd apps/egohygiene
fvm flutter run -d chrome
```

Build web release:

```bash
cd apps/egohygiene
fvm flutter build web --release
```

## Optional Ollama setup

The real Ollama provider is opt-in. The app continues to use the demo provider
unless Ollama is explicitly enabled.

1. Install Ollama locally.
2. Pull a model:

   ```bash
   ollama pull llama3.2
   ```

3. Start the Ollama server:

   ```bash
   ollama serve
   ```

4. Run Ego Hygiene with Ollama enabled:

   ```bash
   cd apps/egohygiene
   fvm flutter run \
     --dart-define=EGOHYGIENE_ENABLE_OLLAMA=true \
     --dart-define=EGOHYGIENE_AI_PROVIDER=ollama \
     --dart-define=EGOHYGIENE_OLLAMA_MODEL=llama3.2
   ```

Optional defines:

- `EGOHYGIENE_OLLAMA_BASE_URL` — defaults to `http://127.0.0.1:11434`
- `EGOHYGIENE_OLLAMA_TIMEOUT_MS` — defaults to `30000`

If Ollama is unreachable, the app falls back to the demo provider so local
development and CI remain unaffected.

## Repository cleanup

Two cleanup tasks are available with different levels of aggressiveness:

| Task | What it removes | When to use |
| --- | --- | --- |
| `task clean` | Build artifacts, `.dart_tool/`, `build/`, `coverage/` | Day-to-day cleanup |
| `task reset` | Everything `clean` removes **plus** the FVM SDK cache | Full environment reset (triggers re-download of Flutter SDK) |

Prefer `task clean` for normal cleanup. Use `task reset` only when you need to fully reset the FVM SDK cache (e.g., after a corrupted installation).

## CI alignment

`task ci:local` mirrors the CI pipeline command sequence:

1. `cd apps/egohygiene && fvm flutter pub get`
2. `cd apps/egohygiene && fvm dart run build_runner build --delete-conflicting-outputs`
3. `cd apps/egohygiene && fvm dart run slang`
4. `cd apps/egohygiene && fvm flutter analyze`
5. `cd apps/egohygiene && fvm flutter test --coverage`

Local commands use `fvm flutter ...` to guarantee the pinned SDK version.

### Coverage reporting

Both CI entry workflows (`build.yml` for pull requests and
`development-build.yml` for `main`) now call the shared reusable workflow at
`.github/workflows/reusable/flutter-ci.yml`.

That reusable test pipeline generates `coverage/lcov.info`, uploads it as the
`coverage-lcov` artifact, and publishes a line-coverage summary in the workflow
run UI for both PR and development builds.

Coverage enforcement remains optional while the project establishes a baseline.
When `COVERAGE_THRESHOLD` is defined as a GitHub Actions variable, the PR CI
workflow enforces the threshold. Development builds continue to publish
artifacts without threshold gating, while still collecting and uploading
coverage for visibility.

## Troubleshooting

### `fvm: command not found`

Install FVM and verify it is on your `PATH`, then re-run `fvm install --setup`.

### VS Code cannot find Flutter SDK

Open the workspace root and ensure the Dart extension is installed. The repo uses `.fvm/` and expects Flutter from FVM.

### `flutter run -d chrome` cannot find Chrome

Install Chrome and run:

```bash
cd apps/egohygiene
fvm flutter devices
```

to confirm `chrome` is available.

### Stale generated code errors

Re-run:

```bash
cd apps/egohygiene && fvm dart run build_runner build --delete-conflicting-outputs && fvm dart run slang
```

### Android license or SDK errors

Run:

```bash
cd apps/egohygiene
fvm flutter doctor --android-licenses
fvm flutter doctor -v
```
