---
name: query
version: 0.2.0
description: >-
  Answer a question from the knowledge base first — select the retrieval mode (exact, metadata, semantic-overlap, graph, timeline, federated), route across vault source scopes, expand through relationship back-links, and answer with citations, confidence, and a freshness delta. Trigger on 'ask the KB', 'what do we know about X', 'search the knowledge base', 'relationship/graph question about my notes', 'which source scope'. Mode, scope, and graph detail live in references/retrieval.md (this skill absorbed search-modes, source-router, and graph-ops). For a proactive prep document use briefing; for brand-new external facts use current-research; for low-level vault CLI mechanics use vaultli.
triggers:
  - "ask the kb"
  - "what does the kb know about"
  - "search the knowledge base"
  - "relationship question in my notes"
  - "which kb source scope"
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
disable-model-invocation: false
mutating: false
---

# Query

## Contract

- Search the KB before external research unless the user explicitly asks for current web facts.
- Pick the retrieval mode from the question type (see references/retrieval.md); metadata filters run before semantic overlap.
- Search results are pointers — hydrate the body or source before answering when content matters.
- Every answer separates cited KB facts, inference, and unknowns, cites the source scope, and ends with a freshness delta.
- Read-only skill: do not write pages, reports, or benchmark fixtures unless the user explicitly asks to save the result or route to another skill.

## Intake And Modes

- Treat `$ARGUMENTS` as the question plus optional entity, source scope, vault root, freshness threshold, and desired depth.
- Quick mode: answer a narrow lookup from a few hydrated pages.
- Standard mode: use the best retrieval mode, hydrate supporting sources, and answer with confidence and freshness.
- Deep mode: combine graph/timeline/federated retrieval and record durable misses for benchmark follow-up.
- Use `ask-user` when source scope is unclear or when personal/team/org facts would be mixed.

## Evidence Requirements

- Hydrate page bodies or source content before using a result as evidence.
- For graph questions, report the relationship path and the source behind each edge.

## Workflow

- Classify the question: exact lookup, concept, relationship/graph, timeline, source, or freshness.
- Route source scope (personal/team/org/public/federated) before reading; never merge scopes without labels.
- Shortlist with `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search` in the chosen mode, then hydrate with `resolve`, `cat`, or `context`.
- For relationship questions, traverse typed back-links and report the path with per-edge source evidence.
- Answer with citations, confidence, source scope, and a freshness delta; route material gaps to `current-research`.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" query`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" retrieval-benchmark`


## Output Format

- KB ANSWER
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Answer, retrieval mode, source scope, citations, confidence, freshness delta, related pages.
- Artifact path: inline unless saved via `reports` as `reports/<YYYYMMDD>-<slug>.md`.

## Anti-Patterns

- Using web search before checking the KB.
- Answering from search metadata as if it were the hydrated body.
- Treating semantic overlap as vector retrieval, or answering relationship questions without source evidence.
