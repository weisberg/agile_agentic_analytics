---
name: dashboard
version: 0.1.0
description: >-
  Produce retrieval, ingestion, quality, and health dashboards for KB operations with trends and actionable remediation.
triggers:
  - "kb dashboard"
  - "retrieval dashboard"
  - "ingestion dashboard"
  - "quality dashboard"
tools:
  - read
  - write
  - exec
  - vaultli
mutating: true
writes_pages: true
---

# Dashboard

## Contract

- Dashboards show metrics that drive action, not vanity counts.
- Every red/yellow status links to a remediation workflow.
- Metrics can be regenerated from files or logs.

## Workflow

- Collect health checks, retrieval benchmark results, ingestion batch outcomes, citation gaps, graph gaps, and generated artifact warnings.
- Compute status by dimension.
- Write dashboard report with trends, blockers, and next actions.
- Link to detailed JSON where available.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py dashboard`


## Output Format

- KB DASHBOARD
- Scores, trends, risks, remediation, source artifacts.

## Anti-Patterns

- Reporting counts without thresholds.
- Hiding failures behind a single composite score.
