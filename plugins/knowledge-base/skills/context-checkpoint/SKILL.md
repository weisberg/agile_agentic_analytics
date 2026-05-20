---
name: context-checkpoint
version: 0.1.0
description: >-
  Save and restore resumable context for long KB migrations, archive scans, enrichment batches, and synthesis jobs.
triggers:
  - "kb checkpoint"
  - "resume kb job"
  - "save kb progress"
  - "restore kb context"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: true
---

# Context Checkpoint

## Contract

- Checkpoints capture enough state to resume without rescanning everything.
- Secrets and raw private content are not stored.
- Batch validation status and remaining work are explicit.

## Workflow

- For save: record branch, target vault, batch ids, files changed, decisions, validation, blockers, and next step.
- For restore: load latest relevant checkpoint, verify current state, and resume from next safe batch.
- Store checkpoints under a KB-local checkpoint path or plugin-manager checkpoint when managing plugin work.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py checkpoint`


## Output Format

- KB CHECKPOINT
- Mode, checkpoint path, completed, remaining, blockers.

## Anti-Patterns

- Saving only vague progress notes.
- Storing raw transcripts or secrets in checkpoints.
