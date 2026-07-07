---
name: skillopt-reflection-edits
version: 0.1.0
description: |
  Turn SkillOpt rollout evidence into bounded structured edits for a plugin
  skill. Use when analyzing success and failure minibatches, merging proposed
  patches, ranking edits by systematic impact, and producing candidate
  add/insert/replace/delete operations without touching the protected slow-update
  block.
triggers:
  - "reflect on skill rollouts"
  - "generate skillopt edits"
  - "merge skill patches"
  - "rank skill edits"
  - "bounded skill update"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
mutating: true
writes_pages: false
writes_to:
  - .plugin-manager/skillopt/

disable-model-invocation: false
---

# SkillOpt Reflection Edits

## Contract

Produce a bounded candidate patch from rollout evidence. The patch must be
structured JSON, grounded in recurring evidence, small enough to preserve the
existing skill, and ready for `skillopt-validation-gate` to apply to a copy.

## Workflow

1. **Load inputs**
   - Read `../../references/skillopt-protocol.md`.
   - Read the current target `SKILL.md`, latest rollout artifacts, and rejected
     buffer for the current epoch.
   - Identify the edit budget from `run.md`.

2. **Partition evidence**
   - Split failures from successes.
   - Group each side into minibatches. Use 4 to 8 trajectories by default when
     enough evidence exists.
   - Keep selection and test evidence out of reflection.

3. **Analyze failures**
   - Look for repeated missing rules, bad evidence-gathering habits, verifier
     mistakes, unsafe mutation patterns, routing confusion, or output contract
     misses.
   - Propose corrective add, insert, replace, or delete edits.
   - Ignore one-off task details unless they expose a general rule.

4. **Analyze successes**
   - Identify behaviors that reliably worked and are not already encoded.
   - Use success edits to preserve useful behavior and prevent regressions.
   - Keep success-driven edits lower priority than failure corrections.

5. **Merge**
   - Deduplicate edits with the same purpose.
   - Resolve conflicts by choosing the stronger evidence or synthesizing a
     narrower instruction.
   - Add `support_count` and `source_type` to every merged edit.
   - Do not generate edits inside `<!-- SLOW_UPDATE_START -->` and
     `<!-- SLOW_UPDATE_END -->`.

6. **Rank and select**
   - Rank by systematic impact, complementarity, generality, then actionability.
   - Clip to the edit budget.
   - Write `failure-analysis.json`, `success-analysis.json`,
     `merged-edits.json`, and `selected-edits.json`.

## Output Format

```text
SKILLOPT REFLECTION EDITS
Run: .plugin-manager/skillopt/<run-id>/
Step: <n>
Evidence:
- failures: <count>
- successes: <count>
Edit budget: <n>
Selected edits:
- [<source_type>, support=<count>] <op> <target or append>
Artifacts:
- .plugin-manager/skillopt/<run-id>/reflection/<step>/selected-edits.json
Gate next:
- /plugin-manager:skillopt-validation-gate
```

## Anti-Patterns

- Rewriting the whole skill when a localized patch is enough.
- Proposing vague advice that a future agent cannot execute.
- Adding rules already present in the skill.
- Optimizing for a single task instead of recurring failure modes.
- Touching the protected slow-update block.
- Dropping rejected-edit feedback before proposing similar edits again.
