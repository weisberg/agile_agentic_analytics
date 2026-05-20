# KB Filing Rules

Use these rules before creating or routing a knowledge base page.

## File By Primary Subject

Choose the page location by what the content is primarily about, not by source
format:

- `people/` for notable people the user interacts with or discusses repeatedly.
- `companies/` for organizations relevant to the user's work or interests.
- `concepts/` for reusable frameworks, ideas, theses, methods, and original thinking.
- `meetings/` for meeting-specific artifacts.
- `sources/` for raw or lightly processed source material that is not yet entity-centered.
- `media/videos/`, `media/podcasts/`, or `media/x/` when the media artifact itself is the durable object.

When the destination is a file-based KB vault, use `vaultli` to keep metadata and
the derived index healthy:

- native markdown pages get inline YAML frontmatter
- non-markdown assets get same-directory sidecars such as `report.sql.md`
- `INDEX.jsonl` is rebuilt with `vaultli index`, never edited by hand
- `vaultli validate` runs after meaningful page or metadata changes

## Notability Gate

Create or update a page when the entity is likely to matter again:

- The user knows, works with, advises, funds, studies, or repeatedly mentions the person or company.
- The entity changes the interpretation of a meeting, source, or decision.
- The concept is a reusable mental model, framework, thesis, or insight.
- The content captures the user's original thinking in their own words.

Do not create pages for incidental one-off mentions unless the mention is needed
for provenance or cross-reference integrity.

## Back-Link Format

When a page mentions an entity, update the entity page with a link back to the
source page. Include the date, short context, and source citation:

```markdown
- YYYY-MM-DD - Mentioned in [[meetings/YYYY-MM-DD-short-description]] in the context of <brief context>. [Source: Meeting "<title>", YYYY-MM-DD]
```

## Page Update Rule

Rewrite State or compiled_truth sections with the current best understanding.
Do not append contradictory snapshots. Timelines can append new dated events,
newest first.
