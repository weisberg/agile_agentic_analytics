---
name: setup
version: 0.1.0
description: >-
  First-time setup wizard for the knowledge-base plugin, vaultli, sample vaults, source scopes, privacy defaults, and validation.
triggers:
  - "setup knowledge base"
  - "kb setup"
  - "first time kb"
  - "configure kb"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true
---

# Setup

## Contract

- Setup produces a working local plugin/vault path and a validation result.
- User choices for source scope, privacy, and sample data are explicit.
- Every setup step has a skip path.

## Workflow

- Validate plugin load path and `vaultli --help`.
- Offer sample vault, existing vault, or new vault setup.
- Set privacy/source-scope defaults.
- Run `vaultli init/index/validate` as appropriate.
- Run plugin health and produce next steps.

## Output Format

- KB SETUP
- Mode, vault root, validation, skipped steps, next actions.

## Anti-Patterns

- Assuming a vault path.
- Failing silently when `vaultli` is unavailable.
