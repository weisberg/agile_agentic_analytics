---
name: maintenance
version: 0.1.0
description: >-
  Maintain stale pages, orphan pages, dead links, missing back-links, citation gaps, timelines, and vault index state.
triggers:
  - "kb maintenance"
  - "stale pages"
  - "orphan pages"
  - "fix backlinks"
  - "maintain kb"
tools:
  - search
  - get_page
  - put_page
  - add_link
  - exec
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Maintenance

## Contract

- Maintenance checks all core KB dimensions and emits specific fixes.
- Graph, citations, frontmatter, timelines, stale state, and source preservation are included.
- Bulk remediation is sampled before large writes.

## Workflow

- Run `health` and `dashboard` checks.
- Fix frontmatter/index issues first, then citations, then graph/backlinks, then stale state.
- Merge duplicate entities and route contradictions.
- Rebuild indexes and rerun health.
- Record remaining manual decisions.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py maintenance-plan`
- `python3 plugins/knowledge-base/scripts/kb_ops.py dashboard`


## Output Format

- KB MAINTENANCE
- Dimensions checked, fixes, remaining issues, health delta.

## Anti-Patterns

- Fixing stale pages without checking latest timeline/source evidence.
- Deleting orphans without determining whether links are missing.
