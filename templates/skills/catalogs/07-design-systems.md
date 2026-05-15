# Design System Components

Rendered design evidence, taste memory, variant boards, AI-slop detection, UI state matrices, design artifact promotion, and live previews.

Components: 60-66.

Source: distilled from the gstack `SKILL.md` corpus. Each component includes a context paragraph, reusable description, and compact sample.

## **60. Live Design Evidence Component**

**Reusable purpose:** Evaluate UI from rendered output, not from source code guesses.

**Context:** Use this for any design or UI claim that should be based on rendered reality. It is most useful in design review, design-html, QA, and visual polish workflows where screenshots, console state, and before/after evidence are required before saying the interface improved.

**Reusable evidence:**

```text
- Desktop screenshot.
- Mobile screenshot.
- Tablet screenshot when layout risk exists.
- Console errors.
- Network failures.
- Before/after screenshots for fixes.
- Visual score before and after each pass.
```

**Rules:**

```text
- Source code can explain why a problem exists, but screenshot evidence proves it.
- Non-trivial visual fixes need target mockups or clear visual direction.
- Revert or stop if a fix makes the rendered UI worse.
```

**Patterns copied from:** `design-review`, `design-html`, `plan-design-review`, `qa`.

**Sample:**

```text
Design evidence:
- desktop screenshot: .gstack/designs/imports/desktop-before.png
- mobile screenshot: .gstack/designs/imports/mobile-before.png
- console errors: 0
- network failures: 0
- score before: 6/10
- score after proposed fix: not verified yet
```

------

## **61. Design Taste Memory Component**

**Reusable purpose:** Let visual work compound across sessions without hard-coding one static style.

**Context:** Use this when a product or user has evolving visual preferences that should compound across sessions. It records approved and rejected patterns, palettes, typography, and layout choices so future design variants start from real taste evidence instead of generic defaults.

**Reusable data:**

```json
{
  "approved_patterns": [],
  "rejected_patterns": [],
  "fonts": [],
  "palettes": [],
  "layout_preferences": [],
  "recency_weight": 0.0,
  "source_artifacts": []
}
```

**Reusable behaviors:**

```text
- Read prior approved designs before generating variants.
- Use taste decay so recent approvals matter more.
- Update taste profile after explicit approvals and rejections.
- Do not infer durable taste from one-off comments unless user confirms.
```

**Use this for:** Design systems, mockup generation, brand work, product UI polish.

**Sample:**

```json
{
  "approved_patterns": ["dense admin tables", "quiet status chips"],
  "rejected_patterns": ["large marketing hero", "purple gradients"],
  "fonts": ["Inter"],
  "palettes": ["neutral base with semantic status colors"],
  "layout_preferences": ["left navigation", "compact filters"],
  "recency_weight": 0.8,
  "source_artifacts": ["~/.gstack/projects/app/designs/admin-board.md"]
}
```

------

## **62. Design Variant Board Component**

**Reusable purpose:** Make visual preference decisions concrete instead of prose-only.

**Context:** Use this when visual direction is uncertain and prose descriptions would be too abstract. A variant board lets the skill present materially different design options, collect structured feedback, remix promising directions, and preserve the winning tokens and rationale.

**Reusable flow:**

```text
1. Generate 3-6 materially different variants.
2. Place them in a comparison board.
3. Store variant metadata and preview paths.
4. Collect structured feedback: choose, remix, regenerate, reject.
5. Preserve winning tokens and rationale.
```

**Variant dimensions:**

```text
- typography
- palette
- density
- navigation model
- layout rhythm
- motion posture
- illustration/photo/asset direction
```

**Use this for:** Product visual direction, landing pages, dashboards, component libraries.

**Sample:**

```text
Variant board:
A) Dense ops console: compact table, side filters, strong status colors.
B) Guided recovery: wizard-like failure groups and next actions.
C) Audit log first: timeline layout with expandable row details.

Feedback options:
- choose A/B/C
- remix two variants
- regenerate with constraints
- reject all and explain why
```

------

