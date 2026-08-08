#!/usr/bin/env node
/**
 * build-token-css.mjs
 *
 * Reads the design-system token JSON files and writes
 * src/tokens/tokens.css — a static `:root { }` block containing every
 * CSS custom property derived from those tokens.
 *
 * Run via:  npm run generate-tokens
 * Auto-runs before every build via the `prebuild` npm lifecycle hook.
 *
 * The generated file is the single source of CSS-variable truth for the app.
 * DO NOT edit tokens.css by hand — edit the JSON source files instead and
 * re-run this script.
 */

import { readFileSync, writeFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { join, dirname } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = join(__dirname, '..', '..')
const TOKENS_DIR = join(REPO_ROOT, 'design-system', 'tokens')
const OUTPUT_PATH = join(__dirname, '..', 'src', 'tokens', 'tokens.css')

// ---------------------------------------------------------------------------
// Token flattening (mirrors the logic in src/tokens/index.ts)
// ---------------------------------------------------------------------------

/** Replace `{category.name}` references with `var(--category-name)`. */
function resolveReference(value) {
  return value.replace(/\{([^}]+)\}/g, (_, ref) => {
    const cssVar = '--' + ref.replace(/[._]/g, '-')
    return `var(${cssVar})`
  })
}

/**
 * Recursively walk a W3C design-token object and collect every node that
 * carries a `$value` key.  The resulting CSS custom-property name is built
 * from the key path joined with hyphens (underscores are also converted).
 *
 * Composite border tokens (objects with `width`, `style`, `color`) are
 * serialised as CSS border shorthand.
 */
function flattenTokens(obj, prefix = [], result = {}) {
  for (const [key, value] of Object.entries(obj)) {
    if (key.startsWith('$')) continue

    if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
      if ('$value' in value) {
        const rawValue = value['$value']
        if (rawValue === null || rawValue === undefined) continue

        const cssVarName = '--' + [...prefix, key].join('-').replace(/_/g, '-')

        if (typeof rawValue === 'object' && !Array.isArray(rawValue)) {
          // Composite border token: { width, style, color }
          if ('width' in rawValue && 'style' in rawValue && 'color' in rawValue) {
            const color = resolveReference(String(rawValue.color))
            result[cssVarName] = `${rawValue.width} ${rawValue.style} ${color}`
          }
        } else {
          result[cssVarName] = resolveReference(String(rawValue))
        }
      } else {
        flattenTokens(value, [...prefix, key], result)
      }
    }
  }
  return result
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const TOKEN_FILES = ['colors.json', 'spacing.json', 'typography.json', 'borders.json']

const allVars = {}
for (const file of TOKEN_FILES) {
  const json = JSON.parse(readFileSync(join(TOKENS_DIR, file), 'utf-8'))
  Object.assign(allVars, flattenTokens(json))
}

const lines = [
  '/* generated — do not edit; run `npm run generate-tokens` to regenerate */',
  ':root {',
  ...Object.entries(allVars).map(([name, value]) => `  ${name}: ${value};`),
  '}',
  '',
]

writeFileSync(OUTPUT_PATH, lines.join('\n'), 'utf-8')
console.log(`✓ Wrote ${Object.keys(allVars).length} CSS variables to ${OUTPUT_PATH}`)
