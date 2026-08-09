# Template Kit

Reusable README starter kits for GitHub repositories and profiles.
Extract only the layer you need — repository or profile — and adapt it
to your project without reading the historical `.staging` tree.

## Structure

```
templates/
  README.md          ← this file
  manifest.yml       ← extraction manifest
  validate_template.py  ← validator script
  repository/
    README.md        ← universal repository README template
    ADAPTATION.md    ← step-by-step adaptation guide
    example/
      README.md      ← rendered generic example
  profile/
    README.md        ← profile-layer README template
    ADAPTATION.md    ← profile adaptation guide
    example/
      README.md      ← rendered generic profile example
```

## Quick start

### Repository README

1. Copy `templates/repository/README.md` to your repository root.
2. Replace every `{{TOKEN}}` placeholder (see `repository/ADAPTATION.md`).
3. Remove optional sections you do not need.
4. Run the validator:

   ```sh
   python templates/validate_template.py templates/repository/example/README.md
   ```

### Profile README

1. Copy `templates/profile/README.md` to your `<username>/<username>` repo.
2. Replace every `{{TOKEN}}` placeholder (see `profile/ADAPTATION.md`).
3. Run the validator:

   ```sh
   python templates/validate_template.py templates/profile/example/README.md
   ```

## Validator

`validate_template.py` checks:

| Rule | Description |
|------|-------------|
| Unresolved tokens | Fails when any `{{TOKEN}}` is still present |
| Single H1 | Exactly one top-level heading is required |
| Heading order | Headings must not skip levels |
| Generated regions | `<!-- BEGIN:name -->` / `<!-- END:name -->` markers must be balanced |
| Duplicate anchors | Two headings must not produce the same GitHub anchor |
| Empty links | `[text]()` and `[](url)` are rejected |
| Empty alt text | `![](url)` without alt text is rejected |
| Byte budget | README must be ≤ 500 KB |
| Personal identifiers | Universal template must contain no Alan-specific data |

## Manifest

`manifest.yml` lists which files are safe to copy into any repository
(`include`) and which personal files must never be included (`exclude`).
See `manifest.yml` for the full list.
