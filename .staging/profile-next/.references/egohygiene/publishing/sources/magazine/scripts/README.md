# 🛠 Developer Utilities

This directory contains internal developer utilities used during content
production and quality assurance.  These scripts are **not** part of the
`magazine` package and are not invoked by the CLI.

---

## 🐍 Python Utilities

### `lint_ip_references.py` — IP Reference Lint Check

Scans all edition schema files for references to external intellectual property,
franchises, or licensed universes that must not appear in published assets.

**Usage:**

```bash
python scripts/lint_ip_references.py
```

Exits `0` when no violations are found, or `1` when violations are detected.
This script is also executed automatically by the `ip-lint` CI workflow on every
push and pull request to `main`.

---

### `visual_dna.py` — Visual DNA Propagator

Extracts the canonical visual language (textures, colors, iconography, and
aesthetic tags) from an edition's existing page schemas and audits each page for
adherence to that shared aesthetic identity.

**Usage:**

```bash
python scripts/visual_dna.py <edition_directory>
```

**Example:**

```bash
python scripts/visual_dna.py editions/edition_1
```

Writes a `visual_dna.json` file to the edition directory and prints a
per-page adherence report to stdout.

---

## 🎬 Production Page Build Pipeline

A high-performance shell script designed to transform master artwork and Fountain screenplays into a complete distribution-ready package. This pipeline automates the generation of visual assets, industry-standard screenplay formats (Final Draft, Fade In, OSF), and web-ready previews.

## 🚀 Quick Start

1. **Process a single page:**

    ```bash
    ./scripts/build_page_assets.sh path/to/cover.front.final.png
    ```

2. **Process an entire edition:**

    ```bash
    ./scripts/build_page_assets.sh --all editions/edition_1
    ```

---

## 🛠 Required Dependencies

This script orchestrates several specialized tools. Ensure they are installed and available in your `$PATH`.

### 1. Visual & Image Processing

* **ImageMagick**: Handles JPG, WebP, and TIFF conversion.
* **img2pdf**: Creates high-fidelity, full-bleed PDFs from master PNGs.

    ```bash
    brew install imagemagick img2pdf
    ```

### 2. Screenwriting & Export Suite

* **Afterwriting (CLI)**: The gold standard for Fountain-to-PDF layout.

    ```bash
    npm install -g afterwriting
    ```

* **Scripttool**: Converts Fountain to `.fdx`, `.fadein`, and `.osf`.
  * [Download from GitHub](https://github.com/rsdoiel/scripttool)
* **Wrap**: Modern Fountain-to-HTML/PDF exporter.
  * [Download Wrap](https://github.com/freetimecoder/wrap)
* **jq**: Essential for pretty-printing the generated `screenplay.json`.

    ```bash
    brew install jq
    ```

---

## 🔐 MacOS Permissions (Gatekeeper)

If you download `scripttool` or `wrap` manually, macOS may block them. Use these commands to authorize them via the terminal:

```bash
# Unblock scripttool binary
sudo xattr -d com.apple.quarantine /usr/local/bin/scripttool

# Unblock Wrap application bundle
sudo xattr -rd com.apple.quarantine /Applications/Wrap.app
