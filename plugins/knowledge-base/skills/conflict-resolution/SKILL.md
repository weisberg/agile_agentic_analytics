---
name: conflict-resolution
version: 0.1.0
description: >-
  Detect, represent, and resolve contradictory KB facts, stale claims, duplicate entities, and competing interpretations.
triggers:
  - "kb conflict"
  - "contradiction in kb"
  - "resolve conflicting facts"
  - "stale claim"
tools:
  - search
  - get_page
  - put_page
  - add_link
  - vaultli
mutating: true
writes_pages: true
---

# Conflict Resolution

## Contract

- Contradictions are preserved with provenance until resolved.
- Resolution states distinguish superseded, disputed, merged, and unresolved.
- The current State section reflects best understanding and uncertainty.

## Workflow

- Identify conflicting claims and their sources/dates.
- Assess recency, source quality, directness, and scope.
- Choose resolution: update, mark disputed, split entities, merge duplicates, or ask user.
- Rewrite State and timeline with citations.
- Add review date for unresolved conflicts.

## Output Format

- CONFLICT RESOLUTION
- Claims, sources, decision, page updates, unresolved items.

## Anti-Patterns

- Deleting the losing claim without provenance.
- Flattening uncertainty into false certainty.
