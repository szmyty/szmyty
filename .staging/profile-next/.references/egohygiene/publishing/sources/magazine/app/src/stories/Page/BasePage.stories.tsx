import type { ReactNode } from "react"
import type { Meta, StoryObj } from "@storybook/react-vite"
import { BasePage } from "../../components/Page/BasePage"
import { PAGE_FORMATS } from "../../components/Page/Page.formats"
import type { PageFormat } from "../../components/Page/Page.types"

/* ────────────────────────────────────────────────────────────────────────────
 * Helpers
 * ──────────────────────────────────────────────────────────────────────────── */

function ViewportWrapper({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "var(--color-charcoal)",
      }}
    >
      {children}
    </div>
  )
}

function FormatLabel({ format }: { format: PageFormat }) {
  const config = PAGE_FORMATS[format]
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100%",
        gap: "8px",
        color: "var(--semantic-text)",
        fontFamily: "var(--font-family-serif)",
        textAlign: "center",
        padding: "16px",
      }}
    >
      <span
        style={{
          fontSize: "var(--font-size-xl)",
          fontFamily: "var(--font-family-display)",
          fontWeight: "var(--font-weight-black)",
          letterSpacing: "0.06em",
          textTransform: "uppercase",
        }}
      >
        {config.label}
      </span>
      <span
        style={{
          fontSize: "var(--font-size-sm)",
          color: "var(--semantic-text)",
          opacity: 0.65,
        }}
      >
        bleed {config.bleed}&#8243; · safe margin {config.safeMargin}&#8243;
      </span>
    </div>
  )
}

/* ────────────────────────────────────────────────────────────────────────────
 * Meta
 * ──────────────────────────────────────────────────────────────────────────── */

const meta = {
  title: "Page/BasePage",
  component: BasePage,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
  argTypes: {
    format: {
      control: "select",
      options: [
        "comic_modern",
        "magazine",
        "digest",
        "manga",
        "european_album",
      ] satisfies PageFormat[],
    },
    backgroundColor: {
      control: "color",
    },
    showBleedGuides: {
      control: "boolean",
    },
    showSafeArea: {
      control: "boolean",
    },
  },
} satisfies Meta<typeof BasePage>

export default meta
type Story = StoryObj<typeof meta>

/* ────────────────────────────────────────────────────────────────────────────
 * Stories
 * ──────────────────────────────────────────────────────────────────────────── */

/** Primary format — the standard modern comic book size */
export const ComicModern: Story = {
  args: {
    format: "comic_modern",
    showBleedGuides: false,
    showSafeArea: false,
  },
  render: (args) => (
    <ViewportWrapper>
      <BasePage {...args}>
        <FormatLabel format="comic_modern" />
      </BasePage>
    </ViewportWrapper>
  ),
}

export const Magazine: Story = {
  args: {
    format: "magazine",
    showBleedGuides: false,
    showSafeArea: false,
  },
  render: (args) => (
    <ViewportWrapper>
      <BasePage {...args}>
        <FormatLabel format="magazine" />
      </BasePage>
    </ViewportWrapper>
  ),
}

export const Digest: Story = {
  args: {
    format: "digest",
    showBleedGuides: false,
    showSafeArea: false,
  },
  render: (args) => (
    <ViewportWrapper>
      <BasePage {...args}>
        <FormatLabel format="digest" />
      </BasePage>
    </ViewportWrapper>
  ),
}

export const Manga: Story = {
  args: {
    format: "manga",
    showBleedGuides: false,
    showSafeArea: false,
  },
  render: (args) => (
    <ViewportWrapper>
      <BasePage {...args}>
        <FormatLabel format="manga" />
      </BasePage>
    </ViewportWrapper>
  ),
}

export const EuropeanAlbum: Story = {
  args: {
    format: "european_album",
    showBleedGuides: false,
    showSafeArea: false,
  },
  render: (args) => (
    <ViewportWrapper>
      <BasePage {...args}>
        <FormatLabel format="european_album" />
      </BasePage>
    </ViewportWrapper>
  ),
}

/** All formats with guides enabled for visual debugging */
export const WithGuides: Story = {
  args: {
    format: "comic_modern",
    showBleedGuides: true,
    showSafeArea: true,
  },
  render: (args) => (
    <ViewportWrapper>
      <BasePage {...args}>
        <FormatLabel format={args.format ?? "comic_modern"} />
      </BasePage>
    </ViewportWrapper>
  ),
}
