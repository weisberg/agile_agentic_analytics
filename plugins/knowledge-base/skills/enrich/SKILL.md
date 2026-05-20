---
name: enrich
version: 0.1.0
description: >-
  Enrich entity and concept pages with tiered lookup, current state, relationships, timelines, citations, and back-links.
triggers:
  - "enrich this kb page"
  - "update entity page"
  - "merge entity info"
  - "refresh this concept"
tools:
  - search
  - get_page
  - put_page
  - add_link
  - add_timeline_entry
  - vaultli
mutating: true
writes_pages: true
---

# Enrich

## Contract

- State sections are rewritten with current best understanding, never blindly appended.
- Every material fact has an inline source citation.
- Every notable person/company mention gets a back-link or an explicit skip reason.

## Workflow

- Load the existing page and related graph context.
- Classify new evidence as confirming, updating, contradicting, or irrelevant.
- Rewrite current state, add timeline entries, and update relationships.
- Run citation and back-link checks.
- Index and validate file-based vaults with `vaultli`.

## Output Format

- ENRICHED
- Page, facts updated, timeline entries, links, citations, conflicts.

## Anti-Patterns

- Appending stale State notes.
- Hiding contradictions instead of routing them.
