---
name: conflict-resolution
version: 0.2.0
description: >-
  Detect, represent, and resolve contradictory KB facts, stale claims, duplicate entities, and competing interpretations while preserving provenance until resolved. Trigger on 'resolve conflicting facts', 'contradiction in the KB', 'this claim is stale/superseded', 'merge these duplicate entities'. This is the dedicated contradiction workflow other skills route to; for a routine page rewrite with no conflict use enrich; for a vault-wide sweep use health.
triggers:
  - "resolve conflicting facts"
  - "contradiction in the kb"
  - "this kb claim is stale"
  - "merge duplicate entities"
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

# Conflict Resolution

## Contract

- Contradictions are preserved with provenance until resolved.
- Resolution states distinguish superseded, disputed, merged, and unresolved.
- The current State section reflects best understanding and remaining uncertainty.
- Mutating skill: it may rewrite State/timeline sections, but it must not erase dissenting evidence without recording the resolution basis.

## Intake And Modes

- Treat `$ARGUMENTS` as the conflicting pages, claims, entities, or duplicate records to reconcile.
- Quick mode: identify the conflict and return a resolution recommendation without writing.
- Standard mode: resolve a bounded page/entity conflict with citations and validation.
- Deep mode: merge duplicate entities or reconcile a multi-page stale-claim cluster.
- Use `ask-user` when both claims are plausible and the resolution depends on user intent or preferred taxonomy.

## Evidence Requirements

- Inspect every cited source, source date, page timeline, and related entity page before resolving.
- Check whether the conflict is scope-based, time-based, source-quality-based, or a true contradiction.

## Workflow

- Identify the conflicting claims and their sources/dates.
- Assess recency, source quality, directness, and scope.
- Choose a resolution: update, mark disputed, split entities, merge duplicates, or `ask-user`.
- Rewrite State and timeline with citations; add a review date for anything unresolved.
- Run `graph-audit` and `citation-audit` after edits.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" graph-audit`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" citation-audit`


## Output Format

- CONFLICT RESOLUTION
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Claims, sources, decision, page updates, unresolved items with review dates.
- Artifact path: updated page path(s), plus optional `reports/<YYYYMMDD>-conflict-resolution.md` for broad reconciliations.

## Anti-Patterns

- Deleting the losing claim without provenance.
- Flattening genuine uncertainty into false certainty.
