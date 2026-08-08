# Community Theme Library

This vault vendors a small set of community themes directly into
`.obsidian/themes/` so they can be selected from Obsidian without cloning
upstream repositories into the vault.

Only the runtime assets required by Obsidian are kept in each theme directory:

- `theme.css`
- `manifest.json`
- `LICENSE`

## Included themes

| Theme | Style | Modes | Source | License |
| ----- | ----- | ----- | ------ | ------- |
| Minimal | Clean default with strong Style Settings support | Light / Dark | [kepano/obsidian-minimal](https://github.com/kepano/obsidian-minimal) | Included in `Minimal/LICENSE` |
| Tokyo Night | High-contrast editor-focused palette | Light / Dark | [tcmmichaelb139/obsidian-tokyonight](https://github.com/tcmmichaelb139/obsidian-tokyonight) | Included in `Tokyo Night/LICENSE` |
| AnuPpuccin | Rich Catppuccin-inspired theme with deep customization | Light / Dark | [AnubisNekhet/AnuPpuccin](https://github.com/AnubisNekhet/AnuPpuccin) | Included in `AnuPpuccin/LICENSE` |

## Using the library

1. Open **Settings**.
2. Go to **Appearance → Themes**.
3. Choose one of the bundled themes from the dropdown.

The vault defaults to **Minimal** via `.obsidian/appearance.json`, but all
bundled themes can be switched instantly from the Obsidian UI.

## Maintenance notes

- Theme assets were vendored from upstream GitHub repositories without copying
  `.git/`, workflows, or other repository metadata.
- Update a theme by replacing the three vendored files from its upstream source.
- Keep directory names aligned with each theme's `manifest.json` `name` field.
