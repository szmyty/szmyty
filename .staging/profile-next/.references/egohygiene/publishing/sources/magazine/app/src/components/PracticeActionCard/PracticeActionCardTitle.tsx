import type { PracticeActionCardTitleProps } from "./PracticeActionCardTitle.types"

export function PracticeActionCardTitle({
  children,
  id,
  color = "var(--color-warm-yellow)",
  glowIntensity = 0.4,
  textureSrc = "/textures/grit.png",
  textureOpacity = 0.9,
  textureBlendMode = "overlay",
  className = "",
  style,
}: PracticeActionCardTitleProps) {
  const glow = Math.min(Math.max(glowIntensity, 0), 1)

  return (
    <h3
      id={id}
      className={[
        "relative z-10 m-0 w-full text-center",
        "font-display uppercase",
        "text-[42px]",
        "tracking-[0.02em]",
        "leading-[1.0]",
        className,
      ].join(" ")}
      style={{
        color,

      // textShadow: `
      //   0 1px 0 rgba(0,0,0,0.5),
      //   0 2px 2px rgba(0,0,0,0.25)
      // `,
      // filter: `drop-shadow(0 0 ${6 * glow}px rgba(245,200,66,0.35))`,

        ...style,
      }}
    >
      {/* BASE TEXT */}
      <span className="relative z-10">
        {children}
      </span>

      {/* TEXTURE TEXT (duplicate, clipped) */}
      {textureSrc && (
        <span
          aria-hidden="true"
          className="absolute inset-0 z-20 pointer-events-none"
          style={{
            backgroundImage: `url(${textureSrc})`,
            backgroundSize: "cover",

            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",

            opacity: textureOpacity,
            mixBlendMode: textureBlendMode,
          }}
        >
          {children}
        </span>
      )}
    </h3>
  )
}

export default PracticeActionCardTitle