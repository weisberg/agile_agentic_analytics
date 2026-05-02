---
name: prd-author
description: Use this skill whenever the user wants to write, draft, create, scaffold, review, or improve a PRD (Product Requirements Document), spec, product brief, one-pager, or "working backwards" PR/FAQ. Trigger on phrases like "write a PRD", "draft a spec", "product doc for X", "one-pager", "PR/FAQ", "feature brief", or when the user describes a feature/product idea and asks for it to be turned into a written requirements document. Also trigger when the user asks to *critique* or *level up* an existing PRD. Do NOT trigger for engineering design docs, RFCs, ADRs, or technical architecture documents — those are downstream of the PRD and have their own conventions. The output of this skill is always a markdown file (or section thereof) that a real product team could ship from.
---

# PRD Author

A skill for producing **spectacular** Product Requirements Documents — the kind that
reduce ambiguity, force tradeoffs into the open, and make a team meaningfully smarter
about what they're building before a line of code is written.

This skill is opinionated. Generic "what is a PRD" advice is everywhere; what's rare
is a skill that consistently produces docs which *survive scrutiny in a real product
review*. That is the bar.

---

## 1. Philosophy

A PRD is **a tool for thinking, not an artifact for compliance.** Its job is to:

1. Force the author to articulate the problem precisely enough that the solution
   becomes negotiable.
2. Surface the hardest tradeoff explicitly, so the team makes it on purpose rather
   than by accident.
3. Give success a falsifiable definition before anyone writes code.
4. Align stakeholders — engineering, design, data, GTM, legal — on the same understanding.

If a draft does not do all four, it is not done. It is a description, not a PRD.

> **The single most important sentence in a PRD is the problem statement.**
> Everything else is downstream of it. If the problem is fuzzy, the solution will be
> fuzzy, the metrics will be fuzzy, and the team will ship something fuzzy.

---

## 2. When to Use This Skill

**Use it for:**
- New product, feature, or capability briefs
- "Working Backwards" PR/FAQ documents (Amazon-style)
- Experiment / test plans that need product framing (not just statistical design)
- Renaming, deprecating, or migrating a feature
- Internal tools whose users are colleagues
- One-pagers / mini-PRDs for discovery or scoping

**Do not use it for:**
- Engineering design docs, RFCs, ADRs (architecture is downstream)
- Pure project plans (Gantt charts, milestones without product framing)
- Marketing briefs, launch comms, press releases as the *primary* artifact
- Bug reports or task tickets

If the user request is ambiguous (e.g. "write a doc for our new feature"), **default to
the PRD format and ask one clarifying question** about the audience and decision the
doc must drive. See §4 (Interview).

---

## 3. The Three Sizes of PRD

Match the size of the doc to the size of the bet. Do not over-document a small thing,
and do not under-document a large one.

| Size | When to use | Length | Required sections |
|------|-------------|--------|-------------------|
| **One-Pager** | Discovery, scoping, early alignment | < 1 page (~400 words) | TL;DR, Problem, Proposed Solution, Success Metric, Open Questions |
| **Standard PRD** | Most features and products | 3–6 pages | All §6 sections, condensed |
| **Deep PRD** | Net-new product, multi-quarter bet, regulated/high-risk | 8–15 pages | All §6 sections, full appendices |

**Never exceed 15 pages.** If a PRD is longer than 15 pages, it has stopped being a PRD
and become a project plan in disguise. Split it.

---

## 4. Interview Before You Write

Before drafting, gather the following. If the user has not provided answers, **ask
explicitly** in a single consolidated question (not an interrogation):

