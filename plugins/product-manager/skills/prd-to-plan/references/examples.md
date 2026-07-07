# prd-to-plan — Templates & Worked Examples

Verbatim templates and reference catalogs for the `prd-to-plan` skill. `SKILL.md`
points here whenever it needs a block to reproduce. Read the relevant section
before producing the corresponding part of `PLAN.md`; reproduce templates
faithfully (keep heading text and field names) unless the plan's specifics
require adaptation.

---

## A. The `PLAN.md` Skeleton (SKILL.md §4)

Every invocation produces a single markdown file with this skeleton. Use the H2
headings **verbatim** so other tools and skills can address sections by slug.

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

Keep the plan **scannable** — an orchestrator should be able to find any task by
ID in under five seconds.

---

## B. Default Phase Template (SKILL.md §5.1)

A **phase** is a horizontally-cut slab of work that ends in a meaningful, testable
state. Phases are sequential; you do not start phase N+1 until phase N's gate
passes. Adapt this template to the work.

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

---

## C. Task Specification Template (SKILL.md §6)

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

## D. Risk Register — Agentic Failure Modes (SKILL.md §10)

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

## E. Antipatterns to Catch (SKILL.md §14)

Catch these in your own drafts.

1. **The wishlist plan.** One task per requirement, no dependencies, no validation.
2. **The hero task.** "Implement the feature" hides 5-15 real tasks.
3. **The trust-fall gate.** "Done when it works" is not falsifiable.
4. **Bundle-of-everything.** Whole-repo context makes agents skim and confabulate.
5. **Test-after.** Acceptance tests arrive after implementation instead of before.
6. **Sub-agent cargo cult.** Specialist labels add no value over the generalist.
7. **No human gates.** Irreversible ops still need human checkpoints.
8. **No agentic failure modes.** The risk register could have been written in 2020.
9. **Phase 0 skipped.** Assumptions move silently into build work.
10. **Frozen plan.** No replanning protocol, decision log, or `[CHANGED]` discipline.
11. **Open-questions amnesia.** PRD questions vanish instead of becoming Phase 0 tasks.
12. **Eval as afterthought.** Eval arrives after the model of quality has drifted.

---

## F. Sub-Agent Assignment Patterns (SKILL.md §11)

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

---

## G. Quality Bar — Self-Review Checklist (SKILL.md §13)

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
