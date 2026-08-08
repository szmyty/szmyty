import type { PageFormat } from "./Page.types"

/** Canonical configuration for a single page format */
export type PageFormatConfig = {
  /** Page width in inches (excluding bleed) */
  width: number

  /** Page height in inches (excluding bleed) */
  height: number

  /** Bleed margin in inches — extra area outside trim for printing */
  bleed: number

  /** Safe content margin in inches — minimum inset from trim edge */
  safeMargin: number

  /** Human-readable label with dimensions */
  label: string
}

/** Canonical format configurations for all supported page formats */
export const PAGE_FORMATS: Record<PageFormat, PageFormatConfig> = {
  comic_modern: {
    width: 6.625,
    height: 10.25,
    bleed: 0.125,
    safeMargin: 0.375,
    label: 'Comic Modern (6.625" × 10.25")',
  },

  magazine: {
    width: 8.5,
    height: 11,
    bleed: 0.125,
    safeMargin: 0.5,
    label: 'Magazine (8.5" × 11")',
  },

  digest: {
    width: 5.5,
    height: 8.5,
    bleed: 0.125,
    safeMargin: 0.375,
    label: 'Digest (5.5" × 8.5")',
  },

  manga: {
    width: 5,
    height: 7.5,
    bleed: 0.125,
    safeMargin: 0.25,
    label: 'Manga (~5" × 7.5")',
  },

  european_album: {
    width: 8.4,
    height: 11.6,
    bleed: 0.125,
    safeMargin: 0.5,
    label: 'European Album (~8.4" × 11.6")',
  },
}
