import type { CSSProperties } from "react"
import type { OrnamentalDividerProps } from "./OrnamentalDivider.types"

export function OrnamentalDivider({
  color = "var(--color-warm-yellow)",
  width = "80%",
  thickness = 2,
  dotSize = 12,
  showDot = true,
  glowIntensity = 0.8,
  className = "",
  style,
}: OrnamentalDividerProps) {
  const glow: number = Math.min(Math.max(glowIntensity, 0), 1)

  /* ──────────────────────────────────────────────────────────────────────────
   * Beam styles (fixed visibility first, then we refine later)
   * ────────────────────────────────────────────────────────────────────────── */

  const leftBeamStyle: CSSProperties = {
    height: `${Math.max(thickness, 3)}px`,
    background: color,

    WebkitMaskImage: `
      linear-gradient(
        to right,
        transparent 0%,
        black 40%,
        black 100%
      )
    `,
    maskImage: `
      linear-gradient(
        to right,
        transparent 0%,
        black 40%,
        black 100%
      )
    `,
  }

  const rightBeamStyle: CSSProperties = {
    height: `${Math.max(thickness, 3)}px`,
    background: color,

    WebkitMaskImage: `
      linear-gradient(
        to left,
        transparent 0%,
        black 40%,
        black 100%
      )
    `,
    maskImage: `
      linear-gradient(
        to left,
        transparent 0%,
        black 40%,
        black 100%
      )
    `,
  }

  /* ──────────────────────────────────────────────────────────────────────────
   * Dot style
   * ────────────────────────────────────────────────────────────────────────── */

  const dotStyle: CSSProperties = {
    width: `${dotSize}px`,
    height: `${dotSize}px`,
    background: color,
    boxShadow: `
      0 0 ${8 * glow}px rgba(245,200,66,${0.9 * glow}),
      0 0 ${16 * glow}px rgba(245,200,66,${0.4 * glow})
    `,
  }

  /* ──────────────────────────────────────────────────────────────────────────
   * Render
   * ────────────────────────────────────────────────────────────────────────── */

  return (
    <div
      aria-hidden="true"
      className={[
        "relative w-full",
        className,
      ].join(" ")}
      style={style}
    >
      <div
        className="flex items-center w-full"
        style={{
          maxWidth: width,
          margin: "0 auto",
        }}
      >
        {/* Left beam */}
        <div className="flex-1" style={leftBeamStyle} />

        {/* Center dot */}
        {showDot && (
          <div
            className="mx-[8px] rounded-full flex-none"
            style={dotStyle}
          />
        )}

        {/* Right beam */}
        <div className="flex-1" style={rightBeamStyle} />
      </div>
    </div>
  )
}

export default OrnamentalDivider