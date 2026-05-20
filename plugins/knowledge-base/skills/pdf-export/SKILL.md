---
name: pdf-export
version: 0.1.0
description: >-
  Render KB pages or reports to PDF using a browser/HTML workflow with citations, source manifests, and visual verification.
triggers:
  - "kb to pdf"
  - "make pdf"
  - "export pdf"
  - "render this page"
tools:
  - read
  - write
  - exec
mutating: true
writes_pages: true
---

# Pdf Export

## Contract

- PDFs are generated from a reviewed source page or report.
- Rendered output is visually checked for clipped text, broken links, and missing citations.

## Workflow

- Resolve the source KB page/report.
- Create a print-safe HTML or markdown-rendered intermediate.
- Render to PDF using available browser/PDF tooling.
- Verify first page, link/citation presence, and file path.
- Record artifact in reports or publication metadata.

## Output Format

- PDF EXPORTED
- Source, PDF path, checks, warnings.

## Anti-Patterns

- Rendering before citation/privacy review.
- Claiming PDF success without checking the output exists.
