---
name: archive-crawler
version: 0.1.0
description: >-
  Crawl allow-listed archives to find valuable documents, ideas, entities, and sources without indiscriminate ingestion.
triggers:
  - "crawl my archive"
  - "find gold in archive"
  - "scan old notes"
  - "archive crawler"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Archive Crawler

## Contract

- Only allow-listed paths are scanned.
- The crawler ranks candidates before ingestion.
- Private or sensitive matches are flagged before writing durable KB pages.

## Workflow

- Load allow-list and exclusion patterns.
- Sample filenames and metadata before reading content.
- Score candidates by originality, entities, decisions, reusable concepts, and source value.
- Present batches for approval when scope is large.
- Ingest approved items with raw preservation and validation.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py privacy-audit`
- `python3 plugins/knowledge-base/scripts/kb_ops.py checkpoint`


## Output Format

- ARCHIVE CRAWL
- Paths scanned, candidates, scores, ingested items, skipped reasons.

## Anti-Patterns

- Scanning unapproved private directories.
- Bulk ingesting low-signal archives.
