# Python Caching Quick Reference

Quick reference guide for using the Python dependency caching system in GitHub Actions workflows.

## TL;DR

Use the `pip-install` action to install Python packages with automatic caching:

```yaml
- name: Install dependencies
  uses: ./.github/actions/pip-install
  with:
    packages: 'Pillow jsonschema'
```

**Benefits**: 60-75% faster than uncached pip install, automatically shares cache across workflows.

## Common Usage Patterns

### Single Package

```yaml
steps:
  - name: Setup environment
    uses: ./.github/actions/setup-environment
    
  - name: Install Pillow
    uses: ./.github/actions/pip-install
    with:
      packages: 'Pillow'
```

### Multiple Packages

```yaml
- name: Install dependencies
  uses: ./.github/actions/pip-install
  with:
    packages: 'Pillow jsonschema pytest'
```

### Skip Base Dependencies

For workflows that don't need requirements.txt:

```yaml
- name: Setup environment
  uses: ./.github/actions/setup-environment
  with:
    install-python-deps: 'false'
```

## Cache Key Structure

Caches are keyed by:
- Operating system (Linux, macOS, Windows)
- Python version (e.g., 3.11.9)
- Package list hash (8 characters)

Example: `pip-packages-Linux-py3.11.9-a1b2c3d4`

## Checking Cache Status

Look for these messages in workflow logs:

```
✓ Cache hit for packages: Pillow jsonschema
  → Fast install (1-3 seconds)

✗ Cache miss for packages: Pillow jsonschema
  → Full install and cache (10-20 seconds)
```

## When Caches Invalidate

Automatic cache invalidation occurs when:

| Change | Cache Invalidated? | Recovery |
|--------|-------------------|----------|
| Python patch version update (3.11.8 → 3.11.9) | ✅ Yes | 1 run |
| Different packages requested | ✅ Yes | 1 run |
| Same packages, different order | ❌ No | N/A |
| requirements.txt updated | ✅ Yes (base deps) | 1 run |
| 7 days since last use | ✅ Yes | 1 run |

## Comparing Approaches

| Method | When to Use | Cache Key | Speed |
|--------|-------------|-----------|-------|
| `setup-environment` | Base dependencies (requirements.txt) | File hash | Fast (5-8s) |
| `pip-install` | Additional workflow packages | Package names | Very Fast (1-3s) |
| Manual `pip install` | Never (use actions above) | None | Slow (10-30s) |

## Troubleshooting

### Slow Install Despite Caching

Check workflow logs for cache miss. Common causes:
- First run after Python version update → Expected
- First run after package change → Expected
- Cache expired (7 days) → Expected

### Want Separate Caches in One Workflow

Use `cache-key-suffix`:

```yaml
- name: Install test deps
  uses: ./.github/actions/pip-install
  with:
    packages: 'pytest pytest-cov'
    cache-key-suffix: 'testing'

- name: Install lint deps
  uses: ./.github/actions/pip-install
  with:
    packages: 'black flake8'
    cache-key-suffix: 'linting'
```

## Best Practices

✅ **Do**:
- Use `pip-install` for all additional packages
- Group related packages in one action call
- Pin package versions in requirements.txt

❌ **Don't**:
- Call multiple pip-install actions with same packages
- Use manual `pip install` in workflows
- Mix cached and uncached approaches

## Performance Examples

### Before (Manual pip install)
```yaml
- name: Install dependencies
  run: pip install Pillow  # 12-18 seconds
```

### After (Cached pip-install)
```yaml
- name: Install dependencies
  uses: ./.github/actions/pip-install
  with:
    packages: 'Pillow'  # 1-3 seconds (cache hit)
```

**Time saved**: ~10-15 seconds per run

## See Also

- [Complete Caching Guide](WORKFLOW_CACHING.md) - Full documentation
- [Benchmark Results](CACHING_BENCHMARKS.md) - Performance measurements
- [Setup Environment Action](../.github/actions/setup-environment/README.md)
- [Pip Install Action](../.github/actions/pip-install/README.md)

---

**Quick Links**:
- View caches: Settings → Actions → Caches
- Monitor workflows: Actions tab
- Report issues: Create an issue with `caching` label
