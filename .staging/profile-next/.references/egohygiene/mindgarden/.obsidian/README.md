# Garden — Obsidian Configuration

This directory contains the Obsidian vault configuration for the Mind Garden.
It is committed to version control to provide a reproducible, opinionated
starter environment for knowledge management.

## Plugin Selection Rationale

### Tier 1 — Core Workflow (Essential)

These plugins form the backbone of the knowledge management system.
Every vault should have them.

#### [Dataview](https://github.com/blacksmithgu/obsidian-dataview)

**Category:** Querying & Dashboards

Dataview is the single most important community plugin for Obsidian.
It enables SQL-like queries over the vault, turning front-matter and
inline fields into queryable data. All dashboards in this vault depend on
Dataview. Without it, the `Home`, `Capture`, and `Current Focus` dashboards
are non-functional.

#### [Templater](https://github.com/SilentVoid13/Templater)

**Category:** Automation & Templates

Templater replaces the built-in core templates plugin with a far more
capable system. It supports dynamic date/time insertion, file manipulation,
user scripts, and conditional logic. All templates in `templates/` use
Templater syntax (`<% tp.* %>`).

The core `templates` plugin is intentionally **disabled** — Templater is
strictly superior and the two can conflict.

#### [Calendar](https://github.com/liamcain/obsidian-calendar-plugin)

**Category:** Navigation

A calendar sidebar widget that shows dots for days with notes and allows
one-click navigation to daily notes. Works with Periodic Notes for
weekly note navigation.

#### [Periodic Notes](https://github.com/liamcain/obsidian-periodic-notes)

**Category:** Journaling

Enables daily, weekly, and monthly notes with configurable folder
locations and templates. Supersedes the built-in daily-notes core plugin,
which is therefore **disabled**.

Configured paths:
- Daily notes → `journal/daily/YYYY-MM-DD`
- Weekly notes → `journal/weekly/YYYY-[W]WW`
- Monthly notes → `journal/monthly/YYYY-MM`

#### [Tasks](https://github.com/obsidian-tasks-group/obsidian-tasks)

**Category:** Task Management

Provides rich task management with due dates, recurrence, priorities,
and query-based task views. Tasks can be queried globally across the vault.
Pairs well with Dataview for custom task dashboards.

#### [Obsidian Git](https://github.com/denolehov/obsidian-git)

**Category:** Version Control & Sync

Automates git commits on a configurable interval. Configured with a
10-minute auto-save interval. This enables the vault to sync with the
Sanctuary repository without manual intervention.

Commit message format: `vault: YYYY-MM-DD HH:mm:ss`

#### [Omnisearch](https://github.com/scambier/obsidian-omnisearch)

**Category:** Search

Replaces the built-in search with a fuzzy, semantic-style search that
returns ranked results with context excerpts. Dramatically improves
note discoverability compared to the core search plugin.

---

### Tier 2 — Knowledge Management

These plugins extend core knowledge management capabilities.

#### [Advanced Tables](https://github.com/tgrosinger/advanced-tables-obsidian)

**Category:** Editing

Makes Markdown table editing bearable. Provides automatic column
alignment, tab-to-next-cell navigation, and formula support.
Essential for any vault that uses tables for structured data.

#### [Excalidraw](https://github.com/zsviczian/obsidian-excalidraw-plugin)

**Category:** Visual Thinking & Diagrams

Embeds a full Excalidraw drawing canvas inside Obsidian notes.
Used for system diagrams, concept maps, sketchnotes, and visual
explanations. Drawings are auto-exported as SVG for portability.

Drawings are stored in `assets/excalidraw/`.

#### [Mind Map](https://github.com/lynchjames/obsidian-mind-map)

**Category:** Visualization

Renders any note as a mind map based on its heading structure.
Useful for quickly visualising the structure of a note or concept.
Zero configuration required.

#### [Citations](https://github.com/hans/obsidian-citation-plugin)

**Category:** Academic / Bibliography

Integrates with Zotero (and other reference managers that export
BibTeX) to create structured literature notes. Each reference
generates a note in `research/references/` using a configurable template.

To activate: export your Zotero library to a BibTeX file and set
the `citationExportPath` in the plugin settings.

#### [Longform](https://github.com/kevboh/longform)

