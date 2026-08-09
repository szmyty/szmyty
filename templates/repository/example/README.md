# widget-factory

> A library for building composable UI widgets in Python.

[![CI](https://img.shields.io/github/actions/workflow/status/example-org/widget-factory/ci.yml?style=flat-square&label=CI)](https://github.com/example-org/widget-factory/actions)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

---

## Overview

**widget-factory** is a Python library that provides a small, composable set
of UI widget primitives for terminal applications.  It targets developers who
want declarative layout without pulling in a full TUI framework.

---

## Table of contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Requirements

- Python ≥ 3.11

---

## Installation

```sh
pip install widget-factory
```

---

## Usage

```sh
# List available widget types
python -m widget_factory --list
```

```sh
# Run a demo layout
python -m widget_factory demo --theme dark
```

---

## Configuration

| Variable / Flag | Default | Description |
|-----------------|---------|-------------|
| `WF_THEME` | `light` | Colour theme (`light` or `dark`) |
| `WF_WIDTH` | `80` | Default terminal width in columns |

---

## Contributing

Contributions are welcome.
Please read [CONTRIBUTING](CONTRIBUTING.md) before opening a pull request.

This project follows standard open-source conventions:
1. Fork the repository.
2. Create a feature branch.
3. Open a pull request against `main`.

---

## License

Distributed under the **MIT** license.
See [LICENSE](LICENSE) for the full text.

---

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

[CONTRIBUTING]: CONTRIBUTING.md
[docs]: https://widget-factory.readthedocs.io
