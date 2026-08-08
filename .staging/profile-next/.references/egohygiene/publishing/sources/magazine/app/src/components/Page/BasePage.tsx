import type { CSSProperties } from "react"
import type { BasePageProps } from "./Page.types"
import { PAGE_FORMATS } from "./Page.formats"

export function BasePage({
  format = "comic_modern",
  children,
  backgroundColor,
  showBleedGuides = false,
  showSafeArea = false,
  width: widthOverride,
  height: heightOverride,
  bleed: bleedOverride,
  safeArea: safeAreaOverride,
  className = "",
  style,
}: BasePageProps) {
  const config = PAGE_FORMATS[format]

  const width = widthOverride ?? config.width
  const height = heightOverride ?? config.height
  const bleed = bleedOverride ?? config.bleed
  const safeArea = safeAreaOverride ?? config.safeMargin

  const aspectRatio = width / height

  /* ──────────────────────────────────────────────────────────────────────────
   * Guide dimensions as percentages of the page surface.
   *
   * CSS absolute positioning uses % of the parent's WIDTH for horizontal
   * offsets and % of the parent's HEIGHT for vertical offsets, so we derive
   * each axis separately.
   * ────────────────────────────────────────────────────────────────────────── */

  const bleedXPct = (bleed / width) * 100
  const bleedYPct = (bleed / height) * 100

  const safeXPct = ((bleed + safeArea) / width) * 100
  const safeYPct = ((bleed + safeArea) / height) * 100

  /* ──────────────────────────────────────────────────────────────────────────
   * Page surface — scales to fit the viewport while preserving aspect ratio.
   *
   * min(90vw, 90vh × aspect) ensures the page never overflows in either axis.
   * ────────────────────────────────────────────────────────────────────────── */

  const pageStyle: CSSProperties = {
    position: "relative",
    aspectRatio: `${width} / ${height}`,
    width: `min(90vw, calc(90vh * ${aspectRatio}))`,
    backgroundColor: backgroundColor ?? "var(--semantic-background)",
    boxShadow:
      "0 4px 24px rgba(0, 0, 0, 0.18), 0 1px 4px rgba(0, 0, 0, 0.12)",
    overflow: "hidden",
    flexShrink: 0,
  }

  /* ──────────────────────────────────────────────────────────────────────────
   * Debug guide overlays
   * ────────────────────────────────────────────────────────────────────────── */

  const bleedGuideStyle: CSSProperties = {
    position: "absolute",
    top: `${bleedYPct}%`,
    left: `${bleedXPct}%`,
    right: `${bleedXPct}%`,
    bottom: `${bleedYPct}%`,
    border: "1px dashed rgba(220, 60, 60, 0.75)",
    pointerEvents: "none",
    zIndex: 10,
  }

  const safeAreaGuideStyle: CSSProperties = {
    position: "absolute",
    top: `${safeYPct}%`,
    left: `${safeXPct}%`,
    right: `${safeXPct}%`,
    bottom: `${safeYPct}%`,
    border: "1px dashed rgba(60, 120, 220, 0.75)",
    pointerEvents: "none",
    zIndex: 10,
  }

  /* ──────────────────────────────────────────────────────────────────────────
   * Content area — children render within safe bounds
   * ────────────────────────────────────────────────────────────────────────── */

  const contentAreaStyle: CSSProperties = {
    position: "absolute",
    top: `${safeYPct}%`,
    left: `${safeXPct}%`,
    right: `${safeXPct}%`,
    bottom: `${safeYPct}%`,
    overflow: "hidden",
  }

  /* ──────────────────────────────────────────────────────────────────────────
   * Render
   * ────────────────────────────────────────────────────────────────────────── */

  return (
    <div
      className={[
        "flex items-center justify-center w-full h-full",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      style={style}
    >
      <div
        role="region"
        aria-label={config.label}
        style={pageStyle}
      >
        {/* Bleed guide — marks printable area boundary */}
        {showBleedGuides && (
          <div style={bleedGuideStyle} aria-hidden="true" />
        )}

        {/* Safe area guide — marks content safety margin */}
        {showSafeArea && (
          <div style={safeAreaGuideStyle} aria-hidden="true" />
        )}

        {/* Content area — children render here */}
        <div style={contentAreaStyle}>{children}</div>
      </div>
    </div>
  )
}

export default BasePage
