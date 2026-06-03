---
name: signal-detector
version: 0.1.0
description: >-
  Detect notable people, companies, concepts, tasks, decisions, and original thinking in inbound messages without blocking the conversation.
triggers:
  - "detect kb signals"
  - "capture signals"
  - "notice entities"
  - "what should go in kb"
tools:
  - search
  - get_page
  - put_page
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Signal Detector

## Contract

- Every inbound message can be scanned for durable KB signals.
- Low-confidence or low-value mentions are ignored instead of cluttering the KB.
- Original user phrasing is preserved verbatim when it is the insight.

## Workflow

- Classify signals: entity, event, decision, task, source, original thought, contradiction, or privacy-sensitive.
- Apply notability gates from `ingest/references/kb-filing-rules.md`.
- Search before creating new pages.
- Queue or perform lightweight updates with citations and back-links.
- Route exact phrasing to `originals` and conflicts to `conflict-resolution`.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py query`
- `python3 plugins/knowledge-base/scripts/kb_ops.py privacy-audit`


## Output Format

- SIGNAL DETECTION
- Detected signals, action taken, skipped items, and privacy notes.

## Anti-Patterns

- Creating pages for every noun.
- Paraphrasing the user's original idea when wording matters.
