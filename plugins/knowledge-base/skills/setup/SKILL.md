---
name: setup
version: 0.2.0
description: >-
  First-run setup and import wizard for the knowledge-base plugin — validate the plugin/vaultli install, choose a sample, existing, or new vault, set privacy and source-scope defaults, then run the gated cold-start import across files, contacts, meetings, articles, notes, and repositories with sample-before-bulk checks. Trigger on 'set up my KB', 'first-time KB setup', 'configure KB', 'cold start', 'bootstrap knowledge base', 'first import'. Absorbs cold-start. To migrate an existing tool's export use migrate; for synthetic demo fixtures use sample-vault.
triggers:
  - "set up my kb"
  - "first time kb setup"
  - "configure the kb plugin"
  - "cold start kb"
  - "bootstrap knowledge base"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
disable-model-invocation: false
mutating: true
---

# Setup

## Contract

- Setup produces a working local plugin/vault path and a validation result; every step has a skip path.
- Each import phase is gated with an explicit user choice and runs on a sample before bulk execution.
- Privacy, source-scope, and sample-data choices are recorded.
- Mutating skill: setup may initialize or import into a vault, but never bulk-imports until the user has reviewed a sample.

## Intake And Modes

- Treat `$ARGUMENTS` as desired vault mode (sample, existing, or new), root path, source scope, and import phases.
- Quick mode: verify plugin/vaultli availability and recommend setup mode.
- Standard mode: initialize or connect one vault and run validation plus a small import sample.
- Deep mode: guide a first-run import across multiple source types with gates and checkpoints.
- Use `ask-user` for vault mode, privacy defaults, import phase selection, and any bulk-import approval.

## Evidence Requirements

- Inspect plugin root, vault root, `.kbroot`/frontmatter state, and sample validation before imports.
- Preserve original sources and record privacy/source-scope defaults before writing durable pages.

## Workflow

- Validate the plugin load path and `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json --help`.
- Offer sample vault, existing vault, or new vault; set privacy/source-scope defaults.
- Run `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json init/index/validate` as appropriate.
- Offer gated import phases (files, contacts, meetings, articles, notes, repositories); sample 3-5 items per phase, then bulk with checkpoints.
- Run `frontmatter-audit` and `dashboard`, then produce a setup report and next steps.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" frontmatter-audit`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" dashboard`


## Output Format

- KB SETUP
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Mode, vault root, import phases, validation, skipped steps, next actions.
- Artifact path: vault root plus any setup report at `reports/<YYYYMMDD>-kb-setup.md`.

## Anti-Patterns

- Assuming a vault path, or failing silently when the bundled vaultli wrapper is unavailable.
- Bulk importing before reviewing sample quality, or asking multiple gates at once.
