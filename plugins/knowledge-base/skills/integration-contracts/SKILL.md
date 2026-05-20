---
name: integration-contracts
version: 0.1.0
description: >-
  Define data contracts for connector and integration payloads that feed the KB, including emails, calendars, docs, webhooks, and files.
triggers:
  - "kb data contract"
  - "connector contract"
  - "integration schema"
  - "payload schema"
tools:
  - read
  - write
mutating: true
writes_pages: true
---

# Integration Contracts

## Contract

- Every connector payload maps to a typed KB envelope with provenance, privacy scope, idempotency key, and destination hint.
- Contracts are versioned and validated before ingestion.

## Workflow

- Identify connector and event/source types.
- Define envelope fields: source, actor, timestamp, content refs, privacy, idempotency, entities, raw pointer.
- Map fields to page schemas and ingestion routes.
- Add examples and validation notes.
- Route webhook payloads through `webhook-transforms`.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py normalize-event`
- `python3 plugins/knowledge-base/scripts/kb_ops.py validate-schedule`


## Output Format

- INTEGRATION CONTRACT
- Connector, envelope, schema path, examples, route.

## Anti-Patterns

- Letting every connector invent its own shape.
- Omitting idempotency and privacy fields.
