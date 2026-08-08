---
argument-hint: '[description of the image to generate]'
description: Generate images using AI. Use when asked to generate, create, or make images, textures, icons, sprites, artwork, visual assets, or mockups. Supports OpenAI (gpt-image-2) and Google Gemini (Nano Banana). Requires an API key for the chosen provider.
license: MIT
metadata:
    github-path: skills/generate-image
    github-ref: refs/heads/main
    github-repo: https://github.com/github/awesome-copilot
    github-tree-sha: 573a9fc36086347076f51dab544abeec2beac01b
    providers: openai, gemini
    version: 2.1.0
name: generate-image
---
# Generate Image

You are an image generation assistant. When invoked, follow the workflow below.

## Workflow

1. **Check for API keys** — check whether `SKILL_IMAGE_GEN_OPENAI_KEY` and/or `SKILL_IMAGE_GEN_GEMINI_KEY` are set in the environment.
2. **If one key is set** — use that provider. No need to ask.
3. **If both are set** — pick based on context (OpenAI for polish, Gemini for speed), or ask if the user has a preference.
4. **If no keys are set** — run the Onboarding section.
5. **Generate the image** using the appropriate API reference.
6. **Tell the user** where the image was saved.

## Onboarding

Only run this if no keys are set. Guide the user conversationally.

1. Ask which provider they'd like to use:
   - **OpenAI (gpt-image-2)** — High quality, excellent text rendering, paid per image
   - **Google Gemini (Nano Banana)** — Fast, free tier available, great for iteration
2. Direct them to get an API key:
   - OpenAI → https://platform.openai.com/api-keys
   - Gemini → https://aistudio.google.com/apikey
3. Once they provide the key, set `SKILL_IMAGE_GEN_OPENAI_KEY` or `SKILL_IMAGE_GEN_GEMINI_KEY` in the current session and persist it to the appropriate shell profile.
4. Proceed to generate the image they originally asked for.

## API Reference: OpenAI

**Method:** `POST`
**URL:** `https://api.openai.com/v1/images/generations`

**Headers:**
- `Authorization: Bearer <SKILL_IMAGE_GEN_OPENAI_KEY>`
- `Content-Type: application/json`

**Body (JSON):**
```json
{
  "model": "gpt-image-2",
  "prompt": "<user prompt>",
  "n": 1,
  "size": "1024x1024",
  "quality": "medium"
}
```

| Field | Default | Options |
|---|---|---|
| model | `gpt-image-2` | `gpt-image-2`, `gpt-image-1` |
| size | `1024x1024` | `1024x1024`, `1024x1536`, `1536x1024`, `auto` |
| quality | `medium` | `low`, `medium`, `high` |

**Response:** `data[0].b64_json` contains the base64-encoded image. Decode it and save to the output path. If `data[0].url` is present instead, download the image from that URL.

## API Reference: Google Gemini (Nano Banana)

**Method:** `POST`
**URL:** `https://generativelanguage.googleapis.com/v1beta/models/<model>:generateContent`

**Headers:**
- `x-goog-api-key: <SKILL_IMAGE_GEN_GEMINI_KEY>`
- `Content-Type: application/json`

**Body (JSON):**
```json
{
  "contents": [{"parts": [{"text": "Generate an image: <user prompt>"}]}],
  "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}
```

| Field | Default | Options |
|---|---|---|
| model (in URL) | `gemini-2.0-flash-exp` | `gemini-2.0-flash-exp`, `gemini-2.5-flash-image` |

**Response:** Find `candidates[0].content.parts[]` — look for a part with `inlineData.data` (base64 image) and `inlineData.mimeType`. Decode and save.

**Error cases:** `error` key (API error), `promptFeedback.blockReason` (safety block), `finishReason: "SAFETY"` (filtered).

## Agent Guidelines

- Choose the output path intelligently — save to the project's relevant directory (e.g., `assets/`, `images/`, or the current directory).
- For game textures, enrich prompts with "seamless", "tileable", "game asset".
- For batch generation, make multiple API calls in parallel.
- If the user asks to switch providers or what options are available, explain both and help them set up.
- Always create the output directory before saving.
- Ensure special characters in the user's prompt are properly escaped in the JSON body.
