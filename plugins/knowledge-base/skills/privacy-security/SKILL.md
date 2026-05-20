---
name: privacy-security
version: 0.1.0
description: >-
  Apply privacy, PII, credential, scope, and publication-safety checks to KB ingestion, retrieval, automation, and publishing.
triggers:
  - "kb privacy"
  - "pii check"
  - "credential safety"
  - "redact kb"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: true
---

# Privacy Security

## Contract

- Sensitive content is classified before broad storage, retrieval, automation, or publication.
- Secrets are never stored in prompts, paths, citations, or raw source manifests.
- Scope downgrades are explicit and reversible.

## Workflow

- Classify content sensitivity: public, team, personal, confidential, secret.
- Detect PII, credentials, private channels, internal paths, and client identifiers.
- Redact, alias, or restrict scope before writing durable pages.
- Document privacy decisions in page frontmatter or output notes.
- Require approval before publication or connector export.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py privacy-audit`


## Output Format

- PRIVACY REVIEW
- Classification, findings, actions, remaining risk.

## Anti-Patterns

- Treating local path leaks as harmless.
- Publishing raw pages because they are cited.
