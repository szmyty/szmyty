# Workflow Performance Optimization: Python Caching Strategy

This document describes the Python dependency caching strategy implemented across all GitHub Actions workflows in this repository.

## Overview

To reduce workflow execution time and GitHub Actions usage, we implement a multi-layered caching strategy for Python dependencies:

1. **Base Dependency Caching** via `actions/setup-python@v5`
2. **Additional Package Caching** via custom `.github/actions/pip-install` composite action
3. **SVG Hash Caching** for incremental generation (already in place)

## Caching Layers

### Layer 1: Base Dependencies (setup-python)

**Location**: `.github/actions/setup-environment/action.yml`

**How it works**:
- Uses `actions/setup-python@v5` with built-in pip caching
- Cache key based on hash of `requirements*.txt`, `pyproject.toml`, and `poetry.lock`
- Automatically restores pip's HTTP cache and wheel cache
- Shared across all workflows using the same base dependencies

**Cache key pattern**:
```
setup-python-Linux-3.11-<hash-of-requirements-files>
```

**Benefits**:
- Fast installation of base dependencies (`jsonschema`, `Pillow`, `pytest`)
- Automatic invalidation when requirements files change
- Standard GitHub Actions pattern

**Usage in workflows**:
```yaml
- name: Setup environment
  uses: ./.github/actions/setup-environment
  # Automatically caches pip dependencies based on requirements.txt
```

### Layer 2: Additional Package Caching (pip-install action)

**Location**: `.github/actions/pip-install/action.yml`

**How it works**:
- Custom composite action for installing workflow-specific packages
- Cache key based on package names (sorted), Python version, and OS
- Caches pip's download and wheel cache directory (`~/.cache/pip`)
- Each unique package combination gets its own cache

**Cache key pattern**:
```
pip-packages-Linux-py3.11.x-<8-char-hash>[-suffix]
```

**Examples**:
- `pip-packages-Linux-py3.11.9-a1b2c3d4` (Pillow only)
- `pip-packages-Linux-py3.11.9-e5f6g7h8` (jsonschema only)
- `pip-packages-Linux-py3.11.9-i9j0k1l2` (Pillow + jsonschema)

**Benefits**:
- Extremely fast installation from cache (1-3 seconds vs 10-30 seconds)
- Shared cache across workflows installing the same packages
- Independent caches for different package combinations
- Transparent cache hit/miss logging

**Usage in workflows**:
```yaml
- name: Install additional dependencies
  uses: ./.github/actions/pip-install
  with:
    packages: 'Pillow jsonschema'
```

### Layer 3: SVG Hash Caching (Existing)

**Location**: Various workflows using `incremental-generate.py`

**How it works**:
- Stores hash of input JSON data in `.cache` directory
- Skips SVG regeneration if data hasn't changed
- Already implemented and working well

**Cache key pattern**:
```
svg-hash-cache-<github.run_id>
restore-keys: svg-hash-cache-
```

## Workflow-Specific Caching Implementation

> **Note**: As of December 5, 2024, multiple workflows have been consolidated into a single unified workflow (`build-profile.yml`). The caching strategy has been enhanced to support this new architecture.

### build-profile.yml (Unified Pipeline)
The main orchestration workflow implements comprehensive multi-level caching:

- **Python Package Cache**: Via setup-python action (requirements.txt, pyproject.toml, poetry.lock)
- **Pip Cache**: ~/.cache/pip caching for faster package installation
- **Additional Python Packages**: Pillow, jsonschema installed with optimized caching
- **Node.js Cache**: NPM packages for dashboard build and SVGO optimization
- **SVG Hash Cache**: Incremental generation for all card types
- **Expected speedup**: ~2-3 minutes per run with warm caches
- **Full run time**: 8-12 minutes (cold) → 5-8 minutes (warm cache)

### tests.yml
- **Base deps**: Via setup-environment (requirements.txt)
- **No additional deps**: Only uses base dependencies
- **Expected speedup**: ~5-10 seconds per run

### monitoring.yml
- **Base deps**: Via setup-environment (requirements.txt)
- **No additional deps**: Only uses base dependencies
- **Expected speedup**: ~5-10 seconds per run

### Archived Workflows (Pre-Consolidation)

The following workflows have been archived but their caching strategies are preserved for reference:

#### developer.yml (archived)
- Base deps via setup-environment, jsonschema via pip-install
- Expected speedup: ~10-15 seconds per run

#### location-card.yml (archived)
- Base deps via setup-environment, Pillow via pip-install
- SVG caching with incremental-generate.py
- Expected speedup: ~15-20 seconds per run

#### soundcloud-card.yml (archived)
- Base deps via setup-environment, Pillow via pip-install
- SVG caching with incremental-generate.py
- Expected speedup: ~15-20 seconds per run

#### oura.yml (archived)
- No Python deps (pure bash workflow)
- SVG caching with incremental-generate.py

#### weather.yml (archived)
- No Python deps (pure bash workflow)
- SVG caching with incremental-generate.py

#### parallel-fetch.yml (archived)
- Pillow via pip-install in multiple jobs
- Cache shared between jobs
- Expected speedup: ~20-30 seconds per run

## Performance Benchmarks

### Before Optimization (Baseline)

