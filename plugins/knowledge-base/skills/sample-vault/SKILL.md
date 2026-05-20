---
name: sample-vault
version: 0.1.0
description: >-
  Create and maintain synthetic sample KB vaults, fixtures, walkthroughs, and expected outputs for plugin validation and onboarding.
triggers:
  - "sample vault"
  - "kb fixtures"
  - "worked walkthrough"
  - "demo kb"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true
---

# Sample Vault

## Contract

- Sample vault content is synthetic and non-sensitive.
- Fixtures cover people, company, concept, meeting, source, article, strategic reading, and sidecar assets.
- Walkthroughs include commands and expected outputs.

## Workflow

- Create or refresh `references/samples/mini-vault`.
- Include markdown pages and non-markdown sidecar examples.
- Run `vaultli init/add/scaffold/index/search/context/validate` where available.
- Record expected outputs and known environment assumptions.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py dashboard`
- `python3 plugins/knowledge-base/scripts/kb_ops.py retrieval-benchmark`


## Output Format

- SAMPLE VAULT
- Files, commands, expected outputs, validation.

## Anti-Patterns

- Using real private names in fixtures.
- Shipping fixtures that do not validate.
