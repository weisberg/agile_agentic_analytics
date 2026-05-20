---
name: kb-ops
version: 0.1.0
description: >-
  Core operations router for KB maintenance, retrieval, ingestion, graph, privacy, health, setup, and release workflows.
triggers:
  - "kb ops"
  - "knowledge base operations"
  - "operate kb"
  - "run kb workflow"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true
---

# Kb Ops

## Contract

- Routes to the right KB skill instead of duplicating workflow logic.
- Operational decisions include scope, risk, validation, and next action.
- Complex work checkpoints progress.

## Workflow

- Classify request: setup, ingest, query, enrich, maintain, publish, automate, release, or repair.
- Read the target child skill and follow it.
- Use `ask-user` for meaningful forks.
- Run validation and produce a concise operational report.

## Output Format

- KB OPS
- Route, child skill, actions, validation, next step.

## Anti-Patterns

- Doing generic assistant work when a child skill exists.
- Skipping validation after writes.
