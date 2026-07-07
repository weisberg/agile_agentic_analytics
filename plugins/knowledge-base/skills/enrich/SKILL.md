---
name: enrich
version: 0.2.0
description: >-
  Enrich an existing entity or concept page — rewrite current state from evidence, add timeline entries, update typed relationships and back-links, and attach inline citations. Trigger on 'enrich this page', 'update this entity/company page', 'merge this info into the page', 'refresh this concept'. For detecting brand-new signals in a message use signal-detector; for repairing missing citations across pages use citation-fixer; contradictory facts are routed to conflict-resolution.
triggers:
  - "enrich this kb page"
  - "update this entity page"
  - "merge this info into the page"
  - "refresh this concept"
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

# Enrich

## Contract

- State sections are rewritten with current best understanding, never blindly appended.
- Every material fact carries an inline source citation.
- Every notable person/company mention gets a back-link or an explicit skip reason.
- Mutating skill: enrichment writes are allowed only after existing state, graph context, and provenance have been inspected.

## Intake And Modes

- Treat `$ARGUMENTS` as the target page/entity plus optional new evidence, vault root, and write scope.
- Quick mode: recommend enrichment changes without writing.
- Standard mode: update one page and its immediate entity back-links.
- Deep mode: refresh a page cluster with timelines, typed relationships, and contradiction routing.
- Use `ask-user` before merging entities, changing page type, or overwriting ambiguous State language.

## Evidence Requirements

- Load the target page, its linked sources, related entity pages, and graph context before editing.
- Classify each new fact as confirming, updating, contradicting, duplicate, or irrelevant.

## Workflow

- Load the existing page and its graph context with `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json resolve` or `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json context`.
- Classify new evidence as confirming, updating, contradicting, or irrelevant.
- Rewrite current state, add reverse-chronological timeline entries, and update typed relationships.
- Run `citation-audit` and `graph-audit`; route contradictions to `conflict-resolution`.
- Reindex and validate the vault with `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index --root <kb-root>` and `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root <kb-root>`.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" citation-audit`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" graph-audit`


## Output Format

- ENRICHED
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Page, facts updated, timeline entries, links, citations, routed conflicts.
- Artifact path: updated page path(s), plus any source sidecars created.

## Anti-Patterns

- Appending stale State notes instead of rewriting.
- Hiding contradictions instead of routing them.
- Leaving notable mentions without back-links.
