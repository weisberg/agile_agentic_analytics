---
name: prd-to-plan
description: >
  Use this skill when the user has a PRD (Product Requirements Document), spec, or product brief and wants to turn it into an executable plan for agentic development — a plan that AI coding agents (Claude Code, sub-agents, orchestrators) can actually run. Trigger on phrases like "turn this PRD into a plan", "agentic plan", "execution plan", "task graph", "break this down for Claude Code", "decompose this spec", "build plan", "implementation plan from PRD", "scrum-master plan", or when the user provides a PRD/spec and asks "what's next" or "how do we build this with agents". The output is always a structured `PLAN.md` artifact with phases, tasks, dependencies, validation gates, sub-agent assignments, and context bundles. Do NOT trigger for: writing the PRD itself (use prd-writer), pure engineering design / RFC / ADR (architecture is a separate artifact), or generic project management plans without an agentic execution model.

disable-model-invocation: false
---

# PRD → Agent Plan

A skill for converting a PRD into an **agentic development plan** — the kind of plan
an orchestrator agent (or a careful human running Claude Code) can actually execute,
phase by phase, without losing the thread.

This skill assumes a serious truth: **agentic development plans are not just regular
plans with "ask Claude to do it" written next to each task.** They are structurally
different artifacts because the executor is structurally different. Agents have
finite context, fail in different ways than humans, parallelize differently,
hallucinate dependencies, and need verification baked in rather than bolted on.

If a plan would not have been a good plan in 2020, when only humans executed it,
it will not be a good plan for agents either. But a plan that *was* good for humans
is usually still **insufficient** for agents — it leaves too much implicit, gates
too informally, and budgets context too generously.

This skill produces plans that close that gap.

## Contract

Use this as a write-capable planning skill that consumes a PRD, spec, or product
brief and produces an agent-executable markdown `PLAN.md`. It does not write the
PRD itself, replace an engineering architecture document, or create a generic
roadmap/Gantt plan without an agentic execution model.

Hard gate: if no PRD/spec exists, stop and route to `prd-writer` instead of
inventing requirements. If the executor model or available tooling is unknown,
ask once with `AskUserQuestion` when available; otherwise ask one consolidated
question. If the user asks to proceed anyway, continue only with visible
`[ASSUMPTION]` / `[TBD]` markers and return `DONE_WITH_CONCERNS`, not `DONE`.

Intake must classify the planning mode:

- `quick`: small feature, 3-5 page plan, few tasks, lightweight gates.
- `standard`: normal feature or product area, full phase map and task DAG.
- `deep`: multi-quarter, regulated, high-blast-radius, multi-agent effort.
- `replan`: update an existing `PLAN.md` after a gate failure or PRD change.

Evidence requirement: inspect the source PRD, named requirements, open
questions, repo layout, key code paths, tests, scripts, CI, existing agents or
skills, and any provided constraints before decomposing work. Every file path,
command, dependency, and agent role in the plan must either be verified from
source evidence or labeled `[TBD]`; do not fabricate implementation facts.

---

## 1. Philosophy

A spectacular agentic plan does five things at once:

1. **Closes the spec-execution gap.** What the PRD leaves implicit, the plan makes
   explicit — APIs, data shapes, file paths, acceptance criteria, error semantics.
2. **Bounds context per task.** Each unit of work names exactly the files, docs,
   and schemas the executing agent needs — and excludes the rest. More context is
   not better; targeted context is better.
3. **Verifies before it advances.** Every task ends with a runnable check. Phases
   end with a gate. Gates fail loudly. Nothing proceeds on vibes.
4. **Assigns work to the right executor.** Some work is for a generalist agent,
   some for a specialized sub-agent, some for a human reviewer, some not for an
   agent at all. The plan distinguishes.
5. **Anticipates how agents fail.** Hallucinated APIs, fabricated dependencies,
   pattern-matching to the wrong example, drift from spec, premature completion
   claims. The plan has guardrails for each.

> **The point is not to micromanage the agent. The point is to make the plan
> robust to the ways agents go wrong** — so the human supervising the work spends
> their attention on the few decisions that genuinely require it, not on
> rediscovering the same hallucination three times.

