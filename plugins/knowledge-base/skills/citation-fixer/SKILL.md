---
name: citation-fixer
version: 0.2.0
description: >-
  Audit and repair KB citations so every factual claim carries inline source provenance with date and origin, and unverifiable claims are flagged rather than laundered into certainty. Trigger on 'fix citations', 'audit KB citations', 'this claim has no source', 'citation audit'. This repairs provenance on existing pages; to rewrite a page's current state use enrich; for a full vault-wide quality sweep (frontmatter, links, stale pages) use health.
triggers:
  - "fix kb citations"
  - "audit kb citations"
  - "flag facts without sources"
  - "citation audit"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
disable-model-invocation: false
mutating: true
---

# Citation Fixer

## Contract

- Every factual claim in durable KB pages has a source citation or is flagged for review.
- Synthetic, inferred, and compiled claims are labeled accurately.
- Unverifiable claims are marked for review rather than given an invented source.
- Mutating skill: citation repairs are allowed, but content rewrites beyond provenance repair route to `enrich` or `conflict-resolution`.

## Intake And Modes

- Treat `$ARGUMENTS` as target pages, vault root, citation scope, and optional fix-vs-audit mode.
- Quick mode: audit one page or claim and return exact missing-source lines.
- Standard mode: repair citations on a small target set and validate the result.
- Deep mode: run a vault slice audit, group unresolved claims by source-recovery path, and create a remediation plan.
- Use `ask-user` before removing a claim or making a broad inference from weak provenance.

## Evidence Requirements

- Inspect the page body, frontmatter, raw-source pointer, sidecar files, and linked originals before declaring a claim unverifiable.
- Preserve quote/source boundaries and copyright limits when adding citation context.

## Workflow

- Scan target pages for uncited factual sentences, timelines, and quotes with `citation-audit`.
- Recover provenance from raw source links, sidecars, and page frontmatter.
- Normalize citations to the formats in `references/quality.md`.
- Flag genuinely unverifiable claims with TODO review notes.
- Run `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root <kb-root>` after edits when a file-based vault is involved.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" citation-audit`


## Output Format

- CITATION AUDIT
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Pages checked, citations fixed, unresolved claims, validation status.
- Artifact path: inline for one-off fixes; saved audit at `reports/<YYYYMMDD>-citation-audit.md` when requested or vault-wide.

## Anti-Patterns

- Inventing a source to satisfy the format.
- Adding one citation to a paragraph of unrelated facts.