## **63. AI Slop Detection Component**

**Reusable purpose:** Reject common generated-design defaults before they ship.

**Context:** Use this during design generation and review to catch common AI-generated visual cliches before they become product direction. It helps the skill reject generic gradients, hero rhythms, blobs, centered layouts, and vague copy in favor of domain-specific design decisions.

**Reusable blacklist:**

```text
- purple/blue-purple gradient default
- centered-everything layout
- three feature cards with circle icons
- decorative blobs/waves/orbs
- generic hero copy
- oversized border radius everywhere
- uniform card grids for unrelated content
- stock SaaS section rhythm: hero, features, testimonials, pricing, CTA
- default system font as the only design decision
```

**Use this for:** Design review, design generation, marketing pages, app UI polish.

**Sample:**

```text
AI slop check:
- Purple gradient hero: not present.
- Three generic feature cards: not present.
- Decorative blobs: present in empty state. Remove.
- Centered everything: not present.
- Generic copy: "Supercharge your imports" found. Replace with concrete failure copy.
```

------

## **64. UI State Matrix Component**

**Reusable purpose:** Force UI skills to handle user-visible states, not just the success state.

**Context:** Use this for any UI component, page, dashboard, or workflow that has asynchronous or conditional states. It ensures loading, empty, error, success, partial, permission, and offline experiences are designed intentionally rather than only rendering the happy path.

**Reusable table:**

```text
FEATURE | LOADING | EMPTY | ERROR | SUCCESS | PARTIAL | PERMISSION | OFFLINE
```

**Checks:**

```text
- Does each state have useful copy?
- Is the next action obvious?
- Does the layout remain stable?
- Does mobile still work?
- Is accessibility preserved?
```

**Use this for:** App UI, dashboards, forms, async workflows, data tools.

**Sample:**

```text
FEATURE | LOADING | EMPTY | ERROR | SUCCESS | PARTIAL | PERMISSION | OFFLINE
Import failures | spinner | no failures | retry load | table | expired rows | no access | cached shell
```

------

## **65. Design Artifact Promotion Component**

**Reusable purpose:** Promote approved design decisions into durable project guidance.

**Context:** Use this after the user approves a visual direction or design-system decision. It moves taste and design choices into durable files such as `DESIGN.md`, project instructions, mockup paths, and tokens so future implementation work can follow the approved direction.

**Reusable outputs:**

```text
- DESIGN.md with typography, color, spacing, motion, layout, and voice.
- CLAUDE.md routing/guidance block for future visual work.
- Approved mockup paths written into the implementation plan.
- Token extraction for CSS variables, Tailwind config, or component props.
```

**Use this for:** Long-lived products where visual decisions should survive the chat.

**Sample:**

```text
Promote approved design:
- Write tokens to docs/DESIGN.md.
- Add "Import diagnostics UI" guidance to CLAUDE.md.
- Copy approved mockups to ~/.gstack/projects/app/designs/.
- Link approved mockup path in the implementation plan.
```

------

## **66. Live HTML Preview Component**

**Reusable purpose:** Let generated HTML or component work be tested as a real page.

**Context:** Use this when a skill creates HTML, previews a design, or needs print/PDF-quality rendering. It makes the generated artifact testable in a browser, with real content, responsive checks, accessibility basics, reduced-motion behavior, and screenshot verification.

**Reusable behaviors:**

```text
- Start a local preview server.
- Use semantic HTML and ARIA.
- Include real content, not lorem ipsum.
- Support contenteditable or data-driven text where relevant.
- Use ResizeObserver or equivalent for layout recalculation.
- Respect reduced motion and dark mode where appropriate.
- Verify screenshots across desktop, tablet, and mobile.
```

**Patterns copied from:** `design-html`, `make-pdf`, `browse`.

**Sample:**

```text
Preview protocol:
1. Start local server on an available port.
2. Open desktop, tablet, and mobile viewports.
3. Verify real content, empty states, and long labels.
4. Check reduced-motion behavior.
5. Capture screenshots before marking complete.
```
