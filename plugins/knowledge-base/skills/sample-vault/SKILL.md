---
name: sample-vault
version: 0.2.0
description: >-
  Create and maintain the synthetic sample KB vault, fixtures, walkthroughs, and expected outputs used for plugin validation and onboarding demos. Trigger on 'refresh the sample vault', 'KB fixtures', 'worked walkthrough', 'demo KB'. This maintains test/demo data; for a real first-time install and import use setup; for the CLI mechanics it exercises use vaultli.
triggers:
  - "refresh the sample vault"
  - "kb fixtures"
  - "worked kb walkthrough"
  - "demo kb vault"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
disable-model-invocation: false
mutating: true
---

# Sample Vault

## Contract

- Sample vault content is synthetic and non-sensitive.
- Fixtures cover people, company, concept, meeting, source, article, strategic reading, and sidecar assets.
- Walkthroughs include commands and expected outputs and must validate.
- Mutating skill: it may update sample fixtures, but never with real names, private content, credentials, or user-specific paths.

## Intake And Modes

- Treat `$ARGUMENTS` as fixture area, scenario, validation target, or desired walkthrough change.
- Quick mode: validate the existing sample vault and report gaps.
- Standard mode: add or repair one fixture scenario and update expected commands.
- Deep mode: refresh the whole mini-vault, benchmark rows, and walkthrough after schema or CLI changes.
- Use `ask-user` before changing fixture semantics that other tests or examples depend on.

## Evidence Requirements

- Inspect existing sample pages, sidecars, `INDEX.jsonl`, benchmark fixtures, and walkthrough commands before editing.
- Run the bundled CLI and KB harness validations before claiming the fixture is usable.

## Workflow

- Create or refresh `references/samples/mini-vault`.
- Include markdown pages and non-markdown sidecar examples.
- Run `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json init/add/scaffold/index/search/context/validate` command flows and record expected outputs.
- Run `dashboard` and `retrieval-benchmark` to confirm the fixture still passes.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" dashboard`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" retrieval-benchmark`


## Output Format

- SAMPLE VAULT
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Files, commands, expected outputs, benchmark and validation status.
- Artifact path: changed files under `references/samples/mini-vault/`, `references/samples/walkthrough.md`, or benchmark fixtures.

## Anti-Patterns

- Using real private names in fixtures.
- Shipping fixtures that do not validate.
