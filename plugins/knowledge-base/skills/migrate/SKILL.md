---
name: migrate
version: 0.2.0
description: >-
  Bring an existing knowledge store into a KB vault — Obsidian, Notion, Logseq, Roam, markdown, CSV, JSON exports, and loose local file archives — with source mapping, dry-run, sample review, allow-listed crawling, candidate ranking, redirects, and rollback notes. Trigger on 'migrate to KB', 'import Obsidian/Notion/Roam', 'convert my notes', 'crawl my archive for gold', 'scan my old notes'. Absorbs archive-crawler. For first-run plugin/vault setup and the guided import wizard use setup; for a single source document use ingest.
triggers:
  - "migrate to kb"
  - "import obsidian"
  - "import notion"
  - "convert my notes"
  - "crawl my archive"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
disable-model-invocation: false
mutating: true
---

# Migrate

## Contract

- Every migration has a source map, dry-run, sample review, and rollback notes; original exports are preserved.
- Links, aliases, tags, dates, and page ids are mapped explicitly, not thrown away.
- Archive crawls only scan allow-listed paths and rank candidates before ingestion.
- Mutating skill: it may write migrated pages only after a dry-run and representative sample have been reviewed.

## Intake And Modes

- Treat `$ARGUMENTS` as source system/path plus optional vault root, allow-list, exclusions, and target schemas.
- Quick mode: inspect the export/archive and return a migration plan.
- Standard mode: migrate a sampled set, validate mapping, then run a bounded batch.
- Deep mode: orchestrate a multi-batch migration with redirects, rollback notes, and checkpoints.
- Use `ask-user` before scanning broad directories, dropping fields, or applying a lossy mapping.

## Evidence Requirements

- Inspect source metadata, link/tag/date fields, sample pages, and existing destination pages before writing.
- Preserve original exports and document every skipped or unmapped field.

## Workflow

- Identify the source system / export format, or load the archive allow-list and exclusion patterns.
- Build a field/link/tag mapping into KB schemas; for archives, score candidates by originality, entities, decisions, and source value before reading bodies.
- Run a dry-run and review 3-5 representative migrated or ranked pages.
- Execute in batches with checkpoints and validation (delegate long runs to `background-jobs`).
- Record redirects, skipped content, and unresolved conflicts.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" frontmatter-audit`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" dashboard`


## Output Format

- MIGRATION REPORT
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Source, mapping, batches, pages, ranked candidates, warnings, validation, next steps.
- Artifact path: `reports/<YYYYMMDD>-migration-report.md` plus migrated page paths and rollback notes.

## Anti-Patterns

- Throwing away source ids or converting links to plain text.
- Scanning unapproved private directories, or bulk-ingesting low-signal archives.
