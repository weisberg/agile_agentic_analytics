---
name: article-enrichment
version: 0.1.0
description: >-
  Turn articles and web pages into KB pages with raw-source preservation, executive analysis, quotes, entities, and cross-links.
triggers:
  - "enrich this article"
  - "save article to kb"
  - "process this article"
  - "analyze this link"
tools:
  - search
  - get_page
  - put_page
  - add_link
  - vaultli
mutating: true
writes_pages: true
---

# Article Enrichment

## Contract

- Article pages contain analysis, not generic summaries.
- Raw source URL, title, author, publication, and fetch date are preserved.
- People, companies, and concepts are extracted and back-linked.

## Workflow

- Fetch or read the article text and preserve raw provenance.
- Extract title, author, publication, date, URL, quotes, and entities.
- Write executive summary, key arguments, implications, contradictions, and KB connections.
- Update related entity pages and graph links.
- Validate citations and index state.

## Output Format

- ARTICLE ENRICHED
- Page, source, entities, links, quotes, raw source path.

## Anti-Patterns

- Summarizing without explaining why it matters.
- Saving URLs without fetch date or publication metadata.
