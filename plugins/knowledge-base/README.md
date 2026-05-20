# Knowledge Base

Knowledge base workflows for capturing, organizing, retrieving, and maintaining reusable domain knowledge.

## Skill Portfolio

The plugin ships 50 skills that cover the full KB lifecycle.

| Area | Skills |
| --- | --- |
| Core operations | `ask-user`, `kb-ops`, `resolver`, `setup`, `health`, `maintenance`, `dashboard`, `vaultli` |
| Retrieval and graph | `query`, `search-modes`, `source-router`, `graph-ops`, `briefing`, `reports` |
| Ingestion | `ingest`, `signal-detector`, `article-enrichment`, `meeting-ingestion`, `media-ingest`, `voice-note-ingest`, `browser-ingest`, `raw-source`, `cold-start`, `migrate`, `archive-crawler` |
| Knowledge work | `enrich`, `citation-fixer`, `frontmatter-guard`, `filing-rules`, `concept-synthesis`, `book-mirror`, `academic-verify`, `current-research`, `strategic-reading`, `originals`, `task-manager` |
| Publishing and automation | `publish`, `pdf-export`, `webhook-transforms`, `cron-scheduler`, `background-jobs`, `context-checkpoint`, `privacy-security`, `quality-gate`, `release-upgrade`, `devex-review`, `integration-contracts`, `conflict-resolution`, `sample-vault`, `skillify` |

## Bundled Tools

| Tool | Path | Use Cases |
| --- | --- | --- |
| `vaultli` | `vaultli/` via `bin/vaultli` | File-based KB setup, YAML frontmatter, sidecar docs for non-markdown assets, `INDEX.jsonl` rebuilds, validation, metadata search, context assembly, and federated vault lookup. |

## Agents

| Agent | Use |
| --- | --- |
| `kb-curator` | Maintain page quality, citations, filing, back-links, and schema-aligned page edits. |
| `kb-researcher` | Compare current facts and primary sources against existing KB context. |
| `kb-ops-auditor` | Audit plugin health, vault health, generated artifacts, releases, and operational workflows. |

## References And Fixtures

| Path | Purpose |
| --- | --- |
| `references/schemas/page-types.md` | Canonical KB page types, frontmatter, and relationship fields. |
| `references/schemas/integration-contracts.md` | Normalized connector/webhook envelope for ingestion. |
| `references/retrieval-and-benchmarks.md` | Retrieval modes, graph/timeline routing, and benchmark record shape. |
| `references/raw-source-storage.md` | Raw source, redirect, hash, and restore conventions. |
| `references/privacy-and-security.md` | Scope, PII, credential, and publication-safety model. |
| `references/automation.md` | Cron/background job and checkpoint envelope. |
| `references/release-upgrade.md` | Release, versioning, and validation bundle. |
| `references/upstream-sources.md` | GBrain/GStack import ledger and drift review cadence. |
| `references/issue-coverage.md` | GitHub issue closeout map for the KB roadmap. |
| `references/samples/mini-vault/` | Synthetic sample vault with people, companies, concepts, meetings, sources, strategic reading, and non-markdown sidecars. |

## Structure

Plugin with reusable workflow skills, specialized KB agents, reference schemas,
synthetic fixtures, and a bundled vault maintenance CLI.

| Directory | Purpose |
| --- | --- |
| `skills/<name>/SKILL.md` | User-facing knowledge base workflows |
| `agents/*.md` | Specialized knowledge management subagents |
| `references/` | Taxonomies, schemas, templates, and curation guidance |
| `scripts/` | Reusable indexing, validation, import, or export utilities |
| `vaultli/` | Bundled file-based knowledge vault CLI and implementation docs |
| `bin/` | Executable wrappers exposed while the plugin is enabled |

## Maintainer Notes

Imported or adapted upstream sources are tracked in
`references/upstream-sources.md`. Use
`/plugin-manager:upstream-skill-harvest` when importing, refreshing, or diffing
skills from GBrain or GStack.

## Installation

```text
/plugin install knowledge-base@agile-agentic-analytics
```

## Local Testing

```bash
claude --plugin-dir ./plugins/knowledge-base
```

Reload after edits with `/reload-plugins`. Validate with `claude plugin validate`.

Try the bundled CLI after loading the plugin:

```bash
vaultli --json root .
vaultli --json validate --root ./kb
```

The Python fallback for `vaultli` requires `PyYAML`; the Rust binary path is
used automatically when a compatible bundled binary is present.

Validate the bundled sample vault:

```bash
vaultli --json index --root ./plugins/knowledge-base/references/samples/mini-vault
vaultli --json validate --root ./plugins/knowledge-base/references/samples/mini-vault
vaultli --json search "renewal risk" --root ./plugins/knowledge-base/references/samples/mini-vault
```
