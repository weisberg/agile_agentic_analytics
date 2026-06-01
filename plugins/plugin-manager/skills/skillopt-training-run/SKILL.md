---
name: skillopt-training-run
version: 0.1.0
description: |
  Orchestrate an offline SkillOpt-style optimization run for a plugin skill.
  Use when the user explicitly asks for SkillOpt, training, evolution, repeated
  rollouts, train/selection/test splits, model or harness comparison, slow/meta
  updates, or best-skill export. For a lightweight one-pass skill improvement,
  use skill-improve instead.
triggers:
  - "skillopt"
  - "optimize this skill"
  - "train this skill"
  - "evolve this skill"
  - "self-improve this skill"
  - "run a skill optimization loop"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - .plugin-manager/skillopt/
  - plugins/
---

# SkillOpt Training Run

## Contract

Use this as the coordinator for a SkillOpt-style training run. A run is complete
when there is a durable run directory, fixed train/selection/test task splits,
baseline evidence, at least one gated candidate decision or a clear blocker, and
an exported best skill when any candidate improves validation performance.

Read `../../references/skillopt-protocol.md` before starting. Route phase work
to the sibling SkillOpt skills:

- `../skillopt-rollout-evidence/SKILL.md`
- `../skillopt-reflection-edits/SKILL.md`
- `../skillopt-validation-gate/SKILL.md`
- `../skillopt-slow-meta-update/SKILL.md`
- `../skillopt-transfer-release/SKILL.md`

## Workflow

1. **Preflight**
   - Run `git status --short --branch`.
   - Identify the target `SKILL.md`, target plugin, and owner boundary.
   - Read the target skill, plugin README, and any existing tests or routing
     fixtures.
   - Record unrelated user changes and do not overwrite them.

2. **Define the run**
   - Create `.plugin-manager/skillopt/YYYY-MM-DD-HHMM-<target-skill>/run.md`.
   - Record target model or harness, optimizer model if one is used, scoring
     method, task source, edit budget, and stopping rule.
   - Keep the target model, tools, harness, and evaluator fixed for the run.

3. **Build task splits**
   - Prefer real historical failures, routing examples, plugin-health failures,
     review notes, CI failures, and user-provided examples.
   - Split tasks into train, held-out selection, and final test.
   - Do not tune directly on the final test split.
   - If there are too few examples, label the run as exploratory and keep the
     candidate out of release until more evidence exists.

4. **Baseline**
   - Use `skillopt-rollout-evidence` to score the current skill on the training
     and selection splits.
   - Run a no-skill baseline only when the harness makes that comparison cheap
     and meaningful.

5. **Optimize**
   - For each step, run rollouts on the current skill.
   - Use `skillopt-reflection-edits` to produce bounded candidate edits.
   - Use `skillopt-validation-gate` to apply the candidate to a copy and accept
     it only if held-out selection score strictly improves.
   - Store rejected edits and score deltas for later reflection.

6. **Consolidate**
   - At epoch boundaries, run `skillopt-slow-meta-update` on repeated tasks to
     identify regressions, persistent failures, and durable optimizer guidance.
   - Gate slow-update candidates the same way as ordinary candidates.

7. **Export**
   - Stop when the run budget is exhausted, improvements plateau, evidence is
     insufficient, or the user asks to stop.
   - Use `skillopt-transfer-release` to evaluate transfer, document evidence,
     and promote `best/SKILL.md` only when the user or release flow calls for it.

## Output Format

```text
SKILLOPT TRAINING RUN
Target: plugins/<plugin>/skills/<skill>/SKILL.md
Run: .plugin-manager/skillopt/<run-id>/
Status: planned|running|best-found|no-improvement|blocked
Baseline:
- train: <score or not-run>
- selection: <score or not-run>
Best:
- step: <n or none>
- selection score: <score or none>
Validation:
- <command or rubric>: pass|fail|not-run
Next:
- <next phase or release action>
```

## Anti-Patterns

- Editing the production skill directly before a candidate passes the gate.
- Changing the evaluator or task split mid-run and calling scores comparable.
- Accepting a candidate because the reflection sounds plausible.
- Optimizing only on one anecdotal failure without labeling the run exploratory.
- Letting step-level edits rewrite the protected slow-update block.
- Shipping optimizer memory with the deployed skill.
