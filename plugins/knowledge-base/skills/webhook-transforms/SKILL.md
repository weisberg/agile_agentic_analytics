---
name: webhook-transforms
version: 0.1.0
description: >-
  Normalize webhook payloads into KB ingestion envelopes with validation, provenance, idempotency, and privacy filters.
triggers:
  - "kb webhook"
  - "transform webhook"
  - "ingest webhook"
  - "webhook to kb"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: true
---

# Webhook Transforms

## Contract

- Webhook payloads are transformed into typed, validated, idempotent KB source envelopes.
- Secrets and credentials are stripped before durable storage.

## Workflow

- Identify provider and event type.
- Validate payload against connector data contracts.
- Map payload to source, entity, event, task, or raw-source envelope.
- Compute idempotency key and privacy classification.
- Route to ingestion or queue for review.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py normalize-event`
- `python3 plugins/knowledge-base/scripts/kb_ops.py privacy-audit`


## Output Format

- WEBHOOK TRANSFORM
- Provider, event, envelope, idempotency key, route.

## Anti-Patterns

- Persisting full raw payloads with secrets.
- Treating retries as new events.
