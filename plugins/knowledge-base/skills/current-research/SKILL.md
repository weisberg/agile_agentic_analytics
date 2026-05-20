---
name: current-research
version: 0.1.0
description: >-
  Research current developments and produce a freshness delta against what the KB already knows.
triggers:
  - "what's new"
  - "current research"
  - "freshness delta"
  - "update this from web"
tools:
  - search
  - read
  - write
  - vaultli
mutating: true
writes_pages: true
---

# Current Research

## Contract

- Current facts are checked against up-to-date sources.
- The output separates already-known KB context from new developments.
- Every web/current claim has source, URL, date, and retrieval date.

## Workflow

- Load current KB page/context first.
- Search current sources and prioritize primary/official sources.
- Build a delta: new, changed, contradicted, unchanged, unknown.
- Update KB pages only when source quality and relevance meet the bar.
- Record freshness and next-review date.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py query`
- `python3 plugins/knowledge-base/scripts/kb_ops.py citation-audit`


## Output Format

- FRESHNESS DELTA
- Known context, new facts, changed facts, sources, KB writes.

## Anti-Patterns

- Overwriting KB context with a single new article.
- Failing to date current claims.
