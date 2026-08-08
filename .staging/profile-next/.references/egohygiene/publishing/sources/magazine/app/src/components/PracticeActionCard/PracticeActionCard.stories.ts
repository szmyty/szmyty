import type { Meta, StoryObj } from "@storybook/react-vite"
import { PracticeActionCard } from "./PracticeActionCard"

const meta = {
  title: "Components/PracticeActionCard",
  component: PracticeActionCard,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof PracticeActionCard>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    title: "Mobilize",
    description: "Invite gentle range and circulation.",
  },
}

export const CustomColors: Story = {
  args: {
    title: "Energize",
    description: "Awaken the body and invite full presence.",
    backgroundColor: "var(--color-deep-blue)",
    borderColor: "var(--color-rose-quartz)",
    accentColor: "var(--color-rose-quartz)",
  },
}