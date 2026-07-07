---
name: plugin-work-checkpoint
version: 0.1.0
description: |
  Save or restore resumable context for long plugin maintenance work. Use during
  migrations, upstream harvest batches, release preparation, broad health fixes,
  or any plugin-manager task that may span multiple sessions. Inspired by
  GStack context-save/context-restore.
triggers:
  - "save plugin work"
  - "restore plugin work"
  - "plugin checkpoint"
  - "resume plugin work"
  - "where did we leave off on this plugin"
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
  - .plugin-manager/checkpoints/

disable-model-invocation: false
---

# Plugin Work Checkpoint

## Contract

A checkpoint captures the *cross-tool* state a future session needs to resume
without re-deriving it. Every checkpoint records exactly these fields:

- **Git ref** — branch name plus short commit SHA (`git rev-parse --short HEAD`).
- **Dirty-file list** — the porcelain `git status --short` output (paths + XY
  status), so the resumer can confirm the working tree still matches. Summaries,
  not full diffs.
- **Validation state** — the last result of each gate that governs this work,
  with the exact command and its verdict:
  - `npm run validate` → pass / fail (+ error count) / not-run
  - `python -m pytest -q` → pass / fail (+ failing tests) / not-run
  - `python scripts/routing_eval.py` → accuracy number / not-run
  - any plugin-specific check run (e.g. `plugin_audit.py --strict-sections`).
- **Open decisions** — questions still unresolved and the options on the table.
- **Next actions** — the ordered, concrete steps to take on resume.
- **Target plugin(s)** and ownership boundaries (what this work may/may not touch).
- **Blockers** and **related GitHub issues**.
- **Privacy note** confirming no secrets or raw private content are stored.

### Boundary vs. git stash / branch

A checkpoint is **not** a substitute for a branch or stash, and vice versa. Git
snapshots *tracked file contents*; a checkpoint snapshots the *state git cannot
see*: which validation gates last passed and with what numbers, which decisions
are still open, what the next action is, and why the work is where it is. Use a
branch/commit to preserve code; use a checkpoint to preserve intent and
verification status on top of that code. A checkpoint therefore **references** a
git ref rather than replacing it — restore reconciles the two.

## Workflow

1. **Choose mode**
   - Save when the user says to checkpoint, pause, hand off, or preserve state.
   - Restore when the user asks to resume or asks where plugin work left off.

2. **Save** — capture, don't guess. Gather evidence before writing:
   - Git ref: `git rev-parse --short HEAD` and the branch from
     `git status --short --branch`.
   - Dirty-file list: the full `git status --short` output, transcribed as the
     checkpoint's file inventory (path + status). Summarize *why* each changed;
     do not paste large diffs.
   - Validation state: record the last verdict of each gate you actually ran —
     `npm run validate` (pass/fail + error count), `python -m pytest -q`
     (pass/fail + failing tests), `python scripts/routing_eval.py` (accuracy),
     and any `--strict-sections` audit. Mark anything you did not run as
     `not-run` rather than omitting it.
   - Open decisions and the next actions in priority order.
   - Write an append-only markdown file under:
     `.plugin-manager/checkpoints/YYYY-MM-DD-HHMM-<slug>.md`
   - Do not include secrets, credentials, raw private transcripts, or full
     proprietary source snippets.

3. **Restore** — verify the tree matches before resuming:
   - List recent checkpoint files newest first; read the relevant one.
   - Re-run `git rev-parse --short HEAD`, the branch check, and
     `git status --short`, then **diff the live state against the saved Git ref
     and dirty-file list**:
     - If the commit SHA differs, report the drift (commits landed since the
       checkpoint) and reconcile before acting — the recorded validation state
       may be stale.
     - If the dirty-file list differs (files added, reverted, or newly changed),
       list the differences explicitly and do not assume the saved validation
       verdicts still hold.
   - Only after reconciling, re-run any gate whose result the next action depends
     on (do not trust a stale `pass`), then summarize what was done, what
     remains, blockers, and the safest next step.

## Checkpoint Template

```markdown
# Plugin Work Checkpoint: <title>

- Date: YYYY-MM-DD HH:MM TZ
- Branch: <branch>
- Commit: <sha>
- Target plugin(s): <names>
- Ownership boundary: <what this work may/may not touch>
- Related issues: <numbers/urls>
- Privacy: no secrets or raw private content stored

## Dirty Files (git status --short)

- `XY <path>` - <why it changed>

## Validation State

- `npm run validate` - pass|fail (<N> errors)|not-run
- `python -m pytest -q` - pass|fail (<failing tests>)|not-run
- `python scripts/routing_eval.py` - <accuracy>|not-run
- `<plugin-specific check>` - pass|fail|not-run

## Open Decisions

- <question> - options: <A | B>; leaning: <choice or undecided>

## Next Actions

1. <ordered concrete step>

## Blockers

- <blocker or none>
```

## Output Format

```text
PLUGIN CHECKPOINT
Mode: save|restore
Checkpoint: .plugin-manager/checkpoints/<file>.md
Branch: <branch>
Status: saved|restored|blocked
Next:
- <next action>
```

## Anti-Patterns

- Storing secrets, API keys, raw private content, or long diffs.
- Treating a stale checkpoint as current without diffing the live git ref and
  dirty-file list against the saved ones.
- Trusting a saved `pass` verdict after the tree changed — re-run the gate the
  next action depends on.
- Using a checkpoint as a stand-in for a branch/commit (or vice versa): git
  preserves file contents, the checkpoint preserves validation state and intent.
- Overwriting prior checkpoints instead of appending a new one.
- Saving vague notes that omit validation state, open decisions, or next actions.

