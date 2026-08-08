# Components

This directory contains the visual component system for the multi-project publishing platform.

## Structure

```
components/
  global/          # Reusable components shared across all projects
  project/         # Project-scoped components
    <project>/
      <edition>/
        <component>/
          component.json   # Component metadata and layer manifest
          preview.png      # Visual preview placeholder
          layers/          # Photoshop-style layer system
            background/
            border/
            content/
```

## Global Components

Components in `global/` are reusable across all projects and editions:

- `ornamental-divider/` — Decorative divider elements
- `typography/` — Typography system components
- `frames/` — Frame and border components

## Project Components

Components in `project/` are scoped to a specific project and edition:

- `egohygiene/edition_1/` — Components for Egohygiene Edition 1
- `forever-and-always/issue_1/` — Components for Forever and Always Issue 1

## Layer System

Each component follows a Photoshop-style layer model. The `layers/` directory
contains named sub-directories corresponding to individual design layers.

## Adding a New Component

1. Create a directory under the appropriate `global/` or `project/<project>/<edition>/` path
2. Add a `component.json` with metadata
3. Add a `preview.png` placeholder
4. Scaffold `layers/` sub-directories as needed, each with a `.gitkeep`
