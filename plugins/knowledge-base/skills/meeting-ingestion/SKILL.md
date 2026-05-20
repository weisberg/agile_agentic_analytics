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

## Output Format

- MEETING INGESTED
- Page, attendees, entities updated, timeline entries, raw transcript.

## Anti-Patterns

- Trusting AI meeting summaries over transcript source.
- Stopping before entity propagation is complete.
