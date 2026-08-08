# Release Process

This document describes the release process for the profile repository using semantic versioning.

## Semantic Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** version (X.0.0) - Incompatible API changes or major feature overhauls
- **MINOR** version (0.X.0) - New functionality in a backward-compatible manner
- **PATCH** version (0.0.X) - Backward-compatible bug fixes

## Release Workflow

### 1. Update VERSION File

Edit the `VERSION` file in the repository root:

```bash
echo "1.1.0" > VERSION
```

### 2. Update CHANGELOG.md

Add a new section for your version following the [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [1.1.0] - 2025-12-05

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description
```

Update the comparison links at the bottom:

```markdown
[Unreleased]: https://github.com/szmyty/profile/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/szmyty/profile/releases/tag/v1.1.0
```

### 3. Update Package Versions

Update version in both:

**pyproject.toml:**
```toml
[tool.poetry]
version = "1.1.0"
```

**dashboard-app/package.json:**
```json
{
  "version": "1.1.0"
}
```

### 4. Commit Changes

```bash
git add VERSION CHANGELOG.md pyproject.toml dashboard-app/package.json
git commit -m "Bump version to 1.1.0"
git push origin main
```

### 5. Create Release Tag

```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

This will automatically trigger the release workflow.

### 6. Verify Release

The release workflow will:
1. ✅ Validate that VERSION file matches the tag
2. ✅ Verify CHANGELOG.md contains the version entry
3. ✅ Run all tests
4. ✅ Validate JSON schemas
5. ✅ Create GitHub Release with release notes
6. ✅ Trigger dashboard deployment

Check the [Actions](https://github.com/szmyty/profile/actions) tab to monitor progress.

## Manual Release (Alternative)

You can also trigger a release manually from GitHub Actions:

1. Go to [Actions](https://github.com/szmyty/profile/actions)
2. Select "Release" workflow
3. Click "Run workflow"
4. Enter the version number (e.g., `1.1.0`)
5. Click "Run workflow"

## Version Badge

The README includes a version badge that automatically updates:

```markdown
[![Version](https://img.shields.io/github/v/tag/szmyty/profile?style=for-the-badge&logo=semver&logoColor=white&labelColor=1a1a2e&color=4a4e69&label=version)](https://github.com/szmyty/profile/releases)
```

## Dashboard Integration

When a release includes dashboard changes:

1. The release workflow automatically triggers dashboard deployment
2. Release notes include a link to the live dashboard
3. Dashboard version is kept in sync with the repository version

## Example Release Scenarios

### New Feature (Minor Version Bump)

New weather card animation added:

```bash
# Update to 1.1.0
echo "1.1.0" > VERSION
# Update CHANGELOG.md with "Added" section
# Update pyproject.toml and package.json
git commit -m "Add weather card animation"
git tag v1.1.0
git push --tags
```

### Bug Fix (Patch Version Bump)

Fix broken link in README:

```bash
# Update to 1.0.1
echo "1.0.1" > VERSION
# Update CHANGELOG.md with "Fixed" section
# Update pyproject.toml and package.json
git commit -m "Fix broken link in README"
git tag v1.0.1
git push --tags
```

### Breaking Change (Major Version Bump)

Restructure entire dashboard architecture:

```bash
# Update to 2.0.0
echo "2.0.0" > VERSION
# Update CHANGELOG.md with "Changed" section explaining breaking changes
# Update pyproject.toml and package.json
git commit -m "feat!: restructure dashboard architecture

BREAKING CHANGE: Complete overhaul of dashboard architecture"
git tag v2.0.0
git push --tags
```

## Troubleshooting

### Release Workflow Fails

**Problem:** VERSION file doesn't match tag

**Solution:** Ensure VERSION file is updated and committed before tagging

**Problem:** CHANGELOG.md missing version entry

**Solution:** Add a section for your version in CHANGELOG.md

**Problem:** Tests fail

**Solution:** Fix failing tests before creating release

### Tag Already Exists

If you need to recreate a tag:

```bash
# Delete local tag
git tag -d v1.1.0

# Delete remote tag
git push origin :refs/tags/v1.1.0

# Create new tag
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

## Best Practices

1. **Always update CHANGELOG.md** - Keep users informed of changes
2. **Test before releasing** - Ensure all tests pass locally
3. **Use descriptive commit messages** - Follow conventional commits format
4. **Version synchronization** - Keep VERSION, pyproject.toml, and package.json in sync
5. **Release notes** - Write clear, user-friendly release notes in CHANGELOG.md
6. **Dashboard updates** - When updating dashboard, mention it in release notes

## Resources

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
