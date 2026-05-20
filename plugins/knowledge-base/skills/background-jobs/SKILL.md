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

## Output Format

- BACKGROUND JOB
- Batch status, checkpoint, validation, next batch.

## Anti-Patterns

- Running 100 items before inspecting the first 3.
- Losing progress state between sessions.
