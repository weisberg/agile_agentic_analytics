---
name: reports
version: 0.2.0
description: >-
  Create a timestamped, saved KB report with a source manifest, the queries used, assumptions, and a reproducible output path. Trigger on 'save this KB report', 'generate a report', 'timestamped output with sources', 'write up this analysis'. For an ephemeral proactive prep briefing use briefing; for privacy-scrubbing and sharing a page externally use publish.
triggers:
  - "save this kb report"
  - "generate a kb report"
  - "timestamped report with sources"
  - "write up this analysis"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
disable-model-invocation: false
mutating: true
---

# Reports

## Contract

- Reports preserve query scope, sources, generation time, and assumptions.
- Outputs are saved under predictable report paths and indexed when useful.
- Mutating skill: report creation is allowed, but every durable report must carry enough source manifest detail to regenerate or audit it.

## Intake And Modes

- Treat `$ARGUMENTS` as report question plus optional audience, date window, source scope, format, and output directory.
- Quick mode: outline the report and source plan before writing.
- Standard mode: generate one markdown report with a source manifest and validation notes.
- Deep mode: generate a multi-source report with assumptions, limitations, appendices, and publish handoff if needed.
- Use `ask-user` when audience or sharing scope changes the evidence/privacy bar.

## Evidence Requirements

- Gather and hydrate all cited KB sources; record query terms, filters, source scope, and generation time.
- Label any live/current research separately and route it through `current-research` before merging into the report.

## Workflow

- Define the report question, audience, and time range.
- Gather KB sources with `query` and cite them in a manifest.
- Write the report with an executive summary, evidence, and next actions.
- Index the report and record regeneration notes with `dashboard`.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" query`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" dashboard`


## Output Format

- REPORT CREATED
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Path, sources, query, assumptions, validation.
- Artifact path: `reports/<YYYYMMDD>-<slug>.md` unless the user specifies a different destination.

## Anti-Patterns

- Saving a report without the source manifest.
- Mixing live research with KB-only reports without labeling it.
