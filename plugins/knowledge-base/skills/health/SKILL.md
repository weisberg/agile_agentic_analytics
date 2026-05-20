---
name: health
version: 0.1.0
description: >-
  Run KB plugin health checks, vault health, skill conformance, generated artifact warnings, and remediation hints.
triggers:
  - "kb health"
  - "knowledge base doctor"
  - "check kb plugin"
  - "skillpack health"
tools:
  - read
  - exec
  - vaultli
mutating: false
writes_pages: false
---

# Health

## Contract

- Health output is both human-readable and machine-actionable.
- Warnings and failures include concrete remediation.
- Vault, skill, manifest, marketplace, and generated-artifact checks are visible.

## Workflow

- Run `/plugin-manager:plugin-health` or `plugin_audit.py` for packaging.
- Run `vaultli validate` for file-based vaults.
- Run upstream ledger and KB terminology checks when imported skills are involved.
- Summarize failures, warnings, and remediation actions.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py dashboard`
- `python3 plugins/knowledge-base/scripts/kb_ops.py resolver-check`


## Output Format

- KB HEALTH
- Verdict, failures, warnings, actions, JSON evidence.

## Anti-Patterns

- Treating ignored generated files as invisible packaging risk.
- Returning only prose when CI needs JSON.
