# Setup Environment Composite Action

This composite action consolidates common setup steps used across all GitHub workflows in this repository. It eliminates duplication and ensures consistency in how the development environment is configured.

## Features

- **Repository Checkout**: Clones the repository with minimal fetch depth for performance
- **Python Setup**: Configures Python with the specified version
- **Python Virtual Environment**: Creates an isolated `.venv` directory for all Python packages
- **Pip Caching**: Automatically caches pip dependencies for faster builds
- **System Dependencies**: Installs required system packages (jq, curl, etc.)
- **Python Dependencies**: Optionally installs Python packages from requirements.txt or Poetry

## Usage

### Basic Usage

```yaml
steps:
  - name: Setup environment
    uses: ./.github/actions/setup-environment
```

This will:
- Checkout the repository
- Set up Python 3.11 (default)
- Install jq and curl
- Install Python dependencies from requirements.txt
- Enable pip caching

### Custom Python Version

```yaml
steps:
  - name: Setup environment
    uses: ./.github/actions/setup-environment
    with:
      python-version: '3.12'
```

### Skip Python Dependencies Installation

For workflows that only need shell scripts and don't require Python packages:

```yaml
steps:
  - name: Setup environment
    uses: ./.github/actions/setup-environment
    with:
      install-python-deps: 'false'
```

### Skip System Tools

If you don't need jq or curl:

```yaml
steps:
  - name: Setup environment
    uses: ./.github/actions/setup-environment
    with:
      install-jq: 'false'
      install-curl: 'false'
```

### Install Additional System Packages

```yaml
steps:
  - name: Setup environment
    uses: ./.github/actions/setup-environment
    with:
      extra-apt-packages: 'imagemagick libpq-dev'
```

### Combined Example

```yaml
steps:
  - name: Setup environment
    uses: ./.github/actions/setup-environment
    with:
      python-version: '3.12'
      install-python-deps: 'false'
      install-jq: 'true'
      install-curl: 'true'
      extra-apt-packages: 'nodejs npm'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `python-version` | Python version to use | No | `3.11` |
| `install-jq` | Install jq JSON processor | No | `true` |
| `install-curl` | Install curl HTTP client | No | `true` |
| `install-python-deps` | Install Python dependencies from requirements.txt | No | `true` |
| `extra-apt-packages` | Additional apt packages to install (space-separated) | No | `''` |

## Performance Optimizations

1. **Python Virtual Environment**: All Python dependencies are installed in an isolated `.venv` directory, preventing conflicts with system packages and ensuring PEP 668 compliance (Python 3.12+)
2. **Pip Caching**: Uses `actions/setup-python@v5` with built-in pip caching, which significantly speeds up workflow runs by caching installed packages based on requirements file hashes
3. **Shallow Clone**: Uses `fetch-depth: 1` for faster repository checkout
4. **Conditional Installation**: Only installs requested system packages
5. **Smart Dependency Detection**: Automatically detects and uses Poetry or pip based on project structure

For additional package caching beyond base requirements, see the [pip-install action](../pip-install/README.md).

## Notes

- All scripts in the `scripts/` directory already have execute permissions in the repository, so there's no need to run `chmod +x` on them in workflows
- The action uses pinned SHA versions for GitHub actions for security
- System packages are only installed if explicitly requested to minimize installation time
- Python packages are installed in an isolated virtual environment (`.venv`), which is automatically activated for subsequent workflow steps
- The virtual environment approach ensures compatibility with Python 3.12+ and prevents PEP 668 "externally managed environment" errors
- Works seamlessly with both GitHub Actions runners and local `act` execution

## Migration Guide

### Before (duplicated steps)

```yaml
steps:
  - name: Checkout repository
    uses: actions/checkout@v4

  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: '3.11'
      cache: 'pip'

  - name: Install system dependencies
    run: |
      sudo apt-get update
      sudo apt-get install -y jq curl

  - name: Install Python dependencies
    run: |
      pip install -r requirements.txt

  - name: Make script executable
    run: chmod +x scripts/fetch-data.sh
```

### After (using composite action)

```yaml
steps:
  - name: Setup environment
    uses: ./.github/actions/setup-environment
```

The `chmod +x` step is no longer needed as scripts are already executable in the repository.
