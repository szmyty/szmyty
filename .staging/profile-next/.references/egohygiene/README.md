# Ego Hygiene

🧠 Personal cognition system for reflection, navigation, growth, and AI-assisted self-understanding.

Ego Hygiene is a local-first, privacy-respecting Flutter platform for building a sustainable reflection practice. It combines structured check-ins, memory and timeline systems, and an optional local AI provider to help you stay aligned with your values and goals.

**Platforms:** Android · Web · Linux  
**Foundation stack:** Flutter · Riverpod · GoRouter · Drift · Slang · Task · FVM

## What is Ego Hygiene?

Ego Hygiene is both:

- a human-centered application for reflection and growth
- a reference implementation of a reusable Flutter engineering foundation

The project is designed so contributors can quickly reason about architecture, run the app locally, and extend features without learning the entire codebase first.

## Philosophy

Ego Hygiene is grounded in a few core ideas:

- **Reflection over reaction** — reflection transforms experience into understanding.
- **Externalized cognition** — important context should be stored, not remembered ad hoc.
- **Progress over perfection** — the system rewards consistent return, not flawless execution.
- **Foundation before feature** — shared engineering capabilities are built as reusable infrastructure first.

For deeper context, see [.engineering/architecture/FOUNDATIONS.md](.engineering/architecture/FOUNDATIONS.md), [.engineering/architecture/MANIFESTO.md](.engineering/architecture/MANIFESTO.md), and [VISION.md](VISION.md).

## Architecture

The app follows a **feature-first** architecture with layered modules:

- `presentation/` — UI and interaction flow
- `providers/` — Riverpod state and orchestration
- `domain/` — core logic and models
- `data/` — repository and storage access

Shared, reusable infrastructure lives under `apps/egohygiene/lib/shared/` (taxonomy and ownership boundary: [apps/egohygiene/lib/shared/README.md](apps/egohygiene/lib/shared/README.md)).

Start here for architecture detail:

- [Architecture overview](ARCHITECTURE.md)
- [App code structure](apps/egohygiene/lib/README.md)
- [Design system](.engineering/architecture/DESIGN.md)
- [System engineering model](SYSTEM.md)

## Flutter Foundation

Key implementation choices:

- **Riverpod + code generation** for state management
- **GoRouter** for declarative navigation
- **Slang** for typed localization
- **Drift + storage abstractions** for local-first persistence
- **Taskfile + CI parity workflow** for repeatable developer setup

## Repository Structure

```text
.
├── apps/egohygiene/         # Flutter app workspace
│   ├── lib/                 # app/, features/, shared/
│   ├── test/                # unit/widget/golden tests
│   └── integration_test/    # end-to-end smoke coverage
├── docs/                    # onboarding, testing, domains, practices, research
├── publishing/              # long-form writing and publication assets
├── schemas/                 # canonical cross-system JSON schemas
├── website/                 # reserved home for future website implementation
├── ARCHITECTURE.md          # high-level architecture reference
├── .engineering/architecture/ # canonical architecture and philosophy corpus
├── ROADMAP.md               # planned work and direction
└── Taskfile.yml             # one-command developer workflows
```

## Quick Start

> **Important:** run code generation before first build. The app does not compile without generated files.

### 1) Clone and install prerequisites

- [FVM](https://fvm.app/) (required)
- [Task](https://taskfile.dev/) (recommended)

```bash
git clone https://github.com/egohygiene/egohygiene.git
cd egohygiene
```

### 2) Setup + generate

```bash
task setup
task generate
```

If you do not use Task:

```bash
fvm install --setup
cd apps/egohygiene
fvm flutter pub get
fvm flutter pub run build_runner build --delete-conflicting-outputs
fvm flutter pub run slang
```

### 3) Run the app

```bash
task run
```

Or directly:

```bash
cd apps/egohygiene
fvm flutter run
```

## Development Workflow

Use these day-to-day commands from repository root:

| Goal | Command |
| --- | --- |
| Setup | `task setup` |
| Generate code | `task generate` |
| Analyze | `task analyze` |
| Test | `task test` |
| Coverage | `task test:coverage` |
| Run | `task run` |
| Local CI parity | `task ci:local` |

Developer onboarding docs:

- [Developer setup](docs/developer-setup.md)
- [Testing foundation](docs/testing.md)
- [Commit conventions](docs/commits.md)

## Screenshots

Current visual preview:

![Ego Hygiene application icon](apps/egohygiene/web/icons/Icon-512.png)

UI walkthrough screenshots are being added as feature surfaces stabilize. Until
those are published, this README intentionally includes the versioned app icon
as a lightweight visual reference.

## Local Ollama Setup (Optional)

If no AI provider is configured, Ego Hygiene uses `DemoAIProvider` by default.

To test local Ollama:

```bash
ollama pull llama3.2
ollama serve

cd apps/egohygiene
fvm flutter run \
  --dart-define=EGOHYGIENE_ENABLE_OLLAMA=true \
  --dart-define=EGOHYGIENE_AI_PROVIDER=ollama \
  --dart-define=EGOHYGIENE_OLLAMA_MODEL=llama3.2
```

Optional overrides:

- `EGOHYGIENE_OLLAMA_BASE_URL` (default: `http://127.0.0.1:11434`)
- `EGOHYGIENE_OLLAMA_TIMEOUT_MS` (default: `30000`)

## Downloads

- Stable Release: https://github.com/egohygiene/egohygiene/releases/latest
- Latest Development Build: https://github.com/egohygiene/egohygiene/releases/tag/development
  - Android APK: https://github.com/egohygiene/egohygiene/releases/download/development/egohygiene-development.apk
  - Web bundle: https://github.com/egohygiene/egohygiene/releases/download/development/egohygiene-web-development.tar.gz
  - Linux bundle: https://github.com/egohygiene/egohygiene/releases/download/development/egohygiene-linux-development.tar.gz

## Roadmap

See [ROADMAP.md](ROADMAP.md) for near-term and long-term direction.

## Documentation

Start here, then dive deeper as needed:

- [Architecture overview](ARCHITECTURE.md)
- [Design system](.engineering/architecture/DESIGN.md)
- [System model](SYSTEM.md)
- [Architectural decisions](.engineering/architecture/DECISIONS.md)
- [Security policy](SECURITY.md)
- [Shared module taxonomy](apps/egohygiene/lib/shared/README.md)
- [Schema boundaries](schemas/README.md)
- [Website placeholder](website/README.md)
- [Developer setup](docs/developer-setup.md)
- [Testing foundation](docs/testing.md)
- [Domains](docs/domains/README.md)
- [Practices](docs/practices/README.md)
- [Research](docs/research/README.md)
- [Audit reports](audits/README.md)
- [Architecture audit report (legacy)](docs/AUDIT.md)

## Contributing

Contributions are welcome.

**New here?** Start with [START_HERE.md](START_HERE.md) for a guided entry point.

Recommended onboarding path:

1. Follow [Quick Start](#quick-start)
2. Read [docs/developer-setup.md](docs/developer-setup.md)
3. Read [docs/CONTRIBUTOR_GUIDE.md](docs/CONTRIBUTOR_GUIDE.md) for coding standards and PR process
4. Run `task ci:local` before opening changes
5. Follow [commit conventions](docs/commits.md)
6. Open a PR with a clear summary and validation notes
