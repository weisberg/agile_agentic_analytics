---
name: skillopt-slow-meta-update
version: 0.1.0
description: |
  Run SkillOpt epoch-boundary consolidation for a skill optimization run. Use
  when comparing adjacent skill versions on repeated tasks, writing protected
  slow-update guidance into the skill, and maintaining separate optimizer-side
  meta memory about which edit patterns helped, hurt, or caused regressions.
triggers:
  - "skillopt slow update"
  - "skillopt meta update"
  - "epoch skill consolidation"
  - "update optimizer memory"
  - "compare skill versions"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - .plugin-manager/skillopt/
---

# SkillOpt Slow Meta Update

## Contract

At epoch boundaries, consolidate longer-horizon evidence that ordinary
step-level edits cannot see. The slow update may rewrite the protected
slow-update block in a candidate skill; optimizer meta memory stays outside the
deployed skill.

## Workflow

1. **Load epoch evidence**
   - Read `../../references/skillopt-protocol.md`.
   - Read previous epoch skill, current epoch skill, previous slow guidance,
     previous optimizer memory, and selected repeated tasks.
   - Prefer 10 to 20 repeated tasks when available.

2. **Run longitudinal comparison**
   - Evaluate the same tasks under both skill versions with the same harness and
     scorer.
   - Categorize each task as regression, persistent failure, improvement, or
     stable success.
   - Save `longitudinal-comparison.md`.

3. **Write slow-update guidance**
   - Preserve guidance that clearly helped.
   - Remove or revise guidance that backfired.
   - Add concise instructions for regressions and persistent failures.
   - Write direct task-agent guidance only inside:

     ```markdown
     <!-- SLOW_UPDATE_START -->
     ...
     <!-- SLOW_UPDATE_END -->
     ```

   - If the skill lacks markers, insert one protected section near the end of the
     workflow content, before output-format or anti-pattern sections when that
     reads cleanly.

4. **Write optimizer meta memory**
   - Store `meta-skill.md` outside the deployed skill.
   - Address the future optimizer, not the task-execution agent.
   - Capture edit abstractions that helped, vague edits that failed, regression
     risks, and ranking preferences.

5. **Gate the slow update**
   - Treat the slow-update candidate as a normal candidate.
   - Run `skillopt-validation-gate` before making it the current skill.

## Output Format

```text
SKILLOPT SLOW META UPDATE
Run: .plugin-manager/skillopt/<run-id>/
Epoch: <n>
Repeated tasks: <count>
Regressions: <count>
Persistent failures: <count>
Improvements: <count>
Artifacts:
- .plugin-manager/skillopt/<run-id>/epochs/<epoch>/longitudinal-comparison.md
- .plugin-manager/skillopt/<run-id>/epochs/<epoch>/slow-update.json
- .plugin-manager/skillopt/<run-id>/epochs/<epoch>/meta-skill.md
Gate next:
- /plugin-manager:skillopt-validation-gate
```

## Anti-Patterns

- Letting ordinary reflection edits modify the protected slow-update section.
- Shipping optimizer meta memory inside the production skill.
- Writing generic slow guidance that ignores adjacent-epoch evidence.
- Consolidating only improvements while ignoring regressions.
- Skipping the validation gate after a slow update.
