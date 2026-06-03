---
name: resolver
version: 0.1.0
description: >-
  Route user intents across knowledge-base skills, maintain routing evals, and prevent overlapping or orphaned skills.
triggers:
  - "resolve kb skill"
  - "route this kb request"
  - "check kb resolver"
  - "routing eval"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Resolver

## Contract

- Every user-facing KB skill has at least one realistic trigger and no orphaned routing intent.
- Routing eval fixtures may contain `//` comments and JSONL cases with `intent`, `expected_skill`, and optional `ambiguous_with`.
- Overlaps are documented as intentional chains or corrected by tightening descriptions.

## Workflow

- Inventory `skills/*/SKILL.md` and collect names, descriptions, triggers, tools, and mutability.
- Read any `routing-eval.jsonl` files; skip blank lines and `//` comments.
- Classify each fixture as exact, fuzzy, ambiguous, or orphaned.
- When routing is ambiguous, decide whether the skills should chain, merge, or split by user outcome.
- Update trigger wording, routing fixtures, or skill descriptions, then rerun `plugin-health`.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py resolver-check`


## Output Format

- ROUTING REPORT
- Skills checked, fixture counts, overlaps, orphans, and fixes applied.

## Anti-Patterns

- Adding generic triggers such as 'help me' that steal unrelated work.
- Deleting ambiguity instead of documenting an intentional skill chain.
