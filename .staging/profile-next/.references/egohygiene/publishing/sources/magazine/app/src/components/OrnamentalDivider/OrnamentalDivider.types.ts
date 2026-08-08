import type { CSSProperties } from "react"

export type OrnamentalDividerProps = {
  /** Primary color of the divider beam and dot */
  color?: string

  /** Width of the divider relative to parent (e.g. "80%", "200px") */
  width?: string

  /** Thickness of the beam */
  thickness?: number

  /** Size of the center dot */
  dotSize?: number

  /** Whether to render the center dot */
  showDot?: boolean

  /** Intensity of glow (0–1 range recommended) */
  glowIntensity?: number

  /** Additional className for wrapper */
  className?: string

  /** Optional style override */
  style?: CSSProperties

  /** Where the beam becomes visible (taper start %) */
  taperStart?: number

  /** Where full brightness begins */
  taperMid?: number

  /** Glow spread multiplier */
  glowSpread?: number
}
