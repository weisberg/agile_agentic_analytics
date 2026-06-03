---
name: skillopt-validation-gate
version: 0.1.0
description: |
  Apply and evaluate SkillOpt candidate skill edits behind a strict held-out
  validation gate. Use when deciding whether bounded skill edits should become
  the current or best skill, recording rejected edits and score deltas, and
  preventing unvalidated self-edits from reaching production plugin skills.
triggers:
  - "gate skillopt candidate"
  - "validate skill edits"
  - "accept or reject skill candidate"
  - "apply skillopt patch"
  - "held-out skill validation"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - .plugin-manager/skillopt/
  - plugins/

disable-model-invocation: false
---

# SkillOpt Validation Gate

## Contract

Evaluate a candidate skill on the held-out selection split and accept it only
when its score is strictly greater than the current skill's selection score.
Rejected candidates must leave useful negative feedback for later reflection.

## Workflow

1. **Preflight**
   - Read `../../references/skillopt-protocol.md`.
   - Verify current selection score, selected edits, candidate path, and
     evaluator.
   - Run `git status --short --branch` before any production file change.

2. **Apply to a copy**
   - Apply selected edits to a candidate `SKILL.md` under
     `.plugin-manager/skillopt/<run-id>/candidates/<step>/`.
   - Produce `edit-apply-report.json` with per-edit applied, skipped, or
     conflicted status.
   - If any edit targets the protected slow-update block, reject the patch before
     scoring.

3. **Evaluate selection**
   - Run the same held-out selection tasks, verifier, target model or harness,
     and scoring method used for the current skill.
   - Store `selection-report.md` under `gates/<step>/`.
   - Keep train and test scores out of the accept/reject decision.

4. **Decide**
   - Accept only if candidate selection score is strictly greater than current
     selection score.
   - Reject ties and regressions.
   - When accepted, update the run's current pointer. If the candidate also
     exceeds the previous best score, copy it to `best/SKILL.md`.
   - Do not overwrite the production plugin skill unless the user explicitly
     asked to deploy or `skillopt-transfer-release` is running that promotion.

5. **Record negative feedback**
   - Append rejected edits, failure patterns, selection score, current score,
     and score delta to `rejected-buffer.jsonl`.
   - Summarize why the candidate failed without trying to fix it in-place.

## Output Format

```text
SKILLOPT VALIDATION GATE
Run: .plugin-manager/skillopt/<run-id>/
Step: <n>
Candidate: accepted|rejected|blocked
Current selection score: <score>
Candidate selection score: <score>
Best updated: yes|no
Artifacts:
- .plugin-manager/skillopt/<run-id>/candidates/<step>/SKILL.md
- .plugin-manager/skillopt/<run-id>/gates/<step>/selection-report.md
Rejected buffer: <path or none>
Next:
- <next optimization, slow update, or release step>
```

## Anti-Patterns

- Accepting ties because the new skill looks cleaner.
- Evaluating the candidate on training tasks and calling it validation.
- Changing the rubric, verifier, model, or harness for the candidate only.
- Mutating the production `SKILL.md` before the gate passes.
- Losing rejected edits instead of feeding them back into future reflection.
