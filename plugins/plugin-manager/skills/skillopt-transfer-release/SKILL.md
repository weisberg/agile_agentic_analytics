---
name: skillopt-transfer-release
version: 0.1.0
description: |
  Export, transfer-check, document, and release a SkillOpt-optimized plugin
  skill. Use after a SkillOpt run finds a best skill and the user wants to test
  cross-model, cross-harness, or nearby-task transfer, promote best/SKILL.md into
  the plugin, update docs, and run plugin-manager release validation.
triggers:
  - "release skillopt best skill"
  - "export best skill"
  - "transfer check optimized skill"
  - "promote skillopt candidate"
  - "ship optimized skill"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - .plugin-manager/skillopt/
  - plugins/
  - README.md
  - PLUGINS_AND_SKILLS.md
  - CLAUDE.md
---

# SkillOpt Transfer Release

## Contract

Move a validated `best/SKILL.md` from training artifact to releasable plugin
change. Promotion is complete only when transfer evidence is recorded, docs are
updated when user-facing behavior changed, production files are edited
intentionally, and plugin validation has been run or clearly marked unavailable.

## Workflow

1. **Preflight**
   - Read `../../references/skillopt-protocol.md`.
   - Run `git status --short --branch`.
   - Verify the run has `best/SKILL.md`, `best-summary.md`, and at least one
     passing held-out selection gate.
   - Read the production target skill and compare it to the best artifact.

2. **Transfer checks**
   - Test the best skill on final held-out test tasks.
   - When feasible, also test one transfer axis:
     - same task split with a different model size
     - same tasks in a different harness
     - nearby but non-identical task family
   - Label transfer checks as measured, rubric-scored, or skipped.
   - Store `best/transfer-report.md`.

3. **Promotion decision**
   - If the best skill regresses final test performance, do not promote.
   - If evidence is thin, ask for or record an explicit waiver before promotion.
   - If promotion is approved, replace only the target `SKILL.md` content that
     belongs to the optimized skill. Preserve unrelated user edits.

4. **Docs and release**
   - Update target plugin README and catalog docs when the skill's behavior,
     trigger surface, or user-facing command list changed.
   - Run plugin-health for the target plugin:

     ```bash
     python3 plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py --plugin <plugin-name> --json
     ```

   - Run `claude plugin validate plugins/<plugin-name>` when available.
   - Use `../plugin-quality-gate/SKILL.md` for high-impact skills before release.
   - Use `../plugin-release/SKILL.md` for versioning, changelog, commit, tag, or
     publish work.

5. **Close the loop**
   - Summarize baseline, best selection score, final test score, transfer result,
     files changed, validation, and known gaps.
   - Keep optimizer memory and rejected buffers in the run directory; do not ship
     them as production skill text.

## Output Format

```text
SKILLOPT TRANSFER RELEASE
Run: .plugin-manager/skillopt/<run-id>/
Target: plugins/<plugin>/skills/<skill>/SKILL.md
Promotion: promoted|not-promoted|blocked
Evidence:
- baseline selection: <score>
- best selection: <score>
- final test: <score or not-run>
- transfer: <score or not-run>
Files changed:
- <path>
Validation:
- <command>: pass|fail|not-run
Known gaps:
- <gap or none>
```

## Anti-Patterns

- Treating a selection win as enough to ship without final test evidence.
- Promoting a candidate when the run changed the harness or evaluator midstream.
- Shipping rejected-edit buffers or optimizer meta memory to end users.
- Updating docs as a broad rewrite unrelated to the optimized skill.
- Calling a transfer check successful when it was not actually measured.
