---
name: background-jobs
version: 0.1.0
description: >-
  Orchestrate long KB operations such as migrations, archive scans, enrichment batches, and research backfills with checkpoints and batch gates.
triggers:
  - "kb background job"
  - "batch ingest"
  - "long kb job"
  - "run in batches"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Background Jobs

## Contract

- Long jobs are batched, checkpointed, resumable, and validated after each batch.
- Bulk writes only happen after sample quality passes.

## Workflow

- Plan batch size, ordering, retry policy, and stop conditions.
- Run 3-5 item sample and inspect output.
- Checkpoint before and after each batch.
- Validate citations, frontmatter, graph links, and indexes.
- Summarize progress and remaining work.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py checkpoint`
- `python3 plugins/knowledge-base/scripts/kb_ops.py dashboard`


## Output Format

- BACKGROUND JOB
- Batch status, checkpoint, validation, next batch.

## Anti-Patterns

- Running 100 items before inspecting the first 3.
- Losing progress state between sessions.
