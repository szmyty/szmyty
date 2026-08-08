# Commit conventions

This repository uses **Conventional Commits** with emoji-enhanced subjects to keep commit history readable and ready for future automation.

## Format

```text
type: emoji short description
```

Examples:

- `docs: 🧠 establish universal AI-native engineering system`
- `feat: ✨ initialize flutter application foundation`
- `fix: 🐛 resolve notification permission handling`
- `ci: ⚙️ add android build workflow`

## Allowed commit types

- `build`
- `chore`
- `ci`
- `docs`
- `feat`
- `fix`
- `perf`
- `refactor`
- `revert`
- `specs`
- `agents`
- `skills`
- `design`
- `test`

## Preferred emoji mapping

- `docs`: 🧠 documentation / knowledge system
- `specs`: 📐 specifications
- `agents`: 🤖 AI agent definitions
- `skills`: 🛠️ AI skills
- `design`: 🎨 design system
- `feat`: ✨ features
- `fix`: 🐛 fixes
- `refactor`: ♻️ refactors
- `test`: 🧪 tests
- `ci`: ⚙️ CI/CD
- `chore`: 🔧 repository maintenance

## Local validation

1. Install dependencies: `npm install`
2. Enable local hooks: `npm run prepare`
3. Commit as normal with `git commit -m "type: emoji description"`

The commit-msg hook runs commitlint and validates commit messages while preserving normal `git commit --message` usage.

## Future release automation

Using Conventional Commits now keeps the project ready for a follow-up setup with tools like semantic-release or release-please to automate versioning, changelogs, and GitHub releases.
