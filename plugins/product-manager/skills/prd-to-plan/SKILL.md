---
name: prd-to-agent-plan
description: Use this skill when the user has a PRD (Product Requirements Document), spec, or product brief and wants to turn it into an executable plan for agentic development — a plan that AI coding agents (Claude Code, sub-agents, orchestrators) can actually run. Trigger on phrases like "turn this PRD into a plan", "agentic plan", "execution plan", "task graph", "break this down for Claude Code", "decompose this spec", "build plan", "implementation plan from PRD", "scrum-master plan", or when the user provides a PRD/spec and asks "what's next" or "how do we build this with agents". The output is always a structured `PLAN.md` artifact with phases, tasks, dependencies, validation gates, sub-agent assignments, and context bundles. Do NOT trigger for: writing the PRD itself (use prd-author), pure engineering design / RFC / ADR (architecture is a separate artifact), or generic project management plans without an agentic execution model.
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
- The PRD is too underspecified to plan from — kick back to `prd-author` first
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

## 4. The Output Artifact: `PLAN.md`

Every invocation produces a single markdown file with this skeleton:

```markdown
# Plan: [Name]

**Source PRD:** [link]   **Last updated:** YYYY-MM-DD
**Executor model:** [single-agent / orchestrator+sub-agents / human-in-loop]
**Status:** Draft / Active / Blocked / Complete

## 0. Snapshot
## 1. Inputs & Assumptions
## 2. Decomposition Strategy
## 3. Phase Map
## 4. Tasks
## 5. Dependency Graph
## 6. Validation Gates
## 7. Sub-Agent Assignments
## 8. Context Bundles
## 9. Human Checkpoints
## 10. Risk Register (Agentic-Specific)
## 11. Replanning Protocol
## 12. Appendix (PRD Crosswalk, Decision Log)
```

What goes in each is detailed in §5–§13. Keep the plan **scannable** — an
orchestrator should be able to find any task by ID in under five seconds.

---

## 5. Decomposition Strategy — The Three Granularities

Decompose top-down through three levels. Do not skip levels.

### 5.1 Phases
A **phase** is a horizontally-cut slab of work that ends in a meaningful, testable
state. Phases are sequential; you do not start phase N+1 until phase N's gate passes.

Default phase template (adapt to the work):

| Phase | Purpose | Typical exit criterion |
|-------|---------|------------------------|
| **0. Discovery** | Resolve open questions, validate assumptions, prove key unknowns | All `[ASSUMPTION]` flags from PRD either confirmed or documented as accepted risk |
| **1. Foundations** | Schemas, contracts, scaffolding, fixtures, eval harness | Eval harness runs end-to-end against stub implementation |
| **2. Build (Vertical Slice)** | Smallest end-to-end working path | One real user journey works in dev, instrumented |
| **3. Build (Breadth)** | Remaining requirements layered on the slice | All P0/P1 requirements implemented and passing eval |
| **4. Hardening** | Edge cases, performance, observability, accessibility | Guardrail metrics within budget; chaos/load tests pass |
| **5. Rollout** | Progressive deployment, monitoring, comms | GA criteria from PRD §Rollout met; rollback verified |

A short feature may collapse to 3 phases; a multi-quarter bet may have 7+. **Always
include Phase 0 (Discovery) and Phase 4 (Hardening)** — agents systematically
under-invest in both unless the plan forces it.

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

Every task in §4 of the plan has this structure. **No field is optional.** Missing
fields mean the agent will guess, and guesses compound.

```markdown
### T-{phase}.{n} — {short verb-led title}

- **Requirement(s):** R3, R7         <!-- back-references to the PRD -->
- **Type:** code / schema / test / doc / research / config / ops
- **Executor:** {agent role, e.g. `general`, `data-eng-subagent`, `human-review`}
- **Blast radius:** local / contained / cross-cutting
- **Estimated effort:** {S / M / L}, {sessions: 1–2}
- **Depends on:** T-1.3, T-2.1
- **Blocks:** T-3.4

**Goal.** One sentence — the user-observable or system-observable outcome.

**Spec.**
- Inputs: ...
- Outputs: ...
- Behavior: ... (what the code/artifact must do, in present-tense declarative)
- Errors: ... (named error cases and expected handling)
- Out of scope: ... (what NOT to touch)

**Context bundle.**
- `path/to/file1.py` — relevant because ...
- `docs/schema.md` — defines the data contract
- `prd.md#R7` — the requirement being implemented
(See §8 for context bundle discipline.)

**Acceptance test.** A runnable check that decides pass/fail with no judgment call.
- Command: `pytest tests/test_t_2_3.py::test_happy_path -q`
- Or: `cargo test --test integration t_2_3`
- Or: manual checklist with explicit observable criteria

