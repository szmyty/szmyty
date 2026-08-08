import type { CSSProperties } from "react"

export type PracticeActionCardTitleProps = {
  children: string
  id?: string
  color?: string

  /** Glow intensity (0 → 1) */
  glowIntensity?: number

  /** Override glow color */
  glowColor?: string

  /** Texture image URL */
  textureSrc?: string

  /** Texture opacity */
  textureOpacity?: number

  /** Blend mode for texture */
  textureBlendMode?: CSSProperties["mixBlendMode"]

  className?: string
  style?: CSSProperties
}