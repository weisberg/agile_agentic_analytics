---
name: voice-note-ingest
version: 0.1.0
description: >-
  Transcribe and file voice notes while preserving exact user phrasing, original ideas, tasks, decisions, and emotional context.
triggers:
  - "ingest voice note"
  - "transcribe this memo"
  - "file this audio note"
  - "voice note to kb"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true
---

# Voice Note Ingest

## Contract

- Exact memorable phrasing is preserved verbatim.
- Original ideas route to `originals`; tasks route to `task-manager`.
- Private or sensitive content is filtered before broad KB exposure.

## Workflow

- Transcribe with timestamps when available.
- Separate exact quotes, ideas, tasks, decisions, people, and sources.
- File by primary subject and preserve raw audio/transcript.
- Create timeline entries and back-links for notable entities.
- Run privacy and citation checks.

## Output Format

- VOICE NOTE INGESTED
- Transcript, originals captured, tasks, entities, privacy notes.

## Anti-Patterns

- Paraphrasing the user's best wording.
- Dumping an unreviewed transcript into public/team scope.
