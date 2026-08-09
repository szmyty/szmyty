# {{PROJECT_NAME}}

> {{PROJECT_DESCRIPTION}}

<!-- BEGIN:badge-row -->
<!-- OPTIONAL BLOCK — remove this entire block if you do not use CI/coverage badges -->
[![CI](https://img.shields.io/github/actions/workflow/status/{{OWNER}}/{{REPO}}/{{BADGE_CI_WORKFLOW}}?style=flat-square&label=CI)](https://github.com/{{OWNER}}/{{REPO}}/actions)
[![License](https://img.shields.io/badge/license-{{LICENSE_SPDX}}-blue?style=flat-square)](LICENSE)
<!-- END:badge-row -->

---

## Overview

<!-- Replace this paragraph with 2–4 sentences describing what the project does,
     who it is for, and why it exists.  Keep it jargon-free. -->

{{PROJECT_NAME}} is a **{{LANGUAGE_OR_STACK}}** project that …

---

## Table of contents

<!-- BEGIN:toc -->
<!-- This region is regenerated automatically by doctoc — do not edit manually -->
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
<!-- END:toc -->

---

## Requirements

<!-- List runtime prerequisites (language version, OS constraints, external services). -->

- {{LANGUAGE_OR_STACK}} ≥ …
- …

---

## Installation

<!-- OPTIONAL BLOCK: package-manager-install — remove if project is not a library -->
<!-- BEGIN:package-manager-install -->
```sh
{{PACKAGE_MANAGER_INSTALL}}
```
<!-- END:package-manager-install -->

For a full development setup, see [CONTRIBUTING][] or the [docs][].

---

## Usage

<!-- Provide the shortest possible example that demonstrates value.
     Add a second example for the most common advanced case. -->

```sh
# Basic usage
{{PROJECT_NAME}} --help
```

<!-- OPTIONAL BLOCK: extended-example — remove if a single snippet is enough -->
<!-- BEGIN:extended-example -->
```sh
# Extended example
{{PROJECT_NAME}} run --config config.yml
```
<!-- END:extended-example -->

---

## Configuration

<!-- Document environment variables, config file keys, or flags.
     A table is preferred when there are more than three options. -->

| Variable / Flag | Default | Description |
|-----------------|---------|-------------|
| `CONFIG_PATH`   | `./config.yml` | Path to the configuration file |

---

## Contributing

Contributions are welcome.
<!-- OPTIONAL BLOCK: contributing-link — remove if there is no CONTRIBUTING guide yet -->
<!-- BEGIN:contributing-link -->
Please read [CONTRIBUTING][] before opening a pull request.
<!-- END:contributing-link -->

This project follows standard open-source conventions:
1. Fork the repository.
2. Create a feature branch.
3. Open a pull request against `main`.

---

## License

Distributed under the **{{LICENSE_SPDX}}** license.
See [LICENSE](LICENSE) for the full text.

---

<!-- BEGIN:contributors -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- END:contributors -->

<!-- Reference-style links — keep at the bottom -->
[CONTRIBUTING]: {{CONTRIBUTING_GUIDE_URL}}
[docs]: {{DOCS_URL}}
