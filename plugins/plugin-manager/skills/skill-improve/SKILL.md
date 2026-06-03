---
name: skill-improve
version: 0.1.0
description: |
  One-pass improvement workflow for an existing SKILL.md. Use when the user asks
  to improve, tighten, repair, simplify, deconflict, or upgrade a skill without
  running a full SkillOpt training session. Applies SkillOpt lessons such as
  evidence-first review, failure/success separation, bounded edits, validation,
  and rejected-change notes, but does not create train/selection/test splits or
  run an offline optimization loop.
triggers:
  - "improve this skill"
  - "skill-improve"
  - "tighten this skill"
  - "repair this skill"
  - "upgrade this skill"
  - "make this skill better"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - plugins/
  - .plugin-manager/skill-improve/

disable-model-invocation: false
---

# Skill Improve

## Contract

Use this for a focused, single-pass skill upgrade. It borrows SkillOpt's
discipline without running SkillOpt: gather evidence, separate failures from
working behavior, make a small bounded patch, validate it, and record what was
changed or deliberately rejected.

Escalate to `../skillopt-training-run/SKILL.md` only when the user wants a full
training loop, repeated rollouts, train/selection/test splits, model or harness
comparison, slow/meta updates, or best-skill export.

## Workflow

1. **Preflight**
   - Run `git status --short --branch`.
   - Identify the target `SKILL.md`, plugin, docs surface, and ownership
     boundary.
   - Read the target skill, plugin README, nearby skills, and any relevant tests,
     routing fixtures, or plugin-health output.
   - Preserve unrelated user edits.

2. **Evidence scan**
   - Look for concrete signals: user complaint, stale docs, failed validation,
     confusing trigger text, missing output contract, unsafe write scope,
     duplicated instructions, vague advice, missing anti-patterns, or examples
     of successful use worth preserving.
   - If no concrete evidence exists, do a design review against local skill
     conventions and label the result as judgment-based.

3. **Failure and success reflection**
   - Failure side: identify recurring or high-impact gaps the skill should
     prevent.
   - Success side: identify behavior already working that should remain intact.
   - Prefer general rules over example-specific patches.
   - Do not add content already covered by the skill.

4. **Bounded patch**
   - Apply the smallest useful edit set; default to 1 to 4 focused changes.
   - Prefer localized add, replace, or delete edits over full rewrites.
   - Keep the skill concise and under the repo's existing style.
   - Do not add new scripts, references, or agents unless deterministic behavior
     or progressive disclosure clearly needs them.

5. **Validation**
   - Run `python3 plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py --plugin <plugin-name> --json`.
   - Run `claude plugin validate plugins/<plugin-name>` when available.
   - Run focused tests for any scripts or fixtures touched.
   - If validation is unavailable, state exactly what was not run.

6. **Receipt**
   - For non-trivial improvements, write a short receipt under
     `.plugin-manager/skill-improve/YYYY-MM-DD-HHMM-<skill>.md` with evidence,
     changes, validation, and rejected ideas.
   - Skip the receipt for tiny typo-only or docs-only fixes unless the user asks
     for an audit trail.

## Output Format

```text
SKILL IMPROVE
Target: plugins/<plugin>/skills/<skill>/SKILL.md
Mode: one-pass
Evidence:
- <signals used>
Changes:
- <bounded edit summary>
Validation:
- <command>: pass|fail|not-run
Rejected:
- <idea intentionally not applied or none>
Receipt: <path or skipped>
```

## Anti-Patterns

- Turning a one-pass improvement request into a full training run.
- Rewriting the whole skill because a bounded patch would work.
- Optimizing around one anecdote without saying the evidence is thin.
- Adding verbose background that belongs in a reference file or nowhere.
- Removing successful behavior while fixing a failure.
- Claiming improvement without running available validation.