**Category:** Long-form Writing

Supports multi-scene writing projects (articles, essays, reports).
Provides a dedicated sidebar for managing scenes/sections and
compiling them into a single document. Used for `content/` writing projects.

---

### Tier 3 — Interface & Experience

These plugins improve the daily user experience.

#### [Homepage](https://github.com/mirnovov/obsidian-homepage)

**Category:** Navigation

Opens `dashboards/Home` automatically when Obsidian starts.
Prevents the vault from opening to the last active note on restart,
ensuring a consistent starting point.

#### [Style Settings](https://github.com/mgmeyers/obsidian-style-settings)

**Category:** Appearance

Exposes theme-specific CSS variables as a settings panel. Required to
configure the recommended Minimal theme's typography, font size,
and layout options without writing CSS manually.

#### [Kanban](https://github.com/mgmeyers/obsidian-kanban)

**Category:** Project Management

Creates Markdown-based Kanban boards for visual project tracking.
Board state is stored as plain Markdown, ensuring portability.
Useful for sprint planning and project status tracking.

#### [Commander](https://github.com/phibr0/obsidian-commander)

**Category:** UI Customization

Adds custom commands to the ribbon, status bar, title bar, and
context menus. Used to surface "Open Daily Note" and "Open Home"
as ribbon buttons for faster access.

---

### Tier 4 — Visualization & Data

#### [Charts](https://github.com/phibr0/obsidian-charts)

**Category:** Data Visualization

Renders Chart.js charts from inline YAML or JSON data blocks.
Useful for visualizing health metrics, project progress, or any
tabular data you want to chart.

---

## Bundled Theme Library

The vault is configured to use the **Minimal** theme by default
(`cssTheme: "Minimal"` in `appearance.json`), but it also vendors a curated
set of additional community themes in `.obsidian/themes/`.

See [`.obsidian/themes/README.md`](themes/README.md) for the full catalog,
licensing, and maintenance notes.

| Theme | Why it is included |
| ----- | ------------------ |
| Minimal | Default theme; best integration with Style Settings |
| Tokyo Night | Distinct editor-centric palette for dark-mode workflows |
| AnuPpuccin | Rich customization surface for experimentation |

Switch themes via: `Settings → Appearance → Themes`

## Bundled CSS Snippets

The vault also includes a curated CSS snippet library in
`.obsidian/snippets/`, sourced from Awesome Obsidian and organized in
[`.obsidian/snippets/README.md`](snippets/README.md).

Enable snippets via: `Settings → Appearance → CSS snippets`

---

## Excluded Plugins & Rationale

| Plugin | Reason Excluded |
| ------ | --------------- |
| Wikidata | Too specialized; adds complexity without general utility |
| Oura | Device-specific integration; better handled outside the vault |
| Calibre | Requires desktop app integration; limited general utility |
| Terminal | Security risk; terminal access inside Obsidian is unsafe |
| Hidden Folder Access | Security concern; bypasses OS-level access controls |
| CSS Editor | Replaced by Style Settings + theme customization |
| Importer | One-time use migration tool; not part of ongoing workflow |
| Claudian | Specialized AI integration; AI features handled externally |
| Core daily-notes | Superseded by Periodic Notes |
| Core templates | Superseded by Templater |

---

## Graph View

The graph is configured with color groups:

| Color | Tag |
| ----- | --- |
| 🟠 Orange | `#dashboard` |
| 🟣 Purple | `#moc` |
| 🟢 Green | `#project` |
| 🔴 Red | `#journal` / `#daily` |
| 🔵 Blue | `#concept` |
| 🟡 Yellow | `#research` |

---

## Hotkeys

| Hotkey | Action |
| ------ | ------ |
| `Alt+D` | Open today's daily note |
| `Alt+W` | Open this week's note |
| `Alt+E` | Insert Templater template |
| `Alt+N` | Create new note from template |
| `Alt+X` | Create new Excalidraw drawing |
| `Alt+K` | Create new Kanban board |
| `Alt+M` | Open note as mind map |
| `Cmd+F` | Omnisearch in-file |
| `Cmd+Shift+F` | Omnisearch vault-wide |
| `Cmd+Enter` | Toggle task done |
| `Cmd+Shift+T` | Edit task details |
