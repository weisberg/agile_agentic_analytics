---
name: ingest
description: >
  Front door for getting a source into the knowledge base: detect the input type
  and delegate to the specialized ingestion skill, applying the shared ingestion
  laws (citation, back-link, raw-source preservation, filing by subject). Trigger
  on "ingest this", "save this to the knowledge base", "add this source to my
  KB", "capture this for the KB". This skill routes; it does not re-implement the
  per-media workflows. For a meeting transcript use meeting-ingestion; for PDFs,
  articles, video, audio, voice notes, browser captures, screenshots, or repos
  use media-ingest; for noticing entities in ordinary chat use signal-detector;
  for bulk import of an existing store use migrate or setup.
triggers:
  - "ingest this"
  - "save this to the knowledge base"
  - "add this source to my kb"
  - "capture this for the kb"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
mutating: true
disable-model-invocation: false
---

# Ingest

The ingestion front door. Detect what the input is, then hand off to the skill
that owns it. Enforce the shared ingestion laws no matter which sub-skill runs.

> **Filing rule:** read `references/kb-filing-rules.md` before creating any new
> page. File by primary subject, not by source format.

## Contract

- Every fact written to a KB page carries an inline `[Source: ...]` citation with date and provenance.
- Every mention of a person or company that has a page creates a back-link FROM that entity's page TO the page mentioning them (the Iron Law — see `references/quality.md`).
- Raw sources are preserved for provenance with size-based routing (see `references/raw-source-storage.md`): small text/PDF stays in the vault; large media is stored externally with a `.redirect.yaml` pointer.
- State sections are rewritten with the current best understanding, never appended to.
- This skill delegates. It classifies the input and routes; it does not restate each sub-skill's workflow.
- File-based vaults use the bundled `vaultli` CLI for frontmatter, sidecars, `INDEX.jsonl`, validation, search, and context assembly.
- Mutating skill: ingestion writes are allowed only after routing, privacy scope, raw-source handling, and filing destination are clear.

## Intake And Modes

- Treat `$ARGUMENTS` as the source payload/path/URL plus optional vault root, privacy scope, and desired destination.
- Quick mode: classify the source and name the owning ingestion skill without writing.
- Standard mode: route one source through the correct child skill, then verify shared ingestion laws.
- Deep mode: plan a multi-source import, delegate batches through `migrate`, `setup`, or `background-jobs`, and checkpoint validation.
- Use `ask-user` when input type, privacy scope, or primary subject is ambiguous.

## Evidence Requirements

- Inspect source metadata, existing matching pages, raw-source destination, and filing rules before creating a page.
- Verify citations, back-links, raw-source preservation, and vault validation before reporting ingestion complete.

## Citation Requirements (MANDATORY)

Every fact written to a KB page must carry an inline `[Source: ...]` citation.

- **User's statements:** `[Source: User, {context}, YYYY-MM-DD]`
- **Meeting data:** `[Source: Meeting "{title}", YYYY-MM-DD]`
- **Email/message:** `[Source: email from {name} re: {subject}, YYYY-MM-DD]`
- **Web content:** `[Source: {publication}, {URL}, YYYY-MM-DD]`
- **Social media:** `[Source: X/@handle, YYYY-MM-DD](URL)` (include link)
- **Synthesis:** `[Source: compiled from {sources}]`

## Routing

Classify the input, then delegate:

| Input | Delegate to |
| --- | --- |
| Meeting transcript or notes | `meeting-ingestion` |
| PDF, book, article, web page, browser capture | `media-ingest` |
| Video, audio, podcast, voice note | `media-ingest` |
| Screenshot, image, code repo | `media-ingest` |
| Entity mention noticed in ordinary chat | `signal-detector` |
| The user's own original idea or exact phrasing | `signal-detector` |
| Bulk import of an existing store or archive | `migrate` |
| First-run vault creation and guided import | `setup` |
| Connector / webhook payload | see `references/connector-ingestion.md` |

If the type is ambiguous, use `ask-user` with 2-4 options and an escape hatch
rather than guessing.

## Workflow

1. **Confirm the KB storage mode.** For a file-based vault, find or initialize the root with `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json root .` or `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json init <path>`.
2. **Classify the input** using the routing table and hand off to the owning sub-skill.
3. **Verify the shared laws held** after the sub-skill runs: every fact cited, every notable entity back-linked (Iron Law), raw source preserved, and pages filed by primary subject.
4. **Index and validate** the file vault with `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index --root <kb-root>` and `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root <kb-root>`.

## Shared Ingestion Laws

These hold for every ingestion path and are the reason this front door exists:

- **File by primary subject, not format.** A page about a person goes in `people/`, a company in `companies/`, a reusable framework in `concepts/`, raw data in `sources/` (see `references/kb-filing-rules.md`).
- **Back-link every notable entity (Iron Law).** An unlinked mention is a broken KB. The same event appears on every mentioned entity's timeline.
- **Preserve raw source.** A page without provenance is unverifiable. Route by size per `references/raw-source-storage.md`.
- **Capture original thinking verbatim.** The user's exact language IS the insight — delegate to `signal-detector`, do not paraphrase.
- **Test before bulk.** For multi-item ingestion, run 3-5 items first, read the output, fix the approach, then bulk-execute with checkpoints via `background-jobs`.

## vaultli Use

Use the bundled CLI whenever ingestion writes to or reads from a file-based vault:

- **New vault:** `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json init <path>`.
- **Markdown pages:** `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json add <file> --root <kb-root>`.
- **Non-markdown sources:** `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json scaffold <file> --root <kb-root>`.
- **Bulk preview:** `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json ingest <path> --root <kb-root> --dry-run`.
- **Integrity:** `"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root <kb-root>`.

Write page bodies, timeline entries, and cross-links by editing markdown with
`Read`/`Write`/`Edit`, then reindex and validate with `vaultli`.
Use the wrapper path when executing those commands; bare `vaultli` is only a
prose shorthand.

## Anti-Patterns

- **Re-implementing a sub-skill inline.** Delegate to `meeting-ingestion` or `media-ingest`; do not restate their workflows here.
- **Ingesting without back-links.** Every notable entity mentioned must have a back-link from its page (Iron Law).
- **Skipping raw source preservation.** Every ingested item must have recoverable provenance.
- **Appending to State sections.** State is rewritten with the current best understanding on every update.
- **Bulk processing without a sample test.** Test on 3-5 items first; fix the approach, not one-off patches.
- **Paraphrasing the user's original thinking.** Route exact phrasing to `signal-detector` and capture it verbatim.

## Output Format

```text
INGESTED: [title]
==================

Routed to: [meeting-ingestion / media-ingest / signal-detector / migrate / setup]
Page: [slug]
Type: [person / company / meeting / media / concept]
Source: [source description]

Entities detected: N
- [entity] -> [created / updated] ([slug])

Back-links created: N
Timeline entries: N
Raw source: [preserved at path / uploaded to cloud]
Shared laws verified: [citations / back-links / raw-source / filing]
Status: [DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT]
```
