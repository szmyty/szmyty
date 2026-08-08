import type { CSSProperties } from "react"
import type { PracticeActionCardProps } from "./PracticeActionCard.types"

import { OrnamentalDivider } from "@magazine/OrnamentalDivider"
import { PracticeActionCardTitle } from "./PracticeActionCardTitle"
import { PracticeActionCardDescription } from "./PracticeActionCardDescription"
import { PracticeActionCardTextureOverlay } from "./PracticeActionCardTextureOverlay"

export function PracticeActionCard({
  title,
  description,
  backgroundColor,
  borderColor,
  textColor,
  accentColor,
  className = "",
}: PracticeActionCardProps) {
  const titleId = `practice-card-title-${title.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "")}`

  const cardStyle: CSSProperties = {
    backgroundColor: backgroundColor ?? "var(--color-deep-brown)",
    border: `4px double ${borderColor ?? "var(--color-soft-gold)"}`,
    color: textColor ?? "var(--color-warm-parchment)",
  }

  return (
    <article
      aria-labelledby={titleId}
      className={[
        "relative overflow-hidden rounded-ds-lg",
        "flex flex-col items-center justify-start",
        "w-[260px] min-h-[280px]",
        "px-ds-6 pt-ds-6 pb-ds-7",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      style={cardStyle}
    >
      <PracticeActionCardTextureOverlay />

      <PracticeActionCardTitle id={titleId} color={accentColor}>
        {title}
      </PracticeActionCardTitle>

      <OrnamentalDivider color={accentColor} />

      <PracticeActionCardDescription color={textColor}>
        {description}
      </PracticeActionCardDescription>
    </article>
  )
}

export default PracticeActionCard