1. **Audience.** Who is this PRD for? (Exec review? Eng team? Cross-functional kickoff?)
2. **Decision.** What decision must this doc drive? (Build / don't build? Scope? Sequencing?)
3. **User.** Who is the customer or user — specifically, not "everyone"?
4. **Problem.** What is the problem in *their* words, with evidence (data, quotes, tickets)?
5. **Why now.** What changed that makes this the right time?
6. **Success.** What numerical outcome would make this a clear win?
7. **Constraints.** Hard constraints — regulatory, technical, timeline, budget?
8. **Out of scope.** What are we explicitly *not* doing?

If the user provides only a feature idea ("let's add X"), reframe back to the problem
before writing. **Never write a PRD that starts from the solution.** The skill must
gently insist on the problem-first framing even when the user resists it.

If after one round of questions the user still cannot articulate the problem clearly,
draft a **placeholder** PRD with `[NEEDS RESEARCH]` flags in the relevant sections
rather than fabricating crispness.

---

## 5. Core Principles for Every Section

These apply everywhere in the document.

### 5.1 Specificity over completeness
A PRD with three crisply-defined requirements beats one with twenty hand-wavy ones.
If a sentence could be deleted without changing engineering's behavior, delete it.

### 5.2 Falsifiable success metrics
Every goal must be expressible as a number with a baseline, a target, and a timeframe.
- ❌ "Improve the checkout experience"
- ✅ "Reduce checkout abandonment from 34% to under 25% within 90 days of launch, measured on the existing `cart_abandoned` event"

### 5.3 Non-goals are not optional
A PRD without a Non-Goals section is broken. Scope is defined as much by what you
refuse to do as by what you commit to. Include at least three non-goals, and prefer
ones that are *plausibly tempting* (not strawmen).

### 5.4 Separate problem, solution, and implementation
- **Problem:** what's wrong in the user's world
- **Solution:** the user-visible behavior change that fixes it
- **Implementation:** how engineering will build it (mostly *not* in the PRD)

When in doubt, the PRD describes what the user can do, not what the system does.

### 5.5 Tradeoffs explicit, not buried
Every meaningful product decision involves a tradeoff. Surface it. A `Tradeoffs`
subsection or callout is required for any PRD beyond the one-pager.

### 5.6 Evidence over assertion
Claims like "users want X" without a source are noise. Cite: support tickets, NPS
verbatims, analytics, sales calls, competitor analysis, user research. If there is
no evidence, mark it `[ASSUMPTION]` so reviewers can challenge it.

### 5.7 Reversibility test
For each requirement, ask: "If we shipped the *opposite* of this, would the doc
still make internal sense?" If yes, the requirement is not load-bearing — cut or
sharpen it.

---

## 6. The Anatomy of a Standard PRD

The required structure. Use these section headings verbatim. Order matters.

```markdown
# [Product/Feature Name]

**Author:** [name]  **Status:** Draft / In Review / Approved / Shipped
**Last updated:** [YYYY-MM-DD]  **Doc owner:** [name]
**Reviewers:** [eng lead], [design lead], [data], [GTM/PM partners]

## TL;DR
## Context
## Problem
## Goals & Non-Goals
## Users & Use Cases
## Proposed Solution
## Requirements
## Success Metrics
## Tradeoffs & Alternatives Considered
## Risks & Mitigations
## Rollout Plan
## Open Questions
## Appendix
```

What goes in each:

### 6.1 TL;DR — 3 to 5 sentences, no more
The whole PRD in a paragraph. Must answer: *what are we building, for whom, why,
and how will we know it worked.* If a busy exec read only this, would they know
enough to ask the right question? If not, rewrite.

### 6.2 Context
Why this, why now, what's the backdrop. Strategic fit (one sentence). Recent signals
(data point, quote, market shift). Keep it under half a page — context is not history.

### 6.3 Problem
The single most-revisited section. Structure:
- **Who** experiences the problem
- **When** they experience it (the trigger / moment)
- **What** they're trying to do (the job-to-be-done)
- **Why** the current state fails them
- **Evidence** (cite at least two independent sources)

A great problem statement is one sentence the user themselves would nod at.

### 6.4 Goals & Non-Goals
- **Goals:** 3–5 outcomes (not features), each tied to a metric.
- **Non-Goals:** 3–5 things explicitly excluded, with one-line rationale each.

Format goals as: *"Goal: [outcome]. Metric: [number, baseline → target, timeframe]."*

### 6.5 Users & Use Cases
- Primary persona (one — be willing to disappoint others)
- Top 3 use cases as user stories: *"As a [persona], when [trigger], I want to [job], so that [outcome]."*
- Anti-personas if helpful (who this is *not* for)

### 6.6 Proposed Solution
The user-visible behavior. Use storyboards, wireframes, or step-by-step narratives.
Describe what the user sees and does. Avoid implementation details; link out to the
eng design doc instead.

If multiple solution approaches are viable, pick one as the recommendation and put
the others in §6.9 (Alternatives Considered).

### 6.7 Requirements
The numbered, testable list. Each requirement:
- Has an ID (`R1`, `R2`, ...) so reviewers and tickets can reference it
- Is written as a user-observable behavior, not an implementation
- Has a priority: **Must / Should / Could** (MoSCoW) or **P0 / P1 / P2**
- Is falsifiable — a tester could decide pass/fail in <30 seconds

Split into:
- **Functional requirements** (what the product does)
- **Non-functional requirements** (performance, security, accessibility, compliance, observability)

For analytics/data products especially, include explicit **data requirements**:
events to track, dimensions, retention, PII handling, downstream consumers.

### 6.8 Success Metrics
The exam the launch will be graded against. Include:
- **North-star metric:** the one number we will be judged on
- **Input metrics:** 2–3 leading indicators we can move week to week
- **Guardrail metrics:** what must *not* get worse (latency, error rate, revenue, CSAT)
- **Measurement plan:** how each is instrumented, where dashboards live, who reviews

If the launch is going through experimentation (A/B, holdout), specify the design
here at a high level: unit of randomization, MDE, expected sample, decision rule.

### 6.9 Tradeoffs & Alternatives Considered
For each meaningful decision, a short row:
- **Decision:** [the choice]
- **Alternatives:** [what else was considered]
- **Why this:** [the reason we chose it]
- **What we give up:** [the cost of choosing it]

Reviewers will ask "why not X?" — answer the top 3 in the doc, in advance.

### 6.10 Risks & Mitigations
A small table:

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|------------|--------|------------|-------|

Include at least one risk in each of: technical, user, business, regulatory/legal.
Be honest. A PRD with no real risks is a PRD that has not been thought through.

### 6.11 Rollout Plan
- Internal alpha → beta → GA stages
- Feature-flag / cohort strategy
- Communication plan (internal, customer, support enablement)
- Rollback criteria — *how* and *when* we'd reverse the change

### 6.12 Open Questions
Numbered, with an owner and a target resolution date. Open questions are not weakness
— they are the active edge of the doc. A PRD with zero open questions late in
discovery is suspicious; one with thirty is unfinished.

### 6.13 Appendix
- Research links and verbatims
- Competitive analysis
- Earlier explorations
- Glossary (if domain-specific)
- Decision log (entries with date, decision, rationale, who decided)

---

## 7. The PR/FAQ Variant ("Working Backwards")

When the user asks for a PR/FAQ, Amazon-style, replace §6.1–6.6 with:

1. **Press Release** (1 page)
   - Headline (the customer benefit, not the technology)
   - Subhead (who and what)
   - Summary paragraph (location, date, value prop)
   - Problem paragraph
   - Solution paragraph
   - Internal quote (leader)
   - Customer quote (representative)
   - Call to action / availability

2. **External FAQ** — what a customer would ask
3. **Internal FAQ** — what the team would ask (this is where the hard tradeoffs live)

Then keep §6.7–6.13 as-is in an appendix-style section called "Implementation
Details" so eng/data partners have what they need.

The PR/FAQ is the right form when the product is **net-new** or **customer-facing
with positioning risk**. It is overkill for internal tooling or incremental features.

---

## 8. Writing Process

Follow this order. Do not jump ahead.

1. **Frame** — fill in metadata, write a placeholder TL;DR (you'll rewrite it last).
2. **Problem first** — write §6.3 Problem with evidence. Stop. Show it. Iterate
   until the user nods. If you skip this step, the rest will be wrong.
3. **Goals & Non-Goals** — define success and explicitly cut scope. Often the
   hardest 30 minutes of the whole doc; do not rush.
4. **Users & Use Cases** — concrete personas and stories.
5. **Solution & Requirements** — *now* you may describe the build.
6. **Metrics, Tradeoffs, Risks, Rollout** — make the bet legible.
7. **Open Questions** — list every uncertainty surfaced during writing.
8. **Rewrite the TL;DR last** — it should now write itself.
9. **Self-review against §10 checklist.**
10. **Cut 20%.** Almost every PRD is 20% too long on the first pass. Be ruthless.

---

## 9. Tone & Format Conventions

- **Voice:** plain, direct, declarative. Avoid hedging ("we might consider possibly
  exploring..."). If the team has not decided, say "Open question: ...".
- **Tense:** present tense for the proposed end state ("The user sees..."), future
  tense only for rollout milestones.
- **Acronyms:** define on first use, even internal ones. Future readers will thank you.
- **Markdown:** use H2 for top-level sections, H3 for subsections. Tables for
  structured data (requirements, risks, metrics). Avoid deep nesting.
- **Links:** prefer linking to research, dashboards, and design files over
  embedding screenshots. Embeds rot.
- **Length signal:** if a section is longer than ~400 words, split it or move
  detail to the appendix.
- **No emoji** in the doc body. They date the artifact and read as unserious.
- **No buzzwords:** "synergy", "10x", "delight", "best-in-class", "world-class",
  "seamless", "leverage" (as a verb). If a word would survive being deleted, delete it.

---

## 10. Quality Bar — Self-Review Checklist

Before declaring a PRD done, the skill must verify all of the following. If any
fail, fix and re-check.

- [ ] **TL;DR test:** can a smart outsider read only the TL;DR and ask a *useful*
      follow-up question? (Not "what does this mean?" — that's a fail.)
- [ ] **Problem test:** is the problem statement one the *user* would agree with,
      in their words, with cited evidence?
- [ ] **Falsifiability test:** does every goal have a number, baseline, target, and
      timeframe? Could a stranger declare success or failure 90 days from launch
      without ambiguity?
- [ ] **Non-goals test:** are there at least three non-goals, and are at least
      two of them *plausibly tempting*?
- [ ] **Reversal test:** if you flipped any single requirement, would the doc
      still make sense? (If yes, that requirement is filler — cut or sharpen.)
- [ ] **Tradeoff test:** is the hardest tradeoff named explicitly, with what we
      give up by choosing this path?
- [ ] **Evidence test:** is every "users want X" claim cited or labeled
      `[ASSUMPTION]`?
- [ ] **Risk test:** is there at least one *uncomfortable* risk listed (i.e., one
      that, if surfaced in review, would prompt a real conversation)?
- [ ] **Rollback test:** is it clear how this gets reversed if it goes wrong?
- [ ] **Length test:** every section ≤ ~400 words; total ≤ 15 pages; passed the
      "cut 20%" pass.
- [ ] **Owner test:** every open question and risk has a named owner.
- [ ] **5-year test:** would this doc still be readable and informative to someone
      onboarding to the area three years from now?

---

## 11. Antipatterns to Avoid

These are the ways PRDs fail in practice. Catch them in your own drafts.

1. **Solution masquerading as problem.** "Users need a dashboard." No — users have
    a job they're failing to do; a dashboard *might* be the answer. Reframe.
2. **The everyone persona.** "Our users are anyone who uses email." If the persona
    fits everyone, the product fits no one.
3. **Vague metrics.** "Improve engagement", "drive growth", "reduce friction"
    without numbers. Reject.
4. **Missing non-goals.** Every absent non-goal becomes scope creep later.
5. **Feature soup.** A long bullet list of features with no prioritization or
    justification. Convert to numbered, prioritized requirements.
6. **Implementation leak.** Database schemas, API endpoints, framework choices in
    the PRD. Move to the eng design doc.
7. **No tradeoffs named.** A PRD where every choice was "obvious" hasn't been
    thought hard enough.
8. **Optimistic-only risk section.** "Risk: low adoption. Mitigation: marketing."
    That's not a mitigation, that's a wish.
9. **Stale TL;DR.** The TL;DR was written first, then the doc evolved, and now
    they disagree. Always rewrite the TL;DR last.
10. **Doc-as-decision-record without a decision.** A 12-page PRD that ends with
    "we'll figure out the metric later" is not a PRD.

---

## 12. Output Format

When invoked, this skill produces a single markdown file. Conventions:

- **Filename:** `prd-<kebab-case-name>.md` unless the user specifies otherwise.
- **Location:** save to the user's preferred directory; if none, default to the
    current working directory. Create the file via `create_file` (or `Write` in
    Claude Code). Do not paste the entire PRD into chat unless explicitly asked —
    point the user to the file and offer a brief summary plus the top 3 open
    questions surfaced.
- **Section anchors:** use stable H2 headings (verbatim from §6) so other tools
    and skills can address sections by slug.
- **Status field:** always include and set to `Draft` on first write.
- **Do not invent specifics.** Names, numbers, dates, citations, customer quotes
    — if not provided or verifiable, use `[TBD]` or `[ASSUMPTION]`. Fabricated
    specifics are the single fastest way to get a PRD rejected by a real team.

---

## 13. Iteration & Reviews

PRDs are living documents. When the user asks to revise:

- Preserve the **decision log** at the bottom of the appendix. Every revision
    that changes a goal, non-goal, or requirement gets a dated entry: *what
    changed, why, who decided.*
- Bump the `Last updated` field.
- If the change is material (scope, metrics, target users), move status back to
    `Draft` or `In Review` and flag the affected sections with a `[CHANGED YYYY-MM-DD]`
    marker for the next round of review.

When the user asks to **review** an existing PRD (rather than write one), run the
§10 checklist explicitly, mark each item ✅ / ❌ / ⚠️, and produce a numbered list
of concrete edits ranked by impact. Do not rewrite silently — show your reasoning.

---

## 14. Two Quick Worked Examples

### 14.1 Bad → Good problem statement

**Bad:**
> Users have asked for a way to export their data. We should add an export feature.

**Good:**
> Power users on annual plans (≈8% of accounts, ≈40% of revenue) need to move
> historical reports out of the platform for compliance audits, which happen
> quarterly. Today they take screenshots one report at a time — averaging
> 4.5 hours per audit, per the last 12 months of support tickets (n=47). Three
> have cited this in churn calls.

The good version names the user, the trigger, the job, the cost, and the evidence.
Engineering and design now have something to design *for*, not just toward.

### 14.2 Bad → Good goal

**Bad:** *Goal: Make exporting easy.*

**Good:** *Goal: Reduce time-to-export-full-account from 4.5 hours (current
median, screenshot workflow) to under 5 minutes for 90% of power users, within
60 days of GA. Measured via the new `export_completed` event, segmented by plan tier.*

---

## 15. When To Push Back

This skill is allowed — and expected — to push back on the user when:

- They ask for a PRD but have not articulated a problem. Ask for it.
- They ask for a "quick PRD" for something that is genuinely a multi-quarter bet.
    Recommend the deeper format and explain the cost of underdocumenting.
- They want to skip non-goals or success metrics. Refuse politely; offer
    `[TBD — needs decision]` placeholders so the gaps are visible rather than hidden.
- The "users" are described generically. Ask who specifically, and what evidence
    supports it.

A skill that produces only what is asked for produces mediocre PRDs. A skill that
produces *what the team actually needs* produces spectacular ones. Err toward the
latter, with a light touch.