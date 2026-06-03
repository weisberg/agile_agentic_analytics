---
name: meeting-ingestion
version: 0.1.0
description: >-
  Ingest meeting transcripts or notes into the KB with attendee propagation, decisions, tensions, timeline updates, and raw transcript links.
triggers:
  - "process this meeting"
  - "ingest meeting"
  - "meeting notes to kb"
  - "file this transcript"
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

# Meeting Ingestion

## Contract

- The raw transcript or notes are preserved as provenance.
- Every attendee and notable company/concept is propagated to entity pages.
- Meeting pages capture crux, decisions, changed state, and follow-ups.

## Workflow

- Preserve transcript and meeting metadata.
- Extract attendees, organizations, decisions, action items, dates, and tensions.
- Write meeting page with analysis above raw transcript links.
- Update attendee/company timelines and back-links.
- Run citation and graph integrity checks.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py citation-audit`
- `python3 plugins/knowledge-base/scripts/kb_ops.py graph-audit`
- `python3 plugins/knowledge-base/scripts/kb_ops.py raw-source-audit`


## Output Format

- MEETING INGESTED
- Page, attendees, entities updated, timeline entries, raw transcript.

## Anti-Patterns

- Trusting AI meeting summaries over transcript source.
- Stopping before entity propagation is complete.
