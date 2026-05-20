# Knowledge Base Page Types

Use these schemas as the canonical target shapes for KB skills. They complement
`vaultli/vaultli-spec-v1.0.md`, which defines file-level metadata and indexing.

## Common Frontmatter

```yaml
id: concepts/decision-quality
title: Decision Quality
description: One sentence describing why this page exists and when to retrieve it.
type: concept
status: active
scope: personal
created: 2026-05-20
updated: 2026-05-20
tags: [strategy, decisions]
aliases: [decision hygiene]
source_summary: "Compiled from cited KB pages"
related: []
```

## Types

| Type | Directory | Required Sections |
| --- | --- | --- |
| `person` | `people/` | State, Timeline, Relationships, See Also |
| `company` | `companies/` | State, Timeline, People, Relationships, See Also |
| `concept` | `concepts/` | State, Evidence, Examples, See Also |
| `meeting` | `meetings/` | Summary, Decisions, Action Items, Entities, Sources |
| `source` | `sources/` | Source Metadata, Extracted Claims, Raw Source |
| `original` | `originals/` | Exact Wording, Context, Related Concepts |
| `report` | `reports/` | Question, Sources, Findings, Repro Notes |
| `task` | `tasks/` | Status, Owner, Source, Next Action |

## Relationship Fields

- `related`: soft conceptual links.
- `depends_on`: required context or source assets.
- `mentions`: entity ids mentioned by the page.
- `backlinks`: derived or manually checked inbound references.
- `conflicts_with`: pages or claims that disagree with this one.

## Citation Rule

Every durable fact needs inline source provenance. Use `ingest/references/quality.md`
for citation formats and `citation-fixer` to repair gaps.