Typical workflow execution times for Python setup:
- Base dependency installation: 15-25 seconds
- Additional package installation: 10-20 seconds per package
- **Total Python setup time**: 25-45 seconds per workflow run

### After Optimization (With Caching)

Expected execution times with cache hits:
- Base dependency installation: 5-8 seconds (cache hit)
- Additional package installation: 1-3 seconds (cache hit)
- **Total Python setup time**: 6-11 seconds per workflow run

### Expected Savings

- **Time saved per run**: 15-35 seconds
- **Percentage improvement**: ~60-75% faster Python setup
- **Daily runs**: ~20 workflow runs (various schedules)
- **Daily time saved**: ~5-12 minutes (calculation: 20 runs × 15-35 seconds)
- **Monthly time saved**: ~2.5-6 hours

## Cache Management

### Cache Retention
- GitHub Actions caches are retained for up to 7 days of inactivity
- Total cache size limit: 10 GB per repository
- Caches are automatically evicted using LRU (Least Recently Used) policy

### Cache Invalidation

Caches are automatically invalidated when:

1. **Base dependencies cache** (setup-python):
   - requirements.txt, requirements-dev.txt modified
   - pyproject.toml or poetry.lock modified
   - Python version changes

2. **Additional packages cache** (pip-install):
   - Different packages are requested
   - Python version changes (e.g., 3.11.8 → 3.11.9)
   - Operating system changes

3. **SVG hash cache**:
   - Input JSON data changes
   - Manually cleared via workflow re-run

### Monitoring Cache Usage

View cache usage in GitHub:
1. Navigate to repository Settings
2. Click on "Actions" → "Caches"
3. See all active caches with keys and sizes

Monitor cache effectiveness in workflow logs:
- Look for "✓ Cache hit for packages: ..." messages
- Look for "✗ Cache miss for packages: ..." messages

## Best Practices

### For Workflow Authors

1. **Use setup-environment first**: Always set up base environment before additional packages
   ```yaml
   - uses: ./.github/actions/setup-environment
   - uses: ./.github/actions/pip-install
     with:
       packages: 'Pillow'
   ```

2. **Group related packages**: Install related packages together
   ```yaml
   # Good: One action for related packages
   - uses: ./.github/actions/pip-install
     with:
       packages: 'Pillow jsonschema'
   
   # Avoid: Separate actions (creates multiple caches)
   - uses: ./.github/actions/pip-install
     with:
       packages: 'Pillow'
   - uses: ./.github/actions/pip-install
     with:
       packages: 'jsonschema'
   ```

3. **Skip unnecessary installs**: If a workflow doesn't need Python deps, skip them
   ```yaml
   - uses: ./.github/actions/setup-environment
     with:
       install-python-deps: 'false'
   ```

4. **Use cache-key-suffix for multiple installs**: If you need separate caches in one workflow
   ```yaml
   - uses: ./.github/actions/pip-install
     with:
       packages: 'pytest pytest-cov'
       cache-key-suffix: 'testing'
   ```

### For Dependency Management

1. **Pin versions in requirements.txt**: For predictable caching
   ```
   # Good
   Pillow==10.4.0
   jsonschema==4.23.0
   
   # Avoid (cache invalidation on every update)
   Pillow>=10.0.0
   jsonschema
   ```

2. **Separate production and dev dependencies**: Keep requirements-dev.txt separate

3. **Review dependencies regularly**: Remove unused packages to keep caches small

## Troubleshooting

### Cache Not Working

**Symptom**: Packages install slowly every run despite caching being enabled

**Solutions**:
1. Check workflow logs for "Cache hit" or "Cache miss" messages
2. Verify Python version hasn't changed
3. Check if package names match exactly (case-sensitive)
4. Review cache storage in Settings → Actions → Caches

### Cache Too Large

**Symptom**: Caches being evicted frequently

**Solutions**:
1. Review and remove unused dependencies
2. Consider splitting large workflows into smaller ones
3. Use more specific cache keys to avoid storing duplicates

### Unexpected Cache Misses

**Symptom**: Cache should hit but shows miss

**Solutions**:
1. Check if Python version changed (even patch version)
2. Verify package names are sorted correctly (automatic in pip-install)
3. Look for extra whitespace in package names

## Related Documentation

- [Setup Environment Action README](.github/actions/setup-environment/README.md)
- [Pip Install Action README](.github/actions/pip-install/README.md)
- [GitHub Actions Cache Documentation](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [actions/setup-python Documentation](https://github.com/actions/setup-python)

## Future Improvements

Potential enhancements to consider:

1. **Poetry caching optimization**: If switching fully to Poetry, optimize poetry cache
2. **Layer caching for Docker**: If containerizing, implement Docker layer caching
3. **Artifact caching**: Cache generated SVGs across workflow runs (currently using hash cache)
4. **Dependency pre-warming**: Pre-populate caches for new dependencies before first use

## Metrics & Monitoring

To track caching effectiveness over time:

1. **Monitor workflow run times**: Compare before/after optimization
2. **Track cache hit rates**: Review workflow logs monthly
3. **Review GitHub Actions usage**: Check Settings → Billing → Actions usage
4. **Set up alerts**: Create issues for workflows with low cache hit rates

---

**Last Updated**: 2024-12-03  
**Optimization Version**: v1.0  
**Contact**: @szmyty
