---
name: reports
version: 0.1.0
description: >-
  Create timestamped saved KB reports with source manifests, queries used, and reproducible output paths.
triggers:
  - "kb report"
  - "save this report"
  - "generate report"
  - "timestamped output"
tools:
  - search
  - read
  - write
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Reports

## Contract

- Reports preserve query scope, sources, generation time, and assumptions.
- Outputs are saved under predictable report paths and indexed when useful.

## Workflow

- Define report question, audience, and time range.
- Gather KB sources and cite them in a manifest.
- Write report with executive summary, evidence, and next actions.
- Index report and record regeneration notes.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py query`
- `python3 plugins/knowledge-base/scripts/kb_ops.py dashboard`


## Output Format

- REPORT CREATED
- Path, sources, query, assumptions, validation.

## Anti-Patterns

- Saving a report without the source manifest.
- Mixing live research with KB-only reports without labeling it.
