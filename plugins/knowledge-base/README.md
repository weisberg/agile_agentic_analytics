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
| `kb_ops.py` | `scripts/kb_ops.py` | Deterministic resolver checks, retrieval benchmarks, frontmatter/citation/graph/raw-source/privacy audits, dashboards, maintenance plans, event normalization, schedule validation, and resumable checkpoints. |

## Deterministic KB Ops

The SKILL.md files describe workflows; `scripts/kb_ops.py` is the repeatable
operating harness behind them. Use it in CI, local debugging, or agent runs:

```bash
python3 plugins/knowledge-base/scripts/kb_ops.py resolver-check
python3 plugins/knowledge-base/scripts/kb_ops.py retrieval-benchmark \
  --root plugins/knowledge-base/references/samples/mini-vault
python3 plugins/knowledge-base/scripts/kb_ops.py dashboard \
  --root plugins/knowledge-base/references/samples/mini-vault
python3 plugins/knowledge-base/scripts/kb_ops.py maintenance-plan \
  --root plugins/knowledge-base/references/samples/mini-vault
```

The harness intentionally emits JSON so plugin-manager, CI, and future agents
can route on exact failures instead of parsing prose.

## Agents

| Agent | Use |
| --- | --- |
| `kb-curator` | Maintain page quality, citations, filing, back-links, and schema-aligned page edits. |
| `kb-researcher` | Compare current facts and primary sources against existing KB context. |
| `kb-ops-auditor` | Audit plugin health, vault health, generated artifacts, releases, and operational workflows. |
| `kb-librarian` | Maintain taxonomy, templates, resolver fixtures, naming, and sample vault structure. |
| `kb-ingestion-operator` | Run ingestion batches with raw-source preservation, privacy gates, and checkpoints. |
| `kb-citation-auditor` | Audit factual claims, citations, source manifests, quotes, and publication readiness. |
| `kb-retrieval-specialist` | Tune KB search, retrieval benchmarks, source routing, graph expansion, and freshness reporting. |
| `kb-enrichment-analyst` | Enrich pages with current state, timelines, contradictions, links, and exact originals. |
| `vaultli-maintainer` | Maintain vaultli CLI parity, sample vault behavior, validation commands, and CI coverage. |

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
| `references/routing-eval.jsonl` | Resolver coverage fixture with at least one realistic intent per skill. |
| `references/benchmarks/retrieval-benchmarks.jsonl` | Retrieval benchmark queries and expected sample-vault hits. |
| `references/templates/` | Page templates for people, companies, concepts, meetings, sources, reports, originals, and tasks. |
| `references/examples/` | Source-envelope and schedule examples for deterministic command tests. |
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
