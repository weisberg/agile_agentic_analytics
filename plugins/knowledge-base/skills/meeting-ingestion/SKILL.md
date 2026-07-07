---
name: meeting-ingestion
version: 0.2.0
description: >-
  Ingest a meeting transcript or notes into the KB — preserve the raw transcript, extract attendees, decisions, tensions and action items, write an analysis-above-the-line meeting page, and propagate every attendee and company to their entity timelines and back-links. Trigger on 'process this meeting', 'ingest this meeting', 'file this transcript', 'meeting notes to KB'. This is the only skill that owns 'process this meeting'. For non-meeting media (PDF, video, article, voice note) use media-ingest; for the general routing front door use ingest.
triggers:
  - "process this meeting"
  - "ingest this meeting"
  - "file this transcript"
  - "meeting notes to kb"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
disable-model-invocation: false
mutating: true
---

# Meeting Ingestion

## Contract

- The raw transcript or notes are preserved as provenance and trusted over any AI summary.
- Every attendee and notable company/concept is propagated to entity pages.
- The meeting page captures the crux, decisions, changed state, and follow-ups — not a bullet dump.
- Mutating skill: a meeting is incomplete until raw provenance, meeting page, attendee/company back-links, and validation are all handled.

## Intake And Modes

- Treat `$ARGUMENTS` as the transcript/notes plus optional title, date, attendees, vault root, and write scope.
- Quick mode: extract meeting metadata, decisions, and action items without writing.
- Standard mode: create/update one meeting page and immediate entity timelines.
- Deep mode: ingest a meeting series with entity propagation, task extraction, and checkpoints.
- Use `ask-user` when title/date/attendees are ambiguous or when a summary conflicts with the transcript.

## Evidence Requirements

- Prefer the raw transcript over summaries; preserve the source path or redirect pointer.
- Inspect existing meeting/entity pages before creating duplicates and before adding timeline events.

## Workflow

- Preserve the transcript and meeting metadata as raw source.
- Extract attendees, organizations, decisions, action items, dates, and unspoken tensions.
- Write the meeting page with analysis above the raw transcript link.
- Update every attendee/company timeline and back-link (a meeting is not ingested until this is done).
- Run `citation-audit`, `graph-audit`, and `raw-source-audit`.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" citation-audit`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" graph-audit`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" raw-source-audit`


## Output Format

- MEETING INGESTED
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Page, attendees, entities updated, timeline entries, decisions, raw transcript.
- Artifact path: `meetings/<YYYY-MM-DD>-<slug>.md` plus any updated people/company/task pages.

## Anti-Patterns

- Trusting an AI meeting summary over the transcript source.
- Stopping before entity propagation is complete.
