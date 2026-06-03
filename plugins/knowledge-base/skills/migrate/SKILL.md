---
name: migrate
version: 0.1.0
description: >-
  Migrate Obsidian, Notion, Logseq, Roam, markdown, CSV, and JSON knowledge stores into a KB vault with mapping, dry-run, and redirects.
triggers:
  - "migrate to kb"
  - "import obsidian"
  - "import notion"
  - "convert my notes"
  - "roam to kb"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Migrate

## Contract

- Every migration has a source map, dry-run, sample review, and rollback notes.
- Original exports are preserved.
- Links, aliases, tags, dates, and page ids are mapped explicitly.

## Workflow

- Identify source system and export format.
- Build field/link/tag mapping into KB schemas.
- Run a dry-run and review 3-5 representative migrated pages.
- Execute in batches with checkpoints and validation.
- Record redirects, skipped content, and unresolved conflicts.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py frontmatter-audit`
- `python3 plugins/knowledge-base/scripts/kb_ops.py dashboard`


## Output Format

- MIGRATION REPORT
- Source, mapping, batches, pages, warnings, validation, next steps.

## Anti-Patterns

- Throwing away source ids.
- Converting all links to plain text.
