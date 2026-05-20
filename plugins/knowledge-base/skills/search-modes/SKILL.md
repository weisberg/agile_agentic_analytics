---
name: search-modes
version: 0.1.0
description: >-
  Choose keyword, metadata, semantic-overlap, graph, timeline, federated, and benchmarked retrieval modes for KB questions.
triggers:
  - "kb search modes"
  - "retrieval benchmark"
  - "hybrid search"
  - "choose search mode"
tools:
  - search
  - read
  - exec
  - vaultli
mutating: false
writes_pages: false
---

# Search Modes

## Contract

- Retrieval mode matches the question type.
- Benchmarks include representative queries, expected pages, and failure notes.
- Metadata search is not mistaken for body hydration.

## Workflow

- Classify question as exact lookup, concept, relationship, timeline, source, or freshness.
- Use metadata filters before semantic overlap.
- Hydrate shortlisted pages with `resolve`, `cat`, or page tools.
- Record misses and tune titles/descriptions/tags.
- For benchmarks, store query, expected ids, actual ids, and judgement.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py query`
- `python3 plugins/knowledge-base/scripts/kb_ops.py retrieval-benchmark`


## Output Format

- SEARCH MODE
- Mode, query, filters, matches, misses, benchmark notes.

## Anti-Patterns

- Assuming search result metadata loaded full content.
- Using semantic overlap as if it were vector retrieval.
