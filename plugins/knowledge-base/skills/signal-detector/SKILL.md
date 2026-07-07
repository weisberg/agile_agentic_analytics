---
name: signal-detector
version: 0.2.0
description: >-
  Notice durable KB signals in an inbound message — notable people, companies, concepts, decisions, tasks, contradictions — and capture the user's own original phrasing verbatim as a first-class KB original, all without blocking the conversation. Trigger on 'notice entities in this', 'what should go in the KB', 'capture this thought/idea', 'save this exact phrasing', 'this is an original idea'. This skill absorbed originals: exact wording is preserved, never paraphrased. For a whole source document use ingest; for reconciling contradictory facts use conflict-resolution.
triggers:
  - "detect kb signals"
  - "what should go in the kb"
  - "capture this idea"
  - "save this exact phrasing"
  - "capture original thinking"
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

# Signal Detector

## Contract

- Every inbound message can be scanned for durable KB signals without blocking the reply.
- Low-confidence or low-value mentions are ignored instead of cluttering the KB.
- The user's original phrasing is preserved verbatim when the wording IS the insight; derivative synthesis links back, never overwrites.
- Mutating skill: lightweight writes are allowed only for durable signals that pass notability and privacy checks.

## Intake And Modes

- Treat `$ARGUMENTS` as the message/source text plus optional vault root, privacy scope, and write permission.
- Quick mode: list candidate signals and what would be filed.
- Standard mode: capture high-confidence signals and original phrasing with citations.
- Deep mode: scan a longer conversation/source set and queue entity/task/enrichment follow-ups.
- Use `ask-user` when original phrasing is sensitive, filing destination is ambiguous, or a low-confidence signal would create a new page.

## Evidence Requirements

- Search existing pages before creating new entities and apply `references/kb-filing-rules.md`.
- Preserve exact wording for originals and record source context/date for every captured signal.

## Workflow

- Classify signals: entity, event, decision, task, source, original thought, contradiction, or privacy-sensitive.
- Apply the notability gate in `references/kb-filing-rules.md`; search before creating any new page.
- For original thinking, quote the exact phrasing with trigger/source context and date; file under originals/concepts.
- Queue or perform lightweight page updates with citations and back-links.
- Route contradictions to `conflict-resolution` and full documents to `ingest`.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" query`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" privacy-audit`


## Output Format

- SIGNAL DETECTION
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Detected signals, originals captured verbatim, action taken, skipped items, privacy notes.
- Artifact path: updated entity/original/task paths, or inline candidate list when no writes are made.

## Anti-Patterns

- Creating a page for every noun.
- Paraphrasing or polishing the user's original idea when the wording matters.
- Blocking the conversation on KB writes.
