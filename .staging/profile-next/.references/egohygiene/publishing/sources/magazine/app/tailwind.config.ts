import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Semantic color tokens (role-based, mapped from the design-system palette)
        'color-primary':    'var(--semantic-primary)',
        'color-background': 'var(--semantic-background)',
        'color-text':       'var(--semantic-text)',
        'color-accent':     'var(--semantic-accent)',
        'color-border':     'var(--semantic-border)',
        // Raw palette tokens
        'burnt-orange':    'var(--color-burnt-orange)',
        'warm-parchment':  'var(--color-warm-parchment)',
        'charcoal':        'var(--color-charcoal)',
        'soft-gold':       'var(--color-soft-gold)',
        'warm-yellow':     'var(--color-warm-yellow)',
        'soft-amber':      'var(--color-soft-amber)',
        'deep-brown':      'var(--color-deep-brown)',
        'deep-blue':       'var(--color-deep-blue)',
      },
      spacing: {
        'ds-1':  'var(--spacing-1)',
        'ds-2':  'var(--spacing-2)',
        'ds-3':  'var(--spacing-3)',
        'ds-4':  'var(--spacing-4)',
        'ds-5':  'var(--spacing-5)',
        'ds-6':  'var(--spacing-6)',
        'ds-7':  'var(--spacing-7)',
        'ds-8':  'var(--spacing-8)',
        'ds-9':  'var(--spacing-9)',
        'ds-10': 'var(--spacing-10)',
      },
      borderWidth: {
        'hairline': 'var(--border-width-hairline)',
        'thin':     'var(--border-width-thin)',
        'medium':   'var(--border-width-medium)',
        'thick':    'var(--border-width-thick)',
        'heavy':    'var(--border-width-heavy)',
      },
      borderRadius: {
        'ds-sm':   'var(--border-radius-sm)',
        'ds-md':   'var(--border-radius-md)',
        'ds-lg':   'var(--border-radius-lg)',
        'ds-pill': 'var(--border-radius-pill)',
      },
      fontFamily: {
        serif:   'var(--font-family-serif)',
        sans:    'var(--font-family-sans)',
        mono:    'var(--font-family-mono)',
        display: 'var(--font-family-display)',
      },
      fontSize: {
        'ds-xs':  'var(--font-size-xs)',
        'ds-sm':  'var(--font-size-sm)',
        'ds-md':  'var(--font-size-md)',
        'ds-lg':  'var(--font-size-lg)',
        'ds-xl':  'var(--font-size-xl)',
        'ds-2xl': 'var(--font-size-2xl)',
        'ds-3xl': 'var(--font-size-3xl)',
      },
      fontWeight: {
        regular: 'var(--font-weight-regular)',
        medium:  'var(--font-weight-medium)',
        bold:    'var(--font-weight-bold)',
        black:   'var(--font-weight-black)',
      },
      lineHeight: {
        'ds-tight':   'var(--font-lineHeight-tight)',
        'ds-snug':    'var(--font-lineHeight-snug)',
        'ds-normal':  'var(--font-lineHeight-normal)',
        'ds-relaxed': 'var(--font-lineHeight-relaxed)',
      },
      letterSpacing: {
        'ds-tight':  'var(--font-letterSpacing-tight)',
        'ds-normal': 'var(--font-letterSpacing-normal)',
        'ds-wide':   'var(--font-letterSpacing-wide)',
        'ds-wider':  'var(--font-letterSpacing-wider)',
      },
    },
  },
  plugins: [],
}

export default config
