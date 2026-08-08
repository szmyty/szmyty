import type { PracticeActionCardDescriptionProps } from "./PracticeActionCardDescription.types"

export function PracticeActionCardDescription({
  children,
  color = "var(--color-warm-parchment)",
  className = "",
  style,
}: PracticeActionCardDescriptionProps) {
  return (
    <p
      className={[
        "relative z-10 m-0 text-center",
        "text-ds-lg leading-ds-snug",
        "font-serif",
        className,
      ].join(" ")}
      style={{
        color,
        ...style,
      }}
    >
      {children}
    </p>
  )
}

export default PracticeActionCardDescription