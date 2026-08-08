# IP Reference Lint Check

## Purpose

The IP Reference Lint Check automatically prevents references to external intellectual property (e.g., named games, movies, franchises) from appearing in Ego Hygiene schemas and other canonical files.

This exists to:

- Preserve Ego Hygiene as a first-principles system
- Avoid accidental attribution of authority to external IP
- Reduce future stress and manual review
- Create a behavioral boundary for AI coding assistants

## How It Works

The lint check:

- Scans all page schema files (`*.page.json`) and edition metadata files (`meta.json`)
- Searches for forbidden terms using case-insensitive matching
- Flags any occurrences with file name, line number, and context
- Fails CI if any forbidden terms are found
- Runs automatically on pull requests and pushes to main

## Forbidden Terms

The current list of forbidden terms includes:

- `fallout` - Reference to the Fallout game franchise

This list can be expanded by editing the `FORBIDDEN_TERMS` list in `lint_ip_references.py`.

## Allowed Aesthetic Language

Instead of IP references, schemas should use neutral aesthetic descriptors:

### Acceptable Descriptor Categories

- **Retro print**: aged paper, weathered artifact, vintage print
- **Distressed elements**: worn ink, scuffed edges, battered surfaces
- **Analog textures**: grain, organic imperfections
- **Field manual tone**: instructional, utilitarian, practical
- **Mystic symbolism**: spiritual geometry, esoteric patterns
- **Post-collapse aesthetic**: weathered, salvaged, repurposed

### Example Replacements

- ❌ `fallout_retro_mystic` → ✅ `post_collapse_retro_mystic`
- ❌ Reference to specific game studios → ✅ `analog_retro_aesthetic`
- ❌ Named universes → ✅ Descriptive visual qualities

## Running the Check Locally

```bash
python3 lint_ip_references.py
```

If violations are found, the script will:

1. List each file with violations
2. Show the line number and forbidden term
3. Display a snippet of the offending line
4. Exit with status code 1

## Adding New Forbidden Terms

1. Edit `lint_ip_references.py`
2. Add new terms to the `FORBIDDEN_TERMS` list
3. Terms are case-insensitive (e.g., "Fallout" matches "fallout")
4. Commit and push - CI will enforce the new rules

## Relationship to Copilot

This lint check acts as a behavioral boundary:

- Copilot suggestions containing forbidden IP terms will fail CI
- Over time, Copilot adapts to the allowed vocabulary
- The system enforces the rule automatically, not relying on manual review

This reduces cognitive load and prevents repeated manual corrections.

## Design Principles

- **Simple and transparent**: Rules are explicit and easy to understand
- **Editable**: The forbidden terms list can be updated as needed
- **Automatic enforcement**: Runs in CI, not reliant on memory
- **Stress reduction**: Prevents issues before they're merged

## Files Checked

The lint check scans:

- All `*.page.json` files in the repository
- All `meta.json` files in edition directories
- Any future canonical machine-readable source files

The check does NOT apply to:

- Draft notes or brainstorm files
- Commit history
- Generated images
- Documentation (unless it contains schema definitions)

## CI Integration

The check runs via GitHub Actions (`.github/workflows/ip-lint.yml`):

- Triggers on pull requests to main
- Triggers on pushes to main
- Uses Python 3.x
- Fails the workflow if violations are found

This ensures that all merged code maintains the IP-free standard.
