---
name: concept-synthesis
version: 0.1.0
description: >-
  Synthesize concepts, patterns, originals, and fragments into tiered intellectual maps with evidence and links.
triggers:
  - "concept synthesis"
  - "synthesize concepts"
  - "find patterns in kb"
  - "build intellectual map"
tools:
  - search
  - get_page
  - put_page
  - add_link
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Concept Synthesis

## Contract

- Synthesis pages cite supporting pages and preserve original language where important.
- Concepts are deduplicated, tiered, and linked to evidence.
- Weak patterns are kept as hypotheses, not facts.

## Workflow

- Search recent originals, reflections, meeting notes, and concept stubs.
- Cluster by recurring theme and distinguish duplicates from adjacent ideas.
- Select evidence threshold before writing a synthesis page.
- Create or update concept pages with See Also links and provenance.
- Route contradictions to conflict resolution.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py query`
- `python3 plugins/knowledge-base/scripts/kb_ops.py graph-audit`


## Output Format

- CONCEPT SYNTHESIS
- Clusters, pages updated, evidence, hypotheses, links.

## Anti-Patterns

- Overfitting a pattern from one example.
- Paraphrasing original user language that should be quoted.
