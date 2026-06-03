---
name: media-ingest
version: 0.1.0
description: >-
  Ingest PDFs, books, video, audio, screenshots, repos, and other media into the KB with extraction, sidecars, transcripts, and citations.
triggers:
  - "ingest media"
  - "process this pdf"
  - "process this video"
  - "save this screenshot"
  - "ingest repo"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Media Ingest

## Contract

- Media gets a durable raw source record and a KB page filed by primary subject.
- Transcripts, OCR, and extracted text are linked from the page.
- Quotes and recommendations are grounded in source locations.

## Workflow

- Classify media type and choose extractor: text, OCR, transcript, metadata, or repo scan.
- Preserve raw asset or redirect pointer.
- Create markdown page or sidecar with frontmatter.
- Extract entities, quotes, claims, and reusable concepts.
- Index, validate, and route to specialized skills when needed.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py raw-source-audit`
- `python3 plugins/knowledge-base/scripts/kb_ops.py privacy-audit`


## Output Format

- MEDIA INGESTED
- Media type, page, extracted assets, entities, validation.

## Anti-Patterns

- Filing everything under media when a subject page is better.
- Omitting transcript links for audio/video.
