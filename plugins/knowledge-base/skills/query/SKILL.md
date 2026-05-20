---
name: query
version: 0.1.0
description: >-
  Answer questions from the KB first, using indexed search, graph context, source citations, and freshness notes before external research.
triggers:
  - "ask the kb"
  - "search the knowledge base"
  - "what does the kb know"
  - "answer from kb"
tools:
  - search
  - get_page
  - vaultli
mutating: false
writes_pages: false
---

# Query

## Contract

- Search the KB before using external research unless the user asks for current web facts.
- Every answer distinguishes cited KB facts, inference, and unknowns.
- Freshness gaps are explicit and can route to `current-research`.

## Workflow

- Identify entity, concept, timeline, relationship, and source constraints in the question.
- Use `vaultli search` or KB search modes to shortlist pages; hydrate with `resolve`, `cat`, or page tools.
- Expand through graph links and back-links when relationship context matters.
- Answer with citations, confidence, and a freshness delta.
- Offer follow-up ingestion only when new source material is required.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py query`
- `python3 plugins/knowledge-base/scripts/kb_ops.py retrieval-benchmark`


## Output Format

- KB ANSWER
- Answer, citations, confidence, freshness, and related pages.

## Anti-Patterns

- Using web search before checking the KB.
- Blending inference into sourced facts.