**Failure modes to watch.** (Agent-specific. See §10 for the catalog.)
- Likely to hallucinate the `XxxClient` API — verify against `path/to/client.py`
- May invent a config key — actual keys live in `config/schema.json`
```

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

Section §10 of the plan is a table of risks specific to agentic execution. Always
include at least these, with task-specific mitigations:

| Risk | What it looks like | Mitigation |
|------|--------------------|------------|
| **API hallucination** | Agent calls `client.frobnicate()` that doesn't exist | Pin the canonical client file in the bundle; require the agent to grep before calling |
| **Spec drift** | Output does the spirit, not the letter, of the requirement | Acceptance test bound to the literal requirement; reviewer crosswalks PRD R-IDs |
| **Premature completion** | Agent declares done when only the happy path works | Acceptance test includes ≥1 error path; gate requires error-path test green |
| **Pattern bleed** | Agent copies a deprecated pattern from elsewhere in the repo | Label deprecated areas `[STALE]`; pin the canonical example explicitly |
| **Context overload** | Bundle is huge, agent skims and confabulates | §8 minimization; cap at 5–8 references for most tasks |
| **Silent dependency add** | Agent introduces a new library to solve a task | Constraint in spec: "no new dependencies without an explicit task to add one" |
| **Test theater** | Agent writes tests that test the mock, not the behavior | Acceptance tests written *first* (validation-first); reviewer spot-checks |
| **Context loss across sessions** | Multi-session task forgets earlier decisions | Decision log in `PLAN.md` §12; each session starts by reading it |
| **Cross-cutting blast** | Local fix breaks shared infra | Blast radius classification (§6) + human gate for `cross-cutting` |
| **Eval gaming** | Agent overfits to the eval set | Hold out a private eval; rotate canonical examples |

Add domain-specific risks (data privacy, compliance, financial calculations,
PII handling, etc.) as appropriate.

---

## 11. Sub-Agent Assignment Patterns

If the executor model uses an orchestrator with sub-agents, §7 of the plan
specifies which sub-agent owns which task type. Common patterns:

- **Hub-and-spoke (scrum-master orchestrator).** A coordinator sub-agent reads
  the plan, dispatches tasks to specialists, collects results, advances gates.
  Best when tasks are heterogeneous and validation is centralized.
- **Pipeline.** Sub-agents in series — researcher → designer → implementer →
  reviewer. Best when phases are linear and each adds a distinct kind of value.
- **Specialist swarm.** Multiple specialists working in parallel on independent
  branches of the DAG, with a final integrator. Best when the breadth phase has
  many parallelizable tasks.
- **Pair / adversarial.** Implementer + critic running in alternation. Best for
  high-stakes tasks where review quality matters more than speed.

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
4. **If PRD-level:** kick back to `prd-author` for the spec change before
   re-deriving the plan.
5. **Bump `Last updated`, mark affected sections `[CHANGED YYYY-MM-DD]`, and
   re-run the §13 quality bar** before resuming.

Replanning is a feature, not a failure. Plans that never replan are plans whose
authors weren't paying attention.

---

## 13. Quality Bar — Self-Review Checklist

Before declaring a plan ready, verify all of the following. If any fail, fix.

- [ ] **PRD crosswalk:** every PRD requirement R{n} maps to ≥1 task; every task
      maps back to ≥1 R{n} (no orphan tasks, no orphan requirements). Show the
      crosswalk table in §12.
- [ ] **Phase 0 exists** and resolves at least one open question or assumption
      from the PRD.
- [ ] **Phase 4 (Hardening) exists** with explicit edge-case, perf, and
      observability tasks — not just "fix bugs".
- [ ] **Every task has all §6 fields populated** — no missing acceptance tests,
      no missing context bundles.
- [ ] **Every task's acceptance test is runnable** by a fresh agent without
      back-channel context.
- [ ] **Every gate is falsifiable** and has the §9.1 pre-mortem answered.
- [ ] **Dependency graph is acyclic** and the critical path is marked.
- [ ] **Context bundles obey the minimization rule** — no task exceeds 8
      references without a noted reason.
- [ ] **Blast radius is classified for every task** and `cross-cutting` tasks
      have human gates.
- [ ] **Sub-agent assignments are explicit;** missing specialist sub-agents are
      themselves Phase 0 tasks.
- [ ] **Risk register is task-specific,** not generic. Each row names actual
      files, APIs, or behaviors that could go wrong.
- [ ] **Replanning protocol §11 is filled in** for this specific plan, not boilerplate.
- [ ] **No fabricated specifics.** File paths, function names, dependencies, and
      commands either exist in the codebase / tooling or are flagged `[TBD]`.
- [ ] **The plan is executable from the top.** A fresh orchestrator agent
      reading only this file (plus the bundles) could run it without asking the
      author what they meant.

If a plan fails the last item, it isn't a plan — it's notes.

---

## 14. Antipatterns

Catch these in your own drafts.

1. **The wishlist plan.** Every PRD requirement → one task, one file, no
   dependencies, no validation. Looks tidy, executes badly.
2. **The hero task.** A single task labeled "implement the feature" or
   "refactor the module." Almost always 5–15 tasks pretending to be one.
3. **The trust-fall gate.** "Phase 2 done when feature works." Define "works."
4. **Bundle-of-everything.** Every task points at the whole repo. The agent
   skims and confabulates. Minimize per §8.
5. **Test-after.** Acceptance tests written after the implementation task. Use
   validation-first ordering: write/spec the test as part of the *prior* task or
   as a foundation task.
6. **Sub-agent cargo cult.** Naming sub-agents that don't exist or that don't
   add value over the generalist. If the only specialist behavior is "knows
   slightly more about Postgres," you don't need a specialist.
7. **No human gates anywhere.** Even fully agentic plans need humans at
   irreversible boundaries (production deploy, schema migration, public comms).
8. **No agentic failure modes named.** A risk register that could have been
   written before agents existed isn't doing its job.
9. **Phase 0 skipped.** "We already know the answers." Then the plan should
   *show* the answers in §1's assumptions, not assume them silently.
10. **Frozen plan.** No replanning protocol, no decision log, no `[CHANGED]`
    discipline. Plans that can't update become fiction inside a week.
11. **Open-questions amnesia.** PRD had 8 open questions; plan has 0. Where did
    they go? Probably into Phase 1 implicitly. Make them explicit Phase 0 tasks.
12. **Eval as afterthought.** Eval harness arrives in Phase 4. By then the model
    of "what good looks like" has already drifted. Build eval in Phase 1.

---

## 15. Output Conventions

When the skill is invoked:

- **Filename:** `plan-<kebab-case-name>.md` (matching the PRD's slug if possible
  — e.g., `prd-checkout-export.md` → `plan-checkout-export.md`).
- **Location:** save via `create_file` (or `Write` in Claude Code) to the user's
  preferred location, defaulting to alongside the PRD.
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
- **Pair with `prd-author`.** If the PRD is missing structure (no R-IDs, no
  non-goals, no metrics), recommend running `prd-author` in review mode first.
  A weak PRD becomes a weak plan no matter how disciplined the planner.

---

## 16. A Worked Mini-Example (Schematic)

PRD requirement excerpt:
> **R3.** Power users can export all historical reports in their account as a
> single ZIP of CSVs within 5 minutes for accounts up to 100k reports.

Bad plan:
> **Task:** Implement export. *Owner:* Claude. *Done when:* it works.

Better plan:
> **T-1.2 — Define export job contract.** Type: schema. Blast: contained.
> Spec: write `schemas/export_job.json` with fields `{job_id, account_id,
> requested_at, status, artifact_url, error}`. Acceptance: schema validates
> against three example payloads in `tests/fixtures/export_job/`.
>
> **T-2.1 — Implement export worker (happy path).** Type: code. Depends on:
> T-1.2. Spec: consumes a job message, streams report rows from `reports`
> table to a temp dir as CSVs (one per report type), zips, uploads to S3,
> updates job row. Bundle: `services/worker/`, `schemas/export_job.json`,
> `db/reports.sql`, *and nothing else*. Acceptance: integration test
> `pytest -k export_happy_path` passes against a 1k-report fixture in <30s.
>
> **T-2.2 — Implement export worker (error paths).** Depends on T-2.1. Spec:
> handle `S3UploadFailed`, `RowStreamTimeout`, `JobCancelled`. Each emits a
> typed error in the job row. Acceptance: three error-path tests green.
>
> **T-3.1 — Scale test to 100k reports.** Depends on T-2.2. Acceptance: end-to-end
> latency p95 < 5 minutes on staging fixture; memory < 512MB; no S3 throttle.
>
> **Phase 2 gate:** all three tests above green AND a reviewer crosswalks T-2.1
> and T-2.2 against R3 and confirms behavior matches the PRD literal text.

Notice how the better version closes the spec gap, gives the agent a small
bundle, and bakes in error-path verification rather than discovering it in QA.

---

## 17. When to Push Back

This skill is allowed and expected to push back when:

- The PRD is too thin to plan from. Recommend `prd-author` review first.
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