---
name: skillopt-rollout-evidence
version: 0.1.0
description: |
  Capture scored rollout evidence for a SkillOpt-style skill optimization run.
  Use when building train, selection, or test trajectories for plugin skills,
  collecting task outputs, verifier results, tool-use summaries, failure modes,
  and before/after evidence for candidate skills.
triggers:
  - "collect skillopt rollouts"
  - "score skill trajectories"
  - "build skill evidence"
  - "run skill optimization tasks"
  - "capture rollout evidence"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - .plugin-manager/skillopt/
---

# SkillOpt Rollout Evidence

## Contract

Create scored, repeatable trajectory evidence for one skill version on a fixed
task split. Evidence must be usable by reflection without requiring another
agent to reread huge transcripts, private content, or full terminal logs.

## Workflow

1. **Load run protocol**
   - Read `../../references/skillopt-protocol.md`.
   - Verify the run directory, target skill version, task split, scoring method,
     and output path.

2. **Freeze conditions**
   - Record skill version, git SHA, target model or harness, tool availability,
     environment variables that affect behavior, and evaluator command or rubric.
   - Do not compare scores across different harnesses unless the run is
     explicitly a transfer check.

3. **Prepare tasks**
   - Use existing `routing-eval.jsonl`, plugin-health failures, tests, review
     reports, user examples, or curated prompts.
   - Keep task records stable with `id`, `prompt`, `expected`, `score_type`,
     `verifier`, and notes.
   - Separate train, selection, and test evidence.

4. **Run trajectories**
   - Execute the skill or simulate the skill workflow consistently for each task.
   - Capture short summaries of messages, tool calls, files touched, verifier
     outputs, and failure modes.
   - Store large raw logs by path when needed; summarize instead of pasting them
     into reflection prompts.

5. **Score**
   - Prefer deterministic commands, exact checks, schema validation, or
     plugin-health checks.
   - If manual or rubric scoring is required, use the same rubric for every
     candidate and label it clearly.
   - Record success, failure, partial credit, and verifier errors separately.

6. **Write artifacts**
   - Save `trajectories.jsonl` and `rollout-summary.md` under the step directory.
   - Include score totals, recurring failure modes, task IDs, and any tasks that
     could not be evaluated.

## Output Format

```text
SKILLOPT ROLLOUT EVIDENCE
Run: .plugin-manager/skillopt/<run-id>/
Skill version: <baseline|step-n|candidate-n>
Split: train|selection|test|transfer
Tasks: <count>
Score: <score>/<max> (<percent or rubric total>)
Artifacts:
- .plugin-manager/skillopt/<run-id>/rollouts/<step>/trajectories.jsonl
- .plugin-manager/skillopt/<run-id>/rollouts/<step>/rollout-summary.md
Failures:
- <failure mode and task ids>
```

## Anti-Patterns

- Gathering anecdotes without scores.
- Mixing train and selection tasks in the same optimization prompt.
- Changing task wording between baseline and candidate runs.
- Treating verifier setup failures as model failures without labeling them.
- Storing secrets, raw private content, or giant logs in rollout artifacts.
