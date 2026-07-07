---
name: background-jobs
version: 0.2.0
description: >-
  Orchestrate a long KB operation — migration, archive scan, enrichment batch, research backfill — as batched, checkpointed, resumable work with sample-before-bulk gates, and save/restore resumable context so a job survives across sessions. Trigger on 'run this KB job in batches', 'long/background KB job', 'save/resume KB progress', 'checkpoint this job'. Absorbs context-checkpoint. Recurring-schedule design lives in references/automation.md; the actual ingestion is done by ingest or media-ingest.
triggers:
  - "run this kb job in batches"
  - "long background kb job"
  - "checkpoint this kb job"
  - "resume this kb job"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
disable-model-invocation: false
mutating: true
---

# Background Jobs

## Contract

- Long jobs are batched, checkpointed, resumable, and validated after each batch; bulk writes only follow a passing sample.
- Checkpoints capture enough state to resume without rescanning everything.
- Secrets, raw private content, and long diffs are never stored in checkpoints.
- Mutating skill: it may write checkpoint files and batch outputs, but it must stop before any strategy change that would widen scope, overwrite many pages, or discard failed work.

## Intake And Modes

- Treat `$ARGUMENTS` as the job goal plus optional vault root, source set, batch size, and resume checkpoint.
- Quick mode: inspect or restore an existing checkpoint and report next safe action.
- Standard mode: run a sampled batch, checkpoint state, validate, and summarize remaining work.
- Deep mode: plan or execute a multi-batch migration/backfill with retries, validation gates, and resume instructions.
- Use `ask-user` before changing batch scope, deleting checkpoint history, or continuing after repeated validation failure.

## Evidence Requirements

- Inspect the current checkpoint, target file list, changed files, and last validation output before resuming.
- For migrations or enrichment backfills, verify the source map and sample output before bulk writes.

## Workflow

- Plan batch size, ordering, retry policy, and stop conditions.
- Run a 3-5 item sample and inspect the output before bulk.
- Checkpoint before and after each batch with `checkpoint` (branch, batch ids, files changed, validation, blockers, next step).
- Validate citations, frontmatter, graph links, and indexes between batches.
- On restore, load the latest checkpoint, verify current state, and resume from the next safe batch.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" checkpoint`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" dashboard`


## Output Format

- BACKGROUND JOB
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Batch status, checkpoint path, completed, remaining, validation, blockers, next batch.
- Artifact path: checkpoint at `.kb/checkpoints/<YYYYMMDD>-<slug>.md` or the user-specified checkpoint path.

## Anti-Patterns

- Running 100 items before inspecting the first 3.
- Losing progress state between sessions, or storing secrets/transcripts in checkpoints.
