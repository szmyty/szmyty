export function PracticeActionCardTextureOverlay() {
  return (
    <div
      aria-hidden="true"
      className="
        pointer-events-none absolute inset-0
        rounded-ds-lg opacity-20 mix-blend-overlay
      "
      style={{
        backgroundImage:
          "repeating-linear-gradient(45deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0.15) 1px, transparent 1px, transparent 6px)",
      }}
    />
  )
}

export default PracticeActionCardTextureOverlay