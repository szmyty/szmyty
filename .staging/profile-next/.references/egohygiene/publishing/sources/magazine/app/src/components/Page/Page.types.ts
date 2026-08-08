import type { CSSProperties, ReactNode } from "react"

/** Industry-standard print formats supported by BasePage */
export type PageFormat =
  | "comic_modern"
  | "magazine"
  | "digest"
  | "manga"
  | "european_album"

export type BasePageProps = {
  /** Page format defining physical dimensions and margins */
  format?: PageFormat

  /** Child content rendered inside safe bounds */
  children?: ReactNode

  /** Background color override (accepts any CSS color or token var) */
  backgroundColor?: string

  /** Show bleed area guide for print debugging */
  showBleedGuides?: boolean

  /** Show safe area guide for content alignment */
  showSafeArea?: boolean

  /** Override page width in inches */
  width?: number

  /** Override page height in inches */
  height?: number

  /** Override bleed margin in inches */
  bleed?: number

  /** Override safe area margin in inches */
  safeArea?: number

  /** Additional className for the outer wrapper */
  className?: string

  /** Inline style override for the outer wrapper */
  style?: CSSProperties
}
