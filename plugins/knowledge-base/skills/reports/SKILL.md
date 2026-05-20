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

## Output Format

- REPORT CREATED
- Path, sources, query, assumptions, validation.

## Anti-Patterns

- Saving a report without the source manifest.
- Mixing live research with KB-only reports without labeling it.
