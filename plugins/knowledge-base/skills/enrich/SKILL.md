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

disable-model-invocation: false
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

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py citation-audit`
- `python3 plugins/knowledge-base/scripts/kb_ops.py graph-audit`


## Output Format

- ENRICHED
- Page, facts updated, timeline entries, links, citations, conflicts.

## Anti-Patterns

- Appending stale State notes.
- Hiding contradictions instead of routing them.
