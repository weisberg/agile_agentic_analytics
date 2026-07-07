# Integration Data Contracts

Connector and webhook payloads should be normalized into this envelope before
ingestion. The goal is to keep email, calendar, docs, browser, webhook, and file
sources from inventing incompatible shapes.

```yaml
schema_version: kb-source-envelope/v1
idempotency_key: provider:event-id-or-content-hash
provider: gmail|calendar|drive|browser|webhook|filesystem|manual
event_type: message|meeting|document|article|file|task|custom
source_uri: provider://stable/source
retrieved_at: 2026-05-20T12:00:00Z
occurred_at: 2026-05-20T11:30:00Z
actor:
  name: Example Person
  email: example@example.com
privacy:
  scope: personal|team|org|public
  contains_pii: false
  contains_secret: false
raw:
  pointer: sources/raw/example.json
  hash: sha256:...
  mime: application/json
routing:
  primary_subject: concepts/example
  candidate_skill: media-ingest
entities:
  people: []
  companies: []
  concepts: []
content:
  title: Example Source
  text_ref: sources/raw/example.txt
```

## Rules

- Never persist connector credentials in the envelope.
- Use `idempotency_key` to make retries safe.
- Route raw payloads through the privacy checks in `health` or `publish` before durable storage.
- Store large bodies as raw pointers, not inline YAML blobs.
- Include enough source metadata for citation repair.
