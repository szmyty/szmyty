# Visual System — Specification

Visuals exist to **clarify structure**.

They are not decoration.
They are not aesthetic padding.
They must reduce cognitive load.

---

## 1. Core Principle

A visual should:

* make a concept easier to understand
* reveal relationships not obvious in text
* reduce explanation length

If a visual does not improve understanding, it should not exist.

---

## 2. When to Include a Visual

Include visuals only when:

* a relationship benefits from spatial representation
* a loop or feedback system is involved
* a comparison is central to the idea
* a layered abstraction needs compression

Do NOT include visuals for:

* aesthetic enhancement
* filler
* redundancy

---

## 3. Visual Count Guidelines

Typical structure per article:

* 1 header image (recommended)
* 2–3 supporting figures

Additional figures (up to ~4) are allowed when:

* each visual introduces a **new structural layer**
* removing it would reduce clarity

There is no fixed maximum.

> Every visual must earn its place.

---

## 4. Visual Roles

### Header Image

* sets conceptual tone
* introduces the idea
* slightly more abstract

### Figures (figure1, figure2, etc.)

* clarify specific concepts
* appear after explanation
* are more structurally grounded

---

## 5. Visual Placement

Visuals should appear:

* after conceptual buildup
* at points of potential confusion
* where structure becomes multi-dimensional

Avoid:

* placing visuals before explanation
* clustering visuals without context

---

## 6. Visual Philosophy

All visuals must be:

* minimal
* clean
* structurally focused
* consistent in style

Avoid:

* visual noise
* unnecessary gradients
* decorative elements without meaning
* photorealistic or stock imagery

Preferred style:

* conceptual diagrams
* abstract representations
* calm, neutral palette

---

## 7. Naming Convention

Use canonical filenames:

```plaintext
header.png
figure1.png
figure2.png
figure3.png
figure4.png
```

All stored in:

```plaintext
articles/YYYY-MM-slug/assets/
```

---

## 8. Alt Text vs Caption (Critical Distinction)

### Alt Text

* describes what is visually present
* objective
* no interpretation

Example:

```plaintext
Diagram showing feedback loop between stress and cognitive load
```

---

### Caption

* explains what the visual means
* connects it to the article
* clarifies relationships

Structure:

```plaintext
*Conceptual explanation of the visual. This image was generated using AI.*
```

---

## 9. AI Image Disclosure (Required)

All AI-generated images must include:

```plaintext
This image was generated using AI.
```

This must appear in **every caption**, including the header.

---

## 10. Visual Integrity Rules

A visual must:

* not introduce new concepts
* not contradict the text
* not oversimplify to the point of distortion

It must reinforce:

* an existing idea
* a structural relationship already introduced

---

## 11. Complexity Constraint

A good visual:

* is understandable in under 5 seconds
* does not require explanation to decode
* reduces the need for additional paragraphs

If a visual requires explanation to understand:

* it is too complex

---

## 12. Anti-Patterns

Do NOT:

* use stock photos
* include unrelated imagery
* overload with visuals
* use visuals as filler

Avoid:

* inconsistent styles
* mismatched tones
* visual clutter

---

## 13. Relationship to Template

The template defines:

* where visuals appear
* formatting patterns

This specification defines:

* when they should exist
* how they behave

---

## 14. Guiding Constraint

If removing a visual:

* does not reduce clarity

Then the visual should not be included.

Visuals must earn their place.
