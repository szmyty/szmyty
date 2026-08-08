# Example: Adding the "Acceptance" Practice Page

This walkthrough demonstrates the complete workflow for adding a new practice page to Edition 1.

## Context

**Regulation Axis**: Emotion/Integration
**Opposing Practice**: Gratitude
**Function**: Acceptance allows integration of difficulty, while Gratitude integrates the good

## Step 1: Review the Axis Partner

First, understand what we're balancing against:

```bash
python3 visual_dna.py editions/edition_1
```

Look at the gratitude page:

- **Role**: regulation_and_softening
- **Primary function**: shift_attention_from_threat_to_safety
- **Tone**: grounding, non-preachy, collectible, calm

**Acceptance must complement, not duplicate** these qualities.

## Step 2: Create Page Directory Structure

```bash
mkdir -p editions/edition_1/pages/acceptance
cd editions/edition_1/pages/acceptance
```

## Step 3: Write Base Schema

Create `acceptance.page.json`:

```json
{
  "page_type": "practice",
  "practice_id": "acceptance",
  "title": "Acceptance",
  "subtitle": "Practices for Allowing & Integration",
  
  "edition": {
    "name": "Ego Hygiene",
    "number": 1,
    "theme": "Orientation"
  },
  
  "intent": {
    "role": "permission_and_integration",
    "primary_function": "allow_difficulty_without_fixing",
    "secondary_function": "reduce_internal_resistance",
    "tone": [
      "permissive",
      "grounding",
      "non-demanding",
      "calm"
    ]
  },
  
  "visual_style": {
    "world": "post_collapse_retro_mystic",
    "texture": [
      "aged_paper",
      "worn_ink",
      "grain"
    ],
    "color_palette": {
      "primary": ["warm_yellow", "burnt_orange", "deep_brown"],
      "secondary": ["charcoal", "soft_gold"],
      "accent": ["muted_teal"]
    },
    "iconography": [
      "open_hands",
      "rain_symbol",
      "mountain_symbol",
      "crystals"
    ]
  },
  
  "practice_panels": [
    {
      "id": "acknowledge",
      "label": "ACKNOWLEDGE",
      "text": "Name what is difficult without needing to change it.",
      "domain": "cognitive",
      "modality": "awareness"
    },
    {
      "id": "allow",
      "label": "ALLOW",
      "text": "Let the difficult feeling exist without pushing it away.",
      "domain": "emotional",
      "modality": "permission"
    },
    {
      "id": "breathe",
      "label": "BREATHE",
      "text": "Return to breath when resistance appears.",
      "domain": "somatic",
      "modality": "regulation"
    },
    {
      "id": "stay",
      "label": "STAY",
      "text": "Remain present with what is hard.",
      "domain": "attentional",
      "modality": "endurance"
    }
  ],
  
  "effect_section": {
    "label": "EFFECT",
    "text": "Reduces internal struggle and allows natural integration of difficult experiences.",
    "scientific_status": "simplified_placeholder"
  },
  
  "footer_banner": {
    "text": "DIFFICULT THINGS DO NOT REQUIRE YOUR PERMISSION TO EXIST",
    "tone": "permission_giving",
    "intent": "reduce_fixing_pressure"
  },
  
  "constraints": {
    "no_medical_claims": true,
    "no_prescriptive_language": true,
    "no_spiritual_superiority": true,
    "no_required_actions": true
  }
}
```

## Step 4: Write Base Prompt

Create `acceptance.prompt`:

```text
MAGAZINE PAGE DESIGN — EGO HYGIENE
PAGE: ACCEPTANCE
EDITION 1: ORIENTATION

Create a magazine page for the practice of Acceptance.

CENTRAL IMAGE:
- Open hands holding rain
- Figure seated in weathered landscape
- Posture: receptive, not resistant
- Rain falling gently into hands

LAYOUT:
- Central focus with surrounding practice panels
- Four practice panels arranged around central image
- Panels: ACKNOWLEDGE, ALLOW, BREATHE, STAY

VISUAL TONE:
- Calm acceptance of difficulty
- Not resignation or defeat
- Permission-giving without passivity
- Grounding presence

TEXT TREATMENT:
- Title: ACCEPTANCE (uppercase, bold serif)
- Subtitle: Practices for Allowing & Integration
- Footer banner: DIFFICULT THINGS DO NOT REQUIRE YOUR PERMISSION TO EXIST

SYMBOLISM:
- Rain: what cannot be controlled
- Open hands: receptivity without grasping
- Mountain: endurance and stability
- Crystals: transformation through pressure

EMOTIONAL QUALITY:
- Permissive
- Non-demanding
- Grounding
- Calm
```

## Step 5: Check Axis Balance

```bash
cd /home/runner/work/magazine/magazine
python3 axis_balancer.py editions/edition_1
```

Expected output:

```text
Axis: Emotion Integration
  Practices: gratitude ↔ acceptance
  ✓ Balanced
```

If you see warnings, revise the schema until balance is achieved.

## Step 6: Check Visual DNA Compliance

```bash
python3 visual_dna.py editions/edition_1
```

Review the acceptance page's adherence scores. Aim for 60%+ adherence while allowing practice-specific uniqueness.

## Step 7: Generate Context-Enriched Prompt

```bash
python3 context_weaver.py editions/edition_1 --apply
```

This creates `acceptance.woven.prompt` containing:

- Edition metadata
- Required visual DNA elements
- Forbidden IP references
- Mandatory tone markers
- Your original prompt

## Step 8: Generate Visuals

Use `acceptance.woven.prompt` (NOT the base prompt) as input to your AI image generation tool.

The woven prompt ensures:

- Consistent visual language
- No accidental IP violations
- Adherence to edition theme
- Proper tone enforcement

## Step 9: Final Verification

```bash
# Check all constraints
python3 axis_balancer.py editions/edition_1
python3 visual_dna.py editions/edition_1
python3 lint_ip_references.py
```

All checks should pass before committing the new page.

## Step 10: Commit

```bash
git add editions/edition_1/pages/acceptance/
git add editions/edition_1/meta.json  # if page order changed
git commit -m "Add acceptance practice page"
```

## Key Learnings

1. **Start with the opposing practice** - understand what you're balancing against
2. **Use visual DNA** to maintain aesthetic coherence
3. **Always use woven prompts** for AI generation, never base prompts
4. **Check axis balance** before finalizing schema
5. **Allow practice-specific uniqueness** within the canonical framework

## What Makes This Different from Generic Workflows?

- The tools understand **regulation axes** (not just arbitrary pages)
- Visual DNA is **extracted from existing work**, not imposed externally
- Context weaving is **automatic**, reducing cognitive load
- Balance checking prevents **conceptual drift** across practice pairs
- The workflow **externalizes memory** so you don't have to track everything mentally

This is context engineering in practice.
