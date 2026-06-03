---
name: publish
version: 0.1.0
description: >-
  Prepare KB pages for sharing or publication with privacy scrub, audience scope, export format, and approval gates.
triggers:
  - "publish kb page"
  - "share this page"
  - "prepare for public"
  - "export this note"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Publish

## Contract

- No KB page is shared without privacy, citation, and audience checks.
- Publication creates a derived artifact; the KB source remains intact.

## Workflow

- Identify audience: personal, team, client, public.
- Run privacy/security review and citation check.
- Redact or generalize sensitive names, paths, and raw sources.
- Export markdown/PDF/html as requested, then record publication metadata.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py privacy-audit`
- `python3 plugins/knowledge-base/scripts/kb_ops.py citation-audit`


## Output Format

- PUBLISH PACKAGE
- Artifact path, audience, redactions, citations, approval state.

## Anti-Patterns

- Publishing raw meeting notes.
- Removing citations to make prose cleaner.
