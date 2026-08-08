import type { Meta, StoryObj } from "@storybook/react-vite"
import { OrnamentalDivider } from "./OrnamentalDivider"

const meta = {
  title: "Primitives/OrnamentalDivider",
  component: OrnamentalDivider,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],

  argTypes: {
    color: {
      control: "color",
    },

    width: {
      control: "text",
    },

    thickness: {
      control: {
        type: "range",
        min: 1,
        max: 8,
        step: 1,
      },
    },

    dotSize: {
      control: {
        type: "range",
        min: 4,
        max: 32,
        step: 1,
      },
    },

    glowIntensity: {
      control: {
        type: "range",
        min: 0,
        max: 1,
        step: 0.05,
      },
    },

    showDot: {
      control: "boolean",
    },
  },
} satisfies Meta<typeof OrnamentalDivider>

export default meta
type Story = StoryObj<typeof meta>

/* ────────────────────────────────────────────────────────────────────────────
 * Helpers
 * ──────────────────────────────────────────────────────────────────────────── */

function Container({
  children,
  width = "300px",
  background = "var(--color-deep-brown)",
}: {
  children: React.ReactNode
  width?: string
  background?: string
}) {
  return (
    <div
      style={{
        width,
        padding: "24px",
        background,
        display: "flex",
        justifyContent: "center",
      }}
    >
      {children}
    </div>
  )
}

/* ────────────────────────────────────────────────────────────────────────────
 * Stories
 * ──────────────────────────────────────────────────────────────────────────── */

export const Default: Story = {
  args: {
    color: "var(--color-warm-yellow)",
    width: "80%",
    thickness: 2,
    dotSize: 12,
    glowIntensity: 0.8,
    showDot: true,
  },

  render: (args) => (
    <div
      style={{
        width: "300px",
        padding: "24px",
        background: "var(--color-deep-brown)",
        display: "flex",
        justifyContent: "center",
      }}
    >
      <OrnamentalDivider {...args} />
    </div>
  ),
}

export const WidthVariants: Story = {
  render: () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <Container>
        <OrnamentalDivider width="40%" />
      </Container>
      <Container>
        <OrnamentalDivider width="60%" />
      </Container>
      <Container>
        <OrnamentalDivider width="80%" />
      </Container>
      <Container>
        <OrnamentalDivider width="100%" />
      </Container>
    </div>
  ),
}

export const GlowVariants: Story = {
  render: () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <Container>
        <OrnamentalDivider glowIntensity={0.3} />
      </Container>
      <Container>
        <OrnamentalDivider glowIntensity={0.6} />
      </Container>
      <Container>
        <OrnamentalDivider glowIntensity={1} />
      </Container>
    </div>
  ),
}

export const DotVariants: Story = {
  render: () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <Container>
        <OrnamentalDivider dotSize={8} />
      </Container>
      <Container>
        <OrnamentalDivider dotSize={12} />
      </Container>
      <Container>
        <OrnamentalDivider dotSize={16} />
      </Container>
      <Container>
        <OrnamentalDivider showDot={false} />
      </Container>
    </div>
  ),
}

export const ThicknessVariants: Story = {
  render: () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <Container>
        <OrnamentalDivider thickness={1} />
      </Container>
      <Container>
        <OrnamentalDivider thickness={2} />
      </Container>
      <Container>
        <OrnamentalDivider thickness={3} />
      </Container>
    </div>
  ),
}

export const BackgroundContrast: Story = {
  render: () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <Container background="var(--color-deep-brown)">
        <OrnamentalDivider />
      </Container>
      <Container background="var(--color-deep-blue)">
        <OrnamentalDivider />
      </Container>
      <Container background="var(--color-charcoal)">
        <OrnamentalDivider />
      </Container>
    </div>
  ),
}
