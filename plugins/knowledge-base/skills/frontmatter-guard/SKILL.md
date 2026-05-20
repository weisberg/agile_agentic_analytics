---
name: frontmatter-guard
version: 0.1.0
description: >-
  Validate and repair YAML frontmatter, sidecars, ids, aliases, tags, lifecycle fields, and stale indexes in file-based KB vaults.
triggers:
  - "validate frontmatter"
  - "fix frontmatter"
  - "page lint"
  - "kb lint"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true
---

# Frontmatter Guard

## Contract

- Markdown pages and non-markdown sidecars have valid YAML frontmatter.
- Required fields match the KB schema and vaultli expectations.
- Indexes are rebuilt; derived files are never edited by hand.

## Workflow

- Run `vaultli ingest --dry-run` for bulk discovery.
- Repair missing ids, titles, descriptions, source fields, tags, and status values.
- Scaffold sidecars for non-markdown assets.
- Run `vaultli index` and `vaultli validate`.
- Report remaining schema exceptions.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py frontmatter-audit`


## Output Format

- FRONTMATTER GUARD
- Files fixed, sidecars created, validation errors, index status.

## Anti-Patterns

- Editing `INDEX.jsonl` directly.
- Changing ids without recording redirects or relationship impact.