---

## 2. When to Use This Skill

**Use it when:**
- A PRD or detailed spec exists and the user wants execution structure
- Multiple agents (or one agent over many sessions) will do the work
- The work is large enough that "just ask Claude to build it" would lose context
- Validation, rollout, or compliance demands explicit gates
- Sub-agents (e.g., scrum-master + workers) will orchestrate

**Do not use it when:**
- The PRD is too underspecified to plan from — kick back to `prd-writer` first
- The task is small enough to fit in one agent session (under ~30 minutes of work
  for an experienced engineer); a plan would be overhead
- The user wants a Gantt chart / roadmap (different artifact, different audience)
- The user wants engineering architecture (that's an eng design doc — write that
  *first* if it's missing, then plan from PRD + design doc together)

If the PRD is missing, **stop and recommend writing one** rather than improvising
specs into the plan. Plans built on assumed PRDs propagate the assumptions.

---

## 3. Inputs — What This Skill Needs

Before drafting the plan, verify you have:

1. **A PRD or equivalent spec** with named requirements (R1, R2, ...). If
   requirements are not numbered, number them yourself in a normalization pass
   and confirm with the user.
2. **Codebase context.** Repo layout, languages, frameworks, key modules. If
   working in an existing codebase, the plan must respect what's there.
3. **The executor model.** Which agents will do the work? A single Claude Code
   session? An orchestrator with sub-agents? A human running a harness? The plan's
   shape depends on this.
4. **Tooling inventory.** What CLI tools, skills, MCP servers, validators, and
   eval frameworks are available? An agent's repertoire bounds what tasks are
   "agent-executable."
5. **Constraints.** Hard deadlines, regulatory gates, environments, cost ceilings.
6. **Open questions from the PRD.** These do not disappear — they become research
   tasks in Phase 0.

If items 1, 3, or 4 are missing, **ask once** in a single consolidated question
before drafting. For 2, 5, 6, fill in `[ASSUMPTION]` / `[TBD]` placeholders if the
user hasn't volunteered them, and call out what you assumed at the top of the plan.

---

## Process

Follow this order. Do not jump from PRD to task list.

1. **Intake and mode** — parse `$ARGUMENTS`, classify `quick` / `standard` /
   `deep` / `replan`, identify the source PRD path, target plan path, executor
   model, and deadline/constraint profile.
2. **Normalize the PRD** — assign requirement IDs if missing, extract non-goals,
   success metrics, rollout gates, risks, and open questions. If the PRD is too
   thin, stop with `NEEDS_CONTEXT` or route to `prd-writer` review mode.
3. **Evidence inventory** — inspect the codebase and tooling needed to make the
   plan executable. Record verified commands, validators, tests, schemas, and
   existing agent/skill names; mark unknowns as Phase 0 discovery tasks.
4. **Decision gates** — use `AskUserQuestion` when available for executor model,
   phase depth, human-vs-agent ownership, acceptance-test strategy, or any
   high-blast-radius work. Hard stop on missing PRD, unbounded scope, no
   validation path, or irreversible production ops without a human gate.
5. **Decompose and crosswalk** — build phases, tasks, dependency graph, context
   bundles, risk register, and PRD requirement crosswalk.
6. **Validate before handback** — run the self-review checklist in
   `references/examples.md` §G and repair failures before saving.
7. **Save and summarize** — write the `PLAN.md`, then summarize phase count,
   task count, critical path, top risks, open questions, assumptions, and status.

---

## 4. The Output Artifact: `PLAN.md`

Every invocation produces a single markdown file built from a fixed skeleton
(metadata header + twelve numbered H2 sections, `## 0. Snapshot` through
`## 12. Appendix`). **Before writing, read `references/examples.md` §A for the
exact skeleton and reproduce its H2 headings verbatim** so other tools and skills
can address sections by slug.

What goes in each section is detailed in §5–§13 below. Keep the plan **scannable**
— an orchestrator should be able to find any task by ID in under five seconds.

---

## 5. Decomposition Strategy — The Three Granularities

Decompose top-down through three levels. Do not skip levels.

### 5.1 Phases
A **phase** is a horizontally-cut slab of work that ends in a meaningful, testable
state. Phases are sequential; you do not start phase N+1 until phase N's gate passes.

Use the default phase template in `references/examples.md` §B — a six-phase arc
(0. Discovery → 1. Foundations → 2. Build/Vertical Slice → 3. Build/Breadth →
4. Hardening → 5. Rollout), each with a purpose and a typical exit criterion.
Adapt it to the work: a short feature may collapse to 3 phases; a multi-quarter
bet may have 7+. **Always include Phase 0 (Discovery) and Phase 4 (Hardening)** —
agents systematically under-invest in both unless the plan forces it.

### 5.2 Tasks
A **task** is a single unit of work assigned to a single executor in a single
focused session. Good tasks have:

- **Bounded scope:** changes one module, one file, or one well-defined surface
- **Bounded context:** the agent needs no more than ~5 files / ~5k tokens of
  reference material to do it well
- **Bounded duration:** would take an experienced engineer between 15 minutes and
  4 hours; in agent-time, completes in 1–2 sessions
- **A single observable outcome:** a passing test, a built artifact, a running
  service, a written doc

If a task has more than one of those, split it. The most common planning mistake
is tasks that are quietly two tasks in a trench coat.

### 5.3 Atoms
Within a complex task, an **atom** is a step the agent should not split further:
"create file X with shape Y", "run command Z and capture output", "add fixture
matching schema S". Atoms appear inside a task's spec when the agent benefits
from explicit sequencing — usually for stateful or order-sensitive work.

Most tasks do not need atoms. Use them when the task involves a fragile sequence
(e.g., migrations, multi-step refactors, ordered tool invocations).

---

## 6. Task Specification — The Mandatory Fields

Every task in §4 of the plan has a fixed structure. **No field is optional** —
missing fields mean the agent will guess, and guesses compound. The mandatory
fields are: requirement back-references, type, executor, blast radius, estimated
effort, depends-on/blocks, a one-sentence goal, a spec (inputs, outputs, behavior,
errors, out-of-scope), a context bundle (§8), an acceptance test, and agent-specific
failure modes to watch (§10). **Copy the exact task template from
`references/examples.md` §C** and populate every field for each task.

The **acceptance test must exist before the task runs.** Validation-first task
design is the single highest-leverage practice this skill enforces.

---

## 7. Dependency Graph — Make Parallelism Explicit

Section §5 of the plan shows tasks as a DAG. Two equivalent views:

1. **Compact list:** for each task, `Depends on:` and `Blocks:` fields (already
   in §6). This is the source of truth.
2. **Rendered graph:** a Mermaid `graph LR` block showing nodes and edges. Agents
   parse Mermaid; humans appreciate it visually. Generate it from the list.

Rules for a clean graph:

- **No cycles.** If you find one, the tasks are wrongly bounded — split or merge.
- **Minimize fan-in on bottleneck tasks.** A task that everything else depends on
  is a serialization point; if possible, push its dependents to depend on a stable
  contract (the schema, the interface) rather than the task itself.
- **Surface critical path explicitly.** Mark the longest dependency chain — that's
  the wall-clock floor, regardless of parallelism.
- **Identify parallelizable batches.** Tasks with no dependencies between them can
  run concurrently. Group them visually so the orchestrator sees what to dispatch
  in parallel.

If the executor model in §3 is a single-agent session, parallelism doesn't help —
but the graph still matters because it tells the agent which task to do *next*
when the current one is blocked.

---

## 8. Context Bundles — The Single Most Underrated Discipline

Every agent task fails or succeeds in proportion to the quality of its context
bundle. Get this right and most tasks just work.

### 8.1 What goes in
- Files the task reads or modifies
- Files the task's *output* must be consistent with (schemas, interfaces, callers)
- The exact PRD requirement(s) being implemented (link or quote)
- Any prior task's output that becomes input here
- Reference examples — *one* canonical example of the pattern being followed

### 8.2 What stays out
- Files unrelated to this surface
- The whole PRD when one section would do
- "Just in case" context — the agent will pattern-match to it
- Stale documentation that contradicts current code (delete or label `[STALE]`)
- Examples of patterns the team is *moving away from*

### 8.3 The minimization rule
> Add context only when its absence would cause a wrong answer. Default to **less**.

A task with 30 files in its bundle is a task that has not been thought through.
The agent will skim, pattern-match, and produce a plausible-looking answer that
matches no specific source. Cap most bundles at 5–8 references; flag any task
that genuinely needs more as a signal that the task may be too big.

### 8.4 Bundle reuse
Tasks in the same module often share most of their bundle. Define a **shared
bundle** in §8 of the plan once (e.g., `bundle-checkout-core`) and reference it
from each task as `Context bundle: bundle-checkout-core + [task-specific files]`.

---

## 9. Validation Gates — How You Know a Phase Is Done

Each phase ends in a **gate**: a set of checks that must all pass before the next
phase begins. Gates are not status meetings; they are runnable.

For each gate, specify:

- **Automated checks:** test commands, lint, typecheck, eval suite scores with
  thresholds (`accuracy ≥ 0.85 on canonical eval set`).
- **Manual checks:** the human-eyeball items, with explicit observable criteria.
  ("Reviewer confirms the new endpoint matches the OpenAPI contract in `api.yaml`.")
- **Artifacts produced:** what files, docs, dashboards, or running services exist
  at the gate.
- **Failure handling:** what to do if the gate fails — replan (§11), patch,
  rollback, escalate.

A phase whose gate is "looks done to me" is a phase without a gate. Replace with
something falsifiable.

### 9.1 The pre-mortem on the gate itself
For each gate, briefly answer: *"What does it look like to pass this gate while
the work is actually broken?"* Then add a check that catches that case. Gates
that can be vacuously satisfied are worse than no gates because they create
false confidence.

---

## 10. Risk Register — Agentic Failure Modes

Section §10 of the plan is a table of risks specific to agentic execution. **Always
include at least the ten canonical agentic failure modes with task-specific
mitigations — the full table is in `references/examples.md` §D** (API hallucination,
spec drift, premature completion, pattern bleed, context overload, silent dependency
add, test theater, context loss across sessions, cross-cutting blast, eval gaming).

Add domain-specific risks (data privacy, compliance, financial calculations,
PII handling, etc.) as appropriate.

---

## 11. Sub-Agent Assignment Patterns

If the executor model uses an orchestrator with sub-agents, §7 of the plan
specifies which sub-agent owns which task type. **See `references/examples.md` §F
for the four common orchestration patterns** — hub-and-spoke (scrum-master),
pipeline, specialist swarm, and pair/adversarial — and pick the one that fits the
work's shape.

For each non-trivial task, name the sub-agent role: `general`, `data-eng`,
`frontend`, `experimentation`, `reviewer`, `researcher`, `human`. If the team
hasn't built a specialist sub-agent for a category that recurs, **flag it as a
prerequisite** in Phase 0 — building the sub-agent is itself a task.

### 11.1 What humans should still own
Reserve human ownership for tasks that are:
- **High blast radius** (cross-cutting infra, schema migrations on prod data,
  irreversible operations)
- **Genuinely ambiguous** (not just underspecified — actually requires judgment
  no spec can capture, e.g., "is this UI tone consistent with the brand?")
- **Stakeholder-facing** (executive sign-off, regulator-facing copy)
- **Novel patterns** (the first time a pattern is used; subsequent uses can be
  agentic once the canonical example exists)

Everything else is fair game for agents — provided §6's spec rigor is met.

---

## 12. Replanning Protocol

Plans are not contracts; they are working hypotheses. Section §11 of the plan
specifies *how* the plan gets revised mid-execution.

Triggers that mandate replanning (do not just patch and continue):

- A gate fails twice on the same root cause
- A task reveals a PRD requirement is wrong, missing, or contradicts another
- The blast radius of a task turns out to be larger than classified
- An assumption from §1 is invalidated
- A new dependency is required that wasn't in the original graph

Replanning workflow:
1. **Stop the affected branch of the DAG.** Other branches may continue.
2. **Capture the trigger** in the decision log (§12) — what we learned, what we
   assumed, why we were wrong.
3. **Decide the scope of replan:** local (just this task), phase (all of phase
   N), or whole-plan.
4. **If PRD-level:** kick back to `prd-writer` for the spec change before
   re-deriving the plan.
5. **Bump `Last updated`, mark affected sections `[CHANGED YYYY-MM-DD]`, and
   re-run the §13 quality bar** before resuming.

Replanning is a feature, not a failure. Plans that never replan are plans whose
authors weren't paying attention.

---

## 13. Quality Bar — Self-Review Checklist

Before declaring a plan ready, **run the full 14-item self-review checklist in
`references/examples.md` §G** and verify every item passes; if any fail, fix
before delivering. The checklist covers PRD crosswalk completeness, Phase 0 and
Phase 4 existence, populated §6 task fields, runnable acceptance tests,
falsifiable gates, an acyclic graph with a marked critical path, context-bundle
minimization, blast-radius classification, explicit sub-agent assignments, a
task-specific risk register, a filled-in replanning protocol, no fabricated
specifics, and top-to-bottom executability. If a plan fails the last item, it
isn't a plan — it's notes.

---

## Anti-Patterns (§14)

Catch these in your own drafts. The full catalog of twelve — the wishlist plan,
the hero task, the trust-fall gate, bundle-of-everything, test-after, sub-agent
cargo cult, no human gates, no agentic failure modes, Phase 0 skipped, the frozen
plan, open-questions amnesia, and eval as afterthought — with a one-line tell for
each is in `references/examples.md` §E. Review your draft against every entry
before declaring it ready.

---

## Output Format (§15)

When the skill is invoked:

- **Filename:** use a `plan-...md` filename matching the PRD's slug if possible
  — e.g., `prd-checkout-export.md` becomes `plan-checkout-export.md`.
- **Location:** save via `create_file` (or `Write` in Claude Code) to the user's
  preferred location, defaulting to alongside the PRD. If the source PRD is not a
  file, use a `plan-...md` filename in the current working directory.
- **Length expectations:** small features ~3–5 pages, standard ~6–10 pages, deep
  ~10–20 pages. If a plan exceeds 20 pages, split by epic.
- **Section headings:** use the verbatim H2 list from §4 so other tools and
  skills can address sections by slug.
- **Status field:** `Draft` on first write.
- **Do not paste the entire plan into chat.** Save the file, summarize in 5–10
  bullets: phase count, task count, critical path length, top 3 risks, top 3
  open questions, any `[ASSUMPTION]` flags the user should review.
- **Crosswalk table is mandatory.** Even on small plans. It's the single
  fastest way to spot orphan requirements or orphan tasks.
- **Pair with `prd-writer`.** If the PRD is missing structure (no R-IDs, no
  non-goals, no metrics), recommend running `prd-writer` in review mode first.
  A weak PRD becomes a weak plan no matter how disciplined the planner.
- **Completion status:** end the handback with one of: `DONE` (plan saved and
  checklist passes), `DONE_WITH_CONCERNS` (usable plan with explicit
  assumptions or unresolved low/medium-risk gaps), `NEEDS_CONTEXT` (missing
  PRD/spec, executor model, source access, or validation basis), or `BLOCKED`
  (cannot proceed because required tools, repo access, policy, or human
  approval is unavailable).

---

## 16. When to Push Back

This skill is allowed and expected to push back when:

- The PRD is too thin to plan from. Recommend `prd-writer` review first.
- The user wants a plan that has no Phase 0 because "we know what to build."
  Insist on at least a 30-minute Discovery phase to validate the riskiest
  assumption. It is cheap and almost always pays off.
- The user wants every task assigned to an agent. Some work — irreversible ops,
  brand-tone judgments, regulator comms — should stay with humans.
- The user asks for a plan with no validation gates. Refuse. Suggest a
  minimum-viable gate even for small plans.
- Tasks are being defined by file or function rather than by user-observable
  behavior. Reframe to behavior; the file/function is an implementation detail.

A plan that is merely what the user asked for is mediocre. A plan that is what
the agents will actually need at execution time is spectacular. Default toward
the latter, with a light touch and clear reasoning when you push back.
