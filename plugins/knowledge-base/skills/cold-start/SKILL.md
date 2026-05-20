---
name: cold-start
version: 0.1.0
description: >-
  First-run import wizard for building a KB from selected sources with explicit phase gates, samples, privacy checks, and validation.
triggers:
  - "set up my kb"
  - "cold start kb"
  - "first import"
  - "bootstrap knowledge base"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true
---

# Cold Start

## Contract

- Each import source is gated with explicit user choice and a skip option.
- Imports run on samples before bulk execution.
- Privacy and source-scope decisions are recorded.

## Workflow

- Initialize or locate a vault with `vaultli root/init`.
- Offer import phases: files, contacts/people, meetings, articles, notes, repositories, exports.
- For each phase, sample 3-5 items, validate quality, then bulk ingest with checkpoints.
- Build index, run health audit, and produce setup report.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py dashboard`
- `python3 plugins/knowledge-base/scripts/kb_ops.py frontmatter-audit`


## Output Format

- KB COLD START
- Sources, sample results, bulk status, skipped phases, validation.

## Anti-Patterns

- Bulk importing before reviewing sample quality.
- Asking multiple choice gates at once.
