# Install Python Packages with Caching

A composite action that installs Python packages using pip with optimized caching. This action creates a cache key based on the specific packages being installed, allowing for efficient reuse across workflow runs.

## Features

- **Smart Caching**: Generates cache keys based on package names and Python version
- **Cache Reuse**: Shares cached packages across workflows with the same dependencies
- **Fast Installation**: Significantly reduces pip install time on cache hits
- **Transparent**: Shows cache hit/miss status in workflow logs

## Usage

### Basic Usage

Install a single package:

```yaml
steps:
  - name: Install Pillow
    uses: ./.github/actions/pip-install
    with:
      packages: 'Pillow'
```

### Multiple Packages

Install multiple packages with a single action:

```yaml
steps:
  - name: Install dependencies
    uses: ./.github/actions/pip-install
    with:
      packages: 'Pillow jsonschema pytest'
```

### With Cache Key Suffix

Use a cache key suffix when you need separate caches in the same workflow:

```yaml
steps:
  - name: Install testing dependencies
    uses: ./.github/actions/pip-install
    with:
      packages: 'pytest pytest-cov'
      cache-key-suffix: 'testing'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `packages` | Space-separated list of Python packages to install | Yes | - |
| `cache-key-suffix` | Optional suffix for cache key (for multiple caches per workflow) | No | `''` |

## How It Works

1. **Package Normalization**: Packages are sorted alphabetically to ensure consistent cache keys regardless of input order
2. **Hash Generation**: Creates an 8-character hash of the package list
3. **Cache Key**: Combines OS, Python version, and package hash: `pip-packages-{os}-py{version}-{hash}`
4. **Cache Lookup**: Checks if cached packages exist
5. **Installation**: Installs packages (uses cache if available)

## Cache Key Structure

The cache key is constructed as:

```
pip-packages-{runner.os}-py{python-version}-{package-hash}[-{suffix}]
```

Examples:
- `pip-packages-Linux-py3.11-a1b2c3d4`
- `pip-packages-Linux-py3.11-a1b2c3d4-testing`

## Performance Benefits

### Without Caching
- Typical pip install time: 10-30 seconds per package
- Downloads packages every workflow run
- Increases GitHub Actions usage

### With Caching
- Cache hit install time: 1-3 seconds
- Reuses previously downloaded packages
- Reduces GitHub Actions usage significantly

## Examples

### Workflow Integration

Replace manual pip install commands with the cached action:

**Before:**
```yaml
- name: Install additional dependencies
  run: |
    pip install Pillow
```

**After:**
```yaml
- name: Install additional dependencies
  uses: ./.github/actions/pip-install
  with:
    packages: 'Pillow'
```

### Multiple Workflows Sharing Cache

When multiple workflows install the same packages, they automatically share the cache:

**developer.yml:**
```yaml
- name: Install dependencies
  uses: ./.github/actions/pip-install
  with:
    packages: 'jsonschema'
```

**location-card.yml:**
```yaml
- name: Install dependencies
  uses: ./.github/actions/pip-install
  with:
    packages: 'Pillow'
```

Both workflows benefit from independent caches based on their specific package needs.

## Cache Management

### Cache Invalidation

Caches are automatically invalidated when:
- Python version changes
- Package list changes (different packages or order after sorting)
- OS changes

### Cache Retention

GitHub Actions caches are:
- Retained for up to 7 days of inactivity
- Automatically cleaned up to maintain 10GB limit
- Scoped to the repository

## Best Practices

1. **Group Related Packages**: Install related packages together to maximize cache reuse
2. **Use in Composite Actions**: Integrate into setup steps for consistency
3. **Monitor Cache Usage**: Check workflow logs for cache hit rates
4. **Version Pinning**: Consider pinning package versions in requirements.txt for more predictable caching

## Comparison with setup-python Caching

This action complements `actions/setup-python`'s cache feature:

| Feature | setup-python cache | pip-install action |
|---------|-------------------|-------------------|
| Scope | requirements.txt, pyproject.toml | Individual packages |
| Use Case | Base dependencies | Additional/optional packages |
| Cache Key | Based on requirements file hash | Based on package names |
| Best For | Project-wide dependencies | Workflow-specific packages |

## Troubleshooting

### Cache Not Working

If caching doesn't seem to work:

1. Check that Python is installed before using this action
2. Verify package names are spelled correctly
3. Look for cache hit/miss messages in workflow logs
4. Check GitHub Actions cache storage (Settings → Actions → Caches)

### Packages Not Found

If installed packages are not available in subsequent steps:

1. Ensure the action completes successfully
2. Check that you're using the same runner for all steps
3. Verify package names are correct

## Related Actions

- `.github/actions/setup-environment` - Sets up Python and base dependencies
- `actions/cache@v4` - GitHub's caching action (used internally)
- `actions/setup-python@v5` - Python setup with built-in pip caching
