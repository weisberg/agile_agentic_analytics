---
name: current-research
version: 0.2.0
description: >-
  Research current or external developments and produce a freshness delta against what the KB already knows, and verify academic or technical claims against primary papers, replication status, methods, and limitations before they enter the KB. Trigger on 'what's new since', 'update this from the web', 'freshness delta', 'verify this study/paper', 'has this been replicated'. Absorbs academic-verify. For answering purely from existing KB context use query; for synthesizing internal notes use concept-synthesis.
triggers:
  - "whats new since"
  - "update this from the web"
  - "freshness delta"
  - "verify this study"
  - "has this been replicated"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - WebFetch
  - WebSearch
disable-model-invocation: false
mutating: true
---

# Current Research

## Contract

- Current facts are checked against up-to-date primary/official sources; academic claims are traced to the primary paper.
- The output separates already-known KB context from new, changed, contradicted, unchanged, and unknown facts.
- Every web/current claim has a source, URL, publication date, and retrieval date; replication and limitation notes are explicit.
- Mutating skill: update KB pages only after the current-source delta is clear and citation quality is sufficient.

## Intake And Modes

- Treat `$ARGUMENTS` as the entity/topic/claim plus optional date threshold, source type, and whether writes are allowed.
- Quick mode: verify one fact or return a narrow freshness delta.
- Standard mode: compare one KB page against current primary/official sources and update if warranted.
- Deep mode: verify an academic/technical claim with methods, limitations, replication, and downstream KB changes.
- Use `ask-user` when sources disagree and no objective quality/recency rule decides the update.

## Evidence Requirements

- Load existing KB context first, then inspect primary/official/current sources.
- For academic claims, record DOI/authors/venue/method/sample/effect/limitations and replication status where available.

## Workflow

- Load the current KB page/context first, then search current or primary sources.
- For academic claims, find the primary paper, DOI, authors, venue, and check methods, sample, effect size, limitations, and replication.
- Build a delta: new, changed, contradicted, unchanged, unknown.
- Update KB pages only when source quality and relevance meet the bar; date every current claim.
- Record freshness and a next-review date.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" query`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" citation-audit`


## Output Format

- FRESHNESS DELTA
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Known context, new facts, changed facts, verification status, sources, KB writes.
- Artifact path: updated page path(s), or `reports/<YYYYMMDD>-freshness-delta.md` when saved as a report.

## Anti-Patterns

- Overwriting KB context with a single new article, or failing to date current claims.
- Relying on a secondary article for a technical claim, or ignoring failed replication and narrow samples.
