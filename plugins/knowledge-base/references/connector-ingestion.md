# Connector & Webhook Ingestion Reference

Detail behind the ingestion front door for connector and webhook payloads.
Formerly the `integration-contracts` and `webhook-transforms` skills; both are
now reference material. The runtime home is `ingest` (routing) and the schema is
`references/schemas/integration-contracts.md`.

## Typed Source Envelope

Every connector payload maps to one typed KB source envelope before it touches a
page. Contracts are versioned and validated before ingestion; validate with
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" normalize-event`.

Envelope fields:

- `schema_version` — e.g. `kb-source-envelope/v1`.
- `source` / `provider` — origin system.
- `actor` — who or what produced the event.
- `timestamp` — event time.
- `content` — title and body references (never raw secrets).
- `entities` — extracted people, companies, concepts.
- `privacy_scope` — `personal` / `team` / `org` / `public` (see
  `privacy-and-security.md`).
- `idempotency_key` — deterministic key so retries are not treated as new
  events.
- `raw_pointer` — pointer to preserved raw source (see
  `raw-source-storage.md`).
- `destination_hint` — page type / directory the content should file under.

## Webhook Transform Rules

1. Identify the provider and event type.
2. Validate the payload against the connector data contract.
3. Map it to a `source`, `entity`, `event`, `task`, or `raw-source` envelope.
4. Compute the idempotency key and privacy classification.
5. **Strip secrets and credentials before durable storage.** Never persist full
   raw payloads containing tokens.
6. Route to ingestion or queue for review.

## Anti-Patterns

- Letting every connector invent its own payload shape.
- Omitting idempotency and privacy fields.
- Treating retries as new events.
- Persisting raw payloads with secrets in citations, paths, or manifests.

## Scheduling

For recurring connector polls and KB jobs, see `references/automation.md` (job
envelope, quiet hours, idempotent prompts, health checks). Orchestrate long
backfills through the `background-jobs` skill.
