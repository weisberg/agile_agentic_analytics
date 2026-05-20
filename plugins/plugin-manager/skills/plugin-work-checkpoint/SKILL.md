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
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: false
writes_to:
  - .plugin-manager/checkpoints/
---

# Plugin Work Checkpoint

## Contract

A checkpoint captures enough state for another agent or a future session to
resume without guessing:

- branch, commit, and git status
- target plugin(s)
- changed files and ownership boundaries
- decisions made
- commands run and validation results
- open blockers and remaining work
- related GitHub issues
- privacy note confirming no secrets or raw private content are stored

## Workflow

1. **Choose mode**
   - Save when the user says to checkpoint, pause, hand off, or preserve state.
   - Restore when the user asks to resume or asks where plugin work left off.

2. **Save**
   - Run `git status --short --branch` and `git rev-parse --short HEAD`.
   - Summarize changed files; do not paste large diffs.
   - Record validation commands and outcomes.
   - Write an append-only markdown file under:
     `.plugin-manager/checkpoints/YYYY-MM-DD-HHMM-<slug>.md`
   - Do not include secrets, credentials, raw private transcripts, or full
     proprietary source snippets.

3. **Restore**
   - List recent checkpoint files newest first.
   - Read the relevant checkpoint.
   - Verify current branch and git status against the saved state.
   - Summarize what was done, what remains, blockers, and the safest next step.

## Checkpoint Template

```markdown
# Plugin Work Checkpoint: <title>

- Date: YYYY-MM-DD HH:MM TZ
- Branch: <branch>
- Commit: <sha>
- Target plugin(s): <names>
- Related issues: <numbers/urls>
- Privacy: no secrets or raw private content stored

## Changed Files

- <path> - <why it changed>

## Decisions

- <decision and rationale>

## Validation

- `<command>` - pass|fail|not-run

## Remaining Work

- <next task>

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
- Treating a stale checkpoint as current without checking git status.
- Overwriting prior checkpoints instead of appending a new one.
- Saving vague notes that omit validation state or remaining work.

