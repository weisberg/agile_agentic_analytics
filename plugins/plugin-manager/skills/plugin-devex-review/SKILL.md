---
name: plugin-devex-review
version: 0.1.0
description: |
  Developer-experience review for plugin onboarding. Use when evaluating a
  plugin's fresh-clone setup, README flow, local testing instructions,
  prerequisites, bundled CLIs, confusing paths, or contributor experience.
  Inspired by GStack devex-review and QA workflows.
triggers:
  - "plugin devex review"
  - "review plugin onboarding"
  - "fresh clone plugin test"
  - "make plugin easier to use"
  - "check plugin quickstart"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - plugins/
  - README.md

disable-model-invocation: false
---

# Plugin Devex Review

## Contract

A devex review produces:

- Fresh-user setup path with concrete commands.
- Measured or estimated time to first useful success.
- Missing prerequisites and confusing path names.
- One-command validation recommendation when useful.
- README or issue updates for discovered blockers.

## Workflow

1. **Scope**
   - Identify the target plugin.
   - Read plugin `README.md`, manifest, and visible skills.
   - Run `git status --short --branch` before editing.

2. **Fresh-user path**
   - Verify install command appears in root and plugin docs.
   - Verify local testing command:
     `claude --plugin-dir ./plugins/<plugin-name>`.
   - Verify expected first skill invocation is named.
   - For bundled CLIs, run `<tool> --help` or the wrapper help command when
     safe and available.

3. **Validation path**
   - Run `claude plugin validate plugins/<plugin-name>` when available.
   - Run `/plugin-manager:plugin-health` or its script:
     `python3 plugins/plugin-manager/skills/plugin-health/scripts/plugin_audit.py --plugin <plugin-name> --json`.
   - Run focused tests for changed scripts.

4. **Experience review**
   - Find jargon, missing prerequisites, stale paths, and commands that assume
     private checkouts.
   - Check whether README tells the user what success looks like.
   - Prefer one clear quickstart over many equivalent alternatives.

5. **Fix or file**
   - Fix straightforward docs and path confusion.
   - For larger blockers, create or update GitHub issues with precise repro
     steps and expected behavior.

## Output Format

```text
PLUGIN DEVEX REVIEW
Plugin: <name>
Fresh-user path: pass|fail
Time to first success: <duration or not measured>
Validation:
- <command>: pass|fail|not-run
Findings:
- <issue and fix/status>
Docs changed:
- <path>
Follow-up issues:
- <url or none>
```

## Anti-Patterns

- Reviewing docs without running the commands they advertise.
- Requiring private local paths in public plugin instructions.
- Adding long setup prose instead of a shorter working quickstart.
- Filing vague issues without repro commands.

