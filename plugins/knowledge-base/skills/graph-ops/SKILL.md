---
name: graph-ops
version: 0.1.0
description: >-
  Maintain and query KB relationship graphs, back-links, entity pairs, timelines, and Graph-style relationship interfaces.
triggers:
  - "kb graph"
  - "relationship query"
  - "backlink audit"
  - "graph ops"
tools:
  - search
  - get_page
  - put_page
  - add_link
  - vaultli
mutating: true
writes_pages: true
---

# Graph Ops

## Contract

- Every notable entity mention creates or validates a relationship/back-link.
- Graph queries return typed edges and source evidence.
- Broken or orphaned links produce remediation hints.

## Workflow

- Extract entities and relationship candidates from target pages.
- Validate existing links and back-links.
- Create typed edges such as knows, works_at, founded, discussed, met_at.
- Answer graph queries with path, edge type, source, and confidence.
- Run health checks for orphans and dead links.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py graph-audit`


## Output Format

- GRAPH OPS
- Edges checked, links added, graph query answer, unresolved links.

## Anti-Patterns

- Creating untyped links for every co-mention.
- Answering relationship questions without source evidence.
