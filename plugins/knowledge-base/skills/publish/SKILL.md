---
name: publish
version: 0.2.0
description: >-
  Prepare a KB page or report for sharing or publication — privacy scrub, audience scope, citation check, approval gate — and render it to the requested export format, including PDF via a browser/HTML workflow with visual verification. Trigger on 'publish this page', 'share this note', 'prepare for public', 'export to PDF', 'render this page'. Absorbs pdf-export. The privacy model itself lives in references/privacy-and-security.md; for generating the report content first use reports.
triggers:
  - "publish this kb page"
  - "share this note"
  - "prepare for public"
  - "export to pdf"
  - "render this page"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
disable-model-invocation: false
mutating: true
---

# Publish

## Contract

- No KB page is shared without privacy, citation, and audience checks.
- Publication creates a derived artifact; the KB source remains intact.
- Rendered output (incl. PDF) is visually verified for clipped text, broken links, and missing citations.
- Mutating skill: publication writes derived artifacts only; it must not weaken the source KB page to make sharing easier.

## Intake And Modes

- Treat `$ARGUMENTS` as source page/report plus audience, format, destination, and approval state.
- Quick mode: assess publication readiness and list blockers.
- Standard mode: produce one redacted/exported artifact and verify it.
- Deep mode: prepare a multi-format publication package with manifest, approval gate, and regeneration notes.
- Use `ask-user` before public/client sharing, irreversible uploads, or redactions that change meaning.

## Evidence Requirements

- Inspect the source page/report, citations, raw-source links, privacy scope, and target audience before rendering.
- Verify rendered files exist and are visually/readably clean before declaring completion.

## Workflow

- Identify the audience: personal, team, client, or public.
- Run a privacy/security review (`privacy-audit`) and citation check (`citation-audit`).
- Redact or generalize sensitive names, paths, and raw sources.
- Export markdown/HTML/PDF as requested via a print-safe intermediate, then verify the rendered artifact exists and is clean.
- Record publication metadata and artifact path.

## Operating System Backing

This skill is backed by the shared deterministic KB operations harness. Use these commands for audits, CI fixtures, and repeatable agent runs:

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" privacy-audit`
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" citation-audit`


## Output Format

- PUBLISH PACKAGE
- Status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Artifact path, format, audience, redactions, citations, render checks, approval state.
- Artifact path: `exports/<YYYYMMDD>-<slug>.<format>` or the user-specified destination.

## Anti-Patterns

- Publishing raw meeting notes, or removing citations to make prose cleaner.
- Claiming a PDF succeeded without confirming the output file exists.
