# Knowledge Base

Knowledge base workflows for capturing, organizing, retrieving, and maintaining reusable domain knowledge.

## Skill Portfolio

The plugin ships 24 consolidated skills that cover the full KB lifecycle.

| Area | Skills |
| --- | --- |
| Core operations | `ask-user`, `resolver`, `setup`, `health`, `sample-vault`, `vaultli`, `skillify` |
| Retrieval and outputs | `query`, `briefing`, `reports` |
| Ingestion and migration | `ingest`, `meeting-ingestion`, `media-ingest`, `signal-detector`, `migrate` |
| Curation and synthesis | `enrich`, `citation-fixer`, `concept-synthesis`, `conflict-resolution`, `current-research`, `strategic-reading`, `task-manager` |
| Publishing and automation | `publish`, `background-jobs` |

## Consolidation Map

Former roadmap skills are intentionally merged into the survivor skills:

| Survivor | Absorbed scope |
| --- | --- |
| `resolver` | `kb-ops` routing and operations dispatch |
| `query` | `search-modes`, `source-router`, `graph-ops` |
| `health` | `maintenance`, `dashboard`, `frontmatter-guard`, `privacy-security` |
| `ingest` | ingestion front door and connector/webhook routing |
| `media-ingest` | `article-enrichment`, `browser-ingest`, `voice-note-ingest`, raw media/source capture |
| `setup` | `cold-start` |
| `migrate` | `archive-crawler` |
| `signal-detector` | `originals` and lightweight signal capture |
| `concept-synthesis` | `book-mirror` |
| `current-research` | `academic-verify` |
| `publish` | `pdf-export` and publication gates |
| `background-jobs` | `cron-scheduler`, `context-checkpoint` |
| `skillify` | `quality-gate`, `devex-review`, and skill buildout checks |
| References | `filing-rules`, `integration-contracts`, `release-upgrade`, `raw-source` |

## Bundled Tools

| Tool | Path | Use Cases |
| --- | --- | --- |
| `vaultli` | `vaultli/` via `bin/vaultli` | File-based KB setup, YAML frontmatter, sidecar docs for non-markdown assets, `INDEX.jsonl` rebuilds, validation, metadata search, context assembly, and federated vault lookup. |
| `kb_ops.py` | `scripts/kb_ops.py` | Deterministic resolver checks, retrieval benchmarks, frontmatter/citation/graph/raw-source/privacy audits, dashboards, maintenance plans, event normalization, schedule validation, and resumable checkpoints. |

## Deterministic KB Ops

The SKILL.md files describe workflows; `scripts/kb_ops.py` is the repeatable
operating harness behind them. Use it in CI, local debugging, or agent runs:

```bash
CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(pwd)/plugins/knowledge-base}"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" resolver-check
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" retrieval-benchmark \
  --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" dashboard \
  --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb_ops.py" maintenance-plan \
  --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
```

The harness intentionally emits JSON so plugin-manager, CI, and future agents
can route on exact failures instead of parsing prose.

## Agents

| Agent | Use |
| --- | --- |
| `kb-curation` | Maintain page quality, citations, filing, back-links, conflict resolution, and synthesis workflows. |
| `kb-ingestion` | Run ingestion and migration batches with raw-source preservation, privacy gates, and checkpoints. |
| `kb-ops` | Audit plugin/vault health, sample fixtures, generated artifacts, release checks, and operational workflows. |
| `kb-retrieval` | Tune KB query routing, retrieval benchmarks, graph expansion, freshness reporting, and source-scope boundaries. |

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
CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(pwd)/plugins/knowledge-base}"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json root .
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root ./kb
```

The Python fallback for `vaultli` requires `PyYAML`; the Rust binary path is
used automatically when a compatible bundled binary is present.

Validate the bundled sample vault:

```bash
CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(pwd)/plugins/knowledge-base}"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json index --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json validate --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
"${CLAUDE_PLUGIN_ROOT}/bin/vaultli" --json search "renewal risk" --root "${CLAUDE_PLUGIN_ROOT}/references/samples/mini-vault"
```
