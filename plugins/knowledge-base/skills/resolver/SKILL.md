---
name: resolver
version: 0.2.0
description: >-
  Route a knowledge-base request to the one right KB skill and keep the routing surface healthy — inventory skills, run routing evals, tighten overlapping triggers, and dispatch operational work to a child skill. Trigger on 'which KB skill', 'route this KB request', 'operate the KB workflow', 'fix KB routing', 'resolver check', 'overlapping KB skills'. This is the meta-router and operations entry point (it absorbed the old kb-ops router); it dispatches but does not itself ingest, enrich, or answer. To actually answer a question use query; to audit vault health use health.
triggers:
  - "route this kb request"
  - "which kb skill"
  - "operate the kb workflow"
  - "resolver check"
  - "check kb routing"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
disable-model-invocation: false
mutating: true
---

# Resolver

## Contract

- Every user-facing KB skill has at least one realistic routing fixture and no orphaned intent.
- Routing eval fixtures may contain `//` comments and JSONL cases with `intent`, `expected_skill`, and optional `ambiguous_with`.
- As the operations entry point, resolver dispatches to a child skill and never re-implements its workflow inline.
- Overlaps are documented as intentional chains or corrected by tightening descriptions.
- Mutating skill: it may update routing fixtures and skill descriptions, but only after identifying the specific ambiguity or orphaned intent.

## Intake And Modes

- Treat `$ARGUMENTS` as the request, fixture path, plugin scope, or overlap to inspect.
- Quick mode: route one user request to the owning skill and explain the boundary.
- Standard mode: run resolver checks, inspect fixtures, and patch a bounded ambiguity.
- Deep mode: audit the full KB routing surface after consolidation or a new skill addition.
- Use `ask-user` when a request is genuinely ambiguous and the desired user outcome cannot be inferred.

## Evidence Requirements

- Inspect skill descriptions, representative triggers, `references/routing-eval.jsonl`, and resolver-check output before editing routing.
- Preserve deliberate chains; only remove overlap when two skills claim the same user outcome.

## Workflow

- Classify the request: setup, ingest, query, enrich, maintain, publish, automate, or repair — then name the owning skill.
- Inventory `skills/*/SKILL.md` names, descriptions, triggers, tools, and mutability with `resolver-check`.
- Read `references/routing-eval.jsonl`; skip blank lines and `//` comments; classify each fixture as exact, fuzzy, ambiguous, or orphaned.
- When routing is ambiguous, decide whether the skills should chain, merge, or split by user outcome; use `ask-user` for a real fork.
- Hand off to the chosen child skill, then update trigger wording or fixtures and rerun `resolver-check`.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" resolver-check`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" skill-inventory`


## Output Format

- ROUTING REPORT
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Request class, chosen skill, fixture counts, overlaps, orphans, dispatch, and fixes applied.
- Artifact path: updated `references/routing-eval.jsonl` or touched `skills/<name>/SKILL.md` paths when fixes are made.

## Anti-Patterns

- Doing generic assistant work when a dedicated child skill exists.
- Adding generic triggers such as 'help me' that steal unrelated work.
- Deleting ambiguity instead of documenting an intentional skill chain.
