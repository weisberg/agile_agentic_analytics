---
name: book-mirror
version: 0.1.0
description: >-
  Read a book through the user's existing KB to mirror ideas, contradictions, examples, and personalized applications.
triggers:
  - "book mirror"
  - "personalize this book"
  - "mirror this book against my kb"
  - "read this book with my notes"
tools:
  - read
  - write
  - exec
  - search
  - vaultli
mutating: true
writes_pages: true

disable-model-invocation: false
---

# Book Mirror

## Contract

- The output is personalized against the KB, not a generic book summary.
- Book claims are linked to chapters or locations and KB parallels.
- New concepts, quotes, and contradictions are filed with citations.

## Workflow

- Extract or load book text and table of contents.
- Search KB for related concepts, projects, people, and originals.
- Map book sections to KB parallels, counterexamples, and actions.
- Write a book mirror page and update related concepts.
- Preserve quotes within copyright limits and cite source locations.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 plugins/knowledge-base/scripts/kb_ops.py query`
- `python3 plugins/knowledge-base/scripts/kb_ops.py citation-audit`


## Output Format

- BOOK MIRROR
- Page, key parallels, contradictions, concepts updated, quotes.

## Anti-Patterns

- Writing a generic summary.
- Treating the book as true when KB evidence conflicts.
