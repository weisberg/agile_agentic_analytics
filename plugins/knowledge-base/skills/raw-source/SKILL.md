---
name: raw-source
version: 0.1.0
description: >-
  Preserve raw sources, large media redirects, source manifests, hashes, and restore instructions for ingested KB items.
triggers:
  - "preserve raw source"
  - "raw source storage"
  - "source manifest"
  - "upload raw"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Raw Source

## Contract

- Every ingested item has recoverable provenance.
- Large or binary assets use redirect/pointer records instead of bloating git.
- Hashes and access instructions are recorded.

## Workflow

- Classify source size, media type, sensitivity, and retention needs.
- Store small text/PDF sources in sidecars or `.raw/`-style paths.
- Use redirect pointer metadata for large or binary sources.
- Record hash, size, mime type, source URL/path, and access method.
- Link raw source from the KB page.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py raw-source-audit`


## Output Format

- RAW SOURCE STORED
- Page, raw path/pointer, hash, size, restore command.

## Anti-Patterns

- Writing unverifiable pages without source links.
- Committing huge binaries to the plugin or KB repo.
