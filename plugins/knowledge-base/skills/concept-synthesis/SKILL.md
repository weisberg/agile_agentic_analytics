---
name: concept-synthesis
version: 0.2.0
description: >-
  Synthesize concepts, patterns, and originals across the KB into tiered intellectual maps with evidence and links, and read a book or long-form work through the KB to mirror its ideas, contradictions, and personalized applications. Trigger on 'synthesize concepts', 'find patterns in my notes', 'build an intellectual map', 'mirror this book against my KB', 'personalize this book'. Absorbs book-mirror. For capturing a single new idea use signal-detector; for verifying an external/academic claim use current-research.
triggers:
  - "synthesize concepts"
  - "find patterns in my notes"
  - "build an intellectual map"
  - "mirror this book against my kb"
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

# Concept Synthesis

## Contract

- Synthesis pages cite the supporting pages and preserve original language where it matters.
- Concepts are deduplicated, tiered, and linked to evidence; weak patterns stay hypotheses, not facts.
- A book mirror is personalized against the KB, not a generic summary; book claims link to chapters/locations and KB parallels.
- Mutating skill: it may create/update concept or project pages only after search confirms the concept is not already represented.

## Intake And Modes

- Treat `$ARGUMENTS` as the concept/theme/source plus optional problem lens, evidence threshold, and target vault path.
- Quick mode: cluster a small set of notes and recommend whether a durable concept page is warranted.
- Standard mode: create or update one synthesis page with evidence, counterexamples, and links.
- Deep mode: mirror a long-form source against the KB and produce a problem-specific playbook.
- Use `ask-user` when multiple filing destinations or lenses are plausible.

## Evidence Requirements

- Search existing concept/original/source pages before creating new pages.
- Require multiple supporting sources for strong synthesis claims; label single-source patterns as hypotheses.

## Workflow

- Search recent originals, reflections, meeting notes, and concept stubs (or load the book text and TOC).
- Cluster by recurring theme; distinguish duplicates from adjacent ideas and map book sections to KB parallels and counterexamples.
- Set an evidence threshold before writing a synthesis or mirror page.
- Create or update concept pages with See Also links, provenance, and quotes within copyright limits.
- Run `query` to confirm evidence and route contradictions to `conflict-resolution`.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" query`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" graph-audit`


## Output Format

- CONCEPT SYNTHESIS
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Clusters, pages updated, evidence, hypotheses, book parallels, links.
- Artifact path: `concepts/<slug>.md` for durable concepts or `projects/<slug>.md` for problem-tied playbooks.

## Anti-Patterns

- Overfitting a pattern from one example.
- Writing a generic book summary, or treating the book as true when KB evidence conflicts.
- Paraphrasing original user language that should be quoted.
