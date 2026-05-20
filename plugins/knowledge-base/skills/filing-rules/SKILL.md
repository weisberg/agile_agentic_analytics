---
name: filing-rules
version: 0.1.0
description: >-
  Apply and evolve KB filing architecture: page types, directory placement, slug rules, back-links, and source-preservation conventions.
triggers:
  - "kb filing rules"
  - "where should this go"
  - "filing architecture"
  - "page type rules"
tools:
  - read
  - write
mutating: true
writes_pages: true
---

# Filing Rules

## Contract

- Content is filed by primary subject, not source format.
- Directory choice, slug, page type, and relationship rules are explicit.
- Rule changes are reflected in references and schema examples.

## Workflow

- Read `ingest/references/kb-filing-rules.md` and schema references.
- Identify primary subject and secondary references.
- Choose page type, slug, raw source location, and backlink obligations.
- If ambiguous, use `ask-user` with 2-4 options and an escape hatch.
- Update filing references when a new durable class appears.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py frontmatter-audit`
- `python3 plugins/knowledge-base/scripts/kb_ops.py graph-audit`


## Output Format

- FILING DECISION
- Destination, slug, rationale, links, and unresolved choices.

## Anti-Patterns

- Filing by file format when a subject page exists.
- Creating parallel directory systems for the same concept.
