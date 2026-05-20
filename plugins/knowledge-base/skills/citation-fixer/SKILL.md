---
name: citation-fixer
version: 0.1.0
description: >-
  Audit and repair KB citations so every factual claim has inline source provenance with date and origin.
triggers:
  - "fix citations"
  - "audit kb citations"
  - "missing sources"
  - "citation fixer"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true
---

# Citation Fixer

## Contract

- Every factual claim in durable KB pages must have a source citation or be flagged.
- Synthetic, inferred, and compiled claims are labeled accurately.
- Unverifiable claims are marked for review rather than laundered into certainty.

## Workflow

- Scan target pages for uncited factual sentences, timelines, and quotes.
- Use raw source links, sidecars, and page frontmatter to recover provenance.
- Normalize citations to the KB citation formats in `ingest/references/quality.md`.
- Flag unverifiable claims with TODO review notes.
- Run `vaultli validate` after edits.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py citation-audit`


## Output Format

- CITATION AUDIT
- Pages checked, citations fixed, unresolved claims, validation status.

## Anti-Patterns

- Inventing a source to satisfy the format.
- Adding one citation to a paragraph of unrelated facts.
