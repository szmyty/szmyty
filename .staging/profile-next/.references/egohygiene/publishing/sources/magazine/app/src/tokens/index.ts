import colorsJson from '../../../design-system/tokens/colors.json'
import spacingJson from '../../../design-system/tokens/spacing.json'
import typographyJson from '../../../design-system/tokens/typography.json'
import bordersJson from '../../../design-system/tokens/borders.json'

type JsonPrimitive = string | number | boolean | null
type JsonObject = { [key: string]: JsonValue }
type JsonValue = JsonPrimitive | JsonObject | JsonValue[]

/**
 * Resolve design-token references like `{color.burnt_orange}` to the
 * corresponding CSS custom property: `var(--color-burnt-orange)`.
 */
function resolveReference(value: string): string {
  return value.replace(/\{([^}]+)\}/g, (_, ref: string) => {
    const cssVar = '--' + ref.replace(/[._]/g, '-')
    return `var(${cssVar})`
  })
}

/**
 * Recursively walk a token object and collect every node that has a `$value`
 * key, mapping it to a CSS custom property name derived from the key path.
 *
 * - Object values with `width` + `style` + `color` fields are composed into
 *   a CSS border shorthand (e.g. `1px solid var(--color-charcoal)`).
 * - Token references (`{category.name}`) are replaced with `var(--…)`.
 * - Keys starting with `$` (meta fields) are skipped.
 * - Underscores in key names are converted to hyphens.
 */
function flattenTokens(
  obj: JsonObject,
  prefix: string[] = [],
  result: Record<string, string> = {},
): Record<string, string> {
  for (const [key, value] of Object.entries(obj)) {
    if (key.startsWith('$')) continue

    if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
      const node = value as JsonObject

      if ('$value' in node) {
        const rawValue = node['$value']
        if (rawValue === null || rawValue === undefined) continue

        const cssVarName =
          '--' + [...prefix, key].join('-').replace(/_/g, '-')

        if (typeof rawValue === 'object' && !Array.isArray(rawValue)) {
          // Composite border token: { width, style, color }
          const rv = rawValue as JsonObject
          if ('width' in rv && 'style' in rv && 'color' in rv) {
            const color = resolveReference(String(rv['color']))
            result[cssVarName] =
              `${String(rv['width'])} ${String(rv['style'])} ${color}`
          }
        } else {
          result[cssVarName] = resolveReference(String(rawValue))
        }
      } else {
        flattenTokens(node, [...prefix, key], result)
      }
    }
  }
  return result
}

/**
 * Build a flat map of all CSS custom properties derived from the
 * design-system token files.
 *
 * Variable names follow the pattern `--<category>-<...path>`, e.g.:
 *   --color-burnt-orange, --spacing-4, --font-size-md, --border-width-thin
 *
 * The result is memoized — token JSON is static at build time so there is no
 * need to re-flatten on every call.
 */
let _tokenVarsCache: Record<string, string> | null = null

export function buildTokenVars(): Record<string, string> {
  if (_tokenVarsCache !== null) return _tokenVarsCache
  _tokenVarsCache = {
    ...flattenTokens(colorsJson as unknown as JsonObject),
    ...flattenTokens(spacingJson as unknown as JsonObject),
    ...flattenTokens(typographyJson as unknown as JsonObject),
    ...flattenTokens(bordersJson as unknown as JsonObject),
  }
  return _tokenVarsCache
}

/**
 * Apply all design-system tokens as CSS custom properties on `:root`.
 * Call once at application startup before the first render.
 */
export function applyTokens(): void {
  const root = document.documentElement
  const vars = buildTokenVars()
  for (const [name, value] of Object.entries(vars)) {
    root.style.setProperty(name, value)
  }
}
